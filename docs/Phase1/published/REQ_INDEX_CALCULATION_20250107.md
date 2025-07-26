# Index Calculation & Gap Analysis API 功能需求文件

**版本**: 2.1  
**更新日期**: 2025-01-08  
**狀態**: 已根據 WenHao 反饋更新

## 更新摘要
- 澄清 job_description 通常為純文字，但支援 HTML 處理
- 確認使用 `UnifiedPromptService` 管理 prompts
- 共用現有的 Azure OpenAI 配置
- 詳細說明編碼錯誤處理和 Fallback 機制
- 更新檔案命名為更清晰的名稱
- 確認 prompt 管理使用現有的 YAML 架構
- **新增 language 參數支援多語言輸出（v2.1）**

## 1. 功能概述

### 1.1 Index_Calculation (相似度計算)
計算履歷與職缺描述之間的關鍵詞覆蓋率和語義相似度。

### 1.2 Index_Calculation_with_Gap_Analysis (相似度計算 + 差距分析)
在相似度計算基礎上，使用 LLM 進行深入的差距分析，提供改進建議。

## 2. 資料流程

### 2.1 Index_Calculation 流程
```
Input (JSON) → HTML清理 → 關鍵詞分析 → 向量相似度計算 → 結果輸出
```

### 2.2 Gap Analysis 流程
```
Index_Calculation → LLM Prompt 建構 → LLM 呼叫 → 結果解析 → HTML處理 → TinyMCE驗證 → 輸出
```

## 3. 詳細規格

### 3.1 輸入格式
```json
{
    "resume": "HTML格式的履歷內容",
    "job_description": "職缺描述（通常為純文字，但支援HTML格式）",
    "keywords": ["關鍵詞1", "關鍵詞2"] 或 "keyword1, keyword2",
    "language": "en"  // 可選，預設為 "en"。支援 "en" (英文) 或 "zh-TW" (繁體中文)
}
```

### 3.2 輸出格式

#### Index_Calculation 輸出
```json
{
    "raw_similarity_percentage": 85,
    "similarity_percentage": 92,
    "keyword_coverage": {
        "total_keywords": 10,
        "covered_count": 8,
        "coverage_percentage": 80,
        "covered_keywords": ["Python", "FastAPI"],
        "missed_keywords": ["Docker", "Kubernetes"]
    }
}
```

#### Gap Analysis 額外輸出
```json
{
    "gap_analysis": {
        "CoreStrengths": "<ol><li>強項1</li><li>強項2</li></ol>",
        "KeyGaps": "<ol><li>差距1</li><li>差距2</li></ol>",
        "QuickImprovements": "<ol><li>改進1</li><li>改進2</li></ol>",
        "OverallAssessment": "<p>整體評估內容</p>",
        "SkillSearchQueries": [
            {
                "skill_name": "Excel",
                "skill_category": "TECHNICAL",
                "description": "Advanced pivot table creation"
            }
        ]
    }
}
```

## 4. 核心功能實作細節

### 4.1 HTML 清理 (`clean_html_text`)
- 移除所有 HTML 標籤
- 解碼 HTML entities
- 正規化空白字元

### 4.2 關鍵詞覆蓋率分析 (`analyze_keyword_coverage`)
- 大小寫不敏感匹配
- 完整單詞匹配 (word boundary)
- 支援複數形式匹配
- 計算覆蓋率百分比

### 4.3 相似度計算 (`compute_similarity`)
- 使用 Azure OpenAI Embedding API
- 計算 cosine similarity
- Sigmoid 轉換調整分數分佈

### 4.4 Gap Analysis 處理
- 使用 `UnifiedPromptService` 管理 Prompt 模板（與 keyword extraction 共用相同架構）
- 根據 `language` 參數選擇對應的 Prompt 版本（en 或 zh-TW）
- 解析 XML 標籤格式的 LLM 回應
- 技能發展優先級解析 (SKILL_N::SkillName::CATEGORY::Description)
- 確保 LLM 輸出符合指定語言

### 4.5 HTML 安全處理
- 移除危險標籤 (script, style, iframe 等)
- 清理事件處理器屬性
- 移除 JavaScript 協議
- TinyMCE 相容性驗證

## 5. 配置需求

