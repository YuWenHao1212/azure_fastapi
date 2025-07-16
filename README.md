# Azure FastAPI - 關鍵字提取 API

> 🚀 **生產就緒**的 FastAPI 應用程式，部署於 Azure Functions
> 
> 支援中英雙語關鍵字提取，採用 FHS 架構設計

## 🎯 **功能特色**

### 🔤 **多語言支援**
- ✅ **英文關鍵字提取** - 完整的英文簡歷關鍵字識別
- ✅ **繁體中文關鍵字提取** - 達到 100% 一致性的繁體中文處理
- ✅ **智能語言檢測** - 自動識別文本語言
- ✅ **混合語言處理** - 支援中英混合內容

### 📝 **履歷優化功能** (New!)
- ✅ **AI 履歷優化** - 基於職缺描述自動優化履歷內容
- ✅ **彈性輸入格式** - 支援多種文字格式（Bubble.io 相容）
- ✅ **視覺化標記** - 清楚標示優化內容
- ✅ **STAR/PAR 格式** - 自動轉換經歷描述為專業格式

### 🛠️ **技術架構**
- **框架**: FastAPI + Azure Functions
- **架構**: FHS (Functional Hierarchy Structure)
- **AI 引擎**: Azure OpenAI GPT-4
- **語言檢測**: 進階繁體中文特徵字符集
- **標準化**: 180+ 繁體中文術語映射
- **監控**: Application Insights with ASGI telemetry

### 📊 **性能指標**
- **繁體中文一致性**: 100% (16/16 關鍵字完全一致)
- **英文一致性**: 65% (v1.3.0 版本)
- **回應時間**: < 10 秒
- **支援語言**: 中文(繁體)、英文
- **部署狀態**: ✅ 生產環境運行中

---

## 💻 **本地開發**

### 1. 環境設置

⚠️ **重要**: 請先激活正確的 conda 環境

```bash
# 激活專案環境
conda activate azure-fastapi

# 或使用快速激活腳本
source activate_env.sh
```

### 2. 確認環境
```bash
# 檢查環境是否正確激活 (應該顯示 azure-fastapi)
echo $CONDA_DEFAULT_ENV

# 檢查 Python 版本
python --version  # 應該是 3.11.x
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 設置環境變數
```bash
# 編輯 local.settings.json 檔案，加入實際的 API Keys (已配置)
# 注意：此檔案已被 .funcignore 保護，不會被部署
```

### 5. 啟動開發伺服器
```bash
# 使用 Azure Functions 本地開發
func start

# 或使用 FastAPI 開發模式
uvicorn src.main:app --reload
```

---

## 🚀 **Azure Functions 部署指南**

### 📋 **前置需求**

1. **Azure 帳號**
   - 有效的 Azure 訂閱
   - Azure Functions 服務權限

2. **本地開發環境**
   - Python 3.10+
   - Azure Functions Core Tools
   - Azure CLI

### 🔧 **安裝 Azure 工具**

```bash
# 安裝 Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 安裝 Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# 登入 Azure
az login
```

### 🏗️ **建立 Azure Resources**

```bash
# 設定變數
RESOURCE_GROUP="rg-fastapi-prod"
LOCATION="East Asia"
STORAGE_ACCOUNT="stfastapi$(date +%s)"
FUNCTION_APP="func-fastapi-keyword-extract"

# 建立資源群組
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# 建立儲存體帳戶
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION" \
  --sku Standard_LRS

# 建立 Function App
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location "$LOCATION" \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux
```

### 🔐 **設定環境變數**

在 Azure Function App 中設定以下環境變數：

```bash
# 核心設定
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
  "FUNCTIONS_WORKER_RUNTIME=python" \
  "AzureWebJobsFeatureFlags=EnableWorkerIndexing"

# Azure OpenAI 設定 (主要 LLM)
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
  "AZURE_OPENAI_API_KEY=<您的-Azure-OpenAI-API-Key>" \
  "AZURE_OPENAI_ENDPOINT=<您的-Azure-OpenAI-Endpoint>"

# Embedding 設定 (一般用途)
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
  "AZURE_OPENAI_EMBEDDING_ENDPOINT=<您的-Embedding-Endpoint>" \
  "AZURE_OPENAI_EMBEDDING_API_KEY=<您的-Embedding-API-Key>"

