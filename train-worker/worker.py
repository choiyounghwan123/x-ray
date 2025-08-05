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
        
        # data_dir 추가 (PVC 마운트 경로에 맞춤)
        mapped_args.append("--data_dir=/data")

        # Job 스펙
        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=job_name, labels={"job": job_name, "pr-number": str(pr)}),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"job": job_name, "pr-number": str(pr)}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="trainer",
                                image=image,
                                command=["python", "train_unet_with_mlflow.py"],
                                args=mapped_args,
                                resources=client.V1ResourceRequirements(
                                    limits={"nvidia.com/gpu": "1"}  # GPU 요청
                                ),
                                env=[
                                    client.V1EnvVar(name="NVIDIA_VISIBLE_DEVICES", value="all"),
                                    client.V1EnvVar(name="NVIDIA_DRIVER_CAPABILITIES", value="compute,utility"),
                                    client.V1EnvVar(
                                name="AWS_ACCESS_KEY_ID",
                                    value_from=client.V1EnvVarSource(
                                    secret_key_ref=client.V1SecretKeySelector(
                        name="mlflow-minio-credentials",
                key="aws-access-key-id"
            )
        )
    ),
    client.V1EnvVar(
        name="AWS_SECRET_ACCESS_KEY",
        value_from=client.V1EnvVarSource(
            secret_key_ref=client.V1SecretKeySelector(
                name="mlflow-minio-credentials",
                key="aws-secret-access-key"
            )
        )
    ),
    client.V1EnvVar(
        name="AWS_DEFAULT_REGION",
        value_from=client.V1EnvVarSource(
            secret_key_ref=client.V1SecretKeySelector(
                name="mlflow-minio-credentials",
                key="aws-default-region"
            )
        )
    ),
    
    # MLflow S3 엔드포인트 (공개 설정)
    client.V1EnvVar(name="MLFLOW_S3_ENDPOINT_URL", value="http://minio-service:30001")
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="training-data",
                                        mount_path="/data",
                                        read_only=True
                                    ),
                                    # GPU Device Files
                                    client.V1VolumeMount(name="nvidia0", mount_path="/dev/nvidia0"),
                                    client.V1VolumeMount(name="nvidiactl", mount_path="/dev/nvidiactl"),
                                    client.V1VolumeMount(name="nvidia-uvm", mount_path="/dev/nvidia-uvm"),
                                    client.V1VolumeMount(name="nvidia-uvm-tools", mount_path="/dev/nvidia-uvm-tools"),
                                    client.V1VolumeMount(name="nvidia-modeset", mount_path="/dev/nvidia-modeset"),
                                    # NVIDIA Binaries
                                    client.V1VolumeMount(name="nvidia-smi", mount_path="/usr/bin/nvidia-smi"),
                                    # NVIDIA Libraries
                                    client.V1VolumeMount(name="libcuda-so-1", mount_path="/usr/lib/x86_64-linux-gnu/libcuda.so.1"),
                                    client.V1VolumeMount(name="libnvidia-ml-so-1", mount_path="/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1")
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="training-data",
                                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name="training-data-pvc-v2"
                                )
                            ),
                            # GPU Device Files
                            client.V1Volume(name="nvidia0", host_path=client.V1HostPathVolumeSource(path="/dev/nvidia0")),
                            client.V1Volume(name="nvidiactl", host_path=client.V1HostPathVolumeSource(path="/dev/nvidiactl")),
                            client.V1Volume(name="nvidia-uvm", host_path=client.V1HostPathVolumeSource(path="/dev/nvidia-uvm")),
                            client.V1Volume(name="nvidia-uvm-tools", host_path=client.V1HostPathVolumeSource(path="/dev/nvidia-uvm-tools")),
                            client.V1Volume(name="nvidia-modeset", host_path=client.V1HostPathVolumeSource(path="/dev/nvidia-modeset")),
                            # NVIDIA Binaries
                            client.V1Volume(name="nvidia-smi", host_path=client.V1HostPathVolumeSource(path="/usr/bin/nvidia-smi")),
                            # NVIDIA Libraries
                            client.V1Volume(name="libcuda-so-1", host_path=client.V1HostPathVolumeSource(path="/usr/lib/x86_64-linux-gnu/libcuda.so.1")),
                            client.V1Volume(name="libnvidia-ml-so-1", host_path=client.V1HostPathVolumeSource(path="/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1"))
                        ],
                        restart_policy="Never",
                        node_selector={"accelerator": "nvidia"}
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