# Bubble.io 快速設定檢查清單

## 🚀 30分鐘內完成整合設定

### Phase 1: API Connector 基本設定 (5 分鐘)

- [ ] **建立新的 API Connector**
  - Name: `AIResumeAdvisor FastAPI`
  - API Root URL: `https://airesumeadvisor-fastapi.azurewebsites.net/api/v1`

- [ ] **設定認證**
  - Authentication Type: `API Key Authentication`
  - Key name: `code`
  - Key value: `[YOUR_FUNCTION_KEY]`
  - Add to: `URL Parameters (Query String)`

### Phase 2: Health Check API (5 分鐘)

- [ ] **建立 HealthCheck API Call**
  - Name: `HealthCheck`
  - Use as: `Action`
  - Method: `GET`
  - Endpoint: `/health`

- [ ] **測試 Health Check**
  - 執行 API Call
  - 確認回傳 `success: true`
  - 確認 `status: "healthy"`

### Phase 3: Resume Tailoring API (10 分鐘)

- [ ] **建立 TailorResume API Call**
  - Name: `TailorResume`
  - Use as: `Action`
  - Method: `POST`
  - Endpoint: `/tailor-resume`

- [ ] **設定 Parameters**
  ```
  code: text (required) - Azure Function Key
  job_description: text (required)
  original_resume: text (required)
  gap_analysis: object (required)
  options: object (required)
  ```

- [ ] **設定 Return Data**
  - 複製 `bubble_api_connector_config.json` 中的 return_type
  - 確保所有欄位類型正確

### Phase 4: Data Types 建立 (5 分鐘)

- [ ] **建立必要的 Data Types**
  - GapAnalysisInput
  - TailoringOptions
  - IndexCalculationResult
  - KeywordsAnalysis
  - VisualMarkers
  - OptimizationStats

### Phase 5: 測試驗證 (5 分鐘)

- [ ] **使用測試數據**
  - 複製 `bubble_api_connector_config.json` 中的 test_data
  - 執行完整的 TailorResume API 測試
  - 確認回傳完整的優化結果

---

## 🎯 關鍵驗證點

### ✅ 必須成功的測試
1. **Health Check 回傳正確**
2. **TailorResume 回傳 success: true**
3. **optimized_resume 包含 HTML 標記**
4. **index_calculation 有數值結果**
5. **visual_markers 統計正確**

### ⚠️ 常見問題解決

**401 Authentication Error:**
- 檢查 Function Key 是否正確
- 確認 Key 加在 URL Parameters (Query String) 而非 Headers

**422 Validation Error:**
- 確認 job_description 和 original_resume 都超過 200 字元
- 檢查 gap_analysis 格式是否正確

**Timeout:**
- 第一次呼叫可能需要 30-60 秒（冷啟動）
- 設定 timeout 為 180 秒

---

## 🔧 後續整合準備

### HTML 顯示元件準備
```html
<style>
.opt-new { background-color: #e8f5e8; border-left: 4px solid #4CAF50; padding: 8px; margin: 4px 0; }
.opt-modified { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 8px; margin: 4px 0; }
.opt-placeholder { background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 2px 4px; font-weight: bold; }
.opt-keyword { background-color: #d1ecf1; color: #0c5460; font-weight: bold; padding: 1px 3px; border-radius: 3px; }
.opt-keyword-existing { background-color: #d4edda; color: #155724; font-weight: bold; padding: 1px 3px; border-radius: 3px; }
</style>
```

### 工作流程設定
1. **收集用戶輸入** → gap_analysis 物件
2. **呼叫 TailorResume API**
3. **顯示優化結果** → HTML 元件
4. **顯示統計數據** → Index Calculation 結果

---

## 📱 準備好的測試案例

所有測試數據都在 `bubble_api_connector_config.json` 中，包括：
- 完整的 Job Description (1347 字元)
- 完整的 Original Resume (1287 字元)  
- Gap Analysis 物件
- Tailoring Options 物件

**預期結果:**
- 相似度改善: ~30%
- 關鍵字覆蓋率改善: ~60%
- 新增關鍵字: ~13 個
- 視覺標記: 30+ 個

---

**設定完成後即可開始調適！** 🎉