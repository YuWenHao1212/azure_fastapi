#!/bin/bash

echo "Checking Application Insights for recent gap analysis requests..."
echo "=================================================="
echo ""

# Query recent customEvents for gap analysis
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --resource-group airesumeadvisorfastapi \
  --analytics-query "
customEvents 
| where timestamp > ago(30m)
| where name in ('GapAnalysisCompleted', 'GapAnalysisEmptyFields', 'GapAnalysisRetryAttempt', 'GapAnalysisRetrySuccess', 'GapAnalysisRetryExhausted')
| project timestamp, name, customDimensions
| order by timestamp desc
| take 20
" --output table

echo ""
echo "Checking request failures in last 30 minutes..."
echo "=================================================="

# Check for 422 errors
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --resource-group airesumeadvisorfastapi \
  --analytics-query "
requests
| where timestamp > ago(30m)
| where url contains 'index-cal-and-gap-analysis'
| where resultCode != '200'
| summarize count() by resultCode
" --output table

echo ""
echo "Checking success rate in last 30 minutes..."
echo "=================================================="

# Check success rate
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --resource-group airesumeadvisorfastapi \
  --analytics-query "
requests
| where timestamp > ago(30m)
| where url contains 'index-cal-and-gap-analysis'
| summarize 
    Total = count(),
    Success = countif(resultCode == '200'),
    Failed = countif(resultCode != '200')
| extend SuccessRate = round(100.0 * Success / Total, 2)
" --output table