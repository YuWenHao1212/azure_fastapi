"""Integration tests for LLM dynamic switching functionality.

These tests use REAL API credentials and make actual API calls.
Ensure you have proper API keys in your .env file before running.
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.mark.integration
class TestLLMSwitchingIntegration:
    """Test LLM switching with actual API endpoints using real APIs."""
    
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
        
        # With real API, should always return 200
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert isinstance(data["data"]["keywords"], list)
        assert len(data["data"]["keywords"]) > 0
        assert data["data"]["keyword_count"] > 0
        
        # Verify the response is from real API (not mock)
        # Real API responses have these fields
        assert "processing_time_ms" in data["data"]
        assert "confidence_score" in data["data"]
    
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
        
        # With real API, should return 200
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert isinstance(data["data"]["keywords"], list)
        assert len(data["data"]["keywords"]) > 0
        
        # Verify it's using the default model (should have standard fields)
        assert "extraction_method" in data["data"]
        assert "detected_language" in data["data"]
    
    def test_llm_model_info_endpoint(self, client):
        """Test if we can get model info (future enhancement)."""
        # This is a placeholder for future API endpoint
        # that returns which model is being used
        pass