# Course Embedding 設定 (課程搜索專用)
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
  "AZURE_OPENAI_COURSE_EMBEDDING_ENDPOINT=<您的-Course-Embedding-Endpoint>" \
  "AZURE_OPENAI_COURSE_EMBEDDING_API_KEY=<您的-Course-Embedding-API-Key>"
```

### 📝 **環境變數對照表**

| 環境變數 | 說明 | 必要性 | 範例值 |
|---------|------|--------|--------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 金鑰 (主要 LLM) | 必要 | `8ZtDqEK70Xog...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 端點 (主要 LLM) | 必要 | `https://wenha-xxx.cognitiveservices.azure.com` |
| `AZURE_OPENAI_EMBEDDING_API_KEY` | 一般用途 Embedding API 金鑰 | 必要 | `8ZtDqEK70Xog...` |
| `AZURE_OPENAI_EMBEDDING_ENDPOINT` | 一般用途 Embedding 端點 | 必要 | `https://xxx.../embeddings?api-version=2023-05-15` |
| `AZURE_OPENAI_COURSE_EMBEDDING_API_KEY` | 課程搜索 Embedding API 金鑰 | 選用 | `bdc4f515c9f6...` |
| `AZURE_OPENAI_COURSE_EMBEDDING_ENDPOINT` | 課程搜索 Embedding 端點 | 選用 | `https://xxx.../embeddings?api-version=2023-05-15` |
| `MONITORING_ENABLED` | 啟用監控功能 | 選用 | `true` 或 `false` |

---

## 🧪 **本地測試**

### 🚦 **測試腳本**

專案提供多個測試腳本，適用於不同場景：

```bash
# 1. 快速測試（約 30 秒）- 只跑核心單元測試
./run_quick_tests.sh

# 2. 提交前測試（約 2-3 分鐘）- 完整測試套件
./run_precommit_tests.sh

# 3. 部署前測試（約 1-2 分鐘）- 檢查部署相容性
./run_predeploy_tests.sh

# 4. KPI 測試（約 5-10 分鐘）- 需要 API 服務運行
./run_kpi_tests.sh
```

### 📋 **測試覆蓋範圍**

| 測試類別 | 檔案數量 | 主要測試內容 |
|---------|---------|------------|
| 單元測試 | 4 | 資料模型、API 處理、語言偵測、關鍵字提取 |
| 整合測試 | 3 | Azure 部署、Bubble.io 相容性、效能測試 |
| 功能測試 | 3 | 一致性 KPI、多語言支援、版本比較 |

### 🎯 **測試指令範例**

```bash
# 執行特定測試檔案
pytest tests/unit/test_core_models.py -v

# 執行所有單元測試
pytest tests/unit/ -v

# 執行測試並產生覆蓋率報告
pytest tests/ --cov=src --cov-report=html

# 檢查程式碼風格（需安裝 ruff）
ruff check src/ tests/
```

---

### 🚀 **部署應用程式**

```bash
# 1. 確認在專案根目錄
cd /path/to/azure_fastapi

# 2. 檢查 .funcignore 設定
cat .funcignore

# 3. 部署到 Azure
func azure functionapp publish $FUNCTION_APP --python

# 4. 驗證部署
curl https://$FUNCTION_APP.azurewebsites.net/api/health
```

---

## 🧪 **測試部署**

### 🔍 **健康檢查**

```bash
# 基本健康檢查
curl https://$FUNCTION_APP.azurewebsites.net/api/health

# 預期回應
{
  "status": "healthy",
  "timestamp": "2025-07-04T10:30:00Z"
}
```

### 📤 **API 測試**

#### 關鍵字提取 API
```bash
# 測試關鍵字提取 API
curl -X POST "https://$FUNCTION_APP.azurewebsites.net/api/v1/keyword-extraction" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a skilled Python developer with FastAPI experience.",
    "prompt_version": "v1.3.0",
    "max_keywords": 16
  }'

# 預期回應
{
  "success": true,
  "data": {
    "keywords": ["Python", "FastAPI", "Developer", "Skilled", ...],
    "language_detected": "en",
    "prompt_version_used": "v1.3.0"
  }
}
```

