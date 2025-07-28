# API 參考文檔

## 基礎資訊

### Base URL
```
https://airesumeadvisor-fastapi.azurewebsites.net
```

### 認證
所有 API 請求需要在 URL 參數中包含 host key：
```
?code=[YOUR_HOST_KEY]
```

### API 版本
目前版本：v1

### 健康檢查端點
- `/api/health` - 系統整體健康狀態
- `/api/v1/health` - 關鍵字提取服務健康狀態
- `/api/v1/tailor-resume/health` - 履歷客製化服務健康狀態

### 請求格式
- Content-Type: `application/json`
- 字元編碼：UTF-8

### 回應格式
所有 API 回應遵循統一格式：

```json
{
  "success": true,
  "data": {
    // 端點特定資料
  },
  "error": {
    "code": "",
    "message": ""
  }
}
```

## API 端點

### 資訊端點

#### 版本資訊
`GET /api/v1/version` - 獲取服務版本和功能資訊

#### Prompt 版本
`GET /api/v1/prompt-version?language=en` - 獲取關鍵字提取的 prompt 版本
`GET /api/v1/prompts/version?task=keyword_extraction&language=en` - 獲取任意任務的 prompt 版本

#### 支援的語言
`GET /api/v1/tailor-resume/supported-languages` - 獲取履歷客製化支援的語言

### 核心功能端點

### 1. 提取職缺關鍵字
`POST /api/v1/extract-jd-keywords`

從職缺描述中提取關鍵技能和要求。

**請求參數**
```json
{
  "job_description": "string (最少 50 字元，最多 20000 字元)",
  "max_keywords": 16,  // 選填，預設 16，範圍 5-25
  "language": "auto",  // 選填，"auto"|“en"|“zh-TW"，預設 "auto"
  "prompt_version": "1.4.0",  // 選填，預設 "1.4.0"
  "include_standardization": true,  // 選填，預設 true
  "use_multi_round_validation": true  // 選填，預設 true
}
```

**回應範例**
```json
{
  "success": true,
  "data": {
    "keywords": ["Python", "FastAPI", "Azure", "Docker"],
    "keyword_count": 4,
    "confidence_score": 0.85,
    "extraction_method": "2_round_intersection",
    "processing_time_ms": 2500,
    "detected_language": "en",
    "prompt_version": "1.4.0",
    "intersection_stats": {
      "intersection_count": 15,
      "round1_count": 20,
      "round2_count": 18,
      "final_count": 15,
      "supplement_count": 0,
      "strategy_used": "pure_intersection"
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-07-26T10:30:00.000Z"
}
```

### 2. 計算匹配指數
`POST /api/v1/index-calculation`

計算履歷與職缺的匹配程度。

**請求參數**
```json
{
  "resume": "string (HTML 或純文字)",
  "job_description": "string (HTML 或純文字)",
  "keywords": ["string"] 或 "string"  // 關鍵字陣列或逗號分隔字串
}
```

**回應範例**
```json
{
  "success": true,
  "data": {
    "raw_similarity_percentage": 65,
    "similarity_percentage": 75,  // 轉換後的分數
    "keyword_coverage": {
      "total_keywords": 20,
      "covered_count": 15,
      "coverage_percentage": 75,
      "covered_keywords": ["Python", "API development", "Azure"],
      "missed_keywords": ["Docker", "Kubernetes", "GraphQL", "Redis", "MongoDB"]
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-07-26T10:30:00.000Z"
}
```

### 3. 指數計算與差距分析
`POST /api/v1/index-cal-and-gap-analysis`

同時計算匹配指數並分析履歷差距。

**請求參數**
```json
{
  "resume": "string (HTML 或純文字)",
  "job_description": "string (HTML 或純文字)",
  "keywords": ["string"] 或 "string",  // 關鍵字陣列或逗號分隔字串
  "language": "en"  // 選填，"en"|“zh-TW"，預設 "en"
}
```

