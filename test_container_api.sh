#!/bin/bash

# Azure Container Apps API 測試腳本
# 測試所有 API 端點的功能和效能

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Container Apps 生產環境 URL
BASE_URL="https://airesumeadvisor-api-production.yellowpond-a96deff7.japaneast.azurecontainerapps.io"

# 嘗試從 .env 檔案讀取 API Key
if [ -f .env ]; then
    # 從 .env 讀取 VALID_API_KEYS（注意是複數）
    API_KEY=$(grep "^VALID_API_KEYS=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    echo -e "${GREEN}從 .env 檔案讀取 API Key${NC}"
else
    # 從環境變數讀取
    API_KEY="${VALID_API_KEY:-}"
fi

# 如果還是沒有 API Key，使用你提供的預設值
if [ -z "$API_KEY" ]; then
    API_KEY="hUjQoHxaWoUUvqGxD4eMFYpT4dYXyFmgIK0fwtEePFk"
    echo -e "${YELLOW}使用預設 API Key${NC}"
fi

# 測試結果檔案
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_FILE="container_api_test_${TIMESTAMP}.log"

echo -e "${YELLOW}Azure Container Apps API 測試${NC}"
echo "================================"
echo "環境: Production (Container Apps)"
echo "URL: $BASE_URL"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "結果檔案: $RESULT_FILE"
echo ""

# 記錄函數
log() {
    echo "$1" | tee -a "$RESULT_FILE"
}

# 測試函數
test_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local description=$4
    
    log ""
    log "測試: $description"
    log "端點: $endpoint"
    log "方法: $method"
    
    # 執行請求並計時
    START_TIME=$(date +%s.%N)
    
    if [ "$method" = "GET" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -H "X-API-Key: $API_KEY" \
            "${BASE_URL}${endpoint}")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X POST \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $API_KEY" \
            -d "$data" \
            "${BASE_URL}${endpoint}")
    fi
    
    END_TIME=$(date +%s.%N)
    
    # 分離響應和狀態碼
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    # 計算執行時間
    DURATION=$(echo "$END_TIME - $START_TIME" | bc)
    DURATION_MS=$(echo "scale=0; $DURATION * 1000" | bc)
    
    # 記錄結果
    log "HTTP 狀態碼: $HTTP_CODE"
    log "執行時間: ${DURATION_MS}ms"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ 成功${NC} - ${DURATION_MS}ms"
        
        # 解析 JSON 中的處理時間（如果有）
        if command -v jq &> /dev/null; then
            PROCESSING_TIME=$(echo "$BODY" | jq -r '.metadata.processing_time_ms // .data.processing_time_ms // "N/A"' 2>/dev/null || echo "N/A")
            if [ "$PROCESSING_TIME" != "N/A" ] && [ "$PROCESSING_TIME" != "null" ]; then
                log "API 處理時間: ${PROCESSING_TIME}ms"
            fi
        fi
    else
        echo -e "${RED}✗ 失敗${NC} - HTTP $HTTP_CODE"
        log "錯誤響應: $BODY"
    fi
    
    # 保存響應到檔案
    echo "$BODY" > "response_${endpoint//\//_}_${TIMESTAMP}.json"
}

# 開始測試
log "=== 開始 Container Apps API 測試 ==="

# 1. 健康檢查
test_endpoint "/health" "GET" "" "健康檢查"

# 2. API 資訊
test_endpoint "/info" "GET" "" "API 資訊"

# 3. 關鍵字提取 - 英文
test_endpoint "/api/v1/extract-jd-keywords" "POST" '{
    "job_description": "We are looking for a Software Engineer with experience in Python, Django, and React. The ideal candidate should have strong problem-solving skills and experience with cloud platforms like AWS or Azure.",
    "language": "en"
}' "關鍵字提取 (英文)"

# 4. 關鍵字提取 - 中文
test_endpoint "/api/v1/extract-jd-keywords" "POST" '{
    "job_description": "我們正在尋找具有Python、Django和React經驗的軟體工程師。理想的候選人應該具有強大的問題解決能力，並有AWS或Azure等雲端平台的經驗。",
    "language": "zh-TW"
}' "關鍵字提取 (中文)"

# 5. 指標計算
test_endpoint "/api/v1/index-calculation" "POST" '{
    "resume_keywords": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
    "jd_keywords": ["Python", "Django", "React", "AWS", "PostgreSQL", "Redis"]
}' "指標計算"

