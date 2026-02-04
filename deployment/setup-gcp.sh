#!/bin/bash

# Setup GCP resources for Healthcare Conversational AI Platform

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"healthcare-ai-project"}
REGION=${GCP_REGION:-"us-central1"}

echo "🔧 Setting up GCP resources"
echo "============================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable \
  dialogflow.googleapis.com \
  aiplatform.googleapis.com \
  pubsub.googleapis.com \
  logging.googleapis.com \
  secretmanager.googleapis.com \
  cloudrun.googleapis.com \
  cloudbuild.googleapis.com \
  --project=${PROJECT_ID}

# Create Pub/Sub topic for conversation events
echo "📨 Creating Pub/Sub topic..."
gcloud pubsub topics create conversation-events --project=${PROJECT_ID} || echo "Topic already exists"

# Create Pub/Sub subscription
echo "📬 Creating Pub/Sub subscription..."
gcloud pubsub subscriptions create conversation-events-sub \
  --topic=conversation-events \
  --project=${PROJECT_ID} || echo "Subscription already exists"

# Create Secret Manager secrets (placeholders)
echo "🔐 Creating Secret Manager secrets..."
echo -n "your-dialogflow-agent-id" | gcloud secrets create dialogflow-agent-id \
  --data-file=- \
  --project=${PROJECT_ID} || echo "Secret already exists"

echo -n "your-genesys-client-id" | gcloud secrets create genesys-client-id \
  --data-file=- \
  --project=${PROJECT_ID} || echo "Secret already exists"

echo -n "your-genesys-client-secret" | gcloud secrets create genesys-client-secret \
  --data-file=- \
  --project=${PROJECT_ID} || echo "Secret already exists"

echo -n "your-jwt-secret" | gcloud secrets create jwt-secret \
  --data-file=- \
  --project=${PROJECT_ID} || echo "Secret already exists"

echo ""
echo "✅ GCP resources setup complete!"
echo ""
echo "Next steps:"
echo "1. Update secrets in Secret Manager with actual values"
echo "2. Create Dialogflow CX agent and note the agent ID"
echo "3. Configure Genesys Cloud integration"
echo "4. Run ./deploy-cloud-run.sh to deploy the application"
