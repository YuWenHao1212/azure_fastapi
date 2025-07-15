"""Course Search Models for Bubble.io compatibility"""
from typing import Any, Literal

from pydantic import BaseModel, validator


class CourseSearchRequest(BaseModel):
    """課程搜尋請求模型"""
    skill_name: str
    search_context: str = ""
    category: Literal["", "Tech", "Non-Tech"] = ""
    limit: int = 5
    similarity_threshold: float = 0.3
    
    @validator('skill_name')
    def validate_skill_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("skill_name cannot be empty")
        if len(v) > 100:
            raise ValueError("skill_name too long (max 100 chars)")
        return v
    
    @validator('search_context')
    def validate_search_context(cls, v):
        if len(v) > 500:
            raise ValueError("search_context too long (max 500 chars)")
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        return max(1, min(v, 10))
    
    @validator('similarity_threshold')
    def validate_threshold(cls, v):
        return max(0.1, min(v, 1.0))
    
    class Config:
        schema_extra = {
            "example": {
                "skill_name": "Python",
                "search_context": "for data analysis and machine learning",
                "category": "Tech",
                "limit": 5,
                "similarity_threshold": 0.3
            }
        }

class CourseResult(BaseModel):
    """單一課程結果"""
    id: str = ""
    name: str = ""
    description: str = ""
    manufacturer: str = ""
    category: str = ""
    sub_category: str = ""
    current_price: float = 0.0
    original_price: float = 0.0
    discount_percentage: float = 0.0
    currency: str = "USD"
    image_url: str = ""
    course_url: str = ""
    tracking_url: str = ""
    similarity_score: float = 0.0
    highlights: list[str] = []

class CourseSearchData(BaseModel):
    """搜尋結果資料"""
    results: list[CourseResult] = []
    total_count: int = 0
    returned_count: int = 0
    query: str = ""
    search_time_ms: int = 0
    filters_applied: dict[str, Any] = {}

class ErrorModel(BaseModel):
    """錯誤模型"""
    code: str = ""
    message: str = ""
    details: str = ""

class CourseSearchResponse(BaseModel):
    """課程搜尋回應（Bubble.io 相容）"""
    success: bool
    data: CourseSearchData
    error: ErrorModel