# Application Insights Dashboard 查詢集

## 1. 檢查數據可用性

首先執行這個查詢來查看有哪些數據：

```kusto
union *
| where timestamp > ago(1h)
| summarize count() by itemType
| render piechart
```

## 2. 主要監控查詢

### 2.1 API 請求總覽
```kusto
requests
| where timestamp > ago(1h)
| where url contains "api"
| summarize 
    TotalRequests = count(),
    SuccessRequests = countif(success == true),
    FailedRequests = countif(success == false),
    AvgDuration = round(avg(duration), 2),
    P95Duration = round(percentile(duration, 95), 2)
| extend SuccessRate = round(100.0 * SuccessRequests / TotalRequests, 2)
```

### 2.2 請求趨勢圖（時間序列）
```kusto
requests
| where timestamp > ago(1h)
| where url contains "api"
| summarize 
    Requests = count(),
    AvgDuration = avg(duration),
    Errors = countif(success == false)
    by bin(timestamp, 5m)
| render timechart
```

### 2.3 端點性能分析
```kusto
requests
| where timestamp > ago(24h)
| where url contains "api"
| extend endpoint = tostring(split(parse_url(url).Path, "?")[0])
| summarize 
    RequestCount = count(),
    AvgDuration = round(avg(duration), 2),
    P95Duration = round(percentile(duration, 95), 2),
    ErrorRate = round(countif(success == false) * 100.0 / count(), 2)
    by endpoint, resultCode
| order by RequestCount desc
```

### 2.4 錯誤分析
```kusto
requests
| where timestamp > ago(24h)
| where success == false
| extend endpoint = tostring(split(parse_url(url).Path, "?")[0])
| summarize ErrorCount = count() by endpoint, resultCode
| order by ErrorCount desc
| render barchart
```

### 2.5 響應時間分布
```kusto
requests
| where timestamp > ago(1h)
| where url contains "api" and success == true
| extend ResponseTimeBucket = case(
    duration <= 100, "0-100ms",
    duration <= 500, "100-500ms", 
    duration <= 1000, "500ms-1s",
    duration <= 2000, "1-2s",
    duration <= 5000, "2-5s",
    ">5s")
| summarize Count = count() by ResponseTimeBucket
| render piechart
```

### 2.6 自定義事件 - 監控事件
```kusto
traces
| where timestamp > ago(24h)
| where message contains "RequestTracked" or message contains "RequestStarted"
| extend 
    EventType = extract("(\\w+)$", 1, message),
    Endpoint = tostring(customDimensions.endpoint),
    Method = tostring(customDimensions.method)
| summarize Count = count() by EventType, Endpoint
| render columnchart
```

### 2.7 關鍵字提取業務指標
```kusto
traces
| where timestamp > ago(24h)
| where message contains "keyword_extraction"
| extend 
    Duration = todouble(customDimensions.duration_ms),
    Success = tobool(customDimensions.success),
    Language = tostring(customDimensions.language)
| summarize 
    AvgDuration = avg(Duration),
    SuccessRate = countif(Success == true) * 100.0 / count()
    by Language
```

### 2.8 安全監控
```kusto
traces
| where timestamp > ago(24h)
| where message contains "security" or message contains "blocked"
| extend 
    SecurityEvent = tostring(customDimensions.event_name),
    RiskLevel = tostring(customDimensions.security_risk),
    ClientIP = tostring(customDimensions.client_ip)
| summarize SecurityEvents = count() by SecurityEvent, RiskLevel
| render piechart
```

### 2.9 外部依賴（OpenAI API）
```kusto
dependencies
| where timestamp > ago(1h)
| where name contains "openai" or data contains "gpt"
| summarize 
    CallCount = count(),
    AvgDuration = avg(duration),
    FailureRate = countif(success == false) * 100.0 / count()
    by name
| render table
```

### 2.10 實時健康狀態
```kusto
requests
| where timestamp > ago(5m)
| summarize 
    LastRequest = max(timestamp),
    RequestsPerMinute = count() / 5.0,
    CurrentErrorRate = countif(success == false) * 100.0 / count()
| extend 
    Status = iff(CurrentErrorRate > 10, "⚠️ Warning", "✅ Healthy"),
    MinutesSinceLastRequest = datetime_diff('minute', now(), LastRequest)
```

## 3. 建立完整儀表板的步驟

1. **在 Workbook 編輯模式中**：
   - 點擊 "+ Add" → "Add query"
   - 貼上上述查詢
   - 設定適當的視覺化類型

2. **為每個查詢設定**：
   - Title: 描述性標題
   - Size: 根據重要性選擇大小
   - Visualization: 選擇合適的圖表類型

3. **組織布局**：
   - 使用 "Add group" 來組織相關查詢
   - 拖放調整順序

4. **設定參數**（可選）：
   - Time Range 參數
   - Endpoint 篩選器
   - Success/Failure 篩選器

## 4. 儲存和分享

完成後：
1. 點擊 "Done Editing"
2. 點擊 "Save"
3. 可選：Pin to dashboard
4. 可選：Share 給團隊成員