#!/bin/bash

# Azure Container Apps 診斷腳本
# 用於診斷部署和運行時問題

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
RESOURCE_GROUP="airesumeadvisorfastapi"
CONTAINER_APP_NAME="airesumeadvisor-api-production"
CONTAINER_APP_ENV="airesumeadvisor-env-production"
ACR_NAME="airesumeadvisorregistry"
LOG_ANALYTICS_WORKSPACE="airesumeadvisorfastapi"

echo -e "${BLUE}=== Azure Container Apps 診斷工具 ===${NC}"
echo "時間: $(TZ='Asia/Taipei' date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# 檢查 Azure CLI 登入
echo -e "${YELLOW}1. 檢查 Azure CLI 登入狀態${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}錯誤：請先執行 'az login'${NC}"
    exit 1
fi

ACCOUNT_INFO=$(az account show)
echo "訂閱: $(echo $ACCOUNT_INFO | jq -r .name)"
echo "用戶: $(echo $ACCOUNT_INFO | jq -r .user.name)"
echo ""

# Container App 基本資訊
echo -e "${YELLOW}2. Container App 基本資訊${NC}"
APP_INFO=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "{name:name, location:location, provisioningState:properties.provisioningState, fqdn:properties.configuration.ingress.fqdn}" \
    -o json)

echo "$APP_INFO" | jq .
APP_URL=$(echo "$APP_INFO" | jq -r .fqdn)
echo ""

# 檢查最新的 Revisions
echo -e "${YELLOW}3. 最新的 Revisions (最近 5 個)${NC}"
az containerapp revision list \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[0:5].{name:name, active:properties.active, state:properties.runningState, created:properties.createdTime, replicas:properties.replicas}" \
    -o table
echo ""

# 取得最新 revision 名稱
LATEST_REVISION=$(az containerapp revision list \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[0].name" -o tsv)

echo -e "${YELLOW}4. 最新 Revision 詳細資訊${NC}"
echo "Revision: $LATEST_REVISION"

# 檢查 revision 的容器配置
CONTAINER_INFO=$(az containerapp revision show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --revision $LATEST_REVISION \
    --query "properties.template.containers[0]" \
    -o json)

echo "容器映像: $(echo "$CONTAINER_INFO" | jq -r .image)"
echo "CPU: $(echo "$CONTAINER_INFO" | jq -r .resources.cpu)"
echo "記憶體: $(echo "$CONTAINER_INFO" | jq -r .resources.memory)"
echo ""

# 檢查環境變數（隱藏敏感資訊）
echo -e "${YELLOW}5. 環境變數配置（已設置的變數）${NC}"
ENV_VARS=$(echo "$CONTAINER_INFO" | jq -r '.env[]? | select(.value != null) | .name' | sort)
SECRET_REFS=$(echo "$CONTAINER_INFO" | jq -r '.env[]? | select(.secretRef != null) | "\(.name) -> secret:\(.secretRef)"' | sort)

echo "環境變數:"
echo "$ENV_VARS"
echo ""
echo "Secret 引用:"
echo "$SECRET_REFS"
echo ""

# 檢查健康狀態
echo -e "${YELLOW}6. 應用程式健康檢查${NC}"
if [ ! -z "$APP_URL" ]; then
    echo "測試 URL: https://$APP_URL/health"
    HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://$APP_URL/health 2>/dev/null || echo "CURL_FAILED")
    
    if [[ "$HEALTH_RESPONSE" == "CURL_FAILED" ]]; then
        echo -e "${RED}無法連接到應用程式${NC}"
    else
        HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
        BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE:/d')
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✓ 健康檢查成功 (HTTP $HTTP_CODE)${NC}"
            echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
        else
            echo -e "${RED}✗ 健康檢查失敗 (HTTP $HTTP_CODE)${NC}"
            echo "$BODY"
        fi
    fi
else
    echo -e "${RED}無法取得應用程式 URL${NC}"
fi
echo ""

# 查看最近的日誌
echo -e "${YELLOW}7. 最近的容器日誌（最後 20 行）${NC}"
echo "從 revision: $LATEST_REVISION"
az containerapp logs show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --revision $LATEST_REVISION \
    --tail 20 2>&1 || echo -e "${RED}無法取得日誌${NC}"
echo ""

# 檢查錯誤日誌
echo -e "${YELLOW}8. 檢查錯誤日誌（包含 ERROR 或 Exception）${NC}"
az containerapp logs show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --revision $LATEST_REVISION \
    --tail 100 2>&1 | grep -i -E "(error|exception|failed|failure)" | tail -20 || echo "沒有發現錯誤日誌"
echo ""

# Log Analytics 查詢
echo -e "${YELLOW}9. Log Analytics 查詢（如果已連接）${NC}"
# 檢查是否有診斷設置
DIAG_SETTINGS=$(az monitor diagnostic-settings list \
    --resource /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/managedEnvironments/$CONTAINER_APP_ENV \
    --query "[0].name" -o tsv 2>/dev/null)

if [ ! -z "$DIAG_SETTINGS" ]; then
    echo "診斷設置已啟用: $DIAG_SETTINGS"
    echo ""
    echo "可以使用以下 KQL 查詢在 Log Analytics 中查看日誌："
    echo -e "${BLUE}ContainerAppConsoleLogs_CL | where ContainerAppName_s == \"$CONTAINER_APP_NAME\" | order by TimeGenerated desc | take 50${NC}"
else
    echo -e "${YELLOW}未設置 Log Analytics 診斷${NC}"
fi
echo ""

# 檢查 ACR 映像
echo -e "${YELLOW}10. 檢查 ACR 中的最新映像${NC}"
LATEST_TAGS=$(az acr repository show-tags \
    --name $ACR_NAME \
    --repository airesumeadvisor-api \
    --orderby time_desc \
    --top 5 \
    -o table)
echo "$LATEST_TAGS"
echo ""

# 生成診斷摘要
echo -e "${BLUE}=== 診斷摘要 ===${NC}"
PROVISIONING_STATE=$(echo "$APP_INFO" | jq -r .provisioningState)
REVISION_STATE=$(az containerapp revision show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --revision $LATEST_REVISION \
    --query "properties.runningState" -o tsv)

echo "Container App 狀態: $PROVISIONING_STATE"
echo "最新 Revision 狀態: $REVISION_STATE"

if [ "$PROVISIONING_STATE" = "Succeeded" ] && [ "$REVISION_STATE" = "Running" ]; then
    echo -e "${GREEN}✓ Container App 和 Revision 都在正常運行${NC}"
else
    echo -e "${RED}✗ 發現問題：請檢查上述日誌${NC}"
fi

# 保存診斷報告
REPORT_FILE="container_apps_diagnosis_$(date +%Y%m%d_%H%M%S).txt"
echo ""
echo -e "${YELLOW}保存完整診斷報告到: $REPORT_FILE${NC}"

{
    echo "Azure Container Apps 診斷報告"
    echo "生成時間: $(TZ='Asia/Taipei' date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "=================================="
    echo ""
    echo "Container App: $CONTAINER_APP_NAME"
    echo "Resource Group: $RESOURCE_GROUP"
    echo "Latest Revision: $LATEST_REVISION"
    echo ""
    echo "App Info:"
    echo "$APP_INFO" | jq .
    echo ""
    echo "Container Config:"
    echo "$CONTAINER_INFO" | jq .
} > "$REPORT_FILE"