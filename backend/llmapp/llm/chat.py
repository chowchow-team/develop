import os
import django
import sys
import re
from collections import deque
from datetime import datetime

from django.conf import settings
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')

django.setup()

MODEL_PATH = os.path.join(current_dir, "EEVEQ4.gguf")

from accountapp.serializers import ProfileSerializer

# 콜백 매니저 설정
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# LLM 모델 설정
n_gpu_layers = -1
n_batch = 1024
llm = None

# 채팅 로그
chat_log = deque(maxlen=10)

def get_llm():
    global llm
    if llm is None:
        model_path = MODEL_PATH
        try:
            llm = LlamaCpp(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_batch=n_batch,
                f16_kv=True,
                callback_manager=callback_manager,
                temperature=0.9,
                verbose=True,
                n_threads=16,
                max_tokens=100,
                n_ctx=1024
            )
        except FileNotFoundError:
            print(f"모델 파일을 찾을 수 없습니다. 경로를 확인해주세요: {model_path}")
            return None
        except Exception as e:
            print(f"모델 로딩 중 오류 발생: {e}")
            return None
    return llm

def remove_html_tags(text):
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def remove_after_last_punctuation(s):
    # 마지막 '!', '.', '?'의 인덱스 찾기
    last_index = max(s.rfind('!'), s.rfind('.'), s.rfind('?'))
    
    # 구두점이 없으면 원래 문자열 반환
    if last_index == -1:
        return s
    
    # 마지막 구두점까지의 문자열 반환
    return s[:last_index + 1]

def generate_prompt(profile_data, query):
    now = datetime.now()
    formatted_time = now.strftime("%p %I시")

    species = profile_data['profile']['kind']
    name = profile_data['profile']['nickname']
    gender = profile_data['profile']['sex']
    current_time = formatted_time
    personality = remove_html_tags(profile_data['profile']['bio'])[:100]

    output_style = """
    허허,,, 저랑은 좀,, 반대네요,,, 손주 학교 앞에 가면,,, 형이냐구 막;;; 물어보던디;;; ㅎㅎㅎ,,,
    자랑은 아닙니다,, ㅎㅎㅎ 젊게 사는 게 좋지요~~,, 꽃 한 송이 놓구 갑니다~~@>~~~~
    """

    input_text = f"""종: {species}
    이름: {name}
    성별: {gender}
    현재시간: {current_time}
    성격: {personality}
    말투 예시: {output_style}
    """
    
    bot_prompt = f"""
    {input_text}
    - 이제, 너가 위에서 설명된 인물이라 생각하고 대화해줘. 
    - 상대방과 자연스럽게 대화해야해. 또한 친근하고 유머러스한 말투를 사용해야 해.
    - 너무 길지않고 간단하게 말해야해.
    이제 질문에 대한 채팅답변을 작성해줘.

    질문: {query}
    """
    return bot_prompt

def chat(query, user):
    llm = get_llm()
    if llm is None:
        return "죄송합니다. 현재 챗봇 서비스를 이용할 수 없습니다."

    profile_serializer = ProfileSerializer(user)
    profile_data = profile_serializer.data
    bot_prompt = generate_prompt(profile_data, query)
    
    chatting = "\n".join(chat_log)
    current_chat = f"\nQ : {query}.\nA : "
    chatting += current_chat

    # 프롬프트가 너무 길지 않도록 조정
    print('**'*50)
    print(bot_prompt)
    if len(chatting) + len(bot_prompt) > 1024:
        excess_length = len(chatting) + len(bot_prompt) - 1024
        # 필요 시 chat_log에서 일부 오래된 대화 제거
        chatting = chatting[excess_length:]

    try:
        output = llm.invoke(bot_prompt + chatting, stop=["Q:", "\n"], echo=True)
        answer = output.strip().replace("A : ", "")
    except Exception as e:
        print(f"응답 생성 중 오류 발생: {e}")
        answer = "죄송합니다. 답변을 생성하는 데 문제가 발생했습니다."
    
    chat_log.append(f"Q : {query}\nA : {answer}")
    
    return remove_after_last_punctuation(answer)

if __name__ == "__main__":
    from django.contrib.auth import get_user_model

    User = get_user_model()
    
    try:
        username = "animal_4025"
        user = User.objects.get(username=username)
        
        query = "너의 이름이 무엇인지 알려줘"
        answer = chat(query, user)
        print(f"Bot >> {answer}")
        
    except User.DoesNotExist:
        print(f"Username '{username}'에 해당하는 사용자가 없습니다.")