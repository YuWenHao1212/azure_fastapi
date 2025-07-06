"""
Monitoring middleware for request/response tracking.
Implements comprehensive monitoring for all API endpoints.
"""
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.metrics.endpoint_metrics import endpoint_metrics
from src.core.monitoring.security_monitor import security_monitor
from src.core.monitoring_service import monitoring_service


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring API requests and responses.
    
    Features:
    - Request/response time tracking
    - Error rate monitoring by endpoint
    - Correlation ID generation
    - Custom properties tracking
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with monitoring."""
        # Security check first
        security_result = await security_monitor.check_request_security(request)
        
        if security_result["is_blocked"]:
            # Return 403 for blocked requests
            monitoring_service.track_event(
                "request_blocked",
                {
                    "client_ip": security_result["client_ip"],
                    "threats": security_result["threats"]
                }
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "data": {},
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Access denied",
                        "details": "Your request has been blocked for security reasons"
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        request.state.security_result = security_result
        
        # Extract request information
        endpoint = f"{request.method} {request.url.path}"
        start_time = time.time()
        
        # Track request start
        monitoring_service.track_event(
            "RequestStarted",
            {
                "endpoint": endpoint,
                "method": request.method,
                "path": request.url.path,
                "correlation_id": correlation_id,
                "origin": request.headers.get("origin", "unknown"),
                "user_agent": request.headers.get("user-agent", "unknown"),
                "security_risk": security_result.get("risk_level", "low"),
                "is_suspicious": security_result.get("is_suspicious", False)
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Track endpoint metrics using EndpointMetrics
            endpoint_metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                custom_properties={
                    "correlation_id": correlation_id
                }
            )
            
            # Track successful request
            monitoring_service.track_request(
                endpoint=endpoint,
                method=request.method,
                duration_ms=duration_ms,
                success=response.status_code < 400,
                status_code=response.status_code,
                custom_properties={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "query_params": str(request.url.query),
                    "response_headers": dict(response.headers)
                }
            )
            
            # Add monitoring headers to response
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
            
            # Track specific endpoint metrics
            if request.url.path.startswith("/api/v1/extract-jd-keywords"):
                monitoring_service.track_metric(
                    "keyword_extraction_request",
                    1,
                    {
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        "endpoint": endpoint
                    }
                )
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Track endpoint metrics for errors using EndpointMetrics
            endpoint_metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=500,
                duration_ms=duration_ms,
                error_type=type(e).__name__,
                custom_properties={
                    "correlation_id": correlation_id,
                    "error_message": str(e)
                }
            )
            
            # Track error
            monitoring_service.track_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint=endpoint,
                custom_properties={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": duration_ms
                }
            )
            
            # Re-raise the exception
            raise
    
    def get_endpoint_stats(self) -> dict:
        """Get current endpoint statistics."""
        return endpoint_metrics.get_endpoint_stats()