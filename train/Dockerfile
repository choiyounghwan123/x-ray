FROM pytorch/pytorch:2.7.0-cuda12.1-cudnn8-runtime

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

COPY . .

# OpenCV, matplotlib 등 시각화/이미지 관련 시스템 라이브러리
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        matplotlib \
        mlflow \
        boto3 \
        python-dotenv \
        opencv-python-headless \
        psutil

CMD ["python", "train_unet_with_mlflow.py"]
