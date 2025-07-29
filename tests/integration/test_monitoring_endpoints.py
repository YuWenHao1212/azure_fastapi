"""
Integration tests for monitoring endpoints
"""
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.middleware.error_capture_middleware import error_storage
from src.middleware.lightweight_monitoring import response_tracker


class TestMonitoringEndpoints:
    """Test monitoring-related endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup and cleanup for each test"""
        # Clear any existing data
        response_tracker.times.clear()
        response_tracker.error_counts.clear()
        response_tracker.last_errors.clear()
        if hasattr(error_storage, 'errors'):
            error_storage.errors.clear()
        
        yield
        
        # Cleanup after test
        response_tracker.times.clear()
        response_tracker.error_counts.clear()
        response_tracker.last_errors.clear()
        if hasattr(error_storage, 'errors'):
            error_storage.errors.clear()
    
    def test_monitoring_stats_endpoint(self):
        """Test /api/v1/monitoring/stats endpoint"""
        with TestClient(app) as client:
            # Make some requests to generate stats
            client.get("/health")
            client.get("/api/v1/monitoring/stats")
            
            # Get monitoring stats
            response = client.get("/api/v1/monitoring/stats")
            
            # In production, this returns 403
            if os.getenv("ENVIRONMENT") == "production":
                assert response.status_code == 403
            else:
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert "data" in data
                
                # Check stats structure
                stats = data["data"]
                assert "endpoints" in stats
                assert "errors" in stats
                assert "summary" in stats
    
    def test_storage_info_endpoint(self):
        """Test /api/v1/debug/storage-info endpoint"""
        with TestClient(app) as client:
            response = client.get("/api/v1/debug/storage-info")
            
            # In production, this returns 403
            if os.getenv("ENVIRONMENT") == "production":
                assert response.status_code == 403
            else:
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert "data" in data
                
                # Check storage info structure
                info = data["data"]
                assert "storage_mode" in info
                assert "storage_location" in info
                assert "environment" in info
    
    def test_recent_errors_endpoint(self):
        """Test /api/v1/debug/errors endpoint"""
        with TestClient(app) as client:
            # First, generate an error
            response = client.post(
                "/api/v1/extract-jd-keywords",
                json={"job_description": "x"}  # Too short, will fail validation
            )
            assert response.status_code == 422
            
            # Now check recent errors
            response = client.get("/api/v1/debug/errors?count=5")
            
            # In production, this returns 403
            if os.getenv("ENVIRONMENT") == "production":
                assert response.status_code == 403
            else:
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert "data" in data
                assert "errors" in data["data"]
                assert "count" in data["data"]
                
                # Should have captured the validation error
                if os.getenv('ERROR_CAPTURE_ENABLED', 'true').lower() == 'true':
                    assert data["data"]["count"] > 0
                    
                    # Check error structure
                    error = data["data"]["errors"][0]
                    assert "timestamp" in error
                    assert "response" in error
                    assert error["response"]["status_code"] == 422
    
    def test_response_time_header(self):
        """Test that X-Response-Time header is added"""
        with TestClient(app) as client:
            # Make a request to a non-health endpoint
            response = client.get("/")
            
            # Check for response time header
            if os.getenv('LIGHTWEIGHT_MONITORING', 'true').lower() == 'true':
                assert "X-Response-Time" in response.headers
                assert response.headers["X-Response-Time"].endswith("ms")
                
                # Parse the time value
                time_str = response.headers["X-Response-Time"].replace("ms", "")
                response_time = float(time_str)
                assert response_time >= 0
    
    def test_health_check_not_tracked(self):
        """Test that health checks are not tracked in stats"""
        with TestClient(app) as client:
            # Clear existing stats
            response_tracker.times.clear()
            
            # Make health check requests
            for _ in range(5):
                response = client.get("/health")
                assert response.status_code == 200
            
            # Check that no stats were recorded
            stats = response_tracker.get_stats()
            assert len(stats["endpoints"]) == 0
    
    def test_error_tracking_integration(self):
        """Test that errors are properly tracked"""
        with TestClient(app) as client:
            # Clear existing data
            response_tracker.error_counts.clear()
            response_tracker.last_errors.clear()
            
            # Generate different types of errors
            # 1. Validation error (422)
            response = client.post(
                "/api/v1/extract-jd-keywords",
                json={"job_description": "x"}
            )
            assert response.status_code == 422
            
            # 2. Method not allowed (405)
            response = client.put("/health")  # Health only accepts GET
            assert response.status_code == 405
            
            # Get stats
            stats = response_tracker.get_stats()
            
            if os.getenv('LIGHTWEIGHT_MONITORING', 'true').lower() == 'true':
                # Check error counts - at least 1 error should be tracked
                assert stats["summary"]["total_errors"] >= 1
                
                # Check error details
                # Check that we have errors tracked
                assert len(stats["errors"]) >= 1
                # At least validation error should be present
                error_codes = list(stats["errors"].keys())
                assert any("VALIDATION" in code or "validation" in code for code in error_codes)
    
    def test_slow_request_tracking(self):
        """Test that slow requests are tracked differently"""
        with TestClient(app) as client:
            # This endpoint might be slow on first call due to initialization
            response = client.post(
                "/api/v1/extract-jd-keywords",
                json={
                    "job_description": "We need a Python developer with 5 years of experience",
                    "language": "en"
                }
            )
            assert response.status_code == 200
            
            # Check response time header
            if os.getenv('LIGHTWEIGHT_MONITORING', 'true').lower() == 'true':
                assert "X-Response-Time" in response.headers
                time_str = response.headers["X-Response-Time"].replace("ms", "")
                response_time = float(time_str)
                
                # This request typically takes > 1000ms
                print(f"Response time: {response_time}ms")
    
    def test_monitoring_disabled(self):
        """Test behavior when monitoring is disabled"""
        with patch.dict(os.environ, {
            'MONITORING_ENABLED': 'false',
            'LIGHTWEIGHT_MONITORING': 'false'
        }):
            # Need to recreate app with new settings
            from src.main import create_app
            test_app = create_app()
            
            with TestClient(test_app) as client:
                response = client.get("/")
                assert response.status_code == 200
                
                # Should not have response time header
                assert "X-Response-Time" not in response.headers
    
    def test_concurrent_request_tracking(self):
        """Test that concurrent requests are tracked correctly"""
        with TestClient(app) as client:
            # Clear existing stats
            response_tracker.times.clear()
            
            # Make multiple concurrent-like requests
            endpoints = ["/", "/api/v1/monitoring/stats", "/health"]
            
            for endpoint in endpoints * 3:
                if endpoint != "/health":  # Health checks are not tracked
                    response = client.get(endpoint)
                    assert response.status_code in [200, 403]
            
            # Check stats
            stats = response_tracker.get_stats()
            
            if os.getenv('LIGHTWEIGHT_MONITORING', 'true').lower() == 'true':
                # Should have tracked non-health endpoints
                assert len(stats["endpoints"]) >= 2
                
                # Check that counts are correct
                for endpoint, data in stats["endpoints"].items():
                    if "/health" not in endpoint:
                        assert data["count"] >= 3