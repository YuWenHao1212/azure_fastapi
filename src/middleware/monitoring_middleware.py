"""
Monitoring middleware for request/response tracking.
Implements comprehensive monitoring for all API endpoints.
"""
import time
import uuid
from typing import Callable
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.monitoring import monitoring_service


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
        self.endpoint_metrics = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with monitoring."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
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
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Track endpoint metrics
            self._update_endpoint_metrics(endpoint, response.status_code, duration_ms)
            
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
            
            # Track endpoint metrics for errors
            self._update_endpoint_metrics(endpoint, 500, duration_ms)
            
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
    
    def _update_endpoint_metrics(self, endpoint: str, status_code: int, duration_ms: float):
        """Update endpoint-level metrics."""
        if endpoint not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint] = {
                "total_requests": 0,
                "failed_requests": 0,
                "total_duration": 0,
                "status_codes": {}
            }
        
        metrics = self.endpoint_metrics[endpoint]
        metrics["total_requests"] += 1
        metrics["total_duration"] += duration_ms
        
        if status_code >= 400:
            metrics["failed_requests"] += 1
        
        # Track status code distribution
        status_code_str = str(status_code)
        metrics["status_codes"][status_code_str] = metrics["status_codes"].get(status_code_str, 0) + 1
        
        # Calculate and track error rate
        error_rate = (metrics["failed_requests"] / metrics["total_requests"]) * 100
        avg_duration = metrics["total_duration"] / metrics["total_requests"]
        
        # Send endpoint metrics to Application Insights
        monitoring_service.track_metric(
            "endpoint_error_rate",
            error_rate,
            {
                "endpoint": endpoint,
                "total_requests": metrics["total_requests"],
                "failed_requests": metrics["failed_requests"],
                "avg_duration_ms": avg_duration
            }
        )
        
        # Track endpoint performance
        monitoring_service.track_metric(
            "endpoint_avg_duration",
            avg_duration,
            {
                "endpoint": endpoint,
                "total_requests": metrics["total_requests"]
            }
        )
    
    def get_endpoint_stats(self) -> dict:
        """Get current endpoint statistics."""
        stats = {}
        for endpoint, metrics in self.endpoint_metrics.items():
            error_rate = (metrics["failed_requests"] / metrics["total_requests"] * 100) if metrics["total_requests"] > 0 else 0
            avg_duration = metrics["total_duration"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
            
            stats[endpoint] = {
                "total_requests": metrics["total_requests"],
                "failed_requests": metrics["failed_requests"],
                "error_rate": f"{error_rate:.2f}%",
                "avg_duration_ms": f"{avg_duration:.2f}",
                "status_code_distribution": metrics["status_codes"]
            }
        
        return stats