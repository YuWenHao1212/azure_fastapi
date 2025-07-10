"""
API models for Resume Tailoring service.
Provides request/response models for resume optimization.
"""

from typing import Literal

from pydantic import BaseModel, Field


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
        description="3-5 identified strengths from gap analysis"
    )
    quick_improvements: list[str] = Field(
        description="3-5 actionable improvements from gap analysis"
    )
    overall_assessment: str = Field(
        description="Strategic guidance from gap analysis"
    )
    covered_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords already present in resume"
    )
    missing_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords that need to be added"
    )


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