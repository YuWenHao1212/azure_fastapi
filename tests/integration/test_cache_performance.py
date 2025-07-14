#!/usr/bin/env python3
"""
Cache performance and verification tests.
Ensures caching mechanism works correctly and improves performance.
"""

import time

import pytest

from src.models.keyword_extraction import KeywordExtractionRequest
from src.services.keyword_extraction import KeywordExtractionService
from src.services.openai_client import get_azure_openai_client


class TestCachePerformance:
    """Test cache functionality and performance improvements."""
    
    # Test JDs
    SHORT_JD = """
    Senior Data Analyst position requiring SQL, Python, and machine learning experience.
    Must have experience with data visualization and business intelligence tools.
    """
    
    LONG_JD = """
    We are seeking a Senior Software Engineer to join our dynamic team. 
    The ideal candidate will have:
    
    Technical Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python, Java, or C++
    - Experience with cloud platforms (AWS, Azure, or GCP)
    - Knowledge of microservices architecture
    - Familiarity with CI/CD pipelines
    - Experience with containerization (Docker, Kubernetes)
    
    Soft Skills:
    - Excellent problem-solving abilities
    - Strong communication skills
    - Team collaboration experience
    - Agile methodology experience
    
    Nice to Have:
    - Machine learning experience
    - Open source contributions
    - Technical blog writing
    - Public speaking experience
    """
    
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Test that cache hits are significantly faster than cache misses."""
        openai_client = get_azure_openai_client()
        service = KeywordExtractionService(openai_client)
        
        # Ensure cache is enabled
        assert service.enable_cache is True
        
        # First call - cache miss
        request = KeywordExtractionRequest(job_description=self.SHORT_JD)
        start_time = time.time()
        result1 = await service.process(request.model_dump())
        miss_duration = time.time() - start_time
        
        # Verify it was a cache miss
        assert result1.get('cache_hit', False) is False
        
        # Second call - cache hit
        start_time = time.time()
        result2 = await service.process(request.model_dump())
        hit_duration = time.time() - start_time
        
        # Verify it was a cache hit
        assert result2.get('cache_hit', False) is True
        
        # Verify cache hit is significantly faster (at least 10x faster)
        assert hit_duration < miss_duration / 10
        
        # Verify results are identical
        assert result1['keywords'] == result2['keywords']
        
        # Check cache statistics
        assert service._cache_hits == 1
        assert service._cache_misses == 1
    
    @pytest.mark.asyncio
    async def test_cache_disabled_behavior(self):
        """Test behavior when cache is explicitly disabled."""
        openai_client = get_azure_openai_client()
        service = KeywordExtractionService(openai_client, enable_cache=False)
        
        # Verify cache is disabled
        assert service.enable_cache is False
        
        request = KeywordExtractionRequest(job_description=self.SHORT_JD)
        
        # First call
        result1 = await service.process(request.model_dump())
        assert result1.get('cache_hit', False) is False
        
        # Second call - should also be a miss
        result2 = await service.process(request.model_dump())
        assert result2.get('cache_hit', False) is False
        
        # Cache statistics should show no hits
        assert service._cache_hits == 0
        assert service._cache_misses == 0  # No misses recorded when cache disabled
    
    @pytest.mark.asyncio
    async def test_cache_with_different_jds(self):
        """Test that different JDs produce different cache keys."""
        openai_client = get_azure_openai_client()
        service = KeywordExtractionService(openai_client)
        
        # Process first JD
        request1 = KeywordExtractionRequest(job_description=self.SHORT_JD)
        result1 = await service.process(request1.model_dump())
        
        # Process different JD
        request2 = KeywordExtractionRequest(job_description=self.LONG_JD)
        result2 = await service.process(request2.model_dump())
        
        # Both should be cache misses
        assert result1.get('cache_hit', False) is False
        assert result2.get('cache_hit', False) is False
        
        # Keywords should be different
        assert set(result1['keywords']) != set(result2['keywords'])
        
        # Process first JD again - should be cache hit
        result3 = await service.process(request1.model_dump())
        assert result3.get('cache_hit', False) is True
        assert result3['keywords'] == result1['keywords']
    
    @pytest.mark.asyncio
    async def test_cache_performance_metrics(self):
        """Test cache performance metrics collection."""
        openai_client = get_azure_openai_client()
        service = KeywordExtractionService(openai_client)
        
        # Reset cache statistics
        service._cache_hits = 0
        service._cache_misses = 0
        
        # Make multiple requests
        request = KeywordExtractionRequest(job_description=self.SHORT_JD)
        
        # First call - miss
        await service.process(request.model_dump())
        
        # Next 5 calls - hits
        for _ in range(5):
            await service.process(request.model_dump())
        
        # Verify statistics
        assert service._cache_hits == 5
        assert service._cache_misses == 1
        
        # Calculate hit rate
        total_requests = service._cache_hits + service._cache_misses
        hit_rate = service._cache_hits / total_requests
        assert hit_rate > 0.8  # 83.3% hit rate
    
    @pytest.mark.asyncio
    async def test_cache_with_language_parameter(self):
        """Test that language parameter affects cache key."""
        openai_client = get_azure_openai_client()
        service = KeywordExtractionService(openai_client)
        
        # Same JD, different languages
        request_en = KeywordExtractionRequest(
            job_description=self.SHORT_JD,
            language="en"
        )
        request_zh = KeywordExtractionRequest(
            job_description=self.SHORT_JD,
            language="zh-TW"
        )
        
        # Process English version
        result_en = await service.process(request_en.model_dump())
        assert result_en.get('cache_hit', False) is False
        
        # Process Chinese version - should be cache miss
        result_zh = await service.process(request_zh.model_dump())
        assert result_zh.get('cache_hit', False) is False
        
        # Process English again - should be cache hit
        result_en2 = await service.process(request_en.model_dump())
        assert result_en2.get('cache_hit', False) is True
        assert result_en2['keywords'] == result_en['keywords']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])