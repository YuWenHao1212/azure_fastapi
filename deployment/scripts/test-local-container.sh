#!/bin/bash

# Test script for local Container Apps development
# Tests extract-jd-keywords API in containerized environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Local Container Apps Testing${NC}"
echo "==============================="

# Configuration
LOCAL_URL="http://localhost:8000"
TEST_JD="{
  \"job_description\": \"We are looking for a Senior Python Developer with 5+ years experience. Required skills: Python, FastAPI, Docker, AWS, PostgreSQL. Nice to have: Kubernetes, React, TypeScript. Strong communication skills and team collaboration required.\",
  \"language\": \"en\",
  \"max_keywords\": 16
}"

echo -e "\n${YELLOW}Step 1: Health Check${NC}"
echo "Testing: $LOCAL_URL/health"

health_response=$(curl -s -w "%{http_code}" "$LOCAL_URL/health" -o /tmp/health_response.json)
http_code="${health_response: -3}"

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "Response:" 
    cat /tmp/health_response.json | jq '.'
else
    echo -e "${RED}❌ Health check failed (HTTP $http_code)${NC}"
    cat /tmp/health_response.json
    exit 1
fi

echo -e "\n${YELLOW}Step 2: API Information${NC}"
echo "Testing: $LOCAL_URL/"

info_response=$(curl -s -w "%{http_code}" "$LOCAL_URL/" -o /tmp/info_response.json)
http_code="${info_response: -3}"

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ API info retrieved${NC}"
    echo "API Information:"
    cat /tmp/info_response.json | jq '.data'
else
    echo -e "${YELLOW}⚠️  API info endpoint returned HTTP $http_code${NC}"
fi

echo -e "\n${YELLOW}Step 3: Extract Keywords API Test${NC}"
echo "Testing: $LOCAL_URL/api/v1/extract-jd-keywords"

start_time=$(date +%s.%3N)
response=$(curl -s -w "\n%{http_code}\n%{time_total}" \
    -X POST "$LOCAL_URL/api/v1/extract-jd-keywords" \
    -H "Content-Type: application/json" \
    -d "$TEST_JD" \
    --max-time 30)

end_time=$(date +%s.%3N)
total_time=$(echo "$end_time - $start_time" | bc)

# Parse response
http_code=$(echo "$response" | tail -2 | head -1)
curl_time=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -2)

echo -e "⏱️  Response time: ${curl_time}s (total: ${total_time}s)"

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Keywords extraction successful${NC}"
    
    # Parse JSON response
    echo "$body" > /tmp/keywords_response.json
    
    # Check if response contains expected structure
    if echo "$body" | jq -e '.success' >/dev/null 2>&1; then
        success=$(echo "$body" | jq -r '.success')
        if [[ "$success" == "true" ]]; then
            echo -e "${GREEN}✅ API returned success=true${NC}"
            
            # Show extracted keywords
            keywords=$(echo "$body" | jq -r '.data.keywords[]' | head -5)
            echo -e "${BLUE}📋 First 5 keywords:${NC}"
            echo "$keywords"
            
            # Check response time
            if (( $(echo "$curl_time < 5.0" | bc -l) )); then
                echo -e "${GREEN}✅ Response time acceptable (< 5s)${NC}"
            else
                echo -e "${YELLOW}⚠️  Response time high (${curl_time}s)${NC}"
            fi
            
        else
            echo -e "${RED}❌ API returned success=false${NC}"
            echo "$body" | jq -r '.error.message' 2>/dev/null || echo "Unknown error"
        fi
    else
        echo -e "${YELLOW}⚠️  Response format unexpected${NC}"
        echo "$body" | head -500
    fi
else
    echo -e "${RED}❌ API request failed (HTTP $http_code)${NC}"
    echo "Response: $body"
fi

echo -e "\n${YELLOW}Step 4: Container Performance Summary${NC}"
echo "============================================="
echo "🔍 Health Check: $(cat /tmp/health_response.json | jq -r '.data.status')"
echo "⏱️  API Response Time: ${curl_time}s"
echo "📊 HTTP Status: $http_code"
echo "🎯 Container Performance: $(echo "$curl_time < 3.0" | bc -l | sed 's/1/✅ Excellent (<3s)/; s/0/⚠️  Needs optimization/')"

# Cleanup
rm -f /tmp/health_response.json /tmp/info_response.json /tmp/keywords_response.json

echo -e "\n${GREEN}🎉 Local Container testing completed!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. If all tests pass, ready for Azure Container Apps deployment"
echo "2. Performance should be ~3s (vs 6s on Function Apps)"
echo "3. Run: make deploy-dev to deploy to Azure"