**回應範例**
```json
{
  "success": true,
  "data": {
    "raw_similarity_percentage": 65,
    "similarity_percentage": 75,
    "keyword_coverage": {
      "total_keywords": 20,
      "covered_count": 15,
      "coverage_percentage": 75,
      "covered_keywords": ["Python", "API development"],
      "missed_keywords": ["Docker", "Kubernetes"]
    },
    "gap_analysis": {
      "CoreStrengths": "<ul><li>Strong Python background</li><li>API development experience</li></ul>",
      "KeyGaps": "<ul><li>Container orchestration (Docker/Kubernetes)</li><li>Cloud deployment experience</li></ul>",
      "QuickImprovements": "<ul><li>Complete Docker fundamentals course</li><li>Build containerized project</li></ul>",
      "OverallAssessment": "<p>Good foundation with 75% match. Focus on DevOps skills to reach 90%+.</p>",
      "SkillSearchQueries": [
        {
          "skill_name": "Docker",
          "skill_category": "TECHNICAL",
          "description": "Container technology"
        }
      ]
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-07-26T10:30:00.000Z"
}
```

### 4. 格式化履歷
`POST /api/v1/format-resume`

將 OCR 識別的文字轉換成結構化 HTML 履歷。

**請求參數**
```json
{
  "ocr_text": "string (最少 100 字元)",  // OCR 格式: 【Type】:Content
  "supplement_info": {  // 選填，補充資訊
    "name": "string",
    "email": "string",
    "linkedin": "string",
    "phone": "string",
    "location": "string"
  }
}
```

**回應範例**
```json
{
  "success": true,
  "data": {
    "formatted_resume": "<h2>John Smith</h2>\n<p>Email: john@example.com | Phone: +1-234-567-8900</p>\n<h3>Professional Summary</h3>\n<p>Experienced software engineer...</p>",
    "sections_detected": {
      "contact": true,
      "summary": true,
      "skills": true,
      "experience": true,
      "education": true,
      "projects": false,
      "certifications": false
    },
    "corrections_made": {
      "ocr_errors": 5,
      "date_standardization": 3,
      "email_fixes": 1,
      "phone_fixes": 1
    },
    "supplement_info_used": ["email", "phone"]
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-07-26T10:30:00.000Z"
}
```

### 5. 客製化履歷
`POST /api/v1/tailor-resume`

根據職缺要求和差距分析結果優化履歷。

**請求參數**
```json
{
  "job_description": "string (50-10000 字元)",
  "original_resume": "string (100-50000 字元, HTML 格式)",
  "gap_analysis": {
    "core_strengths": ["string"],  // 3-5 項優勢
    "key_gaps": ["string"],  // 3-5 項差距
    "quick_improvements": ["string"],  // 3-5 項改進建議
    "covered_keywords": ["string"],  // 已涵蓋關鍵字
    "missing_keywords": ["string"]  // 缺少關鍵字
  },
  "options": {  // 選填
    "include_visual_markers": true,  // 預設 true
    "language": "en"  // "en"|“zh-TW"，預設 "en"
  }
}
```

