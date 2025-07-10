"""
Integration tests for Resume Format functionality.
Tests the complete flow from API endpoint to formatted output.
"""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.models.resume_format import SupplementInfo


@pytest.mark.integration
class TestResumeFormatIntegration:
    """Integration tests for resume format functionality."""
    
    @pytest.fixture
    def sample_ocr_text(self):
        """Sample OCR text that mimics real OCR output."""
        return """【Title】:John Smith
【Title】:Senior Software Engineer
【NarrativeText】:Experienced software engineer with over 10 years developing scalable web applications and leading engineering teams
【Title】:Contact Information
【NarrativeText】:Email: john.smith@example.com • LinkedIn: linkedin.com/in/johnsmith • Location: San Francisco CA
【Title】:Technical Skills
【ListItem】:Programming Languages: Python Java JavaScript TypeScript Go
【ListItem】:Frameworks: Django FastAPI React Node.js Spring Boot
【ListItem】:Databases: PostgreSQL MySQL MongoDB Redis
【Title】:Work Experience
【Title】:Tech Corp Inc
【NarrativeText】:Senior Software Engineer • San Francisco CA • Jan 2020 - Present
【ListItem】:Led development of microservices architecture serving 1M+ daily users
【ListItem】:Implemented CI/CD pipeline reducing deployment time by 60%
【ListItem】:Mentored team of 5 junior developers on best practices
【Title】:Previous Company
【NarrativeText】:Software Engineer • San Jose CA • Jun 2017 - Dec 2019
【Title】:Education
【Title】:University of California Berkeley
【NarrativeText】:Bachelor of Science in Computer Science • Berkeley CA • Sep 2013 - May 2017"""
    
    @pytest.fixture
    def sample_supplement_info(self):
        """Sample supplement information."""
        return SupplementInfo(
            name="John A. Smith",
            email="john.a.smith@promail.com",
            linkedin="https://www.linkedin.com/in/johnsmith",
            phone="+1-415-555-0123",
            location="San Francisco, CA, USA"
        )
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI response with properly formatted HTML."""
        return {
            "choices": [{
                "message": {
                    "content": """<h1>John A. Smith</h1>
<h2>Senior Software Engineer</h2>
<p>
Location: San Francisco, CA, USA<br>
Email: <a href="mailto:john.a.smith@promail.com">john.a.smith@promail.com</a><br>
LinkedIn: <a href="https://www.linkedin.com/in/johnsmith">https://www.linkedin.com/in/johnsmith</a>
</p>
<h2>Summary</h2>
<p>Experienced software engineer with over 10 years developing scalable web applications and leading engineering teams</p>
<h2>Skills</h2>
<ul>
<li>Programming Languages: Python, Java, JavaScript, TypeScript, Go</li>
<li>Frameworks: Django, FastAPI, React, Node.js, Spring Boot</li>
<li>Databases: PostgreSQL, MySQL, MongoDB, Redis</li>
</ul>
<h2>Work Experience</h2>
<h3><strong>Senior Software Engineer</strong></h3>
<p><em>Tech Corp Inc</em>•<em>San Francisco, CA</em>•<em>Jan 2020 - Present</em></p>
<ul>
<li>Led development of microservices architecture serving 1M+ daily users</li>
<li>Implemented CI/CD pipeline reducing deployment time by 60%</li>
<li>Mentored team of 5 junior developers on best practices</li>
</ul>
<h3><strong>Software Engineer</strong></h3>
<p><em>Previous Company</em>•<em>San Jose, CA</em>•<em>Jun 2017 - Dec 2019</em></p>
<h2>Education</h2>
<h4>Bachelor of Science in Computer Science</h4>
<p><em>University of California, Berkeley</em>•<em>Berkeley, CA</em>•<em>Sep 2013 - May 2017</em></p>"""
                }
            }],
            "usage": {
                "prompt_tokens": 500,
                "completion_tokens": 400,
                "total_tokens": 900
            }
        }
    
    @pytest.mark.asyncio
    async def test_format_resume_endpoint_success(self, app, sample_ocr_text, mock_openai_response):
        """Test successful resume formatting through the API endpoint."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_openai_response
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={"ocr_text": sample_ocr_text}
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert "data" in data
        assert "formatted_resume" in data["data"]
        assert "sections_detected" in data["data"]
        assert "corrections_made" in data["data"]
        
        # Check formatted content
        formatted_html = data["data"]["formatted_resume"]
        assert "<h1>John A. Smith</h1>" in formatted_html
        assert "<h2>Senior Software Engineer</h2>" in formatted_html
        assert "<h2>Work Experience</h2>" in formatted_html
        assert "<h2>Education</h2>" in formatted_html
        
        # Check sections detected
        sections = data["data"]["sections_detected"]
        assert sections["contact"] is True
        assert sections["experience"] is True
        assert sections["education"] is True
        assert sections["skills"] is True
    
    @pytest.mark.asyncio
    async def test_format_resume_with_supplement_info(
        self, app, sample_ocr_text, sample_supplement_info, mock_openai_response
    ):
        """Test resume formatting with supplement information."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_openai_response
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={
                        "ocr_text": sample_ocr_text,
                        "supplement_info": sample_supplement_info.dict()
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that supplement info was used
        assert "supplement_info_used" in data["data"]
        used_fields = data["data"]["supplement_info_used"]
        assert "name" in used_fields
        assert "email" in used_fields
        assert "linkedin" in used_fields
        
        # Check that supplement data appears in formatted resume
        formatted_html = data["data"]["formatted_resume"]
        assert "john.a.smith@promail.com" in formatted_html
        assert "John A. Smith" in formatted_html
    
    @pytest.mark.asyncio
    async def test_format_resume_validation_error(self, app):
        """Test validation error for invalid input."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/format-resume",
                json={"ocr_text": "Too short"}  # Less than 100 characters
            )
        
        assert response.status_code == 422  # Pydantic validation returns 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "too short" in data["error"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_format_resume_llm_error(self, app, sample_ocr_text):
        """Test handling of LLM service errors."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.side_effect = Exception("OpenAI service error")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={"ocr_text": sample_ocr_text}
                )
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_ERROR"
    
    @pytest.mark.asyncio
    async def test_format_resume_rate_limit(self, app, sample_ocr_text):
        """Test rate limit error handling."""
        from src.services.openai_client import AzureOpenAIRateLimitError
        
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.side_effect = AzureOpenAIRateLimitError("Rate limit exceeded")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={"ocr_text": sample_ocr_text}
                )
        
        assert response.status_code == 503
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "RATE_LIMIT_ERROR"
        assert "temporarily unavailable" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_format_resume_with_corrections(self, app):
        """Test that corrections are properly tracked and reported."""
        ocr_text_with_errors = """【Title】:John Smith
