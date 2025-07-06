#!/bin/bash

echo "🔄 Restarting Azure Function App to apply configuration changes..."

FUNCTION_APP="airesumeadvisor-fastapi"
RESOURCE_GROUP="airesumeadvisorfastapi"

# Stop the function app
echo "⏸️  Stopping Function App..."
az functionapp stop --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# Wait a bit
echo "⏳ Waiting 10 seconds..."
sleep 10

# Start the function app
echo "▶️  Starting Function App..."
az functionapp start --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

echo "✅ Function App restarted!"
echo ""
echo "⏰ Wait 2-3 minutes for the app to fully initialize"
echo "📊 Then run test requests and check Application Insights again"