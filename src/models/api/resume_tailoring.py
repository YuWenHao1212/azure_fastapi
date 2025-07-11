"""
API models for Resume Tailoring service.
Provides request/response models for resume optimization.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class TailoringOptions(BaseModel):
    """Options for resume tailoring"""
    include_visual_markers: bool = Field(
        default=True,
        description="Include visual markers (CSS classes) for optimizations"
    )
    language: Literal["en", "zh-TW"] = Field(
        default="en",
        description="Output language for the tailored resume"
    )


class GapAnalysisInput(BaseModel):
    """Gap analysis results to be used for tailoring"""
    core_strengths: list[str] = Field(
        description="3-5 identified strengths from gap analysis (supports multiple formats)"
    )
    key_gaps: list[str] = Field(
        description="3-5 identified gaps from gap analysis (supports multiple formats)"
    )
    quick_improvements: list[str] = Field(
        description="3-5 actionable improvements from gap analysis (supports multiple formats)"
    )
    covered_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords already present in resume (comma-separated or list)"
    )
    missing_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that need to be added (comma-separated or list)"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_flexible_inputs(cls, data):
        """Parse various input formats before validation"""
        if not isinstance(data, dict):
            return data
            
        from ...utils.input_parsers import (
            parse_flexible_keywords,
            parse_multiline_items,
        )
        
        # Parse multi-line fields
        for field in ['core_strengths', 'key_gaps', 'quick_improvements']:
            if field in data and isinstance(data[field], str):
                data[field] = parse_multiline_items(data[field])
        
        # Parse keyword fields
        for field in ['covered_keywords', 'missing_keywords']:
            if field in data and isinstance(data[field], str):
                data[field] = parse_flexible_keywords(data[field])
                
        return data


class TailorResumeRequest(BaseModel):
    """Request model for resume tailoring"""
    job_description: str = Field(
        description="Target job description",
        min_length=50,
        max_length=10000
    )
    original_resume: str = Field(
        description="Original resume in HTML format",
        min_length=100,
        max_length=50000
    )
    gap_analysis: GapAnalysisInput = Field(
        description="Gap analysis results"
    )
    options: TailoringOptions = Field(
        default_factory=TailoringOptions,
        description="Tailoring options"
    )


class OptimizationStats(BaseModel):
    """Statistics about the optimization process"""
    sections_modified: int = Field(
        description="Number of resume sections modified"
    )
    keywords_added: int = Field(
        description="Number of new keywords integrated"
    )
    strengths_highlighted: int = Field(
        description="Number of strengths highlighted"
    )
    placeholders_added: int = Field(
        description="Number of metric placeholders added"
    )


class VisualMarkerStats(BaseModel):
    """Statistics about visual markers applied"""
    strength_count: int = Field(
        default=0,
        description="Number of strength markers"
    )
    keyword_count: int = Field(
        default=0,
        description="Number of keyword markers"
    )
    placeholder_count: int = Field(
        default=0,
        description="Number of placeholder markers"
    )
    new_content_count: int = Field(
        default=0,
        description="Number of new content markers"
    )
    improvement_count: int = Field(
        default=0,
        description="Number of improvement markers"
    )


class TailoringResult(BaseModel):
    """Result of resume tailoring"""
    optimized_resume: str = Field(
        description="Optimized resume HTML with visual markers"
    )
    applied_improvements: list[str] = Field(
        description="List of improvements applied by section"
    )
    applied_improvements_html: str = Field(
        default="",
        description="HTML formatted list of improvements for direct display"
    )
    optimization_stats: OptimizationStats = Field(
        description="Statistics about the optimization"
    )
    visual_markers: VisualMarkerStats = Field(
        description="Statistics about visual markers"
    )


class TailoringResponse(BaseModel):
    """Response model for resume tailoring - Bubble.io compatible"""
    success: bool = Field(
        description="Whether the request was successful"
    )
    data: TailoringResult | None = Field(
        default=None,
        description="Tailoring result when successful"
    )
    error: dict = Field(
        default_factory=lambda: {"code": "", "message": "", "details": ""},
        description="Error information if request failed"
    )


class TailoringError(BaseModel):
    """Error details for tailoring failures"""
    error_type: str = Field(
        description="Type of error that occurred"
    )
    details: str = Field(
        description="Detailed error message"
    )
    suggestion: str | None = Field(
        default=None,
        description="Suggestion for fixing the error"
    )