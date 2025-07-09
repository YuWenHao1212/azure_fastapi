"""
Unit tests for gap analysis retry mechanism.
Tests retry behavior when AI returns empty fields.
"""
from unittest.mock import AsyncMock, Mock, patch
import asyncio

import pytest

from src.services.gap_analysis import GapAnalysisService, check_for_empty_fields


class TestCheckForEmptyFields:
    """Test check_for_empty_fields function."""
    
    def test_detect_empty_core_strengths(self):
        """Test detection of empty CoreStrengths field."""
        response = {
            "CoreStrengths": "<ol></ol>",
            "KeyGaps": "<ol><li>Valid gap</li></ol>",
            "QuickImprovements": "<ol><li>Valid improvement</li></ol>",
            "OverallAssessment": "<p>Valid assessment</p>",
            "SkillSearchQueries": [{"skill_name": "Python"}]
        }
        empty_fields = check_for_empty_fields(response)
        assert "CoreStrengths" in empty_fields
        assert len(empty_fields) == 1
    
    def test_detect_empty_key_gaps(self):
        """Test detection of empty KeyGaps field."""
        response = {
            "CoreStrengths": "<ol><li>Valid strength</li></ol>",
            "KeyGaps": "<ol><li>Unable to analyze key gaps. Please try again.</li></ol>",
            "QuickImprovements": "<ol><li>Valid improvement</li></ol>",
            "OverallAssessment": "<p>Valid assessment</p>",
            "SkillSearchQueries": [{"skill_name": "Python"}]
        }
        empty_fields = check_for_empty_fields(response)
        assert "KeyGaps" in empty_fields
        assert len(empty_fields) == 1
    
    def test_detect_empty_quick_improvements(self):
        """Test detection of empty QuickImprovements field."""
        response = {
            "CoreStrengths": "<ol><li>Valid strength</li></ol>",
            "KeyGaps": "<ol><li>Valid gap</li></ol>",
            "QuickImprovements": "<ol></ol>",
            "OverallAssessment": "<p>Valid assessment</p>",
            "SkillSearchQueries": [{"skill_name": "Python"}]
        }
        empty_fields = check_for_empty_fields(response)
        assert "QuickImprovements" in empty_fields
        assert len(empty_fields) == 1
    
    def test_detect_empty_overall_assessment(self):
        """Test detection of empty OverallAssessment field."""
        response = {
            "CoreStrengths": "<ol><li>Valid strength</li></ol>",
            "KeyGaps": "<ol><li>Valid gap</li></ol>",
            "QuickImprovements": "<ol><li>Valid improvement</li></ol>",
            "OverallAssessment": "<p></p>",
            "SkillSearchQueries": [{"skill_name": "Python"}]
        }
        empty_fields = check_for_empty_fields(response)
        assert "OverallAssessment" in empty_fields
        assert len(empty_fields) == 1
    
    def test_detect_default_overall_assessment(self):
        """Test detection of default OverallAssessment messages."""
        default_messages = [
            "<p>Unable to generate a comprehensive assessment. Please review the individual sections above for detailed analysis.</p>",
            "<p>Unable to generate overall assessment. Please review the strengths and gaps above.</p>",
            "<p>Overall assessment not available. Please refer to the detailed analysis above.</p>"
        ]
        
        for default_msg in default_messages:
            response = {
                "CoreStrengths": "<ol><li>Valid strength</li></ol>",
                "KeyGaps": "<ol><li>Valid gap</li></ol>",
                "QuickImprovements": "<ol><li>Valid improvement</li></ol>",
                "OverallAssessment": default_msg,
                "SkillSearchQueries": [{"skill_name": "Python"}]
            }
            empty_fields = check_for_empty_fields(response)
            assert "OverallAssessment" in empty_fields, f"Failed for: {default_msg}"
    
    def test_detect_empty_skill_queries(self):
        """Test detection of empty SkillSearchQueries."""
        response = {
            "CoreStrengths": "<ol><li>Valid strength</li></ol>",
            "KeyGaps": "<ol><li>Valid gap</li></ol>",
            "QuickImprovements": "<ol><li>Valid improvement</li></ol>",
            "OverallAssessment": "<p>Valid assessment</p>",
            "SkillSearchQueries": []
        }
        empty_fields = check_for_empty_fields(response)
        assert "SkillSearchQueries" in empty_fields
        assert len(empty_fields) == 1
    
    def test_detect_multiple_empty_fields(self):
        """Test detection of multiple empty fields."""
        response = {
            "CoreStrengths": "<ol></ol>",
            "KeyGaps": "<ol><li>Unable to analyze key gaps. Please try again.</li></ol>",
            "QuickImprovements": "<ol></ol>",
            "OverallAssessment": "<p></p>",
            "SkillSearchQueries": []
        }
        empty_fields = check_for_empty_fields(response)
        assert len(empty_fields) == 5
        assert "CoreStrengths" in empty_fields
        assert "KeyGaps" in empty_fields
        assert "QuickImprovements" in empty_fields
        assert "OverallAssessment" in empty_fields
        assert "SkillSearchQueries" in empty_fields
    
    def test_all_fields_valid(self):
        """Test when all fields are valid."""
        response = {
            "CoreStrengths": "<ol><li>Valid strength</li></ol>",
            "KeyGaps": "<ol><li>Valid gap</li></ol>",
            "QuickImprovements": "<ol><li>Valid improvement</li></ol>",
            "OverallAssessment": "<p>Valid assessment</p>",
            "SkillSearchQueries": [{"skill_name": "Python"}]
        }
        empty_fields = check_for_empty_fields(response)
        assert len(empty_fields) == 0


