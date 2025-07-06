# Workbook 逐步建立指南

## 步驟 1: 創建空白 Workbook

1. 在 Application Insights 中點擊 **Workbooks**
2. 點擊 **+ New**
3. 點擊 **Empty**

## 步驟 2: 添加標題

點擊 **Add** → **Add text**，貼上：
```markdown
# API Monitoring Dashboard

Based on Custom Events from FastAPI Application
```

## 步驟 3: 添加時間範圍參數

1. 點擊 **Add** → **Add parameters**
2. 點擊 **Add Parameter**
3. 設定：
   - Parameter name: `TimeRange`
   - Display name: `Time Range`
   - Parameter type: `Time range picker`
   - Required: `Yes`
   - Default value: `Last hour`

## 步驟 4: 請求概覽 (Tiles)

點擊 **Add** → **Add query**

### 查詢：
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

### 設定：
- Title: `Request Overview`
- Visualization: `Tiles`
- Size: `Large`

### Tiles 設定：
1. 點擊 **Tile Settings**
2. 設定 Title 為 `{Column}`
3. 設定 Value 為 `{Value}`

## 步驟 5: 響應時間趨勢圖

點擊 **Add** → **Add query**

### 查詢：
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    AvgDuration = avg(duration_ms),
    P95Duration = percentile(duration_ms, 95)
    by bin(timestamp, 5m)
```

### 設定：
- Title: `Response Time Trend`
- Visualization: `Line chart`
- Width: `50%`

## 步驟 6: 端點統計表

點擊 **Add** → **Add query**

### 查詢：
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend 
    endpoint = tostring(customDimensions.endpoint),
    success = tobool(customDimensions.success)
| summarize 
    Requests = count(),
    Failures = countif(success == false)
    by endpoint
| extend ErrorRate = round(100.0 * Failures / Requests, 2)
| order by Requests desc
```

### 設定：
- Title: `Requests by Endpoint`
- Visualization: `Grid`
- Width: `50%`

### Grid 格式化：
1. 點擊 **Column Settings**
2. 選擇 `ErrorRate` 欄位
3. Column renderer: `Heatmap`
4. Color palette: `Red to Green`

## 步驟 7: 每小時請求量

點擊 **Add** → **Add query**

### 查詢：
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| summarize RequestCount = count() by bin(timestamp, 1h)
```

### 設定：
- Title: `Hourly Request Volume`
- Visualization: `Column chart`

## 步驟 8: 最近的請求詳情

點擊 **Add** → **Add query**

### 查詢：
```kql
customEvents
| where timestamp > ago(10m)
| where name == "RequestTracked"
| extend 
    correlation_id = tostring(customDimensions.correlation_id),
    endpoint = tostring(customDimensions.endpoint),
    method = tostring(customDimensions.method),
    duration_ms = todouble(customDimensions.duration_ms),
    status_code = toint(customDimensions.status_code),
    success = tobool(customDimensions.success)
| project timestamp, correlation_id, endpoint, method, duration_ms, status_code, success
| order by timestamp desc
| take 20
```

### 設定：
- Title: `Recent Requests`
- Visualization: `Grid`

## 調試技巧

### 如果查詢失敗：

1. **檢查時間範圍**
   - 將 `ago(1h)` 改為 `ago(24h)` 或 `ago(7d)`

2. **檢查欄位名稱**
   - 在 Logs 中執行：
   ```kql
   customEvents
   | where timestamp > ago(1h)
   | take 1
   | extend dims = customDimensions
   ```
   查看實際的 customDimensions 結構

3. **簡化查詢**
   - 先從最簡單的查詢開始：
   ```kql
   customEvents
   | where name == "RequestTracked"
   | take 10
   ```

4. **檢查數據類型**
   - 如果 `tobool()` 失敗，試試：
   ```kql
   success = tostring(customDimensions.success) == "true"
   ```

### 常見問題：

1. **No data for the specified time range**
   - 擴大時間範圍
   - 確認事件名稱正確

2. **Column not found**
   - 檢查 customDimensions 的實際結構
   - 使用 `tostring()` 確保類型轉換

3. **Visualization not showing**
   - 確保查詢返回正確的欄位名稱
   - 檢查 visualization 設定

## 保存 Workbook

完成所有組件後：
1. 點擊 **Save**
2. 命名為 `API Monitoring Dashboard`
3. 選擇位置
4. 點擊 **Apply**