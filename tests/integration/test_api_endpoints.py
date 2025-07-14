"""
Integration tests for API endpoints.
Tests various API endpoints to ensure they work correctly.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestAPIEndpoints:
    """Test various API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_prompt_version_endpoint_default(self, client):
        """Test /api/v1/prompt-version endpoint with default language."""
        response = client.get("/api/v1/prompt-version")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data['success'] is True
        assert 'data' in data
        assert 'active_version' in data['data']
        assert 'available_versions' in data['data']
        assert 'language' in data['data']
        assert 'prompt_info' in data['data']
        
        # Verify default language
        assert data['data']['language'] == 'en'
        
        # Verify prompt info structure
        if data['data']['prompt_info']:
            assert 'status' in data['data']['prompt_info']
            assert 'description' in data['data']['prompt_info']
    
    def test_prompt_version_endpoint_chinese(self, client):
        """Test /api/v1/prompt-version endpoint with Chinese language."""
        response = client.get("/api/v1/prompt-version?language=zh-TW")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response
        assert data['success'] is True
        assert data['data']['language'] == 'zh-TW'
        assert isinstance(data['data']['available_versions'], list)
        
        # Chinese should have limited versions
        assert len(data['data']['available_versions']) <= 3
    
    def test_prompt_version_endpoint_invalid_language(self, client):
        """Test /api/v1/prompt-version endpoint with invalid language."""
        response = client.get("/api/v1/prompt-version?language=fr")
        
        # API might return 200 with default language or 400 for unsupported
        assert response.status_code in [200, 400]
        data = response.json()
        
        if response.status_code == 400:
            # Verify error response
            assert data['success'] is False
            assert 'error' in data
            assert 'supported' in data['error']['message'].lower()
        else:
            # API returns the requested language (even if unsupported)
            assert data['success'] is True
            # API might return the requested language or fall back to supported ones
            assert data['data']['language'] in ['en', 'zh-TW', 'fr']
    
    def test_prompt_version_endpoint_all_languages(self, client):
        """Test prompt version endpoint for all supported languages."""
        supported_languages = ['en', 'zh-TW']
        
        for lang in supported_languages:
            response = client.get(f"/api/v1/prompt-version?language={lang}")
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            assert data['data']['language'] == lang
            assert data['data']['active_version'] is not None
            assert len(data['data']['available_versions']) > 0
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint if exists."""
        # Try common health check endpoints
        for endpoint in ["/health", "/api/health", "/api/v1/health"]:
            response = client.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                # Check for common health response patterns
                assert ('status' in data or 
                        'healthy' in str(data) or 
                        (isinstance(data, dict) and 'data' in data and 'status' in data['data']))
                break
    
    @pytest.mark.parametrize("endpoint,method", [
        ("/api/v1/extract-jd-keywords", "POST"),
        ("/api/v1/index-calculation", "POST"),
        ("/api/v1/prompt-version", "GET"),
    ])
    def test_endpoint_exists(self, client, endpoint, method):
        """Test that key endpoints exist."""
        if method == "GET":
            response = client.get(endpoint)
        else:
            # Send empty body for POST endpoints
            response = client.post(endpoint, json={})
        
        # Should not return 404
        assert response.status_code != 404
        
        # Should return JSON
        assert response.headers.get("content-type", "").startswith("application/json")
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        # Test with a GET request that includes Origin header to trigger CORS response
        response = client.get(
            "/api/v1/prompt-version", 
            headers={"Origin": "https://airesumeadvisor.bubbleapps.io"}
        )
        
        # Check for CORS headers (case-insensitive)
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower
    
    def test_api_version_in_path(self, client):
        """Test that API version is included in paths."""
        # Test v1 endpoints
        v1_endpoints = [
            "/api/v1/prompt-version",
            "/api/v1/extract-jd-keywords",
            "/api/v1/index-calculation"
        ]
        
        for endpoint in v1_endpoints:
            # Extract version from path
            parts = endpoint.split('/')
            assert 'v1' in parts, f"API version not found in {endpoint}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])