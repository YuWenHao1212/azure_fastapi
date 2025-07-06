# Application Insights 測試查詢

當沒有實際數據時，可以使用這些查詢來測試 Application Insights 的查詢功能。

## 1. 基本連接測試

```kusto
// 測試 Application Insights 連接
print message = "Application Insights is connected", 
      timestamp = now(), 
      testValue = 123
```

## 2. 檢查數據表結構

```kusto
// 查看 requests 表結構
requests
| take 0
| getschema 

// 查看 customEvents 表結構
customEvents
| take 0
| getschema

// 查看 dependencies 表結構
dependencies
| take 0
| getschema
```

## 3. 檢查最近的數據

```kusto
// 檢查最近 24 小時的任何請求
requests
| where timestamp > ago(24h)
| summarize count()

// 檢查最近 24 小時的任何自定義事件
customEvents
| where timestamp > ago(24h)
| summarize count()

// 檢查最近 24 小時的任何追蹤
traces
| where timestamp > ago(24h)
| summarize count()
```

## 4. 模擬數據查詢（用於測試視覺化）

```kusto
// 模擬請求趨勢
range timestamp from ago(1h) to now() step 5m
| extend 
    RequestCount = rand()*100,
    AvgDuration = rand()*1000,
    FailureRate = rand()*10
| project timestamp, RequestCount, AvgDuration, FailureRate
| render timechart

// 模擬端點性能
datatable(endpoint:string, count:long, avgDuration:real, errorRate:real)
[
    "/api/v1/health", 1000, 50.5, 0.1,
    "/api/v1/extract-jd-keywords", 500, 1500.8, 2.5,
    "/api/v1/validate", 300, 200.3, 0.5
]
| render table

// 模擬錯誤分布
datatable(errorType:string, count:long)
[
    "ValidationError", 25,
    "TimeoutError", 15,
    "AuthenticationError", 10,
    "ServerError", 5
]
| render piechart
```

## 5. 檢查 Application Insights 配置

```kusto
// 顯示當前時間（檢查時區）
print CurrentTime = now(), 
      UtcTime = datetime(now()),
      TimeZone = "UTC"

// 檢查數據保留期
.show database policy retention
```

## 6. 實用查詢模板

### 請求監控模板
```kusto
requests
| where timestamp > ago(1h)
| where name contains "api"  // 調整為您的 API 路徑
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true),
    FailedRequests = countif(success == false),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95)
| extend SuccessRate = round(100.0 * SuccessfulRequests / TotalRequests, 2)
```

### 自定義事件模板
```kusto
customEvents
| where timestamp > ago(24h)
| where name == "keyword_extraction_request"  // 替換為您的事件名稱
| extend 
    status_code = toint(customDimensions.status_code),
    duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    Count = count(),
    AvgDuration = avg(duration_ms),
    SuccessRate = countif(status_code == 200) * 100.0 / count()
```

### 錯誤分析模板
```kusto
union requests, dependencies
| where timestamp > ago(1h)
| where success == false
| summarize ErrorCount = count() by type, name
| order by ErrorCount desc
| take 10
```

## 7. 驗證監控設置

```kusto
// 檢查是否有任何遙測數據
union *
| where timestamp > ago(1h)
| summarize count() by itemType
| order by count_ desc
```

## 使用提示

1. **時間範圍**: 如果沒有數據，嘗試擴大時間範圍（如 `ago(7d)`）
2. **表名稱**: 確保使用正確的表名（requests, customEvents, dependencies, traces, exceptions）
3. **自定義維度**: 使用 `tostring()`, `toint()`, `todouble()` 轉換 customDimensions 中的值
4. **測試查詢**: 先用簡單查詢測試連接，再使用複雜查詢

## 故障排除

如果查詢沒有返回數據：

1. 確認 Application Insights 資源名稱正確
2. 檢查 Function App 是否正在運行
3. 驗證 instrumentation key 配置正確
4. 等待 2-5 分鐘讓數據傳輸到 Application Insights
5. 檢查 Function App 的診斷設置