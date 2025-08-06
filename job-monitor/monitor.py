from kubernetes import client, config, watch
from dotenv import load_dotenv
import requests
import os
import time

load_dotenv()

NAMESPACE = 'default'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
MLFLOW_URL = "http://mlflow-service:5000"
print("TOKEN:", GITHUB_TOKEN[:10] + "..." if GITHUB_TOKEN else "None")
print("REPO:", GITHUB_REPO)

def get_container_image(job):
    """Job에서 컨테이너 이미지 추출"""
    try:
        return job.spec.template.spec.containers[0].image
    except:
        return "unknown"

def extract_hyperparameters(job):
    """Job args에서 하이퍼파라미터 추출"""
    try:
        args = job.spec.template.spec.containers[0].args or []
        params = {}
        for arg in args:
            if "=" in arg and arg.startswith("--"):
                key, value = arg[2:].split("=", 1)
                params[key] = value
        return params
    except:
        return {}

def comment_pr(pr_number: int, job_name: str, status: str, job=None):
    # GitHub 코멘트 API
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    run_id = None
    artifact_url = None
    experiment_name = job.metadata.labels.get("experiment_name")
    print("experiment_name: ",experiment_name)
    #동적으로 experiment_id 찾기 mlflow에서 찾기
    mlflow_resp = requests.post(
    f"{MLFLOW_URL}/api/2.0/mlflow/experiments/search",
    headers={"Content-Type": "application/json"},
    json={
        "filter": f"name = '{experiment_name}'",
        "max_results": 1  # 꼭 명시해야 함!!
    },
    timeout=5
)
    
    mlflow_resp.raise_for_status()
    print(mlflow_resp.json())
    experiment_id = mlflow_resp.json()["experiments"][0]["experiment_id"]
        

    # ✅ MLflow에서 Run 찾기 (성공/실패일 때만 조회 시도)
    if status in ("success", "failure"):
        try:
            mlflow_resp = requests.post(
                f"{MLFLOW_URL}/api/2.0/mlflow/runs/search",
                headers={"Content-Type": "application/json"},
                json={
                    "experiment_ids": [experiment_id],
                    "filter": f'tags.job_name = "{job_name}"',
                    "max_results": 1,
                    "order_by": ["attributes.start_time DESC"]
                },
                timeout=5
            )
            mlflow_resp.raise_for_status()
            run = mlflow_resp.json()["runs"][0]
            run_id = run["info"]["run_id"]
            artifact_url = run["info"]["artifact_uri"]
        except Exception as e:
            print(f"[WARN] MLflow 검색 실패: {e}")

    # 코멘트 내용 구성
    now = time.strftime('%Y-%m-%d %H:%M:%S KST')
    body = ""

    if status == "started" and job:
        body = f"""### 🚀 Training **STARTED**
- **Job name:** `{job_name}`
- **Time:** {now}

### 🔧 Configuration
- **GPU:** 1x NVIDIA GPU
- **Image:** `{get_container_image(job)}`
- **Dataset:** `/data` (training-data-pvc-v2)
- **Namespace:** `{job.metadata.namespace}`
- **MLflow Experiment:** [{experiment_id}](http://localhost:30002/#/experiments/{experiment_id})
"""

        params = extract_hyperparameters(job)
        if params:
            body += "- **Hyperparameters:**\n"
            for k, v in params.items():
                body += f"  - `{k}`: {v}\n"

    elif status == "success":
        body = f"""### ✅ Training **SUCCESS**
- **Job name:** `{job_name}`
- **Time:** {now}

### 🎉 Results
- **Status:** Training completed successfully
- **MLflow Run:** [View Detailed Results]({MLFLOW_URL}/#/experiments/{experiment_id}/runs/{run_id})\n"""
        if artifact_url:
            body += f"- **Model Artifacts:** `{artifact_url}`\n"
        body += "- **Next Steps:** 🔍 Review metrics and approve for deployment\n"

    elif status == "failure":
        body = f"""### ❌ Training **FAILED**
- **Job name:** `{job_name}`
- **Time:** {now}

### 🔍 Troubleshooting
- **Status:** Training failed
- **Debug Commands:**
  - `kubectl logs job/{job_name}`
  - `kubectl describe job/{job_name}`
- **MLflow:** [View Failed Run]({MLFLOW_URL}/#/experiments/{experiment_id}/runs/{run_id})
- **Next Steps:** Check logs and retry with updated parameters\n"""

    else:
        emoji, text = {
            "running": ("🔄", "Training **RUNNING**"),
        }.get(status, ("📋", f"Training **{status.upper()}**"))

        body = f"""### {emoji} {text}
- **Job name:** `{job_name}`
- **Time:** {now}
"""

    # GitHub 코멘트 등록
    resp = requests.post(url, json={"body": body}, headers=headers, timeout=10)
    if resp.status_code == 201:
        print(f"✅ PR #{pr_number}에 '{status}' 코멘트 완료")
    else:
        print(f"❌ 코멘트 실패 {resp.status_code}: {resp.text}")
def mark_job_annotation(batch_v1, job, annotation_key):
    """Job에 어노테이션 추가 (중복 방지용)"""
    try:
        body = {
            "metadata": {
                "annotations": {annotation_key: "true"}
            }
        }
        batch_v1.patch_namespaced_job(
            name=job.metadata.name,
            namespace=job.metadata.namespace,
            body=body
        )
        print(f"Job {job.metadata.name}에 {annotation_key} 어노테이션 추가됨")
    except Exception as e:
        print(f"어노테이션 추가 실패: {e}")

def main():
    try:
        config.load_incluster_config()
        print("Loaded kube config from within the cluster.")
    except Exception as e:
        config.load_kube_config()
        print("Loaded kube config from local machine.")    

    batch_v1 = client.BatchV1Api()
    watcher = watch.Watch()
    
    print(f"👀 {NAMESPACE} 네임스페이스 Job 감시 시작...")

    for event in watcher.stream(batch_v1.list_namespaced_job, namespace=NAMESPACE):
        job = event['object']
        name = job.metadata.name
        status = job.status
        labels = job.metadata.labels or {}
        annos = job.metadata.annotations or {}
        print(name)
        # PR 번호 확인
        pr_str = labels.get("pr-number")
        if not pr_str:
            continue
            
        try:
            pr_number = int(pr_str)
        except ValueError:
            print(f"Job {name}: 잘못된 PR 번호 형식: {pr_str}")
            continue
        
        print(f"Job {name} (PR #{pr_number}) 상태 확인...")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 시작 알림 (Job이 처음 관측되었을 때)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if annos.get("started-commented") != "true":
            print(f"🚀 Job {name} 시작됨 - PR #{pr_number}에 알림")
            comment_pr(pr_number, name, "started", job)  # job 객체 전달
            mark_job_annotation(batch_v1, job, "started-commented")
            continue  # 시작 알림 후 이번 루프는 종료
            
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 완료 상태 처리 (성공/실패)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        print(status.succeeded and status.succeeded == 1)
        if status.succeeded and status.succeeded == 1:
            if annos.get("success-commented") != "true":
                print(f"✅ Job {name} 성공 완료 - PR #{pr_number}에 알림")
                comment_pr(pr_number, name, "success", job)  # job 객체 전달
                mark_job_annotation(batch_v1, job, "success-commented")
                
        elif status.failed and status.failed > 0:
            if annos.get("failure-commented") != "true":
                print(f"❌ Job {name} 실패 - PR #{pr_number}에 알림")
                comment_pr(pr_number, name, "failure", job)  # job 객체 전달
                mark_job_annotation(batch_v1, job, "failure-commented")

if __name__ == '__main__':
    main()
