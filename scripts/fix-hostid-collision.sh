#!/bin/bash

# 修復 Host ID 衝突問題

echo "🔧 修復 Azure Functions Host ID 衝突"
echo "===================================="

# 設定變數
RESOURCE_GROUP="airesumeadvisorfastapi"  # 共用的資源群組
FUNCTION_APP="airesumeadvisor-fastapi-japaneast"
OLD_HOST_ID="airesumeadvisor-fastapi-japaneas"  # 錯誤的 Host ID (少了 't')

echo "📋 目前設定："
echo "- Resource Group: $RESOURCE_GROUP"
echo "- Function App: $FUNCTION_APP"
echo "- 問題 Host ID: $OLD_HOST_ID"
echo ""

# 1. 獲取儲存帳戶名稱
echo "1️⃣ 檢查儲存帳戶..."
STORAGE_ACCOUNT=$(az functionapp config appsettings list \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='AzureWebJobsStorage'].value" -o tsv | \
    sed -n 's/.*AccountName=\([^;]*\).*/\1/p')

if [ -z "$STORAGE_ACCOUNT" ]; then
    echo "❌ 無法找到儲存帳戶"
    exit 1
fi

echo "✅ 找到儲存帳戶: $STORAGE_ACCOUNT"

# 2. 列出 azure-webjobs-hosts 容器中的 locks
echo ""
echo "2️⃣ 檢查現有的 Host ID locks..."
echo "列出所有 locks："
az storage blob list \
    --account-name $STORAGE_ACCOUNT \
    --container-name "azure-webjobs-hosts" \
    --prefix "locks" \
    --query "[].name" -o tsv 2>/dev/null || echo "無法列出 locks"

# 3. 清理舊的 Host ID lock
echo ""
echo "3️⃣ 清理舊的 Host ID lock..."
LOCK_BLOB="locks/$OLD_HOST_ID/host"

echo "嘗試刪除: $LOCK_BLOB"
az storage blob delete \
    --account-name $STORAGE_ACCOUNT \
    --container-name "azure-webjobs-hosts" \
    --name "$LOCK_BLOB" 2>/dev/null && echo "✅ 已刪除舊的 lock" || echo "ℹ️ Lock 不存在或已刪除"

# 4. 檢查並設定正確的 Host ID
echo ""
echo "4️⃣ 確認 Function App 設定..."

# 檢查是否有自訂 Host ID 設定
HOST_ID_SETTING=$(az functionapp config appsettings list \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='WEBSITE_CONTENTSHARE'].value" -o tsv)

echo "目前的 WEBSITE_CONTENTSHARE: $HOST_ID_SETTING"

# 5. 重新啟動 Function App
echo ""
echo "5️⃣ 重新啟動 Function App..."
read -p "是否要重新啟動 Function App？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    az functionapp restart \
        --name $FUNCTION_APP \
        --resource-group $RESOURCE_GROUP
    echo "✅ Function App 已重新啟動"
else
    echo "⏭️ 跳過重新啟動"
fi

echo ""
echo "✅ 完成！"
echo ""
echo "📌 注意事項："
echo "1. host.json 已更新，設定了唯一的 Host ID"
echo "2. 推送更新的 host.json 到 GitHub"
echo "3. 如果問題持續，可能需要："
echo "   - 設定不同的儲存帳戶"
echo "   - 或使用不同的 WEBSITE_CONTENTSHARE 值"