"""
Unit tests for Bubble.io response validator.
"""
from src.utils.response_validator import (
    check_for_nulls,
    count_fields,
    validate_bubble_compatibility,
    validate_keyword_extraction_response,
)


class TestResponseValidator:
    """Test response validation functionality."""
    
    def test_valid_success_response(self):
        """Test validation of a valid successful response."""
        response = {
            "success": True,
            "data": {
                "jd_keywords": ["python", "fastapi"],
                "matched_keywords": ["python"],
                "similarity_score": 0.85
            },
            "error": {
                "code": "",
                "message": "",
                "details": ""
            },
            "timestamp": "2025-07-07T10:00:00Z"
        }
        
        result = validate_bubble_compatibility(response)
        assert result["is_valid"] is True
        assert result["bubble_compatible"] is True
        assert len(result["issues"]) == 0
    
    def test_valid_error_response(self):
        """Test validation of a valid error response."""
        response = {
            "success": False,
            "data": {},
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input",
                "details": "Job description is required"
            },
            "timestamp": "2025-07-07T10:00:00Z"
        }
        
        result = validate_bubble_compatibility(response)
        assert result["is_valid"] is True
        assert result["bubble_compatible"] is True
    
    def test_missing_required_fields(self):
        """Test detection of missing required fields."""
        response = {
            "success": True,
            "data": {}
            # Missing error and timestamp
        }
        
        result = validate_bubble_compatibility(response)
        assert result["is_valid"] is False
        assert result["bubble_compatible"] is False
        assert "Missing required fields" in result["issues"][0]
    
    def test_null_values_detection(self):
        """Test detection of null values."""
        response = {
            "success": True,
            "data": {
                "keywords": None,  # This is bad for Bubble.io
                "score": 0.5
            },
            "error": {
                "code": "",
                "message": "",
                "details": None  # This is also bad
            },
            "timestamp": "2025-07-07T10:00:00Z"
        }
        
        result = validate_bubble_compatibility(response)
        assert result["is_valid"] is False
        assert result["has_nulls"] is True
        assert "null values" in str(result["issues"])
    
    def test_failed_response_with_data(self):
        """Test that failed responses should have empty data."""
        response = {
            "success": False,
            "data": {"some": "data"},  # Should be empty for failed responses
            "error": {
                "code": "ERROR",
                "message": "Something failed",
                "details": "Details here"
            },
            "timestamp": "2025-07-07T10:00:00Z"
        }
        
        result = validate_bubble_compatibility(response)
        assert result["is_valid"] is False
        assert "Failed responses should have empty data" in str(result["issues"])
    
    def test_success_response_with_error_data(self):
        """Test that successful responses should have empty error fields."""
        response = {
            "success": True,
            "data": {"result": "ok"},
            "error": {
                "code": "SOME_CODE",  # Should be empty for success
                "message": "Some message",  # Should be empty
                "details": ""
            },
            "timestamp": "2025-07-07T10:00:00Z"
        }
        
        result = validate_bubble_compatibility(response)
        assert result["is_valid"] is False
        assert "Successful responses should have empty error" in str(result["issues"])
    
    def test_check_for_nulls(self):
        """Test null checking function."""
        obj = {
            "a": 1,
            "b": None,
            "c": {
                "d": "hello",
                "e": None
            },
            "f": [1, None, 3]
        }
        
        nulls = check_for_nulls(obj)
        assert "b" in nulls
        assert "c.e" in nulls
        assert "f[1]" in nulls
    
    def test_keyword_extraction_response_validation(self):
        """Test keyword extraction endpoint response validation."""
        # Test missing required fields
        data = {
            "jd_keywords": ["python"],
            "matched_keywords": []
            # Missing other required fields
        }
        
        issues = []
        validate_keyword_extraction_response(data, issues)
        assert len(issues) > 0
        assert any("Missing required field" in issue for issue in issues)
        
        # Test null values
        data = {
            "jd_keywords": None,  # Should be empty list
            "matched_keywords": None,  # Should be empty list
            "similarity_score": 0.85,
            "match_percentage": 85.0,
            "processing_time": 1.2,
            "cache_hit": True,
            "model_used": "gpt-4",
            "prompt_version": "1.0"
        }
        
        issues = []
        validate_keyword_extraction_response(data, issues)
        assert any("should be empty list" in issue for issue in issues)
    
    def test_field_counting(self):
        """Test field counting function."""
        obj = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            },
            "e": [1, 2, 3]
        }
        
        count = count_fields(obj)
        assert count == 5  # a, b, c, d, e