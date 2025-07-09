# Azure API 穩定性測試準備指南

## 測試前準備

### 1. 設定 Function Key
```bash
# 從 Azure Portal 取得 Function Key
export AZURE_FUNCTION_KEY='your-actual-function-key'
```

### 2. 安裝依賴（如果需要）
```bash
pip install aiohttp
```

### 3. 確認 Azure Function App 已部署最新版本
最新版本包含以下增強的日誌記錄：
- `[GAP_ANALYSIS_LLM]` - 完整 LLM 回應
- `[GAP_ANALYSIS]` - 處理過程詳細日誌
- `[GAP_ANALYSIS_HTML]` - 最終 HTML 輸出
- `[GAP_ANALYSIS_EMPTY]` - 空值偵測

### 4. 執行測試
```bash
python test_azure_stability_30.py
```

## 測試腳本特色

1. **偵測空值**：檢查 `<p></p>` 和 `<ol></ol>`
2. **偵測預設訊息**：檢查我們加入的 fallback 訊息
3. **詳細記錄**：
   - 每個測試的結果
   - 空值欄位
   - 預設訊息出現情況
   - 語言別統計

## 測試後分析

### 查看 Application Insights
```bash
# 查詢空值事件
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --analytics-query "customEvents | where name == 'GapAnalysisEmptyFields' | project timestamp, customDimensions | take 10"

# 查詢 LLM 完整回應
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --analytics-query "traces | where message contains '[GAP_ANALYSIS_LLM]' | take 5"
```

### 分析結果檔案
- `azure_stability_test_results_20250709/` - 個別測試結果
- `azure_stability_test_20250709.log` - 完整測試日誌
- `test_summary.json` - 統計摘要

## 預期結果

根據我們的修改，預期：
1. **不應該**再出現純 `<p></p>` 空值
2. **可能會**看到預設訊息（如果 LLM 真的沒回應）
3. **會記錄**完整的 LLM 回應供分析

## 問題類型分類

| 問題類型 | 表現 | 原因 |
|---------|------|------|
| 真空值 | `<p></p>` | LLM 回傳空的標籤內容 |
| 預設訊息 | `Unable to generate...` | 我們的 fallback 被觸發 |
| 缺少標籤 | `Overall assessment not available...` | LLM 沒有回傳該標籤 |

## 建議執行時間
選擇 Azure 負載較低的時段執行，避免因為資源限制導致問題。