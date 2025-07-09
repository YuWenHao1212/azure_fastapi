#!/bin/bash

echo "=== API Testing with Uvicorn Logging ==="
echo "This script will:"
echo "1. Stop current uvicorn"
echo "2. Start uvicorn with logging"
echo "3. Run API tests"
echo ""

# Step 1: Kill existing uvicorn
echo "Step 1: Stopping existing uvicorn..."
pkill -f "uvicorn src.main:app"
sleep 2

# Step 2: Start uvicorn with logging in background
echo "Step 2: Starting uvicorn with info logging..."
echo "Log file: uvicorn_test_log.txt"
nohup uvicorn src.main:app --reload --log-level info --host 0.0.0.0 --port 8000 > uvicorn_test_log.txt 2>&1 &
UVICORN_PID=$!
echo "Uvicorn started with PID: $UVICORN_PID"

# Wait for uvicorn to start
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start"
        exit 1
    fi
    sleep 1
done

# Step 3: Run tests
echo ""
echo "Step 3: Running 2 API tests..."
python3 << 'EOF'
import requests
import json
from datetime import datetime

api_url = "http://localhost:8000/api/v1/index-cal-and-gap-analysis"
test_data = {
    "job_description": "We are looking for a Senior Python Developer with 5+ years of experience in FastAPI, microservices, and cloud platforms (AWS/Azure). Must have strong knowledge of Docker, Kubernetes, and CI/CD pipelines. Experience with monitoring tools and team leadership required.",
    "resume": "Backend Developer with 4 years experience in Python, REST API development, and microservices. Skilled in PostgreSQL, MongoDB, Redis. Experience with CI/CD using Jenkins and GitLab. Contributed to distributed systems serving millions of users.",
    "keywords": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS", "Microservices", "CI/CD", "REST API", "monitoring tools", "team leadership"],
    "language": "en"
}

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
    
    import time
    time.sleep(2)

print("\n✅ Tests completed!")
EOF

echo ""
echo "=== Checking Uvicorn Logs ==="
echo "Looking for gap analysis related logs..."
echo ""

# Check for specific log patterns
grep -n "\[GAP_ANALYSIS\]" uvicorn_test_log.txt | tail -20 || echo "No [GAP_ANALYSIS] logs found"
echo ""
grep -n "Empty fields detected" uvicorn_test_log.txt || echo "No empty fields detected in logs"
echo ""
grep -n "Warning.*assessment" uvicorn_test_log.txt || echo "No assessment warnings found"

echo ""
echo "=== Summary ==="
echo "- Uvicorn PID: $UVICORN_PID"
echo "- Log file: uvicorn_test_log.txt"
echo "- To see full logs: tail -f uvicorn_test_log.txt"
echo "- To stop uvicorn: kill $UVICORN_PID"