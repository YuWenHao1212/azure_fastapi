#!/bin/bash

# Quick Pre-commit Test Suite - For fast validation
# This is a lightweight version that runs within 2 minutes
# For full tests, run ./run_precommit_tests.sh directly

set -e  # Exit on error

echo "🚀 Running Quick Pre-commit Test Suite"
echo "====================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Note: This is a quick version. For full tests including coverage, run ./run_precommit_tests.sh"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test category
run_test_category() {
    local category=$1
    local command=$2
    
    echo -e "${YELLOW}📋 Running $category...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$command"; then
        echo -e "${GREEN}✅ $category passed${NC}\n"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ $category failed${NC}\n"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# 1. Code Style Check (fastest)
echo "═══════════════════════════════════════"
echo "🎨 CODE QUALITY CHECK"
echo "═══════════════════════════════════════"

if command -v ruff &> /dev/null; then
    run_test_category "Code Style Check (ruff)" \
        "ruff check src/ tests/ --exclude=legacy,archive,temp"
else
    echo -e "${YELLOW}⚠️  ruff not installed, skipping code style check${NC}"
fi

# 2. Core Unit Tests Only (essential tests)
echo "═══════════════════════════════════════"
echo "🧪 ESSENTIAL UNIT TESTS"
echo "═══════════════════════════════════════"

# Run only the most critical unit tests
run_test_category "Core Models Test" \
    "pytest tests/unit/test_core_models.py::TestKeywordExtractionRequest -v -q"

run_test_category "API Handlers Test (Basic)" \
    "pytest tests/unit/test_api_handlers.py -k 'test_health' -v -q"

# 3. Basic Integration Test
echo "═══════════════════════════════════════"
echo "🔗 BASIC INTEGRATION TEST"
echo "═══════════════════════════════════════"

# Check if API is running
if curl -s http://localhost:8000/api/v1/health -H "X-Test-Bypass-Security: true" > /dev/null 2>&1; then
    run_test_category "Health Check" \
        "curl -s http://localhost:8000/api/v1/health -H 'X-Test-Bypass-Security: true' | grep -q 'healthy'"
else
    echo -e "${YELLOW}⚠️  API not running, skipping integration tests${NC}"
fi

# 4. Final Summary
echo ""
echo "═══════════════════════════════════════"
echo "📊 QUICK TEST SUMMARY"
echo "═══════════════════════════════════════"
echo "Total tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ Quick tests passed!${NC}"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Run full tests: ./run_precommit_tests.sh"
    echo "   2. Or commit if you're confident: git commit -m 'your message'"
    exit 0
else
    echo -e "${RED}❌ Some quick tests failed. Fix before committing.${NC}"
    exit 1
fi