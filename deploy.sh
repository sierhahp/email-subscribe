#!/bin/bash

# Cloud Run Deployment Script for Email Subscription Service
# Usage: ./deploy.sh <PROJECT_ID> <JOB_ID> <REGION> <BUCKET_NAME> [CORS_ORIGINS]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 4 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: ./deploy.sh <PROJECT_ID> <JOB_ID> <REGION> <BUCKET_NAME> [CORS_ORIGINS]"
    echo ""
    echo "Example:"
    echo "  ./deploy.sh my-project job8 us-central1 my-subscribers-bucket https://mysite.com"
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
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Job ID: ${JOB_ID}"
echo "Region: ${REGION}"
echo "Bucket: ${BUCKET_NAME}"
echo "CORS Origins: ${CORS_ORIGINS}"
echo "Service Name: ${SERVICE_NAME}"
echo ""

# Step 1: Build Docker image
echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
docker build -t ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 2: Push to GCR
echo -e "${YELLOW}Step 2: Pushing image to Google Container Registry...${NC}"
docker push ${IMAGE_NAME}

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to push image${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Image pushed successfully${NC}"
echo ""

# Step 3: Deploy to Cloud Run
echo -e "${YELLOW}Step 3: Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --region ${REGION} \
  --allow-unauthenticated \
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
echo -e "${YELLOW}https://${SERVICE_NAME}-${REGION}.run.app${NC}"
echo ""
echo "API Endpoints:"
echo "  - POST https://${SERVICE_NAME}-${REGION}.run.app/subscribe"
echo "  - GET  https://${SERVICE_NAME}-${REGION}.run.app/health"
echo "  - GET  https://${SERVICE_NAME}-${REGION}.run.app/schema"
echo "  - GET  https://${SERVICE_NAME}-${REGION}.run.app/data"
echo ""
echo "Frontend Integration:"
echo "  Update index.html WEBHOOK_URL to:"
echo "  https://${SERVICE_NAME}-${REGION}.run.app/subscribe"
echo ""
echo "Data will be stored in:"
echo "  gs://${BUCKET_NAME}/subscribers/${JOB_ID}/emails.jsonl"
echo ""
echo "To set up a proxy, route:"
echo "  /api/${JOB_ID}/* → https://${SERVICE_NAME}-${REGION}.run.app/*"
echo ""

