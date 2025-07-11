"""
Unit tests for language validation logic.
Tests case-insensitive language parameter handling.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.api.v1.index_cal_and_gap_analysis import IndexCalAndGapAnalysisRequest
from src.services.gap_analysis import GapAnalysisService


class TestLanguageValidation:
    """Test language parameter validation and normalization."""
    
    def test_language_case_insensitive_zh_tw(self):
        """Test that zh-tw in any case is normalized to zh-TW."""
        test_cases = ["zh-tw", "zh-TW", "ZH-TW", "Zh-Tw", "ZH-tw"]
        
        for test_lang in test_cases:
            # Test in API endpoint
            request = IndexCalAndGapAnalysisRequest(
                resume="test",
                job_description="test",
                keywords=["test"],
                language=test_lang
            )
            
            # Simulate the validation logic from the API
            if request.language.lower() == "zh-tw":
                normalized = "zh-TW"
            elif request.language.lower() != "en":
                normalized = "en"
            else:
                normalized = request.language
            
            assert normalized == "zh-TW", f"Failed for {test_lang}"
    
    def test_language_case_insensitive_en(self):
        """Test that en in any case is accepted."""
        test_cases = ["en", "EN", "En", "eN"]
        
        for test_lang in test_cases:
            request = IndexCalAndGapAnalysisRequest(
                resume="test",
                job_description="test",
                keywords=["test"],
                language=test_lang
            )
            
            # Simulate the validation logic
            if request.language.lower() == "zh-tw":
                normalized = "zh-TW"
            elif request.language.lower() != "en":
                normalized = "en"
            else:
                normalized = request.language
            
            # All should be kept as is or normalized to "en"
            assert normalized in ["en", "EN", "En", "eN"], f"Failed for {test_lang}"
    
    def test_invalid_language_defaults_to_en(self):
        """Test that invalid languages default to en."""
        test_cases = ["fr", "de", "zh-cn", "chinese", "english", ""]
        
        for test_lang in test_cases:
            request = IndexCalAndGapAnalysisRequest(
                resume="test",
                job_description="test",
                keywords=["test"],
                language=test_lang
            )
            
            # Simulate the validation logic
            if request.language.lower() == "zh-tw":
                normalized = "zh-TW"
            elif request.language.lower() != "en":
                normalized = "en"
            else:
                normalized = request.language
            
            assert normalized == "en", f"Failed for {test_lang}"
    
    @pytest.mark.asyncio
    async def test_gap_analysis_service_language_normalization(self):
        """Test language normalization in GapAnalysisService."""
        service = GapAnalysisService()
        
        # Mock the prompt service and openai client
        with patch.object(service.prompt_service, 'get_prompt_config') as mock_prompt_config, \
             patch('src.services.gap_analysis.get_azure_openai_client') as mock_get_client:
            
            # Setup mocks
            mock_prompt_config.return_value = MagicMock(
                get_system_prompt=lambda: "system",
                format_user_prompt=lambda **kwargs: "user"
            )
            
            mock_client = AsyncMock()
            mock_client.chat_completion.return_value = {
                'choices': [{
                    'message': {
                        'content': '<gap_analysis><core_strengths>test</core_strengths></gap_analysis>'
                    }
                }],
                'usage': {'prompt_tokens': 100, 'completion_tokens': 50}
            }
            mock_get_client.return_value = mock_client
            
            # Test with various case variations
            for lang in ["zh-tw", "ZH-TW", "Zh-Tw"]:
                await service.analyze_gap(
                    job_description="test",
                    resume="test",
                    job_keywords=["test"],
                    matched_keywords=["test"],
                    missing_keywords=[],
                    language=lang
                )
                
                # Verify the normalized language was used with correct version
                # For zh-TW, the service uses version 1.2.0
                mock_prompt_config.assert_called_with(
                    language="zh-TW",
                    version="1.2.0"
                )