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
- 使用 Azure OpenAI GPT-4
- 結構化輸出（JSON）
- Prompt 版本：v1.1.0

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
```python
import requests

response = requests.post(
    "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords",
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

### 當前效能 (Japan East + GPT-4o-mini)
- **平均回應時間**: 2.8 秒 (總時間 6.0 秒)
- **API 處理時間**: 2.8 秒
- **網路開銷**: 3.2 秒 (Function App 架構限制)
- **成功率**: 100%

### 目標效能 (Container Apps)
- **預期總時間**: 2.8 秒 (移除 3.2 秒架構開銷)
- **改善幅度**: 53% 響應時間提升

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

## 未來改進

### 短期計畫
- 支援更多語言
- 增加產業分類
- 關鍵字權重評分

### 長期計畫
- 知識圖譜整合
- 趨勢分析功能
- 個人化推薦

## 相關功能

- [履歷匹配指數](index_calculation.md)
- [差距分析](gap_analysis.md)
- [履歷客製化](resume_tailoring.md)