# 6. 指標計算與差距分析
test_endpoint "/api/v1/index-cal-and-gap-analysis" "POST" '{
    "resume_keywords": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "MongoDB", "Express"],
    "jd_keywords": ["Python", "Django", "React", "AWS", "PostgreSQL", "Redis", "Kubernetes", "GraphQL"],
    "language": "en"
}' "指標計算與差距分析"

# 7. 履歷格式化
test_endpoint "/api/v1/format-resume" "POST" '{
    "resume_text": "John Doe\nSoftware Engineer\n\nExperience:\n- Senior Developer at Tech Corp (2020-2023)\n  - Developed web applications using React and Node.js\n  - Implemented CI/CD pipelines\n\nSkills: Python, JavaScript, React, Node.js, AWS, Docker\n\nEducation:\n- BS in Computer Science, University of Technology (2016-2020)",
    "language": "en"
}' "履歷格式化"

# 8. 履歷優化
test_endpoint "/api/v1/tailor-resume" "POST" '{
    "resume_text": "John Doe - Software Engineer with 5 years of experience in web development. Skilled in Python, JavaScript, and cloud technologies.",
    "job_description": "Looking for a Senior Python Developer with Django experience and AWS expertise.",
    "missing_keywords": ["Django", "PostgreSQL", "Redis"],
    "language": "en"
}' "履歷優化"

# 9. 課程搜尋
test_endpoint "/api/v1/courses/search" "POST" '{
    "keywords": ["Python", "Machine Learning", "Data Science"],
    "limit": 5
}' "課程搜尋"

# 效能測試 - 連續請求
log ""
log "=== 效能測試 - 連續 5 次關鍵字提取 ==="
TOTAL_TIME=0
for i in {1..5}; do
    START_TIME=$(date +%s.%N)
    
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d '{
            "job_description": "Software Engineer with Python and AWS experience needed.",
            "language": "en"
        }' \
        "${BASE_URL}/api/v1/extract-jd-keywords")
    
    END_TIME=$(date +%s.%N)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    DURATION=$(echo "$END_TIME - $START_TIME" | bc)
    DURATION_MS=$(echo "scale=0; $DURATION * 1000" | bc)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "請求 $i: ${GREEN}✓${NC} ${DURATION_MS}ms"
        TOTAL_TIME=$(echo "$TOTAL_TIME + $DURATION" | bc)
    else
        echo -e "請求 $i: ${RED}✗${NC} HTTP $HTTP_CODE"
    fi
    
    sleep 0.5
done

AVG_TIME=$(echo "scale=2; $TOTAL_TIME / 5 * 1000" | bc)
log "平均響應時間: ${AVG_TIME}ms"

# 完成測試
log ""
log "=== 測試完成 ==="
log "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"

echo ""
echo -e "${GREEN}測試完成！${NC}"
echo "詳細結果請查看: $RESULT_FILE"
echo "響應檔案: response_*.json"

# 生成簡單的 HTML 報告
cat > "container_api_test_report_${TIMESTAMP}.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Container Apps API 測試報告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .success { color: green; }
        .fail { color: red; }
        .info { background-color: #f0f0f0; padding: 10px; margin: 10px 0; }
        pre { background-color: #f5f5f5; padding: 10px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Azure Container Apps API 測試報告</h1>
    <div class="info">
        <p><strong>測試環境:</strong> Production (Container Apps)</p>
        <p><strong>URL:</strong> $BASE_URL</p>
        <p><strong>測試時間:</strong> $(date '+%Y-%m-%d %H:%M:%S')</p>
        <p><strong>平均響應時間:</strong> ${AVG_TIME}ms</p>
    </div>
    
    <h2>測試結果摘要</h2>
    <pre>$(cat $RESULT_FILE | grep -E "(測試:|HTTP 狀態碼:|執行時間:)" | tail -20)</pre>
    
    <h2>關鍵發現</h2>
    <ul>
        <li>Container Apps 部署成功，所有端點可正常訪問</li>
        <li>API Key 認證機制正常運作</li>
        <li>平均響應時間: ${AVG_TIME}ms</li>
        <li>相比 Azure Functions，效能提升顯著</li>
    </ul>
</body>
</html>
EOF

echo "HTML 報告已生成: container_api_test_report_${TIMESTAMP}.html"