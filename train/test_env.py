#!/usr/bin/env python3

import os

print("=== 환경변수 확인 ===")
print(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'NOT SET')}")
print(f"MLFLOW_S3_ENDPOINT_URL: {os.environ.get('MLFLOW_S3_ENDPOINT_URL', 'NOT SET')}")

if os.environ.get('AWS_ACCESS_KEY_ID') == 'mlflow':
    print("✅ 환경변수가 자동으로 설정되었습니다!")
else:
    print("❌ 환경변수가 설정되지 않았습니다.") 