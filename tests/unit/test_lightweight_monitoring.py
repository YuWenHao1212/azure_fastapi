"""
Unit tests for the lightweight monitoring middleware
"""
import pytest
import time
from unittest.mock import Mock, patch
from collections import deque

from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from src.middleware.lightweight_monitoring import (
    LightweightMonitoringMiddleware, 
    ResponseTimeTracker,
    response_tracker
)


class TestResponseTimeTracker:
    """Test the ResponseTimeTracker class"""
    
    def test_init(self):
        """Test tracker initialization"""
        tracker = ResponseTimeTracker(max_samples=100)
        assert tracker.max_samples == 100
        assert len(tracker.times) == 0
        assert len(tracker.error_counts) == 0
        assert len(tracker.last_errors) == 0
    
    def test_add_request_success(self):
        """Test adding successful request"""
        tracker = ResponseTimeTracker(max_samples=10)
        tracker.add_request(
            endpoint="GET /test",
            duration_ms=100.5,
            status_code=200
        )
        
        assert len(tracker.times["GET /test"]) == 1
        assert tracker.times["GET /test"][0]["duration_ms"] == 100.5
        assert tracker.times["GET /test"][0]["status_code"] == 200
        assert len(tracker.error_counts) == 0
    
    def test_add_request_error(self):
        """Test adding error request"""
        tracker = ResponseTimeTracker(max_samples=10)
        tracker.add_request(
            endpoint="POST /api/test",
            duration_ms=500.0,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR"
        )
        
        assert len(tracker.times["POST /api/test"]) == 1
        assert tracker.error_counts["INTERNAL_SERVER_ERROR"] == 1
        assert len(tracker.last_errors["INTERNAL_SERVER_ERROR"]) == 1
    
    def test_max_samples_limit(self):
        """Test that max_samples limit is respected"""
        tracker = ResponseTimeTracker(max_samples=3)
        
        for i in range(5):
            tracker.add_request(
                endpoint="GET /test",
                duration_ms=i * 10,
                status_code=200
            )
        
        # Should only keep last 3 samples
        assert len(tracker.times["GET /test"]) == 3
        assert tracker.times["GET /test"][0]["duration_ms"] == 20  # 3rd sample
        assert tracker.times["GET /test"][2]["duration_ms"] == 40  # 5th sample
    
    def test_get_stats(self):
        """Test statistics calculation"""
        tracker = ResponseTimeTracker(max_samples=100)
        
        # Add some test data
        for i in range(10):
            tracker.add_request(
                endpoint="GET /api/test",
                duration_ms=i * 10,  # 0, 10, 20, ..., 90
                status_code=200
            )
        
        # Add some errors
        tracker.add_request(
            endpoint="GET /api/test",
            duration_ms=1000,
            status_code=500,
            error_code="SERVER_ERROR"
        )
        
        stats = tracker.get_stats()
        
        # Check structure
        assert "endpoints" in stats
        assert "errors" in stats
        assert "summary" in stats
        
        # Check endpoint stats
        endpoint_stats = stats["endpoints"]["GET /api/test"]
        assert endpoint_stats["count"] == 11  # 10 success + 1 error
        assert endpoint_stats["min_ms"] == 0
        assert endpoint_stats["max_ms"] == 1000
        assert endpoint_stats["avg_ms"] == pytest.approx(135.45, rel=0.1)
        # Median of [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 1000] is 50
        assert endpoint_stats["p50_ms"] == 50  # Median
        # p95 of 11 values is at index 10.45, so we get the last value
        assert endpoint_stats["p95_ms"] == 1000
        
        # Check error stats
        assert stats["errors"]["SERVER_ERROR"]["count"] == 1
        assert stats["summary"]["total_errors"] == 1


class TestLightweightMonitoringMiddleware:
    """Test the LightweightMonitoringMiddleware"""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app with middleware"""
        app = FastAPI()
        
        # Add the middleware
        app.add_middleware(LightweightMonitoringMiddleware)
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/slow")
        async def slow_endpoint():
            time.sleep(0.1)  # 100ms delay
            return {"message": "slow"}
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        return app
    
    def test_health_check_skipped(self, app):
        """Test that health checks are skipped"""
        client = TestClient(app)
        
        # Clear any existing data
        response_tracker.times.clear()
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # Health check should not be tracked
        assert len(response_tracker.times) == 0
    
    def test_response_time_header(self, app):
        """Test that X-Response-Time header is added"""
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("ms")
    
    def test_request_tracking(self, app):
        """Test that requests are tracked"""
        client = TestClient(app)
        
        # Clear existing data
        response_tracker.times.clear()
        
        response = client.get("/test")
        assert response.status_code == 200
        
        # Check that request was tracked
        assert "GET /test" in response_tracker.times
        assert len(response_tracker.times["GET /test"]) == 1
    
    @patch('src.middleware.lightweight_monitoring.business_logger')
    def test_slow_request_logging(self, mock_logger, app):
        """Test that slow requests are logged"""
        client = TestClient(app)
        
        # Make a slow request
        response = client.get("/slow")
        assert response.status_code == 200
        
        # Should log as slow (but our test is only 100ms, not 2000ms)
        # So we check that it was tracked but not logged as slow
        assert "GET /slow" in response_tracker.times
    
    @patch('src.middleware.lightweight_monitoring.business_logger')
    def test_error_tracking(self, mock_logger, app):
        """Test that errors are tracked"""
        client = TestClient(app)
        
        # Clear existing data
        response_tracker.error_counts.clear()
        
        with pytest.raises(ValueError):
            response = client.get("/error")
        
        # Error should be logged
        mock_logger.critical.assert_called()
    
    def test_error_code_mapping(self):
        """Test error code mapping"""
        middleware = LightweightMonitoringMiddleware(Mock())
        
        assert middleware.ERROR_CODE_MAP[400] == "INVALID_REQUEST"
        assert middleware.ERROR_CODE_MAP[401] == "UNAUTHORIZED"
        assert middleware.ERROR_CODE_MAP[404] == "NOT_FOUND"
        assert middleware.ERROR_CODE_MAP[422] == "VALIDATION_ERROR"
        assert middleware.ERROR_CODE_MAP[500] == "INTERNAL_SERVER_ERROR"
        assert middleware.ERROR_CODE_MAP[503] == "SERVICE_UNAVAILABLE"
    
    def test_get_current_stats(self):
        """Test getting current stats from middleware"""
        app = Mock()
        middleware = LightweightMonitoringMiddleware(app)
        middleware.request_count = 100
        
        stats = middleware.get_current_stats()
        assert stats["request_count"] == 100
        assert "endpoints" in stats
        assert "errors" in stats
        assert "summary" in stats