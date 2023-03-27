import json
import os
import re
import threading
from os.path import exists
import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 ' \
             'Safari/537.36 '
LMS_URL = ''
DOWNLOAD_FOLDER = './downloads/'


def get_web_page(url):
    request = requests.session()
    request.encoding = 'utf-8'
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': url,
        'Cookie': open('cookies.txt', 'r').read()
    }
    response = request.get(url, headers=headers)
    return response.text


class User:
    main_url = ""
    cookies = ""

    def __init__(self, domain, cookies):
        global LMS_URL
        LMS_URL = "https://" + domain
        self.main_url = LMS_URL
        self.cookies = cookies
        cookie_file = open('cookies.txt', 'w')
        cookie_file.write(cookies)
        cookie_file.close()

    def get_enrolled_courses(self):
        response = get_web_page(self.main_url + '/Course/GetEnrolledCourses?displayMode=list')
        course_list = []
        matches = re.findall(r'<a class="coursename" href="(.*?)" title=".*?">(.*?)</a>', response, re.MULTILINE)
        for match in matches:
            course_page = get_web_page(self.main_url + match[0])
            course_list.append(Course(match[0], match[1], course_page, self.main_url))

        return course_list


class Downloader:
    max_threads = 6
    threads = list()
    download_queue = list()

    semaphore = threading.Semaphore(value=max_threads)

    def __init__(self):
        pass

    def task(self, url, id, file_path):
        self.semaphore.acquire()
        self.download(url, file_path)
        history = open("history.txt", "a") 
        history.write(id)
        history.write("\n")
        self.semaphore.release()

    def add_to_queue(self, url, id="", file_name="", file_extension="mp4", file_path=DOWNLOAD_FOLDER):
        i = 2
        if exists(file_path + file_name + "." + file_extension):
            while exists(file_path + file_name + "." + file_extension + "_" + str(i)):
                i += 1
            file_name += "_" + str(i)
        self.download_queue.append((url, id, file_path + file_name + "." + file_extension))

    def download(self, url, file_path):
        print(file_path + " indirmesi başladı.")
        import pycurl
        with open(file_path, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.USERAGENT, USER_AGENT)
            c.setopt(c.HTTPHEADER, ['Referer: ' + url, 'Cookie: ' + open('cookies.txt', 'r').read()])
            c.setopt(c.SSL_VERIFYPEER, 0)
            c.setopt(c.SSL_VERIFYHOST, 0)
            c.setopt(c.WRITEDATA, f)
            c.perform()
            c.close()
        print(file_path + " indirmesi bitti.")

    def download_legacy(self, url, file_path):
        headers = {
            'User-Agent': USER_AGENT,
            'Referer': url,
            'Cookie': open('cookies.txt', 'r').read()
        }
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)

    def start_downloads(self):
        threads = [threading.Thread(name="worker/task", target=self.task, args=(video_data[0], video_data[1], video_data[2])) for
                   video_data in
                   self.download_queue]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print("Tüm indirmeler tamamlandı.")


class Course:
    id = ""
    path = ""
    name = ""
    page = ""
    main_url = ""
    activity_count = 0
    lecturers = []
    activities = []
    page_data = {}

    def __init__(self, course_path, course_name, course_page, main_url):
        self.path = course_path
        self.name = course_name
        self.page = course_page
        self.main_url = main_url
        data = re.search(r'var datasource = (.*);', self.page, re.MULTILINE)
        self.page_data = json.loads(data.group(1))
        self.name = self.page_data['courseName']
        self.activity_count = len(self.page_data['activities'])

    def fetch_activities(self):
        if self.page_data:
            self.id = self.page_data['courseId']
            self.lecturers = self.page_data['teachers']
            for activity in self.page_data['activities']:
                if activity['type'] == "Video" and activity['typeName'] == "Video":
                    activity = Activity(activity)
                    activity.main_url = self.main_url
                    activity.download_folder += self.name + "/"
                    self.activities.append(activity)


class Activity:
    id = ""
    name = ""
    slug_name = ""
    type = ""
    type_name = ""
    download_folder = ""
    file_exists = False
    weeks = []
    thumbnail_path = ""
    date = ""
    day_name = ""
    video = ""
    main_url = ""

    def __init__(self, activity):
        self.id = activity['id']
        self.name = activity['name']
        self.type = activity['type']
        self.type_name = activity['typeName']
        self.file_exists = activity['fileExists']
        self.weeks = activity['weeks']
        if not self.weeks:
            self.weeks = [0]
        self.thumbnail_path = activity['thumbnailPath']
        self.date = activity['addedDate']
        self.slugify_name()
        self.fetch_videos()
        self.download_folder = DOWNLOAD_FOLDER

    def fetch_videos(self):
        if self.type == "Video" and self.type_name == "Video":
            video = Video(self.id, LMS_URL)
            if video.url:
                self.video = video

    def get_video_id(self):
        last = self.thumbnail_path.rsplit('/', 1)[-1]
        return last.split('?')[0]

    def slugify_name(self):
        """ replace multiple spaces with single space """
        self.slug_name = re.sub(r'\s+', ' ', self.slug_name)
        """ replace spaces with hyphen """
        self.slug_name = self.name.replace(" ", "_")
        """ remove special characters """
        self.slug_name = re.sub(r'[^\w\s]', '', self.slug_name)
        # self.slug_name += "W" + "0" + str(self.weeks[0]) if self.weeks[0] < 10 else str(self.weeks[0])

    def prepare_video(self, downloader):
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        downloader.add_to_queue(self.video.url, self.video.id, self.slug_name, self.video.extension, self.download_folder)


class Video:
    url = ""
    id = ""
    name = ""
    extension = ""
    duration = ""
    size = ""
    main_url = ""

    def __init__(self, video_id, main_url):
        self.id = video_id
        self.main_url = main_url
        if self.main_url:
            self.fetch_data()

    def fetch_data(self):
        request = requests.session()
        headers = {
            'User-Agent': USER_AGENT,
            'Referer': self.url,
            'Cookie': open('cookies.txt', 'r').read()
        }
        response = request.post(self.main_url + '/Video/ManageInteraction?id=' + self.id,
                                headers=headers)
        data = json.loads(response.text)['Meta']
        self.name = data['VideoName']
        self.duration = data['Duration']
        self.url = self.main_url + data['VideoURL']
        matches = re.search(r"\?ext=(.*?)&", self.url)
        if matches:
            self.extension = matches.group(1)[1:]
