#!/bin/bash

# Azure Container Apps Deployment Script
# Deploy AI Resume Advisor API to Azure Container Apps in Japan East

set -e  # Exit on any error

# Configuration
SUBSCRIPTION_ID="5396d388-8261-464e-8ee4-112770674fba"
RESOURCE_GROUP="airesumeadvisorfastapi"
LOCATION="japaneast"
ACR_NAME="airesumeadvisorregistry"
CONTAINER_APP_NAME="airesumeadvisor-api"
CONTAINER_ENV_NAME="airesumeadvisor-env"
IMAGE_NAME="airesumeadvisor-api"
IMAGE_TAG="latest"

echo "🚀 Starting Azure Container Apps deployment..."

# Login and set subscription
echo "📋 Setting up Azure CLI..."
az account set --subscription "$SUBSCRIPTION_ID"
az configure --defaults group="$RESOURCE_GROUP" location="$LOCATION"

# Check if we're on the container branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "container" ]]; then
    echo "⚠️  Warning: Not on 'container' branch. Current branch: $CURRENT_BRANCH"
    echo "   Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Step 1: Create Container Registry if not exists
echo "🏗️  Creating Azure Container Registry..."
if ! az acr show --name "$ACR_NAME" &>/dev/null; then
    az acr create \
        --name "$ACR_NAME" \
        --sku Basic \
        --admin-enabled true
    echo "✅ Container Registry created: $ACR_NAME"
else
    echo "✅ Container Registry exists: $ACR_NAME"
fi

# Step 2: Build and push Docker image
echo "🔨 Building Docker image..."
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer --output tsv)
FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"

# Login to ACR
az acr login --name "$ACR_NAME"

# Build and push image
docker build -t "$FULL_IMAGE_NAME" .
docker push "$FULL_IMAGE_NAME"
echo "✅ Image pushed: $FULL_IMAGE_NAME"

# Step 3: Create Container Apps Environment if not exists
echo "🌐 Creating Container Apps Environment..."
if ! az containerapp env show --name "$CONTAINER_ENV_NAME" &>/dev/null; then
    az containerapp env create \
        --name "$CONTAINER_ENV_NAME" \
        --location "$LOCATION" \
        --logs-workspace-id $(az monitor log-analytics workspace show \
            --resource-group "$RESOURCE_GROUP" \
            --workspace-name "airesumeadvisorfastapi" \
            --query customerId --output tsv 2>/dev/null || echo "")
    echo "✅ Container Apps Environment created: $CONTAINER_ENV_NAME"
else
    echo "✅ Container Apps Environment exists: $CONTAINER_ENV_NAME"
fi

# Step 4: Get ACR credentials for Container App
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value --output tsv)

# Step 5: Create or update Container App
echo "📦 Deploying Container App..."

# Check if Container App exists
if az containerapp show --name "$CONTAINER_APP_NAME" &>/dev/null; then
    echo "🔄 Updating existing Container App..."
    az containerapp update \
        --name "$CONTAINER_APP_NAME" \
        --image "$FULL_IMAGE_NAME"
else
    echo "🆕 Creating new Container App..."
    az containerapp create \
        --name "$CONTAINER_APP_NAME" \
        --environment "$CONTAINER_ENV_NAME" \
        --image "$FULL_IMAGE_NAME" \
        --registry-server "$ACR_LOGIN_SERVER" \
        --registry-username "$ACR_USERNAME" \
        --registry-password "$ACR_PASSWORD" \
        --target-port 8000 \
        --ingress external \
        --min-replicas 1 \
        --max-replicas 10 \
        --cpu 1.0 \
        --memory 2Gi \
        --env-vars \
            AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
            AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key \
            AZURE_OPENAI_GPT4_DEPLOYMENT=gpt-4o-mini \
            AZURE_OPENAI_API_VERSION=2024-02-15-preview \
            EMBEDDING_ENDPOINT=secretref:embedding-endpoint \
            EMBEDDING_API_KEY=secretref:embedding-api-key \
            APPINSIGHTS_INSTRUMENTATIONKEY=secretref:appinsights-key \
            APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-connection-string
fi

# Step 6: Set secrets (will prompt for values)
echo "🔐 Setting up secrets..."
echo "Please provide the following secret values (they will be stored securely in Container Apps):"

echo "Enter Azure OpenAI Endpoint (default: https://airesumeadvisor.openai.azure.com):"
read -r AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT:-"https://airesumeadvisor.openai.azure.com"}
az containerapp secret set \
    --name "$CONTAINER_APP_NAME" \
    --secrets azure-openai-endpoint="$AZURE_OPENAI_ENDPOINT"

echo "Enter Azure OpenAI API Key:"
read -rs AZURE_OPENAI_API_KEY
az containerapp secret set \
    --name "$CONTAINER_APP_NAME" \
    --secrets azure-openai-api-key="$AZURE_OPENAI_API_KEY"

echo "Enter Embedding Endpoint:"
read -r EMBEDDING_ENDPOINT
az containerapp secret set \
    --name "$CONTAINER_APP_NAME" \
    --secrets embedding-endpoint="$EMBEDDING_ENDPOINT"

echo "Enter Embedding API Key:"
read -rs EMBEDDING_API_KEY
az containerapp secret set \
    --name "$CONTAINER_APP_NAME" \
    --secrets embedding-api-key="$EMBEDDING_API_KEY"

echo "Enter Application Insights Instrumentation Key:"
read -rs APPINSIGHTS_KEY
az containerapp secret set \
    --name "$CONTAINER_APP_NAME" \
    --secrets appinsights-key="$APPINSIGHTS_KEY"

echo "Enter Application Insights Connection String:"
read -rs APPINSIGHTS_CONNECTION_STRING
az containerapp secret set \
    --name "$CONTAINER_APP_NAME" \
    --secrets appinsights-connection-string="$APPINSIGHTS_CONNECTION_STRING"

# Step 7: Get Container App URL
CONTAINER_APP_URL=$(az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container Registry: $ACR_LOGIN_SERVER"
echo "   Container App: $CONTAINER_APP_NAME"
echo "   Environment: $CONTAINER_ENV_NAME"
echo "   Image: $FULL_IMAGE_NAME"
echo ""
echo "🌐 Container App URL: https://$CONTAINER_APP_URL"
echo ""
echo "🧪 Test your deployment:"
echo "   curl https://$CONTAINER_APP_URL/api/health"
echo ""
echo "📊 Monitor your app:"
echo "   az containerapp logs show --name $CONTAINER_APP_NAME --follow"
echo ""
echo "✅ Next steps: Test individual API endpoints and update DNS records"