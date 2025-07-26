# 需求文檔：Resume Tailoring API

**文檔編號**: REQ_RESUME_TAILORING_20250110  
**版本**: 1.0  
**日期**: 2025-01-10  
**作者**: Claude  
**狀態**: 待審核

## 1. 業務背景

### 1.1 現狀分析
- 用戶已完成 Gap Analysis，獲得履歷與職位的差距分析
- 原始履歷已經過 Format Resume 服務轉換為結構化 HTML
- 需要基於 Gap Analysis 結果優化履歷以提高面試機會

### 1.2 業務目標
- 自動應用 Gap Analysis 建議優化履歷
- 突出展現候選人優勢
- 自然整合缺失關鍵字
- 提供視覺化標記便於用戶理解改動

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 履歷優化
- **輸入**：
  - 職位描述（Job Description）
  - 原始履歷（HTML 格式）
  - Gap Analysis 結果（優勢、改進建議、總體評估）
  - 關鍵字分析（已有/缺失關鍵字）

- **處理**：
  - Section-by-section 優化策略
  - 強制創建 Summary（如果缺少）
  - STAR/PAR 格式轉換（無標記）
  - 關鍵字自然整合
  - 量化數據占位符

- **輸出**：
  - 優化後的 HTML 履歷（含視覺標記）
  - 應用改進報告（按 section 分類）

#### 2.1.2 視覺化標記系統
```html
<!-- CSS Classes for Optimization Tracking -->
- opt-strength: 強化的優勢（綠色）
- opt-keyword: 新增的關鍵字（藍色）
- opt-placeholder: 待填數據（紅色）
- opt-new: 新增內容（紫色）
- opt-improvement: 應用的改進（橙色）
```

### 2.2 API 接口規格

#### 2.2.1 端點定義
```
POST /api/v1/tailor-resume
```

#### 2.2.2 請求格式
```json
{
  "job_description": "string",
  "original_resume": "string (HTML)",
  "gap_analysis": {
    "core_strengths": ["strength1", "strength2", "..."],
    "quick_improvements": ["improvement1", "improvement2", "..."],
    "overall_assessment": "string",
    "covered_keywords": ["keyword1", "keyword2", "..."],
    "missing_keywords": ["keyword1", "keyword2", "..."]
  },
  "options": {
    "include_visual_markers": true,
    "language": "en"       // 支援 "en" 和 "zh-TW"
  }
}
```

#### 2.2.3 響應格式
```json
{
  "success": true,
  "data": {
    "optimized_resume": "string (HTML with markers)",
    "applied_improvements": [
      "[Section: Summary] Created new professional summary...",
      "[Section: Skills] Reorganized skills into categories...",
      "[Section: Work Experience] Converted bullets to STAR format..."
    ],
    "optimization_stats": {
      "sections_modified": 5,
      "keywords_added": 8,
      "strengths_highlighted": 4,
      "placeholders_added": 6
    },
    "visual_markers": {
      "strength_count": 4,
      "keyword_count": 8,
      "placeholder_count": 6,
      "new_content_count": 1
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

### 2.3 處理邏輯

#### 2.3.1 Section 處理順序
1. **Summary**: 創建或優化
2. **Skills**: 重組並加入關鍵字
3. **Work Experience**: STAR/PAR 格式化
4. **Projects**: 相關性優化
5. **Education**: 補充相關內容
6. **其他**: 按需處理

#### 2.3.2 STAR/PAR 轉換規則
- 保持自然語言流暢性
- 不顯示格式標記（S/T/A/R/P）
- 每個 bullet point 包含完整故事
- 整合關鍵字和優勢展示

#### 2.3.3 占位符策略
```
[TEAM SIZE] - 團隊規模
[PERCENTAGE] - 百分比改進
[AMOUNT] - 金額/預算
[NUMBER] - 數量
[TIME PERIOD] - 時間週期
[USER COUNT] - 用戶數量
```
**注意**：占位符一律使用英文格式，不翻譯

#### 2.3.4 多語言支援
- **支援語言**：英文 (en)、繁體中文 (zh-TW)
- **實作方式**：單一 prompt YAML + 語言參數
- **術語標準化**：
  - 英文：使用 589 個標準化對應（skills.yaml、positions.yaml、tools.yaml、patterns.yaml）
  - 繁體中文：使用 zh_tw_standard_terms.json 定義的台灣慣用語
- **輸出規則**：
  - HTML 標籤和 CSS 類名保持英文
  - 內容根據語言參數輸出
  - 專有名詞（公司名、產品名）保持原文

## 3. 非功能需求

### 3.1 性能需求
- API 響應時間 < 30 秒
- 支援最大履歷長度：50,000 字符
- 並發處理：10 請求/秒

### 3.2 相容性需求
- Bubble.io API Connector 相容
- TinyMCE 編輯器相容（使用 Gap Analysis 的 TinyMCE 安全函數）
- 保持 HTML 結構完整性
- CSS 類名不被清理

### 3.3 安全需求
- 輸入驗證和消毒
- HTML 注入防護
- 敏感資訊不記錄

## 4. 整合需求

### 4.1 依賴服務
- Gap Analysis Service（獲取分析結果）
- LLM Service（GPT-4 for optimization）
- Monitoring Service（追蹤使用情況）

### 4.2 前端整合
- TinyMCE 顯示優化標記
- 支援標記開關切換
- 占位符點擊編輯
- 導出清潔版本

## 5. 測試需求

### 5.1 單元測試
- Prompt 構建邏輯
- HTML 標記插入
- Section 識別和處理

### 5.2 整合測試
- 完整優化流程
- 各種履歷格式
- 錯誤處理

### 5.3 驗收標準
- [ ] 所有 Gap Analysis 建議被應用
- [ ] 關鍵字自然整合
- [ ] STAR/PAR 格式正確
- [ ] 視覺標記正確顯示
- [ ] 無格式標記洩漏

## 6. 限制和約束

### 6.1 技術限制
- 依賴 LLM 輸出品質
- HTML 結構必須標準化
- 最大 token 限制（6000）

### 6.2 業務限制
- 不得虛構經歷或技能
- 保持履歷真實性
- 量化數據使用占位符

## 7. 風險和緩解

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|------|----------|
| LLM 輸出不一致 | 高 | 中 | 嚴格的 prompt 工程和驗證 |
| HTML 結構破壞 | 高 | 低 | 保留原始結構，只修改內容 |
| 標記被編輯器清理 | 中 | 中 | 使用簡單 CSS 類名 |
| 性能問題 | 中 | 低 | 實施緩存和優化 |

## 8. 未來擴展

### 8.1 短期（1-2月）
- 多語言支援（中文）
- 更多視覺化選項
- 批量處理能力

### 8.2 長期（3-6月）
- AI 寫作建議
- 行業特定優化
- A/B 測試功能

## 9. 成功指標

### 9.1 技術指標
- API 可用性 > 99.9%
- 平均響應時間 < 20秒
- 錯誤率 < 1%

### 9.2 業務指標
- 用戶滿意度 > 90%
- 優化建議採納率 > 80%
- 面試獲得率提升 > 30%

## 10. 審批記錄

| 角色 | 姓名 | 日期 | 簽名 |
|------|------|------|------|
| 產品負責人 | | | |
| 技術負責人 | | | |
| 專案經理 | | | |

---

**下一步行動**：
1. 審核並確認需求
2. 創建技術架構文檔
3. 開始實作開發