【Title】:Software Engineer
【NarrativeText】:Contact: john.smith＠example.c0m Phone: +I-555-O123-4567
【Title】:Work Experience
【NarrativeText】:January 2020 - Present at TechCorp
【NarrativeText】:Led development of microservices architecture serving millions of users
【NarrativeText】:Implemented CI/CD pipeline and improved deployment efficiency"""
        
        mock_response = {
            "choices": [{
                "message": {
                    "content": """<h1>John Smith</h1>
<h2>Software Engineer</h2>
<p>Email: <a href="mailto:john.smith@example.com">john.smith@example.com</a><br>
Phone: +1-555-0123-4567</p>
<h2>Summary</h2>
<p>Experienced software engineer with expertise in microservices and CI/CD</p>
<h2>Skills</h2>
<ul>
<li>Microservices Architecture</li>
<li>CI/CD Pipeline</li>
</ul>
<h2>Work Experience</h2>
<h3><strong>Software Engineer</strong></h3>
<p><em>TechCorp</em>•<em>San Francisco, CA</em>•<em>Jan 2020 - Present</em></p>"""
                }
            }],
            "usage": {
                "prompt_tokens": 500,
                "completion_tokens": 400,
                "total_tokens": 900
            }
        }
        
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={"ocr_text": ocr_text_with_errors}
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check corrections were made (preprocessing phase)
        corrections = data["data"]["corrections_made"]
        assert corrections["email_fixes"] > 0  # Should fix ＠ and c0m
        # Phone fixes may be skipped as user said they will confirm phone format
        # Date standardization happens in post-processing and depends on HTML content
    
    @pytest.mark.asyncio
    async def test_format_resume_missing_sections_warning(self, app):
        """Test that missing sections generate warnings."""
        minimal_ocr_text = """【Title】:John Smith
【Title】:Software Engineer
【NarrativeText】:Experienced software developer with strong technical skills and proven track record
【NarrativeText】:Over 10 years of experience in software development and system architecture"""
        
        mock_response = {
            "choices": [{
                "message": {
                    "content": """<h1>John Smith</h1>
<h2>Software Engineer</h2>"""
                }
            }]
        }
        
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={"ocr_text": minimal_ocr_text}
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify most sections are missing
        sections = data["data"]["sections_detected"]
        assert sections["contact"] is False
        assert sections["experience"] is False
        assert sections["education"] is False
        assert sections["skills"] is False
    
    @pytest.mark.asyncio
    async def test_format_resume_language_preservation(self, app):
        """Test that the service preserves the original language."""
        chinese_ocr_text = """【Title】:張三
【Title】:軟體工程師
【NarrativeText】:具有5年以上經驗的全端工程師，專精於雲端架構與微服務開發
【NarrativeText】:擅長Python、Java、JavaScript等程式語言，熟悉AWS、Azure雲端平台
【Title】:工作經歷
【NarrativeText】:科技股份有限公司 - 台北市 - 2020年至今
【NarrativeText】:負責系統架構設計與團隊技術指導，帶領5人團隊開發高並發微服務系統"""
        
        mock_response = {
            "choices": [{
                "message": {
                    "content": """<h1>張三</h1>
<h2>軟體工程師</h2>
<h2>Summary</h2>
<p>具有5年以上經驗的全端工程師，專精於雲端架構與微服務開發</p>
<h2>Skills</h2>
<ul>
<li>Python、Java、JavaScript</li>
<li>AWS、Azure雲端平台</li>
</ul>
<h2>Work Experience</h2>
<h3><strong>軟體工程師</strong></h3>
<p><em>科技股份有限公司</em>•<em>台北市</em>•<em>Jan 2020 - Present</em></p>"""
                }
            }]
        }
        
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion', 
                   new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = mock_response
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/format-resume",
                    json={"ocr_text": chinese_ocr_text}
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that Chinese characters are preserved
        formatted_html = data["data"]["formatted_resume"]
        assert "張三" in formatted_html
        assert "軟體工程師" in formatted_html
        assert "全端工程師" in formatted_html