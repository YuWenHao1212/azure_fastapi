"""
Unit tests for monitoring components.
Tests for EndpointMetrics, SecurityMonitor, and CacheMetrics.
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from collections import deque

from fastapi import Request
from starlette.datastructures import Headers

from src.core.metrics.endpoint_metrics import EndpointMetrics
from src.core.metrics.cache_metrics import CacheMetrics
from src.core.monitoring.security_monitor import SecurityMonitor


class TestEndpointMetrics:
    """Test EndpointMetrics functionality."""
    
    def test_record_request_success(self):
        """Test recording successful requests."""
        metrics = EndpointMetrics()
        
        # Record a successful request
        metrics.record_request(
            endpoint="/api/v1/extract-jd-keywords",
            method="POST",
            status_code=200,
            duration_ms=1500.0
        )
        
        # Check metrics
        endpoint_stats = metrics.get_endpoint_stats()
        
        # Check endpoint specific stats
        endpoint_key = "/api/v1/extract-jd-keywords"
        assert endpoint_key in endpoint_stats
        endpoint_data = endpoint_stats[endpoint_key]
        assert endpoint_data["total_requests"] == 1
        assert endpoint_data["error_rate"] == "0.00%"
        assert float(endpoint_data["avg_duration_ms"]) == 1500.0
    
    def test_record_request_error(self):
        """Test recording failed requests."""
        metrics = EndpointMetrics()
        
        # Record an error request
        metrics.record_request(
            endpoint="/api/v1/extract-jd-keywords",
            method="POST",
            status_code=500,
            duration_ms=500.0,
            error_type="InternalServerError"
        )
        
        # Check metrics
        endpoint_stats = metrics.get_endpoint_stats()
        
        # Check endpoint specific stats
        endpoint_key = "/api/v1/extract-jd-keywords"
        assert endpoint_key in endpoint_stats
        endpoint_data = endpoint_stats[endpoint_key]
        assert endpoint_data["total_requests"] == 1
        assert endpoint_data["error_rate"] == "100.00%"
        assert "errors_by_type" in endpoint_data
        assert endpoint_data["errors_by_type"]["InternalServerError"] == 1
    
    def test_error_rate_calculation(self):
        """Test error rate calculation across multiple requests."""
        metrics = EndpointMetrics()
        
        # Record mix of success and error requests
        for i in range(7):
            metrics.record_request(
                endpoint="/api/v1/health",
                method="GET",
                status_code=200,
                duration_ms=100.0
            )
        
        for i in range(3):
            metrics.record_request(
                endpoint="/api/v1/health",
                method="GET",
                status_code=503,
                duration_ms=50.0,
                error_type="ServiceUnavailable"
            )
        
        # Check error rate (should be 30%)
        endpoint_stats = metrics.get_endpoint_stats()
        endpoint_key = "/api/v1/health"
        assert endpoint_key in endpoint_stats
        endpoint_data = endpoint_stats[endpoint_key]
        assert endpoint_data["error_rate"] == "30.00%"
        assert endpoint_data["total_requests"] == 10
    
    def test_response_time_percentiles(self):
        """Test response time percentile calculations."""
        metrics = EndpointMetrics()
        
        # Record requests with different response times
        response_times = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        for time_ms in response_times:
            metrics.record_request(
                endpoint="/api/v1/extract-jd-keywords",
                method="POST",
                status_code=200,
                duration_ms=float(time_ms)
            )
        
        endpoint_stats = metrics.get_endpoint_stats()
        endpoint_key = "/api/v1/extract-jd-keywords"
        assert endpoint_key in endpoint_stats
        endpoint_data = endpoint_stats[endpoint_key]
        
        # Check that we have min/max/avg duration
        assert "min_duration_ms" in endpoint_data
        assert "max_duration_ms" in endpoint_data
        assert "avg_duration_ms" in endpoint_data
        
        # Check the values
        assert float(endpoint_data["min_duration_ms"]) == 100.0
        assert float(endpoint_data["max_duration_ms"]) == 1000.0
        assert float(endpoint_data["avg_duration_ms"]) == 550.0  # Average of 100-1000


class TestCacheMetrics:
    """Test CacheMetrics functionality."""
    
    def test_cache_hit_tracking(self):
        """Test cache hit tracking and cost calculation."""
        metrics = CacheMetrics()
        
        # Record a cache hit
        metrics.record_cache_access(
            cache_hit=True,
            cache_key="test_key_123",
            endpoint="/api/v1/extract-jd-keywords",
            processing_time_ms=5.0,
            model="gpt-4o-2",
            actual_tokens={"input": 800, "output": 200}
        )
        
        # Check metrics
        assert metrics.metrics["total_requests"] == 1
        assert metrics.metrics["cache_hits"] == 1
        assert metrics.metrics["cache_misses"] == 0
        assert metrics.metrics["api_calls_saved"] == 1
        
        # Check cost calculation (800 input tokens + 200 output tokens)
        expected_cost = (800 / 1000 * 0.03) + (200 / 1000 * 0.06)
        assert metrics.metrics["total_cost_saved"] == expected_cost
    
    def test_cache_miss_tracking(self):
        """Test cache miss tracking."""
        metrics = CacheMetrics()
        
        # Record a cache miss
        metrics.record_cache_access(
            cache_hit=False,
            cache_key="test_key_456",
            endpoint="/api/v1/extract-jd-keywords",
            processing_time_ms=1500.0
        )
        
        # Check metrics
        assert metrics.metrics["total_requests"] == 1
        assert metrics.metrics["cache_hits"] == 0
        assert metrics.metrics["cache_misses"] == 1
        assert metrics.metrics["api_calls_saved"] == 0
        assert metrics.metrics["total_cost_saved"] == 0.0
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        metrics = CacheMetrics()
        
        # Record 7 hits and 3 misses
        for i in range(7):
            metrics.record_cache_access(
                cache_hit=True,
                cache_key=f"key_{i}",
                endpoint="/api/v1/extract-jd-keywords"
            )
        
        for i in range(3):
            metrics.record_cache_access(
                cache_hit=False,
                cache_key=f"miss_key_{i}",
                endpoint="/api/v1/extract-jd-keywords"
            )
        
        summary = metrics.get_cache_summary()
        assert summary["hit_rate"] == "70.00%"
        assert summary["total_requests"] == 10
        assert summary["cache_hits"] == 7
        assert summary["cache_misses"] == 3
    
    @patch('src.core.metrics.cache_metrics.monitoring_service')
    def test_hourly_reporting(self, mock_monitoring_service):
        """Test hourly report generation."""
        metrics = CacheMetrics()
        
        # Get current hour
        current_hour = datetime.now(timezone.utc).hour
        
        # Add some data for current hour
        for i in range(5):
            metrics.record_cache_access(
                cache_hit=True,
                cache_key=f"key_{i}",
                endpoint="/api/v1/extract-jd-keywords",
                model="gpt-4o-2"
            )
        
        # Verify data was recorded
        assert metrics.current_hour_stats["requests"] == 5
        assert metrics.current_hour_stats["hits"] == 5
        
        # Simulate hour change by modifying the current hour
        metrics.current_hour_stats["hour"] = (current_hour - 1) % 24
        
        # Trigger hour rollover check (this happens on next access)
        metrics._check_hour_rollover()
        
        # Check that hourly stats were archived
        assert len(metrics.hourly_stats) == 1
        archived_stats = metrics.hourly_stats[0]
        assert archived_stats["requests"] == 5
        assert archived_stats["hits"] == 5
        
        # Verify hourly report was sent
        mock_monitoring_service.track_event.assert_called()
        
        # Get the call arguments
        call_args = mock_monitoring_service.track_event.call_args
        assert call_args[0][0] == "cache_hourly_report"
        
        # Check the event properties
        event_props = call_args[0][1]
        assert event_props["hour"] == (current_hour - 1) % 24
        assert event_props["hit_rate_percent"] == 100.0
        assert event_props["total_requests"] == 5
        assert event_props["hits"] == 5
        assert event_props["misses"] == 0


class TestSecurityMonitor:
    """Test SecurityMonitor functionality."""
    
    def create_mock_request(
        self, 
        method="POST", 
        path="/api/v1/extract-jd-keywords",
        headers=None,
        client_host="192.168.1.100"
    ):
        """Create a mock FastAPI Request object."""
        request = MagicMock(spec=Request)
        request.method = method
        request.url.path = path
        request.headers = Headers(headers or {})
        request.client = MagicMock()
        request.client.host = client_host
        request.body = AsyncMock(return_value=b'{"job_description": "test"}')
        return request
    
    @pytest.mark.asyncio
    async def test_valid_origin_check(self):
        """Test request from valid origin."""
        monitor = SecurityMonitor()
        
        request = self.create_mock_request(
            headers={
                "origin": "https://airesumeadvisor.bubbleapps.io",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        result = await monitor.check_request_security(request)
        
        assert not result["is_suspicious"]
        assert not result["is_blocked"]
        assert result["risk_level"] == "low"
        assert "origin" in result["checks_performed"]
    
    @pytest.mark.asyncio
    async def test_invalid_origin_detection(self):
        """Test request from invalid origin."""
        monitor = SecurityMonitor()
        
        request = self.create_mock_request(
            headers={"origin": "https://malicious-site.com"}
        )
        
        result = await monitor.check_request_security(request)
        
        assert result["is_suspicious"]
        assert not result["is_blocked"]  # Invalid origin doesn't block
        assert result["risk_level"] == "medium"
        assert "INVALID_ORIGIN" in result["threats"]
    
    @pytest.mark.asyncio
    async def test_suspicious_user_agent(self):
        """Test detection of suspicious user agents."""
        monitor = SecurityMonitor()
        
        request = self.create_mock_request(
            headers={
                "origin": "https://airesumeadvisor.bubbleapps.io",
                "user-agent": "python-requests/2.28.0"
            }
        )
        
        result = await monitor.check_request_security(request)
        
        assert result["is_suspicious"]
        assert "AUTOMATED_TOOL" in result["threats"]
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limit detection."""
        monitor = SecurityMonitor()
        monitor.rate_limit_threshold = 5  # Lower threshold for testing
        
        # Make requests from same IP
        for i in range(6):
            request = self.create_mock_request(client_host="192.168.1.100")
            result = await monitor.check_request_security(request)
        
        # The 6th request should trigger rate limit
        assert result["is_suspicious"]
        assert "RATE_LIMIT_EXCEEDED" in result["threats"]
        assert result["risk_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_xss_detection(self):
        """Test XSS attack pattern detection."""
        monitor = SecurityMonitor()
        
        request = self.create_mock_request(
            headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
        )
        # Mock malicious body content
        request.body = AsyncMock(
            return_value=b'{"job_description": "<script>alert(\'XSS\')</script>"}'
        )
        
        result = await monitor.check_request_security(request)
        
        assert result["is_suspicious"]
        assert "XSS_ATTEMPT" in result["threats"]
        assert result["risk_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_sql_injection_detection(self):
        """Test SQL injection pattern detection."""
        monitor = SecurityMonitor()
        
        request = self.create_mock_request(
            headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
        )
        # Mock SQL injection attempt
        request.body = AsyncMock(
            return_value=b'{"job_description": "test\' OR 1=1; DROP TABLE users--"}'
        )
        
        result = await monitor.check_request_security(request)
        
        assert result["is_suspicious"]
        assert "SQL_INJECTION" in result["threats"]
        assert result["risk_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_ip_blocking(self):
        """Test IP blocking functionality."""
        monitor = SecurityMonitor()
        
        # Block an IP
        monitor.block_ip("10.0.0.1")
        
        # Try request from blocked IP
        request = self.create_mock_request(client_host="10.0.0.1")
        result = await monitor.check_request_security(request)
        
        assert result["is_blocked"]
        assert result["risk_level"] == "blocked"
        assert "IP_BLOCKED" in result["threats"]
    
    @pytest.mark.asyncio
    async def test_temporary_ip_blocking(self):
        """Test temporary IP blocking."""
        monitor = SecurityMonitor()
        
        # Temporarily block an IP for 1 minute
        monitor._block_ip_temporarily("10.0.0.2", minutes=1)
        
        # Check it's blocked
        assert monitor._is_ip_blocked("10.0.0.2")
        
        # Simulate time passing
        monitor.temp_blocked_ips["10.0.0.2"] = datetime.now(timezone.utc) - timedelta(minutes=2)
        
        # Check it's unblocked
        assert not monitor._is_ip_blocked("10.0.0.2")
    
    def test_security_summary(self):
        """Test security summary generation."""
        monitor = SecurityMonitor()
        
        # Add some stats
        monitor.security_stats["total_requests"] = 100
        monitor.security_stats["suspicious_requests"] = 5
        monitor.security_stats["blocked_requests"] = 2
        monitor.security_stats["threats_by_type"]["XSS_ATTEMPT"] = 3
        monitor.security_stats["threats_by_type"]["SQL_INJECTION"] = 2
        
        summary = monitor.get_security_summary()
        
        assert summary["total_requests"] == 100
        assert summary["suspicious_requests"] == 5
        assert summary["suspicious_rate"] == "5.00%"
        assert summary["threats_detected"]["XSS_ATTEMPT"] == 3
        assert summary["threats_detected"]["SQL_INJECTION"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])