import json
import os
import time
from models import Downloader, User

SETTINGS_FILE = "settings.json"


def human_readable_seconds(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return str(seconds) + " saniye"
    elif seconds < 3600:
        return str(int(seconds // 60)) + " dakika"
    elif seconds < 86400:
        return str(int(seconds // 3600)) + " saat"
    elif seconds < 604800:
        return str(int(seconds // 3600)) + " gün"


# Create history file if it does not exist
if not os.path.exists("history.txt"):
    with open("history.txt", "w") as f:
        f.write("")

# Check if the JSON file exists
if os.path.exists(SETTINGS_FILE):
    # If the file exists, open it and load its contents
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
else:
    # If the file doesn't exist, create it with default contents
    data = {"domain": None}
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

if data["domain"] is None:
    print("Uzaktan eğitim websitesi adresini giriniz: (https:// olmadan)")
else:
    print(f"Uzaktan eğitim websitesi adresini giriniz: ({data['domain']} için enter)")

domain = input()
while domain == "" and data["domain"] is None:
    print("Lütfen geçerli bir adres giriniz.")
    domain = input()

if data["domain"] is None and domain != "":
    data["domain"] = domain
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)
elif data["domain"] is not None and domain == "":
    domain = data["domain"]

print("Çerezleri giriniz:")
cookies = input()
while cookies == "":
    print("Çerezler boş bırakılamaz.")
    cookies = input()

print("Ders listesi alınıyor.")
user = User(domain, cookies)
courses = user.get_enrolled_courses()
downloader = Downloader()
selected_activities = []
choose_again = True
previous_downloads = set(line.strip() for line in open("history.txt", encoding="utf-8"))
while len(courses) > 0 and choose_again:
    i = 1
    for course in courses:
        print(str(i) + ". " + course.name + " (" + str(course.activity_count) + ")")
        i += 1
    print("Ders seçiniz: ")
    course_selection = int(input())
    if 0 < course_selection <= len(courses):
        course = courses[course_selection - 1]
        print(course.name + " içeriği yükleniyor.")
        course.activities = []
        course.fetch_activities()
        i = 1
        for activity in course.activities:
            try:
                if activity.id in previous_downloads:
                    print(
                        "%d) Hafta: %d Dosya Adı: %s (Daha önce indirilmiş.)"
                        % (i, activity.weeks[0], activity.slug_name)
                    )
                else:
                    print(
                        "%d) Hafta: %d Dosya Adı: %s"
                        % (i, activity.weeks[0], activity.slug_name)
                    )
            except:
                continue
            i += 1
        print("İçerik aralığı seçiniz (Örn: 1-17): ")
        activity_selection = input().split("-")
        while len(activity_selection) != 2:
            print("Lütfen geçerli bir aralık giriniz.")
            activity_selection = input().split("-")
        if len(activity_selection) == 2:
            start_activity = int(activity_selection[0])
            end_activity = int(activity_selection[1])
            if (
                end_activity - start_activity >= 0
                and start_activity > 0
                and 0 < end_activity <= len(course.activities)
            ):
                for i in range(start_activity - 1, end_activity):
                    activity = course.activities[i]
                    activity.prepare_video(downloader)
                    selected_activities.append(activity)
                print("Başka bir dersten içerik seçmek ister misiniz? (e/h)")
                choose_again = input().lower() == "e"

if selected_activities:
    start = time.time()
    downloader.start_downloads()
    end = time.time()
else:
    print(selected_activities)
    print("İçerik seçilmedi.")