**回應範例**
```json
{
  "success": true,
  "data": {
    "resume": "<h2>John Smith</h2>\n<p class='opt-modified'>Senior Software Engineer specializing in <span class='opt-keyword'>Python</span> and <span class='opt-keyword'>API development</span>...</p>",
    "improvements": "<ul><li>Added quantified achievements (35% performance improvement)</li><li>Integrated missing keywords naturally</li><li>Enhanced STAR format in experience bullets</li></ul>",
    "markers": {
      "keyword_new": 5,
      "keyword_existing": 8,
      "placeholder": 3,
      "new_section": 1,
      "modified": 12
    },
    "similarity": {
      "before": 65,
      "after": 85,
      "improvement": 20
    },
    "coverage": {
      "before": {
        "percentage": 60,
        "covered": ["Python", "API"],
        "missed": ["Docker", "Kubernetes", "Azure"]
      },
      "after": {
        "percentage": 90,
        "covered": ["Python", "API", "Docker", "Azure"],
        "missed": ["Kubernetes"]
      },
      "improvement": 30,
      "newly_added": ["Docker", "Azure"]
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

### 6. 搜尋相關課程
`POST /api/v1/courses/search`

使用向量相似度搜尋相關課程。

**請求參數**
```json
{
  "skill_name": "string (最多 100 字元)",
  "search_context": "string",  // 選填，搜尋上下文（最多 500 字元）
  "limit": 5,  // 選填，範圍 1-10，預設 5
  "similarity_threshold": 0.3  // 選填，範圍 0.1-1.0，預設 0.3
}
```

### 7. 搜尋類似課程
`POST /api/v1/courses/similar`

尋找與指定課程相似的其他課程。

**請求參數**
```json
{
  "course_id": "string",  // Coursera 課程 ID
  "limit": 5  // 選填，範圍 1-10，預設 5
}
```

**回應範例**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "python-data-science-ibm",
        "name": "Python for Data Science, AI & Development",
        "description": "Learn Python programming, data analysis with pandas, and build AI applications",
        "provider": "IBM",
        "provider_standardized": "IBM",
        "provider_logo_url": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/...",
        "price": 49.0,
        "currency": "USD",
        "image_url": "https://s3.amazonaws.com/coursera-course-photos/...",
        "affiliate_url": "https://www.coursera.org/learn/python-data-science?irclickid=...",
        "course_type": "course",
        "similarity_score": 92
      }
    ],
    "total_count": 25,
    "returned_count": 5,
    "query": "Python for data analysis and machine learning",
    "search_time_ms": 245,
    "filters_applied": {},
    "type_counts": {
      "course": 15,
      "certification": 5,
      "specialization": 3,
      "degree": 1,
      "project": 1
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

## 錯誤碼

| 錯誤碼 | 說明 | HTTP 狀態碼 |
|--------|------|-------------|
| **客戶端錯誤 (4xx)** | | |
| VALIDATION_ERROR | 輸入參數驗證失敗 | 400 |
| INVALID_REQUEST | 無效的請求格式或資料 | 400 |
| UNAUTHORIZED | 缺少或無效的 API 金鑰 | 401 |
| NOT_FOUND | 請求的資源不存在 | 404 |
| PAYLOAD_TOO_LARGE | 請求內容超過大小限制 | 413 |
| RATE_LIMIT_EXCEEDED | 超過 API 呼叫頻率限制 | 429 |
| **伺服器錯誤 (5xx)** | | |
| INTERNAL_SERVER_ERROR | 內部伺服器錯誤 | 500 |
| LLM_SERVICE_ERROR | AI 服務處理錯誤 | 500 |
| DATABASE_ERROR | 資料庫連線或查詢失敗 | 500 |
| TIMEOUT_ERROR | 請求處理超時 | 504 |
| SERVICE_UNAVAILABLE | 服務暫時無法使用 | 503 |
| **健康檢查錯誤** | | |
| HEALTH_CHECK_FAILED | 健康檢查失敗 | 503 |

## Rate Limits

- 每分鐘：60 次請求
- 每小時：1000 次請求
- 並發請求：10

## 最佳實踐

### 1. 錯誤處理
```python
import requests
from time import sleep

def call_api_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, 
                json=data,
                timeout=30  # 30 秒逾時
            )
            
            # Bubble.io 相容：檢查 success 欄位
            result = response.json()
            if result["success"]:
                return result["data"]
            else:
                error = result["error"]
                print(f"API Error: {error['code']} - {error['message']}")
                
                # 如果是暫時性錯誤，重試
                if error["code"] in ["SERVICE_UNAVAILABLE", "TIMEOUT_ERROR", "LLM_SERVICE_ERROR"]:
                    sleep(2 ** attempt)  # 指數退避
                    continue
                elif error["code"] == "RATE_LIMIT_EXCEEDED":
                    sleep(60)  # Rate limit，等待 1 分鐘
                    continue
                else:
                    raise Exception(error["message"])
                    
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            if attempt < max_retries - 1:
                sleep(2 ** attempt)
                continue
            raise
```

### 2. 重試策略
- **SERVICE_UNAVAILABLE (503)**：指數退避重試 (2^n 秒)
- **TIMEOUT_ERROR (504)**：指數退避重試 (2^n 秒)
- **LLM_SERVICE_ERROR (500)**：指數退避重試 (2^n 秒)
- **RATE_LIMIT_EXCEEDED (429)**：等待 60 秒後重試
- **VALIDATION_ERROR (400)**：不重試，檢查輸入參數
- **UNAUTHORIZED (401)**：不重試，檢查 API 金鑰
- 最多重試 3 次

### 3. 效能優化
- **平行請求**：使用 asyncio 或 threading
- **連線重用**：使用 requests.Session()
- **合理的 timeout**：建議 30 秒
- **快取結果**：關鍵字提取結果可快取 1 小時

### 4. 輸入準備建議
- **文字清理**：移除多餘空白和特殊字元
- **長度檢查**：確保符合 API 要求
- **語言一致**：同一請求使用單一語言
- **HTML 清理**：使用 BeautifulSoup 清理 HTML 標籤