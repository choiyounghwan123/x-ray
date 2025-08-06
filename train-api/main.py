from fastapi import FastAPI, Request
from dotenv import load_dotenv
import redis
import os
import json
import uuid

# 환경변수 로드
load_dotenv()

app = FastAPI()

# Redis 연결
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=0
)

@app.post("/train")
async def train_endpoint(request: Request):
    payload = await request.json()
    
    job_id = str(uuid.uuid4())[:8]

    job = {
        "job_id": job_id,
        "pr": payload.get("pr"),
        "repo": payload.get("repo"),
        "sha": payload.get("sha"),
        "image": payload.get("image", "fdgdfgdgf123/train-img:latest"),
        "command": payload.get("command", ["python", "train_unet_with_mlflow.py"]),
        "params": payload.get("params", {"epochs": 3})
    }

    r.rpush("training_jobs", json.dumps(job))

    return {"status": "queued", "job_id": job_id}
