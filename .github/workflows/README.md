# GitHub Actions CI/CD 設置指南

## 概述

本專案使用 GitHub Actions 實現自動化 CI/CD 流程，包含：
- Pull Request 時自動執行測試
- 合併到 `container` 分支時自動建置並部署到 Azure Container Apps
- 自動清理舊的 Docker 映像

## 工作流程說明

### 1. Pull Request 測試 (PR Test)
- **觸發條件**：向 `container` 分支提交 PR
- **執行內容**：
  - 安裝 Python 依賴
  - 執行 `./precommit.sh --level-3 --parallel`
  - 上傳測試結果

### 2. 建置與推送 (Build & Push)
- **觸發條件**：合併到 `container` 分支
- **執行內容**：
  - 建置 Docker 映像
  - 推送到 Azure Container Registry
  - 標記版本（時間戳 + commit SHA）

### 3. 部署 (Deploy)
- **觸發條件**：建置成功後自動執行
- **執行內容**：
  - 更新 Container Apps 使用新映像
  - 健康檢查驗證
  - 建立 GitHub 部署記錄

### 4. 清理 (Cleanup)
- **觸發條件**：部署成功後自動執行
- **執行內容**：
  - 保留最新的 5 個映像
  - 刪除舊的映像以節省空間

## 必要的 GitHub Secrets 設置

在 GitHub 專案的 Settings → Secrets and variables → Actions 中設置以下 secrets：

### 1. Azure 認證
```json
AZURE_CREDENTIALS: {
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "5396d388-8261-464e-8ee4-112770674fba",
  "tenantId": "xxx"
}
```

### 2. Azure Container Registry
```
ACR_USERNAME: airesumeadvisorregistry
ACR_PASSWORD: <從 Azure Portal 獲取>
```

### 3. API Keys
```
# OpenAI 相關
AZURE_OPENAI_ENDPOINT: https://airesumeadvisor-japaneast.openai.azure.com
AZURE_OPENAI_API_KEY: <your-key>
GPT41_MINI_JAPANEAST_ENDPOINT: https://airesumeadvisor-japaneast.openai.azure.com
GPT41_MINI_JAPANEAST_API_KEY: <your-key>
EMBEDDING_ENDPOINT: https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com
EMBEDDING_API_KEY: <your-key>

# 資料庫
DATABASE_URL: postgresql://...

# API 安全
VALID_API_KEYS: key1,key2,key3
```

## 設置步驟

### 1. 獲取 Azure Service Principal
```bash
# 建立 Service Principal
az ad sp create-for-rbac --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/5396d388-8261-464e-8ee4-112770674fba \
  --sdk-auth

# 將輸出的 JSON 設置為 AZURE_CREDENTIALS secret
```

### 2. 獲取 ACR 認證
```bash
# 獲取 ACR 密碼
az acr credential show --name airesumeadvisorregistry --query "passwords[0].value" -o tsv
```

### 3. 設置 Branch Protection Rules (建議)
在 Settings → Branches 中為 `container` 分支設置：
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - 選擇 "test" job
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging

## Best Practices

### 1. 版本管理策略
- 每次部署使用唯一標籤：`YYYYMMDD-HHMMSS-SHA`
- 同時維護 `latest` 標籤
- 保留部署歷史記錄

### 2. 測試策略
- PR 必須通過 Level 3 測試
- 使用平行測試加速執行
- 測試失敗時阻止合併

### 3. 部署策略
- 使用 revision 管理部署版本
- 健康檢查確保部署成功
- 失敗時保留舊版本運行

### 4. 安全性
- 所有敏感資訊使用 GitHub Secrets
- 避免在程式碼中硬編碼任何密鑰
- 定期輪換 API Keys

### 5. 成本優化
- 自動清理舊映像
- 使用 Docker layer caching
- 只在必要時執行完整測試

## 監控與除錯

### 查看工作流程執行
1. 前往 GitHub Actions 頁面
2. 選擇 "Container Apps CI/CD" 工作流程
3. 查看各個 job 的執行狀態

### 常見問題

#### 1. 測試失敗
- 檢查是否設置了所有必要的 secrets
- 確認 API Keys 是否有效
- 查看測試日誌了解具體錯誤

#### 2. 部署失敗
- 檢查 Azure 認證是否正確
- 確認 Container Apps 資源存在
- 查看 Azure CLI 輸出日誌

#### 3. 健康檢查失敗
- 確認應用程式正確啟動
- 檢查環境變數配置
- 查看 Container Apps 日誌

## 進階設置

### 1. 多環境部署
可以修改工作流程支援多環境：
- `container` → production
- `container-staging` → staging
- `container-dev` → development

### 2. 手動部署
工作流程支援 `workflow_dispatch`，可以手動觸發部署

### 3. Rollback 機制
使用 Azure CLI 切換到之前的 revision：
```bash
az containerapp revision activate \
  --name airesumeadvisor-api-production \
  --resource-group airesumeadvisorfastapi \
  --revision <previous-revision-name>
```

## 維護建議

1. **定期檢查**：
   - 清理工作是否正常運行
   - 部署時間是否合理
   - 測試覆蓋率是否足夠

2. **更新依賴**：
   - 定期更新 GitHub Actions
   - 更新 Python 和 Node.js 版本
   - 更新 Azure CLI

3. **優化效能**：
   - 調整快取策略
   - 優化 Docker 建置
   - 減少不必要的步驟