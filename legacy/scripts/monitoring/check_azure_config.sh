#!/bin/bash

# Check Azure Function App configuration
echo "🔍 Checking Azure Function App configuration..."

# Function App name
FUNCTION_APP="airesumeadvisor-fastapi"
RESOURCE_GROUP="airesumeadvisorfastapi"

echo "📌 Function App: $FUNCTION_APP"
echo "📌 Resource Group: $RESOURCE_GROUP"

# Check if logged in
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo -e "\n📋 Checking Application Insights configuration..."
az functionapp config appsettings list \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='APPINSIGHTS_INSTRUMENTATIONKEY' || name=='APPLICATIONINSIGHTS_CONNECTION_STRING' || name=='AzureWebJobsDashboard'].{name:name, value:value}" \
    --output table

echo -e "\n📋 Checking if Application Insights is connected..."
az functionapp show \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --query "{name:name, appInsightsKey:siteConfig.appInsightsKey}" \
    --output json

echo -e "\n💡 If APPINSIGHTS_INSTRUMENTATIONKEY is missing, run:"
echo "az functionapp config appsettings set \\"
echo "    --name $FUNCTION_APP \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --settings APPINSIGHTS_INSTRUMENTATIONKEY=e62aa619-199c-4f43-826e-bdec26344a26"