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
  "https://your-site.com"
```

### Method B: Local Docker

If you have Docker installed:

```bash
./deploy.sh \
  YOUR_PROJECT_ID \
  job8 \
  us-central1 \
  ${BUCKET_NAME} \
  "https://your-site.com"
```

> **Don't have Docker?** Use Method A or see [INSTALL_DOCKER.md](INSTALL_DOCKER.md)

## Step 4: Update Your Frontend

After deployment, you'll get a URL like:
```
https://email-subscribe-job8-HASH.run.app
```

### Option A: Direct Cloud Run URL

1. Open `index.html`
2. Find this line:
   ```javascript
   const WEBHOOK_URL = "https://WEBHOOK_URL_HERE";
   ```
3. Replace with your Cloud Run URL:
   ```javascript
   const WEBHOOK_URL = "https://email-subscribe-job8-HASH.run.app/subscribe";
   ```

### Option B: Proxy URL (Recommended)

If you set up a proxy at `/api/job8/*`:

```javascript
const WEBHOOK_URL = "/api/job8/subscribe";
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
curl -X POST https://email-subscribe-job8-HASH.run.app/subscribe \
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

