"""
Main FastAPI application entry point.
Following FHS architecture principles.
"""
import logging
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Load environment variables from .env file
load_dotenv()

from src.api.v1 import router as v1_router  # noqa: E402
from src.core.config import settings  # noqa: E402
from src.core.monitoring_service import monitoring_service  # noqa: E402
from src.middleware.monitoring_middleware import MonitoringMiddleware  # noqa: E402

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description="""
        Azure FastAPI Resume API - FHS Architecture
        
        **v2.0 主要更新**：
        - 🎯 最多返回 16 個關鍵字（提升一致性）
        - 📊 一致性大幅提升：短文本 78%、長文本 60%
        - 🔧 支援 Prompt 版本控制（v1.0.0, v1.2.0, latest）
        - ⚡ 並行處理優化，效能提升 50%
        
        **核心功能**：
        - 2 輪交集策略確保結果一致性
        - 智能關鍵字標準化
        - Bubble.io 相容的固定 Schema
        - 完整的錯誤處理和品質警告
        """,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods_list,
        allow_headers=settings.cors_allow_headers_list,
    )
    
    # Add monitoring middleware
    app.add_middleware(MonitoringMiddleware)
    
    # Include API routers
    app.include_router(v1_router, prefix=settings.api_v1_prefix)
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "success": True,
            "data": {
                "name": settings.app_name,
                "version": settings.app_version,
                "api_v1": f"{settings.api_v1_prefix}/",
                "docs": "/docs",
                "status": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "version": settings.app_version,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Debug endpoint for monitoring
    @app.get("/debug/monitoring")
    async def debug_monitoring():
        """Debug endpoint to check monitoring status."""
        import contextlib
        import io

        from src.debug_monitoring import debug_monitoring as debug_func
        
        # Capture output
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            debug_func()
        output = f.getvalue()
        
        return {
            "success": True,
            "data": {
                "debug_output": output.split('\n')
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Starlette HTTP Exception handler (for method not allowed, etc.)
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request, exc):
        """Handle Starlette HTTP exceptions with unified response format."""
        from src.utils.error_formatting import get_error_context
        
        logger.warning(f"Starlette HTTP exception: {exc.status_code} - {exc.detail}")
        
        # Track HTTP errors with context
        if monitoring_service:
            error_category = "ClientError" if 400 <= exc.status_code < 500 else "ServerError"
            error_type = {
                400: "BadRequest",
                401: "Unauthorized", 
                403: "Forbidden",
                404: "NotFound",
                405: "MethodNotAllowed",
                408: "RequestTimeout",
                409: "Conflict",
                429: "TooManyRequests",
                500: "InternalServerError",
                502: "BadGateway",
                503: "ServiceUnavailable",
                504: "GatewayTimeout"
            }.get(exc.status_code, f"HTTP_{exc.status_code}")
            
            # Get enriched error context
            error_context = get_error_context(exc.status_code, request, exc)
            
            monitoring_service.track_event(
                "HTTPErrorTracked",
                {
                    "status_code": exc.status_code,
                    "error_type": error_type,
                    "error_category": error_category,
                    "error_message": str(exc.detail),
                    **error_context  # Include all context fields
                }
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": {},
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                    "type": "http_error",
                    "details": {
                        "status_code": exc.status_code,
                        "error_category": "client_error" if 400 <= exc.status_code < 500 else "server_error"
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # HTTP Exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """Handle HTTP exceptions with unified response format."""
        from src.utils.error_formatting import get_error_context
        
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        # Track HTTP errors with categorization and context
        if monitoring_service:
            error_category = "ClientError" if 400 <= exc.status_code < 500 else "ServerError"
            error_type = {
                400: "BadRequest",
                401: "Unauthorized", 
                403: "Forbidden",
                404: "NotFound",
                405: "MethodNotAllowed",
                408: "RequestTimeout",
                409: "Conflict",
                429: "TooManyRequests",
                500: "InternalServerError",
                502: "BadGateway",
                503: "ServiceUnavailable",
                504: "GatewayTimeout"
            }.get(exc.status_code, f"HTTP_{exc.status_code}")
            
            # Get enriched error context
            error_context = get_error_context(exc.status_code, request, exc)
            
            monitoring_service.track_event(
                "HTTPErrorTracked",
                {
                    "status_code": exc.status_code,
                    "error_type": error_type,
                    "error_category": error_category,
                    "error_message": str(exc.detail),
                    **error_context  # Include all context fields
                }
            )
        
        # If detail is already a dict (from our custom error responses), use it
        if isinstance(exc.detail, dict):
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail
            )
        
        # Otherwise, create unified response format
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": {},
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                    "type": "http_error",
                    "details": {
                        "status_code": exc.status_code,
                        "error_category": "client_error" if 400 <= exc.status_code < 500 else "server_error"
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Request validation error handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """Handle request validation errors with unified response format."""

        from src.utils.error_formatting import (
            create_validation_error_response,
            get_error_context,
            get_validation_error_metrics,
        )
        
        logger.warning(f"Validation error: {exc.errors()}")
        
        # Extract validation error metrics
        error_metrics = get_validation_error_metrics(exc)
        
        # Get enriched error context
        error_context = get_error_context(422, request, exc)
        
        # Track error with enhanced context
        if monitoring_service:
            monitoring_service.track_error(
                error_type="VALIDATION_ERROR",
                error_message=f"Validation failed: {error_metrics['primary_error_type']}",
                endpoint=f"{request.method} {request.url.path}",
                custom_properties={
                    **error_metrics,  # Include all error metrics
                    **error_context   # Include enhanced context
                }
            )
            
            # Track detailed validation error event
            monitoring_service.track_event(
                "ValidationErrorDetails",
                {
                    "primary_error_type": error_metrics['primary_error_type'],
                    "all_error_types": error_metrics['all_error_types'],
                    "error_count": error_metrics['error_count'],
                    "affected_fields": error_metrics['error_fields'],
                    **error_context  # Include context here too
                }
            )
        
        # Create detailed error response
        error_response = create_validation_error_response(exc)
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "data": {},
                "error": error_response,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle all unhandled exceptions."""
        from src.utils.error_formatting import (
            classify_exception,
            create_error_response,
            get_error_context,
        )
        
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        # Classify the exception
        exc_details = classify_exception(exc)
        
        # Get enriched error context
        error_context = get_error_context(500, request, exc)
        
        # Track error with detailed type information and context
        if monitoring_service:
            monitoring_service.track_error(
                error_type=exc_details["exception_type"],
                error_message=str(exc),
                endpoint=f"{request.method} {request.url.path}",
                custom_properties={
                    "exception_category": exc_details["exception_category"],
                    "exception_module": exc_details["exception_module"],
                    "is_retryable": exc_details["is_retryable"],
                    "is_client_error": exc_details["is_client_error"],
                    "is_server_error": exc_details["is_server_error"],
                    **error_context  # Include enhanced context
                }
            )
            
            # Track a specific event for exception categorization
            monitoring_service.track_event(
                "ExceptionCategorized",
                {
                    "exception_type": exc_details["exception_type"],
                    "exception_category": exc_details["exception_category"],
                    "endpoint": f"{request.method} {request.url.path}",
                    "is_retryable": exc_details["is_retryable"],
                    **error_context  # Include context here too
                }
            )
        
        # Create error response with details
        error_response = create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            exc=exc,
            status_code=500,
            include_details=settings.debug
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": {},
                "error": error_response,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    logger.info(f"{settings.app_name} initialized successfully")
    return app


# Create app instance
app = create_app()
