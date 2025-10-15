# Docker Installation Guide

If you want to use the local Docker deployment method, you need to install Docker first.

## macOS Installation

### Option 1: Docker Desktop (Recommended)

1. **Download Docker Desktop:**
   - Visit: https://www.docker.com/products/docker-desktop
   - Or use Homebrew: `brew install --cask docker`

2. **Install and Start:**
   - Open the downloaded `.dmg` file
   - Drag Docker to Applications
   - Launch Docker Desktop from Applications
   - Wait for Docker to start (whale icon in menu bar)

3. **Verify Installation:**
   ```bash
   docker --version
   docker ps
   ```

### Option 2: Colima (Lightweight Alternative)

Colima is a lighter alternative to Docker Desktop:

```bash
# Install via Homebrew
brew install colima docker docker-compose

# Start Colima
colima start

# Verify
docker --version
```

## Alternative: Use Cloud Build (No Docker Required)

If you don't want to install Docker locally, use the Cloud Build deployment script instead:

```bash
./deploy-cloudbuild.sh your-project-id job8 us-central1 your-bucket "https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app"
```

This script uses Google Cloud Build to build your Docker image in the cloud, so you don't need Docker installed locally.

## Troubleshooting

### Docker not found after installation

1. **Restart your terminal** after installing Docker Desktop
2. **Check PATH**: Docker should be in `/usr/local/bin/docker`
3. **Restart Docker Desktop** if it's not running

### Permission denied errors

On macOS, Docker Desktop handles permissions automatically. If you see permission errors:

1. Make sure Docker Desktop is running
2. Try restarting Docker Desktop
3. Check that your user is in the `docker` group (should be automatic on macOS)

### Docker Desktop won't start

1. Check system requirements (macOS 10.15+)
2. Ensure virtualization is enabled in System Preferences
3. Try reinstalling Docker Desktop
4. Check Docker Desktop logs: `~/Library/Containers/com.docker.docker/Data/log/`

## Which Method to Use?

| Method | Pros | Cons |
|--------|------|------|
| **Local Docker** (`deploy.sh`) | Faster iterations, test locally | Requires Docker installation |
| **Cloud Build** (`deploy-cloudbuild.sh`) | No local setup, simpler | Slightly slower first build |

**Recommendation**: Use Cloud Build (`deploy-cloudbuild.sh`) for simplicity, or install Docker Desktop if you want to test containers locally.

