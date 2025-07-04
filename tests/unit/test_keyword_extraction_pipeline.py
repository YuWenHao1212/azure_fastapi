"""
Unit tests for Keyword Extraction Pipeline - Consolidated service and prompt management tests.
Tests the complete pipeline including keyword extraction, prompt management, and service integration.
Combines tests from test_keyword_extraction_service.py and test_unified_prompt_service.py.
"""
import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from pathlib import Path

from src.services.keyword_extraction_v2 import KeywordExtractionServiceV2
from src.services.keyword_extraction import KeywordExtractionService
from src.services.unified_prompt_service import UnifiedPromptService, get_unified_prompt_service
from src.models.keyword_extraction import KeywordExtractionRequest, KeywordExtractionData
from src.models.prompt_config import PromptConfig, LLMConfig, PromptMetadata
from src.models.response import UnifiedResponse, ErrorDetail


@pytest.mark.unit
class TestKeywordExtractionPipeline:
    """Test complete keyword extraction pipeline."""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "keywords": [
                            "Python", "FastAPI", "Backend Development",
                            "REST API", "Microservices", "Docker",
                            "PostgreSQL", "Git", "CI/CD",
                            "Agile", "Machine Learning", "AWS"
                        ]
                    })
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
    
    @pytest.mark.asyncio
    async def test_full_extraction_pipeline(self, mock_openai_response):
        """Test complete extraction pipeline from request to response."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            mock_chat.return_value = mock_openai_response
            
            service = KeywordExtractionServiceV2()
            
            request_data = {
                "job_description": "We are seeking a Senior Python Developer with expertise in FastAPI and backend development...",
                "max_keywords": 12,
                "include_standardization": True,
                "use_multi_round_validation": True
            }
            
            result = await service.process(request_data)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "keywords" in result
            assert "keyword_count" in result
            assert "confidence_score" in result
            assert "extraction_method" in result
            assert "processing_time_ms" in result
            
            # Verify keywords
            keywords = result["keywords"]
            assert isinstance(keywords, list)
            assert len(keywords) <= 12  # Should respect max_keywords
            assert all(isinstance(k, str) for k in keywords)
    
    @pytest.mark.asyncio
    async def test_two_round_intersection_algorithm(self):
        """Test 2-round intersection algorithm with different responses."""
        # Mock different responses for round 1 and round 2
        round1_keywords = ["Python", "FastAPI", "Docker", "PostgreSQL", "Git"]
        round2_keywords = ["Python", "FastAPI", "Backend", "PostgreSQL", "AWS"]
        intersection = ["Python", "FastAPI", "PostgreSQL"]  # Common keywords
        
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            # Configure mock to return different results for each call
            mock_chat.side_effect = [
                {"choices": [{"message": {"content": json.dumps({"keywords": round1_keywords})}}]},
                {"choices": [{"message": {"content": json.dumps({"keywords": round2_keywords})}}]}
            ]
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Test job description",
                "max_keywords": 10,
                "use_multi_round_validation": True
            })
            
            # Should prioritize intersection keywords
            for keyword in intersection:
                assert keyword in result["keywords"]
            
            # Should have intersection stats
            assert "intersection_stats" in result
            stats = result["intersection_stats"]
            assert stats["intersection_count"] == len(intersection)
            assert stats["round1_count"] == len(round1_keywords)
            assert stats["round2_count"] == len(round2_keywords)
    
    @pytest.mark.asyncio
    async def test_standardization_integration(self):
        """Test keyword standardization in the pipeline."""
        raw_keywords = ["ML", "AI", "NLP", "React.js", "node.js", "python"]
        
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            mock_chat.return_value = {
                "choices": [{"message": {"content": json.dumps({"keywords": raw_keywords})}}]
            }
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Looking for ML engineer with React.js skills",
                "max_keywords": 10,
                "include_standardization": True
            })
            
            # Should have standardized keywords
            keywords = result["keywords"]
            assert "Machine Learning" in keywords or "ML" in keywords
            assert "React" in keywords or "React.js" in keywords
            
            # Should have standardization info
            if "standardized_terms" in result:
                assert isinstance(result["standardized_terms"], list)


@pytest.mark.unit
class TestPromptManagement:
    """Test prompt management in the extraction pipeline."""
    
    def test_unified_prompt_service_initialization(self):
        """Test UnifiedPromptService initialization."""
        service = UnifiedPromptService()
        
        assert service.SUPPORTED_LANGUAGES == ["en", "zh-TW"]
        assert service.TASK_PATH == "keyword_extraction"
        assert service._cache == {}
        assert service.simple_prompt_manager is not None
    
    @patch('src.services.unified_prompt_service.SimplePromptManager.load_prompt_config_by_filename')
    def test_multilingual_prompt_loading(self, mock_load_config):
        """Test loading prompts for different languages."""
        # Mock English prompt
        en_config = Mock(spec=PromptConfig)
        en_config.get_user_prompt.return_value = "Extract keywords from: {job_description}"
        en_config.get_system_prompt.return_value = "You are a keyword extraction assistant."
        en_config.llm_config = Mock(spec=LLMConfig)
        
        # Mock Chinese prompt
        zh_config = Mock(spec=PromptConfig)
        zh_config.get_user_prompt.return_value = "從以下提取關鍵字: {job_description}"
        zh_config.get_system_prompt.return_value = "您是關鍵字提取助手。"
        zh_config.llm_config = Mock(spec=LLMConfig)
        
        mock_load_config.side_effect = [en_config, zh_config]
        
        service = UnifiedPromptService()
        
        # Test English prompt
        en_prompt, _ = service.get_prompt_with_config(
            language="en",
            version="1.3.0",
            variables={"job_description": "Test"}
        )
        assert "You are a keyword extraction assistant" in en_prompt
        
        # Test Chinese prompt
        zh_prompt, _ = service.get_prompt_with_config(
            language="zh-TW",
            version="1.3.0",
            variables={"job_description": "測試"}
        )
        assert "您是關鍵字提取助手" in zh_prompt
    
    def test_prompt_version_management(self):
        """Test prompt version selection and caching."""
        service = UnifiedPromptService()
        
        with patch.object(service.simple_prompt_manager, 'load_prompt_config_by_filename') as mock_load:
            mock_config = Mock(spec=PromptConfig)
            mock_config.get_user_prompt.return_value = "Test prompt"
            mock_config.get_system_prompt.return_value = None
            mock_config.llm_config = Mock(spec=LLMConfig)
            mock_load.return_value = mock_config
            
            # Test version with 'v' prefix
            service.get_prompt_with_config("en", "v1.3.0")
            mock_load.assert_called_with("keyword_extraction", "v1.3.0-en.yaml")
            
            # Test version without 'v' prefix (should add it)
            mock_load.reset_mock()
            service.get_prompt_with_config("en", "1.3.0")
            mock_load.assert_called_with("keyword_extraction", "v1.3.0-en.yaml")
            
            # Test caching (should not call load again)
            mock_load.reset_mock()
            service.get_prompt_with_config("en", "1.3.0")
            mock_load.assert_not_called()  # Should use cache
    
    def test_prompt_error_handling(self):
        """Test error handling for invalid prompts."""
        service = UnifiedPromptService()
        
        # Test unsupported language
        with pytest.raises(ValueError) as exc_info:
            service.get_prompt_with_config("ja", "1.0.0")
        assert "Language 'ja' not supported" in str(exc_info.value)
        
        # Test missing version
        with patch.object(service.simple_prompt_manager, 'load_prompt_config_by_filename') as mock_load:
            mock_load.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(ValueError) as exc_info:
                service.get_prompt_with_config("en", "999.0.0")
            assert "Version '999.0.0' not available" in str(exc_info.value)


@pytest.mark.unit
class TestPipelineErrorHandling:
    """Test error handling throughout the extraction pipeline."""
    
    @pytest.mark.asyncio
    async def test_malformed_openai_response(self):
        """Test handling of malformed AI responses."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            # Mock malformed JSON response
            mock_chat.return_value = {
                "choices": [{
                    "message": {
                        "content": "Invalid JSON: {keywords: [missing quotes]}"
                    }
                }]
            }
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Test job description",
                "max_keywords": 10
            })
            
            # Should handle gracefully and return valid response
            assert isinstance(result, dict)
            assert "keywords" in result
            assert isinstance(result["keywords"], list)
            # May have warning about parsing issues
            if "warning" in result:
                assert result["warning"]["has_warning"] is True
    
    @pytest.mark.asyncio
    async def test_openai_service_error(self):
        """Test handling of OpenAI service errors."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            mock_chat.side_effect = Exception("OpenAI service unavailable")
            
            service = KeywordExtractionServiceV2()
            
            # Should raise exception (service design decision)
            with pytest.raises(Exception) as exc_info:
                await service.process({
                    "job_description": "Test job description",
                    "max_keywords": 10
                })
            
            assert "OpenAI service unavailable" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance metrics in the pipeline."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            mock_chat.return_value = {
                "choices": [{
                    "message": {"content": json.dumps({"keywords": ["Test", "Keywords"]})}
                }]
            }
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Test job description",
                "max_keywords": 10
            })
            
            # Should include performance metrics
            assert "processing_time_ms" in result
            assert isinstance(result["processing_time_ms"], (int, float))
            assert result["processing_time_ms"] >= 0
            
            # Should include extraction method
            assert "extraction_method" in result
            # The actual extraction method can vary
            assert isinstance(result["extraction_method"], str)


@pytest.mark.unit
class TestQualityWarnings:
    """Test quality warning system in the pipeline."""
    
    @pytest.mark.asyncio
    async def test_low_keyword_count_warning(self):
        """Test warning when extracted keywords are below threshold."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            # Mock response with only 5 keywords (below 12 threshold)
            mock_chat.return_value = {
                "choices": [{
                    "message": {"content": json.dumps({"keywords": ["A", "B", "C", "D", "E"]})}
                }]
            }
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Short job description",
                "max_keywords": 20
            })
            
            # Should have warning
            assert "warning" in result
            warning = result["warning"]
            assert warning["has_warning"] is True
            assert warning["expected_minimum"] == 12
            assert warning["actual_extracted"] == 5
            # Message might be in Chinese or English, just check it exists
            assert len(warning["message"]) > 0
    
    @pytest.mark.asyncio
    async def test_no_warning_sufficient_keywords(self):
        """Test no warning when sufficient keywords extracted."""
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_chat:
            # Mock response with 15 keywords (above threshold)
            keywords = [f"Keyword{i}" for i in range(15)]
            mock_chat.return_value = {
                "choices": [{
                    "message": {"content": json.dumps({"keywords": keywords})}
                }]
            }
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Detailed job description",
                "max_keywords": 20
            })
            
            # Should not have warning
            warning = result.get("warning", {})
            assert warning.get("has_warning", False) is False