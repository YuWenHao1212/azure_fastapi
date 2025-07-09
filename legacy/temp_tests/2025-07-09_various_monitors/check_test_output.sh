#!/bin/bash

echo "Checking test process and output..."
echo "==================================="

# Check process
if ps aux | grep -v grep | grep -q "test_azure_100_simple.py"; then
    echo "✅ Test process is running"
    PID=$(ps aux | grep test_azure_100_simple.py | grep -v grep | awk '{print $2}')
    echo "Process ID: $PID"
    
    # Check open files
    echo -e "\nChecking open files for process $PID:"
    lsof -p $PID 2>/dev/null | grep -E "\.log|\.json" | tail -5
    
    # Force flush Python output
    echo -e "\nTrying to get current output..."
    
    # Check if nohup.out exists
    if [ -f nohup.out ]; then
        echo "Found nohup.out:"
        tail -20 nohup.out
    fi
    
    # Check standard test locations
    for file in azure_test_100_final.log azure_test_100_simple.log test_results_100_*.json; do
        if [ -f "$file" ]; then
            echo -e "\nFound $file:"
            if [[ $file == *.log ]]; then
                tail -20 "$file"
            else
                cat "$file" | python -m json.tool | head -20
            fi
        fi
    done
else
    echo "❌ Test process not found"
fi

# Based on your comment, the API has been called 3 times
echo -e "\n📊 Current status (based on your observation):"
echo "- API calls made: 3"
echo "- Progress: 3/100 (3%)"
echo "- Estimated time per request: ~20 seconds (including 5s delay)"
echo "- Estimated remaining time: ~32 minutes"