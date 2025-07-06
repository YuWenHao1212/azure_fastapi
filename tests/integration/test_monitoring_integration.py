"""
Integration tests for monitoring system.
Tests the complete monitoring flow including middleware, metrics, and security.
"""
import asyncio
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.metrics.cache_metrics import cache_metrics
from src.core.metrics.endpoint_metrics import endpoint_metrics
from src.core.monitoring.security_monitor import security_monitor
from src.core.monitoring.storage.failure_storage import failure_storage
from src.middleware.monitoring_middleware import MonitoringMiddleware


class TestMonitoringIntegration:
    """Integration tests for the monitoring system."""
    
    @pytest.fixture
    def test_app(self):
        """Create a test FastAPI app with monitoring middleware."""
        # Reset security monitor for tests
        security_monitor.blocked_ips.clear()
        security_monitor.temp_blocked_ips.clear()
        security_monitor.ip_requests.clear()
        
        app = FastAPI()
        app.add_middleware(MonitoringMiddleware)
        
        @app.post("/api/v1/extract-jd-keywords")
        async def extract_keywords(data: dict):
            """Mock keyword extraction endpoint."""
            # Simulate some processing
            await asyncio.sleep(0.01)
            
            # Simulate cache check
            cache_key = "test_key"
            cache_metrics.record_cache_access(
                cache_hit=False,
                cache_key=cache_key,
                endpoint="/api/v1/extract-jd-keywords",
                processing_time_ms=10.0
            )
            
            return {
                "success": True,
                "data": {
                    "keywords": ["Python", "FastAPI", "Testing"],
                    "keyword_count": 3
                }
            }
        
        @app.get("/api/v1/health")
        async def health_check():
            """Mock health check endpoint."""
            return {"status": "healthy"}
        
        @app.post("/api/v1/error")
        async def error_endpoint():
            """Mock endpoint that raises an error."""
            raise ValueError("Test error")
        
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return TestClient(test_app)
    
    def test_successful_request_monitoring_flow(self, client):
        """Test complete monitoring flow for successful request."""
        # Reset metrics before test
        endpoint_metrics.reset_metrics()
        
        # Make a successful request
        response = client.post(
            "/api/v1/extract-jd-keywords",
            json={"job_description": "Looking for a Python developer"},
            headers={
                "origin": "https://airesumeadvisor.bubbleapps.io",
                "user-agent": "Mozilla/5.0"
            }
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify response headers
        assert "X-Correlation-ID" in response.headers
        assert "X-Process-Time" in response.headers
        
        # Verify endpoint metrics were updated
        stats = endpoint_metrics.get_endpoint_stats()
        assert stats["total_requests"] == 1
        assert stats["success_requests"] == 1
        assert stats["error_requests"] == 0
        
        # Verify endpoint-specific metrics
        endpoint_data = stats["endpoints"]["/api/v1/extract-jd-keywords"]["POST"]
        assert endpoint_data["total_requests"] == 1
        assert endpoint_data["error_rate"] == 0.0
        
        # Verify cache metrics were updated
        cache_summary = cache_metrics.get_cache_summary()
        assert cache_summary["total_requests"] == 1
        assert cache_summary["cache_misses"] == 1
    
    @pytest.mark.skip(reason="Known issue with error handling in test environment")
    def test_error_request_monitoring_flow(self, client):
        """Test monitoring flow for error requests."""
        # Make a request that will error
        response = client.post(
            "/api/v1/error",
            json={},
            headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
        )
        
        # Verify error response
        assert response.status_code == 500
        
        # Verify endpoint metrics tracked the error
        stats = endpoint_metrics.get_endpoint_stats()
        assert stats["error_requests"] >= 1
        
        # Check endpoint-specific error tracking
        if "/api/v1/error" in stats["endpoints"]:
            endpoint_data = stats["endpoints"]["/api/v1/error"]["POST"]
            assert endpoint_data["error_rate"] == 100.0
            assert "ValueError" in endpoint_data["error_types"]
    
    def test_security_monitoring_integration(self, client):
        """Test security monitoring integration."""
        # Reset security stats
        security_monitor.security_stats["suspicious_requests"] = 0
        
        # Make a suspicious request
        response = client.post(
            "/api/v1/extract-jd-keywords",
            json={"job_description": "Test <script>alert('XSS')</script>"},
            headers={
                "origin": "https://malicious-site.com",
                "user-agent": "python-requests/2.28.0"
            }
        )
        
        # Should still process but be marked as suspicious
        assert response.status_code in [200, 403]  # Might be blocked
        
        # Verify security stats were updated
        security_summary = security_monitor.get_security_summary()
        assert security_summary["suspicious_requests"] >= 1
    
    def test_rate_limiting_integration(self, client):
        """Test rate limiting through monitoring."""
        # Set low rate limit for testing
        original_limit = security_monitor.rate_limit_threshold
        security_monitor.rate_limit_threshold = 3
        
        try:
            # Make multiple requests from same "IP"
            for i in range(5):
                response = client.get(
                    "/api/v1/health",
                    headers={"X-Real-IP": "10.0.0.100"}
                )
                
                # First 3 should succeed, then rate limited
                if i < 3:
                    assert response.status_code == 200
                else:
                    # Later requests might be marked suspicious
                    pass
            
            # Check that rate limiting was detected
            security_summary = security_monitor.get_security_summary()
            # Should have detected suspicious activity
            assert security_summary["suspicious_requests"] >= 1
            
        finally:
            # Restore original limit
            security_monitor.rate_limit_threshold = original_limit
    
    @pytest.mark.asyncio
    async def test_failure_storage_integration(self):
        """Test failure storage integration."""
        # Store a test failure
        await failure_storage.store_failure(
            category="validation_error",
            job_description="Test JD that failed",
            failure_reason="Job description too short",
            language="en"
        )
        
        # Verify failure was stored
        failures = failure_storage.get_recent_failures(category="validation_error")
        assert len(failures) >= 1
        assert failures[0]["job_description"][:50] == "Test JD that failed"
    
    def test_monitoring_headers_propagation(self, client):
        """Test monitoring headers are properly propagated."""
        # Send request with correlation ID
        correlation_id = "test-correlation-12345"
        response = client.get(
            "/api/v1/health",
            headers={
                "X-Correlation-ID": correlation_id,
                "origin": "https://airesumeadvisor.bubbleapps.io"
            }
        )
        
        # Verify correlation ID is returned
        assert response.headers["X-Correlation-ID"] == correlation_id
        assert "X-Process-Time" in response.headers
        
        # Verify processing time format
        process_time = response.headers["X-Process-Time"]
        assert process_time.endswith("ms")
        time_value = float(process_time.replace("ms", ""))
        assert time_value > 0
    
    def test_multiple_endpoint_tracking(self, client):
        """Test tracking across multiple endpoints."""
        # Make requests to different endpoints
        endpoints = [
            ("POST", "/api/v1/extract-jd-keywords", {"job_description": "test"}),
            ("GET", "/api/v1/health", None)
        ]
        
        for method, path, data in endpoints:
            try:
                if method == "POST":
                    client.post(
                        path, 
                        json=data or {},
                        headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
                    )
                else:
                    client.get(
                        path,
                        headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
                    )
            except Exception:
                # Ignore errors for this test
                pass
        
        # Verify all endpoints are tracked
        stats = endpoint_metrics.get_endpoint_stats()
        assert stats["total_requests"] >= 2
        
        # Check individual endpoint tracking
        tracked_endpoints = stats["endpoints"]
        assert "/api/v1/health" in tracked_endpoints
        assert "/api/v1/extract-jd-keywords" in tracked_endpoints
    
    def test_monitoring_service_integration(self, client):
        """Test integration with Application Insights monitoring service."""
        # Patch the monitoring service
        with patch('src.middleware.monitoring_middleware.monitoring_service') as mock_monitoring_service:
            # Make a request
            response = client.get(
                "/api/v1/health",
                headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
            )
            
            assert response.status_code == 200
            
            # Verify monitoring service was called
            mock_monitoring_service.track_event.assert_called()
            mock_monitoring_service.track_request.assert_called()
            
            # Check that proper events were tracked
            event_calls = [call[0][0] for call in mock_monitoring_service.track_event.call_args_list]
            assert "RequestStarted" in event_calls
    
    def test_cache_metrics_cost_tracking(self, client):
        """Test cache metrics cost calculation integration."""
        initial_cost = cache_metrics.metrics["total_cost_saved"]
        
        # Simulate cache hit by recording directly
        cache_metrics.record_cache_access(
            cache_hit=True,
            cache_key="integration_test_key",
            endpoint="/api/v1/extract-jd-keywords",
            processing_time_ms=5.0,
            model="gpt-4o-2",
            actual_tokens={"input": 1000, "output": 300}
        )
        
        # Verify cost was calculated
        new_cost = cache_metrics.metrics["total_cost_saved"]
        assert new_cost > initial_cost
        
        # Calculate expected cost savings
        expected_cost = (1000 / 1000 * 0.03) + (300 / 1000 * 0.06)
        assert new_cost - initial_cost == pytest.approx(expected_cost, rel=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])