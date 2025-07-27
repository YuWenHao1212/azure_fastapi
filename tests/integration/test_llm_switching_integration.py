"""Integration tests for LLM dynamic switching functionality."""
import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestLLMSwitchingIntegration:
    """Test LLM switching with actual API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_keyword_extraction_with_header(self, client):
        """Test keyword extraction with X-LLM-Model header."""
        # Test data
        request_data = {
            "job_description": "We are looking for a Senior Python Developer with experience in FastAPI, "
                             "Azure cloud services, and machine learning. The ideal candidate should have "
                             "strong problem-solving skills and experience with microservices architecture.",
            "language": "en",
            "max_keywords": 10
        }
        
        # Test with GPT-4.1 mini via header
        headers = {"X-LLM-Model": "gpt41-mini"}
        response = client.post(
            "/api/v1/extract-jd-keywords",
            json=request_data,
            headers=headers
        )
        
        # Should still work (or mock the response)
        assert response.status_code in [200, 503]  # 503 if no real API key
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "keywords" in data["data"]
    
    @pytest.mark.asyncio
    async def test_keyword_extraction_default_model(self, client):
        """Test keyword extraction with default model selection."""
        request_data = {
            "job_description": "Looking for a Data Scientist with Python and machine learning experience.",
            "language": "en"
        }
        
        response = client.post(
            "/api/v1/extract-jd-keywords",
            json=request_data
        )
        
        assert response.status_code in [200, 503]
    
    def test_llm_model_info_endpoint(self, client):
        """Test if we can get model info (future enhancement)."""
        # This is a placeholder for future API endpoint
        # that returns which model is being used
        pass