#!/bin/bash

# Test the debug monitoring endpoint
echo "🔍 Testing monitoring debug endpoint..."
echo "====================================="

# Use environment variable for function key
FUNCTION_KEY="${AZURE_FUNCTION_KEY:-YOUR_FUNCTION_KEY_HERE}"
BASE_URL="https://airesumeadvisor-fastapi.azurewebsites.net"

if [ "$FUNCTION_KEY" = "YOUR_FUNCTION_KEY_HERE" ]; then
    echo "❌ Please set AZURE_FUNCTION_KEY environment variable"
    echo "   export AZURE_FUNCTION_KEY='your-actual-key'"
    exit 1
fi

# Call debug endpoint
echo "📡 Calling /debug/monitoring endpoint..."
curl -s "${BASE_URL}/debug/monitoring?code=${FUNCTION_KEY}" | jq .

# Also test a regular endpoint to generate telemetry
echo -e "\n📡 Calling /health endpoint..."
curl -s "${BASE_URL}/health?code=${FUNCTION_KEY}" | jq .

echo -e "\n✅ Done! Check Application Insights in a few minutes."