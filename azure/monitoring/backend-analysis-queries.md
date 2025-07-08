# Backend Analysis Queries for Index Calculation & Gap Analysis

## 1. Token Usage and Cost Analysis

### Daily Token Usage Summary
```kusto
customEvents
| where timestamp > ago(7d)
| where name == "OpenAITokenUsage"
| extend 
    PromptTokens = toint(customDimensions.prompt_tokens),
    CompletionTokens = toint(customDimensions.completion_tokens),
    TotalTokens = toint(customDimensions.total_tokens),
    Operation = tostring(customDimensions.operation)
| summarize 
    TotalPromptTokens = sum(PromptTokens),
    TotalCompletionTokens = sum(CompletionTokens),
    TotalTokensUsed = sum(TotalTokens),
    RequestCount = count()
  by Day = bin(timestamp, 1d), Operation
| extend 
    PromptCostUSD = TotalPromptTokens * 0.01 / 1000,
    CompletionCostUSD = TotalCompletionTokens * 0.03 / 1000,
    TotalCostUSD = PromptCostUSD + CompletionCostUSD
| order by Day desc, Operation
```

### Hourly Cost Projection
```kusto
customEvents
| where timestamp > ago(24h)
| where name == "GapAnalysisCompleted"
| extend 
    EstimatedCost = todouble(customDimensions.estimated_cost_usd),
    Language = tostring(customDimensions.language)
| summarize 
    TotalCost = sum(EstimatedCost),
    AvgCostPerRequest = avg(EstimatedCost),
    RequestCount = count()
  by Hour = bin(timestamp, 1h), Language
| extend 
    ProjectedDailyCost = TotalCost * 24,
    ProjectedMonthlyCost = TotalCost * 24 * 30
| order by Hour desc
```

## 2. Performance Analysis

### API Endpoint Performance Breakdown
```kusto
customEvents
| where timestamp > ago(1h)
| where name == "IndexCalAndGapAnalysisCompleted"
| extend 
    TotalTime = todouble(customDimensions.total_time_ms),
    IndexTime = todouble(customDimensions.index_calc_time_ms),
    GapTime = todouble(customDimensions.gap_analysis_time_ms),
    ResumeLength = toint(customDimensions.resume_length),
    JDLength = toint(customDimensions.jd_length)
| summarize 
    AvgTotalTime = avg(TotalTime),
    AvgIndexTime = avg(IndexTime),
    AvgGapTime = avg(GapTime),
    P95TotalTime = percentile(TotalTime, 95),
    P95IndexTime = percentile(IndexTime, 95),
    P95GapTime = percentile(GapTime, 95),
    Count = count()
| extend 
    IndexTimeRatio = round(AvgIndexTime / AvgTotalTime * 100, 2),
    GapTimeRatio = round(AvgGapTime / AvgTotalTime * 100, 2)
```

### Embedding Performance vs Text Size
```kusto
customEvents
| where timestamp > ago(1h)
| where name == "EmbeddingPerformance"
| extend 
    ProcessingTime = todouble(customDimensions.processing_time_ms),
    ResumeLength = toint(customDimensions['text_lengths'].resume),
    JDLength = toint(customDimensions['text_lengths'].job_description),
    TotalChars = ResumeLength + JDLength
| summarize 
    AvgTime = avg(ProcessingTime),
    P95Time = percentile(ProcessingTime, 95),
    Count = count()
  by CharRange = case(
    TotalChars < 1000, "0-1K",
    TotalChars < 5000, "1K-5K",
    TotalChars < 10000, "5K-10K",
    "10K+"
  )
| order by CharRange
```

## 3. Business Metrics

### Similarity Score Distribution
```kusto
customEvents
| where timestamp > ago(24h)
| where name in ("IndexCalculationCompleted", "IndexCalAndGapAnalysisCompleted")
| extend 
    Similarity = toint(customDimensions.transformed_similarity),
    Coverage = toint(customDimensions.keyword_coverage)
| summarize 
    Count = count()
  by SimilarityRange = case(
    Similarity < 50, "0-49%",
    Similarity < 70, "50-69%",
    Similarity < 85, "70-84%",
    Similarity < 95, "85-94%",
    "95-100%"
  ),
  CoverageRange = case(
    Coverage < 50, "0-49%",
    Coverage < 70, "50-69%",
    Coverage < 85, "70-84%",
    Coverage < 95, "85-94%",
    "95-100%"
  )
| order by SimilarityRange, CoverageRange
```

