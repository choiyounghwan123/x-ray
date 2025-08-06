# 1. CUDA 지원 PyTorch 공식 이미지
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 시스템 패키지 설치 (이미지 처리용)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
 && rm -rf /var/lib/apt/lists/*

# 4. 필요한 Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        torchvision \
        mlflow \
        boto3 \
        requests \
        dotenv

# 5. 전체 코드 복사
COPY . .

# 6. 기본 실행 명령 설정
ENTRYPOINT  ["python", "train_classifier.py"]
