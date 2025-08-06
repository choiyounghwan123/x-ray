import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import mlflow
import mlflow.pytorch  # ✅ NEW
from dotenv import load_dotenv
import argparse

load_dotenv()
job_name = os.getenv("name")

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="Chest-X-Ray", help="Data directory")
parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
parser.add_argument("--num_epochs", type=int, default=5, help="Number of epochs")
args = parser.parse_args()

# 하이퍼파라미터
BATCH_SIZE = args.batch_size
EPOCHS = args.num_epochs
LR = args.lr
DATA_DIR = "data/chest_xray"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ MLflow 설정
mlflow.set_tracking_uri("http://mlflow-service:5000")
mlflow.set_experiment("Lung-Xray-Classifier")

# 이미지 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# 데이터셋
train_dataset = datasets.ImageFolder(root=os.path.join(DATA_DIR, "train"), transform=transform)
val_dataset = datasets.ImageFolder(root=os.path.join(DATA_DIR, "val"), transform=transform)
test_dataset = datasets.ImageFolder(root=os.path.join(DATA_DIR, "test"), transform=transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

num_classes = len(train_dataset.classes)
print("Classes:", train_dataset.classes)

model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# ✅ MLflow 실험 시작
with mlflow.start_run() as run:
    mlflow.set_tag("job_name", job_name)
    # 파라미터 로깅
    mlflow.log_param("batch_size", BATCH_SIZE)
    mlflow.log_param("epochs", EPOCHS)
    mlflow.log_param("lr", LR)
    mlflow.log_param("model", "resnet18")
    mlflow.log_param("dataset", "chest_xray")

    # 학습
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        for x, y in train_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            outputs = model(x)
            loss = criterion(outputs, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{EPOCHS}] Loss: {avg_loss:.4f}")
        mlflow.log_metric("train_loss", avg_loss, step=epoch)

    # 검증 함수
    def evaluate(model, loader, name="val"):
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                outputs = model(x)
                _, predicted = torch.max(outputs, 1)
                total += y.size(0)
                correct += (predicted == y).sum().item()
        acc = 100 * correct / total
        mlflow.log_metric(f"{name}_accuracy", acc)
        print(f"{name.capitalize()} Accuracy: {acc:.2f}%")
        return acc

    evaluate(model, val_loader, "val")
    evaluate(model, test_loader, "test")

    # 모델 artifact 저장
    mlflow.pytorch.log_model(model, artifact_path="model")
    print(f"✅ 모델 저장 완료: Run ID = {run.info.run_id}")
