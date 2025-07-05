"""
Unit tests for monitoring middleware.
Tests request/response tracking and security integration.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

from src.middleware.monitoring_middleware import MonitoringMiddleware


class TestMonitoringMiddleware:
    """Test MonitoringMiddleware functionality."""
    
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
        request.url = MagicMock()
        request.url.path = path
        request.url.query = ""
        request.headers = Headers(headers or {})
        request.client = MagicMock()
        request.client.host = client_host
        request.state = MagicMock()
        return request
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    @patch('src.middleware.monitoring_middleware.endpoint_metrics')
    async def test_successful_request_tracking(
        self, 
        mock_endpoint_metrics,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test middleware tracking for successful requests."""
        # Setup mocks
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": False,
            "is_suspicious": False,
            "risk_level": "low",
            "threats": [],
            "client_ip": "192.168.1.100"
        })
        
        # Create middleware and mock app
        middleware = MonitoringMiddleware(MagicMock())
        
        # Create mock request and response
        request = self.create_mock_request(
            headers={"origin": "https://airesumeadvisor.bubbleapps.io"}
        )
        
        # Mock call_next to return a successful response
        async def mock_call_next(req):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response
        
        # Execute middleware
        response = await middleware.dispatch(request, mock_call_next)
        
        # Verify security check was called
        mock_security_monitor.check_request_security.assert_called_once()
        
        # Verify monitoring service was called
        mock_monitoring_service.track_event.assert_called()
        mock_monitoring_service.track_request.assert_called_once()
        
        # Verify endpoint metrics were recorded
        mock_endpoint_metrics.record_request.assert_called_once()
        call_args = mock_endpoint_metrics.record_request.call_args[1]
        assert call_args["endpoint"] == "/api/v1/extract-jd-keywords"
        assert call_args["method"] == "POST"
        assert call_args["status_code"] == 200
        
        # Verify response headers
        assert "X-Correlation-ID" in response.headers
        assert "X-Process-Time" in response.headers
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    async def test_blocked_request(
        self,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test middleware behavior for blocked requests."""
        # Setup security monitor to block request
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": True,
            "is_suspicious": True,
            "risk_level": "blocked",
            "threats": ["IP_BLOCKED"],
            "client_ip": "10.0.0.1"
        })
        
        # Create middleware
        middleware = MonitoringMiddleware(MagicMock())
        
        # Create request from blocked IP
        request = self.create_mock_request(client_host="10.0.0.1")
        
        # Mock call_next (shouldn't be called for blocked requests)
        mock_call_next = AsyncMock()
        
        # Execute middleware
        response = await middleware.dispatch(request, mock_call_next)
        
        # Verify request was blocked
        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        
        # Verify call_next was NOT called
        mock_call_next.assert_not_called()
        
        # Verify blocked event was tracked
        mock_monitoring_service.track_event.assert_called_with(
            "request_blocked",
            {
                "client_ip": "10.0.0.1",
                "threats": ["IP_BLOCKED"]
            }
        )
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    @patch('src.middleware.monitoring_middleware.endpoint_metrics')
    async def test_error_request_tracking(
        self,
        mock_endpoint_metrics,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test middleware tracking for error responses."""
        # Setup mocks
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": False,
            "is_suspicious": False,
            "risk_level": "low",
            "threats": [],
            "client_ip": "192.168.1.100"
        })
        
        # Create middleware
        middleware = MonitoringMiddleware(MagicMock())
        
        # Create request
        request = self.create_mock_request()
        
        # Mock call_next to raise an exception
        async def mock_call_next(req):
            raise ValueError("Test error")
        
        # Execute middleware and expect exception
        with pytest.raises(ValueError, match="Test error"):
            await middleware.dispatch(request, mock_call_next)
        
        # Verify error was tracked
        mock_monitoring_service.track_error.assert_called_once()
        error_call = mock_monitoring_service.track_error.call_args[1]
        assert error_call["error_type"] == "ValueError"
        assert error_call["error_message"] == "Test error"
        
        # Verify endpoint metrics recorded the error
        mock_endpoint_metrics.record_request.assert_called_once()
        metrics_call = mock_endpoint_metrics.record_request.call_args[1]
        assert metrics_call["status_code"] == 500
        assert metrics_call["error_type"] == "ValueError"
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    async def test_correlation_id_handling(
        self,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test correlation ID generation and propagation."""
        # Setup mocks
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": False,
            "is_suspicious": False,
            "risk_level": "low",
            "threats": [],
            "client_ip": "192.168.1.100"
        })
        
        # Create middleware
        middleware = MonitoringMiddleware(MagicMock())
        
        # Test with provided correlation ID
        provided_correlation_id = "test-correlation-123"
        request = self.create_mock_request(
            headers={"X-Correlation-ID": provided_correlation_id}
        )
        
        async def mock_call_next(req):
            # Verify correlation ID was set on request state
            assert req.state.correlation_id == provided_correlation_id
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response
        
        response = await middleware.dispatch(request, mock_call_next)
        
        # Verify correlation ID in response
        assert response.headers["X-Correlation-ID"] == provided_correlation_id
        
        # Test without provided correlation ID
        request_no_id = self.create_mock_request()
        
        async def mock_call_next_no_id(req):
            # Verify a correlation ID was generated
            assert hasattr(req.state, 'correlation_id')
            assert req.state.correlation_id is not None
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response
        
        response = await middleware.dispatch(request_no_id, mock_call_next_no_id)
        
        # Verify correlation ID was added to response
        assert "X-Correlation-ID" in response.headers
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    async def test_security_risk_tracking(
        self,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test that security risk information is tracked."""
        # Setup security monitor to detect suspicious activity
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": False,
            "is_suspicious": True,
            "risk_level": "medium",
            "threats": ["INVALID_ORIGIN", "AUTOMATED_TOOL"],
            "client_ip": "192.168.1.100"
        })
        
        # Create middleware
        middleware = MonitoringMiddleware(MagicMock())
        
        # Create suspicious request
        request = self.create_mock_request(
            headers={
                "origin": "https://unknown-site.com",
                "user-agent": "python-requests/2.28.0"
            }
        )
        
        async def mock_call_next(req):
            # Verify security result was attached to request
            assert hasattr(req.state, 'security_result')
            assert req.state.security_result["is_suspicious"] is True
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response
        
        response = await middleware.dispatch(request, mock_call_next)
        
        # Verify security information was included in tracking
        # Find the RequestStarted event call
        for call in mock_monitoring_service.track_event.call_args_list:
            if call[0][0] == "RequestStarted":
                track_event_call = call[0][1]
                assert track_event_call["security_risk"] == "medium"
                assert track_event_call["is_suspicious"] is True
                break
        else:
            raise AssertionError("RequestStarted event not found")
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    async def test_processing_time_measurement(
        self,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test accurate processing time measurement."""
        # Setup mocks
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": False,
            "is_suspicious": False,
            "risk_level": "low",
            "threats": [],
            "client_ip": "192.168.1.100"
        })
        
        # Create middleware
        middleware = MonitoringMiddleware(MagicMock())
        
        # Create request
        request = self.create_mock_request()
        
        # Mock call_next with simulated delay
        async def mock_call_next(req):
            await asyncio.sleep(0.1)  # 100ms delay
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response
        
        import asyncio
        response = await middleware.dispatch(request, mock_call_next)
        
        # Extract processing time from response header
        process_time_header = response.headers["X-Process-Time"]
        process_time_ms = float(process_time_header.replace("ms", ""))
        
        # Verify processing time is reasonable (should be ~100ms)
        assert process_time_ms >= 100  # At least 100ms
        assert process_time_ms < 200   # But less than 200ms
        
        # Verify monitoring service received the timing
        track_request_call = mock_monitoring_service.track_request.call_args[1]
        assert track_request_call["duration_ms"] >= 100
    
    @pytest.mark.asyncio
    @patch('src.middleware.monitoring_middleware.security_monitor')
    @patch('src.middleware.monitoring_middleware.monitoring_service')
    async def test_keyword_extraction_endpoint_specific_tracking(
        self,
        mock_monitoring_service,
        mock_security_monitor
    ):
        """Test special tracking for keyword extraction endpoint."""
        # Setup mocks
        mock_security_monitor.check_request_security = AsyncMock(return_value={
            "is_blocked": False,
            "is_suspicious": False,
            "risk_level": "low",
            "threats": [],
            "client_ip": "192.168.1.100"
        })
        
        # Create middleware
        middleware = MonitoringMiddleware(MagicMock())
        
        # Create request for keyword extraction endpoint
        request = self.create_mock_request(
            path="/api/v1/extract-jd-keywords"
        )
        
        async def mock_call_next(req):
            response = MagicMock()
            response.status_code = 200
            response.headers = {}
            return response
        
        response = await middleware.dispatch(request, mock_call_next)
        
        # Verify specific metric was tracked for keyword extraction
        mock_monitoring_service.track_metric.assert_called_with(
            "keyword_extraction_request",
            1,
            {
                "status_code": 200,
                "duration_ms": pytest.approx(0, abs=1000),  # Any reasonable duration
                "endpoint": "POST /api/v1/extract-jd-keywords"
            }
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])