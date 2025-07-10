#!/bin/bash

# Azure Function App reformat API 測試腳本
# 測試已部署到 Azure 的 reformat endpoint

# API 基礎設定
BASE_URL="https://airesumeadvisor-fastapi.azurewebsites.net"
ENDPOINT="/api/v1/format-resume"
HOST_KEY="${AZURE_FUNCTION_HOST_KEY}"  # 從環境變數讀取

# 檢查 HOST_KEY
if [ -z "$HOST_KEY" ]; then
    echo "❌ 錯誤：請設置 AZURE_FUNCTION_HOST_KEY 環境變數"
    echo "使用方式："
    echo "  export AZURE_FUNCTION_HOST_KEY='your-host-key'"
    echo "  ./test_reformat_api.sh"
    exit 1
fi

# 完整 URL
FULL_URL="${BASE_URL}${ENDPOINT}?code=${HOST_KEY}"

# 顏色設定
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}開始測試 Reformat API${NC}"
echo "URL: ${BASE_URL}${ENDPOINT}"
echo "時間: $(date)"
echo "================================================"

# 測試 1：使用正確的 OCR 格式測試
echo -e "\n${YELLOW}測試 1：標準 OCR 格式履歷測試${NC}"
echo "測試內容：使用【Type】:Content 格式的履歷"

PAYLOAD1='{
  "ocr_text": "【Title】:John Doe\n【Title】:Senior Software Engineer\n【NarrativeText】:Software Engineer with 5 years of experience building scalable web applications\n\n【Title】:Contact Information\n【NarrativeText】:Email: john.doe@gmail.com\n【NarrativeText】:Phone: (408) 555-0123\n【NarrativeText】:Location: San Francisco, CA\n\n【Title】:Education\n【Title】:Stanford University\n【NarrativeText】:MS Computer Science • Sep 2016 - Jun 2018\n【ListItem】:GPA: 3.9/4.0\n【ListItem】:Specialization in Machine Learning and Distributed Systems\n\n【Title】:UC Berkeley\n【NarrativeText】:BS Computer Science • Sep 2012 - May 2016\n【ListItem】:Magna Cum Laude\n【ListItem】:Dean'\''s List all semesters\n\n【Title】:Work Experience\n【Title】:Google Inc.\n【NarrativeText】:Senior Software Engineer • Mountain View, CA • Jan 2020 - Present\n【ListItem】:Led development of distributed systems handling 10M+ requests/day\n【ListItem】:Improved system performance by 40% through optimization\n【ListItem】:Mentored 3 junior engineers and conducted code reviews\n\n【Title】:Facebook Inc.\n【NarrativeText】:Software Engineer • Menlo Park, CA • Jul 2018 - Dec 2019\n【ListItem】:Developed React components for News Feed feature\n【ListItem】:Implemented CI/CD pipelines reducing deployment time by 50%\n【ListItem】:Collaborated with cross-functional teams on product launches\n\n【Title】:Technical Skills\n【ListItem】:Programming Languages: Python, Java, JavaScript, TypeScript, Go\n【ListItem】:Frameworks: React, Node.js, Django, FastAPI, Spring Boot\n【ListItem】:Databases: PostgreSQL, MySQL, MongoDB, Redis\n【ListItem】:Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitLab CI"
}'

echo "Request payload preview:"
echo "$PAYLOAD1" | jq -r '.ocr_text' | head -10
echo "... (truncated)"

START_TIME=$(date +%s)
RESPONSE1=$(curl -s -w "\n%{http_code}" -X POST "$FULL_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD1")
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

HTTP_CODE=$(echo "$RESPONSE1" | tail -n1)
BODY=$(echo "$RESPONSE1" | sed '$d')

echo -e "\nHTTP Status Code: ${HTTP_CODE}"
echo "Response time: ${DURATION}s"

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 測試 1 成功${NC}"
    echo "Response structure:"
    echo "$BODY" | jq -r 'keys[]' 2>/dev/null || echo "無法解析 JSON"
    
    # 檢查關鍵欄位
    HAS_SUMMARY=$(echo "$BODY" | jq -r '.data.processed_resume.Summary // empty' 2>/dev/null)
    HAS_EDUCATION=$(echo "$BODY" | jq -r '.data.processed_resume.Education // empty' 2>/dev/null)
    HAS_EXPERIENCE=$(echo "$BODY" | jq -r '.data.processed_resume.Experience // empty' 2>/dev/null)
    HAS_SKILLS=$(echo "$BODY" | jq -r '.data.processed_resume.Skills // empty' 2>/dev/null)
    
    echo -e "\n欄位檢查："
    [ -n "$HAS_SUMMARY" ] && echo -e "  ${GREEN}✓${NC} Summary" || echo -e "  ${RED}✗${NC} Summary"
    [ -n "$HAS_EDUCATION" ] && echo -e "  ${GREEN}✓${NC} Education" || echo -e "  ${RED}✗${NC} Education"
    [ -n "$HAS_EXPERIENCE" ] && echo -e "  ${GREEN}✓${NC} Experience" || echo -e "  ${RED}✗${NC} Experience"
    [ -n "$HAS_SKILLS" ] && echo -e "  ${GREEN}✓${NC} Skills" || echo -e "  ${RED}✗${NC} Skills"
    
    # 顯示部分內容
    echo -e "\nSummary 預覽："
    echo "$BODY" | jq -r '.data.processed_resume.Summary' 2>/dev/null | head -3 || echo "無法取得 Summary"
