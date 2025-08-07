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
from dotenv import load_dotenv
import numpy as np
import matplotlib.pyplot as plt

load_dotenv()
job_name = os.getenv("name")

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="Chest-X-Ray", help="Data directory")
parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
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
print(f"🚀 Using device: {device}")

def overlay_mask_on_image(image, mask, alpha=0.4, mask_color=(1, 0, 0)):
    """
    오버레이 시각화 함수
    image: (H, W) numpy array, grayscale image [0,1]
    mask: (H, W) binary numpy array [0,1]
    alpha: blending ratio (0~1)
    mask_color: RGB tuple (default red)
    """
    image_rgb = np.stack([image]*3, axis=-1)  # (H, W, 3)
    color_mask = np.zeros_like(image_rgb)
    for c in range(3):
        color_mask[..., c] = mask * mask_color[c]
    blended = (1 - alpha) * image_rgb + alpha * color_mask
    return blended

def calculate_dice_score(y_true, y_pred, smooth=1):
    """Dice coefficient 계산"""
    y_true_f = y_true.flatten()
    y_pred_f = y_pred.flatten()
    intersection = np.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (np.sum(y_true_f) + np.sum(y_pred_f) + smooth)

def evaluate_and_visualize(model, test_loader, device, num_samples=10):
    """평가 및 오버레이 시각화를 MLflow에 업로드"""
    
    model.eval()
    dice_scores = []
    
    print("📊 평가 및 시각화 시작...")
    
    with torch.no_grad():
        for i, (imgs, masks) in enumerate(test_loader):
            if i >= num_samples:
                break
                
            imgs, masks = imgs.to(device), masks.to(device)
            preds = model(imgs)
            
            # 첫 번째 샘플로 시각화 (배치 인덱스 사용)
            img = imgs[0][0].cpu().numpy()  # 첫 번째 이미지의 첫 번째 채널
            gt_mask = masks[0][0].cpu().numpy()  # 첫 번째 마스크의 첫 번째 채널
            pred_mask = (preds[0][0].cpu().numpy() > 0.5).astype(np.float32)
            
            # Dice Score 계산
            dice = calculate_dice_score(gt_mask, pred_mask)
            dice_scores.append(dice)
            
            # 오버레이 시각화
            overlay_gt = overlay_mask_on_image(img, gt_mask, alpha=0.5, mask_color=(0, 1, 0))    # 초록색
            overlay_pred = overlay_mask_on_image(img, pred_mask, alpha=0.5, mask_color=(1, 0, 0)) # 빨간색
            
            plt.figure(figsize=(12, 4))
            plt.subplot(1, 3, 1)
            plt.imshow(img, cmap='gray')
            plt.title("Input")
            plt.axis('off')
            
            plt.subplot(1, 3, 2)
            plt.imshow(overlay_gt)
            plt.title("GT Overlay")
            plt.axis('off')
            
            plt.subplot(1, 3, 3)
            plt.imshow(overlay_pred)
            plt.title("Prediction Overlay")
            plt.axis('off')
            
            plt.suptitle(f"Sample {i+1} (Dice: {dice:.3f})", fontsize=14)
            plt.tight_layout()
            
            # MLflow에 업로드
            mlflow.log_figure(plt.gcf(), f"test_results/sample_{i+1:03d}.png")
            plt.close()  # 메모리 절약
            
            print(f"📸 샘플 {i+1}/{num_samples} 업로드 완료 (Dice: {dice:.3f})")
    
    # 전체 성능 요약
    if dice_scores:
        avg_dice = sum(dice_scores) / len(dice_scores)
        mlflow.log_metric("test_avg_dice_score", avg_dice)
        
        # 성능 분포 차트
        plt.figure(figsize=(8, 5))
        plt.hist(dice_scores, bins=min(10, len(dice_scores)), alpha=0.7, color='skyblue', edgecolor='black')
        plt.axvline(avg_dice, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_dice:.3f}')
        plt.title('Dice Score Distribution')
        plt.xlabel('Dice Score')
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        mlflow.log_figure(plt.gcf(), "dice_score_distribution.png")
        plt.close()
        
        print(f"📈 전체 평균 Dice Score: {avg_dice:.3f}")
    
    return dice_scores

# 데이터셋 및 데이터로더 설정
transform = T.Compose([
    T.Resize((256, 256)),
    T.ToTensor()
])

dataset = LungDataset(image_dir, mask_dir, transform=transform)

# 데이터셋을 train/test로 분할 (80:20)
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

train_loader = DataLoader(
    train_dataset, 
    batch_size=batch_size,
    shuffle=True,
    num_workers=2,
    pin_memory=False,
    persistent_workers=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=batch_size,
    shuffle=False,
    num_workers=2,
    pin_memory=False,
    persistent_workers=True
)

print(f"📊 데이터셋: Train {len(train_dataset)}, Test {len(test_dataset)}")

# 모델 & 학습 설정
model = UNet().to(device)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

# MLflow 설정
mlflow.set_tracking_uri("http://mlflow-service:5000")
mlflow.set_experiment("unet-lung-segmentation")

with mlflow.start_run() as run:
    print(f"🔍 MLflow Run ID: {run.info.run_id}")
    
    # 태그 및 파라미터 로깅
    mlflow.set_tag("job_name", job_name)
    mlflow.log_param("lr", lr)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("epochs", num_epochs)
    mlflow.log_param("device", str(device))
    mlflow.log_param("train_size", len(train_dataset))
    mlflow.log_param("test_size", len(test_dataset))

    print("🚀 훈련 시작...")
    
    # 훈련 루프
    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0

        for batch_idx, (images, masks) in enumerate(train_loader):
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)
            loss = criterion(outputs, masks)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(train_loader)
        print(f"[Epoch {epoch+1}/{num_epochs}] Loss: {avg_loss:.4f}")
        mlflow.log_metric("train_loss", avg_loss, step=epoch)

    print("✅ 훈련 완료!")
    
    # 모델 저장
    mlflow.pytorch.log_model(model, "model")
    print("💾 모델 MLflow에 저장 완료")

    # 🖼️ 평가 및 오버레이 시각화
    dice_scores = evaluate_and_visualize(model, test_loader, device, num_samples=10)
    
    # 기존 단순 예측 이미지도 추가로 저장 (호환성)
    model.eval()
    sample, _ = next(iter(test_loader))
    with torch.no_grad():
        pred = model(sample.to(device))
    pred_np = pred[0][0].cpu().numpy()
    
    os.makedirs("outputs", exist_ok=True)
    plt.imsave("outputs/predicted.png", pred_np, cmap='gray')
    mlflow.log_artifact("outputs/predicted.png")
    
    print("🎉 모든 과정 완료! MLflow에서 결과를 확인하세요.")
    print(f"📊 MLflow Run: {run.info.run_id}")
