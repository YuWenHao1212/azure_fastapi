# Application Insights Diagnostic Queries

## 1. Check all telemetry types (last 30 minutes)
```kql
union *
| where timestamp > ago(30m)
| summarize count() by itemType
| order by count_ desc
```

## 2. Check for any HTTP-related telemetry
```kql
union *
| where timestamp > ago(30m)
| where tostring(customDimensions) contains "HTTP" or 
        tostring(customDimensions) contains "http" or
        name contains "HTTP" or
        message contains "HTTP"
| take 20
```

## 3. Check Function execution logs
```kql
traces
| where timestamp > ago(30m)
| where message contains "Function triggered" or 
        message contains "Function completed" or
        message contains "HTTP trigger"
| order by timestamp desc
| take 20
```

## 4. Check dependencies (external calls)
```kql
dependencies
| where timestamp > ago(30m)
| order by timestamp desc
| take 20
```

## 5. Check custom metrics
```kql
customMetrics
| where timestamp > ago(30m)
| order by timestamp desc
| take 20
```

## 6. Check if telemetry is being sampled out
```kql
traces
| where timestamp > ago(30m)
| where message contains "sampling" or message contains "Sampling"
| order by timestamp desc
```

## 7. Check for Azure Functions specific telemetry
```kql
traces
| where timestamp > ago(30m)
| where customDimensions.Category == "Host.Executor" or
        customDimensions.Category == "Function" or
        customDimensions.LogLevel == "Information"
| order by timestamp desc
| take 20
```

## 8. Alternative way to find HTTP requests
```kql
traces
| where timestamp > ago(30m)
| extend 
    url = tostring(customDimensions.url),
    method = tostring(customDimensions.method),
    statusCode = toint(customDimensions.status_code)
| where isnotempty(url)
| project timestamp, url, method, statusCode, message
| order by timestamp desc
```