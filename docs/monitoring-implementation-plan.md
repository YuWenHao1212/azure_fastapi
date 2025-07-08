# Index Calculation & Gap Analysis 監控實作方案

## 方案 1：增強現有事件追蹤（推薦）

### 1.1 OpenAI Client Token 追蹤

修改 `openai_client.py` 來追蹤 token 使用：

```python
# 在 chat_completion 方法中
result = response.json()

# 提取 token 使用資訊
usage = result.get('usage', {})
tokens_info = {
    "prompt_tokens": usage.get('prompt_tokens', 0),
    "completion_tokens": usage.get('completion_tokens', 0),
    "total_tokens": usage.get('total_tokens', 0)
}

# 記錄到監控
monitoring_service.track_event(
    "OpenAITokenUsage",
    {
        "deployment": self.deployment_id,
        "prompt_tokens": tokens_info["prompt_tokens"],
        "completion_tokens": tokens_info["completion_tokens"],
        "total_tokens": tokens_info["total_tokens"],
        "endpoint_type": "chat_completion",
        "messages_count": len(messages),
        "temperature": temperature,
        "max_tokens": max_tokens
    }
)
```

### 1.2 Index Calculation 詳細監控

在 `index_calculation.py` service 中添加：

```python
# 在 calculate_index 方法中
embedding_start = time.time()
resume_embedding = await self.embedding_client.create_embeddings([resume_text])
jd_embedding = await self.embedding_client.create_embeddings([jd_text])
embedding_time = time.time() - embedding_start

# 追蹤 embedding 效能
monitoring_service.track_event(
    "EmbeddingPerformance",
    {
        "operation": "index_calculation",
        "text_lengths": {
            "resume": len(resume_text),
            "job_description": len(jd_text)
        },
        "processing_time_ms": round(embedding_time * 1000, 2),
        "embeddings_count": 2
    }
)
```

### 1.3 Gap Analysis 詳細監控

在 `gap_analysis.py` service 中添加：

```python
# 在 analyze_gap 方法中
llm_start = time.time()
response = await openai_client.chat_completion(...)
llm_time = time.time() - llm_start

# 從 response 提取 token 使用
usage = response.get('usage', {})

monitoring_service.track_event(
    "GapAnalysisCompleted",
    {
        "language": language,
        "prompt_tokens": usage.get('prompt_tokens', 0),
        "completion_tokens": usage.get('completion_tokens', 0),
        "total_tokens": usage.get('total_tokens', 0),
        "processing_time_ms": round(llm_time * 1000, 2),
        "skill_queries_count": len(parsed_response.get('skill_queries', [])),
        "response_sections": {
            "strengths": len(parsed_response.get('strengths', [])),
            "gaps": len(parsed_response.get('gaps', [])),
            "improvements": len(parsed_response.get('improvements', []))
        }
    }
)
```

## 方案 2：建立專門的 Metrics Service

### 2.1 新增 MetricsCollector 類別

```python
# src/services/metrics_collector.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class APIMetrics:
    """API 執行指標"""
    endpoint: str
    start_time: float
    end_time: Optional[float] = None
    
    # Token 使用
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # 效能指標
    embedding_time_ms: float = 0
    llm_time_ms: float = 0
    total_time_ms: float = 0
    
    # 結果指標
    similarity_percentage: Optional[int] = None
    keyword_coverage: Optional[int] = None
    gap_analysis_sections: Optional[dict] = None
    
    # 錯誤追蹤
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    def calculate_durations(self):
        """計算各項時間"""
        if self.end_time:
            self.total_time_ms = (self.end_time - self.start_time) * 1000

class MetricsCollector:
    """收集和報告 API 指標"""
    
    def __init__(self, monitoring_service):
        self.monitoring_service = monitoring_service
        
    def track_api_metrics(self, metrics: APIMetrics):
        """發送完整的 API 指標到 Application Insights"""
        metrics.calculate_durations()
        
        self.monitoring_service.track_event(
            "APIMetricsComplete",
            {
                "endpoint": metrics.endpoint,
                "total_time_ms": round(metrics.total_time_ms, 2),
                "embedding_time_ms": round(metrics.embedding_time_ms, 2),
                "llm_time_ms": round(metrics.llm_time_ms, 2),
                "prompt_tokens": metrics.prompt_tokens,
                "completion_tokens": metrics.completion_tokens,
                "total_tokens": metrics.total_tokens,
                "similarity_percentage": metrics.similarity_percentage,
                "keyword_coverage": metrics.keyword_coverage,
                "has_error": metrics.error_type is not None,
                "error_type": metrics.error_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

## 方案 3：Application Insights 查詢範例

### 3.1 功能正常性查詢

```kusto
// 檢查各 API 端點的成功率
customEvents
| where timestamp > ago(1h)
| where name in ("IndexCalculationCompleted", "GapAnalysisCompleted", "APIMetricsComplete")
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(customDimensions.has_error == "false" or isempty(customDimensions.has_error)),
    FailedRequests = countif(customDimensions.has_error == "true")
    by Endpoint = tostring(customDimensions.endpoint)
