"""
API v1 router initialization.
Aggregates all v1 endpoints for Work Item #347 integration.
"""
from fastapi import APIRouter

# Import endpoint routers
from .keyword_extraction import router as keyword_router
# from .resume_format import router as format_router
# from .similarity import router as similarity_router
# from .gap_analysis import router as gap_router
# from .resume_tailoring import router as tailoring_router
# from .course_matching import router as course_router

# Create main v1 router
router = APIRouter()

# Include keyword extraction router directly (Work Item #347)
# This provides the main /api/v1/extract-jd-keywords endpoint
router.include_router(keyword_router, tags=["Keyword Extraction"])

# Include other routers as they are implemented
# router.include_router(format_router, tags=["Resume Format"])
# router.include_router(similarity_router, tags=["Similarity"])
# router.include_router(gap_router, tags=["Gap Analysis"])
# router.include_router(tailoring_router, tags=["Resume Tailoring"])
# router.include_router(course_router, tags=["Course Matching"])

# V1 API root endpoint
@router.get("/")
async def v1_root():
    """
    API v1 root endpoint with available endpoints information.
    
    Returns information about implemented endpoints following Work Item #347.
    """
    return {
        "success": True,
        "data": {
            "version": "v1",
            "description": "Azure FastAPI Resume API - Keyword Extraction Service",
            "implemented_endpoints": {
                "extract_jd_keywords": {
                    "path": "/api/v1/extract-jd-keywords",
                    "method": "POST",
                    "description": "Extract keywords from job descriptions",
                    "work_item": "#347",
                    "status": "implemented"
                },
                "health_check": {
                    "path": "/api/v1/health",
                    "method": "GET", 
                    "description": "Health check for keyword extraction service",
                    "status": "implemented"
                },
                "version_info": {
                    "path": "/api/v1/version",
                    "method": "GET",
                    "description": "Service version and capability information", 
                    "status": "implemented"
                }
            },
            "planned_endpoints": {
                "resume_format": "/api/v1/format-resume",
                "similarity": "/api/v1/calculate-similarity",
                "gap_analysis": "/api/v1/analyze-gaps",
                "resume_tailoring": "/api/v1/tailor-resume",
                "course_matching": "/api/v1/match-courses"
            },
            "features": {
                "2_round_intersection_strategy": True,
                "azure_openai_integration": True,
                "bubble_io_compatibility": True,
                "comprehensive_error_handling": True,
                "parallel_processing": True
            },
            "status": "ready"
        },
        "error": {
            "code": "",
            "message": "",
            "details": ""
        }
    }
