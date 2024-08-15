import sys
import os
import re
import time
import select
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from django.contrib.auth import get_user_model
import django
import logging
from django.conf import settings
import random


# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__)) #'/develop/backend'
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')
django.setup()

MODEL_PATH = os.path.join(current_dir, "llm", "EEVEQ4.gguf")

from accountapp.serializers import ProfileSerializer
from mainapp.models import Post
from mainapp.serializers import PostSerializer

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(settings.BASE_DIR, 'llm_post.log'))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def extract_text_from_html(html_content):
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', html_content)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_after_last_punctuation(s):
    # 마지막 '!', '.', '?'의 인덱스 찾기
    last_index = max(s.rfind('!'), s.rfind('.'), s.rfind('?'))
    
    # 구두점이 없으면 원래 문자열 반환
    if last_index == -1:
        return s
    
    # 마지막 구두점까지의 문자열 반환
    return s[:last_index + 1]

def refine_info(species,sex):
    result_species, result_sex = None, None
    if species=="CAT":
        result_species = "고양이"
    else:
        result_species = "강아지"
    if sex=="W":
        result_sex = "여성"
    else:
        result_sex = "남성"
    return result_species, result_sex

def llm_post(user):
    if user.char_num == -1:
        user.char_num = random.randrange(0,5)
    logger.info(f"Starting llm_post for user: {user.username}")
    # 프로파일 데이터 가져오기
    profile = ProfileSerializer(user)
    profile_data = profile.data

    template = """
    [Persona]
    - 당신은 **{nickname}**입니다.
    - 당신의 역할은 오늘 당신을 기쁘게한 일을 200~300자 분량의 글로 작성하는 것입니다.
    - 당신은 당신이 {species}점에 유의해서 {species}가 겪을 수 있는 현실적인 글을 작성해야 합니다.
    - 당신에게 유기동물이기 때문에 주인은 없고 당신을 돌보는 보호님이 있습니다. 이점을 신경써서 글을 작성합니다.

    """

    
    prompt_template = PromptTemplate.from_template(template)

    # 콜백 관리자를 설정하여 출력 스트리밍 지원
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    # LlamaCpp 모델 초기화
    llm = LlamaCpp(
        model_path=MODEL_PATH,
        n_gpu_layers=-1,  # GPU 레이어 수 설정
        n_batch=1024,  # 배치 크기 설정
        f16_kv=True,  # f16_kv 설정 활성화 
        callback_manager=callback_manager,  # 콜백 관리자 설정
        verbose=True,  # 자세한 로그 출력을 위해 활성화
        n_threads=8,  # 스레드 수 설정 
        temperature=0.5,
        n_ctx = 4096
    )

    # 성격 및 스타일 예시

    tones    = [
    # 표준어 종결어미
    ["-다", "-요", "-습니다", "-니", "-냐", "-세요", "-십시오", "-자", "-아요", "-어요", "-구나", "-군요", "-네"],
    
    # 경상도 사투리 종결어미
    ["-마소", "-합시데이", "-차리나", "-해삣다", "-가끼가"],
    
    # 전라도 사투리 종결어미
    ["-으까잉", "-여", "-능가", "-쓰까", "-하소"],
    
    # 충청도 사투리 종결어미
    ["-가유", "-굴러가유", "-해유", "-있쥬", "-봅세"],
    
    # 강원도 사투리 종결어미
    ["-드래요", "-굽소야", "-교", "-하대", "-오시우야"]
    ]

    num = user.char_num
    species, sex = refine_info(profile_data['profile']['species'],profile_data['profile']['sex'])
    input_data = {
        'species': species,
        'nickname': profile_data['profile']['nickname'],
        'sex': sex,
        #'bio': extract_text_from_html(profile_data['profile']['bio'])[:300],
        'tone': tones[num]
    }

    prompt = prompt_template.format(**input_data)
    print("!"*30)
    print(f"prompt:{prompt}")
    logger.info(f"Generated prompt: {prompt}")

    logger.info("Generating post content")
    # 모델에 프롬프트를 전달하고 응답을 받음
    response = llm.invoke(prompt)
    response = remove_after_last_punctuation(response)
    logger.info(f"Generated post content for user {user.username}: {response[:100]}...")  # 처음 100자만 로깅
    post = Post(user=user, content=response.strip(), view_count=0)
    post.save()
    logger.info(f"Post saved for user {user.username} with ID: {post.id}")


    return post

User = get_user_model()

def update_animals():
    logger.info("Starting update_animals function")
    logger.info(f"Current working directory: {os.getcwd()}")
    users = User.objects.filter(is_animal=True)[20:24]
    logger.info(f"Found {len(users)} animal users to update")
    for user in users:
        try:
            post = llm_post(user)
            logger.info(f"Successfully created post for user {user.username}: {post.id}")
        except Exception as e:
            logger.error(f"Error creating post for user {user.username}: {str(e)}")

if __name__ == "__main__":
    logger.info("Script started")
    logger.info(f"Current working directory: {os.getcwd()}")
    update_animals()
    logger.info("Script completed")
