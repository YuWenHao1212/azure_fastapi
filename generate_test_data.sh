#!/bin/bash

# Generate test data for monitoring
echo "🚀 Generating test data for monitoring..."

# Set function key as environment variable
FUNCTION_KEY="${AZURE_FUNCTION_KEY:-YOUR_KEY_HERE}"
BASE_URL="https://airesumeadvisor-fastapi.azurewebsites.net"

if [ "$FUNCTION_KEY" = "YOUR_KEY_HERE" ]; then
    echo "❌ Please set AZURE_FUNCTION_KEY environment variable"
    exit 1
fi

# 1. Health checks
echo "📍 Sending health checks..."
for i in {1..3}; do
    curl -s "${BASE_URL}/health?code=${FUNCTION_KEY}" \
        -H "X-Correlation-ID: health-$i-$(date +%s)" > /dev/null
    echo "  ✓ Health check $i"
    sleep 1
done

# 2. Successful keyword extraction
echo -e "\n📍 Sending successful requests..."
for i in {1..3}; do
    curl -s -X POST "${BASE_URL}/api/v1/extract-jd-keywords?code=${FUNCTION_KEY}" \
        -H "Content-Type: application/json" \
        -H "X-Correlation-ID: success-$i-$(date +%s)" \
        -d '{
            "job_description": "We are looking for a Senior Full Stack Developer with 5+ years of experience in React, Node.js, Python, and cloud services. Strong knowledge of microservices architecture, Docker, Kubernetes, and DevOps practices required."
        }' > /dev/null
    echo "  ✓ Successful request $i"
    sleep 2
done

# 3. Error requests
echo -e "\n📍 Sending error requests..."
for i in {1..2}; do
    curl -s -X POST "${BASE_URL}/api/v1/extract-jd-keywords?code=${FUNCTION_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"job_description": "Too short"}' > /dev/null
    echo "  ✓ Error request $i"
    sleep 1
done

echo -e "\n✅ Test data generated!"
echo "⏰ Wait 1-2 minutes and check Application Insights"