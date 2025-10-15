# Email Subscription Service

A FastAPI-based email subscription service that stores subscriber data in Google Cloud Storage. Designed for Cloud Run deployment with support for proxy routing and CORS.

## Features

- ✅ RESTful API for email subscriptions
- ✅ GCS-backed JSONL storage
- ✅ CORS support for web frontends
- ✅ Health check and monitoring endpoints
- ✅ Schema and data retrieval endpoints
- ✅ Docker containerized for Cloud Run
- ✅ Idempotent storage (prevents duplicates)

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GCS_BUCKET=your-bucket-name
export JOB_ID=local-test
export CORS_ORIGINS=http://localhost:3000
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

3. Run the service:
```bash
uvicorn main:app --reload --port 8080
```

4. Test the endpoint:
```bash
curl -X POST http://localhost:8080/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","source":"local-test"}'
```

### Docker Deployment

#### Option 1: Cloud Build (No Docker Required - Recommended)

Use Cloud Build to build your image in the cloud (no local Docker needed):

```bash
./deploy-cloudbuild.sh <PROJECT_ID> <JOB_ID> <REGION> <BUCKET_NAME> [CORS_ORIGINS]
```

Example:
```bash
./deploy-cloudbuild.sh my-project job8 us-central1 my-subscribers https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app
```

#### Option 2: Local Docker

If you have Docker installed locally:

```bash
./deploy.sh <PROJECT_ID> <JOB_ID> <REGION> <BUCKET_NAME> [CORS_ORIGINS]
```

Example:
```bash
./deploy.sh my-project job8 us-central1 my-subscribers https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app
```

> **Note**: If you don't have Docker installed, see [INSTALL_DOCKER.md](INSTALL_DOCKER.md) or use Option 1 above.

#### Manual deployment:

1. Build the Docker image:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/email-subscribe-YOUR_JOB_ID:latest .
```

2. Push to Google Container Registry:
```bash
docker push gcr.io/YOUR_PROJECT_ID/email-subscribe-YOUR_JOB_ID:latest
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy email-subscribe-YOUR_JOB_ID \
  --image gcr.io/YOUR_PROJECT_ID/email-subscribe-YOUR_JOB_ID:latest \
  --region YOUR_REGION \
  --no-allow-unauthenticated \
  --ingress internal-and-cloud-load-balancing \
  --set-env-vars GCS_BUCKET=YOUR_BUCKET,JOB_ID=YOUR_JOB_ID,CORS_ORIGINS=https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app
