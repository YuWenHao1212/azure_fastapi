# Azure Application Insights 儀表板設置指南

## 步驟 1: 進入 Application Insights

1. 登入 [Azure Portal](https://portal.azure.com)
2. 搜尋並選擇 **Application Insights**
3. 選擇 **airesumeadvisorfastapi** 資源

## 步驟 2: 創建新儀表板

### 方法 A: 使用 Workbook (推薦)

1. 在左側導航中，選擇 **Workbooks** (工作簿)
2. 點擊 **+ New** (新增)
3. 點擊 **Advanced Editor** (進階編輯器)
4. 複製下面的 JSON 配置並貼上
5. 點擊 **Apply** (套用)
6. 點擊 **Save** (儲存)，命名為 "API Monitoring Dashboard"

### 方法 B: 使用 Dashboard

1. 在 Azure Portal 頂部，點擊 **Dashboard** (儀表板)
2. 點擊 **+ New dashboard** (新增儀表板)
3. 選擇 **Blank dashboard** (空白儀表板)
4. 為每個查詢添加 **Tile** (磚塊)

## 步驟 3: 添加查詢面板

以下是每個監控面板的設置步驟：

### 1. 請求概覽 (Request Overview)
- **標題**: Request Overview - Last Hour
- **查詢類型**: Logs
- **查詢**:
```kusto
requests
| where timestamp > ago(1h)
| summarize 
    RequestCount = count(), 
    AvgDuration = avg(duration), 
    P95Duration = percentile(duration, 95),
    FailureRate = countif(success == false) * 100.0 / count()
  by bin(timestamp, 5m)
| render timechart
```
- **視覺化**: Time chart

### 2. API 端點效能 (Endpoint Performance)
- **標題**: API Endpoint Performance
- **查詢**:
```kusto
requests
| where timestamp > ago(24h)
| summarize 
    Count = count(),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95),
    ErrorRate = countif(success == false) * 100.0 / count()
  by name
| order by Count desc
| render table
```
- **視覺化**: Table

### 3. 錯誤分析 (Error Analysis)
- **標題**: Top Errors - Last Hour
- **查詢**:
```kusto
requests
| where timestamp > ago(1h)
| where success == false
| summarize ErrorCount = count() by name, resultCode
| order by ErrorCount desc
| take 10
| render barchart
```
- **視覺化**: Bar chart

### 4. 自定義事件 - 關鍵字提取 (Custom Events)
- **標題**: Keyword Extraction Metrics
- **查詢**:
```kusto
customEvents
| where timestamp > ago(24h)
| where name == "keyword_extraction_request"
| extend 
    endpoint = tostring(customDimensions.endpoint),
    status_code = toint(customDimensions.status_code),
    duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    Count = count(), 
    AvgDuration = avg(duration_ms),
    SuccessRate = countif(status_code == 200) * 100.0 / count()
  by endpoint
| render table
```
- **視覺化**: Table

### 5. 安全監控 (Security Monitoring)
- **標題**: Security Threats
- **查詢**:
```kusto
customEvents
| where timestamp > ago(24h)
| where name == "request_blocked" or name == "security_threat_detected"
| extend 
    threat_type = tostring(customDimensions.threats),
    client_ip = tostring(customDimensions.client_ip)
| summarize ThreatCount = count() by threat_type
| render piechart
```
- **視覺化**: Pie chart

### 6. 依賴追蹤 (Dependencies)
- **標題**: External Dependencies
- **查詢**:
```kusto
dependencies
| where timestamp > ago(1h)
| where type == "HTTP" or name contains "openai"
| summarize 
    AvgDuration = avg(duration), 
    Count = count(),
    FailureRate = countif(success == false) * 100.0 / count()
  by name
| order by Count desc
| render table
```
- **視覺化**: Table

## 步驟 4: 儲存和分享儀表板

1. 點擊 **Save** (儲存)
2. 命名為 "AI Resume Advisor API Monitoring"
3. 選擇 **Pin to dashboard** (釘選到儀表板)
4. 設置自動重新整理（建議 5 分鐘）

## 步驟 5: 設置警報

在每個查詢面板上：
1. 點擊 **New alert rule** (新增警示規則)
2. 設定條件（例如：錯誤率 > 5%）
3. 設定動作群組（電子郵件通知）

## 無數據時的測試查詢

如果沒有數據，可以使用這些簡單查詢來測試：

```kusto
// 測試查詢 1: 檢查時間範圍
range timestamp from ago(1h) to now() step 5m
| project timestamp, value = rand()
| render timechart

// 測試查詢 2: 模擬數據
datatable(timestamp:datetime, name:string, duration:real, success:bool)
[
    datetime(2025-01-06T12:00:00Z), "/api/v1/health", 50, true,
    datetime(2025-01-06T12:05:00Z), "/api/v1/extract-jd-keywords", 1500, true,
    datetime(2025-01-06T12:10:00Z), "/api/v1/extract-jd-keywords", 2000, false
]
| render table
```

## 注意事項

1. **數據延遲**: Application Insights 數據可能需要 2-5 分鐘才會顯示
2. **查詢限制**: 免費層有查詢次數限制
3. **時區**: 注意 UTC 和本地時間的差異
4. **權限**: 確保有 Application Insights Reader 權限

## 後續步驟

1. 等待實際數據流入後，調整查詢的時間範圍和篩選條件
2. 根據業務需求自定義儀表板佈局
3. 設置定期報告發送到團隊信箱
4. 考慮整合到 Power BI 進行更高級的分析