# GitHub Actions Configuration Guide

## Required Secrets

This repository uses multiple GitHub Actions workflows that require different secrets:

### For Deployment (azure-deploy.yml)

#### 1. AZURE_CREDENTIALS
Azure Service Principal credentials for deployment.

**How to create:**
```bash
az ad sp create-for-rbac --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `AZURE_CREDENTIALS`
4. Value: Paste the JSON output from the command above

#### 2. FUNCTION_KEY
Function App host key for health check endpoint.

**How to get:**
1. Go to Azure Portal
2. Navigate to your Function App
3. Go to "App keys" → "Host keys"
4. Copy the `_master` key value

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `FUNCTION_KEY`
4. Value: Paste the host key

### For Consistency Monitoring (consistency-monitoring-fixed.yml) - Currently Disabled

#### 3. OPENAI_API_KEY
OpenAI API key for accessing the language model.

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key

#### 4. OPENAI_API_BASE
Base URL for OpenAI API endpoint.

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_BASE`
4. Value: Your OpenAI API base URL (e.g., `https://your-resource.openai.azure.com/`)

#### 5. OPENAI_API_VERSION
API version for OpenAI service.

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_API_VERSION`
4. Value: API version (e.g., `2023-05-15`)

#### 6. OPENAI_DEPLOYMENT_NAME
Deployment name for OpenAI model.

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `OPENAI_DEPLOYMENT_NAME`
4. Value: Your deployment name

#### 7. SLACK_WEBHOOK_URL (Optional)
Slack webhook for notifications when KPIs fail.

**Add to GitHub:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `SLACK_WEBHOOK_URL`
4. Value: Your Slack webhook URL

## Validation

The workflow includes a validation step that checks if these secrets are configured.
If any secret is missing, the workflow will fail with a clear error message.

## IDE Warnings

If you see warnings in your IDE about these secrets:
- These are expected - the IDE cannot access GitHub secrets
- The warnings serve as a reminder that these need to be configured
- You can verify they're set correctly by checking the Actions tab after pushing