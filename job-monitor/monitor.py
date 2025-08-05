from kubernetes import client, config, watch
from dotenv import load_dotenv
import requests
import os
import time
# asafsdfdf
load_dotenv()
NAMESPACE = 'default'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
print("TOKEN:", GITHUB_TOKEN)  
print("REPO:", GITHUB_REPO)
def comment_pr(pr_number: int, job_name: str, status: str):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    body = (
        f"### 🔔 Training **{status.upper()}**\n"
        f"- **Job name:** `{job_name}`\n"
        f"- **Finished at:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    resp = requests.post(url, json={"body": body}, headers=headers, timeout=10)
    if resp.status_code == 201:
        print(f"✅ PR #{pr_number} 에 코멘트 완료")
    else:
        print(f"❌ 코멘트 실패 {resp.status_code}: {resp.text}")

def notify_github(job_name, status):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    data = {
        "event_type": "training_completed",
        "client_payload": {
            "job_name": job_name,
            "status": status
        }
    }

    response = requests.post(url,json=data, headers=headers)

    if response.status_code == 204:
        print(f"Notification sent to GitHub for job {job_name} with status {status}.")
    else:
        print(f"Failed to send notification to GitHub for job {job_name}. Status code: {response.status_code}, Response: {response.text}")

def main():
    try:
        config.load_incluster_config()
        print("Loaded kube config from within the cluster.")
    except Exception as e:
        config.load_kube_config()
        print("Loaded kube config from local machine.")    

    batch_v1 = client.BatchV1Api()
    watcher = watch.Watch()

    for event in watcher.stream(batch_v1.list_namespaced_job, namespace=NAMESPACE):
        job = event['object']
        name = job.metadata.name
        status = job.status
        labels = job.metadata.labels or {}
        pr_str = labels.get("pr-number")
        print(pr_str)
        if status.succeeded == 1:
            print(f"Job {name} completed successfully.")
            comment_pr(int(pr_str), name, "success")
        elif status.failed == 1:
            print(f"Job {name} failed.")
            comment_pr(int(pr_str), name, "failure")
        # 실행중인 잡
        elif status.active == 1:
            print(f"Job {name} is still running.")
            comment_pr(int(pr_str), name, "running")
            continue
        else:
            print(f"Job {name} is in an unknown state.")


if __name__ == '__main__':
    main()
