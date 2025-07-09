#!/bin/bash
echo "Azure API Stability Test Status"
echo "=============================="
echo "Current time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check if process is running
if ps aux | grep -v grep | grep -q "test_azure_stability_100.py"; then
    echo "✅ Test is running"
    echo ""
    
    # Estimate completion time (100 tests * 5 seconds interval + ~20 seconds per test)
    echo "Estimated total time: ~35-40 minutes"
    echo "Test started at: ~12:19"
    echo "Expected completion: ~12:54-12:59"
else
    echo "❌ Test is not running"
fi

echo ""
echo "Looking for result directories..."
ls -la | grep azure_stability_test_results_100 || echo "No result directories found yet"

echo ""
echo "To monitor when test completes, run:"
echo "  watch -n 30 ls -la | grep azure_stability_test_results_100"