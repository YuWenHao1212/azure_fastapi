#!/bin/bash

# Fix Host ID Collision for Azure Functions
# This script diagnoses and fixes AZFD0004 errors

set -e

# Configuration
RESOURCE_GROUP="airesumeadvisorfastapi"
FUNCTION_APP_NAME="airesumeadvisor-fastapi-japaneast"
PRODUCTION_HOST_ID="ara-api-je-prod-v2"
STAGING_HOST_ID="ara-api-je-stg-v2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Azure Functions Host ID Collision Fix Script${NC}"
echo "============================================"
echo ""

# Step 1: Check current configuration
echo -e "${YELLOW}Step 1: Checking current configuration...${NC}"

# Get current app settings
echo "Fetching current Host ID settings..."
CURRENT_SETTINGS=$(az functionapp config appsettings list \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?name=='AzureFunctionsWebHost__hostId'].value" \
  --output tsv 2>/dev/null || echo "")

if [ -n "$CURRENT_SETTINGS" ]; then
    echo -e "${GREEN}Current Host ID: $CURRENT_SETTINGS${NC}"
else
    echo -e "${RED}No Host ID currently set in app settings${NC}"
fi

# Get storage account info
echo ""
echo "Fetching storage account information..."
STORAGE_CONNECTION=$(az functionapp config appsettings list \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?name=='AzureWebJobsStorage'].value" \
  --output tsv)

# Extract storage account name from connection string
STORAGE_ACCOUNT=$(echo "$STORAGE_CONNECTION" | grep -oP 'AccountName=\K[^;]+' || echo "")
echo -e "${GREEN}Storage Account: $STORAGE_ACCOUNT${NC}"

# Step 2: Diagnose the issue
echo ""
echo -e "${YELLOW}Step 2: Diagnosing the issue...${NC}"

# Check if there are other function apps using the same storage
echo "Checking for other Function Apps using the same storage account..."
OTHER_APPS=$(az functionapp list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?name!='$FUNCTION_APP_NAME'].name" \
  --output tsv)

if [ -n "$OTHER_APPS" ]; then
    echo -e "${YELLOW}Other Function Apps in the same resource group:${NC}"
    echo "$OTHER_APPS"
else
    echo -e "${GREEN}No other Function Apps found in the resource group${NC}"
fi

# Step 3: Apply the fix
echo ""
echo -e "${YELLOW}Step 3: Ready to apply the fix${NC}"
echo "This will set the following Host IDs:"
echo "  Production: $PRODUCTION_HOST_ID"
echo "  Staging: $STAGING_HOST_ID"
echo ""
read -p "Do you want to proceed? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Applying fix...${NC}"
    
    # Set Host ID for production
    echo "Setting Host ID for production slot..."
    az functionapp config appsettings set \
      --name "$FUNCTION_APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --settings "AzureFunctionsWebHost__hostId=$PRODUCTION_HOST_ID" \
      --output none
    
    echo -e "${GREEN}✓ Production Host ID set to: $PRODUCTION_HOST_ID${NC}"
    
    # Check if staging slot exists
    STAGING_EXISTS=$(az functionapp deployment slot list \
      --name "$FUNCTION_APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "[?name=='staging'].name" \
      --output tsv)
    
    if [ -n "$STAGING_EXISTS" ]; then
        echo "Setting Host ID for staging slot..."
        az functionapp config appsettings set \
          --name "$FUNCTION_APP_NAME" \
          --resource-group "$RESOURCE_GROUP" \
          --slot staging \
          --settings "AzureFunctionsWebHost__hostId=$STAGING_HOST_ID" \
          --output none
        
        echo -e "${GREEN}✓ Staging Host ID set to: $STAGING_HOST_ID${NC}"
    else
        echo -e "${YELLOW}No staging slot found, skipping staging configuration${NC}"
    fi
    
    # Step 4: Restart the Function App
    echo ""
    echo -e "${YELLOW}Step 4: Restarting Function App...${NC}"
    
    az functionapp restart \
      --name "$FUNCTION_APP_NAME" \
      --resource-group "$RESOURCE_GROUP"
    
    echo -e "${GREEN}✓ Function App restarted${NC}"
    
    # Step 5: Verify the fix
    echo ""
    echo -e "${YELLOW}Step 5: Verifying the fix...${NC}"
    echo "Please check the following:"
    echo "1. Go to Azure Portal > Function App > Diagnose and solve problems"
    echo "2. Look for AZFD0004 errors in the last 30 minutes"
    echo "3. Test your API endpoints"
    echo ""
    echo -e "${GREEN}Fix applied successfully!${NC}"
    
    # Optional: Clean up storage account
    echo ""
    echo -e "${YELLOW}Optional: Clean up storage account${NC}"
    echo "If the error persists, you may need to clean up the storage account."
    echo "This requires manual intervention in the Azure Portal:"
    echo "1. Navigate to Storage Account: $STORAGE_ACCOUNT"
    echo "2. Go to Containers > azure-webjobs-hosts"
    echo "3. Delete any files/folders containing 'airesumeadvisor-fastapi-japaneas'"
    echo ""
else
    echo -e "${YELLOW}Fix cancelled${NC}"
fi

echo ""
echo "Script completed!"