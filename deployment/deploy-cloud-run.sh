#!/bin/bash

# Deploy Healthcare Conversational AI Platform to GCP Cloud Run

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"healthcare-ai-project"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="healthcare-conversational-ai"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Healthcare Conversational AI Platform"
echo "=================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Set the project
echo "📌 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Build the container image
echo "🏗️  Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 1 \
  --set-env-vars ENVIRONMENT=production

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "To test the health endpoint:"
echo "curl ${SERVICE_URL}/health"
