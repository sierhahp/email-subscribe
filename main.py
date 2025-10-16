import os
import io
import re
import json
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from google.cloud import storage
from sqlalchemy import text
from db import engine

JOB_ID = os.getenv("JOB_ID", "local")
BUCKET = os.getenv("GCS_BUCKET")  # optional if WRITE_GCS=false
WRITE_GCS = os.getenv("WRITE_GCS", "false").lower() == "true"
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
    try:
        with engine.begin() as conn:
            rows = conn.execute(text(
                """
                SELECT email, source, user_agent, job_id, subscribed_at, unsubscribed_at
                FROM subscribers
                ORDER BY subscribed_at DESC
                LIMIT :limit OFFSET :offset
                """
            ), {"limit": limit, "offset": offset}).mappings().all()
            total = conn.execute(text("SELECT COUNT(*) AS c FROM subscribers")).scalar_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    return {"rows": [dict(r) for r in rows], "total": total, "limit": limit, "offset": offset}

@app.get("/code")
def code():
    # Minimal to align with your GET /code endpoint
    return {"files": ["main.py", "requirements.txt", "dockerfile"]}

@app.post("/subscribe")
async def subscribe(payload: SubscribeIn, request: Request):
    record = payload.dict()
    if not record.get("subscribed_at"):
        record["subscribed_at"] = datetime.now(timezone.utc).isoformat()
    if not record.get("source"):
        record["source"] = str(request.headers.get("origin") or "")

    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO subscribers (email, source, user_agent, job_id, subscribed_at)
                VALUES (:email, :source, :ua, :job_id, :subscribed_at)
                ON CONFLICT (email_norm) DO UPDATE SET
                  source = COALESCE(EXCLUDED.source, subscribers.source),
                  user_agent = COALESCE(EXCLUDED.user_agent, subscribers.user_agent),
                  job_id = COALESCE(EXCLUDED.job_id, subscribers.job_id)
                """
                ),
                {
                    "email": record["email"],
                    "source": record.get("source"),
                    "ua": record.get("user_agent") or request.headers.get("user-agent"),
                    "job_id": JOB_ID,
                    "subscribed_at": record["subscribed_at"],
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if WRITE_GCS:
        try:
            _append_jsonl({
                "email": record["email"],
                "source": record.get("source"),
                "user_agent": record.get("user_agent") or request.headers.get("user-agent"),
                "job_id": JOB_ID,
                "subscribed_at": record["subscribed_at"],
            })
        except Exception as e:
            # Don't fail the request if optional GCS write fails
            pass

    return {"ok": True}


@app.get("/export.csv")
def export_csv():
    try:
        with engine.begin() as conn:
            rows = conn.execute(text(
                """
                SELECT email, source, user_agent, job_id, subscribed_at, unsubscribed_at
                FROM subscribers
                ORDER BY subscribed_at DESC
                """
            )).mappings().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    buf = io.StringIO()
    fieldnames = [
        "email",
        "source",
        "user_agent",
        "job_id",
        "subscribed_at",
        "unsubscribed_at",
    ]
    import csv

    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(dict(r))

    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=subscribers.csv"},
    )

