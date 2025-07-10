#!/bin/bash

# 測試 Azure Function App 的健康狀態和路由

# API 基礎設定
BASE_URL="https://airesumeadvisor-fastapi.azurewebsites.net"
HOST_KEY="${AZURE_FUNCTION_HOST_KEY}"

# 顏色設定
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}測試 Azure Function App API 健康狀態${NC}"
echo "Base URL: ${BASE_URL}"
echo "================================================"

# 測試 1: 根路徑
echo -e "\n${YELLOW}測試 1: 根路徑 /${NC}"
curl -s "${BASE_URL}/?code=${HOST_KEY}" | jq . || echo "無法解析 JSON"

# 測試 2: /api/v1/
echo -e "\n${YELLOW}測試 2: API v1 根路徑 /api/v1/${NC}"
curl -s "${BASE_URL}/api/v1/?code=${HOST_KEY}" | jq . || echo "無法解析 JSON"

# 測試 3: 健康檢查
echo -e "\n${YELLOW}測試 3: 健康檢查 /health${NC}"
curl -s "${BASE_URL}/health?code=${HOST_KEY}" | jq . || echo "無法解析 JSON"

# 測試 4: API v1 健康檢查
echo -e "\n${YELLOW}測試 4: API v1 健康檢查 /api/v1/health${NC}"
curl -s "${BASE_URL}/api/v1/health?code=${HOST_KEY}" | jq . || echo "無法解析 JSON"

# 測試 5: 列出所有可用端點
echo -e "\n${YELLOW}測試 5: 顯示 API v1 路由資訊${NC}"
RESPONSE=$(curl -s "${BASE_URL}/api/v1/?code=${HOST_KEY}")
if [ $? -eq 0 ]; then
    echo "$RESPONSE" | jq -r '.data.implemented_endpoints | to_entries[] | "\(.value.method) \(.value.path) - \(.value.description)"' 2>/dev/null || echo "無法解析端點列表"
fi

echo -e "\n${BLUE}================================================${NC}"
echo "健康檢查完成"