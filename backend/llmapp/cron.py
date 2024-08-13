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
    logger.info(f"Starting llm_post for user: {user.username}")
    # 프롬프트 템플릿 설정
    profile = ProfileSerializer(user)
    profile_data = profile.data
    template = """Question: {question}
    Answer: Let's work this out in a step by step way to be sure we have the right answer."""
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
        n_threads=20,  # 스레드 수 설정 
    )

    # 입력 데이터
    logger.info(f"Animal profile data: {profile_data}")
    input_text = f"""종: {profile_data['profile']['species']}
    이름: {profile_data['profile']['nickname']}
    성별: {profile_data['profile']['sex']}
    현재시간: 오후 1시
    성격: 쾌활하지만 철학적인 사고를 자주함
    말투 예시: 
    """

    output_style="""
    허허,,, 저랑은 좀,, 반대네요,,, 손주 학교 앞에 가면,,, 형이냐구 막;;; 물어보던디;;; ㅎㅎㅎ,,,
    자랑은 아닙니다,, ㅎㅎㅎ 젊게 사는 게 좋지요~~,, 꽃 한 송이 놓구 갑니다~~@>~~~~
    """

    prompt = f"""
    {input_text}

    이제, 마치 너가 {input_text}에 설명된 인물이라 생각하고, SNS에 올릴 짧고 일상적인 글을 작성해줘. 이 글은 약 200자 정도로, 쾌활하면서도 철학적인 사고를 반영해야 해. 또한, 아래의 예시와 같은 친근하고 유머러스한 말투를 사용해야 해.

    스타일 예시:
    {output_style}

    이제 글을 작성해줘.
    """

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
    users = User.objects.filter(is_animal=True)[:5]
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