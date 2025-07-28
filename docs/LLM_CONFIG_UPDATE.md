# LLM 配置更新 - GPT-4.1 Japan East

## 📋 更新摘要

已將主要 LLM 服務更新為新的 GPT-4.1 Japan East 部署，用於處理複雜的 API 端點。

## 🎯 適用的 API 端點

新的 GPT-4.1 Japan 部署主要用於以下複雜處理端點：

- `POST /api/v1/index-cal-and-gap-analysis` - 指標計算與差距分析
- `POST /api/v1/tailor-resume` - 履歷客製化  
- `POST /api/v1/format-resume` - 履歷格式化

## 🔧 新配置詳情

### 主要 LLM 服務
```env
AZURE_OPENAI_ENDPOINT=https://airesumeadvisor.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key-here>
AZURE_OPENAI_GPT4_DEPLOYMENT=gpt-4.1-japan
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

### 取代的舊配置
- ❌ `LLM2_ENDPOINT` (舊的 Sweden Central)
- ❌ `LLM2_API_KEY` (舊的 API Key)  
- ✅ 新配置提供更好的效能和在地化支援

## 📁 已更新的檔案

1. **`.env`** - 環境變數配置更新
2. **`deployment/container-apps/container-apps-environment.yaml`** - Container Apps 環境配置
3. **`.github/workflows/deploy-container-apps.yml`** - GitHub Actions 工作流程
4. **`deployment/scripts/deploy-container-apps.sh`** - 部署腳本

## 🚀 效能預期

使用 GPT-4.1 Japan East 部署的優勢：

- **地理位置優勢**: Japan East 區域，減少延遲
- **模型版本**: GPT-4.1 提供更好的處理能力
- **API 版本**: 2025-01-01-preview 支援最新功能
- **專用部署**: 避免多租戶限制

## 🔄 向後相容性

- 保留了舊的 `LLM2_ENDPOINT` 和 `LLM2_API_KEY` 配置
- 確保現有程式碼不會中斷
- 逐步遷移策略

## 📝 測試建議

部署後測試以下端點確認新 LLM 服務正常運作：

```bash
# 測試差距分析
curl -X POST "https://your-container-app-url/api/v1/index-cal-and-gap-analysis" \
  -H "Content-Type: application/json" \
  -d '{"resume": "test resume", "job_description": "test job", "keywords": "Python,API"}'

# 測試履歷客製化  
curl -X POST "https://your-container-app-url/api/v1/tailor-resume" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "test", "original_resume": "test", "gap_analysis": {...}}'

# 測試履歷格式化
curl -X POST "https://your-container-app-url/api/v1/format-resume" \
  -H "Content-Type: application/json" \
  -d '{"ocr_text": "test OCR text"}'
```

## 🔐 安全注意事項

- 新的 API Key 已加入 `.env` 檔案
- 確保 `.env` 檔案不會提交到版本控制
- 在 Azure Container Apps 中使用 secrets 管理敏感資訊
- GitHub Actions 中使用 repository secrets

---

**更新日期**: 2025-07-28  
**適用環境**: Container Apps 部署環境  
**下一步**: 測試 API 1 (extract-jd-keywords) 遷移