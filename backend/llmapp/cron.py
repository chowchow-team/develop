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


# Add the project root to the Python path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

current_dir = os.path.dirname(os.path.abspath(__file__)) #'/develop/backend'
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# Set up Django
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

def llm_post(user):
    if user.char_num == -1:
        user.char_num = random.randrange(0,7)
    logger.info(f"Starting llm_post for user: {user.username}")
    # 프롬프트 템플릿 설정
    profile = ProfileSerializer(user)
    profile_data = profile.data
    template = """요청: {question}
    답변: 사용자의 요청을 정확하게 반영하여 답변합니다."""
    prompt = PromptTemplate.from_template(template)

    # 콜백 관리자를 설정하여 출력 스트리밍 지원
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    # GPU 가속 관련 설정
    n_gpu_layers = -1  # GPU에 할당할 레이어 수
    n_batch = 1024  # 배치 크기

    # LlamaCpp 모델 초기화
    llm = LlamaCpp(
        model_path=MODEL_PATH,
        n_gpu_layers=n_gpu_layers,  # GPU 레이어 수 설정
        n_batch=n_batch,  # 배치 크기 설정
        f16_kv=True,  # f16_kv 설정 활성화 
        callback_manager=callback_manager,  # 콜백 관리자 설정
        verbose=True,  # 자세한 로그 출력을 위해 활성화
        n_threads=8,  # 스레드 수 설정 
    )
    
    characters = ["쾌활하지만 철학적인 사고를 자주함","음식을 좋아하는 미식가임. 음식의 특징을 잘 파악하며 소탈할 말투로 음식 리뷰글을 씀",
                  "망상을 자주하는 INFP임", "문학적 감각이 뛰어나고 일기를 짧은 시처럼 씀", "집순이로 밖에 나가기를 싫어함", "재밌는 사행시를 잘 지음",
                  "아재 개그를 자주힘"]
    output_styles = ["""
    허허,,, 저랑은 좀,, 반대네요,,, 손주 학교 앞에 가면,,, 형이냐구 막;;; 물어보던디;;; ㅎㅎㅎ,,,
    자랑은 아닙니다,, ㅎㅎㅎ 젊게 사는 게 좋지요~~,, 꽃 한 송이 놓구 갑니다~~@>~~~~
    """,
    """
    ✨오리젠✨

    평점: 8.5/10

    닭, 칠면조, 계란의 조합으로 만들어진 사료는 달콤하면서도 단백질 함량이 높아 맛의 밸런스가 뛰어난 조합이었소. 
    신선하고 단백질이 풍부한 사료가 먹고 싶다면 이 제품을 추천하오. 일반사료에 비해 씹는 맛이 있었소.
    """,
    """
    뻘하게 갖고 싶은 능력들

    1. 이빨에 치석을 제거하는 능력
    2. 발톱이 항상 적정 길이로 유지되는 능력
    3. 털에 묻은 물이 바로 마르는 능력
    4. 스파이 패밀리의 본드 포저처럼 미래를 예지하는 능력
    5. 웰레스와 그로밋의 그로밋처럼 계산을 잘하는 능력
    """,
    f"""
    배식소

                        {profile_data['profile']['nickname']}
    유기견 보호사는 항상 많이 먹으라한다.

    많이 줘야 많이 먹지...
    """,
    f"""
    뚱냥이: {profile_data['profile']['nickname']}

    아침부터 "너 산책 가기 싫어?"라는 말을 들었다.

    진정 나를 잘 이해하는 유기견 보호사와 함께 지내고 있다.
    """,

    """
    아: 아버지
    나: 나를 낳으시고
    바: 바지석삼
    다: 다 적시셨네.
    """,
    """
    돼지가 떨어지면?







    돈벼락
    """,
    ]

    # 0에서 6 사이의 랜덤한 정수를 생성
    num = user.char_num
    if True:
        # 입력 데이터
        logger.info(f"Animal profile data: {profile_data}")
        input_text = f"""종: {profile_data['profile']['species']}
        이름: {profile_data['profile']['nickname']}
        성별: {profile_data['profile']['sex']}
        현재시간: 오후 1시
        성격: {characters[num]}
        """

        prompt = f"""
        {input_text}

        이제, 마치 너가 {input_text}에 설명된 인물이라 생각하고, SNS에 올릴 짧고 일상적인 글을 작성해줘. 이 글은 약 200자 정도로, 쾌활하면서도 철학적인 사고를 반영해야 해. 또한, 아래의 예시와 같은 친근하고 유머러스한 말투를 사용해야 해.

        스타일 예시:
        {output_styles[num]}

        이제 글을 작성해줘.
        """
        print(f"prompt: {prompt}")

        logger.info("Generating post content")
        # 모델에 프롬프트를 전달하고 응답을 받음
        response = llm.invoke(prompt)

        logger.info(f"Generated post content for user {user.username}: {response[:100]}...")  # 처음 100자만 로깅
        post = Post(user=user, content=response.strip(), view_count=0)
        post.save()
        logger.info(f"Post saved for user {user.username} with ID: {post.id}")

        return post

User = get_user_model()

def update_animals():
    logger.info("Starting update_animals function")
    logger.info(f"Current working directory: {os.getcwd()}")
    users = User.objects.filter(is_animal=True)
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