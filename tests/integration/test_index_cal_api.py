"""
Integration tests for index calculation and gap analysis API endpoints.
Tests the complete API flow including request/response handling.
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestIndexCalculationAPI:
    """Test /api/v1/index-calculation endpoint."""
    
    @patch('src.api.v1.index_calculation.IndexCalculationService')
    def test_index_calculation_success(self, mock_service_class, client):
        """Test successful index calculation."""
        # Mock service
        mock_service = Mock()
        mock_service.calculate_index = AsyncMock(return_value={
            "raw_similarity_percentage": 75,
            "similarity_percentage": 85,
            "keyword_coverage": {
                "total_keywords": 10,
                "covered_count": 7,
                "coverage_percentage": 70,
                "covered_keywords": ["Python", "API", "SQL"],
                "missed_keywords": ["Java", "React", "Docker"]
            }
        })
        mock_service_class.return_value = mock_service
        
        # Test request
        response = client.post(
            "/api/v1/index-calculation",
            json={
                "resume": "Python developer with API and SQL experience",
                "job_description": "Looking for full-stack developer",
                "keywords": ["Python", "API", "SQL", "Java", "React", "Docker"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["raw_similarity_percentage"] == 75
        assert data["data"]["similarity_percentage"] == 85
        assert data["data"]["keyword_coverage"]["coverage_percentage"] == 70
        assert len(data["data"]["keyword_coverage"]["covered_keywords"]) == 3
        assert len(data["data"]["keyword_coverage"]["missed_keywords"]) == 3
    
    @patch('src.api.v1.index_calculation.IndexCalculationService')
    def test_index_calculation_with_string_keywords(self, mock_service_class, client):
        """Test index calculation with comma-separated keywords."""
        # Mock service
        mock_service = Mock()
        mock_service.calculate_index = AsyncMock(return_value={
            "raw_similarity_percentage": 80,
            "similarity_percentage": 90,
            "keyword_coverage": {
                "total_keywords": 3,
                "covered_count": 2,
                "coverage_percentage": 67,
                "covered_keywords": ["Python", "Django"],
                "missed_keywords": ["React"]
            }
        })
        mock_service_class.return_value = mock_service
        
        # Test request with string keywords
        response = client.post(
            "/api/v1/index-calculation",
            json={
                "resume": "Python Django developer",
                "job_description": "Full-stack position",
                "keywords": "Python, Django, React"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["keyword_coverage"]["coverage_percentage"] == 67
    
    def test_index_calculation_validation_error(self, client):
        """Test validation error handling."""
        # Missing required fields
        response = client.post(
            "/api/v1/index-calculation",
            json={
                "resume": "Python developer"
                # Missing job_description and keywords
            }
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    @patch('src.api.v1.index_calculation.IndexCalculationService')
    def test_index_calculation_service_error(self, mock_service_class, client):
        """Test service error handling."""
        # Mock service error
        mock_service = Mock()
        mock_service.calculate_index = AsyncMock(
            side_effect=Exception("Embedding service unavailable")
        )
        mock_service_class.return_value = mock_service
        
        response = client.post(
            "/api/v1/index-calculation",
            json={
                "resume": "Test resume",
                "job_description": "Test job",
                "keywords": ["test"]
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_ERROR"


class TestIndexCalAndGapAnalysisAPI:
    """Test /api/v1/index-cal-and-gap-analysis endpoint."""
    
    @patch('src.api.v1.index_cal_and_gap_analysis.GapAnalysisService')
    @patch('src.api.v1.index_cal_and_gap_analysis.IndexCalculationService')
    def test_combined_analysis_success(self, mock_index_class, mock_gap_class, client):
        """Test successful combined analysis."""
        # Mock index calculation service
        mock_index_service = Mock()
        mock_index_service.calculate_index = AsyncMock(return_value={
            "raw_similarity_percentage": 75,
            "similarity_percentage": 85,
            "keyword_coverage": {
                "total_keywords": 5,
                "covered_count": 3,
                "coverage_percentage": 60,
                "covered_keywords": ["Python", "API", "SQL"],
                "missed_keywords": ["AWS", "Docker"]
            }
        })
        mock_index_class.return_value = mock_index_service
        
        # Mock gap analysis service
        mock_gap_service = Mock()
        mock_gap_service.analyze_gap = AsyncMock(return_value={
            "CoreStrengths": "<ol><li>Strong Python skills</li></ol>",
            "KeyGaps": "<ol><li>No cloud experience</li></ol>",
            "QuickImprovements": "<ol><li>Add AWS certification</li></ol>",
            "OverallAssessment": "<p>Good backend developer</p>",
            "SkillSearchQueries": [
                {
                    "skill_name": "AWS",
                    "skill_category": "TECHNICAL",
                    "description": "Cloud platform expertise"
                }
            ]
        })
        mock_gap_class.return_value = mock_gap_service
        
        # Test request
        response = client.post(
            "/api/v1/index-cal-and-gap-analysis",
            json={
                "resume": "Python developer with API and SQL experience",
                "job_description": "Looking for cloud-native developer",
                "keywords": ["Python", "API", "SQL", "AWS", "Docker"],
                "language": "en"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # Check index calculation results
        assert data["data"]["raw_similarity_percentage"] == 75
        assert data["data"]["similarity_percentage"] == 85
        assert data["data"]["keyword_coverage"]["coverage_percentage"] == 60
        
        # Check gap analysis results
        gap_analysis = data["data"]["gap_analysis"]
        assert "<li>Strong Python skills</li>" in gap_analysis["CoreStrengths"]
        assert "<li>No cloud experience</li>" in gap_analysis["KeyGaps"]
        assert "<li>Add AWS certification</li>" in gap_analysis["QuickImprovements"]
        assert "Good backend developer" in gap_analysis["OverallAssessment"]
        assert len(gap_analysis["SkillSearchQueries"]) == 1
        assert gap_analysis["SkillSearchQueries"][0]["skill_name"] == "AWS"
    
    @patch('src.api.v1.index_cal_and_gap_analysis.GapAnalysisService')
    @patch('src.api.v1.index_cal_and_gap_analysis.IndexCalculationService')
    def test_combined_analysis_chinese(self, mock_index_class, mock_gap_class, client):
        """Test combined analysis with Chinese language."""
        # Mock services
        mock_index_service = Mock()
        mock_index_service.calculate_index = AsyncMock(return_value={
            "raw_similarity_percentage": 80,
            "similarity_percentage": 90,
            "keyword_coverage": {
                "total_keywords": 3,
                "covered_count": 2,
                "coverage_percentage": 67,
                "covered_keywords": ["Python", "Django"],
                "missed_keywords": ["React"]
            }
        })
        mock_index_class.return_value = mock_index_service
        
        mock_gap_service = Mock()
        mock_gap_service.analyze_gap = AsyncMock(return_value={
            "CoreStrengths": "<ol><li>Python 專業知識</li></ol>",
            "KeyGaps": "<ol><li>缺乏前端經驗</li></ol>",
            "QuickImprovements": "<ol><li>學習 React</li></ol>",
            "OverallAssessment": "<p>優秀的後端開發者</p>",
            "SkillSearchQueries": []
        })
        mock_gap_class.return_value = mock_gap_service
        
        # Test request with Chinese
        response = client.post(
            "/api/v1/index-cal-and-gap-analysis",
            json={
                "resume": "Python Django 開發者",
                "job_description": "尋找全端開發者",
                "keywords": "Python, Django, React",
                "language": "zh-TW"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        gap_analysis = data["data"]["gap_analysis"]
        assert "Python 專業知識" in gap_analysis["CoreStrengths"]
        assert "缺乏前端經驗" in gap_analysis["KeyGaps"]
        
        # Verify language was passed to gap analysis
        mock_gap_service.analyze_gap.assert_called_once()
        call_args = mock_gap_service.analyze_gap.call_args[1]
        assert call_args["language"] == "zh-TW"
    
    @patch('src.api.v1.index_cal_and_gap_analysis.GapAnalysisService')
    @patch('src.api.v1.index_cal_and_gap_analysis.IndexCalculationService')
    def test_combined_analysis_default_language(self, mock_index_class, mock_gap_class, client):
        """Test that invalid language defaults to English."""
        # Mock services
        mock_index_service = Mock()
        mock_index_service.calculate_index = AsyncMock(return_value={
            "raw_similarity_percentage": 70,
            "similarity_percentage": 80,
            "keyword_coverage": {
                "total_keywords": 1,
                "covered_count": 1,
                "coverage_percentage": 100,
                "covered_keywords": ["Python"],
                "missed_keywords": []
            }
        })
        mock_index_class.return_value = mock_index_service
        
        mock_gap_service = Mock()
        mock_gap_service.analyze_gap = AsyncMock(return_value={
            "CoreStrengths": "<ol></ol>",
            "KeyGaps": "<ol></ol>",
            "QuickImprovements": "<ol></ol>",
            "OverallAssessment": "<p></p>",
            "SkillSearchQueries": []
        })
        mock_gap_class.return_value = mock_gap_service
        
        # Test without language parameter
        response = client.post(
            "/api/v1/index-cal-and-gap-analysis",
            json={
                "resume": "Python developer",
                "job_description": "Python role",
                "keywords": ["Python"]
                # No language specified
            }
        )
        
        assert response.status_code == 200
        
        # Should default to "en"
        call_args = mock_gap_service.analyze_gap.call_args[1]
        assert call_args["language"] == "en"
    
    def test_combined_analysis_validation_error(self, client):
        """Test validation error handling."""
        # Missing required fields
        response = client.post(
            "/api/v1/index-cal-and-gap-analysis",
            json={
                "resume": "Test resume"
                # Missing other required fields
            }
        )
        
        assert response.status_code == 422
    
    @patch('src.api.v1.index_cal_and_gap_analysis.IndexCalculationService')
    def test_combined_analysis_service_error(self, mock_index_class, client):
        """Test service error handling."""
        # Mock service error
        mock_index_service = Mock()
        mock_index_service.calculate_index = AsyncMock(
            side_effect=Exception("Service unavailable")
        )
        mock_index_class.return_value = mock_index_service
        
        response = client.post(
            "/api/v1/index-cal-and-gap-analysis",
            json={
                "resume": "Test",
                "job_description": "Test",
                "keywords": ["test"],
                "language": "en"
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "error" in data


class TestBubbleIOCompatibility:
    """Test Bubble.io compatibility requirements."""
    
    @patch('src.api.v1.index_calculation.IndexCalculationService')
    def test_response_structure_consistency(self, mock_service_class, client):
        """Test that response structure is consistent for Bubble.io."""
        # Mock service
        mock_service = Mock()
        mock_service.calculate_index = AsyncMock(return_value={
            "raw_similarity_percentage": 0,
            "similarity_percentage": 0,
            "keyword_coverage": {
                "total_keywords": 0,
                "covered_count": 0,
                "coverage_percentage": 0,
                "covered_keywords": [],
                "missed_keywords": []
            }
        })
        mock_service_class.return_value = mock_service
        
        # Test empty/zero values
        response = client.post(
            "/api/v1/index-calculation",
            json={
                "resume": "",
                "job_description": "",
                "keywords": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all fields exist even with empty data
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert "timestamp" in data
        
        # Verify data structure
        assert "raw_similarity_percentage" in data["data"]
        assert "similarity_percentage" in data["data"]
        assert "keyword_coverage" in data["data"]
        
        # Verify no null values (Bubble.io requirement)
        assert data["data"]["raw_similarity_percentage"] == 0
        assert data["data"]["keyword_coverage"]["covered_keywords"] == []
        assert data["data"]["keyword_coverage"]["missed_keywords"] == []