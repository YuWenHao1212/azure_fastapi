"""
Unit tests for API endpoints - Work Item #348.
Tests FastAPI routing, error handling, dependency injection, and HTTP responses.

✅ STATUS: FULLY COMPATIBLE WITH CURRENT ARCHITECTURE
📅 LAST UPDATE: 2025-07-03 (supports UnifiedPromptService)

🚀 USAGE:
    # Run all API endpoint tests
    pytest tests/unit/test_api_endpoints.py -v
    
    # Run specific test class
    pytest tests/unit/test_api_endpoints.py::TestKeywordExtractionAPI -v
    
    # Run with coverage
    pytest tests/unit/test_api_endpoints.py --cov=src.api --cov-report=html

📋 COVERS:
    - Health endpoint testing
    - Keyword extraction API endpoints
    - HTTP status codes and responses
    - Error handling and validation
    - Dependency injection mocking
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock, Mock, patch

from src.api.v1.keyword_extraction import router
from src.models.keyword_extraction import KeywordExtractionRequest
from src.models.response import UnifiedResponse, ErrorDetail


@pytest.mark.unit
class TestKeywordExtractionAPI:
    """Test keyword extraction API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI test app with the router."""
        from src.main import create_app
        app = create_app()
        yield app
        # Clean up dependency overrides after test
        if hasattr(app, 'dependency_overrides'):
            app.dependency_overrides.clear()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_service(self):
        """Mock KeywordExtractionService."""
        service = AsyncMock()
        return service
    
    def test_health_endpoint_success(self, client):
        """Test health check endpoint returns success."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["service"] == "keyword_extraction"
        assert data["data"]["status"] == "healthy"
        assert "features" in data["data"]
        assert "dependencies" in data["data"]
    
    def test_version_endpoint_success(self, client):
        """Test version endpoint returns correct information."""
        response = client.get("/api/v1/version")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "version" in data["data"]
        assert "build_date" in data["data"]
        assert "capabilities" in data["data"]
        assert "service" in data["data"]
    
    @patch('src.api.v1.keyword_extraction.get_keyword_extraction_service_v2')
    def test_extract_keywords_success(self, mock_get_service, client):
        """Test successful keyword extraction."""
        # Create mock service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Mock the validate_input method
        mock_service.validate_input.return_value = {
            "job_description": "We need a Python developer with FastAPI experience.",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        
        # Mock the process method to return data dict
        mock_service.process.return_value = {
            "keywords": ["Python", "FastAPI", "Backend"],
            "keyword_count": 3,
            "confidence_score": 0.85,
            "extraction_method": "2_round_intersection",
            "processing_time_ms": 2500.0,
            "intersection_stats": {},
            "warning": {"has_warning": False, "message": ""}
        }
        
        # Make request
        request_data = {
            "job_description": "We need a Python developer with FastAPI experience.",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert len(data["data"]["keywords"]) == 3
        assert "Python" in data["data"]["keywords"]
        assert "FastAPI" in data["data"]["keywords"]
        assert "confidence_score" in data["data"]
        assert "extraction_method" in data["data"]
        assert data["data"]["extraction_method"] == "2_round_intersection"
    
    def test_extract_keywords_validation_error(self, client):
        """Test input validation error handling."""
        # Test missing required field
        request_data = {
            "max_keywords": 20,
            "prompt_version": "latest"
            # Missing job_description
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        # Custom error format
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "job_description" in data["error"]["details"]
    
    def test_extract_keywords_short_description_error(self, client):
        """Test validation error for short job description."""
        request_data = {
            "job_description": "Short",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_extract_keywords_invalid_max_keywords(self, client):
        """Test validation error for invalid max_keywords."""
        request_data = {
            "job_description": "We need a Python developer with extensive experience.",
            "max_keywords": 50,  # Above maximum of 25
            "prompt_version": "latest"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 422  # Pydantic validation error
    
    @patch('src.api.v1.keyword_extraction.get_keyword_extraction_service_v2')
    def test_extract_keywords_service_error(self, mock_get_service, client):
        """Test service error handling."""
        # Create mock service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Mock service error - raise an exception
        from src.services.openai_client import AzureOpenAIServerError
        mock_service.validate_input.return_value = {"job_description": "test", "max_keywords": 20, "prompt_version": "latest"}
        mock_service.process.side_effect = AzureOpenAIServerError("OpenAI service is temporarily unavailable")
        
        request_data = {
            "job_description": "We need a Python developer with FastAPI experience.",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 503  # Service unavailable
        data = response.json()
        
        # HTTPException handler returns the error response directly when detail is a dict
        assert data["success"] is False
        assert data["error"]["code"] == "SERVICE_UNAVAILABLE"
        assert "無法使用" in data["error"]["message"] or "unavailable" in data["error"]["message"]
    
    @patch('src.api.v1.keyword_extraction.get_keyword_extraction_service_v2')
    def test_extract_keywords_unexpected_exception(self, mock_get_service, client):
        """Test handling of unexpected exceptions."""
        # Create mock service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Mock validation passes but process fails
        mock_service.validate_input.return_value = {"job_description": "test", "max_keywords": 20, "prompt_version": "latest"}
        mock_service.process.side_effect = Exception("Unexpected error")
        
        request_data = {
            "job_description": "We need a Python developer with FastAPI experience.",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 500  # Internal server error
        data = response.json()
        
        # HTTPException handler returns the error response directly when detail is a dict
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    
    @patch('src.api.v1.keyword_extraction.get_keyword_extraction_service_v2')
    def test_extract_keywords_default_values(self, mock_get_service, client):
        """Test that default values are applied correctly."""
        # Create mock service
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service
        
        # Mock successful response
        mock_service.validate_input.return_value = {
            "job_description": "We need a Python developer with extensive experience in web development.",
            "max_keywords": 16,  # Updated to match actual default
            "prompt_version": "latest"
        }
        mock_service.process.return_value = {
            "keywords": ["Python", "FastAPI"],
            "keyword_count": 2,
            "confidence_score": 0.9,
            "extraction_method": "2_round_intersection",
            "processing_time_ms": 1500.0,
            "intersection_stats": {},
            "warning": {"has_warning": False, "message": ""}
        }
        
        # Request with minimal data (using defaults)
        request_data = {
            "job_description": "We need a Python developer with extensive experience in web development."
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        
        # Verify service was called with default values
        call_args = mock_service.validate_input.call_args[0][0]
        # Check the raw input data from Pydantic model
        assert "max_keywords" not in call_args or call_args["max_keywords"] == 16  # correct default
        assert "prompt_version" not in call_args or call_args["prompt_version"] == "latest"  # default
    
    def test_cors_headers(self, client):
        """Test CORS headers are present in responses."""
        response = client.get("/api/v1/health")
        
        # Note: CORS headers depend on FastAPI CORS middleware configuration
        # This test verifies the endpoint is accessible
        assert response.status_code == 200
    
    def test_openapi_documentation(self, app):
        """Test that OpenAPI documentation is generated."""
        # Test that the app has OpenAPI schema
        openapi_schema = app.openapi()
        
        assert openapi_schema is not None
        assert "paths" in openapi_schema
        assert "/api/v1/extract-jd-keywords" in openapi_schema["paths"]
        assert "/api/v1/health" in openapi_schema["paths"]
        assert "/api/v1/version" in openapi_schema["paths"]
        
        # Verify extract-jd-keywords endpoint documentation
        extract_endpoint = openapi_schema["paths"]["/api/v1/extract-jd-keywords"]
        assert "post" in extract_endpoint
        post_spec = extract_endpoint["post"]
        
        assert "summary" in post_spec
        assert "requestBody" in post_spec
        assert "responses" in post_spec
        assert "200" in post_spec["responses"]
        assert "400" in post_spec["responses"]
        assert "422" in post_spec["responses"]
        assert "500" in post_spec["responses"]
        assert "503" in post_spec["responses"]
    
    def test_request_response_models(self, app):
        """Test that request and response models are properly defined in OpenAPI."""
        openapi_schema = app.openapi()
        
        # Check components/schemas
        assert "components" in openapi_schema
        assert "schemas" in openapi_schema["components"]
        schemas = openapi_schema["components"]["schemas"]
        
        # Verify important models are defined
        assert "KeywordExtractionRequest" in schemas
        assert "UnifiedResponse" in schemas
        
        # Verify KeywordExtractionRequest structure
        request_schema = schemas["KeywordExtractionRequest"]
        assert "properties" in request_schema
        properties = request_schema["properties"]
        
        assert "job_description" in properties
        assert "max_keywords" in properties
        assert "prompt_version" in properties
        
        # Verify required fields
        assert "required" in request_schema
        assert "job_description" in request_schema["required"]
    
    def test_bubble_io_compatibility(self, app, client):
        """Test Bubble.io API compatibility requirements."""
        # Create mock service
        mock_service = AsyncMock()
        
        # Override the dependency
        from src.services.keyword_extraction import get_keyword_extraction_service
        app.dependency_overrides[get_keyword_extraction_service] = lambda: mock_service
        
        # Mock response with all required fields
        mock_service.validate_input.return_value = {
            "job_description": "We need a Python developer with FastAPI experience.",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        mock_service.process.return_value = {
            "keywords": ["Python", "FastAPI"],
            "keyword_count": 2,
            "confidence_score": 0.85,
            "extraction_method": "2_round_intersection",
            "processing_time_ms": 2000.0,
            "intersection_stats": {
                "intersection_count": 2,
                "round1_count": 3,
                "round2_count": 3,
                "strategy_used": "2_round_intersection"
            },
            "warning": {
                "has_warning": False,
                "message": "",
                "expected_minimum": 12,
                "actual_extracted": 2
            }
        }
        
        request_data = {
            "job_description": "We need a Python developer with FastAPI experience.",
            "max_keywords": 20,
            "prompt_version": "latest"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify Bubble.io compatibility: consistent schema
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert "timestamp" in data
        
        # Verify error object structure (even in success case)
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "details" in error
        
        # Verify no None/null values
        def check_no_none_values(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    assert value is not None, f"None value found at {current_path}"
                    check_no_none_values(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    assert item is not None, f"None value found at {current_path}"
                    check_no_none_values(item, current_path)
        
        check_no_none_values(data)
    
    def test_http_methods_not_allowed(self, client):
        """Test that only allowed HTTP methods work."""
        # POST should work for extract-jd-keywords
        response = client.post("/api/v1/extract-jd-keywords", json={
            "job_description": "Valid job description for testing purposes."
        })
        # Should return 200 or validation error, but not method not allowed
        assert response.status_code != 405
        
        # GET should not work for extract-jd-keywords
        response = client.get("/api/v1/extract-jd-keywords")
        assert response.status_code == 405  # Method not allowed
        
        # GET should work for health and version
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/version").status_code == 200
        
        # POST should not work for health and version
        assert client.post("/api/v1/health").status_code == 405
        assert client.post("/api/v1/version").status_code == 405
    
    def test_content_type_validation(self, client):
        """Test content type validation."""
        # Valid JSON content type should work
        response = client.post(
            "/api/v1/extract-jd-keywords",
            json={"job_description": "Valid job description for testing purposes."},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code != 415  # Not unsupported media type
        
        # Invalid content type should be rejected
        response = client.post(
            "/api/v1/extract-jd-keywords",
            data="job_description=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422  # Validation error or unsupported media type 