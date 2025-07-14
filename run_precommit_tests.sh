#!/bin/bash

# Pre-commit Test Suite
# Run this script before committing to ensure code quality
# Usage: ./run_precommit_tests.sh [options]
# Options:
#   --no-api: Skip API server startup and online tests
#   --full-perf: Run all performance tests including flaky ones (default: skip flaky tests)
#   --parallel: Run tests in parallel using multiple CPU cores
#   --timeout <seconds>: Set custom timeout (default: 300 seconds)
#   --no-coverage: Skip coverage report generation to save time

set -e  # Exit on error

echo "🚀 Running Pre-commit Test Suite"
echo "================================"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
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
SKIPPED_TESTS=0

# Parse command line arguments
SKIP_API_STARTUP=false
RUN_FULL_PERF_TESTS=false
PARALLEL_EXECUTION=false
SKIP_COVERAGE=false
TIMEOUT_SECONDS=300  # 5 minutes default
for arg in "$@"; do
    case $arg in
        --no-api)
            SKIP_API_STARTUP=true
            shift
            ;;
        --full-perf)
            RUN_FULL_PERF_TESTS=true
            shift
            ;;
        --parallel)
            PARALLEL_EXECUTION=true
            shift
            ;;
        --no-coverage)
            SKIP_COVERAGE=true
            shift
            ;;
        --timeout)
            TIMEOUT_SECONDS=$2
            shift 2
            ;;
    esac
done

# Function to run a test category
run_test_category() {
    local category=$1
    local command=$2
    
    echo -e "${YELLOW}📋 Running $category...${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Add parallel execution flag if enabled
    if [ "$PARALLEL_EXECUTION" = true ] && [[ $command == pytest* ]]; then
        # Detect number of CPUs
        if [[ "$OSTYPE" == "darwin"* ]]; then
            NUM_CPUS=$(sysctl -n hw.ncpu)
        else
            NUM_CPUS=$(nproc)
        fi
        # Use half the CPUs to avoid overload
        WORKERS=$((NUM_CPUS / 2))
        [ $WORKERS -lt 1 ] && WORKERS=1
        command="${command/pytest/pytest -n $WORKERS}"
        echo -e "   🚀 Running with $WORKERS parallel workers"
    fi
    
    if eval "$command"; then
        echo -e "${GREEN}✅ $category passed${NC}\n"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ $category failed${NC}\n"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        # Don't exit on failure, continue with other tests
    fi
}

