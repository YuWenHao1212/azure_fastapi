# 多個 Function Apps Host ID 衝突解決方案

## 問題發現

在資源群組 `airesumeadvisorfastapi` 中有 **3 個 Function Apps**：
1. `airesumeadvisor-fastapi` (原始版本)
2. `airesumeadvisor-fastapi-premium` (Premium 版本)
3. `airesumeadvisor-fastapi-japaneast` (日本東部版本)

所有這些可能共用相同的 Storage Account：`airesumeadvisorjpeast`

## 根本原因

當多個 Function Apps 共用相同的 Storage Account 時，如果它們的 Host ID 相同或相似，就會發生衝突。特別是：
- `airesumeadvisor-fastapi-japaneast` 被截斷為 `airesumeadvisor-fastapi-japaneas`
- 可能與 `airesumeadvisor-fastapi` 或 `airesumeadvisor-fastapi-premium` 產生衝突

## 解決方案

### 方案 A：為每個 Function App 設置唯一的 Host ID（推薦）

```bash
# 1. 原始版本
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi \
  --resource-group airesumeadvisorfastapi \
  --settings "AzureFunctionsWebHost__hostId=ara-api-original-v2"

# 2. Premium 版本
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-premium \
  --resource-group airesumeadvisorfastapi \
  --settings "AzureFunctionsWebHost__hostId=ara-api-premium-v2"

# 3. Japan East 版本 - Production
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --settings "AzureFunctionsWebHost__hostId=ara-api-je-prod-v2"

# 4. Japan East 版本 - Staging (如果有)
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --slot staging \
  --settings "AzureFunctionsWebHost__hostId=ara-api-je-stg-v2"
```

### 方案 B：使用不同的 Storage Accounts（長期解決方案）

為每個 Function App 創建獨立的 Storage Account：

```bash
# 1. 創建新的 Storage Account for Japan East
az storage account create \
  --name arafastapijeast \
  --resource-group airesumeadvisorfastapi \
  --location japaneast \
  --sku Standard_LRS

# 2. 創建新的 Storage Account for Premium
az storage account create \
  --name arafastapipremium \
  --resource-group airesumeadvisorfastapi \
  --location eastasia \
  --sku Standard_LRS

# 3. 更新 Function Apps 的 Storage 配置
# (需要獲取完整的連接字串)
```

## 立即執行的修復腳本

創建一個修復所有 Function Apps 的腳本：

```bash
#!/bin/bash

# 修復所有 Function Apps 的 Host ID
RESOURCE_GROUP="airesumeadvisorfastapi"

echo "Setting unique Host IDs for all Function Apps..."

# Function App 1: Original
echo "Configuring airesumeadvisor-fastapi..."
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi \
  --resource-group $RESOURCE_GROUP \
  --settings "AzureFunctionsWebHost__hostId=ara-api-orig-v2" \
  --output none

# Function App 2: Premium
echo "Configuring airesumeadvisor-fastapi-premium..."
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-premium \
  --resource-group $RESOURCE_GROUP \
  --settings "AzureFunctionsWebHost__hostId=ara-api-prem-v2" \
  --output none

# Function App 3: Japan East
echo "Configuring airesumeadvisor-fastapi-japaneast..."
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --settings "AzureFunctionsWebHost__hostId=ara-api-je-v2" \
  --output none

# Check for staging slot
STAGING_EXISTS=$(az functionapp deployment slot list \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --query "[?name=='staging'].name" \
  --output tsv)

if [ -n "$STAGING_EXISTS" ]; then
  echo "Configuring staging slot..."
  az functionapp config appsettings set \
    --name airesumeadvisor-fastapi-japaneast \
    --resource-group $RESOURCE_GROUP \
    --slot staging \
    --settings "AzureFunctionsWebHost__hostId=ara-api-je-stg-v2" \
    --output none
fi

echo "Restarting all Function Apps..."
az functionapp restart --name airesumeadvisor-fastapi --resource-group $RESOURCE_GROUP
az functionapp restart --name airesumeadvisor-fastapi-premium --resource-group $RESOURCE_GROUP
az functionapp restart --name airesumeadvisor-fastapi-japaneast --resource-group $RESOURCE_GROUP

echo "✅ All Function Apps configured with unique Host IDs!"
```

## 驗證步驟

1. 等待所有 Function Apps 重啟（約 2-3 分鐘）
2. 檢查每個 Function App 的診斷：
   - Azure Portal > 每個 Function App > Diagnose and solve problems
   - 確認 AZFD0004 錯誤不再出現
3. 測試每個 Function App 的健康端點

## 預防措施

1. **命名規範**：使用簡短、唯一的名稱
   - ❌ `airesumeadvisor-fastapi-japaneast-production`
   - ✅ `ara-api-je`

2. **Host ID 規範**：
   - Original: `ara-api-orig-v2`
   - Premium: `ara-api-prem-v2`
   - Japan East: `ara-api-je-v2`
   - Staging: `ara-api-je-stg-v2`

3. **Storage Account 隔離**：
   - 考慮為每個 Function App 使用獨立的 Storage Account
   - 特別是生產環境和測試環境應該分離