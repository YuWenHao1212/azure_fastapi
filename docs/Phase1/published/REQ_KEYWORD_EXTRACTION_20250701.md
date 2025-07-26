# 職位描述關鍵字提取需求規格書（更新版）

**文檔編號**: REQ_KEYWORD_EXTRACTION_20250701  
**版本**: 2.1  
**建立日期**: 2025-07-01  
**最後更新**: 2025-07-02  
**作者**: Claude Code  
**狀態**: 已發布  
**相關文檔**: REQ_KEYWORD_EXTRACTION_20250630, DESIGN_KEYWORD_EXTRACTION_20250701, TEST_CONSISTENCY_KPI_20250701, REQ_BILINGUAL_KEYWORD_20250702

---

## 版本更新說明

### v2.0 主要變更
1. **演算法優化**：新增 16 個關鍵字硬性上限，提升一致性
2. **交集優先策略**：當交集 ≥12 個時直接返回交集
3. **Prompt 版本管理**：支援 v1.0.0 和 v1.2.0 版本選擇
4. **KPI 要求更新**：新增一致性 KPI 具體目標值

---

## Work Items 規劃

### Epic
- **[#333](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/333)**: Azure FastAPI 系統遷移
  - **Owner**: Claude
  - **狀態**: Active
  - **優先級**: 高

### Feature
- **[#334](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/334)**: 職位描述關鍵字提取 API (F-007)
  - **Owner**: Claude
  - **狀態**: Active
  - **父項**: [#333](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/333)
  - **優先級**: 高（第一個開發的端點）

### User Stories

1. **[#336](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/336)**: 實作關鍵字提取服務
   - **Owner**: Cursor
   - **狀態**: Resolved
   - **驗收條件**:
     - [x] 實作 2 輪交集提取策略
     - [x] 每輪提取 25 個關鍵字（v1.2.0）
     - [x] 計算交集並應用補充策略
     - [x] 回傳最多 16 個標準化關鍵字

2. **[#337](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/337)**: 建立標準化字典
   - **Owner**: Cursor
   - **狀態**: New
   - **驗收條件**:
     - [ ] 建立 200+ 技能標準化映射
     - [ ] 建立 50+ 職位標準化映射
     - [ ] 建立 100+ 工具標準化映射
     - [ ] 實作模式化標準化規則

3. **[#338](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/338)**: 建構 API 端點
   - **Owner**: Cursor
   - **狀態**: Resolved
   - **驗收條件**:
     - [x] 實作 POST /api/v1/extract-jd-keywords
     - [x] 支援 prompt_version 參數選擇
     - [x] 請求驗證（最少 50 字元）
     - [x] 錯誤處理機制
     - [x] 回應格式符合 Bubble.io 要求

### 一致性測試 Work Items

- [x] **[#394](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/394)**: Epic: 關鍵字提取一致性測試
- [x] **[#395](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/395)**: Feature: 一致性 KPI 測試實作
- [x] **[#396](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/396)**: Test Case: 短文本一致性測試（78.1% ✅）
- [x] **[#397](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/397)**: Test Case: 長文本一致性測試（60.0% ✅）
- [x] **[#398](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/398)**: Test Case: 兩次測試相同機率驗證（39.84% ✅）

---

## 功能需求

### 1. 概述

職位描述關鍵字提取功能（F-007）是系統的核心功能之一，負責從非結構化的職位描述文本中提取標準化的關鍵字集合。v2.0 版本著重提升一致性，確保相同輸入得到更穩定的輸出。

### 2. 核心功能更新（v2.0）

#### 2.1 關鍵字數量限制
- **硬性上限**：最多返回 16 個關鍵字（即使用戶要求 20 個）
- **最小要求**：至少 12 個關鍵字（品質警告閾值）
- **理由**：從較大的交集池（20-25個）中選取固定數量，大幅提升一致性

#### 2.2 交集優先策略
```
IF 交集 ≥ 12 個 THEN
    返回交集的前 16 個（或用戶要求的數量，取較小值）
ELSE
    保留所有交集 + 智能補充至目標數量（最多 16 個）
END IF
```

#### 2.3 Prompt 版本管理
- **v1.0.0**：初始版本，每輪提取 15-22 個關鍵字
- **v1.2.0**：優化版本，每輪固定提取 25 個關鍵字
- **latest**：自動指向最新版本（目前為 v1.2.0）

### 3. 處理流程（更新版）

::: mermaid
graph TD
    A[接收職位描述] --> B[載入 Prompt 版本]
    B --> C[輸入驗證]
    C --> D{長度 >= 50?}
    D -->|否| E[返回錯誤]
    D -->|是| F[並行執行兩輪提取]
    F --> G[第1輪: 25個關鍵字]
    F --> H[第2輪: 25個關鍵字]
    G --> I[計算交集<br/>不區分大小寫]
    H --> I
    I --> J{交集 >= 12?}
    J -->|是| K[直接返回交集<br/>最多16個]
    J -->|否| L{總可用 >= 12?}
    L -->|否| M[品質警告]
    L -->|是| N[交集+智能補充<br/>最多16個]
    K --> O[標準化處理<br/>可選]
    N --> O
    M --> O
    O --> P[返回結果]
:::


### 4. 輸入規格（更新版）

#### 4.1 請求格式
```json
{
  "job_description": "職位描述文本...",
  "max_keywords": 20,
  "include_standardization": true,
  "use_multi_round_validation": true
}
```

#### 4.2 API 端點參數
```
POST /api/v1/extract-jd-keywords?prompt_version=v1.2.0
```

| 查詢參數 | 類型 | 必要 | 預設值 | 說明 |
|----------|------|------|---------|------|
| prompt_version | string | 否 | latest | Prompt 版本選擇（v1.0.0, v1.2.0, latest） |

### 5. 輸出規格（更新版）

#### 5.1 回應範例（v2.0）
```json
{
  "success": true,
  "data": {
    "keywords": [
      "Senior Data Analyst",
      "Python",
      "SQL",
      "Tableau",
      "Machine Learning",
      "AWS",
      "Data Visualization",
      "Statistics",
      "ETL",
      "Power BI",
      "Excel",
      "Data Mining",
      "R",
      "Big Data",
      "Hadoop",
      "Spark"
    ],
    "keyword_count": 16,
    "standardized_terms": [...],
    "confidence_score": 0.95,
    "processing_time_ms": 2850,
    "extraction_method": "2-round_intersection",
    "prompt_version": "v1.2.0",  // 新增欄位
    "intersection_stats": {
      "intersection_count": 23,
      "round1_count": 25,
      "round2_count": 25,
      "total_available": 27,
      "final_count": 16,
      "supplement_count": 0,
      "strategy_used": "intersection_only",  // v2.0 新策略
      "consistency_score": 0.92,  // 新增指標
      "warning": false,
      "warning_message": ""
    },
    "warning": {
      "has_warning": false,
      "message": "",
      "expected_minimum": 12,
      "actual_extracted": 16,
      "suggestion": ""
    }
  },
  "timestamp": "2025-07-01T15:30:00.000000"
}
```

### 6. 一致性 KPI 要求（新增）

#### 6.1 商業 KPI 目標
| KPI 指標 | 目標值 | 警戒值 | 測量方法 |
|---------|--------|--------|----------|
| 短文本一致率 | ≥70% | <60% | 50次測試中相同結果的比例 |
| 長文本一致率 | ≥50% | <40% | 50次測試中相同結果的比例 |
| 核心關鍵字穩定性 | 100% | <95% | Top 13 關鍵字的出現率 |
| 兩次測試相同機率 | ≥35% | <25% | 統計學 95% 信賴區間 |

#### 6.2 測試基準（已達成）
- **TSMC 短文本（1,200字符）**: 78.1% 一致率 ✅
- **BCG 長文本（5,898字符）**: 60.0% 一致率 ✅
- **兩次相同機率**: 39.84% [26.3%, 53.4%] ✅

### 7. 品質保證機制（v2.0 更新）

#### 7.1 演算法參數
```python
# 核心參數配置
MIN_RESPONSE_KEYWORDS = 12    # 最小響應關鍵字數
MAX_RETURN_KEYWORDS = 16      # 最大返回關鍵字數（硬上限）
DEFAULT_MAX_KEYWORDS = 20     # 用戶請求的預設值

# Prompt 版本配置
PROMPT_VERSIONS = {
    "v1.0.0": {"per_round": "15-22", "consistency": "baseline"},
    "v1.2.0": {"per_round": "25", "consistency": "+20%"},
    "latest": "v1.2.0"
}
```

#### 7.2 智能補充策略
當交集少於 12 個時的補充邏輯：
1. 保留所有交集關鍵字
2. 統計兩輪中非交集關鍵字的出現頻率
3. 優先選擇出現 2 次的關鍵字
4. 按原始順序補充至目標數量（最多 16 個）

### 8. 並行處理要求（新增）

#### 8.1 問題背景
Azure OpenAI 客戶端不支援真正的並行請求，需要特殊處理。

#### 8.2 解決方案
```python
# 為每個請求創建獨立的客戶端實例
async def _extract_keywords_round(self, job_description: str, round_number: int):
    client = get_azure_openai_client()  # 創建新實例
    try:
        response = await client.chat_completion(...)
        return parse_keywords(response)
    finally:
        await client.close()  # 確保關閉
```

---

## 非功能需求（更新版）

### 1. 效能需求
- **回應時間**: 
  - P50: ≤ 1.5 秒
  - P95: ≤ 3 秒
  - P99: ≤ 5 秒
- **並發處理**: 支援 10 個同時請求（使用獨立客戶端）

### 2. 可靠性需求
- **可用性**: ≥ 99.5%
- **一致性**: 
  - 短文本：≥ 70%
  - 長文本：≥ 50%
- **核心關鍵字穩定性**: 100%

### 3. 監控需求（新增）
- 每週執行一致性 KPI 測試
- 追蹤 prompt 版本使用情況
- 監控交集大小分布
- 警報：一致性低於警戒值

---

## 技術規格（更新版）

### 1. API 端點
```
POST /api/v1/extract-jd-keywords?prompt_version={version}
Content-Type: application/json
```

### 2. Prompt 版本檔案結構
```
src/prompts/keyword_extraction/
├── v1.0.0.yaml      # 初始版本
├── v1.2.0.yaml      # 優化版本
├── latest.yaml      # 符號連結 -> v1.2.0.yaml
└── versions.json    # 版本元數據
```

### 3. 測試工具
```
src/tests/consistency_kpi/
├── test_consistency_kpi.sh      # 主測試腳本
├── test_tsmc_consistency.sh     # 短文本測試
├── test_bcg_consistency.sh      # 長文本測試
├── generate_report.sh           # 報告生成
└── README.md                    # 使用說明
```

---

## 驗收標準（更新版）

### 功能驗收
- [x] 成功處理標準職位描述
- [x] 16 個關鍵字上限正確執行
- [x] 交集優先策略正確運作
- [x] Prompt 版本選擇功能正常
- [x] 品質警告機制正確觸發
- [ ] 標準化處理產生一致結果
- [x] 並行處理問題已解決

### 一致性驗收
- [x] TSMC 短文本一致率 ≥ 70%（實際：78.1%）
- [x] BCG 長文本一致率 ≥ 50%（實際：60.0%）
- [x] 兩次相同機率 ≥ 35%（實際：39.84%）
- [x] 核心關鍵字穩定性 = 100%

### 效能驗收
- [x] P50 回應時間 ≤ 1.5 秒
- [x] P95 回應時間 ≤ 3 秒
- [x] 10 個並發請求成功處理

---

## 風險與緩解措施（更新版）

### 技術風險
1. **一致性退化**
   - 風險：Prompt 更新可能影響一致性
   - 緩解：每次更新前執行完整 KPI 測試
   - 監控：設置自動化一致性監控

2. **16 個上限影響用戶體驗**
   - 風險：用戶期望 20 個但只得到 16 個
   - 緩解：在 API 文檔中明確說明
   - 考慮：未來可配置化此參數

## 雙語擴展需求（v3.0 預計）

### 背景
基於中文 JD 輸入產生英文關鍵字輸出的語言一致性問題，計劃實現雙語關鍵字提取功能。

### 功能概述
**語言一致性原則**：
- 中文 JD 輸入 → 中文關鍵字輸出
- 英文 JD 輸入 → 英文關鍵字輸出

### 支援範圍
- **支援語言**：英文 (en) + 台灣繁體中文 (zh-TW)
- **不支援語言**：簡體中文、日文、韓文等其他語言

### 相關 Work Items
- **Feature [#399](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/399)**: 雙語關鍵字提取功能（英文+繁體中文）
- **詳細規格**: 參見 [REQ_BILINGUAL_KEYWORD_20250702](REQ_BILINGUAL_KEYWORD_20250702.md)

### 技術要求
1. **語言檢測**：自動識別輸入語言 (langdetect)
2. **語言路由**：根據檢測結果選擇對應處理流程
3. **獨立資源**：繁體中文專用 Prompt (v1.2.0-zh-TW) 和標準化字典
4. **一致性標準**：繁體中文版本一致性目標 ≥ 85%（比照英文標準）

### API 擴展
```json
{
  "language": "auto|en|zh-TW",  // 新增參數
  "detected_language": "zh-TW", // 新增回應欄位
  "input_language": "auto"      // 新增回應欄位
}
```

### 實作時程
預計在 v2.0 穩定後開始實作，總工時約 60 小時。

---

### 業務風險
1. **KPI 未達標**
   - 風險：一致性低於目標值
   - 緩解：持續優化 prompt 和演算法
   - 備案：提供「高一致性模式」選項

2. **雙語功能風險**
   - 風險：語言檢測準確性不足
   - 緩解：使用成熟的 langdetect 庫，設置信心度閾值
   - 備案：提供手動語言指定選項

---

**文檔版本記錄**:
- v1.0 (2025-06-30): 初始需求
- v2.0 (2025-07-01): 新增 16 個上限、交集優先策略、一致性 KPI

**審核狀態**: ✅ 已發布  
**下次審查**: 2025-08-01