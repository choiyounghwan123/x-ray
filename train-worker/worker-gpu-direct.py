import os
import redis
import json
import time
from kubernetes import client, config

print("[INFO] Starting train-worker (GPU Direct Mode)...")

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
config.load_incluster_config()

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

        # GPU를 직접 마운트하는 Job 스펙 (rootless Docker 호환)
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
                                # Dockerfile의 CMD 사용: python train_unet_with_mlflow.py
                                args=[f"--{k}={v}" for k, v in params.items()],
                                env=[
                                    client.V1EnvVar(name="NVIDIA_VISIBLE_DEVICES", value="all"),
                                    client.V1EnvVar(name="LD_LIBRARY_PATH", value="/usr/lib/x86_64-linux-gnu")
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(name="nvidia-dev", mount_path="/dev"),
                                    client.V1VolumeMount(name="nvidia-libs", mount_path="/usr/lib/x86_64-linux-gnu", read_only=True),
                                    client.V1VolumeMount(name="nvidia-bin", mount_path="/usr/bin", read_only=True)
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="nvidia-dev",
                                host_path=client.V1HostPathVolumeSource(path="/dev")
                            ),
                            client.V1Volume(
                                name="nvidia-libs", 
                                host_path=client.V1HostPathVolumeSource(path="/usr/lib/x86_64-linux-gnu")
                            ),
                            client.V1Volume(
                                name="nvidia-bin",
                                host_path=client.V1HostPathVolumeSource(path="/usr/bin")
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
        print(f"[+] Created GPU job: {job_name}")

    except Exception as e:
        print(f"[!] Error: {e}")
        time.sleep(3) 