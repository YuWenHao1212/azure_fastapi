# 關鍵字提取功能

## 功能概述

從職缺描述（Job Description）中智能提取關鍵技能、要求和資格，協助求職者快速理解職位需求。

## API 端點

`POST /api/v1/extract-jd-keywords`

## 核心功能

### 1. 多語言支援
- 自動偵測語言（英文/繁體中文）
- 語言特定的 prompt 優化
- 保持原始語言的關鍵字

### 2. 分類提取
將關鍵字分為多個類別：
- **技術技能**（Technical Skills）
- **軟技能**（Soft Skills）  
- **認證資格**（Certifications）
- **工具與框架**（Tools & Frameworks）
- **產業知識**（Domain Knowledge）

### 3. 智能去重
- 移除重複的關鍵字
- 合併相似概念
- 保留最具代表性的表述

## 技術實作

### LLM 整合
- 使用 Azure OpenAI GPT-4.1 mini (Japan East 部署)
- 結構化輸出（JSON）
- Prompt 版本：v1.4.0
- API 版本：2025-01-01-preview

### 處理流程
1. 接收職缺描述文字
2. 語言偵測與驗證
3. 呼叫 LLM 提取關鍵字
4. 後處理與分類
5. 返回結構化結果

### 錯誤處理
- 輸入驗證（200-5000 字元）
- LLM 逾時保護（30 秒）
- 重試機制（3 次）
- 降級處理

## 使用範例

### 請求範例

#### Container Apps 部署 (目標架構)
```python
import requests

response = requests.post(
    "https://airesumeadvisor-api.[region].azurecontainerapps.io/api/v1/extract-jd-keywords",
    json={
        "job_description": """
        We are looking for a Senior Python Developer with 5+ years experience.
        Required skills: Python, FastAPI, Docker, AWS, PostgreSQL.
        Nice to have: Kubernetes, React, TypeScript.
        Strong communication skills and team collaboration required.
        """,
        "language": "auto",  # 可選：auto, en, zh-TW
        "max_keywords": 16,  # 可選：5-25
        "prompt_version": "1.4.0"  # 可選：指定 prompt 版本
    }
)
```

#### Function Apps 部署 (當前)
```python
import requests

response = requests.post(
    "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/extract-jd-keywords",
    params={"code": "YOUR_HOST_KEY"},
    json={
        "job_description": """
        We are looking for a Senior Python Developer with 5+ years experience.
        Required skills: Python, FastAPI, Docker, AWS, PostgreSQL.
        Nice to have: Kubernetes, React, TypeScript.
        Strong communication skills and team collaboration required.
        """
    }
)
```

### 回應範例
```json
{
  "success": true,
  "data": {
    "keywords": [
      "Python", "FastAPI", "Docker", "AWS", "PostgreSQL",
      "Kubernetes", "React", "TypeScript", "communication skills",
      "team collaboration", "Senior Developer", "5+ years experience"
    ],
    "categories": {
      "technical_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
      "tools_frameworks": ["AWS", "Kubernetes", "React", "TypeScript"],
      "soft_skills": ["communication skills", "team collaboration"],
      "experience": ["Senior Developer", "5+ years experience"]
    }
  },
  "error": {
    "code": "",
    "message": ""
  }
}
```

## 效能指標

### 當前效能 (Function Apps - Japan East + GPT-4.1 mini)
- **平均回應時間**: 2.8 秒 (API 處理)
- **總回應時間**: 6.0 秒 (含 Function App 開銷)
- **架構開銷**: 3.2 秒 (Function App + ASGI 適配器)
- **成功率**: 100%
- **P95 目標**: < 3 秒 (Container Apps 目標)

### 目標效能 (Container Apps - 預期改善)
- **預期 API 處理時間**: 2.8 秒 (不變)
- **預期總回應時間**: 2.8 秒 (移除架構開銷)
- **效能提升**: 53% 回應時間改善
- **延遲減少**: -3.2 秒 架構開銷消除

### 架構比較
| 指標 | Function Apps | Container Apps | 改善 |
|------|---------------|----------------|------|
| API 處理時間 | 2.8s | 2.8s | 0% |
| 架構開銷 | 3.2s | 0s | -100% |
| 總回應時間 | 6.0s | 2.8s | -53% |
| 冷啟動時間 | 2-5s | 0.5-1s | -75% |

### 準確度
- 關鍵字召回率：> 90%
- 分類準確度：> 85%
- 誤判率：< 5%

## 最佳實踐

### 輸入準備
1. 提供完整的職缺描述
2. 包含技能要求部分
3. 保持原始格式

### 結果使用
1. 用於履歷優化
2. 技能差距分析
3. 求職準備指引

## 限制與注意事項

### 輸入限制
- 最小長度：200 字元
- 最大長度：5000 字元
- 支援語言：英文、繁體中文

### 已知限制
1. 可能遺漏隱含要求
2. 產業特定術語需持續優化
3. 新興技術關鍵字需要更新

## Container Apps 遷移狀態

### 🚀 遷移計畫 (5天執行)
- **Day 1**: ✅ 基礎環境建立 (Dockerfile, Container Apps 環境)
- **Day 2**: 🔄 extract-jd-keywords API 遷移與測試 (進行中)
- **Day 3**: ⏳ index-calculation API 遷移
- **Day 4**: ⏳ gap-analysis 與 tailor-resume API 遷移  
- **Day 5**: ⏳ 效能測試與流量切換

### 🔧 技術配置更新
- **LLM 服務**: GPT-4.1 mini Japan East 部署
- **API 端點**: 移除 host key 認證要求
- **監控**: Application Insights 整合保持
- **CORS**: 支援 Bubble.io 前端整合

### 📊 驗證指標
- 回應時間 < 3 秒 (P95)
- 成功率 > 99.9%
- 功能一致性 100%
- 前端整合無中斷

## 未來改進

### 短期計畫 (Q1 2025)
- ✅ Container Apps 架構遷移
- 🔄 GPT-4.1 mini Japan East 整合
- ⏳ 多輪驗證算法優化
- ⏳ 產業特定關鍵字詞典

### 長期計畫 (Q2-Q4 2025)
- 支援更多語言 (日文、韓文)
- 知識圖譜整合
- 即時趨勢分析
- 個人化推薦算法

## 相關功能

- [履歷匹配指數](index_calculation.md)
- [差距分析](gap_analysis.md)
- [履歷客製化](resume_tailoring.md)