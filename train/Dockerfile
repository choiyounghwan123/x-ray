# Dockerfile2313

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# 작업 디렉토리 설정
WORKDIR /app

# 코드 복사
COPY . .

# 🔥 NumPy 버전 호환성 해결 + 시스템 라이브러리
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install "numpy>=1.21.0,<2.0.0" --force-reinstall \
    && pip install matplotlib mlflow boto3 python-dotenv opencv-python-headless psutil

# 학습 실행
CMD ["python", "train_unet_with_mlflow.py"]
