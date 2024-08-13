#!/bin/bash

# 오류 발생시 스크립트 중단
set -e

error_exit() {
    echo "Error: $1" >&2
    exit 1
}

path=$(pwd)

python3 -m venv ivenv || error_exit "Failed to create virtual environment"
. ivenv/bin/activate || error_exit "Failed to activate virtual environment"
pip3 install -r "$path/backend/requirements.txt" || error_exit "Failed to install requirements"

# llama-cpp-python (Metal 지원) > cpu 버전 설치된 상태일 경우 삭제 후 Metal 지원 버전 설치하도록함
CMAKE_ARGS="-DLLAMA_METAL=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir || error_exit "Failed to install llama-cpp-python with Metal support"

cd "$path/backend" || error_exit "Failed to change directory to backend"
python3 manage.py makemigrations || error_exit "Failed to make migrations"
python3 manage.py migrate || error_exit "Failed to apply migrations"

cd "$path/frontend" || error_exit "Failed to change directory to frontend"
npm install || error_exit "Failed to install npm packages"

echo "Setup completed successfully!"

# daphne -p 8000 backend.asgi:application &
# npm start