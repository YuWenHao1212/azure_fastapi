"""
Unit tests for Pydantic models - Work Item #348.
Tests request/response model validation, serialization, and error handling.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from src.models.keyword_extraction import (
    KeywordExtractionRequest, 
    KeywordExtractionData,
    KeywordExtractionResponse
)
from src.models.response import (
    UnifiedResponse, 
    ErrorDetail, 
    WarningInfo, 
    IntersectionStats,
    StandardizedTerm,
    create_success_response,
    create_error_response
)


@pytest.mark.unit
class TestKeywordExtractionRequest:
    """Test KeywordExtractionRequest model validation."""
    
    def test_valid_request_creation(self, sample_job_description):
        """Test creating a valid request."""
        request = KeywordExtractionRequest(
            job_description=sample_job_description,
            max_keywords=15,
            prompt_version="v1.0.0"
        )
        
        assert request.job_description == sample_job_description.strip()
        assert request.max_keywords == 15
        assert request.prompt_version == "v1.0.0"
    
    def test_default_values(self, sample_job_description):
        """Test that default values are applied correctly."""
        request = KeywordExtractionRequest(job_description=sample_job_description)
        
        assert request.max_keywords == 16  # Default value
        assert request.include_standardization is True
        assert request.use_multi_round_validation is True
        assert request.prompt_version == "latest"  # Updated to correct default
    
    def test_job_description_trimming(self):
        """Test that job description is trimmed of whitespace."""
        job_desc = "  We are seeking a Senior Python Developer with experience in FastAPI, machine learning, and backend development. The ideal candidate should have strong skills.  "
        request = KeywordExtractionRequest(job_description=job_desc)
        
        # Should be trimmed
        assert request.job_description == job_desc.strip()
        assert len(request.job_description) >= 50  # Meets minimum length requirement
    
    def test_short_job_description_validation(self):
        """Test validation fails for short job descriptions."""
        with pytest.raises(ValidationError) as exc_info:
            KeywordExtractionRequest(job_description="Short")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert "too short" in str(errors[0]["ctx"]["error"])
    
    def test_max_keywords_range_validation(self, sample_job_description):
        """Test max_keywords range validation."""
        # Test minimum boundary
        with pytest.raises(ValidationError):
            KeywordExtractionRequest(
                job_description=sample_job_description,
                max_keywords=4  # Below minimum of 5
            )
        
        # Test maximum boundary
        with pytest.raises(ValidationError):
            KeywordExtractionRequest(
                job_description=sample_job_description,
                max_keywords=26  # Above maximum of 25
            )
        
        # Test valid boundaries
        request_min = KeywordExtractionRequest(
            job_description=sample_job_description,
            max_keywords=5
        )
        assert request_min.max_keywords == 5
        
        request_max = KeywordExtractionRequest(
            job_description=sample_job_description,
            max_keywords=25
        )
        assert request_max.max_keywords == 25
    
    def test_prompt_version_validation(self, sample_job_description):
        """Test prompt_version field accepts various formats."""
        # Test valid versions
        valid_versions = ["v1.0.0", "v2.1.0", "latest", "stable", "invalid-version"]
        for version in valid_versions:
            request = KeywordExtractionRequest(
                job_description=sample_job_description,
                prompt_version=version
            )
            assert request.prompt_version == version
        
        # Note: No strict validation is implemented for prompt_version format
        # It accepts any string value
    
    def test_model_serialization(self, sample_job_description):
        """Test model can be serialized to dict."""
        request = KeywordExtractionRequest(job_description=sample_job_description)
        data = request.dict()
        
        assert data["job_description"] == sample_job_description.strip()
        assert data["max_keywords"] == 16  # Default value
        assert data["prompt_version"] == "latest"  # Updated to correct default


@pytest.mark.unit
class TestKeywordExtractionData:
    """Test KeywordExtractionData model."""
    
    def test_valid_data_creation(self):
        """Test creating valid KeywordExtractionData."""
        data = KeywordExtractionData(
            keywords=["Python", "FastAPI", "Backend"],
            keyword_count=3,
            confidence_score=0.85,
            extraction_method="2_round_intersection"
        )
        
        assert len(data.keywords) == 3
        assert data.keyword_count == 3
        assert data.confidence_score == 0.85
        assert data.extraction_method == "2_round_intersection"
    
    def test_default_values(self):
        """Test default values for optional fields."""
        data = KeywordExtractionData()
        
        assert data.keywords == []
        assert data.keyword_count == 0
        assert data.confidence_score == 0.0
        assert data.extraction_method == ""
        assert isinstance(data.intersection_stats, IntersectionStats)
        assert isinstance(data.warning, WarningInfo)
        assert data.processing_time_ms == 0
    
    def test_confidence_score_range(self):
        """Test confidence score validation."""
        # Test minimum boundary
        data = KeywordExtractionData(confidence_score=0.0)
        assert data.confidence_score == 0.0
        
        # Test maximum boundary
        data = KeywordExtractionData(confidence_score=1.0)
        assert data.confidence_score == 1.0
        
        # Test invalid values
        with pytest.raises(ValidationError):
            KeywordExtractionData(confidence_score=-0.1)
        
        with pytest.raises(ValidationError):
            KeywordExtractionData(confidence_score=1.1)
    
    def test_keyword_count_consistency(self):
        """Test keyword count matches keywords list length."""
        keywords = ["Python", "FastAPI", "Backend"]
        data = KeywordExtractionData(
            keywords=keywords,
            keyword_count=len(keywords)
        )
        
        assert data.keyword_count == len(data.keywords)
    
    def test_complex_data_structure(self, sample_keyword_extraction_data):
        """Test complex data structure with all fields."""
        assert isinstance(sample_keyword_extraction_data.intersection_stats, IntersectionStats)
        assert isinstance(sample_keyword_extraction_data.warning, WarningInfo)
        assert sample_keyword_extraction_data.processing_time_ms > 0


@pytest.mark.unit
class TestUnifiedResponse:
    """Test UnifiedResponse model."""
    
    def test_success_response_creation(self):
        """Test creating a successful response."""
        response = UnifiedResponse(
            success=True,
            data={"message": "Success"}
        )
        
        assert response.success is True
        assert response.data == {"message": "Success"}
        assert response.error.code == ""
        assert response.error.message == ""
        assert response.timestamp is not None
    
    def test_error_response_creation(self):
        """Test creating an error response."""
        error = ErrorDetail(
            code="TEST_ERROR",
            message="Test error message",
            details="Additional details"
        )
        
        response = UnifiedResponse(
            success=False,
            data={},
            error=error
        )
        
        assert response.success is False
        assert response.data == {}
        assert response.error.code == "TEST_ERROR"
        assert response.error.message == "Test error message"
    
    def test_default_values(self):
        """Test default values for UnifiedResponse."""
        response = UnifiedResponse()
        
        assert response.success is True
        assert response.data == {}
        assert response.error.code == ""
        assert response.timestamp is not None
    
    def test_timestamp_format(self):
        """Test timestamp is in ISO format."""
        response = UnifiedResponse()
        
        # Test timestamp can be parsed as datetime
        parsed_time = datetime.fromisoformat(
            response.timestamp.replace('Z', '+00:00') if response.timestamp.endswith('Z') 
            else response.timestamp
        )
        assert isinstance(parsed_time, datetime)


@pytest.mark.unit
class TestErrorDetail:
    """Test ErrorDetail model."""
    
    def test_default_values(self):
        """Test default values for ErrorDetail."""
        error = ErrorDetail()
        
        assert error.code == ""
        assert error.message == ""
        assert error.details == ""
    
    def test_custom_values(self):
        """Test custom error values."""
        error = ErrorDetail(
            code="VALIDATION_ERROR",
            message="輸入參數驗證失敗",
            details="Job description too short"
        )
        
        assert error.code == "VALIDATION_ERROR"
        assert error.message == "輸入參數驗證失敗"
        assert error.details == "Job description too short"


@pytest.mark.unit
class TestWarningInfo:
    """Test WarningInfo model."""
    
    def test_default_values(self):
        """Test default values for WarningInfo."""
        warning = WarningInfo()
        
        assert warning.has_warning is False
        assert warning.message == ""
        assert warning.expected_minimum == 12
        assert warning.actual_extracted == 0
        assert warning.suggestion == ""
    
    def test_warning_creation(self):
        """Test creating warning with custom values."""
        warning = WarningInfo(
            has_warning=True,
            message="Low keyword count",
            expected_minimum=12,
            actual_extracted=5,
            suggestion="Consider expanding job description"
        )
        
        assert warning.has_warning is True
        assert warning.message == "Low keyword count"
        assert warning.expected_minimum == 12
        assert warning.actual_extracted == 5


@pytest.mark.unit
class TestIntersectionStats:
    """Test IntersectionStats model."""
    
    def test_default_values(self):
        """Test default values for IntersectionStats."""
        stats = IntersectionStats()
        
        assert stats.intersection_count == 0
        assert stats.round1_count == 0
        assert stats.round2_count == 0
        assert stats.total_available == 0
        assert stats.final_count == 0
        assert stats.supplement_count == 0
        assert stats.strategy_used == ""
        assert stats.warning is False
        assert stats.warning_message == ""
    
    def test_stats_creation(self):
        """Test creating intersection stats."""
        stats = IntersectionStats(
            intersection_count=3,
            round1_count=8,
            round2_count=7,
            total_available=10,
            final_count=5,
            supplement_count=2,
            strategy_used="2_round_intersection_with_supplement",
            warning=False
        )
        
        assert stats.intersection_count == 3
        assert stats.round1_count == 8
        assert stats.final_count == 5
        assert stats.strategy_used == "2_round_intersection_with_supplement"


@pytest.mark.unit
class TestStandardizedTerm:
    """Test StandardizedTerm model."""
    
    def test_default_values(self):
        """Test default values for StandardizedTerm."""
        term = StandardizedTerm()
        
        assert term.original == ""
        assert term.standardized == ""
        assert term.method == ""
    
    def test_term_creation(self):
        """Test creating standardized term."""
        term = StandardizedTerm(
            original="ML",
            standardized="Machine Learning",
            method="abbreviation_expansion"
        )
        
        assert term.original == "ML"
        assert term.standardized == "Machine Learning"
        assert term.method == "abbreviation_expansion"


@pytest.mark.unit
class TestResponseUtilities:
    """Test response utility functions."""
    
    def test_create_success_response(self):
        """Test create_success_response utility."""
        test_data = {"keywords": ["Python", "FastAPI"], "count": 2}
        response = create_success_response(test_data)
        
        assert response.success is True
        assert response.data == test_data
        assert response.error.code == ""
        assert response.timestamp is not None
    
    def test_create_error_response(self):
        """Test create_error_response utility."""
        response = create_error_response(
            code="TEST_ERROR",
            message="Test message",
            details="Test details",
            data={"extra": "info"}
        )
        
        assert response.success is False
        assert response.data == {"extra": "info"}
        assert response.error.code == "TEST_ERROR"
        assert response.error.message == "Test message"
        assert response.error.details == "Test details"
    
    def test_create_error_response_without_data(self):
        """Test create_error_response without data parameter."""
        response = create_error_response(
            code="ERROR",
            message="Error message"
        )
        
        assert response.success is False
        assert response.data == {}
        assert response.error.code == "ERROR"
        assert response.error.details == ""


@pytest.mark.unit
class TestBubbleIoCompatibility:
    """Test Bubble.io compatibility requirements."""
    
    def test_no_optional_none_values(self, sample_keyword_extraction_data):
        """Test that no fields return None (Bubble.io requirement)."""
        data_dict = sample_keyword_extraction_data.model_dump()
        
        def check_no_none_values(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    assert value is not None, f"None value found at {current_path}"
                    check_no_none_values(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    assert item is not None, f"None value found at {current_path}"
                    check_no_none_values(item, current_path)
        
        check_no_none_values(data_dict)
    
    def test_consistent_schema_success_error(self):
        """Test success and error responses have consistent schema."""
        # Success response
        success_response = create_success_response({"test": "data"})
        success_dict = success_response.model_dump()
        
        # Error response
        error_response = create_error_response("ERROR", "message")
        error_dict = error_response.model_dump()
        
        # Both should have same top-level keys
        assert set(success_dict.keys()) == set(error_dict.keys())
        
        # Both should have consistent error structure
        assert "code" in success_dict["error"]
        assert "message" in success_dict["error"]
        assert "details" in success_dict["error"]
        
        assert "code" in error_dict["error"]
        assert "message" in error_dict["error"]
        assert "details" in error_dict["error"]
    
    def test_array_fields_always_arrays(self, sample_keyword_extraction_data):
        """Test array fields are always arrays, never None."""
        # Test with data
        assert isinstance(sample_keyword_extraction_data.keywords, list)
        
        # Test with empty data
        empty_data = KeywordExtractionData()
        assert isinstance(empty_data.keywords, list)
        assert len(empty_data.keywords) == 0 