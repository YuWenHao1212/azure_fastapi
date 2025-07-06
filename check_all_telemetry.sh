#!/bin/bash

# Check all telemetry tables in Application Insights
echo "🔍 Checking all Application Insights telemetry tables..."
echo "================================================"

# Set your Application Insights app ID and API key
APP_ID="${APP_INSIGHTS_APP_ID:-YOUR_APP_ID}"
API_KEY="${APP_INSIGHTS_API_KEY:-YOUR_API_KEY}"

if [ "$APP_ID" = "YOUR_APP_ID" ]; then
    echo "ℹ️  Note: This script uses the Application Insights Data Access API"
    echo "   You can also run these queries directly in the Azure Portal"
    echo ""
fi

# Function to display KQL query
show_query() {
    local table=$1
    local title=$2
    echo ""
    echo "📊 $title"
    echo "Table: $table"
    echo "KQL Query:"
    echo "--------"
    cat << EOF
$table
| where timestamp > ago(1h)
| take 10
| project timestamp, name, customDimensions, message, severityLevel
EOF
    echo "--------"
}

# 1. Check traces table (where logs are stored)
show_query "traces" "Traces Table (Logs)"

# 2. Check customEvents table
show_query "customEvents" "Custom Events Table"

# 3. Check customMetrics table  
show_query "customMetrics" "Custom Metrics Table"

# 4. Check requests table
show_query "requests" "Requests Table"

# 5. Check dependencies table
show_query "dependencies" "Dependencies Table"

echo ""
echo "🎯 Specific queries to find monitoring data:"
echo ""

echo "1️⃣ Find RequestTracked events in traces:"
echo "--------"
cat << 'EOF'
traces
| where timestamp > ago(1h)
| where message contains "RequestTracked" or message contains "CustomEvent"
| extend 
    eventName = extract(@"(RequestTracked|RequestStarted|CustomEvent\.\w+)", 1, message),
    dimensions = parse_json(tostring(customDimensions))
| project timestamp, eventName, dimensions, message
| order by timestamp desc
| take 20
EOF
echo "--------"

echo ""
echo "2️⃣ Find all monitoring events:"
echo "--------"
cat << 'EOF'
traces
| where timestamp > ago(1h)
| where customDimensions has "endpoint" or customDimensions has "duration_ms"
| extend 
    endpoint = tostring(customDimensions.endpoint),
    method = tostring(customDimensions.method),
    duration_ms = todouble(customDimensions.duration_ms),
    status_code = toint(customDimensions.status_code)
| project timestamp, endpoint, method, duration_ms, status_code, message
| order by timestamp desc
| take 20
EOF
echo "--------"

echo ""
echo "3️⃣ Find metrics in traces:"
echo "--------"
cat << 'EOF'
traces
| where timestamp > ago(1h)
| where message contains "CustomMetric"
| extend 
    metricName = extract(@"CustomMetric\.(\w+)", 1, message),
    metricValue = todouble(customDimensions.metric_value)
| project timestamp, metricName, metricValue, customDimensions
| order by timestamp desc
| take 20
EOF
echo "--------"

echo ""
echo "📝 Instructions:"
echo "1. Copy these queries to Application Insights Logs in Azure Portal"
echo "2. Run each query to see where your monitoring data is stored"
echo "3. The data is likely in the 'traces' table as shown in the Function logs"
echo ""
echo "🔗 Azure Portal: https://portal.azure.com"
echo "   Navigate to: Application Insights → Logs"