#!/bin/bash
# 簡化版 Japan East 部署腳本 - 使用現有資源

set -e

# 配置
RESOURCE_GROUP="airesumeadvisorfastapi"
LOCATION="japaneast"
FUNCTION_APP_NAME="airesumeadvisor-fastapi-japaneast"
STORAGE_ACCOUNT_NAME="airesumeadvisorjpeast"  # 必須新建
EXISTING_PLAN_NAME="airesumeadvisor-premium-plan"  # 使用現有 Plan
EXISTING_INSIGHTS_NAME="airesumeadvisorfastapi"  # 使用現有 Application Insights

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 簡化版 Japan East 部署${NC}"
echo "================================"

# 1. 設定訂閱
echo -e "\n${YELLOW}1. 設定訂閱${NC}"
az account set --subscription "5396d388-8261-464e-8ee4-112770674fba"

# 2. 只創建必要的 Storage Account
echo -e "\n${YELLOW}2. 創建 Storage Account（必需）${NC}"
az storage account create \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2

# 3. 創建 Function App（使用現有 Plan 和 Insights）
echo -e "\n${YELLOW}3. 創建 Function App${NC}"
az functionapp create \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $EXISTING_PLAN_NAME \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --storage-account $STORAGE_ACCOUNT_NAME

# 4. 複製所有設定（從 staging）
echo -e "\n${YELLOW}4. 複製 Staging 設定${NC}"
SOURCE_APP="airesumeadvisor-fastapi-premium"
SOURCE_SLOT="staging"

# 匯出設定
echo "匯出設定..."
SETTINGS=$(az functionapp config appsettings list \
    --name $SOURCE_APP \
    --resource-group $RESOURCE_GROUP \
    --slot $SOURCE_SLOT \
    --query "[?name!='WEBSITE_CONTENTAZUREFILECONNECTIONSTRING' && name!='WEBSITE_CONTENTSHARE' && name!='AzureWebJobsStorage'].{name:name, value:value}" \
    -o json)

# 套用設定
echo "套用設定到新 Function App..."
echo "$SETTINGS" | jq -r '.[] | "\(.name)=\(.value)"' | while IFS= read -r setting; do
    if [[ ! -z "$setting" ]]; then
        az functionapp config appsettings set \
            --name $FUNCTION_APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --settings "$setting" \
            --output none
    fi
done

# 5. 確保 Application Insights 連接正確
echo -e "\n${YELLOW}5. 更新 Application Insights 連接${NC}"
INSIGHTS_CONNECTION=$(az monitor app-insights component show \
    --app $EXISTING_INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query connectionString -o tsv)

az functionapp config appsettings set \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="$INSIGHTS_CONNECTION" \
    --output none

# 6. 取得 Function Keys
echo -e "\n${YELLOW}6. 取得 Function Keys${NC}"
sleep 10
MASTER_KEY=$(az functionapp keys list \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query masterKey -o tsv)

DEFAULT_KEY=$(az functionapp keys list \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query functionKeys.default -o tsv)

# 7. 輸出結果
echo -e "\n${GREEN}✅ 部署完成！${NC}"
echo "================================"
echo "📍 URL: https://${FUNCTION_APP_NAME}.azurewebsites.net"
echo "🔑 Master Key: $MASTER_KEY"
echo "🔑 Default Key: $DEFAULT_KEY"
echo ""
echo "📌 共用資源："
echo "   - Application Insights: $EXISTING_INSIGHTS_NAME"
echo "   - Premium Plan: $EXISTING_PLAN_NAME"
echo ""
echo "🚀 下一步：更新 GitHub Actions 部署到此 Function App"