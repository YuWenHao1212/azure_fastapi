#!/usr/bin/env python3
"""
Monitor API logs and run tests to capture LLM responses when empty fields occur.
"""

import subprocess
import time
import threading
import re
import json
from datetime import datetime
from pathlib import Path

# Global storage for captured logs
captured_logs = []
test_results = []

def monitor_uvicorn_logs():
    """Monitor uvicorn logs for LLM responses and gap analysis warnings."""
    # Find uvicorn process
    ps_output = subprocess.check_output(['ps', 'aux'], text=True)
    uvicorn_pid = None
    
    for line in ps_output.splitlines():
        if 'uvicorn src.main:app' in line and 'grep' not in line:
            uvicorn_pid = line.split()[1]
            break
    
    if not uvicorn_pid:
        print("❌ Uvicorn process not found. Please start it with: uvicorn src.main:app --reload")
        return
    
    print(f"✅ Found uvicorn process: PID {uvicorn_pid}")
    print("Monitoring logs...")
    
    # Monitor logs using tail
    process = subprocess.Popen(
        ['tail', '-f', '-n', '0', f'/tmp/uvicorn_{uvicorn_pid}.log'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    current_request = {}
    
    for line in process.stdout:
        timestamp = datetime.now().isoformat()
        
        # Capture correlation ID
        if "x-correlation-id" in line:
            match = re.search(r'x-correlation-id:\s*([a-f0-9-]+)', line)
            if match:
                current_request['correlation_id'] = match.group(1)
                current_request['timestamp'] = timestamp
        
        # Capture raw LLM response
        if "Raw LLM response:" in line:
            current_request['raw_llm_response'] = line.strip()
        
        # Capture gap analysis warnings
        if "[GAP_ANALYSIS]" in line or "empty" in line.lower():
            if 'warnings' not in current_request:
                current_request['warnings'] = []
            current_request['warnings'].append(line.strip())
        
        # Capture empty field errors
        if "[GAP_ANALYSIS_EMPTY]" in line:
            current_request['has_empty_fields'] = True
            match = re.search(r'Empty fields detected: \[(.*?)\]', line)
            if match:
                current_request['empty_fields'] = match.group(1).split(', ')
        
        # Save when request completes
        if "Request completed" in line or "HTTP/1.1 200" in line:
            if current_request:
                captured_logs.append(current_request.copy())
                print(f"📝 Captured request data: {current_request.get('correlation_id', 'unknown')}")
                if current_request.get('has_empty_fields'):
                    print(f"  ⚠️  Empty fields detected: {current_request.get('empty_fields')}")
                current_request = {}

def run_api_tests(num_tests=2):
    """Run API tests."""
    import requests
    
    print(f"\nStarting {num_tests} API tests...")
    
    api_url = "http://localhost:8000/api/v1/index-cal-and-gap-analysis"
    test_data = {
        "job_description": "We are looking for a Senior Python Developer with 5+ years of experience in FastAPI, microservices, and cloud platforms (AWS/Azure). Must have strong knowledge of Docker, Kubernetes, and CI/CD pipelines. Experience with monitoring tools and team leadership required.",
        "resume": "Backend Developer with 4 years experience in Python, REST API development, and microservices. Skilled in PostgreSQL, MongoDB, Redis. Experience with CI/CD using Jenkins and GitLab. Contributed to distributed systems serving millions of users.",
        "keywords": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "Microservices", "CI/CD", "REST API", "monitoring tools", "team leadership"],
        "language": "en"
    }
    
    for i in range(1, num_tests + 1):
        print(f"\nTest {i}/{num_tests}...")
        start_time = datetime.now()
        
        try:
            response = requests.post(api_url, json=test_data, timeout=60)
            duration = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for empty fields
                gap = data.get("data", {}).get("gap_analysis", {})
                empty_fields = []
                
                if gap.get("OverallAssessment") == "<p></p>":
                    empty_fields.append("OverallAssessment")
                if gap.get("CoreStrengths") == "<ol></ol>":
                    empty_fields.append("CoreStrengths")
                if gap.get("KeyGaps") == "<ol></ol>":
                    empty_fields.append("KeyGaps")
                if gap.get("QuickImprovements") == "<ol></ol>":
                    empty_fields.append("QuickImprovements")
                if not gap.get("SkillSearchQueries"):
                    empty_fields.append("SkillSearchQueries")
                
                result = {
                    "test_number": i,
                    "timestamp": start_time.isoformat(),
                    "duration": duration,
                    "status": "success",
                    "empty_fields": empty_fields,
                    "correlation_id": response.headers.get("x-correlation-id")
                }
                
                if empty_fields:
                    print(f"  ❌ Empty fields: {', '.join(empty_fields)}")
                else:
                    print(f"  ✅ All fields OK")
                
                test_results.append(result)
            else:
                print(f"  ❌ HTTP {response.status_code}")
                test_results.append({
                    "test_number": i,
                    "timestamp": start_time.isoformat(),
                    "status": "error",
                    "status_code": response.status_code
                })
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            test_results.append({
                "test_number": i,
                "timestamp": start_time.isoformat(),
                "status": "error",
                "error": str(e)
            })
        
        time.sleep(1)  # Delay between tests

def main():
    """Main function to coordinate monitoring and testing."""
    print("Starting API monitoring and testing...")
    print("Note: Make sure uvicorn is running with proper logging")
    print("Recommended: uvicorn src.main:app --reload --log-level debug\n")
    
    # Start log monitoring in a separate thread
    # monitor_thread = threading.Thread(target=monitor_uvicorn_logs, daemon=True)
    # monitor_thread.start()
    
    # Give monitor time to start
    # time.sleep(2)
    
    # Run tests
    run_api_tests(2)
    
    # Wait a bit for logs to be captured
    time.sleep(2)
    
    # Save results
    results_dir = Path(f"monitor_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    results_dir.mkdir(exist_ok=True)
    
    # Match test results with captured logs
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    
    for test in test_results:
        print(f"\nTest {test['test_number']}:")
        print(f"  Status: {test.get('status', 'unknown')}")
        print(f"  Empty fields: {test.get('empty_fields', [])}")
        
        # Find matching log entry
        correlation_id = test.get('correlation_id')
        if correlation_id:
            matching_logs = [log for log in captured_logs if log.get('correlation_id') == correlation_id]
            if matching_logs:
                log = matching_logs[0]
                print(f"  Log captured: Yes")
                if 'raw_llm_response' in log:
                    print(f"  LLM response length: {len(log['raw_llm_response'])}")
                if 'warnings' in log:
                    print(f"  Warnings: {len(log['warnings'])}")
    
    # Save combined results
    combined_results = {
        "test_datetime": datetime.now().isoformat(),
        "test_results": test_results,
        "captured_logs": captured_logs
    }
    
    with open(results_dir / "combined_results.json", 'w') as f:
        json.dump(combined_results, f, indent=2)
    
    print(f"\nResults saved to: {results_dir}")
    
    # Note about checking server logs
    print("\n📌 To check server logs for LLM responses:")
    print("1. Look at the uvicorn console output")
    print("2. Or check Application Insights:")
    print("   az monitor app-insights query --app airesumeadvisorfastapi --analytics-query \"customEvents | where name == 'GapAnalysisEmptyFields' | take 10\"")

if __name__ == "__main__":
    main()