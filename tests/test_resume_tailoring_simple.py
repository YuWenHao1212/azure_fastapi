"""
Simple test to verify resume tailoring endpoint is working.
"""

import asyncio
import json
from httpx import AsyncClient

async def test_resume_tailoring():
    """Test the resume tailoring endpoint with a simple request"""
    
    # Test data
    request_data = {
        "job_description": """
        We are looking for a Senior Software Engineer with expertise in Python and Machine Learning.
        The ideal candidate should have experience with cloud platforms (AWS preferred), 
        containerization (Docker, Kubernetes), and building scalable ML pipelines.
        5+ years of experience required. Strong communication skills and ability to work in a team.
        """,
        "original_resume": """
        <div class="header">
            <h1>John Doe</h1>
            <p>Software Engineer | john.doe@email.com | (555) 123-4567</p>
        </div>
        <h2>Summary</h2>
        <p>Experienced software engineer with strong background in Python development and data analysis. 
        Passionate about building efficient solutions and learning new technologies.</p>
        <h2>Experience</h2>
        <div class="job">
            <h3>Software Engineer - TechCorp (2019-Present)</h3>
            <ul>
                <li>Developed Python applications for data processing and analysis</li>
                <li>Built machine learning models using TensorFlow for customer behavior prediction</li>
                <li>Collaborated with cross-functional teams to deliver features on time</li>
                <li>Mentored junior developers on Python best practices</li>
            </ul>
        </div>
        <h2>Skills</h2>
        <ul>
            <li>Programming Languages: Python, JavaScript, SQL</li>
            <li>Machine Learning: TensorFlow, Scikit-learn, Pandas</li>
            <li>Tools: Git, JIRA, VS Code, Jupyter Notebooks</li>
        </ul>
        <h2>Education</h2>
        <p>B.S. Computer Science - State University (2018)</p>
        """,
        "gap_analysis": {
            "core_strengths": [
                "Strong Python programming skills with production experience",
                "Machine learning experience with TensorFlow",
                "Team collaboration and mentoring abilities"
            ],
            "quick_improvements": [
                "Add specific metrics to achievements (e.g., improved performance by X%)",
                "Include cloud platform experience (AWS/Azure/GCP)",
                "Highlight leadership or project management experiences",
                "Add containerization skills (Docker/Kubernetes)"
            ],
            "overall_assessment": "Strong technical foundation with Python and ML. To better match the senior role, emphasize leadership experiences, add cloud/DevOps skills, and quantify achievements.",
            "covered_keywords": ["Python", "Machine Learning", "Software Engineer", "TensorFlow"],
            "missing_keywords": ["AWS", "Docker", "Kubernetes", "scalable", "pipelines", "Senior", "cloud"]
        },
        "options": {
            "include_visual_markers": True,
            "language": "en"
        }
    }
    
    # Make request
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/api/v1/tailor-resume",
            json=request_data,
            timeout=60.0  # Increase timeout for LLM call
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Basic assertions
        assert response.status_code == 200
        data = response.json()
        
        if data["success"]:
            print("\n✅ Resume tailoring successful!")
            print(f"Sections modified: {data['data']['optimization_stats']['sections_modified']}")
            print(f"Keywords added: {data['data']['optimization_stats']['keywords_added']}")
            print(f"Applied improvements: {len(data['data']['applied_improvements'])}")
            
            # Show first few improvements
            print("\nFirst 3 improvements:")
            for imp in data['data']['applied_improvements'][:3]:
                print(f"  - {imp}")
            
            # Check if markers are present
            if data['data']['visual_markers']['keyword_count'] > 0:
                print(f"\n✅ Visual markers added: {data['data']['visual_markers']['keyword_count']} keywords marked")
        else:
            print(f"\n❌ Resume tailoring failed: {data['error']['message']}")

if __name__ == "__main__":
    # Note: Make sure the FastAPI server is running before running this test
    # Run with: uvicorn src.main:app --reload
    asyncio.run(test_resume_tailoring())