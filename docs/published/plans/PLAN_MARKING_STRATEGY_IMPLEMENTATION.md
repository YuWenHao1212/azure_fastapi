# 履歷標記策略實施計畫

**日期**: 2025-01-12  
**目標**: 實施新的三層級標記策略，整合 Index Calculation 功能

## 1. 背景與需求

### 1.1 標記策略變更
- **移除** opt-strength 標記（簡化 LLM 負擔）
- **調整** opt-modified 必須使用 `<span>` 包裹（不能直接用在 `<li>` 或 `<p>`）
- **明確** 三層級架構：
  - opt-new：段落層級（新增 section）
  - opt-modified：內容層級（改寫內容）
  - opt-placeholder：數據層級（需填寫數據）

### 1.2 新功能需求
- Python 負責標記關鍵字（opt-keyword、opt-keyword-existing）
- 整合 Index Calculation 提供優化前後分數對比
- 返回新增關鍵字列表

## 2. 實施計畫

### Phase 1: 分析現有程式碼（30分鐘）

#### 2.1 檢查現有 Index Calculation 實作
- [ ] 尋找 legacy 中的 index calculation 邏輯
- [ ] 確認是否可以重用或需要重構
- [ ] 理解計算邏輯和輸入輸出格式

#### 2.2 分析 resume_tailoring.py 現況
- [ ] 檢查當前的標記邏輯
- [ ] 確認 MarkerFixer 的功能範圍
- [ ] 了解 API 回應格式

#### 2.3 檢查 LLM Prompt 結構
- [ ] 找到 prompt 檔案位置
- [ ] 分析現有標記指示
- [ ] 確認需要修改的部分

### Phase 2: 設計解決方案（45分鐘）

#### 2.4 設計 Python 關鍵字標記邏輯
```python
class EnhancedMarker:
    def mark_keywords(
        self, 
        html: str, 
        original_keywords: List[str],
        new_keywords: List[str]
    ) -> str:
        """
        標記關鍵字：
        - opt-keyword-existing: 原有關鍵字
        - opt-keyword: 新增關鍵字
        """
        pass
```

#### 2.5 設計 Index Calculation 整合
```python
class IndexCalculationService:
    def calculate_improvement(
        self,
        original_resume: str,
        optimized_resume: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        計算優化前後的匹配度提升
        返回：
        - original_score: 原始分數
        - optimized_score: 優化後分數
        - improvement_percentage: 提升百分比
        - new_keywords_added: 新增的關鍵字列表
        """
        pass
```

#### 2.6 設計新的 API 回應格式
```python
class TailoringResult(BaseModel):
    optimized_resume: str
    applied_improvements: List[str]
    optimization_stats: OptimizationStats
    visual_markers: VisualMarkerStats
    
    # 新增欄位
    index_calculation: IndexCalculationResult
    keywords_analysis: KeywordsAnalysis
```

### Phase 3: 實作核心功能（2-3小時）

#### 2.7 更新 LLM Prompt
- [ ] 移除 opt-strength 相關指示
- [ ] 更新 opt-modified 使用規則（必須用 span）
- [ ] 加強 opt-new vs opt-modified 的區分說明
- [ ] 提供明確的 HTML 範例

#### 2.8 實作 EnhancedMarker
- [ ] 關鍵字匹配演算法
- [ ] 處理重疊關鍵字
- [ ] 支援複合詞（如 "Machine Learning"）
- [ ] 大小寫不敏感但保留原始大小寫

#### 2.9 整合 Index Calculation
- [ ] 移植或重構現有邏輯
- [ ] 計算關鍵字覆蓋率
- [ ] 生成改善指標

#### 2.10 更新 resume_tailoring.py
- [ ] 整合 EnhancedMarker
- [ ] 整合 IndexCalculationService
- [ ] 更新處理流程
- [ ] 確保向後相容

### Phase 4: 測試與驗證（1-2小時）

#### 2.11 單元測試
- [ ] EnhancedMarker 測試
- [ ] Index Calculation 測試
- [ ] 整合測試

#### 2.12 API 測試
- [ ] 測試新的回應格式
- [ ] 驗證標記正確性
- [ ] 性能測試

## 3. 關鍵決策點

### 3.1 是否重用 legacy Index Calculation？
- **選項 A**: 直接移植（快速但可能有技術債）
- **選項 B**: 重新實作（乾淨但耗時）
- **建議**: 先評估 legacy 代碼品質後決定

### 3.2 關鍵字標記時機
- **選項 A**: LLM 處理後立即標記
- **選項 B**: 在 MarkerFixer 中一併處理
- **建議**: 選項 B，保持處理流程集中

### 3.3 API 回應格式變更
- **選項 A**: 新增欄位（向後相容）
- **選項 B**: 新版本 API endpoint
- **建議**: 選項 A，使用 optional 欄位

## 4. 風險評估

| 風險 | 影響 | 緩解措施 |
|-----|------|---------|
| LLM 不遵循新規則 | 標記錯誤 | 提供清晰範例，多次測試 |
| 關鍵字標記性能 | API 回應變慢 | 優化演算法，設置上限 |
| Index Calculation 不準確 | 用戶體驗差 | 充分測試，調整權重 |

## 5. 實施順序建議

1. **先檢查 legacy code**
   - 了解 Index Calculation 實作
   - 評估是否可重用

2. **更新 LLM Prompt**
   - 這是最關鍵的部分
   - 需要充分測試

3. **實作 Python 標記邏輯**
   - EnhancedMarker 類別
   - 整合到現有流程

4. **整合 Index Calculation**
   - 提供優化指標
   - 豐富 API 回應

## 6. 時間估計

- **總時間**: 4-6 小時
- **最小可行版本**: 2-3 小時（不含 Index Calculation）
- **完整版本**: 4-6 小時

## 7. 下一步行動

1. 審核此計畫
2. 決定實施範圍
3. 開始 Phase 1 的程式碼分析

---

**問題討論**：
1. 是否需要保持向後相容性？
2. Index Calculation 的優先級如何？
3. 是否需要分階段部署？