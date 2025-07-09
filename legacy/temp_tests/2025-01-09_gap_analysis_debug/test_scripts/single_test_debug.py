#!/usr/bin/env python3
"""
Single test to debug gap analysis empty fields issue.
"""

import requests
import json
from datetime import datetime

# API endpoint
API_URL = "http://localhost:8000/api/v1/index-cal-and-gap-analysis"

# Test data
TEST_DATA = {
    "job_description": "We are looking for a Senior Python Developer with 5+ years of experience in FastAPI, microservices, and cloud platforms (AWS/Azure). Must have strong knowledge of Docker, Kubernetes, and CI/CD pipelines. Experience with monitoring tools and team leadership required.",
    "resume": "Backend Developer with 4 years experience in Python, REST API development, and microservices. Skilled in PostgreSQL, MongoDB, Redis. Experience with CI/CD using Jenkins and GitLab. Contributed to distributed systems serving millions of users.",
    "keywords": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "Microservices", "CI/CD", "REST API"],
    "language": "en"
}

print("Starting single test debug...")
print(f"API URL: {API_URL}")
print(f"Timestamp: {datetime.now()}")
print("-" * 80)

try:
    # Make request
    print("Sending request...")
    start_time = datetime.now()
    response = requests.post(API_URL, json=TEST_DATA, timeout=60)
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"Response received in {duration:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check gap analysis fields
        gap_analysis = data.get("data", {}).get("gap_analysis", {})
        
        print("\nGap Analysis Fields:")
        for field in ["CoreStrengths", "KeyGaps", "QuickImprovements", "OverallAssessment", "SkillSearchQueries"]:
            value = gap_analysis.get(field)
            if field == "SkillSearchQueries":
                print(f"  - {field}: {len(value) if value else 0} items")
            else:
                if value in ["<p></p>", "<ol></ol>", "", None]:
                    print(f"  - {field}: ❌ EMPTY (value: '{value}')")
                else:
                    print(f"  - {field}: ✓ Has content ({len(value)} chars)")
        
        # Save full response
        with open("single_test_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\nFull response saved to: single_test_response.json")
        
        # Print OverallAssessment specifically
        overall = gap_analysis.get("OverallAssessment", "")
        print(f"\nOverallAssessment value: '{overall}'")
        
    else:
        print(f"Error response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()