else
    echo -e "${RED}❌ 測試 1 失敗${NC}"
    echo "Error response:"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
fi

# 等待 2 秒避免 rate limiting
sleep 2

# 測試 2：招聘經理視角測試（使用較短的履歷）
echo -e "\n${YELLOW}測試 2：招聘經理視角測試${NC}"
echo "測試內容：較短的履歷，招聘經理視角"

PAYLOAD2='{
  "ocr_text": "【Title】:Jane Smith\n【Title】:Product Manager\n【NarrativeText】:Experienced PM with 8 years driving product strategy\n\n【Title】:Contact\n【NarrativeText】:jane.smith@email.com • San Francisco, CA\n\n【Title】:Experience\n【Title】:Uber Technologies\n【NarrativeText】:Senior Product Manager • 2020 - Present\n【ListItem】:Led product roadmap for rider experience features\n【ListItem】:Increased user engagement by 25%\n\n【Title】:Education\n【NarrativeText】:Harvard Business School • MBA • 2015\n【NarrativeText】:MIT • BS Computer Science • 2012\n\n【Title】:Skills\n【ListItem】:Product Strategy, Data Analysis, User Research\n【ListItem】:SQL, Python, Tableau, Figma"
}'

echo "Request payload preview:"
echo "$PAYLOAD2" | jq -r '.ocr_text' | head -10
echo "... (truncated)"

START_TIME=$(date +%s)
RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$FULL_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD2")
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

HTTP_CODE=$(echo "$RESPONSE2" | tail -n1)
BODY=$(echo "$RESPONSE2" | sed '$d')

echo -e "\nHTTP Status Code: ${HTTP_CODE}"
echo "Response time: ${DURATION}s"

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 測試 2 成功${NC}"
    
    # 檢查是否包含招聘經理專屬欄位
    HAS_CERTIFICATIONS=$(echo "$BODY" | jq -r '.data.processed_resume.Certifications // empty' 2>/dev/null)
    HAS_INTERESTS=$(echo "$BODY" | jq -r '.data.processed_resume.Interests // empty' 2>/dev/null)
    HAS_LANGUAGES=$(echo "$BODY" | jq -r '.data.processed_resume.Languages // empty' 2>/dev/null)
    
    echo -e "\n招聘經理視角欄位檢查："
    [ -n "$HAS_CERTIFICATIONS" ] && echo -e "  ${GREEN}✓${NC} Certifications" || echo -e "  ${YELLOW}○${NC} Certifications (可選)"
    [ -n "$HAS_INTERESTS" ] && echo -e "  ${GREEN}✓${NC} Interests" || echo -e "  ${YELLOW}○${NC} Interests (可選)"
    [ -n "$HAS_LANGUAGES" ] && echo -e "  ${GREEN}✓${NC} Languages" || echo -e "  ${YELLOW}○${NC} Languages (可選)"
    
    # 檢查處理統計
    LINES_PROCESSED=$(echo "$BODY" | jq -r '.data.processing_stats.lines_processed // 0' 2>/dev/null)
    SECTIONS_FOUND=$(echo "$BODY" | jq -r '.data.processing_stats.sections_found // 0' 2>/dev/null)
    
    echo -e "\n處理統計："
    echo "  處理行數: $LINES_PROCESSED"
    echo "  找到區段: $SECTIONS_FOUND"
else
    echo -e "${RED}❌ 測試 2 失敗${NC}"
    echo "Error response:"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
fi

# 測試總結
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}測試完成${NC}"
echo "完成時間: $(date)"

# 保存測試結果
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="test_reformat_results_${TIMESTAMP}.json"

{
    echo "{"
    echo "  \"test_time\": \"$(date)\","
    echo "  \"api_url\": \"${BASE_URL}${ENDPOINT}\","
    echo "  \"test_1\": $RESPONSE1,"
    echo "  \"test_2\": $RESPONSE2"
    echo "}"
} > "$LOG_FILE"

echo -e "\n測試結果已保存到: ${LOG_FILE}"

# 提供使用建議
echo -e "\n${YELLOW}使用提示：${NC}"
echo "1. 確保已設置 AZURE_FUNCTION_HOST_KEY 環境變數"
echo "2. OCR 格式必須使用【Type】:Content 格式"
echo "3. 支援的 Type 包括：Title, NarrativeText, ListItem"
echo "4. is_hiring_manager=true 會產生更詳細的履歷格式"