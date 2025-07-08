"""
Unit tests for gap analysis service.
Tests gap analysis functionality and LLM response parsing.
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.gap_analysis import (
    GapAnalysisService,
    clean_and_process_lines,
    format_gap_analysis_html,
    parse_gap_response,
    parse_skill_development_priorities,
)


class TestCleanAndProcessLines:
    """Test clean_and_process_lines function."""
    
    def test_process_bullet_points(self):
        """Test bullet point processing."""
        content = """
        - First point
        * Second point
        • Third point
        """
        result = clean_and_process_lines(content)
        
        assert len(result) == 3
        assert "First point" in result[0]
        assert "Second point" in result[1]
        assert "Third point" in result[2]
    
    def test_process_numbered_list(self):
        """Test numbered list processing."""
        content = """
        1. First item
        2. Second item
        3. Third item
        """
        result = clean_and_process_lines(content)
        
        assert len(result) == 3
        assert "First item" in result[0]
        assert "Second item" in result[1]
    
    def test_markdown_conversion(self):
        """Test markdown conversion in lines."""
        content = "- This is **bold** text"
        result = clean_and_process_lines(content)
        
        assert len(result) == 1
        assert "<strong>bold</strong>" in result[0]
    
    def test_empty_content(self):
        """Test empty content handling."""
        assert clean_and_process_lines(None) == []
        assert clean_and_process_lines("") == []
        assert clean_and_process_lines("   ") == []


class TestParseSkillDevelopmentPriorities:
    """Test parse_skill_development_priorities function."""
    
    def test_parse_valid_skills(self):
        """Test parsing valid skill format."""
        content = """
        SKILL_1::Python Programming::TECHNICAL::Advanced Python including async/await and decorators
        SKILL_2::Project Management::NON_TECHNICAL::Agile methodologies and team leadership
        SKILL_3::Docker::TECHNICAL::Container orchestration with Kubernetes
        """
        
        result = parse_skill_development_priorities(content)
        
        assert len(result) == 3
        
        assert result[0]["skill_name"] == "Python Programming"
        assert result[0]["skill_category"] == "TECHNICAL"
        assert "async/await" in result[0]["description"]
        
        assert result[1]["skill_name"] == "Project Management"
        assert result[1]["skill_category"] == "NON_TECHNICAL"
        
        assert result[2]["skill_name"] == "Docker"
        assert result[2]["skill_category"] == "TECHNICAL"
    
    def test_invalid_category_defaults(self):
        """Test invalid category defaults to TECHNICAL."""
        content = "SKILL_1::Python::INVALID::Python programming"
        result = parse_skill_development_priorities(content)
        
        assert result[0]["skill_category"] == "TECHNICAL"
    
    def test_malformed_skill_lines(self):
        """Test handling of malformed skill lines."""
        content = """
        SKILL_1::Python::TECHNICAL::Valid skill
        Invalid line without proper format
        SKILL_2::Missing::Parts
        ::Empty::Skill::Name
        """
        
        result = parse_skill_development_priorities(content)
        
        # Should parse both valid skill lines
        # SKILL_1::Python::TECHNICAL::Valid skill - valid
        # SKILL_2::Missing::Parts - invalid (not enough parts)
        # ::Empty::Skill::Name - parses as "Empty" skill name
        assert len(result) == 2
        assert result[0]["skill_name"] == "Python"
        assert result[1]["skill_name"] == "Empty"
    
    def test_empty_content(self):
        """Test empty content handling."""
        assert parse_skill_development_priorities("") == []
        assert parse_skill_development_priorities(None) == []


class TestParseGapResponse:
    """Test parse_gap_response function."""
    
    def test_parse_complete_response(self):
        """Test parsing a complete gap analysis response."""
        content = """
        <gap_analysis>
        <core_strengths>
        - Strong Python programming skills
        - Experience with REST APIs
        - Good communication skills
        </core_strengths>
        
        <key_gaps>
        - Limited experience with cloud platforms
        - No formal project management training
        - Lack of frontend development skills
        </key_gaps>
        
        <quick_improvements>
        - Add AWS/Azure certifications to resume
        - Highlight any team lead experience
        - Include personal projects with React/Vue
        </quick_improvements>
        
        <overall_assessment>
        The candidate shows strong backend development skills with Python.
        However, they need to develop cloud and frontend skills for this full-stack role.
        </overall_assessment>
        
        <skill_development_priorities>
        SKILL_1::AWS/Azure::TECHNICAL::Cloud platform expertise including deployment and scaling
        SKILL_2::React::TECHNICAL::Modern frontend framework for full-stack development
        SKILL_3::Agile/Scrum::NON_TECHNICAL::Project management methodologies
        </skill_development_priorities>
        </gap_analysis>
        """
        
        result = parse_gap_response(content)
        
        assert len(result["strengths"]) == 3
        assert "Python programming" in result["strengths"][0]
        
        assert len(result["gaps"]) == 3
        assert "cloud platforms" in result["gaps"][0]
        
        assert len(result["improvements"]) == 3
        assert "AWS/Azure certifications" in result["improvements"][0]
        
        assert "backend development skills" in result["assessment"]
        assert "full-stack role" in result["assessment"]
        
        assert len(result["skill_queries"]) == 3
        assert result["skill_queries"][0]["skill_name"] == "AWS/Azure"
    
    def test_parse_partial_response(self):
        """Test parsing response with missing sections."""
        content = """
        <core_strengths>
        - Python skills
        </core_strengths>
        
        <key_gaps>
        - Cloud experience
        </key_gaps>
        """
        
        result = parse_gap_response(content)
        
        assert len(result["strengths"]) == 1
        assert len(result["gaps"]) == 1
        assert len(result["improvements"]) == 0
        assert result["assessment"] == ""
        assert len(result["skill_queries"]) == 0
    
    def test_parse_empty_response(self):
        """Test parsing empty or malformed response."""
        result = parse_gap_response("")
        
        assert result["strengths"] == []
        assert result["gaps"] == []
        assert result["improvements"] == []
        assert result["assessment"] == ""
        assert result["skill_queries"] == []


class TestFormatGapAnalysisHtml:
    """Test format_gap_analysis_html function."""
    
    def test_format_complete_analysis(self):
        """Test formatting complete gap analysis."""
        parsed_response = {
            "strengths": ["Strong Python skills", "API development"],
            "gaps": ["No cloud experience", "Limited frontend skills"],
            "improvements": ["Add certifications", "Build portfolio"],
            "assessment": "Good backend developer needing cloud skills",
            "skill_queries": [
                {
                    "skill_name": "AWS",
                    "skill_category": "TECHNICAL",
                    "description": "Cloud services"
                }
            ]
        }
        
        result = format_gap_analysis_html(parsed_response)
        
        assert "<ol>" in result["CoreStrengths"]
        assert "<li>Strong Python skills</li>" in result["CoreStrengths"]
        assert "<li>API development</li>" in result["CoreStrengths"]
        
        assert "<ol>" in result["KeyGaps"]
        assert "<li>No cloud experience</li>" in result["KeyGaps"]
        
        assert "<ol>" in result["QuickImprovements"]
        assert "<li>Add certifications</li>" in result["QuickImprovements"]
        
        assert "<p>" in result["OverallAssessment"]
        assert "Good backend developer" in result["OverallAssessment"]
        
        assert len(result["SkillSearchQueries"]) == 1
        assert result["SkillSearchQueries"][0]["skill_name"] == "AWS"
    
    def test_format_empty_sections(self):
        """Test formatting with empty sections."""
        parsed_response = {
            "strengths": [],
            "gaps": [],
            "improvements": [],
            "assessment": "",
            "skill_queries": []
        }
        
        result = format_gap_analysis_html(parsed_response)
        
        assert result["CoreStrengths"] == "<ol></ol>"
        assert result["KeyGaps"] == "<ol></ol>"
        assert result["QuickImprovements"] == "<ol></ol>"
        assert result["OverallAssessment"] == "<p></p>"
        assert result["SkillSearchQueries"] == []


@pytest.mark.asyncio
class TestGapAnalysisService:
    """Test GapAnalysisService class."""
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    async def test_analyze_gap_english(self, mock_prompt_service, mock_get_client):
        """Test gap analysis with English language."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User: job description and resume"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = {
            'choices': [{
                'message': {
                    'content': """
                    <gap_analysis>
                    <core_strengths>
                    - Python expertise
                    </core_strengths>
                    <key_gaps>
                    - Cloud experience
                    </key_gaps>
                    <quick_improvements>
                    - Add certifications
                    </quick_improvements>
                    <overall_assessment>
                    Good candidate
                    </overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::Cloud services
                    </skill_development_priorities>
                    </gap_analysis>
                    """
                }
            }]
        }
        mock_client.chat_completion.return_value = mock_response
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Test service
        service = GapAnalysisService()
        result = await service.analyze_gap(
            job_description="Python developer needed",
            resume="Experienced Python developer",
            job_keywords=["Python", "AWS"],
            matched_keywords=["Python"],
            missing_keywords=["AWS"],
            language="en"
        )
        
        assert "<li>Python expertise</li>" in result["CoreStrengths"]
        assert "<li>Cloud experience</li>" in result["KeyGaps"]
        assert "<li>Add certifications</li>" in result["QuickImprovements"]
        assert "Good candidate" in result["OverallAssessment"]
        assert len(result["SkillSearchQueries"]) == 1
        assert result["SkillSearchQueries"][0]["skill_name"] == "AWS"
        
        # Verify prompt service was called with correct language
        mock_prompt_instance.get_prompt_config.assert_called_with(
            language="en",
            version="1.0.0"
        )
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    async def test_analyze_gap_chinese(self, mock_prompt_service, mock_get_client):
        """Test gap analysis with Chinese language."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "系統提示"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "用戶：職位描述和簡歷"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = {
            'choices': [{
                'message': {
                    'content': """
                    <gap_analysis>
                    <core_strengths>
                    - Python 專業知識
                    </core_strengths>
                    <key_gaps>
                    - 雲端經驗不足
                    </key_gaps>
                    <quick_improvements>
                    - 增加認證
                    </quick_improvements>
                    <overall_assessment>
                    優秀的候選人
                    </overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::雲端服務
                    </skill_development_priorities>
                    </gap_analysis>
                    """
                }
            }]
        }
        mock_client.chat_completion.return_value = mock_response
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Test service
        service = GapAnalysisService()
        result = await service.analyze_gap(
            job_description="需要 Python 開發者",
            resume="經驗豐富的 Python 開發者",
            job_keywords=["Python", "AWS"],
            matched_keywords=["Python"],
            missing_keywords=["AWS"],
            language="zh-TW"
        )
        
        assert "Python 專業知識" in result["CoreStrengths"]
        assert "雲端經驗不足" in result["KeyGaps"]
        assert "增加認證" in result["QuickImprovements"]
        assert "優秀的候選人" in result["OverallAssessment"]
        
        # Verify prompt service was called with correct language
        mock_prompt_instance.get_prompt_config.assert_called_with(
            language="zh-TW",
            version="1.0.0"
        )
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    async def test_analyze_gap_invalid_language(self, mock_prompt_service, mock_get_client):
        """Test gap analysis with invalid language defaults to English."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User: job description"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = {'choices': [{'message': {'content': '<gap_analysis></gap_analysis>'}}]}
        mock_client.chat_completion.return_value = mock_response
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Test service with invalid language
        service = GapAnalysisService()
        await service.analyze_gap(
            job_description="Job",
            resume="Resume",
            job_keywords=[],
            matched_keywords=[],
            missing_keywords=[],
            language="fr"  # Invalid language
        )
        
        # Should default to English
        mock_prompt_instance.get_prompt_config.assert_called_with(
            language="en",
            version="1.0.0"
        )