#### 履歷優化 API (New!)
```bash
# 測試履歷優化 API
curl -X POST "https://$FUNCTION_APP.azurewebsites.net/api/v1/tailor-resume" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for a Senior Python Developer with cloud experience",
    "original_resume": "<h1>John Doe</h1><p>Python Developer with 4 years experience</p>",
    "gap_analysis": {
      "core_strengths": "Strong Python skills\nAPI development experience",
      "key_gaps": "Limited cloud experience\nNo senior role mentioned",
      "quick_improvements": "Add cloud projects\nHighlight leadership",
      "covered_keywords": "Python, Developer, API",
      "missing_keywords": "Senior, Cloud, AWS, Leadership"
    }
  }'

# 預期回應
{
  "success": true,
  "data": {
    "optimized_resume": "<h1>John Doe</h1><p class=\"opt-new\">Senior Python Developer...</p>",
    "applied_improvements": ["Added senior positioning", "Integrated cloud keywords"],
    "optimization_stats": {
      "sections_modified": 2,
      "keywords_added": 4
    }
  }
}
```

---

## 🔐 **安全性考量**

### 🛡️ **敏感資訊管理**

- ✅ **本地開發**: 使用 `local.settings.json` (已被 .funcignore 忽略)
- ✅ **生產環境**: 使用 Azure Function App 環境變數
- ✅ **版本控制**: 所有敏感資訊都被 .gitignore 和 .funcignore 保護

### 🔒 **最佳實踐**

1. **定期輪換 API Keys**
2. **使用 Azure Key Vault** (進階配置)
3. **啟用 Application Insights** 監控
4. **設定適當的 CORS 政策**

---

## 🏗️ **架構說明**

### 📁 **專案結構**

```
azure_fastapi/
├── function_app.py          # Azure Functions 入口點
├── host.json               # Azure Functions 設定
├── requirements.txt        # Python 依賴
├── .funcignore            # 部署忽略檔案
└── src/                   # 應用程式主體
    ├── main.py            # FastAPI 應用
    ├── api/               # API 路由
    ├── core/              # 核心配置
    ├── models/            # 資料模型
    ├── services/          # 業務邏輯
    ├── prompts/           # Prompt 模板
    └── data/              # 標準化字典
```

### 🔄 **請求流程**

1. **HTTP 請求** → Azure Functions HTTP Trigger
2. **ASGI 中間件** → 轉換為 FastAPI 格式
3. **語言檢測** → 識別輸入文本語言
4. **Prompt 選擇** → 根據語言和版本選擇 Prompt
5. **OpenAI API** → 呼叫 Azure OpenAI 服務
6. **標準化處理** → 套用語言特定的標準化規則
7. **回應格式化** → 返回結構化結果

---

## 🔧 **故障排除**

### 本地開發問題

```bash
# Terminal 環境問題
# 如果新開的 terminal 顯示 `(base)` 而不是 `(azure-fastapi)`：

# 方法 1: 手動激活
conda activate azure-fastapi

# 方法 2: 使用快速腳本
source activate_env.sh
```

### Azure 部署問題

```bash
# 檢查 Function App 日誌
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# 檢查應用程式設定
az functionapp config appsettings list --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# 重新啟動 Function App
az functionapp restart --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

---

## 📚 **相關文檔**

### 內部文檔
- **開發協作指南**: [`CLAUDE.md`](./CLAUDE.md)
- **協作記錄**: [`COLLABORATION_LOG.md`](./COLLABORATION_LOG.md)
- **履歷優化 API 文檔**: [`docs/API_RESUME_TAILORING_V1.md`](./docs/API_RESUME_TAILORING_V1.md)
- **Bubble.io 整合指南**: [`docs/BUBBLE_IO_INTEGRATION_GUIDE.md`](./docs/BUBBLE_IO_INTEGRATION_GUIDE.md)

### 外部資源
- [Azure Functions Python 開發者指南](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [Azure OpenAI 服務文檔](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

---

## 📄 **授權**

本專案採用 MIT 授權條款。

---

*🤖 本文檔由 Claude Code 協助生成*
