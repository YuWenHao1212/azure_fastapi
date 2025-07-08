"""
API v1 router initialization.
Aggregates all v1 endpoints for Work Item #347 integration.
"""
from fastapi import APIRouter

from .index_cal_and_gap_analysis import router as index_gap_router
from .index_calculation import router as index_calculation_router

# Import endpoint routers
from .keyword_extraction import router as keyword_router
from .prompts import router as prompts_router

# from .resume_format import router as format_router
# from .resume_tailoring import router as tailoring_router
# from .course_matching import router as course_router

# Create main v1 router
router = APIRouter()

# Include keyword extraction router directly (Work Item #347)
# This provides the main /api/v1/extract-jd-keywords endpoint
router.include_router(keyword_router, tags=["Keyword Extraction"])

# Include prompt management router
# This provides generic prompt version management for all tasks
router.include_router(prompts_router, tags=["Prompt Management"])

# Include index calculation and gap analysis routers
router.include_router(index_calculation_router, tags=["Index Calculation"])
router.include_router(index_gap_router, tags=["Gap Analysis"])

# Include other routers as they are implemented
# router.include_router(format_router, tags=["Resume Format"])
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
                },
                "prompt_version": {
                    "path": "/api/v1/prompt-version",
                    "method": "GET",
                    "description": "Get active prompt version for keyword extraction",
                    "status": "implemented"
                },
                "prompts_version": {
                    "path": "/api/v1/prompts/version",
                    "method": "GET",
                    "description": "Get prompt version for any task (generic)",
                    "status": "implemented"
                },
                "prompts_tasks": {
                    "path": "/api/v1/prompts/tasks",
                    "method": "GET",
                    "description": "List all tasks with prompt configurations",
                    "status": "implemented"
                },
                "index_calculation": {
                    "path": "/api/v1/index-calculation",
                    "method": "POST",
                    "description": "Calculate similarity index and keyword coverage",
                    "status": "implemented"
                },
                "index_cal_and_gap_analysis": {
                    "path": "/api/v1/index-cal-and-gap-analysis",
                    "method": "POST",
                    "description": "Calculate index and perform gap analysis",
                    "status": "implemented"
                }
            },
            "planned_endpoints": {
                "resume_format": "/api/v1/format-resume",
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
