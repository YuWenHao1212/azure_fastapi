#!/bin/bash

# Test script for Azure Container Apps deployment
# Tests all API endpoints and compares performance with Function Apps

set -e

# Configuration
CONTAINER_APP_URL="https://airesumeadvisor-api.PLACEHOLDER.azurecontainerapps.io"
FUNCTION_APP_URL="https://airesumeadvisor-fastapi-japaneast.azurewebsites.net"
FUNCTION_KEY="${AZURE_FUNCTION_KEY:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Container Apps API Testing Script${NC}"
echo "=================================="

# Function to test endpoint with timing
test_endpoint() {
    local url="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "URL: $url$endpoint"
    
    # Make request with timing
    local start_time=$(date +%s.%3N)
    local response=$(curl -s -w "\n%{http_code}\n%{time_total}" \
        -X POST "$url$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data" \
        --max-time 60)
    
    local end_time=$(date +%s.%3N)
    local total_time=$(echo "$end_time - $start_time" | bc)
    
    # Parse response
    local http_code=$(echo "$response" | tail -2 | head -1)
    local curl_time=$(echo "$response" | tail -1)
    local body=$(echo "$response" | head -n -2)
    
    # Check if successful
    if [[ "$http_code" == "200" ]]; then
        echo -e "${GREEN}✅ Success${NC} - HTTP $http_code"
        echo -e "⏱️  Response time: ${curl_time}s (total: ${total_time}s)"
        
        # Check if response contains expected structure
        if echo "$body" | jq -e '.success' >/dev/null 2>&1; then
            local success=$(echo "$body" | jq -r '.success')
            if [[ "$success" == "true" ]]; then
                echo -e "${GREEN}✅ API Success${NC}"
            else
                echo -e "${RED}❌ API Error${NC}"
                echo "$body" | jq -r '.error.message' 2>/dev/null || echo "Unknown error"
            fi
        fi
    else
        echo -e "${RED}❌ Failed${NC} - HTTP $http_code"
        echo "Response: $body"
    fi
    
    return 0
}

# Check if Container App URL is set
if [[ "$CONTAINER_APP_URL" == *"PLACEHOLDER"* ]]; then
    echo -e "${RED}❌ Error: Please update CONTAINER_APP_URL with actual Container Apps URL${NC}"
    echo "Get URL with: az containerapp show --name airesumeadvisor-api --resource-group airesumeadvisorfastapi --query properties.configuration.ingress.fqdn --output tsv"
    exit 1
fi

# Health check
echo -e "\n${BLUE}1. Health Check${NC}"
echo "==============="

curl -f "$CONTAINER_APP_URL/api/health" --max-time 10 && echo -e "\n${GREEN}✅ Health check passed${NC}" || echo -e "\n${RED}❌ Health check failed${NC}"

# Test data
JD_DATA='{
  "job_description": "We are looking for a Senior Python Developer with 5+ years experience. Required skills: Python, FastAPI, Docker, AWS, PostgreSQL. Nice to have: Kubernetes, React, TypeScript. Strong communication skills and team collaboration required.",
  "language": "en"
}'

RESUME_DATA='<!DOCTYPE html><html><body><h2>John Smith</h2><p>Senior Software Engineer</p><h3>Skills</h3><ul><li>Python (5 years)</li><li>FastAPI (2 years)</li><li>Docker (3 years)</li></ul><h3>Experience</h3><p>Software Engineer at Tech Corp (2020-2025)</p></body></html>'

INDEX_DATA="{
  \"resume\": \"$RESUME_DATA\",
  \"job_description\": \"Senior Python Developer with FastAPI and Docker experience required\",
  \"keywords\": \"Python,FastAPI,Docker,AWS,PostgreSQL\"
}"

GAP_DATA="{
  \"resume\": \"$RESUME_DATA\",
  \"job_description\": \"Senior Python Developer with FastAPI and Docker experience required\",
  \"keywords\": \"Python,FastAPI,Docker,AWS,PostgreSQL\",
  \"language\": \"en\"
}"

FORMAT_DATA='{
  "ocr_text": "【Name】: John Smith\n【Email】: john@example.com\n【Phone】: +1-234-567-8900\n【Experience】: Software Engineer at Tech Corp (2020-2025)\n【Skills】: Python, FastAPI, Docker"
}'

TAILOR_DATA="{
  \"job_description\": \"Senior Python Developer with FastAPI and Docker experience required\",
  \"original_resume\": \"$RESUME_DATA\",
  \"gap_analysis\": {
    \"core_strengths\": [\"Python expertise\", \"FastAPI experience\"],
    \"key_gaps\": [\"AWS experience\", \"PostgreSQL knowledge\"],
    \"quick_improvements\": [\"Complete AWS course\", \"Practice PostgreSQL\"],
    \"covered_keywords\": [\"Python\", \"FastAPI\", \"Docker\"],
    \"missing_keywords\": [\"AWS\", \"PostgreSQL\"]
  }
}"

COURSE_DATA='{
  "skill_name": "Docker containerization",
  "search_context": "Looking for beginner-friendly Docker courses",
  "limit": 3
}'

# Test all endpoints
echo -e "\n${BLUE}2. API Endpoint Tests${NC}"
echo "====================="

test_endpoint "$CONTAINER_APP_URL" "/api/v1/extract-jd-keywords" "$JD_DATA" "Extract Keywords"
test_endpoint "$CONTAINER_APP_URL" "/api/v1/index-calculation" "$INDEX_DATA" "Index Calculation"
test_endpoint "$CONTAINER_APP_URL" "/api/v1/index-cal-and-gap-analysis" "$GAP_DATA" "Gap Analysis"
test_endpoint "$CONTAINER_APP_URL" "/api/v1/format-resume" "$FORMAT_DATA" "Resume Format"
test_endpoint "$CONTAINER_APP_URL" "/api/v1/tailor-resume" "$TAILOR_DATA" "Resume Tailoring"
test_endpoint "$CONTAINER_APP_URL" "/api/v1/courses/search" "$COURSE_DATA" "Course Search"

# Performance comparison (if Function App key is provided)
if [[ -n "$FUNCTION_KEY" ]]; then
    echo -e "\n${BLUE}3. Performance Comparison${NC}"
    echo "========================="
    
    echo -e "\n${YELLOW}Testing Container Apps vs Function Apps (Keywords Extraction)${NC}"
    
    echo -e "\n📊 Container Apps:"
    test_endpoint "$CONTAINER_APP_URL" "/api/v1/extract-jd-keywords" "$JD_DATA" "Extract Keywords"
    
    echo -e "\n📊 Function Apps:"
    test_endpoint "$FUNCTION_APP_URL" "/api/v1/extract-jd-keywords?code=$FUNCTION_KEY" "" "$JD_DATA" "Extract Keywords"
    
else
    echo -e "\n${YELLOW}⚠️  Skipping performance comparison (no AZURE_FUNCTION_KEY provided)${NC}"
fi

echo -e "\n${GREEN}🎉 Testing completed!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Review response times and compare with Function Apps"
echo "2. Check Application Insights for detailed metrics"
echo "3. Update frontend to use Container Apps URL"
echo "4. Run load testing for production readiness"