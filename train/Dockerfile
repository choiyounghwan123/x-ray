# Dockerfile

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# 작업 디렉토리 설정
WORKDIR /app

# 코드 복사
COPY . .

# 필요한 패키지 설치 (torch는 이미 포함됨)
RUN pip install --upgrade pip && \
    pip install matplotlib mlflow boto3 dotenv

# 학습 실행
CMD ["python", "train_unet_with_mlflow.py"]
