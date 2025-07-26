#!/bin/bash
# Demo script to test the new level-based precommit test system

echo "🧪 Testing new level-based precommit test system"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Testing different levels (dry run - just showing what would run):"
echo ""

# Test Level 0
echo -e "${YELLOW}📋 Level 0 - Prompt files only:${NC}"
echo "./run_precommit_tests.sh --level-0"
echo "Expected: Only check prompt files exist"
echo ""

# Test Level 1  
echo -e "${YELLOW}📋 Level 1 - Code style only:${NC}"
echo "./run_precommit_tests.sh --level-1"
echo "Expected: Only run ruff code style checks"
echo ""

# Test Level 2
echo -e "${YELLOW}📋 Level 2 - Code style + Unit tests:${NC}"
echo "./run_precommit_tests.sh --level-2 --parallel"
echo "Expected: Run ruff + all unit tests (with parallel execution)"
echo ""

# Test Level 3
echo -e "${YELLOW}📋 Level 3 - Full suite:${NC}"
echo "./run_precommit_tests.sh --level-3 --parallel"
echo "Expected: Run everything including integration and performance tests"
echo ""

echo -e "${GREEN}✅ Test script created! You can now test each level manually.${NC}"
echo ""
echo "Quick test commands:"
echo "  chmod +x test_levels_demo.sh"
echo "  ./run_precommit_tests.sh --level-0  # Should be very fast"
echo "  ./run_precommit_tests.sh --level-1  # Should run code style only"