# Dockerfile

FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 코드 복사
COPY . .

# 필요한 패키지 설치
RUN pip install --upgrade pip && \
    pip install torch torchvision matplotlib mlflow

# 학습 실행
CMD ["python", "train_unet_with_mlflow.py"]
