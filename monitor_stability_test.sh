#!/bin/bash

echo "監控 API 穩定性測試進度"
echo "========================"

while true; do
    # Count completed tests
    if [ -d "api_stability_test_results" ]; then
        COMPLETED=$(ls api_stability_test_results/test_*.json 2>/dev/null | wc -l)
        
        # Clear screen
        clear
        echo "API 穩定性測試進度"
        echo "=================="
        echo "時間: $(date '+%H:%M:%S')"
        echo ""
        echo "進度: $COMPLETED/30 測試完成"
        
        # Progress bar
        printf "["
        for i in $(seq 1 30); do
            if [ $i -le $COMPLETED ]; then
                printf "█"
            else
                printf "░"
            fi
        done
        printf "] %.1f%%\n" $(echo "scale=1; $COMPLETED * 100 / 30" | bc)
        
        # Check if test is complete
        if [ -f "api_stability_test_results/test_summary.json" ]; then
            echo ""
            echo "測試完成！"
            echo ""
            echo "摘要："
            cat api_stability_test_results/test_summary.json | jq -r '
                "總測試數: \(.total_tests)",
                "成功: \(.successful)",
                "失敗: \(.failed)",
                "成功率: \(.success_rate)%",
                "平均時間: \(.average_duration)秒"
            '
            
            # Check for empty fields
            EMPTY_FIELDS=$(cat api_stability_test_results/test_summary.json | jq -r '.empty_field_issues | to_entries | .[] | "\(.key): \(.value)次"')
            if [ ! -z "$EMPTY_FIELDS" ]; then
                echo ""
                echo "空值欄位問題："
                echo "$EMPTY_FIELDS"
            else
                echo ""
                echo "✅ 沒有發現空值欄位！"
            fi
            
            break
        fi
        
        # Check if process is still running
        if ! ps aux | grep -v grep | grep -q "test_api_stability_30.py"; then
            echo ""
            echo "⚠️  測試進程已停止"
            break
        fi
    else
        echo "等待測試開始..."
    fi
    
    sleep 5
done