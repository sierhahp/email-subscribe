import os
import io
import re
import json
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from google.cloud import storage

JOB_ID = os.getenv("JOB_ID", "local")
BUCKET = os.getenv("GCS_BUCKET")  # required
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]

app = FastAPI(title=f"newsletter-webhook-{JOB_ID}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["*"],
)

# Simple payload schema
class SubscribeIn(BaseModel):
    email: EmailStr
    source: str | None = None
    subscribed_at: str | None = None
    user_agent: str | None = None

EMAIL_OBJECT_PREFIX = f"subscribers/{JOB_ID}/"  # folder-like prefix in GCS
EMAIL_LOG_OBJECT = f"{EMAIL_OBJECT_PREFIX}emails.jsonl"  # append-only
SCHEMA_CACHE = {
    "fields": [
        {"name": "email", "type": "string"},
        {"name": "source", "type": "string"},
        {"name": "subscribed_at", "type": "string"},
        {"name": "user_agent", "type": "string"},
    ]
}

def _gcs_client():
    if not BUCKET:
        raise RuntimeError("GCS_BUCKET env var is required")
    return storage.Client(), BUCKET

def _append_jsonl(record: dict):
    client, bucket_name = _gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(EMAIL_LOG_OBJECT)

    # Ensure timestamp
    record = {**record}
    if not record.get("subscribed_at"):
        record["subscribed_at"] = datetime.now(timezone.utc).isoformat()

    line = json.dumps(record, ensure_ascii=False) + "\n"

    # If object exists, compose append
    if blob.exists():
        # Download existing then upload concatenated content for simplicity
        # For higher volume, switch to GCS compose API or PubSub
        prev = blob.download_as_bytes()
        blob.upload_from_string(prev + line.encode("utf-8"), content_type="application/x-ndjson")
    else:
        blob.upload_from_string(line, content_type="application/x-ndjson")

@app.get("/health")
def health():
    return {"status": "ok", "job_id": JOB_ID}

@app.get("/schema")
def schema():
    # Mirrors your pattern of exposing column info
    return {"columns": SCHEMA_CACHE["fields"]}

@app.get("/data")
def data(limit: int = 100, offset: int = 0):
    """Basic reader to match your standard GET /data pattern."""
    client, bucket_name = _gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(EMAIL_LOG_OBJECT)
    if not blob.exists():
        return {"rows": [], "total": 0}

    content = blob.download_as_text()
    rows = [json.loads(x) for x in content.splitlines() if x.strip()]
    total = len(rows)
    rows = rows[offset: offset + limit]
    return {"rows": rows, "total": total, "limit": limit, "offset": offset}

@app.get("/code")
def code():
    # Minimal to align with your GET /code endpoint
    return {"files": ["main.py", "requirements.txt", "dockerfile"]}

@app.post("/subscribe")
async def subscribe(payload: SubscribeIn, request: Request):
    # Basic duplicate of fields plus server-side source
    record = payload.dict()
    # Capture origin URL if not provided by client
    if not record.get("source"):
        record["source"] = str(request.headers.get("origin") or "")
    try:
        _append_jsonl(record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {e}")
    return {"ok": True}

