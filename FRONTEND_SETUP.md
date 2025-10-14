# Frontend Setup Guide

This guide explains how to use the `index.html` subscription form with your deployed email subscription service.

## Quick Setup

### Step 1: Deploy the Backend

Deploy your email subscription service to Cloud Run:

```bash
./deploy.sh your-project-id job8 us-central1 your-bucket https://your-site.com
```

After deployment, you'll get a URL like:
```
https://email-subscribe-job8-HASH.run.app
```

### Step 2: Configure the Frontend

Open `index.html` and update the `WEBHOOK_URL` constant:

```javascript
// Option 1: Direct Cloud Run URL (requires CORS setup)
const WEBHOOK_URL = "https://email-subscribe-job8-HASH.run.app/subscribe";

// Option 2: Proxy URL (recommended, no CORS issues)
const WEBHOOK_URL = "/api/job8/subscribe";
```

### Step 3: Host the Frontend

You have several options:

#### Option A: Static Hosting (Recommended)
Host `index.html` on your main website:
- GitHub Pages
- Netlify
- Vercel
- Cloudflare Pages
- Your existing web server

#### Option B: Same Domain as API
If you set up a proxy (see below), you can host `index.html` on the same domain.

#### Option C: Test Locally
For testing, you can open `index.html` directly in a browser:
```bash
open index.html
```

## Proxy Setup (Recommended)

To avoid CORS issues and keep everything under your domain:

### 1. Set up a proxy in your CDN/Edge

Configure your edge (Cloudflare, Cloud Run, etc.) to proxy:
```
/api/{job_id}/*  →  https://email-subscribe-{job_id}-HASH.run.app/*
```

### 2. Update index.html

```javascript
const WEBHOOK_URL = "/api/YOUR_JOB_ID/subscribe";
```

### Example: Cloudflare Workers Proxy

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  
  // Proxy /api/job8/* to Cloud Run
  if (url.pathname.startsWith('/api/job8/')) {
    const targetUrl = 'https://email-subscribe-job8-HASH.run.app' + url.pathname.replace('/api/job8', '')
    const modifiedRequest = new Request(targetUrl, request)
    return fetch(modifiedRequest)
  }
  
  // Serve index.html for root
  if (url.pathname === '/') {
    return new Response(htmlContent, {
      headers: { 'Content-Type': 'text/html' }
    })
  }
  
  return new Response('Not Found', { status: 404 })
}
```

## Configuration Options

### Delivery Mode

The form supports two delivery modes:

```javascript
// JSON mode (default)
const DELIVERY_MODE = "json";

// Form-encoded mode
const DELIVERY_MODE = "form";
```

### CORS Configuration

If calling Cloud Run directly, ensure your backend has the correct CORS origins:

```bash
gcloud run services update email-subscribe-YOUR_JOB_ID \
  --set-env-vars CORS_ORIGINS=https://your-site.com,https://www.your-site.com
```

## Testing

### Test Locally

1. Deploy the backend
2. Update `index.html` with the Cloud Run URL
3. Open `index.html` in a browser
4. Try subscribing with a test email

### Test with cURL

```bash
curl -X POST https://email-subscribe-job8-HASH.run.app/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "source": "test",
    "subscribed_at": "2024-01-15T10:30:00Z"
  }'
```

### Verify Data Storage

Check that emails are being stored:

```bash
gsutil cat gs://your-bucket/subscribers/job8/emails.jsonl
```

## Customization

### Styling

The form uses CSS custom properties for easy theming:

```css
:root {
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 14px rgba(0,0,0,.08);
}

button {
  background: #111827;
}
```

### Spam Protection

The form includes a honeypot field to prevent bot submissions:

```html
<input id="hp" name="company" type="text" 
       autocomplete="organization" 
       tabindex="-1" 
       aria-hidden="true" 
       style="position:absolute;left:-9999px;" />
```

Bots that fill this field are silently accepted without being stored.

## Troubleshooting

### CORS Errors

**Problem**: Browser blocks the request due to CORS

**Solutions**:
1. Use a proxy (recommended)
2. Set `CORS_ORIGINS` environment variable on Cloud Run
3. Add your domain to the allowed origins

### Form Not Submitting

**Problem**: Clicking submit does nothing

**Check**:
1. Browser console for JavaScript errors
2. Network tab for failed requests
3. `WEBHOOK_URL` is correctly set

### Emails Not Being Stored

**Problem**: Form submits successfully but no data in GCS

**Check**:
1. GCS bucket exists and is accessible
2. Service account has Storage permissions
3. `JOB_ID` environment variable is set correctly
4. Cloud Run logs: `gcloud run logs read email-subscribe-YOUR_JOB_ID`

## Security Considerations

1. **Rate Limiting**: Consider adding rate limiting to prevent abuse
2. **Email Validation**: The backend validates emails, but frontend validation is also included
3. **HTTPS Only**: Always use HTTPS in production
4. **Content Security Policy**: Add CSP headers if needed
5. **API Keys**: The current setup is public. Add authentication if needed

## Next Steps

- Add email verification (double opt-in)
- Integrate with email service (SendGrid, Mailgun, etc.)
- Add analytics tracking
- Implement A/B testing
- Add more form fields (name, preferences, etc.)

