# 增強版監控實作指南

## 1. OpenAI Client Token 追蹤實作

### 修改 `src/services/openai_client.py`

在 `_chat_completion_non_stream` 方法的第 153 行後添加：

```python
# 在取得 result 後立即追蹤 token 使用
from src.core.monitoring_service import monitoring_service

# 提取 token 使用資訊
usage = result.get('usage', {})
monitoring_service.track_event(
    "OpenAITokenUsage",
    {
        "deployment": self.deployment_id,
        "operation": "chat_completion",
        "prompt_tokens": usage.get('prompt_tokens', 0),
        "completion_tokens": usage.get('completion_tokens', 0),
        "total_tokens": usage.get('total_tokens', 0),
        "model": result.get("model", self.deployment_id),
        "finish_reason": result.get('choices', [{}])[0].get('finish_reason', 'unknown'),
        "temperature": payload.get('temperature', 0.7),
        "max_tokens": payload.get('max_tokens', 1000)
    }
)
```

## 2. Gap Analysis Service 增強監控

### 修改 `src/services/gap_analysis.py`

在第 16 行後添加 mixin import：
```python
from src.services.token_tracking_mixin import TokenTrackingMixin
```

修改 class 定義（第 160 行）：
```python
class GapAnalysisService(TokenTrackingMixin):
```

在 `analyze_gap` 方法中追蹤詳細指標（第 235 行後）：

```python
# 提取 response content 後
llm_response = response['choices'][0]['message']['content']

# 追蹤 token 使用和時間
llm_time = time.time() - llm_start_time  # 需要在調用前記錄 llm_start_time
token_info = self.track_openai_usage(
    response,
    operation="gap_analysis",
    additional_properties={
        "language": language,
        "processing_time_ms": round(llm_time * 1000, 2),
        "prompt_length": len(system_prompt) + len(user_prompt),
        "response_length": len(llm_response)
    }
)

# 記錄詳細的 gap analysis 完成事件
monitoring_service.track_event(
    "GapAnalysisCompleted",
    {
        "language": language,
        "prompt_tokens": token_info["prompt_tokens"],
        "completion_tokens": token_info["completion_tokens"],
        "total_tokens": token_info["total_tokens"],
        "processing_time_ms": round(llm_time * 1000, 2),
        "estimated_cost_usd": self.estimate_token_cost(
            token_info["prompt_tokens"],
            token_info["completion_tokens"]
        ),
        "skill_queries_count": len(parsed_response.get('skill_queries', [])),
        "response_sections": {
            "strengths": len(parsed_response.get('strengths', [])),
            "gaps": len(parsed_response.get('gaps', [])),
            "improvements": len(parsed_response.get('improvements', []))
        }
    }
)
```

## 3. Index Calculation Service 增強監控

### 修改 `src/services/index_calculation.py`

在計算 embeddings 時添加時間追蹤：

```python
# 在 calculate_similarity 方法中
embedding_start = time.time()

# 創建 embeddings
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
        "embeddings_count": 2,
        "estimated_tokens": (len(resume_text) + len(jd_text)) // 4  # 粗略估算
    }
)
```

## 4. API 端點完整指標追蹤

### 修改 `src/api/v1/index_cal_and_gap_analysis.py`

在第 147 行的 track_event 調用中添加更多指標：

```python
# 收集各階段時間
index_time = index_end_time - start_time  # 需要記錄 index_end_time
gap_time = gap_end_time - index_end_time  # 需要記錄 gap_end_time
total_time = time.time() - start_time

monitoring_service.track_event(
    "IndexCalAndGapAnalysisCompleted",
    {
        # 現有指標
        "raw_similarity": index_result["raw_similarity_percentage"],
        "transformed_similarity": index_result["similarity_percentage"],
        "keyword_coverage": keyword_coverage["coverage_percentage"],
        "language": request.language,
        "skills_identified": len(gap_result.get("SkillSearchQueries", [])),
        
        # 新增時間指標
        "total_time_ms": round(total_time * 1000, 2),
        "index_calc_time_ms": round(index_time * 1000, 2),
        "gap_analysis_time_ms": round(gap_time * 1000, 2),
        
        # 新增資料大小指標
        "resume_length": len(request.resume),
        "jd_length": len(request.job_description),
        "keywords_count": len(keywords_list),
        
        # 新增結果指標
        "matched_keywords_count": len(keyword_coverage["covered_keywords"]),
        "missed_keywords_count": len(keyword_coverage["missed_keywords"])
    }
)
```

