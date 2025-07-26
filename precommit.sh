#!/bin/bash

# Pre-commit Test Script - Simplified Version for Keyword Extraction API
# Based on CLAUDE.md Level 0-3 testing strategy
# Usage: ./precommit.sh [--level-0|--level-1|--level-2|--level-3]

set -e  # Exit on error

# Default to Level 2
LEVEL=${1:-"--level-2"}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current time
echo "🚀 Pre-commit Test Suite"
echo "======================="
echo "Time: $(TZ='Asia/Taipei' date '+%Y-%m-%d %H:%M:%S %Z')"
echo "Test Level: $LEVEL"
echo ""

# Load environment variables
if [ -f ".env" ]; then
    echo "📄 Loading environment from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Function to run tests based on level
run_tests() {
    local level=$1
    local passed=0
    local failed=0

    # Level 0: Prompt files only (YAML validation)
    if [[ "$level" == "--level-0" || "$level" == "--level-1" || "$level" == "--level-2" || "$level" == "--level-3" ]]; then
        echo -e "\n${YELLOW}=== Level 0: Prompt File Validation ===${NC}"
        
        # Check if prompt files exist
        if [ -d "src/prompts/keyword_extraction" ]; then
            echo "✓ Prompt directory exists"
            
            # Validate YAML syntax
            for file in src/prompts/keyword_extraction/*.yaml; do
                if [ -f "$file" ]; then
                    python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null
                    if [ $? -eq 0 ]; then
                        echo "✓ $(basename $file) - Valid YAML"
                        ((passed++))
                    else
                        echo -e "${RED}✗ $(basename $file) - Invalid YAML${NC}"
                        ((failed++))
                    fi
                fi
            done
        else
            echo -e "${RED}✗ Prompt directory not found${NC}"
            ((failed++))
        fi
    fi

    # Level 1: Code style checks (Ruff)
    if [[ "$level" == "--level-1" || "$level" == "--level-2" || "$level" == "--level-3" ]]; then
        echo -e "\n${YELLOW}=== Level 1: Code Style Check (Ruff) ===${NC}"
        
        if ruff check src/ tests/ --exclude=legacy,archive; then
            echo -e "${GREEN}✓ Code style check passed${NC}"
            ((passed++))
        else
            echo -e "${RED}✗ Code style check failed${NC}"
            echo "  Run: ruff check src/ tests/ --exclude=legacy,archive --fix"
            ((failed++))
        fi
    fi

    # Level 2: Unit tests
    if [[ "$level" == "--level-2" || "$level" == "--level-3" ]]; then
        echo -e "\n${YELLOW}=== Level 2: Unit Tests ===${NC}"
        
        # Run keyword extraction specific unit tests
        if python -m pytest tests/unit/test_keyword_extraction_pipeline.py -v --tb=short; then
            echo -e "${GREEN}✓ Keyword extraction unit tests passed${NC}"
            ((passed++))
        else
            echo -e "${RED}✗ Keyword extraction unit tests failed${NC}"
            ((failed++))
        fi
        
        # Run core models tests
        if python -m pytest tests/unit/test_core_models.py::TestKeywordExtractionData -v --tb=short; then
            echo -e "${GREEN}✓ Core models unit tests passed${NC}"
            ((passed++))
        else
            echo -e "${RED}✗ Core models unit tests failed${NC}"
            ((failed++))
        fi
    fi

    # Level 3: Integration tests
    if [[ "$level" == "--level-3" ]]; then
        echo -e "\n${YELLOW}=== Level 3: Integration Tests ===${NC}"
        
        # Start local API server for integration tests
        echo "Starting local API server..."
        uvicorn src.main:app --port 8000 > /tmp/api_server.log 2>&1 &
        API_PID=$!
        
        # Wait for server to start
        sleep 5
        
        # Check if server is running
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✓ API server started (PID: $API_PID)"
            
            # Run integration tests
            if python -m pytest tests/integration/test_keyword_extraction_api.py -v --tb=short; then
                echo -e "${GREEN}✓ Integration tests passed${NC}"
                ((passed++))
            else
                echo -e "${RED}✗ Integration tests failed${NC}"
                ((failed++))
            fi
        else
            echo -e "${RED}✗ Failed to start API server${NC}"
            ((failed++))
        fi
        
        # Stop API server
        kill $API_PID 2>/dev/null || true
        echo "API server stopped"
    fi

    # Summary
    echo -e "\n${YELLOW}=== Test Summary ===${NC}"
    echo "Total tests: $((passed + failed))"
    echo -e "${GREEN}Passed: $passed${NC}"
    echo -e "${RED}Failed: $failed${NC}"
    
    if [ $failed -eq 0 ]; then
        echo -e "\n${GREEN}✅ All tests passed! Ready to commit.${NC}"
        return 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please fix before committing.${NC}"
        return 1
    fi
}

# Main execution
case $LEVEL in
    --level-0)
        echo "Running Level 0: Prompt files only"
        run_tests --level-0
        ;;
    --level-1)
        echo "Running Level 1: Prompt files + Code style"
        run_tests --level-1
        ;;
    --level-2)
        echo "Running Level 2: Prompt files + Code style + Unit tests"
        run_tests --level-2
        ;;
    --level-3)
        echo "Running Level 3: Full suite (all tests)"
        run_tests --level-3
        ;;
    *)
        echo "Invalid option. Use: --level-0, --level-1, --level-2, or --level-3"
        exit 1
        ;;
esac