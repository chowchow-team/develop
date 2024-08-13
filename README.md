## Requirements
- python 3.11 
- git-lfs
- 50GB 이상 여유저장공간
```bash
# brew install git-lfs
```

## How to start
``` bash
0813: 자동화설정을 추가했음
1. develop/backend/.env 추가
2. chmod +x initialize.sh
3. ./initialize.sh
4. cd develop/backend
5. daphne -p 8000 backend.asgi:application
6. cd develop/frontend
7. npm start
```


쉘파일 실패 시:
``` bash
0. clone시 lfs 를 필요로 합니다.
git lfs install
git clone "~~~" 

1. 서버준비
cd backend
python -m venv venv
./venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

2. llm 모델 준비
cd llmapp
git clone https://github.com/ggerganov/llama.cpp
git clone https://huggingface.co/KISTI-KONI/KONI-Llama3-8B-Instruct-20240729 # 클론 시간 약 20분 걸립니다.
cd llama.cpp
LLAMA_METAL=1 make # mac m1 MPS 기준
pip install -r requirements.txt
python convert_hf_to_gguf.py ../KONI-8b
./llama-quantize ../KONI-8b/KONI-8B-F16.gguf q4_0

# 모델실행예시
./llama-cli -m ../KONI-8b/ggml-model-Q4_0.gguf -n 256 --repeat_penalty 1.0 --color -i -r "User:" -f prompts/chat-with-bob.txt


3. 서버실행
daphne -p 8000 backend.asgi:application

4. 크론탭 동작 설명
배포환경에서는 06시마다, 로컬에선 1분주기 accountapp/cron.py 작동시킴
python manage.py crontab add # 작동시작
python manage.py crontab show # 동작중인 크론탭현황
python manage.py crontab remove # 크론탭제거
# cron.log 로 로깅중임

```

test