@pytest.mark.asyncio
class TestGapAnalysisRetryMechanism:
    """Test GapAnalysisService retry mechanism."""
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    @patch('src.services.gap_analysis.monitoring_service')
    async def test_retry_on_empty_overall_assessment(
        self, mock_monitoring, mock_prompt_service, mock_get_client
    ):
        """Test retry when OverallAssessment is empty."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User prompt"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client with different responses
        mock_client = AsyncMock()
        
        # First attempt: empty OverallAssessment
        first_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths>- Python expertise</core_strengths>
                    <key_gaps>- Cloud experience</key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment></overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::Cloud services
                    </skill_development_priorities>
                    """
                }
            }]
        }
        
        # Second attempt: still empty
        second_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths>- Python expertise</core_strengths>
                    <key_gaps>- Cloud experience</key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment></overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::Cloud services
                    </skill_development_priorities>
                    """
                }
            }]
        }
        
        # Third attempt: success
        third_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths>- Python expertise</core_strengths>
                    <key_gaps>- Cloud experience</key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment>Good candidate with strong Python skills</overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::Cloud services
                    </skill_development_priorities>
                    """
                }
            }]
        }
        
        # Set up mock to return different responses on each call
        mock_client.chat_completion.side_effect = [first_response, second_response, third_response]
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock):
            # Test service
            service = GapAnalysisService()
            result = await service.analyze_gap(
                job_description="Python developer",
                resume="Python experience",
                job_keywords=["Python"],
                matched_keywords=["Python"],
                missing_keywords=[],
                language="en"
            )
        
        # Verify result is from third attempt (successful)
        assert "Good candidate with strong Python skills" in result["OverallAssessment"]
        
        # Verify retry was attempted 3 times
        assert mock_client.chat_completion.call_count == 3
        
        # Verify monitoring events were tracked
        mock_monitoring.track_event.assert_any_call(
            "GapAnalysisRetryAttempt",
            {
                "attempt": 2,
                "max_attempts": 3,
                "language": "en",
                "reason": "empty_fields"
            }
        )
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    @patch('src.services.gap_analysis.monitoring_service')
    async def test_retry_on_multiple_empty_fields(
        self, mock_monitoring, mock_prompt_service, mock_get_client
    ):
        """Test retry when multiple fields are empty."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User prompt"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        
        # First attempt: multiple empty fields
        first_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths></core_strengths>
                    <key_gaps></key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment></overall_assessment>
                    <skill_development_priorities></skill_development_priorities>
                    """
                }
            }]
        }
        
        # Second attempt: some fields filled
        second_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths>- Python expertise</core_strengths>
                    <key_gaps>- Cloud experience</key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment></overall_assessment>
                    <skill_development_priorities></skill_development_priorities>
                    """
                }
            }]
        }
        
        # Third attempt: all fields filled
        third_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths>- Python expertise</core_strengths>
                    <key_gaps>- Cloud experience</key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment>Good candidate</overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::Cloud services
                    </skill_development_priorities>
                    """
                }
            }]
        }
        
        mock_client.chat_completion.side_effect = [first_response, second_response, third_response]
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock):
            # Test service
            service = GapAnalysisService()
            result = await service.analyze_gap(
                job_description="Python developer",
                resume="Python experience",
                job_keywords=["Python"],
                matched_keywords=["Python"],
                missing_keywords=[],
                language="en"
            )
        
        # Verify all fields are filled
        assert "<li>Python expertise</li>" in result["CoreStrengths"]
        assert "<li>Cloud experience</li>" in result["KeyGaps"]
        assert "Good candidate" in result["OverallAssessment"]
        assert len(result["SkillSearchQueries"]) == 1
        
        # Verify retry was attempted 3 times
        assert mock_client.chat_completion.call_count == 3
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    @patch('src.services.gap_analysis.monitoring_service')
    async def test_fallback_after_max_retries(
        self, mock_monitoring, mock_prompt_service, mock_get_client
    ):
        """Test fallback messages after all retries fail."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User prompt"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client - all attempts return empty fields
        mock_client = AsyncMock()
        empty_response = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths></core_strengths>
                    <key_gaps></key_gaps>
                    <quick_improvements></quick_improvements>
                    <overall_assessment></overall_assessment>
                    <skill_development_priorities></skill_development_priorities>
                    """
                }
            }]
        }
        
        # All three attempts return empty
        mock_client.chat_completion.return_value = empty_response
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock):
            # Test service
            service = GapAnalysisService()
            result = await service.analyze_gap(
                job_description="Python developer",
                resume="Python experience",
                job_keywords=["Python"],
                matched_keywords=["Python"],
                missing_keywords=[],
                language="en"
            )
        
        # Verify fallback messages are used
        assert result["CoreStrengths"] == "<ol><li>Unable to analyze core strengths. Please try again.</li></ol>"
        assert result["KeyGaps"] == "<ol><li>Unable to analyze key gaps. Please try again.</li></ol>"
        assert result["QuickImprovements"] == "<ol><li>Unable to analyze quick improvements. Please try again.</li></ol>"
        assert result["OverallAssessment"] == "<p>Unable to generate a comprehensive assessment. Please review the individual sections above for detailed analysis.</p>"
        assert result["SkillSearchQueries"] == []
        
        # Verify all 3 attempts were made
        assert mock_client.chat_completion.call_count == 3
        
        # Verify retry exhausted event was tracked
        mock_monitoring.track_event.assert_any_call(
            "GapAnalysisRetryExhausted",
            {
                "attempts": 3,
                "empty_fields": "CoreStrengths,KeyGaps,QuickImprovements,OverallAssessment,SkillSearchQueries",
                "language": "en"
            }
        )
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    @patch('src.services.gap_analysis.monitoring_service')
    async def test_retry_on_network_error(
        self, mock_monitoring, mock_prompt_service, mock_get_client
    ):
        """Test retry on retryable network errors."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User prompt"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        
        # First attempt: network error
        mock_client.chat_completion.side_effect = [
            Exception("Connection timeout"),
            Exception("503 Service Unavailable"),
            {
                'choices': [{
                    'message': {
                        'content': """
                        <core_strengths>- Python expertise</core_strengths>
                        <key_gaps>- Cloud experience</key_gaps>
                        <quick_improvements>- Add certifications</quick_improvements>
                        <overall_assessment>Good candidate</overall_assessment>
                        <skill_development_priorities>
                        SKILL_1::AWS::TECHNICAL::Cloud services
                        </skill_development_priorities>
                        """
                    }
                }]
            }
        ]
        
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock):
            # Test service
            service = GapAnalysisService()
            result = await service.analyze_gap(
                job_description="Python developer",
                resume="Python experience",
                job_keywords=["Python"],
                matched_keywords=["Python"],
                missing_keywords=[],
                language="en"
            )
        
        # Verify successful result after retries
        assert "Good candidate" in result["OverallAssessment"]
        
        # Verify 3 attempts were made
        assert mock_client.chat_completion.call_count == 3
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    async def test_no_retry_on_non_retryable_error(
        self, mock_prompt_service, mock_get_client
    ):
        """Test no retry on non-retryable errors."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User prompt"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client with non-retryable error
        mock_client = AsyncMock()
        mock_client.chat_completion.side_effect = ValueError("Invalid API key")
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Test service
        service = GapAnalysisService()
        
        with pytest.raises(ValueError, match="Invalid API key"):
            await service.analyze_gap(
                job_description="Python developer",
                resume="Python experience",
                job_keywords=["Python"],
                matched_keywords=["Python"],
                missing_keywords=[],
                language="en"
            )
        
        # Verify only one attempt was made (no retry)
        assert mock_client.chat_completion.call_count == 1
    
    @patch('src.services.gap_analysis.get_azure_openai_client')
    @patch('src.services.gap_analysis.UnifiedPromptService')
    @patch('src.services.gap_analysis.monitoring_service')
    async def test_success_on_first_attempt(
        self, mock_monitoring, mock_prompt_service, mock_get_client
    ):
        """Test no retry when first attempt succeeds."""
        # Mock prompt service
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt = lambda: "System prompt"
        mock_prompt_config.format_user_prompt = lambda **kwargs: "User prompt"
        
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock OpenAI client with successful response
        mock_client = AsyncMock()
        mock_client.chat_completion.return_value = {
            'choices': [{
                'message': {
                    'content': """
                    <core_strengths>- Python expertise</core_strengths>
                    <key_gaps>- Cloud experience</key_gaps>
                    <quick_improvements>- Add certifications</quick_improvements>
                    <overall_assessment>Good candidate</overall_assessment>
                    <skill_development_priorities>
                    SKILL_1::AWS::TECHNICAL::Cloud services
                    </skill_development_priorities>
                    """
                }
            }]
        }
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Test service
        service = GapAnalysisService()
        result = await service.analyze_gap(
            job_description="Python developer",
            resume="Python experience",
            job_keywords=["Python"],
            matched_keywords=["Python"],
            missing_keywords=[],
            language="en"
        )
        
        # Verify successful result
        assert "Good candidate" in result["OverallAssessment"]
        
        # Verify only one attempt was made
        assert mock_client.chat_completion.call_count == 1
        
        # Verify no retry events were tracked
        assert not any(
            call[0][0] == "GapAnalysisRetryAttempt" 
            for call in mock_monitoring.track_event.call_args_list
        )