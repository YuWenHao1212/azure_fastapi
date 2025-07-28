#!/bin/bash

# Pre-commit Test Script - Compliant with CLAUDE.md v2.8.3
# 
# This script implements the 4-level testing strategy from CLAUDE.md.
# Currently includes keyword extraction tests as the foundation,
# with other endpoints to be added progressively during development.
#
# Usage: ./precommit.sh [options]
# Options:
#   --level-0: Prompt files only (YAML validation)
#   --level-1: + Code style checks (Ruff)
#   --level-2: + Unit tests (default)
#   --level-3: + Integration tests
#   --parallel: Run tests in parallel (Level 2-3)
#   --no-coverage: Skip coverage report

# Don't exit on error - we want to see all test results
# set -e

# Default settings
TEST_LEVEL=2
USE_PARALLEL=false
SKIP_COVERAGE=false

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_LOWER_LEVELS=false
for arg in "$@"; do
    case $arg in
        --level-0) TEST_LEVEL=0 ;;
        --level-1) TEST_LEVEL=1 ;;
        --level-2) TEST_LEVEL=2 ;;
        --level-3) TEST_LEVEL=3 ;;
        --level-4) 
            TEST_LEVEL=4
            SKIP_LOWER_LEVELS=true
            ;;
        --parallel) USE_PARALLEL=true ;;
        --no-coverage) SKIP_COVERAGE=true ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--level-0|--level-1|--level-2|--level-3|--level-4] [--parallel] [--no-coverage]"
            echo ""
            echo "Note: --level-4 runs ONLY Azure Functions test (skips levels 0-3)"
            exit 1
            ;;
    esac
done

# Header
if [ "$SKIP_LOWER_LEVELS" = true ]; then
    echo "🚀 Azure Functions Local Test Only (Level 4)"
else
    echo "🚀 Pre-commit Tests (Level $TEST_LEVEL$([ "$USE_PARALLEL" = true ] && echo ", parallel")$([ "$SKIP_COVERAGE" = true ] && echo ", no coverage"))"
fi
echo "─────────────────────────────────────"

# Track results
PASSED=0
FAILED=0
START_TIME=$(date +%s)

# Function to run command and track result
run_test() {
    local description=$1
    local command=$2
    
    # Show progress indicator
    echo -n "  • $description... "
    
    if eval "$command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        echo -e "    ${RED}Error output:${NC}"
        cat /tmp/test_output.log | head -5
        ((FAILED++))
        # Don't exit - continue running other tests
    fi
}

# Function to check execution time
check_time() {
    local level=$1
    local max_seconds=$2
    local elapsed=$(($(date +%s) - START_TIME))
    
    if [ $elapsed -gt $max_seconds ]; then
        echo -e "${YELLOW}⚠️  Warning: Level $level took ${elapsed}s (expected < ${max_seconds}s)${NC}"
    fi
}

# Load environment variables
if [ -f ".env" ]; then
    echo "📄 Loading environment from .env"
    # Safer method to load .env file
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^[[:space:]]*# ]] && [[ -n "$key" ]]; then
            # Remove leading/trailing whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            # Only export if key is valid
            if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
                export "$key"="$value"
            fi
        fi
    done < .env
    echo ""
fi

