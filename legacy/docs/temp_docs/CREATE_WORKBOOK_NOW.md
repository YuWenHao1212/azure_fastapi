# 創建 Application Insights Workbook - 立即執行

## ✅ 數據已確認存在

customEvents 表格中現在有以下事件：
- **RequestStarted** - 請求開始時的事件
- **RequestTracked** - 請求完成時的事件（含響應時間、狀態碼等）

## 🚀 快速創建步驟

### 1. 開啟 Azure Portal
前往: https://portal.azure.com

### 2. 導航到 Application Insights
- Resource Group: `airesumeadvisorfastapi`
- Application Insights: `airesumeadvisorfastapi`

### 3. 創建 Workbook

#### 方法 A: 導入 JSON (推薦)
1. 點擊左側選單 **Workbooks**
2. 點擊 **+ New**
3. 點擊 **Advanced Editor** (</> 圖標)
4. 刪除預設內容
5. 貼上 `/azure/monitoring/custom-events-workbook.json` 的內容
6. 點擊 **Apply**
7. 點擊 **Save**，命名為 "API Monitoring Dashboard"

#### 方法 B: 手動創建
如果 JSON 導入有問題，使用以下查詢手動創建：

### 4. 核心查詢

#### 請求概覽 (Tiles視圖)
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend 
    endpoint = tostring(customDimensions.endpoint),
    method = tostring(customDimensions.method),
    duration_ms = todouble(customDimensions.duration_ms),
    status_code = toint(customDimensions.status_code),
    success = tobool(customDimensions.success)
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true),
    FailedRequests = countif(success == false),
    AvgDuration = round(avg(duration_ms), 2),
    P95Duration = round(percentile(duration_ms, 95), 2)
| extend SuccessRate = round(100.0 * SuccessfulRequests / TotalRequests, 2)
```

#### 響應時間趨勢 (Time Chart)
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    AvgDuration = avg(duration_ms),
    P95Duration = percentile(duration_ms, 95)
    by bin(timestamp, 5m)
| render timechart
```

#### 端點性能 (Table)
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend 
    path = tostring(customDimensions.path),
    method = tostring(customDimensions.method),
    success = tobool(customDimensions.success),
    duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    Requests = count(),
    Failures = countif(success == false),
    AvgDuration = round(avg(duration_ms), 2),
    P95Duration = round(percentile(duration_ms, 95), 2)
    by path, method
| extend ErrorRate = round(100.0 * Failures / Requests, 2)
| order by Requests desc
```

#### 即時請求流 (Table)
```kql
customEvents
| where timestamp > ago(10m)
| where name in ("RequestStarted", "RequestTracked")
| extend 
    event_type = name,
    correlation_id = tostring(customDimensions.correlation_id),
    endpoint = tostring(customDimensions.endpoint),
    duration_ms = todouble(customDimensions.duration_ms),
    status_code = toint(customDimensions.status_code)
| project timestamp, event_type, correlation_id, endpoint, duration_ms, status_code
| order by timestamp desc
| take 50
```

## 📊 驗證數據

在 Application Insights 的 Logs 中執行：
```kql
customEvents
| where timestamp > ago(5m)
| summarize count() by name
```

應該看到：
- RequestStarted
- RequestTracked

## 🎯 下一步

1. 創建 Alert Rules：
   - 錯誤率 > 5%
   - P95 響應時間 > 2000ms
   - 任何 5xx 錯誤

2. 設置 Availability Tests：
   - 每 5 分鐘檢查 /health endpoint
   - 多地區檢查

3. 導出到 Power BI（可選）：
   - 用於管理層儀表板
   - 長期趨勢分析