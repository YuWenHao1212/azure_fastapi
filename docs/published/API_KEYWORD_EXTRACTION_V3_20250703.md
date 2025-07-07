# 關鍵字提取 API 文檔 v3.1 - UnifiedPromptService 版本

  

**文檔編號**: API_KEYWORD_EXTRACTION_V3_20250703

**版本**: 3.1

**建立日期**: 2025-07-03

**最後更新**: 2025-07-05

**作者**: Claude Code (Opus 4)

**狀態**: 已發布

**相關文檔**:

- DESIGN_UNIFIED_PROMPT_SERVICE_20250703

- TEST_PROMPT_VERSION_COMPARISON_20250703

- API_KEYWORD_EXTRACTION_V2_20250702 (前版本)

  

---

  

## 📋 目錄

  

1. [API 概述](#api-概述)

2. [v3.1 更新重點](#v31-更新重點)

3. [端點說明](#端點說明)

4. [請求參數](#請求參數)

5. [回應格式](#回應格式)

6. [Prompt 版本管理](#prompt-版本管理)

7. [錯誤處理](#錯誤處理)

8. [使用範例](#使用範例)

9. [一致性測試結果](#一致性測試結果)

10. [最佳實踐](#最佳實踐)

11. [Azure 部署資訊](#azure-部署資訊)

  

---

  

## API 概述

  

關鍵字提取 API v3.0 採用全新的 UnifiedPromptService 架構，提供動態 prompt 版本選擇和完全基於 YAML 的 LLM 參數配置。

  

### 核心特性

  

- **UnifiedPromptService**: 統一管理所有 prompt 和 LLM 配置

- **動態版本選擇**: 支援 prompt_version 參數動態切換

- **YAML 配置驅動**: 所有 LLM 參數從 YAML 檔案載入

- **無硬編碼參數**: 完全消除硬編碼的 temperature、top_p 等參數

- **雙語支援**: 英文 (en) 和繁體中文 (zh-TW)

- **2 輪交集策略**: 確保高一致性結果

  

---

  

## v3.1 更新重點

  

### 🚀 重大更新 (2025-07-05)

  

1. **UnifiedPromptService 整合**

```python

# 舊版 (V1): 硬編碼參數

temperature=0.0 # 硬編碼

top_p=0.1 # 硬編碼

# 新版 (V2): YAML 配置

llm_config = unified_prompt_service.get_llm_config(version)

temperature = llm_config.temperature # 從 YAML 載入

top_p = llm_config.top_p # 從 YAML 載入

```

  

2. **API 回應增強**

- 新增 `llm_config_used` 欄位，顯示實際使用的 LLM 參數

- 明確顯示使用的 prompt_version

  

3. **可用 Prompt 版本**

- `latest`: 最新版本 (目前指向 1.4.0)

- `1.4.0`: **新增！生產版本** - 改進關鍵字排序 (依重要性)

- `1.3.0`: top_p=0.1 (較高一致性)

- `1.2.0`: top_p=1.0 (較高創意性)

- `1.1.0`: 早期版本

- `1.0.0`: 初始版本

  

4. **新端點**

- `GET /api/v1/prompts/version`: 查詢特定任務和語言的活躍 prompt 版本

  

---

  

## 端點說明

  

### 主要端點

  

```http

POST /api/v1/extract-jd-keywords

```

  

從職位描述中提取關鍵字，支援動態 prompt 版本選擇。

  

### 健康檢查

  

```http

GET https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/health?code=YOUR_FUNCTION_KEY

```

  

檢查服務健康狀態，包含 prompt 管理資訊。

  

### 版本資訊

  

```http

GET https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/version?code=YOUR_FUNCTION_KEY

```

  

取得服務版本和功能資訊。

  

### Prompt 版本查詢 (新增！)

  

```http

https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/prompts/version?task=keyword_extraction&language=en&code=YOUR_FUNCTION_KEY
```

  

查詢特定任務和語言的活躍 prompt 版本。

  

---

  

## 請求參數

  

```json

{

"job_description": "string", // 必填，職位描述文字

"max_keywords": 16, // 選填，最多關鍵字數 (5-25，預設 16)

"include_standardization": true, // 選填，是否標準化 (預設 true)

"use_multi_round_validation": true, // 選填，使用 2 輪策略 (預設 true)

"prompt_version": "1.4.0", // 選填，prompt 版本 (預設 "1.4.0")

"language": "auto" // 選填，語言 (auto/en/zh-TW，預設 auto)

}

```

  

### prompt_version 參數詳解

  

| 版本 | top_p | temperature | 特性 | 狀態 |

|------|-------|-------------|------|------|

| 1.4.0 | 0.1 | 0.0 | **生產版本** - 改進排序邏輯 | active |

| 1.3.0 | 0.1 | 0.0 | 高一致性，穩定結果 | stable |

| 1.2.0 | 1.0 | 0.0 | 高創意性，多樣化結果 | stable |

| 1.1.0 | 0.1 | 0.0 | 早期改進版本 | stable |

| 1.0.0 | 0.1 | 0.0 | 初始版本 | stable |

| latest | - | - | 自動選擇最新版本 (目前=1.4.0) | - |

  

---

  

## 回應格式

  

### 成功回應 (200)

  

```json

{

"success": true,

"data": {

"keywords": [

"Machine Learning",

"Python",

"Data Analysis",

// ... 最多 16 個關鍵字

],

"keyword_count": 16,

"standardized_terms": [

{

"original": "Python programming",

"standardized": "Python",

"method": "dictionary"

}

],

"confidence_score": 0.85,

"processing_time_ms": 2500,

"extraction_method": "pure_intersection",

"intersection_stats": {

"intersection_count": 14,

"round1_count": 16,

"round2_count": 16,

"total_available": 18,

"final_count": 16,

"supplement_count": 2,

"strategy_used": "supplement",

"warning": false,

"warning_message": ""

},

"warning": {

"has_warning": false,

"message": "",

"expected_minimum": 12,

"actual_extracted": 16,

"suggestion": ""

},

"prompt_version": "1.4.0", // 實際使用的版本

"prompt_version_used": "1.4.0", // 同上，為相容性保留

"llm_config_used": { // V3 新增！

"temperature": 0.0,

"top_p": 0.1,

"seed": 42,

"max_tokens": 500

},

"detected_language": "en",

"input_language": "auto",

"language_detection_time_ms": 120,

"cache_hit": false

},

"error": {

"code": "",

"message": "",

"details": ""

},

"timestamp": "2025-07-03T10:00:00.000Z"

}

```

  

---

  

## Prompt 版本管理

  

### YAML 配置結構

  

每個 prompt 版本都有對應的 YAML 檔案：

  

```yaml

# /src/prompts/keyword_extraction/v1.4.0-en.yaml

version: "1.4.0"

metadata:

author: "DevOps Team"

created_at: "2025-07-05T10:00:00Z"

description: "Enhanced keyword extraction with importance-based ordering requirement"

status: "active"

  

llm_config:

temperature: 0.0

max_tokens: 500

seed: 42

top_p: 0.1 # 關鍵參數！

frequency_penalty: 0.0

presence_penalty: 0.0

  

prompts:

system: |

You are an expert keyword extractor...

user: |

Extract keywords from this job description...

```

  

### 支援的語言路徑

  

- 英文: `/src/prompts/keyword_extraction/`

- 繁中: `/src/prompts/keyword_extraction/zh-TW/`

  

---

  

## 錯誤處理

  

### 錯誤回應格式

  

```json

{

"success": false,

"data": {},

"error": {

"code": "VALIDATION_ERROR",

"message": "輸入參數驗證失敗",

"details": "Job description too short after trimming"

},

"timestamp": "2025-07-03T10:00:00.000Z"

}

```

  

### 錯誤代碼

  

| 代碼 | HTTP 狀態 | 說明 |

|------|-----------|------|

| VALIDATION_ERROR | 400 | 輸入參數無效 |

| SERVICE_UNAVAILABLE | 503 | Azure OpenAI 服務不可用 |

| TIMEOUT_ERROR | 500 | 請求處理超時 |

| INTERNAL_SERVER_ERROR | 500 | 內部伺服器錯誤 |

  

---

  

## 使用範例

  

### 使用 v1.4.0 (生產版本 - 預設)

  

```bash

curl -X POST "http://localhost:8000/api/v1/extract-jd-keywords" \

-H "Content-Type: application/json" \

-d '{

"job_description": "We are seeking a Senior Python Developer with expertise in machine learning...",

"max_keywords": 16

}'

```

  

### 查詢活躍 Prompt 版本 (新增！)

  

```bash

curl -X GET "http://localhost:8000/api/v1/prompts/version?task=keyword_extraction&language=en"

```

  

### 使用 v1.3.0 (高一致性)

  

```bash

curl -X POST "http://localhost:8000/api/v1/extract-jd-keywords" \

-H "Content-Type: application/json" \

-d '{

"job_description": "We are seeking a Senior Python Developer with expertise in machine learning...",

"prompt_version": "1.3.0",

"max_keywords": 16

}'

```

  

### 使用 v1.2.0 (高創意性)

  

```bash

curl -X POST "http://localhost:8000/api/v1/extract-jd-keywords" \

-H "Content-Type: application/json" \

-d '{

"job_description": "We are seeking a Senior Python Developer with expertise in machine learning...",

"prompt_version": "1.2.0",

"max_keywords": 16

}'

```

  

### Python 範例

  

```python

import httpx

import asyncio

  

async def extract_keywords(job_description, version="1.3.0"):

async with httpx.AsyncClient() as client:

response = await client.post(

"http://localhost:8000/api/v1/extract-jd-keywords",

json={

"job_description": job_description,

"prompt_version": version,

"max_keywords": 16

}

)

return response.json()

  

# 執行

result = asyncio.run(extract_keywords("Your JD here", "1.3.0"))

print(f"Keywords: {result['data']['keywords']}")

print(f"LLM Config: {result['data']['llm_config_used']}")

```

  

---

  

## 一致性測試結果

  

### BCG Lead Data Scientist JD 測試

  

使用 20 次重複測試的結果：

  

| 版本 | top_p | 唯一組合 | 一致性率 | 95% CI |

|------|-------|----------|----------|---------|

| v1.2.0 | 1.0 | 多種 | ~20% | [15%, 25%] |

| v1.3.0 | 0.1 | 2-3種 | ~65% | [58%, 72%] |

  

### v1.3.0 主要組合差異

  

兩個主要組合僅在第 16 個關鍵字不同：

- Combo 1: Strategic Decision Making

- Combo 2: Optimization

  

這反映了多個同等重要關鍵字競爭最後位置的情況。

  

---

  

## 最佳實踐

  

### 1. 選擇適合的 Prompt 版本

  

- **生產環境**: 使用 `v1.4.0` 或不指定 (預設)

- **一致性優先**: 使用 `v1.3.0` (top_p=0.1)

- **創意性優先**: 使用 `v1.2.0` (top_p=1.0)

- **自動選擇**: 使用 `latest` (目前=1.4.0)

  

### 2. 處理 API 速率限制

  

```python

# 批次請求時加入延遲

for jd in job_descriptions:

result = await extract_keywords(jd)

await asyncio.sleep(1.5) # 避免速率限制

```

  

### 3. 監控 LLM 配置

  

始終檢查 `llm_config_used` 欄位以確認實際使用的參數：

  

```python

if result['data']['llm_config_used']['top_p'] == 0.1:

print("使用高一致性配置")

```

  

### 4. 處理警告

  

檢查 `warning` 欄位以了解提取品質：

  

```python

if result['data']['warning']['has_warning']:

print(f"警告: {result['data']['warning']['message']}")

print(f"建議: {result['data']['warning']['suggestion']}")

```

  

---

  

## 遷移指南

  

### 從 v2.0 遷移到 v3.0

  

1. **無需修改請求格式** - v3.0 完全向後相容

2. **新增功能為選用** - llm_config_used 是額外資訊

3. **預設行為不變** - 仍使用 latest 版本

  

### 主要差異

  

| 功能 | v2.0 | v3.0 |

|------|------|------|

| LLM 參數 | 硬編碼 | YAML 配置 |

| prompt_version | 部分支援 | 完全支援 |

| 回應資訊 | 基本 | 包含 llm_config_used |

| 服務架構 | KeywordExtractionService | KeywordExtractionServiceV2 |

  

---

  

## Azure 部署資訊

  

### 生產環境端點

  

```

https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/

```

  

### 認證方式

  

Azure Function App 需要使用 Function Key 進行認證：

  

```bash

# 範例：查詢活躍 prompt 版本

curl -X GET "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/prompts/version?task=keyword_extraction&language=en&code=YOUR_FUNCTION_KEY"

  

# 範例：提取關鍵字

curl -X POST "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords?code=YOUR_FUNCTION_KEY" \

-H "Content-Type: application/json" \

-d '{

"job_description": "Your job description here",

"max_keywords": 16

}'

```

  

### 部署狀態 (2025-07-05)

  

- **活躍 Prompt 版本**:

- 英文 (en): v1.4.0

- 繁體中文 (zh-TW): v1.4.0

- **預設 Prompt 版本**: v1.4.0

- **服務狀態**: 健康

- **CI/CD**: GitHub Actions 自動部署至 main 分支

  

### CORS 設定

  

僅允許以下來源存取 API：

- `https://airesumeadvisor.com`

- `https://airesumeadvisor.bubbleapps.io`

- `https://airesumeadvisor.bubble.io`

- `http://localhost:3000` (開發環境)

- `http://localhost:8000` (測試環境)

  

### 監控與日誌

  

- **Application Insights**: airesumeadvisor-fastapi-insights

- **資源群組**: airesumeadvisorfastapi

- **區域**: East Asia

  

---

  

*文檔更新: 2025-07-05 by Claude Code*

*服務版本: 2.0.0 (API endpoint v1)*