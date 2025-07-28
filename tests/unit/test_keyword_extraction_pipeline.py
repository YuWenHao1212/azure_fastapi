"""
Unit tests for Keyword Extraction Pipeline - Consolidated service and prompt management tests.
Tests the complete pipeline including keyword extraction, prompt management, and service integration.
Combines tests from test_keyword_extraction_service.py and test_unified_prompt_service.py.
"""
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.models.prompt_config import PromptConfig
from src.services.keyword_extraction_v2 import KeywordExtractionServiceV2
from src.services.unified_prompt_service import (
    UnifiedPromptService,
    get_unified_prompt_service,
)


@pytest.mark.unit
class TestKeywordExtractionPipeline:
    """Test the keyword extraction pipeline with integrated prompt management."""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Standard mock response for OpenAI API."""
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "keywords": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS", 
                                   "Microservices", "REST API", "CI/CD", "Git", "Agile"]
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
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            mock_client.chat_completion = AsyncMock(return_value=mock_openai_response)
            # complete_text should return the content string directly
            mock_client.complete_text = AsyncMock(return_value=json.dumps({
                "keywords": ["Python", "FastAPI", "Docker", "PostgreSQL", "AWS", 
                           "Microservices", "REST API", "CI/CD", "Git", "Agile"]
            }))
            mock_get_client.return_value = mock_client
            
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
            
            # Verify keywords were extracted
            assert len(result["keywords"]) > 0
            assert result["keyword_count"] == len(result["keywords"])
    
    @pytest.mark.asyncio
    async def test_two_round_intersection_algorithm(self):
        """Test 2-round intersection algorithm with different responses."""
        # Mock different responses for round 1 and round 2
        round1_keywords = ["Python", "FastAPI", "Docker", "PostgreSQL", "Git"]
        round2_keywords = ["Python", "FastAPI", "Backend", "PostgreSQL", "AWS"]
        intersection = ["Python", "FastAPI", "PostgreSQL"]  # Common keywords
        
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            # Configure mock to return different results for each call
            mock_client.chat_completion = AsyncMock(side_effect=[
                {"choices": [{"message": {"content": json.dumps({"keywords": round1_keywords})}}]},
                {"choices": [{"message": {"content": json.dumps({"keywords": round2_keywords})}}]}
            ])
            # complete_text should return the content string directly
            mock_client.complete_text = AsyncMock(side_effect=[
                json.dumps({"keywords": round1_keywords}),
                json.dumps({"keywords": round2_keywords})
            ])
            mock_get_client.return_value = mock_client
            
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
        
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            response = {
                "choices": [{"message": {"content": json.dumps({"keywords": raw_keywords})}}]
            }
            mock_client.chat_completion = AsyncMock(return_value=response)
            # complete_text should return the content string directly
            mock_client.complete_text = AsyncMock(return_value=json.dumps({"keywords": raw_keywords}))
            mock_get_client.return_value = mock_client
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Looking for ML engineer with React.js skills",
                "max_keywords": 10,
                "include_standardization": True
            })
            
            # Verify standardization was applied through standardized_terms
            assert "standardized_terms" in result
            assert isinstance(result["standardized_terms"], list)
            # Since we're using include_standardization=True, there should be standardized terms
            assert "standardized_terms" in result


@pytest.mark.unit
class TestPromptManagement:
    """Test unified prompt service functionality."""
    
    def test_unified_prompt_service_initialization(self):
        """Test that the unified prompt service initializes correctly."""
        service = get_unified_prompt_service()
        assert isinstance(service, UnifiedPromptService)
        assert hasattr(service, 'simple_prompt_manager')
        assert hasattr(service, '_cache')
    
    def test_multilingual_prompt_loading(self):
        """Test loading prompts for different languages."""
        service = get_unified_prompt_service()
        
        # Check supported languages
        assert "en" in service.SUPPORTED_LANGUAGES
        assert "zh-TW" in service.SUPPORTED_LANGUAGES
    
    def test_prompt_version_management(self):
        """Test prompt version retrieval and management."""
        service = get_unified_prompt_service()
        
        # Get prompt config using get_prompt_config method
        prompt_config = service.get_prompt_config("en", version="latest")
        assert isinstance(prompt_config, PromptConfig)
        assert hasattr(prompt_config, 'metadata')
        assert hasattr(prompt_config, 'llm_config')
    
    def test_prompt_error_handling(self):
        """Test error handling for invalid language/version."""
        service = get_unified_prompt_service()
        
        # Test invalid language
        with pytest.raises(ValueError):
            service.get_prompt_config("invalid-lang")
        
        # Test invalid version  
        with pytest.raises((ValueError, FileNotFoundError)):
            service.get_prompt_config("en", version="v99.99.99")


@pytest.mark.unit
class TestPipelineErrorHandling:
    """Test error handling throughout the extraction pipeline."""
    
    @pytest.mark.asyncio
    async def test_malformed_openai_response(self):
        """Test handling of malformed AI responses."""
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            # Mock malformed JSON response
            response = {
                "choices": [{
                    "message": {
                        "content": "Invalid JSON: {keywords: [missing quotes]}"
                    }
                }]
            }
            mock_client.chat_completion = AsyncMock(return_value=response)
            # complete_text should return malformed string
            mock_client.complete_text = AsyncMock(return_value="Invalid JSON: {keywords: [missing quotes]}")
            mock_get_client.return_value = mock_client
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Test job description",
                "max_keywords": 10
            })
            
            # Should handle gracefully - either return empty or have an error
            assert "keywords" in result
            assert isinstance(result["keywords"], list)
    
    @pytest.mark.asyncio
    async def test_openai_service_error(self):
        """Test handling of OpenAI service errors."""
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            # Mock service error
            mock_client.chat_completion = AsyncMock(side_effect=Exception("OpenAI service unavailable"))
            mock_client.complete_text = AsyncMock(side_effect=Exception("OpenAI service unavailable"))
            mock_get_client.return_value = mock_client
            
            service = KeywordExtractionServiceV2()
            
            # Should handle the error appropriately
            with pytest.raises(Exception) as exc_info:
                await service.process({
                    "job_description": "Test job description", 
                    "max_keywords": 10
                })
            assert "OpenAI service unavailable" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test that performance metrics are captured."""
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            response = {
                "choices": [{
                    "message": {
                        "content": json.dumps({"keywords": ["Python", "FastAPI"]})
                    }
                }]
            }
            mock_client.chat_completion = AsyncMock(return_value=response)
            # complete_text should return the content string directly
            mock_client.complete_text = AsyncMock(return_value=json.dumps({"keywords": ["Python", "FastAPI"]}))
            mock_get_client.return_value = mock_client
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Python developer needed",
                "max_keywords": 10
            })
            
            # Should include performance metrics
            assert "processing_time_ms" in result
            assert isinstance(result["processing_time_ms"], int | float)
            assert result["processing_time_ms"] >= 0


