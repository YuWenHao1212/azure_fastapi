#!/usr/bin/env python3
"""Run 30 API tests in background with progress tracking"""

import requests
import json
from datetime import datetime
import time
import os

api_url = "http://localhost:8000/api/v1/index-cal-and-gap-analysis"
test_data = {
    "job_description": "We are looking for a Senior Python Developer with 5+ years of experience in FastAPI, microservices, and cloud platforms (AWS/Azure). Must have strong knowledge of Docker, Kubernetes, and CI/CD pipelines. Experience with monitoring tools and team leadership required.",
    "resume": "Backend Developer with 4 years experience in Python, REST API development, and microservices. Skilled in PostgreSQL, MongoDB, Redis. Experience with CI/CD using Jenkins and GitLab. Contributed to distributed systems serving millions of users.",
    "keywords": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "Microservices", "CI/CD", "REST API", "monitoring tools", "team leadership"],
    "language": "en"
}

# Create results directory
results_dir = f"test_30_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(results_dir, exist_ok=True)

# Progress file
progress_file = f"{results_dir}/progress.txt"

def update_progress(test_num, status, empty_fields=None):
    """Update progress file"""
    with open(progress_file, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if empty_fields:
            f.write(f"[{timestamp}] Test {test_num}/30: {status} - Empty fields: {empty_fields}\n")
        else:
            f.write(f"[{timestamp}] Test {test_num}/30: {status}\n")
        f.flush()

# Summary tracking
summary = {
    "start_time": datetime.now().isoformat(),
    "total_tests": 30,
    "completed": 0,
    "success": 0,
    "failed": 0,
    "empty_field_count": 0,
    "empty_field_details": {}
}

print(f"Starting 30 API tests at {datetime.now().strftime('%H:%M:%S')}")
print(f"Results directory: {results_dir}")
print(f"Progress file: {progress_file}")
print("="*80)

# Initial progress
update_progress(0, "Starting test run")

for i in range(1, 31):
    try:
        start = datetime.now()
        response = requests.post(api_url, json=test_data, timeout=60)
        duration = (datetime.now() - start).total_seconds()
        
        if response.status_code == 200:
            data = response.json()
            gap = data.get("data", {}).get("gap_analysis", {})
            
            # Check for empty fields
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
            
            summary["completed"] += 1
            summary["success"] += 1
            
            if empty_fields:
                summary["empty_field_count"] += 1
                for field in empty_fields:
                    summary["empty_field_details"][field] = summary["empty_field_details"].get(field, 0) + 1
                
                # Save detailed response
                with open(f"{results_dir}/test_{i:03d}_empty.json", "w") as f:
                    json.dump({
                        "test_number": i,
                        "timestamp": start.isoformat(),
                        "duration": duration,
                        "empty_fields": empty_fields,
                        "response": data
                    }, f, indent=2)
                
                update_progress(i, f"❌ EMPTY FIELDS", empty_fields)
                print(f"Test {i}: ❌ Empty fields: {', '.join(empty_fields)}")
            else:
                update_progress(i, "✅ SUCCESS")
                if i % 5 == 0:  # Print every 5th success
                    print(f"Test {i}: ✅ All fields OK (duration: {duration:.2f}s)")
        else:
            summary["completed"] += 1
            summary["failed"] += 1
            update_progress(i, f"❌ HTTP {response.status_code}")
            print(f"Test {i}: ❌ HTTP {response.status_code}")
            
    except Exception as e:
        summary["completed"] += 1
        summary["failed"] += 1
        update_progress(i, f"❌ ERROR: {str(e)}")
        print(f"Test {i}: ❌ Error: {e}")
    
    # Small delay between tests
    time.sleep(0.5)

# Final summary
summary["end_time"] = datetime.now().isoformat()
summary["total_duration"] = (datetime.now() - datetime.fromisoformat(summary["start_time"])).total_seconds()

# Save summary
with open(f"{results_dir}/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# Print final results
print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)
print(f"Total tests: {summary['total_tests']}")
print(f"Completed: {summary['completed']}")
print(f"Success: {summary['success']}")
print(f"Failed: {summary['failed']}")
print(f"Tests with empty fields: {summary['empty_field_count']}")

if summary["empty_field_details"]:
    print("\nEmpty field breakdown:")
    for field, count in summary["empty_field_details"].items():
        print(f"  - {field}: {count} times ({count/30*100:.1f}%)")

print(f"\nTotal duration: {summary['total_duration']:.2f} seconds")
print(f"Results saved to: {results_dir}")

# Final progress update
update_progress(30, f"COMPLETED - Success: {summary['success']}, Failed: {summary['failed']}, Empty: {summary['empty_field_count']}")