#!/bin/bash

echo "Monitoring Azure API Test Progress"
echo "=================================="
echo "Start time: 12:27"
echo "Expected completion: ~13:02-13:07 (35-40 minutes)"
echo ""

while true; do
    # Check if process is still running
    if ps aux | grep -v grep | grep -q "test_azure_stability_100.py"; then
        # Look for result directory
        RESULT_DIR=$(ls -d azure_stability_test_results_100_* 2>/dev/null | head -1)
        
        if [ -n "$RESULT_DIR" ]; then
            # Check if detailed_results.json exists
            if [ -f "$RESULT_DIR/detailed_results.json" ]; then
                COUNT=$(grep -o '"iteration":' "$RESULT_DIR/detailed_results.json" 2>/dev/null | wc -l | tr -d ' ')
                echo -ne "\r[$(date '+%H:%M:%S')] Progress: $COUNT/100 tests completed"
            else
                echo -ne "\r[$(date '+%H:%M:%S')] Test running, waiting for results..."
            fi
        else
            echo -ne "\r[$(date '+%H:%M:%S')] Test starting up..."
        fi
    else
        echo -e "\n\nTest completed or stopped!"
        
        # Show final results if available
        RESULT_DIR=$(ls -d azure_stability_test_results_100_* 2>/dev/null | head -1)
        if [ -n "$RESULT_DIR" ] && [ -f "$RESULT_DIR/test_summary.json" ]; then
            echo "Summary available at: $RESULT_DIR/test_summary.json"
            echo ""
            cat "$RESULT_DIR/test_summary.json" | python -m json.tool | head -30
        fi
        break
    fi
    
    sleep 5
done