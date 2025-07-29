"""
Unit tests for the error capture middleware
"""
import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.middleware.error_capture_middleware import (
    ErrorCaptureMiddleware,
    error_storage,
)


class TestErrorCaptureMiddleware:
    """Test the ErrorCaptureMiddleware"""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app with middleware"""
        app = FastAPI()
        
        # Add the middleware
        app.add_middleware(ErrorCaptureMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        @app.get("/http-error")
        async def http_error_endpoint():
            raise HTTPException(status_code=404, detail="Not found")
        
        @app.post("/validation-error")
        async def validation_error_endpoint(data: dict):
            # This will trigger validation error if wrong data is sent
            return {"data": data}
        
        return app
    
    def test_successful_request_not_captured(self, app):
        """Test that successful requests are not captured"""
        client = TestClient(app)
        
        # Clear any existing errors
        error_storage.memory_store.clear()
        
        response = client.get("/test")
        assert response.status_code == 200
        
        # No errors should be captured
        assert len(error_storage.get_recent_errors(10)) == 0
    
    def test_error_capture_500(self, app):
        """Test that 500 errors are captured"""
        client = TestClient(app)
        
        # Clear any existing errors
        error_storage.memory_store.clear()
        
        with pytest.raises(ValueError):
            response = client.get("/error")
        
        # Check that error was captured
        errors = error_storage.get_recent_errors(1)
        assert len(errors) > 0
        
        error = errors[0]
        assert error["response"]["status_code"] == 500
        assert error["request"]["endpoint"] == "/error"
        assert "ValueError: Test error" in str(error["error"])
    
    def test_error_capture_404(self, app):
        """Test that 404 errors are captured"""
        client = TestClient(app)
        
        # Clear any existing errors
        error_storage.memory_store.clear()
        
        response = client.get("/http-error")
        assert response.status_code == 404
        
        # Check that error was captured
        errors = error_storage.get_recent_errors(1)
        assert len(errors) > 0
        
        error = errors[0]
        assert error["response"]["status_code"] == 404
        assert error["request"]["endpoint"] == "/http-error"
        assert error["error"]["code"] == "HTTP_404"
    
    
    def test_error_details_captured(self, app):
        """Test that full error details are captured"""
        client = TestClient(app)
        
        # Clear any existing errors
        error_storage.memory_store.clear()
        
        # Trigger a validation error
        response = client.post("/validation-error", json="invalid")
        assert response.status_code == 422
        
        # Check captured error details
        errors = error_storage.get_recent_errors(1)
        assert len(errors) > 0
        
        error = errors[0]
        assert error["response"]["status_code"] == 422
        assert error["request"]["endpoint"] == "/validation-error"
        assert "body" in error["request"]
        assert error["request"]["method"] == "POST"
    
    def test_error_id_generation(self, app):
        """Test that unique error IDs are generated"""
        client = TestClient(app)
        
        # Clear any existing errors
        error_storage.memory_store.clear()
        
        # Generate multiple errors
        for _ in range(3):
            response = client.get("/http-error")
        
        errors = error_storage.get_recent_errors(3)
        
        # Check that we have errors
        assert len(errors) == 3
        
        # Check that each error has a unique timestamp
        timestamps = [e["timestamp"] for e in errors]
        assert len(timestamps) == len(set(timestamps))
    
    def test_request_headers_captured(self, app):
        """Test that request headers are captured"""
        client = TestClient(app)
        
        # Clear any existing errors
        error_storage.memory_store.clear()
        
        # Make request with custom headers
        headers = {
            "X-Custom-Header": "test-value",
            "User-Agent": "test-agent"
        }
        response = client.get("/http-error", headers=headers)
        
        errors = error_storage.get_recent_errors(1)
        error = errors[0]
        
        assert "headers" in error["request"]
        assert error["request"]["headers"]["user-agent"] == "test-agent"
        assert error["request"]["headers"]["x-custom-header"] == "test-value"
    
    
    def test_storage_mode_selection(self):
        """Test that correct storage mode is selected based on environment"""
        from src.core.monitoring_config import MonitoringConfig, StorageMode
        
        # Test explicit storage mode setting
        with patch.dict(os.environ, {"ERROR_STORAGE_MODE": "disk"}):
            config = MonitoringConfig()
            assert config.error_storage_mode == StorageMode.DISK
            
        with patch.dict(os.environ, {"ERROR_STORAGE_MODE": "memory"}):
            config = MonitoringConfig()
            assert config.error_storage_mode == StorageMode.MEMORY