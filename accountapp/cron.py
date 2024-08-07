import os
import django
import random
from django.utils import timezone
import re
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import secrets
import string
import requests
import logging
from accountapp.models import User, AnimalUser, AnimalProfile
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')
django.setup()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(settings.BASE_DIR, 'cron.log'))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def call_api():
    key = settings.ANIMAL_API_KEY
    url = f"http://openapi.seoul.go.kr:8088/{key}/json/TbAdpWaitAnimalView/1/70/"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "TbAdpWaitAnimalView" in data:
            animals = data["TbAdpWaitAnimalView"]["row"]
            return animals
    else:
        logger.error(f"Failed to retrieve data: {response.status_code}")
        return []

def extract_name_and_center(nm):
    match = re.match(r"(.+?)\((.+?)(?:-[^)]+)?\)", nm)
    if match:
        name, center = match.groups()
        return name, center
    else:
        return nm, "Default Center"

def get_youtube_thumbnail_url(youtube_url):
    match = re.search(r"v=([^&]+)", youtube_url)
    if match:
        video_id = match.group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/sddefault.jpg"
        return thumbnail_url
    return None

def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image = image.convert('RGB')
        output = BytesIO()
        image.save(output, format='JPEG')
        output.seek(0)
        return InMemoryUploadedFile(output, 'ImageField', "temp.jpg", 'image/jpeg', sys.getsizeof(output), None)
    return None

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def create_animal_account(animal):
    name, center = extract_name_and_center(animal.get('NM'))
    username = f"animal_{animal.get('ANIMAL_NO')}"
    password = generate_random_password()

    user, created = User.objects.get_or_create(username=username, defaults={'password': password, 'is_animal': True})
    if not created:
        user.set_password(password)
        user.is_animal = True
    user.is_active = True
    user.save()

    animal_num = animal.get('ANIMAL_NO', random.randint(1000, 9999))
    animal_user, created = AnimalUser.objects.get_or_create(
        user=user,
        defaults={
            'animal_num': animal_num,
            'center': center,
            'species': animal.get('SPCS', 'Dog'),
            'breed': animal.get('BREEDS', 'Breed')
        }
    )

    youtube_url = animal.get('INTRCN_MVP_URL', '')
    profile_pic_url = get_youtube_thumbnail_url(youtube_url)
    profile_pic = None
    if profile_pic_url:
        profile_pic = download_image(profile_pic_url)
    if not profile_pic:
        default_image_path = os.path.join('media', 'default_animal.png')
        profile_pic = InMemoryUploadedFile(open(default_image_path, 'rb'), 'ImageField', 'default_animal.png', 'image/png', os.path.getsize(default_image_path), None)

    enter_date_str = animal.get('ENTRNC_DATE', timezone.now().strftime('%Y-%m-%d'))
    enter_date = datetime.strptime(enter_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

    animal_profile, created = AnimalProfile.objects.get_or_create(
        user=user,
        defaults={
            'center': center,
            'species': animal.get('SPCS', '0'),
            'kind': animal.get('BREEDS', 'Breed'),
            'sex': animal.get('SEXDSTN', 'M'),
            'age': animal.get('AGE', '1/0'),
            'weight': float(animal.get('BDWGH', 10.0)),
            'enter': enter_date,
            'youtube': youtube_url,
            'profile_pic': profile_pic,
            'nickname': name,
            'bio': animal.get('INTRCN_CN', '')
        }
    )

    if not created:
        animal_profile.center = center
        animal_profile.species = animal.get('SPCS', '0')
        animal_profile.kind = animal.get('BREEDS', 'Breed')
        animal_profile.sex = animal.get('SEXDSTN', 'M')
        animal_profile.age = animal.get('AGE', '1/0')
        animal_profile.weight = float(animal.get('BDWGH', 10.0))
        animal_profile.enter = enter_date
        animal_profile.youtube = youtube_url
        animal_profile.profile_pic = profile_pic
        animal_profile.nickname = name
        animal_profile.bio = animal.get('INTRCN_CN', '')
        animal_profile.save()

def my_scheduled_job():
    logger.info("Scheduled job started.")
    animals = call_api()
    for animal in animals:
        try:
            create_animal_account(animal)
            logger.info(f"Created account for animal: {animal.get('NM')}")
        except Exception as e:
            logger.error(f"Failed to create account for animal {animal.get('NM')}: {e}")

    logger.info("Scheduled job completed.")

if __name__ == "__main__":
    my_scheduled_job()