```

## API Endpoints

### POST /subscribe
Subscribe an email address.

**Request:**
```json
{
  "email": "user@example.com",
  "source": "landing-page",
  "subscribed_at": "2024-01-15T10:30:00Z",
  "user_agent": "Mozilla/5.0..."
}
```

**Response:**
```json
{
  "ok": true
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "job_id": "your-job-id"
}
```

### GET /schema
Get the data schema.

**Response:**
```json
{
  "columns": [
    {"name": "email", "type": "string"},
    {"name": "source", "type": "string"},
    {"name": "subscribed_at", "type": "string"},
    {"name": "user_agent", "type": "string"}
  ]
}
```

### GET /data
Retrieve subscriber data with pagination.

**Query Parameters:**
- `limit` (default: 100) - Number of records to return
- `offset` (default: 0) - Number of records to skip

**Response:**
```json
{
  "rows": [...],
  "total": 150,
  "limit": 100,
  "offset": 0
}
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GCS_BUCKET` | GCS bucket name for storing subscriber logs | Yes | - |
| `JOB_ID` | Job identifier for this deployment | No | `local` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | No | `*` |
| `PORT` | Server port | No | `8080` |

## Data Storage

Subscriber data is stored in GCS at:
```
gs://YOUR_BUCKET/subscribers/{JOB_ID}/emails.jsonl
```

Format: JSON Lines (one JSON object per line)

Example:
```jsonl
{"email":"user1@example.com","source":"landing-page","subscribed_at":"2024-01-15T10:30:00Z","user_agent":"Mozilla/5.0..."}
{"email":"user2@example.com","source":"blog","subscribed_at":"2024-01-15T11:45:00Z","user_agent":"Mozilla/5.0..."}
```

## Proxy Setup (Recommended)

To avoid CORS issues, put an external HTTPS Load Balancer in front of Cloud Run and proxy to the Load Balancer host (not the `run.app` URL):

```
/api/{job_id}/*  →  https://<YOUR-LB-HOSTNAME>/*
```

Then update `index.html` to use a same-origin path via your LB:
```javascript
const WEBHOOK_URL = "/api/YOUR_JOB_ID/subscribe"; // same-origin via your LB
```

### Expose via HTTPS Load Balancer (Serverless NEG)

Use an external HTTPS Load Balancer with a Serverless NEG that targets your private Cloud Run service.

- Backend: Serverless NEG → Cloud Run service
- Backend auth: Use a service account so the LB sends an identity token to Cloud Run
- Cloud Run ingress: `internal-and-cloud-load-balancing` (keeps service private)
- Domain: Point your site at the LB hostname, or route `/api/{job_id}/*` to the LB

This keeps browser requests same-origin (to the LB), and the LB calls Cloud Run with proper auth. Result: no CORS preflight failures, no unauthenticated calls blocked by org policy.

## Frontend Integration

### Using a proxy (recommended):
```javascript
const WEBHOOK_URL = "/api/YOUR_JOB_ID/subscribe";

async function subscribe(email) {
  const response = await fetch(WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email,
      source: window.location.href
    })
  });
  return response.json();
}
```

### Direct Cloud Run call
**Not supported** in organizations that block public access to Cloud Run. Use the HTTPS Load Balancer + Serverless NEG approach above. If you keep an example, clearly mark it as only for orgs that allow public Cloud Run.

## Project Structure

```
.
├── main.py                    # FastAPI application
├── index.html                 # Subscription form frontend
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image definition
├── deploy.sh                  # Local Docker deployment script
├── deploy-cloudbuild.sh       # Cloud Build deployment script (no Docker required)
├── .dockerignore              # Files to exclude from Docker build
├── .gcloudignore              # Files to exclude from Cloud Run
├── DEPLOYMENT.md              # Detailed deployment guide
├── FRONTEND_SETUP.md          # Frontend integration guide
├── INSTALL_DOCKER.md          # Docker installation guide
└── README.md                  # This file
```

## Optional Enhancements

### TL;DR of org-safe setup

- Deploy Cloud Run with `--no-allow-unauthenticated` and `--ingress internal-and-cloud-load-balancing`.
- Front Cloud Run with an external HTTPS Load Balancer using Serverless NEG.
- Configure backend authentication with a service account so the LB sends an identity token.
- Route your site (same-origin) or `/api/{job_id}/*` to the LB; call the API via same-origin.
- For local dev CORS, list exact origins and allow `POST`, `GET`, `OPTIONS`.

### Idempotency (avoid duplicates)
Hash emails and store individually:
```
subscribers/{job_id}/by_email/{sha256}.json
```

### Higher Volume
Replace JSONL append with Pub/Sub → BigQuery pipeline for better scalability.

### Monitoring
Add monitoring for:
- Request rates
- Error rates
- GCS write latency
- Response times

## Troubleshooting

### GCS Permission Errors
Ensure your service account has the following IAM roles:
- `Storage Object Creator`
- `Storage Object Viewer`

### CORS Guidance (local dev only)

If you still want to test cross-origin (e.g., calling the LB from `http://localhost:3000` or your Vercel domains):

- `CORS_ORIGINS` must list exact origins (scheme + host + optional port), comma-separated, no trailing slashes. Example: `http://localhost:3000,https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app`
- FastAPI `CORSMiddleware` should allow `POST`, `GET`, and `OPTIONS`, and headers `Content-Type`, `Authorization` (or `*`).
- Keep `allow_credentials=false` unless you truly send cookies/Authorization from the browser.
- Preflight 401/403 means auth blocked the OPTIONS probe. Fix by using HTTPS LB + Serverless NEG and calling same-origin path `/api/{job_id}/subscribe`.

### Troubleshooting → CORS

- Error: `Response to preflight request doesn't pass access control check` with status 401/403
  - Cause: Cloud Run requires auth; browser’s preflight is blocked.
  - Fix: Use HTTPS LB + Serverless NEG with backend auth; call same-origin path `/api/{job_id}/subscribe`.

- Error: `No 'Access-Control-Allow-Origin' header present` on a 200
  - Cause: Origin not in `CORS_ORIGINS`.
  - Fix: Add the exact origin, or use the same-origin proxy so CORS isn’t needed.

### TL;DR

- Change deploy flags: `--no-allow-unauthenticated` and `--ingress internal-and-cloud-load-balancing`.
- Add LB section with Serverless NEG + backend service account auth.
- Update proxy to hit the LB host and recommend same-origin calls.
- Remove/mark the direct Cloud Run example as not applicable for orgs blocking public Cloud Run.
- Tighten CORS notes (exact origins, methods/headers) for local dev only.

### Deployment Issues
1. Verify Docker image builds successfully
2. Check Cloud Run logs: `gcloud run logs read SERVICE_NAME --region REGION`
3. Verify environment variables are set correctly

## License

MIT