# ====================
# LEVEL 0: Prompt Files (< 5 seconds)
# ====================
if [ $TEST_LEVEL -ge 0 ] && [ "$SKIP_LOWER_LEVELS" = false ]; then
    echo -e "${BLUE}Level 0: Prompt Validation${NC}"
    
    LEVEL_START=$(date +%s)
    
    # Check prompt directory exists
    if [ -d "src/prompts/keyword_extraction" ]; then
        # Count and validate YAML files
        yaml_count=$(ls src/prompts/keyword_extraction/*.yaml 2>/dev/null | wc -l)
        echo -n "  • Validating $yaml_count prompt files... "
        
        # Validate all YAML files
        failed=0
        validated=0
        for yaml_file in src/prompts/keyword_extraction/*.yaml; do
            if [ -f "$yaml_file" ]; then
                if python -c "import yaml; yaml.safe_load(open('$yaml_file'))" >/dev/null 2>&1; then
                    ((validated++))
                else
                    failed=1
                    break
                fi
            fi
        done
        
        if [ $failed -eq 0 ] && [ $validated -eq $yaml_count ]; then
            echo -e "${GREEN}✓${NC} ($validated files)"
            PASSED=$((PASSED + validated))  # Count each file as a test
        else
            echo -e "${RED}✗${NC}"
            FAILED=$((FAILED + 1))
        fi
        
        # Check version naming convention
        run_test "Version naming convention" \
            "ls src/prompts/keyword_extraction/*.yaml | grep -E 'v[0-9]+\.[0-9]+\.[0-9]+(-[a-z]{2}(-[A-Z]{2})?)?\.yaml' > /dev/null"
    else
        echo -e "  ${RED}✗ Prompt directory not found${NC}"
        ((FAILED++))
    fi
    
    check_time 0 5
    echo ""
fi

# ====================
# LEVEL 1: Code Style (< 1 second)
# ====================
if [ $TEST_LEVEL -ge 1 ] && [ "$SKIP_LOWER_LEVELS" = false ]; then
    echo -e "${BLUE}Level 1: Code Style${NC}"
    
    LEVEL_START=$(date +%s)
    
    # Run Ruff on entire codebase (simpler and more reliable)
    echo -n "  • Code style checks... "
    
    # Try to run ruff with different methods
    ruff_success=false
    
    # Method 1: Try python -m ruff (most reliable in virtual environments)
    if python -m ruff check src/ tests/ --exclude=legacy,archive > /tmp/ruff_output.log 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        ruff_success=true
    # Method 2: Try direct ruff command
    elif command -v ruff &> /dev/null && ruff check src/ tests/ --exclude=legacy,archive > /tmp/ruff_output.log 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        ruff_success=true
    # Method 3: Try with explicit .venv path if it exists
    elif [ -f ".venv/bin/ruff" ] && .venv/bin/ruff check src/ tests/ --exclude=legacy,archive > /tmp/ruff_output.log 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        ruff_success=true
    # Method 4: Try with explicit venv path (no dot)
    elif [ -f "venv/bin/ruff" ] && venv/bin/ruff check src/ tests/ --exclude=legacy,archive > /tmp/ruff_output.log 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        ruff_success=true
    fi
    
    # If all methods failed, check if it's because ruff is not installed or there are actual errors
    if [ "$ruff_success" = false ]; then
        # Check if the error is about ruff not being found
        if grep -q "No module named 'ruff'" /tmp/ruff_output.log 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Skipped${NC} (ruff not installed)"
            echo "    Note: Code style checks skipped in this environment"
            # Don't count as failure if ruff is simply not installed
        else
            echo -e "${RED}✗${NC}"
            echo -e "    ${RED}Ruff errors found:${NC}"
            # Show first 10 lines of errors
            head -10 /tmp/ruff_output.log | sed 's/^/    /'
            echo "    ... (run 'python -m ruff check src/ tests/ --exclude=legacy,archive' for full output)"
            ((FAILED++))
        fi
    fi
    
    check_time 1 1
    echo ""
fi

# ====================
# LEVEL 2: Unit Tests (10-30 seconds)
# ====================
if [ $TEST_LEVEL -ge 2 ] && [ "$SKIP_LOWER_LEVELS" = false ]; then
    echo -e "${BLUE}Level 2: Unit Tests${NC}"
    
    LEVEL_START=$(date +%s)
    
    # Build pytest command (quiet mode for cleaner output)
    PYTEST_CMD="python -m pytest -q --tb=short"
    if [ "$USE_PARALLEL" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -n auto"
    fi
    if [ "$SKIP_COVERAGE" = false ]; then
        # Suppress coverage warnings with better settings
        export COVERAGE_CORE=sysmon
        PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report= --no-cov-on-fail"
    fi
    
    # Run keyword extraction specific unit tests
    run_test "Unit tests - keyword extraction pipeline" \
        "$PYTEST_CMD tests/unit/test_keyword_extraction_pipeline.py 2>/dev/null | grep -v 'CoverageWarning'"
    
    run_test "Unit tests - keyword standardizer" \
        "$PYTEST_CMD tests/unit/test_keyword_standardizer.py 2>/dev/null | grep -v 'CoverageWarning'"
    
    run_test "Unit tests - keyword extraction models" \
        "$PYTEST_CMD tests/unit/test_core_models.py::TestKeywordExtractionData 2>/dev/null | grep -v 'CoverageWarning'"
    
    # Check for language validation tests
    if [ -f "tests/unit/test_language_validation.py" ]; then
        echo -e "${YELLOW}Checking for keyword-specific language validation tests...${NC}"
        # Run silently first to check if any tests exist
        if python -m pytest tests/unit/test_language_validation.py -k 'keyword' --collect-only -q 2>/dev/null | grep -q "test"; then
            run_test "Unit tests - language validation (keyword)" \
                "$PYTEST_CMD tests/unit/test_language_validation.py -k 'keyword' 2>/dev/null | grep -v 'CoverageWarning'"
        else
            echo -e "${YELLOW}⚠️  No keyword-specific tests found in language validation${NC}"
            echo ""
        fi
    fi
    
    check_time 2 30
fi

# ====================
# LEVEL 3: Integration Tests (1-2 minutes)
# ====================
if [ $TEST_LEVEL -ge 3 ] && [ "$SKIP_LOWER_LEVELS" = false ]; then
    echo -e "${BLUE}Level 3: Integration Tests${NC}"
    
    LEVEL_START=$(date +%s)
    
    # Check if API keys are configured
    if [ -z "$AZURE_OPENAI_API_KEY" ] && [ -z "$LLM2_API_KEY" ] && [ -z "$GPT41_MINI_JAPANEAST_API_KEY" ]; then
        echo -e "${RED}❌ ERROR: No API keys found in .env file${NC}"
        echo -e "${YELLOW}Integration tests (Level 3) require real API credentials.${NC}"
        echo -e "${YELLOW}Please set one of:${NC}"
        echo -e "${YELLOW}  - AZURE_OPENAI_API_KEY or LLM2_API_KEY (for Azure OpenAI)${NC}"
        echo -e "${YELLOW}  - GPT41_MINI_JAPANEAST_API_KEY (for GPT-4.1 mini)${NC}"
        ((FAILED++))
        echo ""
        check_time 3 120
        echo ""
        # Skip to next level
        TEST_LEVEL=$((TEST_LEVEL - 1))  # Prevent Level 4 from running if no API keys
    else
        echo -e "${GREEN}✅ Real API credentials found. Running integration tests.${NC}"
        available_apis=""
        [ -n "$AZURE_OPENAI_API_KEY" ] || [ -n "$LLM2_API_KEY" ] && available_apis="${available_apis}Azure-OpenAI "
        [ -n "$GPT41_MINI_JAPANEAST_API_KEY" ] && available_apis="${available_apis}GPT-4.1-mini "
        echo -e "${BLUE}Available APIs: ${available_apis}${NC}"
        echo ""
        
        # Start API server
        echo -n "  • Starting API server... "
        SERVER_STARTED=false
        
        # Kill any existing process on port 8000
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 1
        
        # Start server with better error handling
        uvicorn src.main:app --port 8000 --log-level error > /tmp/api_server.log 2>&1 &
        API_PID=$!
        
        # Wait for server to start with timeout
        for i in {1..10}; do
            if curl -s http://localhost:8000/health > /dev/null 2>/dev/null; then
                echo -e "${GREEN}✓${NC} (PID: $API_PID)"
                SERVER_STARTED=true
                break
            fi
            sleep 1
        done
        
        if [ "$SERVER_STARTED" = false ]; then
            echo -e "${RED}✗${NC}"
        fi
        
        if [ "$SERVER_STARTED" = true ]; then
            # Build pytest command for integration tests
            PYTEST_CMD="python -m pytest -v --tb=short"
            if [ "$USE_PARALLEL" = true ]; then
                PYTEST_CMD="$PYTEST_CMD -n auto"
            fi
            
            # Run integration tests with real API
            echo -e "${BLUE}Running integration tests with real API...${NC}"
            
            # Test real API providers
            if [ -f "tests/integration/test_real_api_providers.py" ]; then
                run_test "Integration tests - Real API providers" \
                    "$PYTEST_CMD tests/integration/test_real_api_providers.py -s"
            fi
            
            # Test Azure deployment (includes keyword extraction)
            if [ -f "tests/integration/test_azure_deployment.py" ]; then
                run_test "Integration tests - Azure deployment" \
                    "$PYTEST_CMD tests/integration/test_azure_deployment.py::TestAzureFunctionsIntegration::test_keyword_extraction_endpoint -s"
            fi
            
            # Test LLM switching (includes keyword extraction)
            if [ -f "tests/integration/test_llm_switching_integration.py" ]; then
                run_test "Integration tests - LLM switching" \
                    "$PYTEST_CMD tests/integration/test_llm_switching_integration.py -s"
            fi
            
            # Stop API server
            kill $API_PID 2>/dev/null || true
            echo "  • API server stopped"
        else
            echo -e "${RED}❌ Failed to start API server${NC}"
            echo "Server log:"
            cat /tmp/api_server.log 2>/dev/null || echo "No log available"
            ((FAILED++))
            kill $API_PID 2>/dev/null || true
        fi
        
        check_time 3 120
        echo ""
    fi
fi

# ====================
# LEVEL 4: Azure Functions Local Test (< 3 minutes)
# ====================
if [ $TEST_LEVEL -ge 4 ]; then
    # Show message if skipping lower levels
    if [ "$SKIP_LOWER_LEVELS" = true ]; then
        echo -e "${YELLOW}Skipping Levels 0-3, running only Level 4 Azure Functions test${NC}"
        echo ""
    fi
    
    echo -e "${BLUE}Level 4: Azure Functions Local Test (Pre-deployment)${NC}"
    
    LEVEL_START=$(date +%s)
    
    # Check prerequisites
    echo -n "  • Checking Azure Functions Core Tools... "
    if command -v func &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo -e "    ${RED}Azure Functions Core Tools not installed${NC}"
        echo "    Install with: brew install azure-functions-core-tools@4"
        ((FAILED++))
        check_time 4 180
        echo ""
        # Skip rest of Level 4 if func not installed
        TEST_LEVEL=3
    fi
    
    if [ $TEST_LEVEL -ge 4 ]; then
        # Check for real API credentials
        if [ -z "$AZURE_OPENAI_API_KEY" ] && [ -z "$LLM2_API_KEY" ] && [ -z "$GPT41_MINI_JAPANEAST_API_KEY" ]; then
            echo -e "  ${YELLOW}⚠️  Warning: No real API keys found. Level 4 requires actual API credentials.${NC}"
            echo -e "  ${YELLOW}   Skipping Level 4 tests.${NC}"
            echo ""
        else
            echo -e "  ${GREEN}✓ API credentials available${NC}"
            
            # Create test evidence directory if not exists
            EVIDENCE_DIR="temp/tests/evidence"
            mkdir -p "$EVIDENCE_DIR"
            TEST_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
            EVIDENCE_FILE="$EVIDENCE_DIR/level4_${TEST_TIMESTAMP}.json"
            echo "  📁 Test evidence will be saved to: $EVIDENCE_FILE"
            
            # Check if local.settings.json exists
            if [ ! -f "local.settings.json" ]; then
                echo -e "${YELLOW}⚠️  local.settings.json not found${NC}"
                echo "    Creating from .env file..."
                
                # Create local.settings.json from .env
                cat > local.settings.json << 'EOF'
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "PYTHON_ISOLATE_WORKER_DEPENDENCIES": "1",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing"
  },
  "Host": {
    "LocalHttpPort": 7071,
    "CORS": "*",
    "CORSCredentials": false
  }
}
EOF
                
                # Add environment variables from .env to local.settings.json
                if [ -f .env ]; then
                    # Use Python to merge .env into local.settings.json
                    python3 -c "
import json
import os
from pathlib import Path

# Load .env file
env_vars = {}
if Path('.env').exists():
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('\"')

# Load local.settings.json
with open('local.settings.json', 'r') as f:
    settings = json.load(f)

# Add env vars to settings
settings['Values'].update(env_vars)

# Write back
with open('local.settings.json', 'w') as f:
    json.dump(settings, f, indent=2)
"
                fi
            fi
            
            # Start Azure Functions locally
            echo -n "  • Starting Azure Functions locally... "
            
            # Kill any existing Functions process
            pkill -f "func start" 2>/dev/null || true
            lsof -ti:7071 | xargs kill -9 2>/dev/null || true
            sleep 1
            
            # Start Functions with Python runtime specified
            func start --port 7071 --python > /tmp/azure_functions.log 2>&1 &
            FUNC_PID=$!
            
            # Wait for Functions to start
            FUNC_STARTED=false
            for i in {1..20}; do
                # Check if Functions HTTP endpoint is responding
                if curl -s http://localhost:7071/ > /dev/null 2>/dev/null || \
                   curl -s http://localhost:7071/api/v1/health > /dev/null 2>/dev/null; then
                    echo -e "${GREEN}✓${NC} (PID: $FUNC_PID)"
                    FUNC_STARTED=true
                    break
                fi
                sleep 1
            done
            
            if [ "$FUNC_STARTED" = false ]; then
                echo -e "${RED}✗${NC}"
                echo "    Functions log:"
                tail -20 /tmp/azure_functions.log
                ((FAILED++))
            fi
            
            if [ "$FUNC_STARTED" = true ]; then
                # Run real API tests against local Functions
                echo "  • Testing with real Azure OpenAI API:"
                
                # Test keyword extraction
                echo -n "    - Keyword extraction endpoint... "
                
                # Prepare test input
                TEST_INPUT='{
                    "job_description": "We are looking for a Senior Python Developer with experience in FastAPI, Azure cloud services, and machine learning.",
                    "language": "en",
                    "max_keywords": 10
                }'
                
                # Record start time
                TEST_START_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
                
                # Make API call
                response=$(curl -s -w "\n%{http_code}" -X POST \
                    "http://localhost:7071/api/v1/extract-jd-keywords" \
                    -H "Content-Type: application/json" \
                    -d "$TEST_INPUT" 2>/dev/null || echo "CURL_ERROR")
                
                if [[ "$response" == *"CURL_ERROR"* ]]; then
                    echo -e "${RED}✗ (connection failed)${NC}"
                    
                    # Create combined evidence file for failure
                    cat > "$EVIDENCE_FILE" << EOF
{
  "metadata": {
    "test_name": "keyword_extraction",
    "endpoint": "/api/v1/extract-jd-keywords",
    "timestamp": "$TEST_START_TIME",
    "http_status": "connection_failed",
    "test_result": "FAILED",
    "failure_reason": "Connection failed"
  },
  "input": $(echo "$TEST_INPUT" | jq '.' 2>/dev/null || echo "$TEST_INPUT"),
  "output": null
}
EOF
                    ((FAILED++))
                else
                    status_code=$(echo "$response" | tail -n 1)
                    body=$(echo "$response" | sed '$d')
                    
                    if [ "$status_code" = "200" ]; then
                        # Check if response has expected structure
                        if echo "$body" | grep -q '"success":true' && echo "$body" | grep -q '"keywords":\['; then
                            keyword_count=$(echo "$body" | grep -o '"keywords":\[[^]]*\]' | grep -o '"[^"]*"' | grep -v "keywords" | wc -l)
                            echo -e "${GREEN}✓${NC} ($keyword_count keywords extracted)"
                            
                            # Create combined evidence file for success
                            cat > "$EVIDENCE_FILE" << EOF
{
  "metadata": {
    "test_name": "keyword_extraction",
    "endpoint": "/api/v1/extract-jd-keywords",
    "timestamp": "$TEST_START_TIME",
    "http_status": "$status_code",
    "test_result": "PASSED",
    "keyword_count": $keyword_count
  },
  "input": $(echo "$TEST_INPUT" | jq '.' 2>/dev/null || echo "$TEST_INPUT"),
  "output": $(echo "$body" | jq '.' 2>/dev/null || echo "$body")
}
EOF
                            ((PASSED++))
                        else
                            echo -e "${RED}✗ (invalid response structure)${NC}"
                            
                            # Create combined evidence file for invalid response
                            cat > "$EVIDENCE_FILE" << EOF
{
  "metadata": {
    "test_name": "keyword_extraction",
    "endpoint": "/api/v1/extract-jd-keywords",
    "timestamp": "$TEST_START_TIME",
    "http_status": "$status_code",
    "test_result": "FAILED",
    "failure_reason": "Invalid response structure"
  },
  "input": $(echo "$TEST_INPUT" | jq '.' 2>/dev/null || echo "$TEST_INPUT"),
  "output": $(echo "$body" | jq '.' 2>/dev/null || echo "$body")
}
EOF
                            ((FAILED++))
                        fi
                    else
                        echo -e "${RED}✗ (HTTP $status_code)${NC}"
                        
                        # Create combined evidence file for HTTP error
                        cat > "$EVIDENCE_FILE" << EOF
{
  "metadata": {
    "test_name": "keyword_extraction",
    "endpoint": "/api/v1/extract-jd-keywords",
    "timestamp": "$TEST_START_TIME",
    "http_status": "$status_code",
    "test_result": "FAILED",
    "failure_reason": "HTTP error"
  },
  "input": $(echo "$TEST_INPUT" | jq '.' 2>/dev/null || echo "$TEST_INPUT"),
  "output": $(echo "$body" | jq '.' 2>/dev/null || echo "$body")
}
EOF
                        ((FAILED++))
                    fi
                fi
                
                # Add more endpoint tests here as needed
                
                # Stop Functions
                kill $FUNC_PID 2>/dev/null || true
                echo "  • Azure Functions stopped"
                
                # Show evidence file location
                echo ""
                echo "  📊 Test Evidence: $EVIDENCE_FILE"
            fi
        fi
    fi
    
    check_time 4 180
    echo ""
fi

# ====================
# SUMMARY
# ====================
echo ""
echo -e "${BLUE}Summary${NC}"
echo "Total Time: $(($(date +%s) - START_TIME)) seconds"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed! Ready to commit.${NC}"
    echo ""
    echo "According to CLAUDE.md, you should now:"
    echo "1. Review the test results"
    echo "2. Get explicit approval before committing"
    echo "3. Use conventional commit message format"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Please fix before committing.${NC}"
    echo ""
    echo "Tips:"
    echo "- Run 'ruff check --fix' to auto-fix style issues"
    echo "- Check test output above for specific failures"
    echo "- Ensure all YAML files are valid"
    exit 1
fi