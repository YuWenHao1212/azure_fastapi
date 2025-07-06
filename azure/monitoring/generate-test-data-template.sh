#!/bin/bash

# Template for generating test data for Application Insights monitoring
# IMPORTANT: Replace placeholders before using

# Configuration - REPLACE THESE VALUES
FUNCTION_KEY="YOUR_FUNCTION_KEY_HERE"  # Get from Azure Portal
BASE_URL="https://YOUR_FUNCTION_APP.azurewebsites.net"

# Verify configuration
if [ "$FUNCTION_KEY" = "YOUR_FUNCTION_KEY_HERE" ]; then
    echo "❌ Error: Please replace FUNCTION_KEY with your actual function key"
    echo "   You can find it in Azure Portal > Function App > Functions > HttpTrigger > Function Keys"
    exit 1
fi

echo "🚀 Generating test data for Application Insights..."
echo "================================================"

# 1. Health check requests (5 requests)
echo "📍 Sending health check requests..."
for i in {1..5}; do
    echo "  Request $i/5"
    curl -s -X GET "${BASE_URL}/api/v1/health?code=${FUNCTION_KEY}" \
        -H "Origin: https://airesumeadvisor.bubbleapps.io" \
        -H "X-Correlation-ID: health-test-$i-$(date +%s)" \
        -o /dev/null
    sleep 1
done

# 2. Successful keyword extraction requests (5 requests)
echo "📍 Sending successful keyword extraction requests..."
for i in {1..5}; do
    echo "  Request $i/5"
    curl -s -X POST "${BASE_URL}/api/v1/extract-jd-keywords?code=${FUNCTION_KEY}" \
        -H "Content-Type: application/json" \
        -H "Origin: https://airesumeadvisor.bubbleapps.io" \
        -H "X-Correlation-ID: success-test-$i-$(date +%s)" \
        -d '{
            "job_description": "We are looking for a Senior Software Engineer with expertise in Python, FastAPI, and Azure cloud services. Experience with microservices architecture and CI/CD pipelines is required.",
            "language": "en"
        }' \
        -o /dev/null
    sleep 2
done

# 3. Validation error requests (3 requests)
echo "📍 Sending validation error requests..."
for i in {1..3}; do
    echo "  Request $i/3"
    curl -s -X POST "${BASE_URL}/api/v1/extract-jd-keywords?code=${FUNCTION_KEY}" \
        -H "Content-Type: application/json" \
        -H "Origin: https://airesumeadvisor.bubbleapps.io" \
        -H "X-Correlation-ID: error-test-$i-$(date +%s)" \
        -d '{
            "job_description": "Too short",
            "language": "en"
        }' \
        -o /dev/null
    sleep 1
done

# 4. Different language request
echo "📍 Sending Chinese language request..."
curl -s -X POST "${BASE_URL}/api/v1/extract-jd-keywords?code=${FUNCTION_KEY}" \
    -H "Content-Type: application/json" \
    -H "Origin: https://airesumeadvisor.bubbleapps.io" \
    -H "X-Correlation-ID: chinese-test-$(date +%s)" \
    -d '{
        "job_description": "我們正在尋找資深後端工程師，需要具備 Python、FastAPI 和 Azure 雲端服務經驗。熟悉微服務架構和 CI/CD 流程者優先。",
        "language": "zh-TW"
    }' \
    -o /dev/null

# 5. Suspicious request (from different origin)
echo "📍 Sending suspicious request..."
curl -s -X POST "${BASE_URL}/api/v1/extract-jd-keywords?code=${FUNCTION_KEY}" \
    -H "Content-Type: application/json" \
    -H "Origin: https://unknown-site.com" \
    -H "User-Agent: automated-scanner/1.0" \
    -H "X-Correlation-ID: suspicious-test-$(date +%s)" \
    -d '{
        "job_description": "Looking for a developer with experience in web development",
        "language": "en"
    }' \
    -o /dev/null

echo ""
echo "✅ Test data generation completed!"
echo "⏰ Wait 2-5 minutes for data to appear in Application Insights"
echo "📊 Then refresh your Workbook to see the monitoring data"

# Security reminder
echo ""
echo "🔒 Security Note: Never commit this file with actual function keys!"
echo "   Consider using environment variables or Azure Key Vault for production use."