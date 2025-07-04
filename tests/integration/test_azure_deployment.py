"""
Integration tests for Azure Functions deployment.
Tests the FastAPI application running on Azure Functions.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import azure.functions as func
from pathlib import Path
import sys

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.integration
class TestAzureFunctionsIntegration:
    """Test Azure Functions integration with FastAPI."""
    
    @pytest.fixture
    def mock_context(self):
        """Create mock Azure Functions context."""
        context = Mock(spec=func.Context)
        context.invocation_id = "test-invocation-id"
        context.function_name = "HttpTrigger"
        context.function_directory = str(project_root / "azure")
        return context
    
    @pytest.fixture
    def mock_http_request(self):
        """Create mock HTTP request factory."""
        def _create_request(
            method="GET",
            url="/",
            headers=None,
            params=None,
            body=None,
            route_params=None
        ):
            request = Mock(spec=func.HttpRequest)
            request.method = method
            request.url = f"http://localhost:7071{url}"
            request.headers = headers or {}
            request.params = params or {}
            request.route_params = route_params or {}
            
            if body:
                if isinstance(body, dict):
                    request.get_body.return_value = json.dumps(body).encode()
                    request.get_json.return_value = body
                else:
                    request.get_body.return_value = body.encode() if isinstance(body, str) else body
                    request.get_json.side_effect = ValueError("Invalid JSON")
            else:
                request.get_body.return_value = b""
                request.get_json.side_effect = ValueError("No body")
            
            return request
        
        return _create_request
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, mock_http_request, mock_context):
        """Test health check endpoint through Azure Functions."""
        # Import the function app from project root
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Create health check request
        request = mock_http_request(
            method="GET",
            url="/health"
        )
        
        # Execute function
        response = await process_http_request(request)
        
        # Verify response
        assert response.status_code == 200
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is True
        assert response_data["data"]["status"] == "healthy"
        assert "timestamp" in response_data
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, mock_http_request, mock_context):
        """Test root endpoint through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Create root request
        request = mock_http_request(
            method="GET",
            url="/"
        )
        
        # Execute function
        response = await process_http_request(request)
        
        # Verify response
        assert response.status_code == 200
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is True
        assert response_data["data"]["name"] == "AzureFastAPIProject"
        assert response_data["data"]["api_v1"] == "/api/v1/"
    
    @pytest.mark.asyncio
    async def test_keyword_extraction_endpoint(self, mock_http_request, mock_context):
        """Test keyword extraction endpoint through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Mock the entire keyword extraction service for reliability
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            # Setup mock response in the expected format
            mock_process.return_value = {
                "keywords": ["Python", "FastAPI", "Azure", "Developer", "API", "Senior", "Technology", "Team", "Web Development", "Cloud", "Backend", "Software Engineer", "REST API", "Microservices", "Database", "Docker"],
                "keyword_count": 16,
                "standardized_terms": [],
                "confidence_score": 0.95,
                "processing_time_ms": 250,
                "extraction_method": "intersection_with_supplement",
                "intersection_stats": {
                    "intersection_count": 16,
                    "strategy_used": "intersection_with_supplement",
                    "warning": False
                },
                "detected_language": "en",
                "prompt_version_used": "1.3.0"
            }
            
            # Create keyword extraction request
            request = mock_http_request(
                method="POST",
                url="/api/v1/extract-jd-keywords",
                headers={"Content-Type": "application/json"},
                body={
                    "job_description": "We are seeking a Senior Python Developer with extensive FastAPI experience to join our technology team. The ideal candidate should have strong knowledge of web development, API design, and cloud platforms like Azure."
                }
            )
            
            # Execute function
            response = await process_http_request(request)
            
            # Verify response
            assert response.status_code == 200
            
            response_data = json.loads(response.get_body().decode())
            assert response_data["success"] is True
            assert "keywords" in response_data["data"]
            assert len(response_data["data"]["keywords"]) > 0
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, mock_http_request, mock_context):
        """Test CORS headers are properly set through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Create OPTIONS request
        request = mock_http_request(
            method="OPTIONS",
            url="/api/v1/extract-jd-keywords",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Execute function
        response = await process_http_request(request)
        
        # Verify CORS headers
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_http_request, mock_context):
        """Test error handling through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Create invalid request
        request = mock_http_request(
            method="POST",
            url="/api/v1/extract-jd-keywords",
            headers={"Content-Type": "application/json"},
            body="invalid json"
        )
        
        # Execute function
        response = await process_http_request(request)
        
        # Verify error response
        assert response.status_code == 422
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is False
        assert "error" in response_data
    
    @pytest.mark.asyncio
    async def test_method_not_allowed(self, mock_http_request, mock_context):
        """Test method not allowed handling through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Create request with unsupported method
        request = mock_http_request(
            method="DELETE",
            url="/health"  # Health endpoint only supports GET
        )
        
        # Execute function
        response = await process_http_request(request)
        
        # Verify response
        assert response.status_code == 405
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is False
    
    @pytest.mark.asyncio
    async def test_route_not_found(self, mock_http_request, mock_context):
        """Test 404 handling through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Create request to non-existent route
        request = mock_http_request(
            method="GET",
            url="/api/v1/non-existent"
        )
        
        # Execute function
        response = await process_http_request(request)
        
        # Verify response
        assert response.status_code == 404
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is False
    
    @pytest.mark.asyncio
    async def test_request_with_query_params(self, mock_http_request, mock_context):
        """Test handling query parameters through Azure Functions."""
        sys.path.insert(0, str(project_root))
        from function_app import process_http_request
        
        # Mock the keyword extraction service V2
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            # Setup mock response
            mock_process.return_value = {
                "keywords": ["Python", "Developer", "Senior", "Backend", "API", "Cloud"],
                "keyword_count": 6,
                "standardized_terms": [],
                "confidence_score": 0.90,
                "processing_time_ms": 200,
                "extraction_method": "intersection_with_supplement",
                "intersection_stats": {
                    "intersection_count": 6,
                    "strategy_used": "intersection_with_supplement", 
                    "warning": False
                },
                "detected_language": "en",
                "prompt_version_used": "1.3.0"
            }
            
            # Create request with query parameters
            request = mock_http_request(
                method="POST",
                url="/api/v1/extract-jd-keywords?max_keywords=5",
                headers={"Content-Type": "application/json"},
                params={"max_keywords": "5"},
                body={
                    "job_description": "We are seeking a Senior Python Developer with extensive experience in backend development. The ideal candidate should have strong knowledge of web development, API design, and cloud platforms."
                }
            )
            
            # Execute function
            response = await process_http_request(request)
            
            # Verify response
            assert response.status_code == 200
            
            response_data = json.loads(response.get_body().decode())
            assert response_data["success"] is True


@pytest.mark.integration
class TestAzureFunctionsConfiguration:
    """Test Azure Functions configuration."""
    
    def test_function_json_exists(self):
        """Verify function.json exists and is valid."""
        function_json_path = project_root / "function.json"
        assert function_json_path.exists()
        
        with open(function_json_path) as f:
            config = json.load(f)
        
        assert config["scriptFile"] == "function_app.py"
        assert len(config["bindings"]) == 2
        assert config["bindings"][0]["type"] == "httpTrigger"
        assert config["bindings"][0]["route"] == "{*route}"
    
    def test_host_json_exists(self):
        """Verify host.json exists and is valid."""
        host_json_path = project_root / "host.json"
        assert host_json_path.exists()
        
        with open(host_json_path) as f:
            config = json.load(f)
        
        assert config["version"] == "2.0"
    
    def test_function_app_module_exists(self):
        """Verify function_app.py exists and can be imported."""
        function_app_path = project_root / "function_app.py"
        assert function_app_path.exists()
        
        # Try to import the module
        sys.path.insert(0, str(project_root))
        import function_app
        assert hasattr(function_app, 'process_http_request')
        assert callable(function_app.process_http_request)


# Test helpers for local Azure Functions testing
def create_test_context():
    """Create a test context for Azure Functions."""
    context = Mock(spec=func.Context)
    context.invocation_id = "test-invocation-id"
    context.function_name = "HttpTrigger"
    return context


def create_test_request(method="GET", url="/", body=None, headers=None):
    """Create a test HTTP request for Azure Functions."""
    request = Mock(spec=func.HttpRequest)
    request.method = method
    request.url = f"http://localhost:7071{url}"
    request.headers = headers or {}
    
    if body:
        request.get_body.return_value = json.dumps(body).encode() if isinstance(body, dict) else body.encode()
        request.get_json.return_value = body if isinstance(body, dict) else None
    else:
        request.get_body.return_value = b""
        request.get_json.side_effect = ValueError("No body")
    
    return request