# 部署 GPT-4o-mini 到 East Asia 區域指南

**文檔編號**: DEPLOY_GPT4OMINI_EASTASIA_20250726  
**撰寫日期**: 2025-07-26  
**作者**: Claude Code  
**狀態**: 實施中  

## 目標

在 Azure East Asia 區域部署 GPT-4o-mini 模型，以改善 API 效能並降低網路延遲。

## 背景

目前的效能瓶頸分析顯示：
- 網路延遲佔總回應時間的 60.58%（約 7.3 秒）
- 主因：Function App (East Asia) → OpenAI (Sweden Central) 的跨區域通訊
- 解決方案：在 East Asia 部署 OpenAI 資源

## 實施步驟

### Step 1: 建立 Azure OpenAI 資源

```bash
# 1. 建立新的 Azure OpenAI 資源
az cognitiveservices account create \
  --name "airesumeadvisor-openai-eastasia" \
  --resource-group "airesumeadvisorfastapi" \
  --kind "OpenAI" \
  --sku "S0" \
  --location "eastasia" \
  --custom-domain "airesumeadvisor-openai-eastasia" \
  --yes

# 2. 取得資源詳細資訊
az cognitiveservices account show \
  --name "airesumeadvisor-openai-eastasia" \
  --resource-group "airesumeadvisorfastapi"

# 3. 取得 API 金鑰
az cognitiveservices account keys list \
  --name "airesumeadvisor-openai-eastasia" \
  --resource-group "airesumeadvisorfastapi"
```

### Step 2: 部署 GPT-4o-mini 模型

部署需要在 Azure Portal 進行：

1. 登入 [Azure Portal](https://portal.azure.com)
2. 導航到新建立的 OpenAI 資源
3. 選擇 "Model deployments" → "Manage Deployments"
4. 點擊 "Create new deployment"
5. 選擇：
   - Model: `gpt-4o-mini`
   - Deployment name: `gpt-4o-mini`
   - Version: 選擇最新版本
   - Capacity: 根據需求設定（建議先從 10K TPM 開始）

### Step 3: 更新應用程式配置

#### 3.1 更新環境變數

```bash
# 新增到 .env 檔案
OPENAI_EASTASIA_ENDPOINT=https://airesumeadvisor-openai-eastasia.openai.azure.com/
OPENAI_EASTASIA_KEY=[從 Step 1.3 取得的金鑰]
OPENAI_EASTASIA_DEPLOYMENT=gpt-4o-mini
```

#### 3.2 更新 Azure Function App 設定

```bash
# 設定 Function App 環境變數
az functionapp config appsettings set \
  --name "airesumeadvisor-fastapi" \
  --resource-group "airesumeadvisorfastapi" \
  --settings \
    "OPENAI_EASTASIA_ENDPOINT=https://airesumeadvisor-openai-eastasia.openai.azure.com/" \
    "OPENAI_EASTASIA_KEY=[YOUR_API_KEY]" \
    "OPENAI_EASTASIA_DEPLOYMENT=gpt-4o-mini"
```

### Step 4: 修改程式碼以支援多區域配置

#### 4.1 更新 config.py

```python
# src/core/config.py
class Settings(BaseSettings):
    # 現有的 Sweden Central 配置
    llm2_endpoint: str
    llm2_api_key: str
    
    # 新增 East Asia 配置
    openai_eastasia_endpoint: str = ""
    openai_eastasia_key: str = ""
    openai_eastasia_deployment: str = "gpt-4o-mini"
    
    # 功能開關
    use_eastasia_for_keywords: bool = True  # 關鍵字提取使用 East Asia
```

#### 4.2 更新 keyword_extraction.py

```python
# src/services/keyword_extraction.py
def _get_llm_client(self):
    """根據配置選擇適當的 LLM 客戶端"""
    settings = get_settings()
    
    if settings.use_eastasia_for_keywords and settings.openai_eastasia_endpoint:
        # 使用 East Asia 的 GPT-4o-mini
        return AzureOpenAI(
            azure_endpoint=settings.openai_eastasia_endpoint,
            api_key=settings.openai_eastasia_key,
            api_version="2024-02-01"
        )
    else:
        # 使用原本的 Sweden Central
        return self._original_client()
```

### Step 5: 效能測試與驗證

#### 5.1 建立對比測試腳本

```python
# temp/tests/scripts/test_eastasia_performance_20250726.py
import asyncio
import time
from statistics import mean, median

async def test_endpoint_performance(endpoint_config, test_cases):
    """測試特定端點的效能"""
    results = []
    
    for test_case in test_cases:
        start = time.time()
        # 呼叫 API
        response = await call_api(endpoint_config, test_case)
        duration = time.time() - start
        
        results.append({
            'endpoint': endpoint_config['name'],
            'duration': duration,
            'success': response.status_code == 200
        })
    
    return results

# 測試兩個區域
sweden_config = {'name': 'Sweden Central', 'endpoint': '...'}
eastasia_config = {'name': 'East Asia', 'endpoint': '...'}

results = await asyncio.gather(
    test_endpoint_performance(sweden_config, test_cases),
    test_endpoint_performance(eastasia_config, test_cases)
)
```

#### 5.2 品質驗證

確保 GPT-4o-mini 的輸出品質符合要求：
- 關鍵字數量：應返回 25 個（或指定數量）
- 關鍵字相關性：與 JD 高度相關
- 語言支援：正確處理中英文

### Step 6: 監控與優化

#### 6.1 設定 Application Insights 追蹤

```python
# 追蹤區域效能
custom_dimensions = {
    'endpoint': 'extract-jd-keywords',
    'region': 'eastasia',
    'model': 'gpt-4o-mini',
    'duration_ms': duration * 1000
}
```

#### 6.2 建立效能儀表板

在 Azure Monitor 建立 Workbook 追蹤：
- 各區域的平均回應時間
- 模型使用率
- 錯誤率
- 成本分析

## 預期結果

1. **效能提升**：
   - 網路延遲：7,300ms → 500-1,000ms
   - 總回應時間：12s → 3-4s
   - P95：18.6s → 4-5s

2. **成本優化**：
   - GPT-4o-mini 成本約為 GPT-4o-2 的 1/10
   - 每 1M input tokens：$0.15 (vs $1.50)
   - 每 1M output tokens：$0.60 (vs $6.00)

3. **可靠性**：
   - 減少跨區域網路問題
   - 提高服務穩定性

## 注意事項

1. **配額申請**：
   - 新區域可能需要申請配額
   - 初始配額可能較小，需根據使用量調整

2. **逐步遷移**：
   - 先在部分流量測試
   - 確認品質後再全面切換

3. **回滾計畫**：
   - 保留 Sweden Central 配置
   - 可透過功能開關快速切換

## 時間表

- Day 1-2：建立資源和部署模型
- Day 3-4：程式碼修改和測試
- Day 5-7：效能驗證和優化
- Week 2：監控和調整

## 相關資源

- [Azure OpenAI Service 區域可用性](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability)
- [GPT-4o-mini 文檔](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4o-mini)
- [Azure OpenAI 定價](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)