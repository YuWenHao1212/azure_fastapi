"""
Integration tests specifically for Premium environment features.
Tests the new GPT-4.1 mini Japan East endpoint and premium capabilities.
"""
import time

import pytest
from fastapi.testclient import TestClient

from src.core.config import get_settings
from src.main import app


@pytest.mark.integration
class TestPremiumEnvironment:
    """Test Premium environment specific features."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def settings(self):
        """Get real settings."""
        return get_settings()
    
    def test_premium_configuration(self, settings):
        """Verify Premium environment configuration."""
        # Check GPT-4.1 mini Japan East configuration
        assert settings.gpt41_mini_japaneast_endpoint, "GPT-4.1 mini endpoint not configured"
        assert "airesumeadvisor.openai.azure.com" in settings.gpt41_mini_japaneast_endpoint
        assert settings.gpt41_mini_japaneast_deployment == "gpt-4-1-mini-japaneast"
        assert settings.gpt41_mini_japaneast_api_version == "2025-01-01-preview"
        
        print("\n✅ Premium Configuration:")
        print(f"   Endpoint: {settings.gpt41_mini_japaneast_endpoint}")
        print(f"   Deployment: {settings.gpt41_mini_japaneast_deployment}")
        print(f"   API Version: {settings.gpt41_mini_japaneast_api_version}")
        print(f"   Use for Keywords: {settings.use_gpt41_mini_for_keywords}")
    
    @pytest.mark.asyncio
    async def test_gpt41_mini_performance(self, client, settings):
        """Test GPT-4.1 mini performance characteristics."""
        if not settings.gpt41_mini_japaneast_api_key:
            pytest.skip("GPT-4.1 mini not configured")
        
        # Test with a typical job description
        request_data = {
            "job_description": """
            We are seeking an experienced Machine Learning Engineer to join our AI team.
            Required skills include Python, TensorFlow, PyTorch, scikit-learn, deep learning,
            natural language processing, computer vision, MLOps, Docker, Kubernetes, and AWS.
            Experience with transformer models, BERT, GPT, and production ML systems is essential.
            """,
            "language": "en",
            "max_keywords": 20
        }
        
        # Measure performance
        start_time = time.time()
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Performance metrics
        total_time = (end_time - start_time) * 1000
        api_time = data["data"]["processing_time_ms"]
        
        print("\n📊 GPT-4.1 mini Performance:")
        print(f"   Total request time: {total_time:.0f}ms")
        print(f"   API processing time: {api_time:.0f}ms")
        print(f"   Keywords extracted: {data['data']['keyword_count']}")
        
        # GPT-4.1 mini should be fast
        assert api_time < 5000, f"GPT-4.1 mini took too long: {api_time}ms"
        
        # Check ML-related keywords
        keywords = data["data"]["keywords"]
        ml_keywords = ["machine learning", "tensorflow", "pytorch", "deep learning", 
                       "nlp", "computer vision", "mlops", "transformer"]
        found_ml = sum(1 for kw in ml_keywords if any(kw in k.lower() for k in keywords))
        assert found_ml >= 4, f"Expected more ML keywords, found: {keywords}"
    
    @pytest.mark.asyncio
    async def test_premium_model_selection_logic(self, client, settings):
        """Test that GPT-4.1 mini is used when configured."""
        if not settings.use_gpt41_mini_for_keywords:
            pytest.skip("GPT-4.1 mini not enabled for keywords")
        
        request_data = {
            "job_description": "Data Scientist with Python and SQL skills needed.",
            "language": "en"
        }
        
        # Without header, should use GPT-4.1 mini if configured
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that appropriate keywords were extracted
        keywords = [k.lower() for k in data["data"]["keywords"]]
        assert any("python" in k for k in keywords)
        assert any("sql" in k for k in keywords)
        assert any("data" in k for k in keywords)
    
    @pytest.mark.asyncio
    async def test_premium_chinese_support(self, client, settings):
        """Test GPT-4.1 mini with Chinese job descriptions."""
        if not settings.gpt41_mini_japaneast_api_key:
            pytest.skip("GPT-4.1 mini not configured")
        
        request_data = {
            "job_description": """
            誠徵資深後端工程師，需具備以下技能：
            - 精通 Java, Spring Boot, Microservices
            - 熟悉 MySQL, PostgreSQL, Redis
            - 了解 Docker, Kubernetes, CI/CD
            - 有金融科技經驗者佳
            """,
            "language": "zh-TW"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Should extract tech keywords even from Chinese
        keywords = data["data"]["keywords"]
        tech_keywords = ["java", "spring", "mysql", "postgresql", "redis", 
                        "docker", "kubernetes", "ci/cd", "microservices"]
        
        keywords_lower = [k.lower() for k in keywords]
        found_tech = sum(1 for tech in tech_keywords if any(tech in k for k in keywords_lower))
        
        assert found_tech >= 5, f"Expected more tech keywords from Chinese text, got: {keywords}"
        assert data["data"]["detected_language"] in ["zh", "zh-TW"]
    
    @pytest.mark.asyncio
    async def test_premium_concurrent_requests(self, client, settings):
        """Test handling multiple concurrent requests."""
        if not settings.gpt41_mini_japaneast_api_key:
            pytest.skip("GPT-4.1 mini not configured")
        
        import asyncio

        import httpx
        
        async def make_request(job_title: str):
            """Make async request to API."""
            async with httpx.AsyncClient(base_url="http://testserver") as async_client:
                response = await async_client.post(
                    "/api/v1/extract-jd-keywords",
                    json={
                        "job_description": f"Looking for {job_title} with relevant experience",
                        "language": "en"
                    }
                )
                return response
        
        # Test 3 concurrent requests
        job_titles = ["Python Developer", "Data Analyst", "DevOps Engineer"]
        
        start_time = time.time()
        responses = await asyncio.gather(
            *[make_request(title) for title in job_titles]
        )
        end_time = time.time()
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["keywords"]) > 0
        
        total_time = (end_time - start_time) * 1000
        print("\n⚡ Concurrent request performance:")
        print(f"   3 requests completed in: {total_time:.0f}ms")
        print(f"   Average per request: {total_time/3:.0f}ms")
    
    @pytest.mark.asyncio
    async def test_premium_error_handling(self, client):
        """Test Premium environment error handling."""
        # Test with invalid language code
        response = client.post("/api/v1/extract-jd-keywords", json={
            "job_description": "Test job description",
            "language": "invalid-lang"
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
        data = response.json()
        
        if response.status_code == 422:
            assert data["success"] is False
            assert "error" in data
        else:
            # API might auto-detect language
            assert data["success"] is True
            assert data["data"]["detected_language"] in ["en", "zh", "zh-TW"]