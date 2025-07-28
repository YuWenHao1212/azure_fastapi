# GitHub Secrets 設置指南

本文檔說明需要在 GitHub Repository Settings > Secrets and variables > Actions 中設置的所有密鑰。

## 必要的 Secrets

### Azure OpenAI 相關
- `AZURE_OPENAI_API_KEY` - 主要的 Azure OpenAI API 金鑰
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI 端點 URL

### GPT-4.1 Mini (Japan East) 相關
- `GPT41_MINI_JAPANEAST_API_KEY` - GPT-4.1 mini 專用 API 金鑰
- `GPT41_MINI_JAPANEAST_ENDPOINT` - GPT-4.1 mini 端點 URL

### 嵌入服務相關
- `AZURE_OPENAI_EMBEDDING_API_KEY` - 嵌入服務 API 金鑰（可選，預設使用 AZURE_OPENAI_API_KEY）
- `AZURE_OPENAI_EMBEDDING_ENDPOINT` - 嵌入服務端點 URL
- `EMBEDDING_ENDPOINT` - 舊版嵌入服務端點（為向後相容保留）

### LLM 模型配置（可選，有預設值）
- `LLM_MODEL_KEYWORDS` - 關鍵字提取使用的模型（預設：'gpt41-mini'）
- `LLM_MODEL_DEFAULT` - 其他功能使用的預設模型（預設：'gpt4o-2'）
- `ENABLE_LLM_MODEL_OVERRIDE` - 是否啟用模型覆寫功能（預設：'true'）
- `ENABLE_LLM_MODEL_HEADER` - 是否啟用 HTTP header 模型選擇（預設：'true'）

### Azure 部署相關
- `AZURE_FUNCTIONAPP_JAPANEAST_PUBLISH_PROFILE` - Production 部署配置
- `AZURE_FUNCTIONAPP_JAPANEAST_STAGING_PUBLISH_PROFILE` - Staging 部署配置
- `JAPANEAST_PRODUCTION_HOST_KEY` - Production Function App 的 Host Key
- `JAPANEAST_STAGING_HOST_KEY` - Staging Function App 的 Host Key

### JWT 相關（測試用）
- `JWT_SECRET_KEY` - JWT 加密金鑰（可選，測試環境會使用預設值）

## 設置步驟

1. 前往你的 GitHub Repository
2. 點擊 Settings > Secrets and variables > Actions
3. 點擊 "New repository secret"
4. 輸入 Secret 名稱和值
5. 點擊 "Add secret"

## 取得這些值的方式

### Azure OpenAI 金鑰和端點
1. 登入 [Azure Portal](https://portal.azure.com)
2. 找到你的 Azure OpenAI 資源
3. 在 "Keys and Endpoint" 頁面複製金鑰和端點

### Publish Profile
1. 在 Azure Portal 中找到 Function App
2. 在 Overview 頁面點擊 "Get publish profile"
3. 將下載的整個 XML 內容貼到 Secret 中

### Function Host Keys
1. 在 Azure Portal 中找到 Function App
2. 前往 "Functions" > "App keys"
3. 複製 default host key

## 注意事項

- 所有 Secrets 都是加密存儲的
- 只有在 workflow 執行時才能訪問
- 不會在日誌中顯示（GitHub 會自動遮蔽）
- 定期更新金鑰以維護安全性