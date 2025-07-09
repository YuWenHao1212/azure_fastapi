#!/usr/bin/env python3
"""Monitor test progress every minute"""
import time
import os
from datetime import datetime, timedelta

def get_latest_progress():
    """Get latest progress from log file"""
    if not os.path.exists("test_output_unbuffered.log"):
        return None
    
    with open("test_output_unbuffered.log", "r") as f:
        lines = f.readlines()
    
    # Find progress lines
    progress_lines = [l.strip() for l in lines if "Progress:" in l]
    
    if progress_lines:
        return progress_lines[-1]
    return None

def monitor():
    print("Monitoring Azure API Test Progress")
    print("==================================")
    print("Test started at: 13:01:43")
    print("Checking every minute...\n")
    
    last_progress = None
    
    while True:
        current_progress = get_latest_progress()
        
        if current_progress and current_progress != last_progress:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {current_progress}")
            
            # Parse progress
            if "/" in current_progress:
                parts = current_progress.split("|")
                if len(parts) >= 1:
                    progress_part = parts[0].split(":")[-1].strip()
                    if "/" in progress_part:
                        completed, total = progress_part.split("/")
                        completed = int(completed)
                        total = int(total)
                        
                        # Estimate remaining time
                        if completed > 0:
                            elapsed_minutes = (datetime.now() - datetime(2025, 7, 9, 13, 1, 43)).total_seconds() / 60
                            rate = completed / elapsed_minutes
                            remaining = total - completed
                            eta_minutes = remaining / rate if rate > 0 else 0
                            
                            print(f"  → {completed}% complete")
                            print(f"  → Estimated time remaining: {eta_minutes:.1f} minutes")
                            eta = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=int(eta_minutes))
                            print(f"  → ETA: {eta.strftime('%H:%M')}")
                            
                            # Check for completion
                            if completed >= total:
                                print("\n✅ Test completed!")
                                # Look for summary
                                with open("test_output_unbuffered.log", "r") as f:
                                    content = f.read()
                                    if "TEST SUMMARY" in content:
                                        print(content[content.find("TEST SUMMARY"):])
                                return
            
            last_progress = current_progress
        elif not current_progress:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for first progress update...")
        
        # Check if process is still running
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'test_azure_100_simple' not in result.stdout:
            print("\n❌ Test process not found. Test may have completed or stopped.")
            break
        
        # Wait 1 minute
        time.sleep(60)

if __name__ == "__main__":
    from datetime import timedelta
    monitor()