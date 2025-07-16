"""Test Course Search Models"""
import pytest

from src.models.course_search import (
    CourseResult,
    CourseSearchData,
    CourseSearchRequest,
    CourseSearchResponse,
    ErrorModel,
)


def test_course_search_request_validation():
    """測試請求模型驗證"""
    # 正常請求
    request = CourseSearchRequest(
        skill_name="Python",
        search_context="for data analysis",
        limit=5
    )
    assert request.skill_name == "Python"
    assert request.limit == 5
    
    # 測試限制
    request = CourseSearchRequest(
        skill_name="Python",
        limit=20  # 超過上限
    )
    assert request.limit == 10  # 應該被限制在 10
    
    # 測試空白 skill_name
    with pytest.raises(ValueError, match="skill_name cannot be empty"):
        CourseSearchRequest(skill_name="")
        
    # 測試過長的 skill_name
    with pytest.raises(ValueError, match="skill_name too long"):
        CourseSearchRequest(skill_name="a" * 101)
        
    # 測試過長的 search_context
    with pytest.raises(ValueError, match="search_context too long"):
        CourseSearchRequest(
            skill_name="Python",
            search_context="a" * 501
        )


def test_course_search_response_structure():
    """測試回應模型結構"""
    # 成功回應
    response = CourseSearchResponse(
        success=True,
        data=CourseSearchData(
            results=[
                CourseResult(
                    id="course_123",
                    name="Python for Beginners",
                    description="Learn Python",
                    provider="Coursera",
                    provider_standardized="Coursera",
                    provider_logo_url="https://bubble.io/.../coursera-official.svg",
                    price=49.99,
                    currency="USD",
                    image_url="https://course-image.jpg",
                    affiliate_url="https://imp.i384100.net/...",
                    similarity_score=0.95
                )
            ],
            total_count=1,
            returned_count=1,
            query="Python",
            search_time_ms=150
        ),
        error=ErrorModel()
    )
    
    assert response.success is True
    assert len(response.data.results) == 1
    assert response.data.results[0].name == "Python for Beginners"
    assert response.data.results[0].price == 49.99
    assert response.data.results[0].affiliate_url == "https://imp.i384100.net/..."
    assert response.error.code == ""
    
    # 失敗回應
    error_response = CourseSearchResponse(
        success=False,
        data=CourseSearchData(),
        error=ErrorModel(
            code="SEARCH_ERROR",
            message="Search failed",
            details="Database connection error"
        )
    )
    
    assert error_response.success is False
    assert len(error_response.data.results) == 0
    assert error_response.error.code == "SEARCH_ERROR"


def test_bubble_io_compatibility():
    """測試 Bubble.io 相容性"""
    # 所有欄位都必須有預設值
    empty_result = CourseResult()
    assert empty_result.id == ""
    assert empty_result.name == ""
    assert empty_result.price == 0.0
    assert empty_result.affiliate_url == ""
    assert empty_result.provider == ""
    assert empty_result.provider_standardized == ""
    assert empty_result.provider_logo_url == ""
    
    empty_data = CourseSearchData()
    assert empty_data.results == []
    assert empty_data.total_count == 0
    
    empty_error = ErrorModel()
    assert empty_error.code == ""
    assert empty_error.message == ""