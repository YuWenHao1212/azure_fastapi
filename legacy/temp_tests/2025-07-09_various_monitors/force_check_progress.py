#!/usr/bin/env python3
"""Force check test progress using various methods"""
import subprocess
import os
import json
import glob
from datetime import datetime

def check_methods():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking test progress...")
    print("=" * 60)
    
    # Method 1: Check process
    print("\n1. Process Status:")
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'test_azure_100_simple' in line and 'grep' not in line:
            print(f"   ✅ Test process found: {line[:100]}...")
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                print(f"   Process ID: {pid}")
    
    # Method 2: Check for any output files
    print("\n2. Output Files:")
    patterns = [
        'azure_test_*.log',
        'test_results_*.json',
        'nohup.out',
        '*.out'
    ]
    
    found_files = False
    for pattern in patterns:
        files = glob.glob(pattern)
        for f in files:
            if os.path.getsize(f) > 0:
                print(f"   Found: {f} ({os.path.getsize(f)} bytes)")
                found_files = True
                # Try to read last few lines
                try:
                    with open(f, 'r') as file:
                        lines = file.readlines()
                        if lines:
                            print(f"   Last line: {lines[-1].strip()[:100]}")
                except:
                    pass
    
    if not found_files:
        print("   No output files with content found")
    
    # Method 3: Estimate based on time
    print("\n3. Time-based Estimation:")
    # Assuming test started around 12:51
    start_time = datetime(2025, 7, 9, 12, 51)
    now = datetime.now()
    elapsed_seconds = (now - start_time).total_seconds()
    
    # Each test takes about 20 seconds (5s delay + processing)
    estimated_completed = int(elapsed_seconds / 20)
    if estimated_completed > 100:
        estimated_completed = 100
    
    print(f"   Test started: ~{start_time.strftime('%H:%M')}")
    print(f"   Current time: {now.strftime('%H:%M:%S')}")
    print(f"   Elapsed: {elapsed_seconds/60:.1f} minutes")
    print(f"   Estimated progress: {estimated_completed}/100 ({estimated_completed}%)")
    
    # Method 4: Check Python's stdout/stderr buffering
    print("\n4. Python Output Buffering Issue:")
    print("   The test script is using print() without flush=True")
    print("   Output is likely buffered until process completes or buffer fills")
    print("   Solution: Use 'python -u' for unbuffered output or add flush=True")
    
    # Method 5: Try to find any strace output
    print("\n5. Recommendations:")
    print("   - Kill current test: pkill -f test_azure_100_simple.py")
    print("   - Run with unbuffered output:")
    print("     python -u test_azure_100_simple.py > test_output.log 2>&1 &")
    print("   - Or modify script to use logging module instead of print")

if __name__ == "__main__":
    check_methods()