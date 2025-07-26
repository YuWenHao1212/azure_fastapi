# Azure FastAPI - API Specification v3

## Overview
Production-ready Keyword Extraction API with bilingual support (EN/zh-TW), built on FHS architecture.

## Base Information
- **Base URL**: `https://airesumeadvisor-fastapi.azurewebsites.net`
- **API Version**: v1
- **Authentication**: Function Key (query parameter: `code`)

## Endpoints

### 1. Extract JD Keywords
**POST** `/api/v1/extract-jd-keywords`

Extracts keywords from job descriptions with language detection and standardization.

#### Request
```json
{
  "job_description": "string (required, min 50 chars)",
  "max_keywords": "integer (optional, default: 20, range: 10-30)",
  "language": "string (optional, 'auto'|'en'|'zh-TW', default: 'auto')",
  "prompt_version": "string (optional, default: 'latest')"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "keywords": ["keyword1", "keyword2", ...],
    "confidence_score": 0.95,
    "extraction_method": "intersection_with_supplement",
    "detected_language": "en",
    "prompt_version": "1.4.0",
    "metadata": {
      "extraction_time_ms": 1500,
      "keyword_count": 20,
      "warnings": []
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-01-07T12:00:00Z"
}
```

#### Error Responses
- **422 Unprocessable Entity**: Validation error
- **400 Bad Request**: Invalid request format
- **500 Internal Server Error**: Server error

### 2. Health Check
**GET** `/api/v1/health`

Returns service health status.

#### Response
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "openai": "connected",
      "cache": "enabled"
    }
  },
  "timestamp": "2025-01-07T12:00:00Z"
}
```

### 3. Version Information
**GET** `/api/v1/version`

Returns service version and capabilities.

#### Response
```json
{
  "success": true,
  "data": {
    "api_version": "v1",
    "service_version": "2.0.0",
    "capabilities": {
      "languages": ["en", "zh-TW"],
      "max_keywords": 30,
      "cache_enabled": true,
      "prompt_versions": ["1.0.0", "1.2.0", "1.4.0"]
    }
  }
}
```

### 4. Prompt Version Management
**GET** `/api/v1/prompts/version?task={task}&language={language}`

Get prompt version for specific task and language.

#### Parameters
- `task`: Task name (e.g., "keyword_extraction")
- `language`: Language code ("en" or "zh-TW")

### 5. List Available Tasks
**GET** `/api/v1/prompts/tasks`

Lists all tasks with prompt configurations.

## Features

### Language Detection
- Automatic detection of English and Traditional Chinese
- Rejection of unsupported languages (Simplified Chinese, Japanese, Korean, Spanish)
- Configurable thresholds for language determination

### Keyword Standardization
- Industry-standard terminology mapping
- Skill normalization
- Tool and technology standardization
- Position title standardization

### Performance Optimization
- Response caching (60 minutes TTL)
- Parallel processing for multiple extractions
- Average response time: < 2 seconds (cache miss), < 50ms (cache hit)

### Error Handling
- Comprehensive error classification
- Detailed validation messages
- Request context preservation for debugging
- Bubble.io compatible error format

## Monitoring Integration
- Azure Application Insights tracking
- Custom events for business metrics
- Performance metrics per endpoint
- Error rate monitoring
- Language distribution tracking

## Rate Limits
- 60 requests per minute per IP
- Temporary blocking for violations (15 minutes)

## Example Usage

### cURL
```bash
curl -X POST "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords?code=[YOUR_FUNCTION_KEY]" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Python developer with FastAPI experience...",
    "language": "auto",
    "max_keywords": 20
  }'
```

### Python
```python
import requests

url = "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords"
params = {"code": "[YOUR_FUNCTION_KEY]"}
data = {
    "job_description": "職位描述...",
    "language": "auto"
}

response = requests.post(url, params=params, json=data)
result = response.json()
```

## Bubble.io Integration
1. Use API Connector plugin
2. Configure as POST request
3. Add Function Key as query parameter
4. Set Content-Type: application/json
5. Handle unified response format

---

**Version**: 3.0  
**Last Updated**: 2025-01-07  
**Status**: Production Ready