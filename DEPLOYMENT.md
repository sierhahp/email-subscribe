# Cloud Run Deployment Guide

## Prerequisites
- Google Cloud SDK installed
- Docker installed
- GCS bucket created for storing subscriber logs

## Build and Deploy

### 1. Build the Docker image
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/email-subscribe-YOUR_JOB_ID:latest .
```

### 2. Push to Google Container Registry
```bash
docker push gcr.io/YOUR_PROJECT_ID/email-subscribe-YOUR_JOB_ID:latest
```

### 3. Deploy to Cloud Run
```bash
gcloud run deploy email-subscribe-YOUR_JOB_ID \
  --image gcr.io/YOUR_PROJECT_ID/email-subscribe-YOUR_JOB_ID:latest \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars GCS_BUCKET=YOUR_BUCKET_NAME,JOB_ID=YOUR_JOB_ID,CORS_ORIGINS=https://your-site.com
```

### 4. Service URL
After deployment, your service will be available at:
```
https://email-subscribe-YOUR_JOB_ID-HASH.run.app
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GCS_BUCKET` | GCS bucket name for storing subscriber logs | Yes |
| `JOB_ID` | Job identifier for this deployment | Yes |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | No (defaults to *) |

## API Endpoints

- `POST /subscribe` - Subscribe an email address
- `GET /health` - Health check endpoint
- `GET /schema` - Get data schema
- `GET /data` - Get subscriber data (with limit/offset params)
- `GET /code` - List source files

## Proxy Setup (Recommended)

Configure your edge/CDN to proxy:
```
/api/{job_id}/*  →  https://email-subscribe-{id}-{hash}.run.app/*
```

Then update `index.html` to use:
```javascript
const WEBHOOK_URL = "/api/YOUR_JOB_ID/subscribe";
```

Or if calling Cloud Run directly, update `index.html`:
```javascript
const WEBHOOK_URL = "https://email-subscribe-YOUR_JOB_ID-HASH.run.app/subscribe";
```

This avoids CORS issues since requests go to your own domain.

## Data Storage

Subscriber data is stored in GCS at:
```
gs://YOUR_BUCKET/subscribers/{JOB_ID}/emails.jsonl
```

Format: JSON Lines (one JSON object per line)

## Optional Enhancements

### Idempotency (avoid duplicates)
Hash emails and store individually:
```
subscribers/{job_id}/by_email/{sha256}.json
```

### Higher Volume
Replace JSONL append with Pub/Sub → BigQuery pipeline

### Observability
Add monitoring and logging for:
- Request rates
- Error rates
- GCS write latency

## Testing

Test locally with Docker:
```bash
docker build -t email-subscribe .
docker run -p 8080:8080 \
  -e GCS_BUCKET=your-bucket \
  -e JOB_ID=test \
  -e CORS_ORIGINS=http://localhost:3000 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
  -v /path/to/key.json:/app/key.json \
  email-subscribe
```

Then test the endpoint:
```bash
curl -X POST http://localhost:8080/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","source":"test"}'
```

