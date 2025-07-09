#!/usr/bin/env python3
"""Monitor Azure API test progress every minute"""
import os
import json
import time
from datetime import datetime
import glob

def check_progress():
    """Check test progress from result files or logs"""
    
    # Look for test result files
    result_files = glob.glob("test_results_100_*.json")
    
    if result_files:
        # Found completed test results
        latest_file = max(result_files)
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] TEST COMPLETED")
        print(f"=" * 50)
        print(f"Total: {summary.get('total', 0)}")
        print(f"Success: {summary.get('successful', 0)} ({summary.get('success_rate', 0):.1f}%)")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"With empty fields: {summary.get('with_empty_fields', 0)}")
        
        # Check for empty fields details
        if data.get('results'):
            empty_count = {}
            for r in data['results']:
                if r.get('empty_fields'):
                    for field in r['empty_fields']:
                        empty_count[field] = empty_count.get(field, 0) + 1
            
            if empty_count:
                print(f"\nEmpty fields breakdown:")
                for field, count in empty_count.items():
                    print(f"  - {field}: {count}")
            else:
                print(f"\n✅ NO EMPTY FIELDS DETECTED!")
        
        return True
    
    # Check log file for progress
    log_files = ["azure_test_100_final.log", "azure_test_100_simple.log"]
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                # Look for progress lines
                progress_lines = [l for l in lines if "Progress:" in l]
                if progress_lines:
                    latest_progress = progress_lines[-1].strip()
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {latest_progress}")
                    
                    # Extract numbers
                    if "/" in latest_progress:
                        parts = latest_progress.split()
                        for part in parts:
                            if "/" in part:
                                completed, total = part.split("/")
                                try:
                                    completed = int(completed)
                                    total = int(total)
                                    percentage = (completed / total * 100) if total > 0 else 0
                                    
                                    # Estimate time
                                    if completed > 0:
                                        # Assuming 5 seconds per test + response time
                                        avg_time_per_test = 20  # seconds
                                        remaining = total - completed
                                        est_minutes = (remaining * avg_time_per_test) / 60
                                        
                                        print(f"Completed: {completed}/{total} ({percentage:.1f}%)")
                                        print(f"Estimated time remaining: {est_minutes:.1f} minutes")
                                except:
                                    pass
                    return False
            except:
                pass
    
    # Check if process is running
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    test_running = 'test_azure_100_simple' in result.stdout or 'test_azure_stability_100' in result.stdout
    
    if test_running:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Test is running but no progress data yet...")
    else:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] No test process found. Waiting for test to start...")
    
    return False

def monitor_loop():
    """Monitor every minute until test completes"""
    print("Starting Azure API Test Monitor")
    print("Will check progress every minute...")
    print("Press Ctrl+C to stop monitoring")
    
    while True:
        if check_progress():
            print("\n✅ Test completed! Stopping monitor.")
            break
        
        # Wait 1 minute
        time.sleep(60)

if __name__ == "__main__":
    monitor_loop()