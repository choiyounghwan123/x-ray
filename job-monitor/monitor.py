#!/usr/bin/env python3
"""
Kubernetes Job Monitor
쿠버네티스 잡의 완료 상태를 모니터링하고 완료 시 액션을 실행합니다.
"""

import os
import time
import logging
import json
import requests
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수에서 설정 로드
NAMESPACE = os.getenv('NAMESPACE', 'default')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')


class KubernetesJobMonitor:
    """쿠버네티스 잡 모니터링 클래스"""
    
    def __init__(self, namespace: str = None, kubeconfig_path: Optional[str] = None):
        """
        초기화
        
        Args:
            namespace: 모니터링할 네임스페이스
            kubeconfig_path: kubeconfig 파일 경로 (None이면 클러스터 내부 설정 사용)
        """
        self.namespace = namespace or NAMESPACE
        self.kubeconfig_path = kubeconfig_path
        self._load_kubernetes_config()
        self.batch_v1 = client.BatchV1Api()
        self.core_v1 = client.CoreV1Api()
        
    def _load_kubernetes_config(self):
        """쿠버네티스 설정 로드"""
        try:
            if self.kubeconfig_path:
                config.load_kube_config(config_file=self.kubeconfig_path)
                logger.info(f"Loaded kubeconfig from: {self.kubeconfig_path}")
            else:
                try:
                    # 클러스터 내부에서 실행되는 경우
                    config.load_incluster_config()
                    logger.info("Loaded in-cluster config")
                except:
                    # 로컬에서 실행되는 경우 기본 kubeconfig 사용
                    config.load_kube_config()
                    logger.info("Loaded default kubeconfig")
        except Exception as e:
            logger.error(f"Failed to load kubernetes config: {e}")
            raise

    def get_job_status(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        잡의 현재 상태를 조회
        
        Args:
            job_name: 조회할 잡 이름
            
        Returns:
            잡 상태 정보 딕셔너리 또는 None
        """
        try:
            job = self.batch_v1.read_namespaced_job(
                name=job_name, 
                namespace=self.namespace
            )
            
            status = {
                'name': job.metadata.name,
                'namespace': job.metadata.namespace,
                'creation_timestamp': job.metadata.creation_timestamp,
                'labels': job.metadata.labels or {},
                'active': job.status.active or 0,
                'succeeded': job.status.succeeded or 0,
                'failed': job.status.failed or 0,
                'completion_time': job.status.completion_time,
                'start_time': job.status.start_time,
                'conditions': []
            }
            
            if job.status.conditions:
                for condition in job.status.conditions:
                    status['conditions'].append({
                        'type': condition.type,
                        'status': condition.status,
                        'last_probe_time': condition.last_probe_time,
                        'last_transition_time': condition.last_transition_time,
                        'reason': condition.reason,
                        'message': condition.message
                    })
            
            return status
            
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Job '{job_name}' not found in namespace '{self.namespace}'")
                return None
            else:
                logger.error(f"Error getting job status: {e}")
                raise

    def is_job_completed(self, job_name: str) -> tuple[bool, str]:
        """
        잡이 완료되었는지 확인
        
        Args:
            job_name: 확인할 잡 이름
            
        Returns:
            (완료 여부, 완료 상태) - 상태: 'succeeded', 'failed', 'running', 'not_found'
        """
        status = self.get_job_status(job_name)
        
        if not status:
            return False, 'not_found'
        
        # 성공한 경우
        if status['succeeded'] > 0:
            return True, 'succeeded'
        
        # 실패한 경우
        if status['failed'] > 0:
            return True, 'failed'
        
        # 아직 실행 중인 경우
        if status['active'] > 0:
            return False, 'running'
        
        # 조건을 확인하여 완료 상태 판단
        for condition in status['conditions']:
            if condition['type'] == 'Complete' and condition['status'] == 'True':
                return True, 'succeeded'
            elif condition['type'] == 'Failed' and condition['status'] == 'True':
                return True, 'failed'
        
        return False, 'running'

    def wait_for_job_completion(
        self, 
        job_name: str, 
        timeout: int = 3600,
        check_interval: int = 30,
        on_completion: Optional[Callable[[str, Dict], None]] = None
    ) -> tuple[bool, str]:
        """
        잡 완료까지 대기 (폴링 방식)
        
        Args:
            job_name: 대기할 잡 이름
            timeout: 최대 대기 시간 (초)
            check_interval: 체크 간격 (초)
            on_completion: 완료 시 호출할 콜백 함수
            
        Returns:
            (완료 여부, 완료 상태)
        """
        logger.info(f"Waiting for job '{job_name}' to complete...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            completed, status = self.is_job_completed(job_name)
            
            if completed:
                logger.info(f"Job '{job_name}' completed with status: {status}")
                
                if on_completion:
                    job_info = self.get_job_status(job_name)
                    on_completion(status, job_info)
                
                return True, status
            
            logger.info(f"Job '{job_name}' is still {status}. Checking again in {check_interval} seconds...")
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for job '{job_name}' to complete")
        return False, 'timeout'

    def watch_job_completion(
        self, 
        job_name: str,
        timeout: int = 3600,
        on_completion: Optional[Callable[[str, Dict], None]] = None
    ) -> tuple[bool, str]:
        """
        잡 완료를 실시간으로 감지 (Watch API 사용)
        
        Args:
            job_name: 감시할 잡 이름
            timeout: 최대 대기 시간 (초)
            on_completion: 완료 시 호출할 콜백 함수
            
        Returns:
            (완료 여부, 완료 상태)
        """
        logger.info(f"Watching job '{job_name}' for completion...")
        
        w = watch.Watch()
        start_time = time.time()
        
        try:
            for event in w.stream(
                self.batch_v1.list_namespaced_job,
                namespace=self.namespace,
                field_selector=f"metadata.name={job_name}",
                timeout_seconds=timeout
            ):
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout watching job '{job_name}'")
                    w.stop()
                    return False, 'timeout'
                
                job = event['object']
                event_type = event['type']
                
                logger.debug(f"Event: {event_type}, Job: {job.metadata.name}")
                
                # 잡 상태 확인
                completed, status = self.is_job_completed(job_name)
                
                if completed:
                    logger.info(f"Job '{job_name}' completed with status: {status}")
                    w.stop()
                    
                    if on_completion:
                        job_info = self.get_job_status(job_name)
                        on_completion(status, job_info)
                    
                    return True, status
                    
        except Exception as e:
            logger.error(f"Error watching job: {e}")
            w.stop()
            raise
        
        return False, 'unknown'

    def get_job_logs(self, job_name: str) -> str:
        """
        잡의 로그를 가져오기
        
        Args:
            job_name: 로그를 가져올 잡 이름
            
        Returns:
            잡의 로그 문자열
        """
        try:
            # 잡에서 생성된 파드 찾기
            pods = self.core_v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=f"job-name={job_name}"
            )
            
            logs = []
            for pod in pods.items:
                try:
                    pod_logs = self.core_v1.read_namespaced_pod_log(
                        name=pod.metadata.name,
                        namespace=self.namespace
                    )
                    logs.append(f"=== Pod: {pod.metadata.name} ===\n{pod_logs}")
                except Exception as e:
                    logs.append(f"=== Pod: {pod.metadata.name} ===\nError getting logs: {e}")
            
            return "\n\n".join(logs)
            
        except Exception as e:
            logger.error(f"Error getting job logs: {e}")
            return f"Error getting logs: {e}"


def comment_pr(pr_number: int, job_name: str, status: str):
    """GitHub PR에 댓글 추가"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        logger.warning("GitHub token or repo not configured")
        return
        
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
    
    try:
        resp = requests.post(url, json={"body": body}, headers=headers, timeout=10)
        if resp.status_code == 201:
            logger.info(f"✅ PR #{pr_number} 에 코멘트 완료")
        else:
            logger.error(f"❌ 코멘트 실패 {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Error commenting on PR: {e}")


def notify_github(job_name: str, status: str):
    """GitHub Repository Dispatch 이벤트 발송"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        logger.warning("GitHub token or repo not configured")
        return
        
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

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 204:
            logger.info(f"Notification sent to GitHub for job {job_name} with status {status}")
        else:
            logger.error(f"Failed to send notification to GitHub for job {job_name}. "
                        f"Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logger.error(f"Error sending GitHub notification: {e}")


def example_completion_handler(status: str, job_info: Dict[str, Any]):
    """잡 완료 시 실행될 예제 핸들러"""
    logger.info("=" * 50)
    logger.info("JOB COMPLETION HANDLER CALLED")
    logger.info(f"Status: {status}")
    logger.info(f"Job Name: {job_info['name']}")
    logger.info(f"Namespace: {job_info['namespace']}")
    logger.info(f"Start Time: {job_info['start_time']}")
    logger.info(f"Completion Time: {job_info['completion_time']}")
    logger.info(f"Succeeded: {job_info['succeeded']}")
    logger.info(f"Failed: {job_info['failed']}")
    
    # GitHub 알림 발송
    notify_github(job_info['name'], status)
    
    # 여기에 잡 완료 후 실행하고 싶은 작업을 추가하세요
    if status == 'succeeded':
        logger.info("✅ Job completed successfully! Executing post-completion tasks...")
        # 예: 모델 아티팩트 정리, 알림 발송, 다음 파이프라인 단계 실행 등
        
    elif status == 'failed':
        logger.error("❌ Job failed! Executing failure handling tasks...")
        # 예: 에러 로그 수집, 알림 발송, 롤백 작업 등
    
    logger.info("=" * 50)


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kubernetes Job Monitor')
    parser.add_argument('job_name', help='Name of the job to monitor')
    parser.add_argument('--namespace', default=NAMESPACE, help='Kubernetes namespace')
    parser.add_argument('--kubeconfig', help='Path to kubeconfig file')
    parser.add_argument('--timeout', type=int, default=3600, help='Timeout in seconds')
    parser.add_argument('--check-interval', type=int, default=30, help='Check interval for polling mode')
    parser.add_argument('--mode', choices=['poll', 'watch'], default='watch', 
                       help='Monitoring mode: poll (polling) or watch (real-time)')
    parser.add_argument('--show-logs', action='store_true', help='Show job logs on completion')
    parser.add_argument('--pr-number', type=int, help='PR number to comment on completion')
    
    args = parser.parse_args()
    
    # 모니터 초기화
    monitor = KubernetesJobMonitor(
        namespace=args.namespace,
        kubeconfig_path=args.kubeconfig
    )
    
    # 완료 핸들러 정의
    def completion_handler(status: str, job_info: Dict[str, Any]):
        example_completion_handler(status, job_info)
        
        # PR 댓글 추가
        if args.pr_number:
            comment_pr(args.pr_number, args.job_name, status)
        
        if args.show_logs:
            logger.info("Fetching job logs...")
            logs = monitor.get_job_logs(args.job_name)
            print("\n" + "=" * 80)
            print("JOB LOGS:")
            print("=" * 80)
            print(logs)
            print("=" * 80)
    
    # 모니터링 시작
    try:
        if args.mode == 'watch':
            completed, status = monitor.watch_job_completion(
                job_name=args.job_name,
                timeout=args.timeout,
                on_completion=completion_handler
            )
        else:
            completed, status = monitor.wait_for_job_completion(
                job_name=args.job_name,
                timeout=args.timeout,
                check_interval=args.check_interval,
                on_completion=completion_handler
            )
        
        if completed:
            logger.info(f"Monitoring completed. Final status: {status}")
        else:
            logger.warning(f"Monitoring ended without completion. Status: {status}")
            
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
    except Exception as e:
        logger.error(f"Error during monitoring: {e}")
        raise


if __name__ == "__main__":
    main()
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

        if status.succeeded == 1:
            print(f"Job {name} completed successfully.")
            comment_pr(int(pr_str), name, "success")
        elif status.failed == 1:
            print(f"Job {name} failed.")
            comment_pr(int(pr_str), name, "failure")


if __name__ == '__main__':
    main()
