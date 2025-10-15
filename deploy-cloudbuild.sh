#!/bin/bash

# Cloud Run Deployment Script using Cloud Build (no Docker required locally)
# Usage: ./deploy-cloudbuild.sh <PROJECT_ID> <JOB_ID> <REGION> <BUCKET_NAME> [CORS_ORIGINS]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 4 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: ./deploy-cloudbuild.sh <PROJECT_ID> <JOB_ID> <REGION> <BUCKET_NAME> [CORS_ORIGINS]"
    echo ""
    echo "Example:"
    echo "  ./deploy-cloudbuild.sh my-project job8 us-central1 my-subscribers-bucket https://email-subscribe-theta.vercel.app,https://email-subscribe-git-main-sierhahs-projects.vercel.app,https://email-subscribe-moatqed0u-sierhahs-projects.vercel.app"
    exit 1
fi

PROJECT_ID=$1
JOB_ID=$2
REGION=$3
BUCKET_NAME=$4
CORS_ORIGINS=${5:-"*"}

SERVICE_NAME="email-subscribe-${JOB_ID}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying Email Subscription Service${NC}"
echo -e "${GREEN}Using Cloud Build (no Docker required)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Job ID: ${JOB_ID}"
echo "Region: ${REGION}"
echo "Bucket: ${BUCKET_NAME}"
echo "CORS Origins: ${CORS_ORIGINS}"
echo "Service Name: ${SERVICE_NAME}"
echo ""

# Step 1: Set the project
echo -e "${YELLOW}Step 1: Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to set GCP project${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project set to ${PROJECT_ID}${NC}"
echo ""

# Step 2: Submit build to Cloud Build
echo -e "${YELLOW}Step 2: Building Docker image with Cloud Build...${NC}"
echo "This may take a few minutes..."

gcloud builds submit --tag ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Cloud Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Image built successfully${NC}"
echo ""

# Step 3: Deploy to Cloud Run
echo -e "${YELLOW}Step 3: Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --region ${REGION} \
  --no-allow-unauthenticated \
  --ingress internal-and-cloud-load-balancing \
  --set-env-vars GCS_BUCKET=${BUCKET_NAME},JOB_ID=${JOB_ID},CORS_ORIGINS=${CORS_ORIGINS} \
  --platform managed

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Cloud Run deployment failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your service is now available at:"
echo -e "${YELLOW}<your HTTPS Load Balancer host> (fronting ${SERVICE_NAME})${NC}"
echo ""
echo "API Endpoints:"
echo "  - POST https://<LB_HOST>/subscribe"
echo "  - GET  https://<LB_HOST>/health"
echo "  - GET  https://<LB_HOST>/schema"
echo "  - GET  https://<LB_HOST>/data"
echo ""
echo "Frontend Integration:"
echo "  Update index.html WEBHOOK_URL to:"
echo "  https://email-subscribe.onrender.com/subscribe (or your LB same-origin path)"
echo ""
echo "Data will be stored in:"
echo "  gs://${BUCKET_NAME}/subscribers/${JOB_ID}/emails.jsonl"
echo ""
echo "To set up a proxy, route:"
echo "  /api/${JOB_ID}/* → https://<LB_HOST>/*"
echo ""