### 5.1 Azure OpenAI 配置
- 共用現有的 Azure OpenAI 配置（已在 Keyword Extraction 功能中實作）
- 使用 `src/core/config.py` 中的設定
- 包含 Embedding 和 LLM 的 endpoints、API keys 和模型版本

### 5.2 相似度計算參數
- Sigmoid 轉換參數 (x0, k)
- 關鍵詞匹配選項
- 最大輸入長度限制

## 6. 錯誤處理

### 6.1 輸入驗證
- 必填欄位檢查
- 長度限制驗證
- 關鍵詞數量限制
- language 參數驗證（只接受 "en" 或 "zh-TW"）

### 6.2 API 錯誤處理
- Azure OpenAI API 錯誤
- 超時處理
- 速率限制

### 6.3 輸出安全性
- HTML 安全驗證
- 編碼錯誤處理
  - 處理 LLM 回傳的特殊字符（如表情符號、非標準字符）
  - 範例：`content.encode('utf-8', errors='ignore').decode('utf-8')`
  - 防止因編碼問題導致程式崩潰
- Fallback 機制
  - 當 HTML 處理失敗時的備用方案
  - 範例：無法解析 HTML 時，提取純文字並轉換為安全的 HTML
  - 最終備案：返回錯誤提示訊息 `<p>Content processing failed - please check the original format</p>`

## 7. 實作建議

### 7.1 模組結構
```
src/
├── services/
│   ├── index_calculation.py   # 索引計算服務（包含相似度和關鍵詞覆蓋率）
│   ├── gap_analysis.py        # 差距分析服務
│   └── text_processing.py     # 文字處理工具（共用）
├── api/v1/
│   ├── index_calculation.py   # Index Calculation 端點
│   └── index_cal_and_gap_analysis.py  # Index Calculation + Gap Analysis 端點
└── prompts/
    └── gap_analysis/
        ├── v1.0.0-en.yaml     # 英文版 Gap Analysis Prompt
        └── v1.0.0-zh-TW.yaml  # 繁體中文版 Gap Analysis Prompt
```

**註：使用 `UnifiedPromptService` 管理所有 prompts，與 keyword extraction 共用相同的架構**

### 7.2 關鍵技術點
1. 保持與 Bubble.io 的相容性 (無 Optional 欄位)
2. 確保 HTML 輸出適合 TinyMCE 編輯器
3. 實作完整的錯誤處理和日誌記錄
4. 支援配置化的參數調整
5. language 參數的預設值處理（預設為 "en"）
6. 多語言 Prompt 的動態載入

## 8. 新架構遷移注意事項

### 8.1 從舊架構遷移的功能
- `clean_html_text` → `src/services/text_processing.py`
- `analyze_keyword_coverage` → `src/services/index_calculation.py`
- `compute_similarity` → `src/services/index_calculation.py`
- `parse_gap_response` → `src/services/gap_analysis.py`
- HTML 安全處理函數群組 → `src/services/text_processing.py`

### 8.2 配置遷移 
舊架構使用的配置需要整合到新的 `src/core/config.py`：  
- Sigmoid 轉換參數
- 關鍵詞匹配設定
- LLM 溫度和 token 限制 
- 輸入長度限制

### 8.3 Prompt 管理
- 將 `GAP_ANALYSIS_PROMPTS` 從 Python dict 轉換為 YAML 格式
- 存放在 `src/prompts/gap_analysis/` 目錄下
- 使用與 keyword extraction 相同的命名規則：
  - `v1.0.0-en.yaml` - 英文版本
  - `v1.0.0-zh-TW.yaml` - 繁體中文版本
- 透過 `UnifiedPromptService` 根據 language 參數載入對應版本
- 保留原有的 XML 標籤格式要求
- Prompt 內容需明確指定輸出語言

## 9. 測試需求

### 9.1 單元測試
- HTML 清理功能測試
- 關鍵詞覆蓋率計算測試
- 相似度計算測試
- Gap Analysis 解析測試

### 9.2 整合測試
- 完整 API 流程測試
- 錯誤情況測試
- 效能測試

### 9.3 Bubble.io 相容性測試
- 確保輸出格式符合 Bubble.io 要求
- 測試各種 HTML 內容的處理
- 驗證 TinyMCE 相容性