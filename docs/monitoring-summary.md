# Index Calculation & Gap Analysis 監控實作總結

## 實作完成狀態

### ✅ 已完成項目

1. **基礎監控事件**
   - `IndexCalculationCompleted` - 追蹤相似度計算完成
   - `IndexCalAndGapAnalysisCompleted` - 追蹤組合 API 完成
   - `EmbeddingPerformance` - 追蹤 embedding 效能
   - 各種錯誤事件追蹤（Validation/Service/Unexpected）

2. **增強監控實作**
   - OpenAI Client 中添加了 token 使用追蹤
   - Gap Analysis Service 整合 TokenTrackingMixin
   - API 端點添加詳細時間分解指標
   - 成本估算功能

3. **監控基礎設施**
   - Application Insights 整合正常運作
   - 自定義事件和指標追蹤
   - 錯誤追蹤和效能監控

### ⚠️ 注意事項

1. **環境變數配置**
   - 需要設置 `EMBEDDING_API_KEY` 環境變數
   - 建議使用 `.env` 檔案管理敏感資訊
   - 生產環境應使用 Azure Key Vault

2. **Token 追蹤限制**
   - Embedding API 不返回 token 使用資訊
   - Token 估算使用粗略公式（字符數/4）
   - 實際成本可能有差異

## 監控數據查看方式

### 1. Azure Portal - Application Insights

登入 Azure Portal 並導航到：
```
Portal > Application Insights > airesumeadvisorfastapi > Logs
```

### 2. 關鍵查詢

**查看最近的 API 請求**：
```kusto
customEvents
| where timestamp > ago(10m)
| where name in ("IndexCalculationCompleted", "IndexCalAndGapAnalysisCompleted")
| project timestamp, name, customDimensions
| order by timestamp desc
```

**查看 Token 使用情況**：
```kusto
customEvents
| where timestamp > ago(1h)
| where name == "OpenAITokenUsage"
| summarize 
    TotalTokens = sum(toint(customDimensions.total_tokens)),
    AvgTokens = avg(toint(customDimensions.total_tokens))
  by bin(timestamp, 5m)
```

**查看錯誤事件**：
```kusto
customEvents
| where timestamp > ago(1h)
| where name contains "Error"
| project timestamp, name, customDimensions.error_message
```

### 3. 設置 Workbook

1. 在 Application Insights 中選擇 "Workbooks"
2. 點擊 "New"
3. 切換到 "Advanced Editor"
4. 貼上 `/azure/monitoring/index-gap-analysis-workbook.json` 的內容
5. 保存並命名為 "Index & Gap Analysis Dashboard"

## 關鍵指標說明

### 功能正常性指標
- **成功率**: API 請求成功比例
- **錯誤類型分佈**: Validation vs Service vs Internal 錯誤
- **端點可用性**: 各端點的運行狀態

### 效能指標
- **總處理時間**: 端到端響應時間
- **Index 計算時間**: 相似度計算耗時
- **Gap 分析時間**: LLM 處理耗時
- **Embedding 時間**: 文本向量化耗時

### Token 消耗指標
- **Prompt Tokens**: 輸入 token 數量
- **Completion Tokens**: 輸出 token 數量
- **總 Token 數**: 總消耗量
- **估算成本**: 基於 token 使用的成本估算

## 後續優化建議

1. **成本優化**
   - 監控高 token 消耗的請求
   - 優化 prompt 長度
   - 實施請求緩存機制

2. **效能優化**
   - 識別慢查詢模式
   - 優化 embedding 批次處理
   - 考慮異步處理長時間任務

3. **告警設置**
   - 錯誤率 > 5% 時發送告警
   - 平均處理時間 > 10 秒時告警
   - Token 使用異常高時告警

## 測試監控

使用提供的測試工具驗證監控：
```bash
python tools/test_monitoring_events.py
```

這將測試所有 API 端點並顯示預期的監控事件。