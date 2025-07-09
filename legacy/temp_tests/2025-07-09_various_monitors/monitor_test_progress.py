#!/usr/bin/env python3
"""Monitor the progress of Azure API stability test"""
import json
import os
import time
from pathlib import Path
from datetime import datetime

def monitor_progress():
    while True:
        # Find the latest test results directory
        result_dirs = list(Path(".").glob("azure_stability_test_results_100_*"))
        
        if result_dirs:
            latest_dir = max(result_dirs, key=lambda x: x.stat().st_mtime)
            results_file = latest_dir / "detailed_results.json"
            
            if results_file.exists():
                with open(results_file, "r") as f:
                    try:
                        results = json.load(f)
                        total_completed = len(results)
                        successful = sum(1 for r in results if r["status"] == "success")
                        
                        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Progress: {total_completed}/100 tests completed | Success: {successful}/{total_completed}", end="", flush=True)
                        
                        if total_completed >= 100:
                            print("\n\nTest completed!")
                            break
                    except:
                        pass
        
        time.sleep(5)

if __name__ == "__main__":
    print("Monitoring Azure API stability test progress...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        monitor_progress()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")