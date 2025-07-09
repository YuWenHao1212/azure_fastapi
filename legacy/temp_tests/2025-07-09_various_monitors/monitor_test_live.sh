#!/bin/bash

echo "Live monitoring Azure API test..."
echo "================================"
echo "Test started at: 13:01:43"
echo "Progress updates every 10 tests"
echo ""

while true; do
    # Check if process is still running
    if ps aux | grep -v grep | grep -q "test_azure_100_simple.py"; then
        # Get latest log content
        if [ -f "test_output_unbuffered.log" ]; then
            echo -e "\n[$(date '+%H:%M:%S')] Current log content:"
            echo "-----------------------------------"
            cat test_output_unbuffered.log | tail -10
            
            # Check for completion
            if grep -q "TEST SUMMARY" test_output_unbuffered.log; then
                echo -e "\n✅ Test completed!"
                cat test_output_unbuffered.log | grep -A 20 "TEST SUMMARY"
                break
            fi
        fi
    else
        echo -e "\n❌ Test process not found"
        break
    fi
    
    # Wait 30 seconds before next check
    sleep 30
done