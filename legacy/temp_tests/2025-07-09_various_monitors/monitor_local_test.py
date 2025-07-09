#!/usr/bin/env python3
"""Monitor local test progress by checking for result files"""
import os
import json
import time
from datetime import datetime

def check_test_status():
    # Check for any test result files
    result_files = [f for f in os.listdir('.') if f.startswith('test_results_100_') and f.endswith('.json')]
    
    if result_files:
        latest_file = max(result_files)
        print(f"\nFound result file: {latest_file}")
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
            
        summary = data.get('summary', {})
        print(f"\nTest Summary:")
        print(f"- Total tests: {summary.get('total', 0)}")
        print(f"- Successful: {summary.get('successful', 0)}")
        print(f"- Failed: {summary.get('failed', 0)}")
        print(f"- With empty fields: {summary.get('with_empty_fields', 0)}")
        print(f"- Success rate: {summary.get('success_rate', 0):.1f}%")
        
        # Check for empty fields details
        if 'results' in data:
            empty_field_details = {}
            for result in data['results']:
                if result.get('empty_fields'):
                    for field in result['empty_fields']:
                        if field not in empty_field_details:
                            empty_field_details[field] = 0
                        empty_field_details[field] += 1
            
            if empty_field_details:
                print(f"\nEmpty fields breakdown:")
                for field, count in empty_field_details.items():
                    print(f"- {field}: {count} occurrences")
        
        return True
    
    return False

if __name__ == "__main__":
    print("Checking for test results...")
    
    if not check_test_status():
        print("No test result files found yet.")
        print("\nPossible reasons:")
        print("1. Test is still running")
        print("2. Test failed to start")
        print("3. Results are being written to a different location")
    
    # Check if any test process is running
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'test_azure' in result.stdout:
        print("\n✅ A test process appears to be running")