| extend SuccessRate = round(100.0 * SuccessfulRequests / TotalRequests, 2)
| order by Endpoint
```

### 3.2 處理時間分析

```kusto
// 分析各端點的處理時間分佈
customEvents
| where timestamp > ago(1h)
| where name == "APIMetricsComplete"
| extend 
    Endpoint = tostring(customDimensions.endpoint),
    TotalTime = todouble(customDimensions.total_time_ms),
    EmbeddingTime = todouble(customDimensions.embedding_time_ms),
    LLMTime = todouble(customDimensions.llm_time_ms)
| summarize 
    avg(TotalTime), 
    percentiles(TotalTime, 50, 90, 95, 99),
    avg(EmbeddingTime),
    avg(LLMTime)
    by Endpoint
```

### 3.3 Token 消耗分析

```kusto
// 分析 Token 使用情況
customEvents
| where timestamp > ago(1h)
| where name in ("OpenAITokenUsage", "APIMetricsComplete")
| extend 
    PromptTokens = toint(customDimensions.prompt_tokens),
    CompletionTokens = toint(customDimensions.completion_tokens),
    TotalTokens = toint(customDimensions.total_tokens),
    Endpoint = tostring(customDimensions.endpoint)
| summarize 
    TotalPromptTokens = sum(PromptTokens),
    TotalCompletionTokens = sum(CompletionTokens),
    TotalTokensUsed = sum(TotalTokens),
    AvgPromptTokens = avg(PromptTokens),
    AvgCompletionTokens = avg(CompletionTokens),
    RequestCount = count()
    by Endpoint
| extend AvgTokensPerRequest = TotalTokensUsed / RequestCount
```

### 3.4 成本估算查詢

```kusto
// 估算 API 使用成本 (假設每 1K tokens = $0.01)
customEvents
| where timestamp > ago(1d)
| where name == "APIMetricsComplete"
| extend 
    TotalTokens = toint(customDimensions.total_tokens),
    Endpoint = tostring(customDimensions.endpoint)
| summarize 
    TotalTokensUsed = sum(TotalTokens),
    RequestCount = count()
    by bin(timestamp, 1h), Endpoint
| extend EstimatedCostUSD = round(TotalTokensUsed * 0.01 / 1000, 4)
| order by timestamp desc
```

## 實作建議

1. **優先實作方案 1**：最小改動，立即可用
2. **逐步增加 MetricsCollector**：更結構化的數據收集
3. **設置 Azure Monitor Workbook**：視覺化關鍵指標

## 監控重點指標

### 必要指標
- ✅ API 成功/失敗率
- ✅ 端到端處理時間
- ✅ Token 使用量（輸入/輸出）
- ✅ 各步驟耗時（embedding, LLM, parsing）

### 建議指標
- 📊 相似度分數分佈
- 📊 關鍵詞覆蓋率分佈
- 📊 技能查詢數量
- 📊 錯誤類型分佈

### 告警設置
- 🚨 錯誤率 > 5%
- 🚨 平均處理時間 > 5 秒
- 🚨 Token 使用異常高
- 🚨 連續失敗 > 3 次