@pytest.mark.unit 
class TestQualityWarnings:
    """Test quality warning generation for extracted keywords."""
    
    @pytest.mark.asyncio
    async def test_low_keyword_count_warning(self):
        """Test warning generation when too few keywords are extracted."""
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            response = {
                "choices": [{
                    "message": {
                        "content": json.dumps({"keywords": ["Python", "Developer"]})  # Only 2 keywords
                    }
                }]
            }
            mock_client.chat_completion = AsyncMock(return_value=response)
            # complete_text should return the content string directly
            mock_client.complete_text = AsyncMock(return_value=json.dumps({"keywords": ["Python", "Developer"]}))
            mock_get_client.return_value = mock_client
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Python developer needed",
                "max_keywords": 10
            })
            
            # Should generate warnings in the warning field
            assert "warning" in result
            warning_info = result["warning"]
            assert isinstance(warning_info, dict)
            assert warning_info.get("has_warning", False) is True
            # Check warning message exists
            assert "message" in warning_info
            assert len(warning_info["message"]) > 0
    
    @pytest.mark.asyncio
    async def test_no_warning_sufficient_keywords(self):
        """Test no warnings are generated when sufficient keywords are extracted."""
        with patch('src.services.llm_factory.get_llm_client') as mock_get_client:
            # Create a mock client with the necessary methods
            mock_client = Mock()
            response = {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "keywords": ["Python", "FastAPI", "Docker", "AWS", "PostgreSQL", 
                                       "Git", "CI/CD", "Microservices", "REST API", "Agile"]
                        })
                    }
                }]
            }
            mock_client.chat_completion = AsyncMock(return_value=response)
            # complete_text should return the content string directly
            mock_client.complete_text = AsyncMock(return_value=json.dumps({
                "keywords": ["Python", "FastAPI", "Docker", "AWS", "PostgreSQL", 
                           "Git", "CI/CD", "Microservices", "REST API", "Agile"]
            }))
            mock_get_client.return_value = mock_client
            
            service = KeywordExtractionServiceV2()
            result = await service.process({
                "job_description": "Senior Python developer with cloud experience",
                "max_keywords": 15
            })
            
            # Should not have warnings (or empty list)
            warnings = result.get("quality_warnings", [])
            assert isinstance(warnings, list)
            assert len(warnings) == 0