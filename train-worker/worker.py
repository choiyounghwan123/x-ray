import os
import redis
import json
import time
from kubernetes import client, config

print("[INFO] Starting train-worker...")

# Redis 설정
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

print(f"[INFO] Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

try:
    r.ping()
    print("[INFO] Redis connection successful")
except Exception as e:
    print(f"[ERROR] Redis connection failed: {e}")
    exit(1)

# K8s 클러스터 접근 설정
print("[INFO] Initializing Kubernetes client...")
config.load_incluster_config()  # 쿠버네티스 클러스터 안에서 실행할 경우

batch_v1 = client.BatchV1Api()

print("[INFO] Worker ready. Waiting for jobs...")
while True:
    try:
        print("[INFO] Waiting for jobs in training_jobs queue...")
        job_data = r.blpop("training_jobs", timeout=5)
        if not job_data:
            print("[DEBUG] No jobs in queue, waiting...")
            continue

        _, data = job_data
        print(f"[INFO] Received job: {data}")
        payload = json.loads(data)

        pr = payload["pr"]
        image = payload["image"]
        params = payload["params"]

        # Kubernetes Job 이름
        job_name = f"train-job-pr-{pr}"

        # 인자 이름 매핑 (스크립트의 정확한 인자명에 맞춤)
        arg_mapping = {
            "epochs": "num_epochs",
            "batch_size": "batch_size", 
            "lr": "lr",
            "data_dir": "data_dir"
        }
        
        # 매핑된 인자들로 변환
        mapped_args = []
        for k, v in params.items():
            arg_name = arg_mapping.get(k, k)
            mapped_args.append(f"--{arg_name}={v}")

        # Job 스펙
        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=job_name),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"job": job_name}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="trainer",
                                image=image,
                                command=["python", "train_unet_with_mlflow.py"],
                                args=mapped_args,
                                resources=client.V1ResourceRequirements(
                                    limits={"nvidia.com/gpu": "1"}  # GPU 요청
                                )
                            )
                        ],
                        restart_policy="Never"
                    )
                ),
                backoff_limit=2
            )
        )

        # Job 생성
        batch_v1.create_namespaced_job(namespace="default", body=job)
        print(f"[+] Created job: {job_name}")

    except Exception as e:
        print(f"[!] Error: {e}")
        time.sleep(3)
## 23112