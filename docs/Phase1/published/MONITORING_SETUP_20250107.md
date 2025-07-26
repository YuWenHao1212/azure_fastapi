# Monitoring Setup Guide for Azure Application Insights

## Overview
This guide covers setting up Application Insights monitoring, dashboards, and alerts for the AI Resume Advisor API.

## Prerequisites
- Azure Function App deployed
- Application Insights resource created
- Azure CLI installed and authenticated

## Application Insights Configuration

### Primary Resource Information
- **Name**: airesumeadvisorfastapi
- **Instrumentation Key**: e62aa619-199c-4f43-826e-bdec26344a26
- **Application ID**: c8a25079-7aa0-4cd2-828c-50f554c7d494
- **Resource Group**: airesumeadvisorfastapi

### Environment Variables
The following environment variables are automatically configured in the Function App:

```bash
APPINSIGHTS_INSTRUMENTATIONKEY=e62aa619-199c-4f43-826e-bdec26344a26
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=e62aa619-199c-4f43-826e-bdec26344a26;IngestionEndpoint=https://eastasia-0.in.applicationinsights.azure.com/;LiveEndpoint=https://eastasia.livediagnostics.monitor.azure.com/;ApplicationId=c8a25079-7aa0-4cd2-828c-50f554c7d494
```

## Monitoring Components

### 1. Core Monitoring Service
- **Location**: `src/core/monitoring_service.py`
- **Features**:
  - Request tracking with duration and status
  - Custom business metrics (keyword extraction)
  - Error tracking with detailed context
  - Dependency tracking (OpenAI API calls)

### 2. Monitoring Middleware
- **Location**: `src/middleware/monitoring_middleware.py`
- **Features**:
  - Automatic request/response tracking
  - Correlation ID generation and propagation
  - Security integration
  - Processing time measurement

### 3. Security Monitor
- **Location**: `src/core/monitoring/security_monitor.py`
- **Features**:
  - XSS and SQL injection detection
  - Rate limiting (60 requests/minute per IP)
  - IP blocking (temporary and permanent)
  - Threat tracking and reporting

### 4. Metrics Collection
- **Endpoint Metrics**: `src/core/metrics/endpoint_metrics.py`
  - Per-endpoint request counts
  - Error rates and types
  - Response time statistics
  
- **Cache Metrics**: `src/core/metrics/cache_metrics.py`
  - Hit/miss rates
  - Cost savings calculation
  - Hourly reporting

## Dashboard Setup

### Creating the Dashboard in Azure Portal

1. Navigate to your Application Insights resource
2. Click on "Dashboards" → "Create new dashboard"
3. Import the queries from `azure/monitoring/dashboard-config.json`

### Key Dashboard Panels

1. **Request Overview**
   - Request count, average duration, P95 latency, failure rate
   - 5-minute time bins for real-time monitoring

2. **Keyword Extraction Metrics**
   - Success rates by endpoint
   - Average processing times
   - Request volume trends

3. **Cache Performance**
   - Hit rate trends
   - Cost savings over time
   - Request volume impact

4. **Security Threats**
   - Distribution of threat types
   - Blocked requests count
   - Suspicious activity patterns

5. **Error Analysis**
   - Top errors by type
   - Error trends over time
   - Affected endpoints

6. **External Dependencies**
   - OpenAI API performance
   - Average latency and failure rates

## Alert Configuration

### Setting Up Alerts via Azure CLI

```bash
# Create action group
az monitor action-group create \
  --name APIMonitoringActionGroup \
  --short-name APIMonitor \
  --resource-group airesumeadvisorfastapi \
  --action email DevTeam dev-team@airesumeadvisor.com

# Create high error rate alert
az monitor scheduled-query create \
  --name "HighErrorRate" \
  --resource-group airesumeadvisorfastapi \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/airesumeadvisorfastapi/providers/Microsoft.Insights/components/airesumeadvisorfastapi" \
  --condition "count > 0" \
  --condition-query "requests | where timestamp > ago(5m) | summarize FailureRate = countif(success == false) * 100.0 / count() | where FailureRate > 5" \
  --action-groups APIMonitoringActionGroup \
  --severity 2 \
  --window-size 5m \
  --evaluation-frequency 5m
```

### Alert Types

1. **High Error Rate** (Severity 2)
   - Triggers when error rate > 5% in 5 minutes
   - Checks every 5 minutes

2. **High Response Time** (Severity 3)
   - Triggers when P95 latency > 5 seconds
   - Monitors performance degradation

3. **Security Threat Detected** (Severity 1)
   - Immediate alert on blocked requests
   - High-risk security events

4. **Cache Performance Degraded** (Severity 3)
   - Triggers when hit rate < 50%
   - Hourly evaluation

5. **API Quota Exceeded** (Severity 2)
   - Monitors rate limit violations
   - Helps prevent service disruption

## Viewing Monitoring Data

### Via Azure Portal
1. Navigate to Application Insights resource
2. Use "Logs" for custom queries
3. Check "Metrics" for standard telemetry
4. View "Application Map" for dependencies

### Via Azure CLI
```bash
# View recent requests
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --resource-group airesumeadvisorfastapi \
  --analytics-query "requests | where timestamp > ago(1h) | take 10"

# Check error rate
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --resource-group airesumeadvisorfastapi \
  --analytics-query "requests | where timestamp > ago(1h) | summarize ErrorRate = countif(success == false) * 100.0 / count()"
```

## Custom Metrics Reference

### Business Metrics
- `keyword_extraction_request`: Tracks each keyword extraction with status and duration
- `cache_hourly_report`: Hourly cache performance summary
- `request_blocked`: Security blocks with threat details

### Technical Metrics
- Request duration (P50, P95, P99)
- Error rates by endpoint
- Dependency call performance
- Cache hit/miss ratios

## Troubleshooting

### No Data in Application Insights
1. Check instrumentation key in Function App settings
2. Verify `MONITORING_ENABLED=true`
3. Check Application Insights resource location matches Function App region

### Missing Custom Events
1. Ensure OpenCensus exporters are properly initialized
2. Check for exceptions in monitoring service initialization
3. Verify network connectivity to Application Insights endpoints

### Alert Not Firing
1. Verify alert query returns results in Logs
2. Check action group email configuration
3. Review alert evaluation frequency vs window size

## Best Practices

1. **Sampling**: Currently set to 100% (ProbabilitySampler(1.0)). Consider reducing for high-volume production.

2. **Correlation IDs**: Always propagate X-Correlation-ID header for request tracing.

3. **Custom Properties**: Add relevant business context to tracked events for better analysis.

4. **Cost Management**: Monitor data ingestion volume and adjust sampling/retention as needed.

5. **Security**: Never log sensitive data (passwords, API keys, PII) in telemetry.

## Maintenance Tasks

### Weekly
- Review alert noise and adjust thresholds
- Check dashboard performance and query efficiency
- Analyze security threat patterns

### Monthly
- Review data retention settings
- Analyze cost and optimize telemetry
- Update alert recipients and channels
- Archive old failure analysis reports

## Contact
For monitoring issues or questions:
- Technical Lead: wenhao@airesumeadvisor.com
- DevOps Team: devops@airesumeadvisor.com