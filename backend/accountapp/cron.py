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
import sys

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
    
    response = requests.get(url, timeout=10)
    
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

def get_youtube_video_id(youtube_url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # 일반적인 YouTube URL
        r'(?:embed\/|v\/|youtu.be\/)([0-9A-Za-z_-]{11})',  # 임베드 또는 짧은 URL
        r'(?:watch\?feature=player_embedded&v=)([0-9A-Za-z_-]{11})',  # 플레이어 임베드 URL
        r'^([0-9A-Za-z_-]{11})$'  # 비디오 ID만 있는 경우
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def get_youtube_thumbnail_url(youtube_url, default_url=None):
    video_id = get_youtube_video_id(youtube_url)
    
    if video_id:
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/sddefault.jpg"
        return thumbnail_url
    
    return default_url

def download_image(url):
    response = requests.get(url, timeout=10)
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
    if not profile_pic_url:
        profile_pic_url = f"{settings.MEDIA_URL}default_animal.png"

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
            'profile_pic_url': profile_pic_url,  # URL을 새로운 필드에 저장
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
        animal_profile.profile_pic_url = profile_pic_url  # URL 업데이트
        animal_profile.nickname = name
        animal_profile.bio = animal.get('INTRCN_CN', '')
        animal_profile.save()

    return user, animal_profile

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
