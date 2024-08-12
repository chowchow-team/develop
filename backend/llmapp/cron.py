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

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')
django.setup()

from accountapp.serializers import ProfileSerializer
from mainapp.models import Post
from mainapp.serializers import PostSerializer

def extract_text_from_html(html_content):
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', html_content)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def llm_post(user):
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
        model_path="./llm/EEVEQ4.gguf",  # 모델 경로를 정확히 입력
        n_gpu_layers=n_gpu_layers,  # GPU 레이어 수 설정
        n_batch=n_batch,  # 배치 크기 설정
        f16_kv=True,  # f16_kv 설정 활성화 
        callback_manager=callback_manager,  # 콜백 관리자 설정
        verbose=True,  # 자세한 로그 출력을 위해 활성화
        n_threads=20,  # 스레드 수 설정 
    )

    # 입력 데이터
    print(f"동물의 프로필은: {profile_data}")
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

    #prompt = f"{input_text}이정보가 너에 대한 정보야. 너가 이 정보의 인물이라고 가정하고, 200자 정도 짧은 일상글을 생성하는게 너의 목표야. 글은 1인칭으로 작성되어야해. 말투는 아래와 같이 해야해: {output_style}"
    #prompt = f"{input_text}위 정보를 바탕으로 해당 동물의 페르소나를 가지고 300자 정도의 짧은 일상글을 생성해주세요. 1인칭 시점에서 작성해주세요."

    prompt = f"""
    {input_text}

    이제, 마치 너가 {input_text}에 설명된 인물이라 생각하고, SNS에 올릴 짧고 일상적인 글을 작성해줘. 이 글은 약 200자 정도로, 쾌활하면서도 철학적인 사고를 반영해야 해. 또한, 아래의 예시와 같은 친근하고 유머러스한 말투를 사용해야 해.

    스타일 예시:
    {output_style}

    이제 글을 작성해줘.
    """

    # 모델에 프롬프트를 전달하고 응답을 받음
    response = llm.invoke(prompt)

    # 결과 출력
    post = Post(user=user, content=response.strip(), view_count=0)
    post.save()  # 데이터베이스에 저장

    return post

User = get_user_model()

def update_animals():
    users = User.objects.filter(is_animal=True)[:5]
    print(users or None)
    # llm_post 함수가 이제 Post 객체를 반환하여 자동으로 저장합니다.
    for user in users:
        post = llm_post(user)
        print(f"Post created for user {user.username}: {post.content}")

if __name__ == "__main__":
    update_animals()


