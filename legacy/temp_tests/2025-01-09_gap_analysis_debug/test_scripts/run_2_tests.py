#!/usr/bin/env python3
"""Run 2 API tests to check LLM logging"""

import requests
import json
from datetime import datetime
import time

api_url = "http://localhost:8000/api/v1/index-cal-and-gap-analysis"
test_data = {
    "job_description": "We are looking for a Senior Python Developer with 5+ years of experience in FastAPI, microservices, and cloud platforms (AWS/Azure). Must have strong knowledge of Docker, Kubernetes, and CI/CD pipelines. Experience with monitoring tools and team leadership required.",
    "resume": "Backend Developer with 4 years experience in Python, REST API development, and microservices. Skilled in PostgreSQL, MongoDB, Redis. Experience with CI/CD using Jenkins and GitLab. Contributed to distributed systems serving millions of users.",
    "keywords": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "Microservices", "CI/CD", "REST API", "monitoring tools", "team leadership"],
    "language": "en"
}

print("Running 2 API tests...")
print("="*80)

for i in range(1, 3):
    print(f"\n🔄 Test {i}/2 at {datetime.now().strftime('%H:%M:%S')}...")
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
            
            print(f"  Duration: {duration:.2f}s")
            print(f"  Correlation ID: {response.headers.get('x-correlation-id', 'N/A')}")
            
            if empty_fields:
                print(f"  ❌ Empty fields: {', '.join(empty_fields)}")
                # Save response for debugging
                with open(f"empty_response_test_{i}.json", "w") as f:
                    json.dump(data, f, indent=2)
            else:
                print(f"  ✅ All fields OK")
                print(f"  - OverallAssessment length: {len(gap.get('OverallAssessment', ''))}")
        else:
            print(f"  ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(2)

print("\n✅ Tests completed!")
print("\n📋 To check uvicorn logs for LLM responses:")
print("   grep '[GAP_ANALYSIS_LLM]' uvicorn_full_log.txt")
print("   grep '[GAP_ANALYSIS]' uvicorn_full_log.txt | grep -v preview")