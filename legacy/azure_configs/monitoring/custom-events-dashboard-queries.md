# Custom Events Dashboard Queries

Since Azure Functions Flex Consumption plan may not support automatic request tracking, we can use our custom events to create a comprehensive dashboard.

## 1. Request Overview (替代 requests 表)
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

## 2. Requests by Endpoint
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

## 3. Response Time Trend
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    AvgDuration = avg(duration_ms),
    P95Duration = percentile(duration_ms, 95),
    P99Duration = percentile(duration_ms, 99)
    by bin(timestamp, 5m)
| render timechart
```

## 4. Error Analysis
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| where tobool(customDimensions.success) == false
| extend 
    endpoint = tostring(customDimensions.endpoint),
    status_code = toint(customDimensions.status_code)
| summarize 
    ErrorCount = count()
    by endpoint, status_code
| order by ErrorCount desc
```

## 5. Security Events
```kql
customEvents
| where timestamp > ago(1h)
| where name == "security_threat_detected"
| extend 
    threat_type = tostring(customDimensions.threat_type),
    risk_level = tostring(customDimensions.risk_level),
    ip_address = tostring(customDimensions.ip_address)
| summarize 
    ThreatCount = count()
    by threat_type, risk_level
| order by ThreatCount desc
```

## 6. Keyword Extraction Performance
```kql
customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| where tostring(customDimensions.endpoint) contains "extract-jd-keywords"
| extend 
    duration_ms = todouble(customDimensions.duration_ms),
    success = tobool(customDimensions.success)
| summarize 
    TotalExtractions = count(),
    SuccessfulExtractions = countif(success == true),
    AvgProcessingTime = round(avg(duration_ms), 2),
    P95ProcessingTime = round(percentile(duration_ms, 95), 2)
```

## 7. Real-time Request Monitor
```kql
customEvents
| where timestamp > ago(5m)
| where name == "RequestTracked"
| extend 
    endpoint = tostring(customDimensions.endpoint),
    method = tostring(customDimensions.method),
    duration_ms = todouble(customDimensions.duration_ms),
    status_code = toint(customDimensions.status_code),
    correlation_id = tostring(customDimensions.correlation_id)
| project timestamp, endpoint, method, duration_ms, status_code, correlation_id
| order by timestamp desc
| take 50
```

## 8. Hourly Request Volume
```kql
customEvents
| where timestamp > ago(24h)
| where name == "RequestTracked"
| summarize RequestCount = count() by bin(timestamp, 1h)
| render columnchart
```

## 9. Custom Metrics Summary
```kql
customMetrics
| where timestamp > ago(1h)
| summarize 
    AvgValue = avg(value),
    MaxValue = max(value),
    MinValue = min(value),
    Count = count()
    by name
| order by name
```

## 10. Combined Dashboard View
```kql
let requests = customEvents
| where timestamp > ago(1h)
| where name == "RequestTracked"
| extend 
    endpoint = tostring(customDimensions.endpoint),
    duration_ms = todouble(customDimensions.duration_ms),
    success = tobool(customDimensions.success);
let summary = requests
| summarize 
    TotalRequests = count(),
    SuccessRate = round(100.0 * countif(success == true) / count(), 2),
    AvgDuration = round(avg(duration_ms), 2);
summary
```