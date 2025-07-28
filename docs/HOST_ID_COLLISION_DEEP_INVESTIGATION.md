# Host ID Collision 深度調查與修復計劃

## 問題摘要
- **錯誤代碼**: AZFD0004
- **Host ID**: 'airesumeadvisor-fastapi-japaneas' (被截斷，缺少最後的 't')
- **發生次數**: 88 次
- **影響**: 可能導致 Function App 執行不穩定

## 根本原因分析

### 1. Host ID 生成機制
Azure Functions 的 Host ID 用於在共享存儲中唯一標識 Function App 實例。Host ID 來源有以下優先順序：

1. **應用程式設置**: `AzureFunctionsWebHost__hostId`
2. **host.json**: `extensions.durableTask.hostId`
3. **自動生成**: 基於 Function App 名稱

### 2. 為什麼會被截斷？
- Host ID 有 **32 字符長度限制**
- 'airesumeadvisor-fastapi-japaneast' = 34 字符
- 被截斷為 'airesumeadvisor-fastapi-japaneas' = 32 字符

### 3. 為什麼移除 host.json 配置後仍有問題？
可能原因：
- Azure 已在存儲帳戶中緩存了舊的 Host ID
- Function App 名稱太長，自動生成的 ID 仍然被截斷
- 可能有多個 Function App 共用相同的存儲帳戶

## 調查步驟

### 步驟 1：檢查存儲帳戶
```bash
# 使用 Azure CLI 查詢存儲帳戶
az functionapp show \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --query "siteConfig.azureStorageAccounts"

# 列出所有使用相同存儲帳戶的 Function Apps
az functionapp list \
  --resource-group airesumeadvisorfastapi \
  --query "[?contains(siteConfig.azureStorageAccounts, 'STORAGE_ACCOUNT_NAME')].name"
```

### 步驟 2：檢查存儲帳戶中的 Host ID
在 Azure Portal 中：
1. 前往 Function App 使用的 Storage Account
2. 瀏覽到 Containers > `azure-webjobs-hosts`
3. 查看 `locks` 和 `ids` 資料夾
4. 尋找包含 'airesumeadvisor-fastapi-japaneas' 的檔案

### 步驟 3：檢查應用程式設置
```bash
# 查看是否有設置 Host ID
az functionapp config appsettings list \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  | grep -i hostid
```

## 修復方案

### 方案 A：明確設置較短的 Host ID（推薦）
在 Function App 的應用程式設置中添加：

```bash
# Production
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --settings "AzureFunctionsWebHost__hostId=ara-api-je-prod-v2"

# Staging
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --slot-settings "AzureFunctionsWebHost__hostId=ara-api-je-stg-v2" \
  --slot staging
```

### 方案 B：清理存儲帳戶中的衝突
1. 停止 Function App
2. 在 Storage Account 中刪除相關的 lock 檔案：
   - `azure-webjobs-hosts/locks/airesumeadvisor-fastapi-japaneas*`
   - `azure-webjobs-hosts/ids/airesumeadvisor-fastapi-japaneas*`
3. 重啟 Function App

### 方案 C：使用不同的存儲帳戶
如果有多個 Function App 共用存儲：
```bash
# 創建新的存儲帳戶
az storage account create \
  --name arafastapijestorage \
  --resource-group airesumeadvisorfastapi \
  --location japaneast \
  --sku Standard_LRS

# 更新 Function App 配置
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --settings "AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=arafastapijestorage;..."
```

## 實施計劃

### 階段 1：診斷（10 分鐘）
1. 執行上述調查步驟 1-3
2. 記錄發現的問題
3. 確認衝突的來源

### 階段 2：備份（5 分鐘）
1. 備份當前的應用程式設置
2. 記錄當前的存儲帳戶連接字串

### 階段 3：實施修復（15 分鐘）
1. **優先嘗試方案 A**（最簡單、影響最小）
2. 如果方案 A 無效，執行方案 B
3. 最後考慮方案 C（影響較大）

### 階段 4：驗證（10 分鐘）
1. 重啟 Function App
2. 檢查診斷日誌，確認錯誤不再出現
3. 測試所有 API 端點
4. 監控 30 分鐘確保穩定

## 預防措施

### 1. 命名規範
未來的 Function App 命名應考慮 32 字符限制：
- ❌ `airesumeadvisor-fastapi-japaneast` (34 chars)
- ✅ `ara-fastapi-je` (14 chars)

### 2. 配置管理
- 總是在應用程式設置中明確設置 Host ID
- 使用簡短但唯一的 ID
- 為不同環境使用不同的 Host ID

### 3. 監控
設置警報來監控 AZFD0004 錯誤：
```bash
az monitor metrics alert create \
  --name "HostIDCollisionAlert" \
  --resource-group airesumeadvisorfastapi \
  --scopes "/subscriptions/.../providers/Microsoft.Web/sites/airesumeadvisor-fastapi-japaneast" \
  --condition "count ExceptionCount > 0 where ExceptionType == 'AZFD0004'" \
  --description "Alert when host ID collision occurs"
```

## 緊急聯絡資訊
如果問題持續：
1. Azure Support Ticket (Severity B)
2. 參考: https://aka.ms/functions-hostid-collision
3. 準備提供：
   - Subscription ID
   - Resource Group
   - Function App 名稱
   - 錯誤時間戳記
   - 此調查文檔