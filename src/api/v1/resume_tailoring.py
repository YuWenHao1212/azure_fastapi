"""
Resume Tailoring API endpoints.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ...core.config import Settings, get_settings
from ...models.api.resume_tailoring import (
    TailoringResponse,
    TailorResumeRequest,
)
from ...services.resume_tailoring import ResumeTailoringService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tailor-resume")

# Initialize service
tailoring_service = ResumeTailoringService()


@router.post(
    "",
    response_model=TailoringResponse,
    summary="Tailor Resume",
    description="Optimize a resume based on job description and gap analysis results",
    responses={
        200: {
            "description": "Resume successfully tailored",
            "model": TailoringResponse
        },
        400: {
            "description": "Invalid request data",
            "model": TailoringResponse
        },
        500: {
            "description": "Internal server error",
            "model": TailoringResponse
        }
    }
)
async def tailor_resume(
    request: TailorResumeRequest,
    settings: Settings = Depends(get_settings)
) -> TailoringResponse:
    """
    Tailor a resume to better match a job description.
    
    This endpoint uses gap analysis results to:
    - Create or optimize Summary section
    - Convert experience bullets to STAR/PAR format
    - Integrate missing keywords naturally
    - Highlight core strengths
    - Add metric placeholders where needed
    
    The output includes visual markers (CSS classes) to show optimizations.
    """
    try:
        logger.info(f"Resume tailoring request received for language: {request.options.language}")
        
        # Call service (validation already handled by Pydantic field_validators)
        result = await tailoring_service.tailor_resume(
            job_description=request.job_description,
            original_resume=request.original_resume,
            gap_analysis=request.gap_analysis,
            language=request.options.language,
            include_markers=request.options.include_visual_markers
        )
        
        logger.info(f"Resume tailoring completed: {result.markers.new_section} new sections, {result.markers.modified} modified content")
        
        return TailoringResponse(
            success=True,
            data=result,
            error={
                "code": "",
                "message": "",
                "details": ""
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return TailoringResponse(
            success=False,
            data=None,
            error={
                "code": "INVALID_REQUEST",
                "message": str(e),
                "details": "Please check your input data"
            }
        )
        
    except Exception as e:
        logger.error(f"Resume tailoring failed: {str(e)}", exc_info=True)
        return TailoringResponse(
            success=False,
            data=None,
            error={
                "code": "TAILORING_ERROR",
                "message": "Failed to tailor resume",
                "details": str(e)
            }
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the resume tailoring service is healthy"
)
async def health_check():
    """Check service health"""
    try:
        # Check if service is initialized
        if not tailoring_service:
            raise Exception("Service not initialized")
        
        # Check standardizers
        en_available = tailoring_service.en_standardizer.is_standardization_available()
        zh_available = tailoring_service.zh_tw_standardizer.is_standardization_available()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "service": "resume_tailoring",
                "standardizers": {
                    "en": en_available,
                    "zh-TW": zh_available
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get(
    "/supported-languages",
    summary="Get Supported Languages",
    description="Get list of supported languages for resume tailoring"
)
async def get_supported_languages():
    """Get supported languages"""
    from ...core.language_handler import LanguageHandler
    
    return {
        "success": True,
        "data": {
            "languages": LanguageHandler.SUPPORTED_LANGUAGES,
            "default": LanguageHandler.DEFAULT_LANGUAGE
        }
    }