# 部署指南

## 概述

本專案使用 GitHub Actions 自動部署到 Azure Functions。每次推送到 `main` 分支都會觸發自動部署。

## 環境需求

### 本地開發
- Python 3.11.8
- Azure CLI
- Azure Functions Core Tools
- Git

### Azure 資源
- **Subscription ID**: `5396d388-8261-464e-8ee4-112770674fba`
- **Tenant**: `wenhaoairesumeadvisor.onmicrosoft.com`
- **Resource Group**: `airesumeadvisorfastapi`
- **Function App**: `airesumeadvisor-fastapi`
- **Application Insights**: `airesumeadvisorfastapi`
- **Portal URL**: [Azure Portal](https://portal.azure.com/#@wenhaoairesumeadvisor.onmicrosoft.com/resource/subscriptions/5396d388-8261-464e-8ee4-112770674fba/resourceGroups/airesumeadvisorfastapi/providers/Microsoft.Insights/components/airesumeadvisorfastapi/overview)

## 自動部署流程

### CI/CD Pipeline
```yaml
觸發條件：push to main
步驟：
1. 執行測試 (Level 2)
2. 建置部署套件
3. 部署到 Azure Functions
4. 驗證部署健康狀態
```

### 部署前檢查清單
執行對應的預提交測試（參見 [CLAUDE.md](/CLAUDE.md) 的測試層級定義）：
- Level 2 或 Level 3 測試通過
- 環境變數已正確配置

## 環境變數配置 

### 必要的環境變數
```bash
# Application Insights
APPINSIGHTS_INSTRUMENTATIONKEY="your-app-insights-key"
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=..."

# Azure OpenAI 服務
AZURE_OPENAI_API_KEY="your-azure-openai-key"
AZURE_OPENAI_ENDPOINT="https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com"

# Embedding 服務
AZURE_OPENAI_EMBEDDING_API_KEY="your-embedding-key"
AZURE_OPENAI_EMBEDDING_ENDPOINT="https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"

# 課程 Embedding 服務
AZURE_OPENAI_COURSE_EMBEDDING_API_KEY="your-course-embedding-key"
AZURE_OPENAI_COURSE_EMBEDDING_ENDPOINT="https://ai-azureai700705952086.cognitiveservices.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2023-05-15"

# Azure Storage
AzureWebJobsStorage="your-storage-connection-string"
DEPLOYMENT_STORAGE_CONNECTION_STRING="your-deployment-storage-connection"

# 監控設定
MONITORING_ENABLED="true"

```

### 配置方式

#### Azure Portal
1. 進入 Function App
2. Configuration → Application settings
3. 新增或更新環境變數
4. 儲存並重啟

#### Azure CLI
```bash
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi \
  --resource-group airesumeadvisorfastapi \
  --settings KEY=VALUE
```

## 手動部署步驟

如需手動部署（例如緊急修復）：

### 1. 準備部署套件
```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝相依套件
pip install -r requirements.txt

# 執行測試
./run_precommit_tests.sh --level-3 --parallel
```

### 2. 部署到 Azure
```bash
# 登入 Azure
az login

# 設定預設值
az account set --subscription "5396d388-8261-464e-8ee4-112770674fba"
az configure --defaults group=airesumeadvisorfastapi

# 部署
func azure functionapp publish airesumeadvisor-fastapi
```

### 3. 驗證部署
```bash
# 檢查健康狀態
curl https://airesumeadvisor-fastapi.azurewebsites.net/api/health

# 測試 API
curl -X POST "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords?code=[YOUR_HOST_KEY]" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Python developer needed"}'
```

## 監控與日誌

### Application Insights
1. 登入 [Azure Portal](https://portal.azure.com)
2. 前往 Application Insights: `airesumeadvisorfastapi`
3. 查看：
   - Live Metrics：即時效能
   - Failures：錯誤追蹤
   - Performance：效能分析
   - Logs：查詢日誌

### 常用查詢
```kusto
// 最近的錯誤
exceptions
| where timestamp > ago(1h)
| order by timestamp desc

// API 效能統計
customEvents
| where name == "RequestTracked"
| summarize 
    avg(todouble(customDimensions.duration_ms)), 
    percentile(todouble(customDimensions.duration_ms), 95)
  by tostring(customDimensions.endpoint)

// 每小時請求量
requests
| where timestamp > ago(24h)
| summarize count() by bin(timestamp, 1h)
| render timechart
```

## 故障排除

### 常見問題

#### 1. 部署失敗
**症狀**：GitHub Actions 顯示部署失敗
**解決**：
- 檢查 Azure 憑證是否過期
- 確認 Function App 名稱正確
- 查看詳細錯誤日誌

#### 2. API 回應 500 錯誤
**症狀**：API 呼叫返回內部錯誤
**解決**：
- 檢查環境變數配置
- 查看 Application Insights 錯誤日誌
- 確認 LLM API 金鑰有效

#### 3. 效能問題
**症狀**：API 回應緩慢
**解決**：
- 檢查 Function App 執行計畫
- 分析 Application Insights 效能數據
- 考慮升級服務方案

### 緊急回滾

如需回滾到前一版本：

```bash
# 查看部署歷史
az functionapp deployment list-publishing-profiles \
  --name airesumeadvisor-fastapi

# 回滾到特定版本
git checkout [previous-commit-hash]
func azure functionapp publish airesumeadvisor-fastapi
```

## 安全最佳實踐

### 金鑰管理
1. 使用 Azure Key Vault（計劃中）
2. 定期輪換 API 金鑰
3. 限制金鑰權限範圍

### 存取控制
1. 使用 host key 保護 API
2. 實施 IP 白名單（如需要）
3. 監控異常存取模式

### 資料保護
1. 不記錄敏感資料
2. 使用 HTTPS only
3. 遵循 GDPR 規範

## 成本優化

### 監控成本
```bash
# 查看當前成本
az consumption usage list \
  --subscription "5396d388-8261-464e-8ee4-112770674fba" \
  --start-date 2025-07-01 \
  --end-date 2025-07-31
```

### 優化建議
1. 使用 Consumption Plan（目前方案）
2. 設定自動縮放規則
3. 優化冷啟動時間
4. 實施適當的快取策略

## 維護計畫

### 定期任務
- **每週**：檢查錯誤日誌
- **每月**：審查成本與效能
- **每季**：更新相依套件
- **每年**：災難恢復演練

### 更新流程
1. 在開發環境測試
2. 執行完整測試套件
3. 部署到 staging（如有）
4. 監控 30 分鐘
5. 正式發布