#!/bin/bash
# Azure Function App Japan East 部署腳本
# 請先確保已登入 Azure CLI: az login

set -e  # 遇到錯誤立即停止

# 配置變數
RESOURCE_GROUP="airesumeadvisorfastapi"
LOCATION="japaneast"
FUNCTION_APP_NAME="airesumeadvisor-fastapi-japaneast"
STORAGE_ACCOUNT_NAME="airesumeadvisorjpeast"
PLAN_NAME="airesumeadvisor-plan-japaneast"
INSIGHTS_NAME="airesumeadvisorfastapi-japaneast"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 開始部署 Azure Function App 到 Japan East${NC}"
echo "=================================================="

# 1. 檢查 Azure CLI 登入狀態
echo -e "\n${YELLOW}步驟 1: 檢查 Azure CLI 登入狀態${NC}"
if ! az account show > /dev/null 2>&1; then
    echo -e "${RED}❌ 請先執行 'az login' 登入 Azure${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 已登入 Azure${NC}"

# 2. 設定訂閱
echo -e "\n${YELLOW}步驟 2: 設定訂閱${NC}"
az account set --subscription "5396d388-8261-464e-8ee4-112770674fba"
echo -e "${GREEN}✅ 訂閱設定完成${NC}"

# 3. 創建 Storage Account
echo -e "\n${YELLOW}步驟 3: 創建 Storage Account${NC}"
if az storage account show --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    echo "⚠️  Storage Account 已存在，跳過創建"
else
    az storage account create \
        --name $STORAGE_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    echo -e "${GREEN}✅ Storage Account 創建成功${NC}"
fi

# 4. 創建 Application Insights
echo -e "\n${YELLOW}步驟 4: 創建 Application Insights${NC}"
if az monitor app-insights component show --app $INSIGHTS_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    echo "⚠️  Application Insights 已存在，跳過創建"
else
    az monitor app-insights component create \
        --app $INSIGHTS_NAME \
        --location $LOCATION \
        --resource-group $RESOURCE_GROUP \
        --application-type web
    echo -e "${GREEN}✅ Application Insights 創建成功${NC}"
fi

# 5. 創建 Premium Plan
echo -e "\n${YELLOW}步驟 5: 創建 Premium Plan${NC}"
if az functionapp plan show --name $PLAN_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    echo "⚠️  Premium Plan 已存在，跳過創建"
else
    az functionapp plan create \
        --name $PLAN_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku EP1 \
        --is-linux
    echo -e "${GREEN}✅ Premium Plan 創建成功${NC}"
fi

# 6. 創建 Function App
echo -e "\n${YELLOW}步驟 6: 創建 Function App${NC}"
if az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    echo "⚠️  Function App 已存在，跳過創建"
else
    az functionapp create \
        --name $FUNCTION_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --plan $PLAN_NAME \
        --runtime python \
        --runtime-version 3.11 \
        --functions-version 4 \
        --storage-account $STORAGE_ACCOUNT_NAME
    echo -e "${GREEN}✅ Function App 創建成功${NC}"
fi

# 7. 獲取 Application Insights Key
echo -e "\n${YELLOW}步驟 7: 配置 Application Insights${NC}"
INSIGHTS_KEY=$(az monitor app-insights component show \
    --app $INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey -o tsv)

INSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
    --app $INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query connectionString -o tsv)

# 8. 複製現有設定
echo -e "\n${YELLOW}步驟 8: 複製應用程式設定${NC}"
echo "從 staging 環境複製設定..."

# 獲取現有設定並過濾掉不需要的
TEMP_SETTINGS_FILE="/tmp/app_settings_temp.json"
az functionapp config appsettings list \
    --name airesumeadvisor-fastapi-premium \
    --resource-group $RESOURCE_GROUP \
    --slot staging \
    --query "[?name!='WEBSITE_CONTENTAZUREFILECONNECTIONSTRING' && name!='WEBSITE_CONTENTSHARE' && name!='AzureWebJobsStorage' && name!='APPLICATIONINSIGHTS_CONNECTION_STRING'].{name:name, value:value}" \
    > $TEMP_SETTINGS_FILE

# 應用設定
while IFS= read -r setting; do
    name=$(echo $setting | jq -r '.name')
    value=$(echo $setting | jq -r '.value')
    if [[ ! -z "$name" && "$name" != "null" && ! -z "$value" && "$value" != "null" ]]; then
        az functionapp config appsettings set \
            --name $FUNCTION_APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --settings "$name=$value" \
            --output none
    fi
done < <(jq -c '.[]' $TEMP_SETTINGS_FILE)

echo -e "${GREEN}✅ 應用程式設定複製完成${NC}"

# 9. 設定 Application Insights
echo -e "\n${YELLOW}步驟 9: 更新 Application Insights 連接${NC}"
az functionapp config appsettings set \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="$INSIGHTS_CONNECTION_STRING" \
    --output none
echo -e "${GREEN}✅ Application Insights 設定完成${NC}"

# 10. 確保 LLM 模型設定正確
echo -e "\n${YELLOW}步驟 10: 確認 LLM 模型設定${NC}"
az functionapp config appsettings set \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings LLM_MODEL_KEYWORDS="gpt41-mini" \
    --output none
echo -e "${GREEN}✅ LLM 模型設定完成${NC}"

# 11. 獲取 Function Key
echo -e "\n${YELLOW}步驟 11: 獲取 Function Keys${NC}"
# 等待 Function App 完全啟動
sleep 10
FUNCTION_KEY=$(az functionapp keys list \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query functionKeys.default -o tsv 2>/dev/null || echo "待生成")

# 12. 輸出摘要
echo -e "\n${GREEN}=================================================="
echo "🎉 部署完成！"
echo "=================================================="
echo -e "${NC}"
echo "📍 Function App URL: https://${FUNCTION_APP_NAME}.azurewebsites.net"
echo "🔑 Function Key: $FUNCTION_KEY"
echo ""
echo "📋 下一步："
echo "1. 使用 GitHub Actions 或 ZIP 部署程式碼"
echo "2. 執行功能和效能測試"
echo "3. 設定 Traffic Manager 進行流量切換"
echo ""
echo "💡 測試命令："
echo "curl -X GET \"https://${FUNCTION_APP_NAME}.azurewebsites.net/api/v1/health?code=${FUNCTION_KEY}\""

# 清理臨時檔案
rm -f $TEMP_SETTINGS_FILE