#!/bin/bash

# Fix Host ID Collision for ALL Function Apps in the Resource Group
# This addresses the issue where multiple Function Apps share the same storage account

set -e

# Configuration
RESOURCE_GROUP="airesumeadvisorfastapi"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Fix Host ID for ALL Function Apps ===${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Step 1: List all Function Apps
echo -e "${YELLOW}Step 1: Identifying all Function Apps...${NC}"
FUNCTION_APPS=$(az functionapp list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[].name" \
  --output tsv)

echo "Found Function Apps:"
echo "$FUNCTION_APPS" | while read -r app; do
    echo "  - $app"
done
echo ""

# Step 2: Check current Host IDs
echo -e "${YELLOW}Step 2: Checking current Host IDs...${NC}"
echo "$FUNCTION_APPS" | while read -r app; do
    HOST_ID=$(az functionapp config appsettings list \
      --name "$app" \
      --resource-group "$RESOURCE_GROUP" \
      --query "[?name=='AzureFunctionsWebHost__hostId'].value" \
      --output tsv 2>/dev/null || echo "Not Set")
    
    echo "$app: $HOST_ID"
done
echo ""

# Step 3: Confirm fix
echo -e "${YELLOW}Step 3: Ready to apply unique Host IDs${NC}"
echo "This will set the following Host IDs:"
echo "  airesumeadvisor-fastapi: ara-api-orig-v2"
echo "  airesumeadvisor-fastapi-premium: ara-api-prem-v2"
echo "  airesumeadvisor-fastapi-japaneast: ara-api-je-v2"
echo "  airesumeadvisor-fastapi-japaneast (staging): ara-api-je-stg-v2"
echo ""
read -p "Do you want to proceed? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Applying fixes...${NC}"
    
    # Function App 1: Original
    if az functionapp show --name airesumeadvisor-fastapi --resource-group $RESOURCE_GROUP &>/dev/null; then
        echo "Setting Host ID for airesumeadvisor-fastapi..."
        az functionapp config appsettings set \
          --name airesumeadvisor-fastapi \
          --resource-group $RESOURCE_GROUP \
          --settings "AzureFunctionsWebHost__hostId=ara-api-orig-v2" \
          --output none
        echo -e "${GREEN}✓ Done${NC}"
    fi
    
    # Function App 2: Premium
    if az functionapp show --name airesumeadvisor-fastapi-premium --resource-group $RESOURCE_GROUP &>/dev/null; then
        echo "Setting Host ID for airesumeadvisor-fastapi-premium..."
        az functionapp config appsettings set \
          --name airesumeadvisor-fastapi-premium \
          --resource-group $RESOURCE_GROUP \
          --settings "AzureFunctionsWebHost__hostId=ara-api-prem-v2" \
          --output none
        echo -e "${GREEN}✓ Done${NC}"
    fi
    
    # Function App 3: Japan East
    if az functionapp show --name airesumeadvisor-fastapi-japaneast --resource-group $RESOURCE_GROUP &>/dev/null; then
        echo "Setting Host ID for airesumeadvisor-fastapi-japaneast..."
        az functionapp config appsettings set \
          --name airesumeadvisor-fastapi-japaneast \
          --resource-group $RESOURCE_GROUP \
          --settings "AzureFunctionsWebHost__hostId=ara-api-je-v2" \
          --output none
        echo -e "${GREEN}✓ Done${NC}"
        
        # Check for staging slot
        STAGING_EXISTS=$(az functionapp deployment slot list \
          --name airesumeadvisor-fastapi-japaneast \
          --resource-group $RESOURCE_GROUP \
          --query "[?name=='staging'].name" \
          --output tsv)
        
        if [ -n "$STAGING_EXISTS" ]; then
            echo "Setting Host ID for staging slot..."
            az functionapp config appsettings set \
              --name airesumeadvisor-fastapi-japaneast \
              --resource-group $RESOURCE_GROUP \
              --slot staging \
              --settings "AzureFunctionsWebHost__hostId=ara-api-je-stg-v2" \
              --output none
            echo -e "${GREEN}✓ Done${NC}"
        fi
    fi
    
    # Step 4: Restart all Function Apps
    echo ""
    echo -e "${YELLOW}Step 4: Restarting all Function Apps...${NC}"
    echo "$FUNCTION_APPS" | while read -r app; do
        echo "Restarting $app..."
        az functionapp restart \
          --name "$app" \
          --resource-group "$RESOURCE_GROUP" \
          --output none
        echo -e "${GREEN}✓ Done${NC}"
    done
    
    # Step 5: Verify
    echo ""
    echo -e "${YELLOW}Step 5: Verifying configuration...${NC}"
    sleep 5
    
    echo "$FUNCTION_APPS" | while read -r app; do
        HOST_ID=$(az functionapp config appsettings list \
          --name "$app" \
          --resource-group "$RESOURCE_GROUP" \
          --query "[?name=='AzureFunctionsWebHost__hostId'].value" \
          --output tsv 2>/dev/null || echo "Not Set")
        
        if [ "$HOST_ID" != "Not Set" ] && [ -n "$HOST_ID" ]; then
            echo -e "$app: ${GREEN}$HOST_ID ✓${NC}"
        else
            echo -e "$app: ${RED}$HOST_ID ✗${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}✅ All Function Apps have been configured with unique Host IDs!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Wait 5-10 minutes for changes to fully propagate"
    echo "2. Check Azure Portal > each Function App > Diagnose and solve problems"
    echo "3. Verify AZFD0004 errors have stopped"
    echo ""
    echo -e "${YELLOW}Important:${NC} If errors persist, you may need to:"
    echo "1. Clear the storage account containers (azure-webjobs-hosts)"
    echo "2. Consider using separate storage accounts for each Function App"
else
    echo -e "${YELLOW}Fix cancelled${NC}"
fi

echo ""
echo "Script completed!"