### Language Usage Statistics
```kusto
customEvents
| where timestamp > ago(7d)
| where name == "GapAnalysisCompleted"
| extend Language = tostring(customDimensions.language)
| summarize 
    RequestCount = count(),
    AvgSkillsIdentified = avg(toint(customDimensions.skill_queries_count)),
    AvgProcessingTime = avg(todouble(customDimensions.processing_time_ms))
  by Language
| extend PercentageOfTotal = round(100.0 * RequestCount / toscalar(
    customEvents
    | where timestamp > ago(7d)
    | where name == "GapAnalysisCompleted"
    | count
), 2)
```

## 4. Error Analysis

### Error Rate by Type
```kusto
customEvents
| where timestamp > ago(24h)
| where name contains "Error"
| extend 
    ErrorType = case(
        name contains "Validation", "Validation",
        name contains "Service", "Service",
        name contains "Unexpected", "Internal",
        "Other"
    ),
    ErrorMessage = tostring(customDimensions.error_message)
| summarize 
    ErrorCount = count(),
    UniqueErrors = dcount(ErrorMessage)
  by ErrorType, bin(timestamp, 1h)
| render timechart
```

### Error Impact Analysis
```kusto
let errors = customEvents
| where timestamp > ago(24h)
| where name contains "Error"
| extend RequestId = tostring(customDimensions.request_id);
let allRequests = customEvents
| where timestamp > ago(24h)
| where name == "RequestStarted"
| extend RequestId = tostring(customDimensions.request_id);
allRequests
| join kind=leftouter (errors) on RequestId
| summarize 
    TotalRequests = count(),
    FailedRequests = countif(isnotnull(RequestId1)),
    SuccessfulRequests = countif(isnull(RequestId1))
  by bin(timestamp, 1h)
| extend ErrorRate = round(100.0 * FailedRequests / TotalRequests, 2)
| render timechart
```

## 5. Monitoring Alerts Setup

### Alert 1: High Error Rate
```kusto
customEvents
| where timestamp > ago(5m)
| where name contains "Error"
| summarize ErrorCount = count()
| extend AlertThreshold = 5
| where ErrorCount > AlertThreshold
```

### Alert 2: Excessive Token Usage
```kusto
customEvents
| where timestamp > ago(10m)
| where name == "OpenAITokenUsage"
| summarize AvgTokensPerRequest = avg(toint(customDimensions.total_tokens))
| extend AlertThreshold = 3000
| where AvgTokensPerRequest > AlertThreshold
```

### Alert 3: Slow Response Time
```kusto
customEvents
| where timestamp > ago(5m)
| where name contains "Completed"
| extend ProcessingTime = todouble(customDimensions.processing_time_ms)
| summarize P95Time = percentile(ProcessingTime, 95)
| extend AlertThreshold = 10000  // 10 seconds
| where P95Time > AlertThreshold
```

### Alert 4: Cost Spike Detection
```kusto
customEvents
| where timestamp > ago(1h)
| where name == "GapAnalysisCompleted"
| summarize HourlyCost = sum(todouble(customDimensions.estimated_cost_usd))
| extend AlertThreshold = 10.0  // $10 per hour
| where HourlyCost > AlertThreshold
```

## Usage Instructions

1. **Import to Application Insights**:
   - Navigate to Azure Portal > Application Insights > Logs
   - Copy and paste queries as needed
   - Save frequently used queries

2. **Create Alerts**:
   - Use Alert queries with Azure Monitor Alerts
   - Set appropriate thresholds based on your requirements
   - Configure action groups for notifications

3. **Schedule Reports**:
   - Use Logic Apps or Azure Functions to run queries periodically
   - Export results to storage or send via email

4. **Cost Optimization**:
   - Monitor token usage trends
   - Identify high-cost operations
   - Optimize prompts based on usage patterns