# train_unet_with_mlflow.py

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import mlflow
import mlflow.pytorch
import torchvision.transforms as T
import os
from unet import UNet
from dataset import LungDataset
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="Chest-X-Ray", help="Data directory")
parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
parser.add_argument("--num_epochs", type=int, default=5, help="Number of epochs")
args = parser.parse_args()

image_dir = os.path.join(args.data_dir, "image")
mask_dir = os.path.join(args.data_dir, "mask")

# 하이퍼파라미터
num_epochs = args.num_epochs
batch_size = args.batch_size
lr = args.lr

# 장치 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 데이터셋
transform = T.Compose([
    T.Resize((256, 256)),
    T.ToTensor()
])
dataset = LungDataset(image_dir, mask_dir, transform=transform)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# 모델 & 학습 설정
model = UNet().to(device)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

# MLflow 설정
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("unet-lung-segmentation")

with mlflow.start_run():
    mlflow.log_param("lr", lr)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("epochs", num_epochs)

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0

        for images, masks in loader:
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)
            loss = criterion(outputs, masks)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(loader)
        print(f"[Epoch {epoch+1}] Loss: {avg_loss:.4f}")
        mlflow.log_metric("loss", avg_loss, step=epoch)

    # 모델 저장
    mlflow.pytorch.log_model(model, "model")

    # 예측 이미지 저장
    model.eval()
    sample, _ = next(iter(loader))
    with torch.no_grad():
        pred = model(sample.to(device))
    pred_np = pred[0][0].cpu().numpy()
    import matplotlib.pyplot as plt
    os.makedirs("outputs", exist_ok=True)
    plt.imsave("outputs/predicted.png", pred_np, cmap='gray')
    mlflow.log_artifact("outputs/predicted.png")
