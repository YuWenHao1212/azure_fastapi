#!/bin/bash

echo "🔍 診斷 Application Insights 連接問題..."
echo "========================================"

FUNCTION_APP="airesumeadvisor-fastapi"
RESOURCE_GROUP="airesumeadvisorfastapi"

# 1. 檢查 Function App 狀態
echo -e "\n1️⃣ 檢查 Function App 狀態..."
az functionapp show --name $FUNCTION_APP --resource-group $RESOURCE_GROUP --query "{state:state, hostNamesDisabled:hostNamesDisabled}" -o json

# 2. 檢查所有 App Settings
echo -e "\n2️⃣ 檢查 Application Insights 相關設定..."
az functionapp config appsettings list --name $FUNCTION_APP --resource-group $RESOURCE_GROUP --query "[?contains(name, 'APPINSIGHTS') || contains(name, 'APPLICATIONINSIGHTS')].{name:name, value:value}" -o table

# 3. 檢查診斷設定
echo -e "\n3️⃣ 檢查診斷設定..."
az monitor diagnostic-settings list --resource "/subscriptions/5396d388-8261-464e-8ee4-112770674fba/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$FUNCTION_APP" -o table

# 4. 測試 Application Insights 連接
echo -e "\n4️⃣ 驗證 Application Insights 資源..."
az resource show --ids "/subscriptions/5396d388-8261-464e-8ee4-112770674fba/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/components/airesumeadvisorfastapi" --query "{name:name, instrumentationKey:properties.InstrumentationKey, connectionString:properties.ConnectionString}" -o json

# 5. 檢查最近的 Function 執行
echo -e "\n5️⃣ 檢查最近的 Function 執行日誌..."
echo "請在 Azure Portal 中檢查："
echo "Function App → Functions → HttpTrigger → Monitor → Logs"

echo -e "\n💡 可能的問題："
echo "1. Application Insights 連接字串不正確"
echo "2. 網路連接問題（防火牆/NSG）"
echo "3. Function App 還在初始化中"
echo "4. 權限問題"