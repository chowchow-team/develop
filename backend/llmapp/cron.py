import sys
import os
import re
import time
import select
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
import logging
import random
import requests
import traceback

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')

import django
from django.conf import settings
from django.contrib.auth import get_user_model

django.setup()

from mainapp.models import PostImage
from accountapp.serializers import ProfileSerializer
from mainapp.models import Post
from mainapp.serializers import PostSerializer

# MODEL_PATH 정의
MODEL_PATH = os.path.join(current_dir, "llm", "EEVEQ4.gguf")

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(settings.BASE_DIR, 'llm_post.log'))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def extract_text_from_html(html_content):
    text = re.sub(r'<[^>]+>', '', html_content)  # HTML 태그 제거
    text = re.sub(r'\s+', ' ', text)  # 연속된 공백 제거
    return text.strip()

def extract_korean_text(html_text):
    # 정규 표현식을 사용하여 한글만 추출
    korean_text = re.findall(r'[가-힣\s]+', html_text)
    # 추출된 한글 문자열을 하나의 문자열로 결합
    result = ''.join(korean_text).strip()
    return result

def refine_answer(text):
    text = re.sub(r'\b주인\w*', '보호사님', text)
    
    if text.startswith("답변:"):
        text = text[len("답변:"):].strip()
    
    last_index = max(text.rfind('!'), text.rfind('.'), text.rfind('?'))
    if last_index != -1:
        text = text[:last_index + 1].strip()
    
    return text

def refine_info(species, sex):
    result_species = "고양이" if species == "CAT" else "강아지"
    result_sex = "여성" if sex == "W" else "남성"
    return result_species, result_sex

from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

def call_api(animal_num, post):
    key = settings.ANIMAL_API_KEY
    url = f"http://openapi.seoul.go.kr:8088/{key}/json/TbAdpWaitAnimalPhotoView/1/387/"
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch data from API, status code: {response.status_code}")
        return
    
    data = response.json()
    photo_urls = []
    for item in data['TbAdpWaitAnimalPhotoView']['row']:
        if item['ANIMAL_NO'] == str(animal_num):
            photo_url = item['PHOTO_URL'].replace('&amp;', '&')
            full_url = f"https://{photo_url}"
            photo_urls.append(full_url)

    if len(photo_urls) < 4:
        logger.warning(f"Not enough photos found for animal number: {animal_num}")
        return

    images = []
    for item in random.sample(photo_urls, 4):
        image_response = requests.get(item)
        if image_response.status_code == 200:
            images.append(image_response.content)
        else:
            logger.error(f"Failed to download image from {item}")

    for i, image in enumerate(images):
        image_io = BytesIO(image)
        image_file = InMemoryUploadedFile(
            file=image_io,
            field_name=None,
            name=f"{animal_num}_{i}.jpg",  # 고유한 파일 이름 생성
            content_type='image/jpeg',
            size=image_io.getbuffer().nbytes,
            charset=None
        )
        PostImage.objects.create(post=post, image=image_file)


def llm_post(user):
    try:
        print("llm_post 시작")
        if user.char_num == -1:
            user.char_num = random.randrange(0, 5)
        logger.info(f"Starting llm_post for user: {user.username}")

        print(f"user: {user.username}, char_num: {user.char_num}")
        
        profile = ProfileSerializer(user)
        profile_data = profile.data

        template = """
        Knowledge:
        - 종: {species}
        - 이름: {nickname}
        - 성별: {sex}
        - 정보: {bio}

        Persona
        - 이제, 너가 Knowledge에 설명된 인물이라 생각하고 대화해줘.
        - 상대방과 자연스럽게 대화해야 해. 또한 친근하고 유머러스한 말투를 사용해야 해.
        - 금지어: '주인', '주인님'.
        - 이 단어들을 사용하지 않고도 상대방과 친근하고 유머러스하게 대화할 수 있어. 이 규칙을 지키면 대화가 훨씬 매끄럽고 재미있어질 거야.
        - 200~300자 정도로 아래 질문에 답변해줘.

        질문: {query}
        """

        prompt_template = PromptTemplate.from_template(template)

        print("PromptTemplate 생성 완료")

        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        llm = LlamaCpp(
            model_path=MODEL_PATH,
            n_gpu_layers=-1,
            n_batch=1024,
            f16_kv=True,
            callback_manager=callback_manager,
            verbose=True,
            n_threads=8,
            temperature=0.7,
            n_ctx=4096
        )

        print("LlamaCpp 모델 초기화 완료")

        num = user.char_num
        species, sex = refine_info(profile_data['profile']['species'], profile_data['profile']['sex'])
        input_data = {
            'species': species,
            'nickname': profile_data['profile']['nickname'],
            'sex': sex,
            'bio': extract_korean_text(profile_data['profile']['bio'])[:200],
            'query': "오늘 너의 일상을 얘기해줘."
        }

        prompt = prompt_template.format(**input_data)
        print(f"Prompt 생성 완료: {prompt}")

        logger.info(f"Generated prompt: {prompt}")

        logger.info("Generating post content")
        print("LlamaCpp 모델에 프롬프트 전달 중...")
        response = llm.invoke(prompt)
        response = refine_answer(response)
        print(f"생성된 응답: {response[:100]}")  # 처음 100자만 출력

        logger.info(f"Generated post content for user {user.username}: {response[:100]}...")
        
        post = Post(user=user, content=response.strip(), view_count=0)
        post.save()
        logger.info(f"Post saved for user {user.username} with ID: {post.id}")
        print(f"Post 저장 완료: {post.id}")
        
        if hasattr(user, 'animaluser'):
            print('-'*50)
            print(user.animaluser)
            call_api(user.animaluser.animal_num, post)
            print("API 호출 완료")
        else:
            logger.warning(f"No AnimalUser associated with user: {user.username}")

        return post
    
    except Exception as e:
        logger.error(f"An error occurred during post creation for user {user.username}: {str(e)}")
        logger.error(traceback.format_exc())  # 에러의 스택 트레이스를 로그에 기록
        print(f"에러 발생: {e}")
        print(traceback.format_exc())

User = get_user_model()

def update_animals():
    logger.info("Starting update_animals function")
    users = User.objects.filter(is_animal=True)[:5]
    logger.info(f"Found {len(users)} animal users to update")
    
    for user in users:
        try:
            post = llm_post(user)
            if post:
                logger.info(f"Successfully created post for user {user.username}: {post.id}")
        except Exception as e:
            logger.error(f"Error creating post for user {user.username}: {str(e)}")
            logger.error(traceback.format_exc())  # 전체 스택 트레이스 로깅

if __name__ == "__main__":
    logger.info("Script started")
    update_animals()
    logger.info("Script completed")
