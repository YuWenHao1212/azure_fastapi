"""
Main FastAPI application entry point.
Following FHS architecture principles.
"""
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.v1 import router as v1_router
from src.core.config import settings

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
    
    # Starlette HTTP Exception handler (for method not allowed, etc.)
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request, exc):
        """Handle Starlette HTTP exceptions with unified response format."""
        logger.warning(f"Starlette HTTP exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": {},
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                    "details": ""
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # HTTP Exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """Handle HTTP exceptions with unified response format."""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
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
                    "details": ""
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Request validation error handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """Handle request validation errors with unified response format."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "data": {},
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": str(exc.errors())
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": {},
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": str(exc) if settings.debug else ""
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    logger.info(f"{settings.app_name} initialized successfully")
    return app


# Create app instance
app = create_app()
