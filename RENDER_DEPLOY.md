# Deploy to Render

## Quick Deploy to Render

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Add your GitHub repository
git remote add origin YOUR_GITHUB_REPO_URL

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy to Render

1. **Go to Render**: https://render.com
2. **Sign up/Login** (free account)
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repository**
5. **Configure:**
   - **Name**: `email-subscribe`
   - **Environment**: `Docker`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Dockerfile Path**: `./Dockerfile`
6. **Add Environment Variables:**
   - `GCS_BUCKET` = `email-subscribers-1760399688`
   - `JOB_ID` = `job8`
   - `CORS_ORIGINS` = `http://127.0.0.1:5501,http://localhost:5501`
   - `PORT` = `8080`
7. **Click "Create Web Service"**

### Step 3: Update Your Frontend

Once deployed, Render will give you a URL like:
```
https://email-subscribe.onrender.com
```

Update `index.html`:
```javascript
const WEBHOOK_URL = "https://email-subscribe.onrender.com/subscribe";
```

### Step 4: Test!

Open your `index.html` and test the subscription form!

---

## Alternative: Railway (Manual Login Required)

If you prefer Railway:

1. **Run this command in your terminal:**
   ```bash
   npx @railway/cli login
   ```
   (This will open a browser for authentication)

2. **Then run:**
   ```bash
   npx @railway/cli init
   npx @railway/cli up
   ```

3. **Add environment variables in Railway dashboard:**
   - `GCS_BUCKET` = `email-subscribers-1760399688`
   - `JOB_ID` = `job8`
   - `CORS_ORIGINS` = `http://127.0.0.1:5501,http://localhost:5501`

---

## Which to Choose?

- **Render**: Easier setup, free tier, auto-deploy from GitHub
- **Railway**: More flexible, also free tier, requires CLI login

Both work great! I recommend Render for simplicity.

