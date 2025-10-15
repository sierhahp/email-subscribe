# Quick Start Guide

Get your email subscription service up and running in 5 minutes!

## Prerequisites

- Google Cloud account with billing enabled
- Google Cloud SDK (`gcloud`) installed
- A GCS bucket for storing subscribers

## Step 1: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  storage-api.googleapis.com
```

## Step 2: Create a GCS Bucket

```bash
# Replace with your bucket name
BUCKET_NAME="my-email-subscribers-$(date +%s)"

# Create bucket
gsutil mb -l us-central1 gs://${BUCKET_NAME}

echo "Bucket created: gs://${BUCKET_NAME}"
```

## Step 3: Deploy the Service

Choose one of these methods:

### Method A: Cloud Build (Recommended - No Docker Required)

```bash
./deploy-cloudbuild.sh \
  YOUR_PROJECT_ID \
  job8 \
  us-central1 \
  ${BUCKET_NAME} \
  "https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app"
```

### Method B: Local Docker

If you have Docker installed:

```bash
./deploy.sh \
  YOUR_PROJECT_ID \
  job8 \
  us-central1 \
  ${BUCKET_NAME} \
  "https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app"
```

> **Don't have Docker?** Use Method A or see [INSTALL_DOCKER.md](INSTALL_DOCKER.md)

## Step 4: Update Your Frontend

After deployment, expose Cloud Run via an HTTPS Load Balancer (Serverless NEG). Use that LB host for your site’s same-origin calls, or use the Render backend URL below for direct calls.

### Option A: Same-origin via Load Balancer (Recommended)

1. Open `index.html`
2. Find this line:
   ```javascript
   const WEBHOOK_URL = "https://WEBHOOK_URL_HERE";
   ```
3. Replace with a same-origin path (proxied by your LB):
   ```javascript
   const WEBHOOK_URL = "/api/job8/subscribe";
   ```

### Option B: Direct to Render backend

```javascript
const WEBHOOK_URL = "https://email-subscribe.onrender.com/subscribe";
```

## Step 5: Host Your Frontend

Upload `index.html` to your website or use static hosting:

- **Netlify**: Drag and drop `index.html`
- **Vercel**: `vercel deploy`
- **GitHub Pages**: Push to a repo and enable Pages
- **Cloudflare Pages**: Connect your repo

## Step 6: Test It!

1. Open your hosted `index.html` page
2. Enter a test email
3. Click Subscribe
4. You should see "Thanks for subscribing!"

## Verify Data Storage

Check that emails are being stored:

```bash
# List files in your bucket
gsutil ls gs://${BUCKET_NAME}/subscribers/job8/

# View the emails file
gsutil cat gs://${BUCKET_NAME}/subscribers/job8/emails.jsonl
```

## Test the API Directly

```bash
curl -X POST https://email-subscribe.onrender.com/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "source": "manual-test",
    "subscribed_at": "2024-01-15T10:30:00Z"
  }'
```

## Common Issues

### "Docker not found"

Use the Cloud Build deployment method instead:
```bash
./deploy-cloudbuild.sh ...
```

### "Permission denied" on scripts

Make scripts executable:
```bash
chmod +x deploy-cloudbuild.sh
chmod +x deploy.sh
```

### CORS errors in browser

1. Check that `CORS_ORIGINS` includes your domain
2. Or set up a proxy (recommended)

### "Bucket not found" error

Make sure your bucket exists:
```bash
gsutil ls gs://YOUR_BUCKET_NAME
```

If not, create it:
```bash
gsutil mb -l us-central1 gs://YOUR_BUCKET_NAME
```

## Next Steps

- [ ] Set up email verification (double opt-in)
- [ ] Configure email delivery service (SendGrid, Mailgun, etc.)
- [ ] Add analytics tracking
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts

## Getting Help

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment info
- See [FRONTEND_SETUP.md](FRONTEND_SETUP.md) for frontend configuration
- Review [README.md](README.md) for complete documentation

## Cleanup

To delete everything:

```bash
# Delete Cloud Run service
gcloud run services delete email-subscribe-job8 --region us-central1

# Delete container image
gcloud container images delete gcr.io/YOUR_PROJECT_ID/email-subscribe-job8

# Delete bucket (careful - this deletes all data!)
gsutil rm -r gs://YOUR_BUCKET_NAME
```