# Function to check if API server is running
check_api_server() {
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start API server
start_api_server() {
    echo -e "${YELLOW}🌐 Starting local API server...${NC}"
    
    # Check if port 8000 is already in use
    if lsof -i :8000 > /dev/null 2>&1; then
        echo -e "${YELLOW}   Port 8000 is already in use. Checking if it's our API...${NC}"
        if check_api_server; then
            echo -e "${GREEN}   ✓ API server is already running${NC}"
            return 0
        else
            echo -e "${RED}   ✗ Port 8000 is in use by another process${NC}"
            echo "   Please stop the other process or use --no-api flag"
            exit 1
        fi
    fi
    
    # Start the API server in background
    uvicorn src.main:app --port 8000 --log-level error > /tmp/api_server.log 2>&1 &
    API_PID=$!
    
    # Wait for API to start (max 10 seconds)
    local wait_time=0
    while ! check_api_server && [ $wait_time -lt 10 ]; do
        sleep 1
        wait_time=$((wait_time + 1))
        echo -e "   Waiting for API to start... ${wait_time}s"
    done
    
    if check_api_server; then
        echo -e "${GREEN}   ✓ API server started successfully (PID: $API_PID)${NC}"
        return 0
    else
        echo -e "${RED}   ✗ Failed to start API server${NC}"
        echo "   Check /tmp/api_server.log for details"
        kill $API_PID 2>/dev/null || true
        return 1
    fi
}

# Cleanup function
cleanup() {
    # Only stop API if we started it (not if it was already running)
    if [ ! -z "$API_PID" ] && [ "$API_WAS_RUNNING" = false ] && kill -0 $API_PID 2>/dev/null; then
        echo -e "\n${YELLOW}🛑 Stopping API server (PID: $API_PID)...${NC}"
        kill $API_PID
        wait $API_PID 2>/dev/null || true
        echo -e "${GREEN}   ✓ API server stopped${NC}"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Change to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $(pwd)"
echo ""

# Load test environment if exists
if [ -f ".env.test" ]; then
    echo "📄 Loading test environment from .env.test"
    # Export variables, handling values with commas properly
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^[[:space:]]*# ]] && [[ -n "$key" ]]; then
            # Remove leading/trailing whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            # Export the variable
            export "$key=$value"
        fi
    done < .env.test
fi

# Auto-detect current default prompt version
export CURRENT_DEFAULT_VERSION=$(python -c "
try:
    from src.models.keyword_extraction import KeywordExtractionRequest
    print(KeywordExtractionRequest.__fields__['prompt_version'].default)
except:
    print('1.4.0')
" 2>/dev/null)

echo "📌 Current default prompt version: $CURRENT_DEFAULT_VERSION"
echo ""

# Start API server if not skipped
API_PID=""
API_WAS_RUNNING=false
if [ "$SKIP_API_STARTUP" = false ]; then
    if check_api_server; then
        API_WAS_RUNNING=true
        echo -e "${GREEN}🌐 API server is already running${NC}"
    else
        start_api_server
    fi
    echo ""
fi

# 1. Check Python version
echo -e "${YELLOW}🐍 Checking Python version...${NC}"
python_version=$(python --version 2>&1)
echo "   $python_version"
if [[ $python_version == *"3.10"* ]] || [[ $python_version == *"3.11"* ]] || [[ $python_version == *"3.12"* ]]; then
    echo -e "${GREEN}   ✓ Python version compatible${NC}\n"
else
    echo -e "${RED}   ⚠️  Warning: Recommended Python 3.10+${NC}\n"
fi

# 2. Run Unit Tests (always run)
echo "═══════════════════════════════════════"
echo "🧪 UNIT TESTS"
echo "═══════════════════════════════════════"

run_test_category "Core Models Test" \
    "pytest tests/unit/test_core_models.py -v --tb=short"

run_test_category "API Handlers Test" \
    "pytest tests/unit/test_api_handlers.py -v --tb=short"

run_test_category "Bilingual Services Test" \
    "pytest tests/unit/test_bilingual_services.py -v --tb=short"

run_test_category "Keyword Extraction Pipeline Test" \
    "pytest tests/unit/test_keyword_extraction_pipeline.py -v --tb=short"

run_test_category "Index Calculation Test" \
    "pytest tests/unit/test_index_calculation.py -v --tb=short"

run_test_category "Gap Analysis Test" \
    "pytest tests/unit/test_gap_analysis.py tests/unit/test_gap_analysis_retry.py -v --tb=short"

run_test_category "Resume Format Test" \
    "pytest tests/unit/test_resume_format_models.py tests/unit/test_resume_format_services.py -v --tb=short"

run_test_category "Resume Tailoring Test" \
    "pytest tests/unit/test_resume_tailoring.py -v --tb=short"

# NEW: Add Enhanced Marker Test
run_test_category "Enhanced Marker Test" \
    "pytest tests/unit/test_enhanced_marker.py -v --tb=short"

# 3. Run Integration Tests (partial)
echo "═══════════════════════════════════════"
echo "🔗 INTEGRATION TESTS"
echo "═══════════════════════════════════════"

run_test_category "Azure Deployment Test" \
    "pytest tests/integration/test_azure_deployment.py -v --tb=short"

run_test_category "Index Cal API Test" \
    "pytest tests/integration/test_index_cal_api.py -v --tb=short"

run_test_category "Resume Format Integration Test" \
    "pytest tests/integration/test_resume_format_integration.py -v --tb=short"

run_test_category "Resume Tailoring API Test" \
    "pytest tests/integration/test_resume_tailoring_api.py -v --tb=short"

# NEW: Add Resume Tailoring with Index Test
run_test_category "Resume Tailoring with Index Test" \
    "pytest tests/integration/test_resume_tailoring_with_index.py -v --tb=short"

# NEW: Add Security Test
run_test_category "Security Test" \
    "pytest tests/integration/test_security.py -v --tb=short"

# NEW: Add API Documentation Test
run_test_category "API Documentation Test" \
    "pytest tests/integration/test_api_documentation.py -v --tb=short"

# Run performance tests based on API availability
if check_api_server; then
    echo -e "${GREEN}🌐 API server is available - running all tests${NC}"
    
    # Run performance tests
    if [ "$RUN_FULL_PERF_TESTS" = true ]; then
        echo -e "${YELLOW}   Running FULL performance tests (including flaky ones)${NC}"
        run_test_category "Performance Tests (complete)" \
            "pytest tests/integration/test_performance_suite.py -v --tb=short"
    else
        echo -e "${YELLOW}   Running stable performance tests only (use --full-perf for all)${NC}"
        run_test_category "Performance Tests (stable only)" \
            "pytest tests/integration/test_performance_suite.py -v --tb=short -k 'not (parallel_processing_speedup or api_concurrent_performance)'"
    fi
    
    # Run Bubble.io compatibility tests (standalone script)
    run_test_category "Bubble.io API Compatibility Test" \
        "python tests/integration/test_bubble_api_compatibility.py"
else
    echo -e "${YELLOW}⚠️  API server not available${NC}"
    if [ "$SKIP_API_STARTUP" = true ]; then
        echo -e "${YELLOW}   Running with --no-api flag, skipping online tests${NC}"
    else
        echo -e "${RED}   Failed to start API server, skipping online tests${NC}"
    fi
    SKIPPED_TESTS=$((SKIPPED_TESTS + 2))
    TOTAL_TESTS=$((TOTAL_TESTS + 2))
    
    # Only run offline performance tests
    run_test_category "Performance Tests (offline only)" \
        "pytest tests/integration/test_performance_suite.py -v -k 'not requires_api' --tb=short"
fi

# 4. Check Code Style (if ruff is installed)
echo "═══════════════════════════════════════"
echo "🎨 CODE QUALITY CHECKS"
echo "═══════════════════════════════════════"

if command -v ruff &> /dev/null; then
    run_test_category "Code Style Check (ruff)" \
        "ruff check src/ tests/ --exclude=legacy,archive"
else
    echo -e "${YELLOW}⚠️  ruff not installed, skipping code style check${NC}"
    echo -e "   Install with: pip install ruff"
    SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# 5. Check for common issues
echo "═══════════════════════════════════════"
echo "🔍 COMMON ISSUES CHECK"
echo "═══════════════════════════════════════"

# Check for print statements in src/ (excluding standardization tools)
echo -e "${YELLOW}Checking for debug print statements...${NC}"
if grep -r "print(" src/ --include="*.py" | grep -v "__pycache__" | grep -v "# noqa" | grep -v "src/data/standardization/"; then
    echo -e "${RED}⚠️  Found print statements in source code${NC}"
else
    echo -e "${GREEN}✓ No print statements found${NC}"
fi

# Check for TODO comments
echo -e "\n${YELLOW}Checking for TODO comments...${NC}"
todo_count=$(grep -r "TODO\|FIXME\|XXX" src/ tests/ --include="*.py" | wc -l)
if [ $todo_count -gt 0 ]; then
    echo -e "${YELLOW}📝 Found $todo_count TODO/FIXME comments${NC}"
else
    echo -e "${GREEN}✓ No TODO comments found${NC}"
fi

# Check for required prompt files
echo -e "\n${YELLOW}Checking for required prompt files...${NC}"
missing_prompts=0
prompt_files=(
    "src/prompts/resume_tailoring/v1.0.0.yaml"
    "src/prompts/resume_tailoring/v1.1.0.yaml"
    "src/prompts/keyword_extraction/v1.4.0-en.yaml"
    "src/prompts/keyword_extraction/v1.4.0-zh-TW.yaml"
    "src/prompts/gap_analysis/v1.0.0.yaml"
    "src/prompts/resume_format/v1.0.0.yaml"
)
for prompt_file in "${prompt_files[@]}"; do
    if [ ! -f "$prompt_file" ]; then
        echo -e "${RED}   ✗ Missing: $prompt_file${NC}"
        missing_prompts=$((missing_prompts + 1))
    fi
done
if [ $missing_prompts -eq 0 ]; then
    echo -e "${GREEN}✓ All prompt files found${NC}"
else
    echo -e "${RED}⚠️  Missing $missing_prompts prompt files${NC}"
fi

# 6. Test Coverage Report (if all tests passed)
SKIP_COVERAGE=${SKIP_COVERAGE:-false}
if [ $FAILED_TESTS -eq 0 ] && [ "$SKIP_API_STARTUP" = false ] && [ "$SKIP_COVERAGE" = false ]; then
    echo ""
    echo "═══════════════════════════════════════"
    echo "📊 TEST COVERAGE REPORT"
    echo "═══════════════════════════════════════"
    echo -e "${YELLOW}Generating test coverage report...${NC}"
    echo -e "${YELLOW}(Skip with --no-coverage to save time)${NC}"
    
    # Run coverage with pytest
    if pytest --cov=src --cov-report=html --cov-report=term-missing tests/unit/ tests/integration/ -q; then
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/${NC}"
        
        # Extract coverage percentage
        coverage_percent=$(coverage report | grep "TOTAL" | awk '{print $4}')
        echo -e "${GREEN}Total coverage: $coverage_percent${NC}"
        
        # Check if coverage meets threshold
        coverage_value=$(echo $coverage_percent | sed 's/%//')
        if (( $(echo "$coverage_value >= 80" | bc -l) )); then
            echo -e "${GREEN}✓ Coverage meets 80% threshold${NC}"
        else
            echo -e "${YELLOW}⚠️  Coverage below 80% threshold${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Failed to generate coverage report${NC}"
    fi
else
    if [ "$SKIP_COVERAGE" = true ]; then
        echo -e "${YELLOW}📊 Skipping coverage report (--no-coverage flag)${NC}"
    fi
fi

# 7. Final Summary
echo ""
echo "═══════════════════════════════════════"
echo "📊 TEST SUMMARY"
echo "═══════════════════════════════════════"
echo "Total tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED_TESTS${NC}"
echo ""

# Determine exit status
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! Ready to commit.${NC}"
    echo ""
    echo "💡 Suggested commit command:"
    echo "   git add -A && git commit -m 'feat: your commit message'"
    echo ""
    echo "📝 Usage tips:"
    echo "   ./run_precommit_tests.sh                    # Run with auto API startup (default)"
    echo "   ./run_precommit_tests.sh --no-api           # Skip API tests for quick check"
    echo "   ./run_precommit_tests.sh --parallel         # Run tests in parallel (faster)"
    echo "   ./run_precommit_tests.sh --no-coverage      # Skip coverage report (saves ~30s)"
    echo "   ./run_precommit_tests.sh --parallel --no-coverage  # Fastest full test"
    echo "   ./run_precommit_tests_quick.sh              # Ultra-fast essential tests only"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please fix before committing.${NC}"
    echo ""
    echo "💡 To run specific failed tests:"
    echo "   pytest tests/unit/test_name.py -v"
    echo ""
    echo "💡 To check API server logs (if startup failed):"
    echo "   cat /tmp/api_server.log"
    exit 1
fi