import os
import torch
import numpy as np
from torch.utils.data import Dataset
from PIL import Image
import cv2  # 더 빠른 이미지 처리

class LungDataset(Dataset):
    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform

        self.image_list = sorted(os.listdir(image_dir))
        self.mask_list = sorted(os.listdir(mask_dir))
        
        # 🔍 추가: 데이터셋 크기 확인
        print(f"📊 데이터셋 크기: {len(self.image_list)}개")
        
        # 🔍 추가: 파일 매칭 확인
        if len(self.image_list) != len(self.mask_list):
            print(f"⚠️ 경고: 이미지({len(self.image_list)})와 마스크({len(self.mask_list)}) 개수 불일치")
    
    def __len__(self):
        return len(self.image_list)
    
    def __getitem__(self, idx):
        try:
            image_path = os.path.join(self.image_dir, self.image_list[idx])
            mask_path = os.path.join(self.mask_dir, self.mask_list[idx])

            # 🔥 최적화: PIL 대신 cv2 사용 (더 빠름)
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            
            # numpy array를 PIL로 변환 (transform 호환성)
            image = Image.fromarray(image)
            mask = Image.fromarray(mask)

            if self.transform:
                image = self.transform(image)
                mask = self.transform(mask)
            
            return image, mask
            
        except Exception as e:
            print(f"❌ 데이터 로드 오류 (idx={idx}): {e}")
            # 오류 시 더미 데이터 반환
            dummy_image = torch.zeros(1, 256, 256)
            dummy_mask = torch.zeros(1, 256, 256)
            return dummy_image, dummy_mask