## 5. 建立 Azure Monitor Workbook

### 基本 Dashboard 配置

```json
{
  "version": "Notebook/1.0",
  "items": [
    {
      "type": "text",
      "content": {
        "json": "# Index Calculation & Gap Analysis Dashboard"
      }
    },
    {
      "type": "query",
      "name": "API Success Rate",
      "query": "customEvents | where timestamp > ago(1h) | where name in ('IndexCalculationCompleted', 'IndexCalAndGapAnalysisCompleted') | summarize Success = count(), Total = count() by bin(timestamp, 5m) | extend SuccessRate = 100.0 * Success / Total | render timechart"
    },
    {
      "type": "query", 
      "name": "Token Usage Trend",
      "query": "customEvents | where timestamp > ago(1h) | where name == 'OpenAITokenUsage' | summarize TotalTokens = sum(toint(customDimensions.total_tokens)) by bin(timestamp, 5m) | render timechart"
    }
  ]
}
```

## 6. 成本監控查詢

```kusto
// 每小時 API 使用成本
customEvents
| where timestamp > ago(24h)
| where name == "OpenAITokenUsage"
| extend 
    PromptTokens = toint(customDimensions.prompt_tokens),
    CompletionTokens = toint(customDimensions.completion_tokens),
    Operation = tostring(customDimensions.operation)
| summarize 
    TotalPromptTokens = sum(PromptTokens),
    TotalCompletionTokens = sum(CompletionTokens)
  by bin(timestamp, 1h), Operation
| extend 
    PromptCost = TotalPromptTokens * 0.01 / 1000,
    CompletionCost = TotalCompletionTokens * 0.03 / 1000,
    TotalCost = PromptCost + CompletionCost
| project timestamp, Operation, TotalCost, TotalPromptTokens, TotalCompletionTokens
| order by timestamp desc
```

## 7. 效能分析查詢

```kusto
// API 端點效能分解
customEvents
| where timestamp > ago(1h)
| where name == "IndexCalAndGapAnalysisCompleted"
| extend 
    TotalTime = todouble(customDimensions.total_time_ms),
    IndexTime = todouble(customDimensions.index_calc_time_ms),
    GapTime = todouble(customDimensions.gap_analysis_time_ms)
| summarize 
    avg(TotalTime), percentiles(TotalTime, 50, 90, 95),
    avg(IndexTime), percentiles(IndexTime, 50, 90, 95),
    avg(GapTime), percentiles(GapTime, 50, 90, 95),
    count()
| extend 
    IndexTimeRatio = avg_IndexTime / avg_TotalTime * 100,
    GapTimeRatio = avg_GapTime / avg_TotalTime * 100
```

## 8. 異常檢測告警

### 設置 Application Insights Alert Rules

1. **高錯誤率告警**
   - 條件: 錯誤事件數 > 5 in 5 minutes
   - 查詢: `customEvents | where name contains "Error" | count`

2. **Token 使用異常告警**
   - 條件: 平均 token 使用 > 3000 per request
   - 查詢: `customEvents | where name == "OpenAITokenUsage" | summarize avg(toint(customDimensions.total_tokens))`

3. **回應時間過長告警**
   - 條件: P95 處理時間 > 10 秒
   - 查詢: `customEvents | where name contains "Completed" | summarize percentile(todouble(customDimensions.processing_time_ms), 95)`

## 實作優先順序

1. **立即實作** (Phase 1)
   - ✅ OpenAI Client token 追蹤
   - ✅ API 端點基本監控
   - ✅ 錯誤事件追蹤

2. **短期實作** (Phase 2)
   - 📊 Token 成本計算
   - 📊 詳細時間分解
   - 📊 Azure Workbook 設置

3. **長期優化** (Phase 3)
   - 🔧 自動告警設置
   - 🔧 成本優化建議
   - 🔧 效能瓶頸分析