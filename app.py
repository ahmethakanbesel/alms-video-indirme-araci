import time
from models import Downloader, User


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


print("Uzaktan eğitim websitesi adresini giriniz: (https:// olmadan)")
domain = input()
while domain == "":
    print("Lütfen geçerli bir adres giriniz.")
    domain = input()
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
while len(courses) > 0 and choose_again:
    i = 1
    for course in courses:
        print(str(i) + ". " + course.name + " (" + str(course.activity_count) + ")")
        i += 1
    print("Ders seçiniz: ")
    course_selection = int(input())
    if 0 < course_selection <= len(courses):
        course = courses[course_selection - 1]
        print(course.name + " içeriği yükleniyor")
        course.activities = []
        course.fetch_activities()
        i = 1
        for activity in course.activities:
            try:
                print("%d) Hafta: %d Dosya Adı: %s" % (i, activity.weeks[0], activity.slug_name))
            except:
                continue
            i += 1
    print("İçerik aralığı seçiniz (Örn: 1-17): ")
    activity_selection = input().split('-')
    while len(activity_selection) != 2:
        print("Lütfen geçerli bir aralık giriniz.")
        activity_selection = input().split('-')
    if len(activity_selection) == 2:
        start_activity = int(activity_selection[0])
        end_activity = int(activity_selection[1])
        if end_activity - start_activity >= 0 and start_activity > 0 and 0 < end_activity <= len(
                courses[course_selection].activities):
            for i in range(start_activity - 1, end_activity):
                activity = courses[course_selection].activities[i]
                activity.prepare_video(downloader)
                selected_activities.append(activity)
    print("Başka bir dersten içerik seçmek ister misiniz? (e/h)")
    choose_again = input().lower() == "e"
    del course

if selected_activities:
    start = time.time()
    downloader.start_downloads()
    end = time.time()
    print(human_readable_seconds(end - start) + " sürdü.")
else:
    print("İçerik seçilmedi.")
