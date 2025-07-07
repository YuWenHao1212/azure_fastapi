# 測試查詢 - 逐個驗證

在 Application Insights Logs 中逐個測試這些查詢：

## 1. 基本測試 - 確認數據存在
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| take 10
```

## 2. 檢查數據結構
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| take 1
| project customDimensions
```

## 3. 請求統計（簡化版）
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| extend 
    success = tostring(customDimensions.success) == "true"
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true),
    FailedRequests = countif(success == false)
```

## 4. 端點統計（簡化版）
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| extend 
    endpoint = tostring(customDimensions.endpoint)
| summarize 
    Requests = count()
    by endpoint
| order by Requests desc
```

## 5. 響應時間趨勢（簡化版）
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| extend duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    AvgDuration = avg(duration_ms)
    by bin(timestamp, 5m)
| order by timestamp asc
```

## 修正常見問題

### 如果 success 欄位轉換失敗
```kql
// 檢查 success 的實際值
customEvents
| where name == "RequestTracked"
| take 10
| project success_value = tostring(customDimensions.success)
```

### 如果時間範圍沒有數據
```kql
// 查看最近的事件時間
customEvents
| where name == "RequestTracked"
| summarize max_time = max(timestamp), min_time = min(timestamp)
```

### 如果 duration_ms 轉換失敗
```kql
// 檢查 duration_ms 的值
customEvents
| where name == "RequestTracked"
| extend duration_raw = tostring(customDimensions.duration_ms)
| project duration_raw
| take 10
```

## Workbook 創建步驟

1. **先在 Logs 中測試每個查詢**
2. **確認查詢返回預期結果**
3. **在 Workbook 中逐個添加**
4. **如果出錯，簡化查詢直到工作**
5. **逐步增加複雜度**

## 最簡單的 Workbook 起始點

### Step 1: 只顯示總請求數
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| count
```

### Step 2: 添加成功/失敗
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| extend success = tostring(customDimensions.success) == "true"
| summarize 
    Total = count(),
    Success = countif(success == true)
```

### Step 3: 逐步增加更多指標

記住：**從簡單開始，逐步構建！**