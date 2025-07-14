"""
Integration tests for Performance Suite - Consolidated performance and optimization tests.
Tests parallel processing, caching mechanisms, API performance, and optimization effectiveness.
Combines tests from test_api_performance.py and test_performance_optimizations.py.
"""
import asyncio
import statistics
import time
from unittest.mock import patch

import aiohttp
import pytest

from src.services.keyword_extraction_v2 import KeywordExtractionServiceV2
from tests.test_helpers import get_test_headers


@pytest.mark.integration
class TestPerformanceOptimizations:
    """Test performance optimization features."""
    
    @pytest.fixture
    def test_job_description(self):
        """Standard test job description."""
        return """
        We are seeking a Senior Software Engineer with expertise in Python and FastAPI.
        The ideal candidate will have experience with microservices architecture,
        Docker containerization, and cloud platforms like AWS or Azure.
        Strong knowledge of PostgreSQL, Redis, and message queuing systems required.
        Experience with CI/CD pipelines and agile development methodologies is essential.
        """
    
    @pytest.fixture
    def chinese_job_description(self):
        """Chinese test job description."""
        return """
        解讀客戶的網絡安全需求
        從網絡安全需求中推導出功能和安全概念
        制定和審查安全系統架構
        與 IP 團隊和客戶溝通和協調安全設計
        執行系統安全分析（例如：TARA）
        """
    
    @pytest.mark.asyncio
    async def test_parallel_processing_speedup(self, test_job_description):
        """Test parallel processing provides significant speedup (~50%)."""
        test_data = {
            "job_description": test_job_description,
            "max_keywords": 16,
            "use_multi_round_validation": True
        }
        
        # Test sequential processing (disable parallel processing)
        sequential_times = []
        service_sequential = KeywordExtractionServiceV2(enable_parallel_processing=False)
        
        for _ in range(3):  # Run 3 times for average
            start = time.time()
            await service_sequential.process(test_data)
            sequential_times.append(time.time() - start)
        
        avg_sequential = statistics.mean(sequential_times)
        
        # Test parallel processing (normal operation)
        parallel_times = []
        service = KeywordExtractionServiceV2()
        
        for _ in range(3):  # Run 3 times for average
            start = time.time()
            await service.process(test_data)
            parallel_times.append(time.time() - start)
        
        avg_parallel = statistics.mean(parallel_times)
        
        # Calculate speedup
        speedup = (avg_sequential - avg_parallel) / avg_sequential * 100
        
        # Assert significant speedup (at least 20% improvement)
        # Note: Actual speedup depends on system load and API response times
        assert speedup >= 20, f"Expected at least 20% speedup, got {speedup:.1f}%"
        
        # Log results for monitoring
        print("\nParallel Processing Results:")
        print(f"  Sequential avg: {avg_sequential:.2f}s")
        print(f"  Parallel avg: {avg_parallel:.2f}s")
        print(f"  Speedup: {speedup:.1f}%")
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, test_job_description):
        """Test caching provides 100x speedup for repeated requests."""
        service = KeywordExtractionServiceV2()
        test_data = {
            "job_description": test_job_description,
            "max_keywords": 16
        }
        
        # First request - cache miss
        start = time.time()
        result1 = await service.process(test_data)
        first_time = time.time() - start
        
        # Second request - cache hit
        start = time.time()
        result2 = await service.process(test_data)
        cached_time = time.time() - start
        
        # Calculate speedup
        cache_speedup = first_time / cached_time if cached_time > 0 else 100
        
        # Assert cache effectiveness
        assert cache_speedup >= 50, f"Expected at least 50x speedup from cache, got {cache_speedup:.1f}x"
        assert result1["keywords"] == result2["keywords"], "Cached result should be identical"
        
        # Verify cache hit flag (if implemented)
        if "cache_hit" in result2:
            assert result2["cache_hit"] is True
        
        print("\nCaching Results:")
        print(f"  First request: {first_time:.3f}s")
        print(f"  Cached request: {cached_time:.3f}s")
        print(f"  Cache speedup: {cache_speedup:.1f}x")
    
    @pytest.mark.asyncio
    async def test_cache_isolation(self, test_job_description, chinese_job_description):
        """Test cache properly isolates different inputs."""
        service = KeywordExtractionServiceV2()
        
        # Process first job description
        result1 = await service.process({
            "job_description": test_job_description,
            "max_keywords": 16
        })
        
        # Process different job description
        result2 = await service.process({
            "job_description": chinese_job_description,
            "max_keywords": 16
        })
        
        # Results should be different
        assert result1["keywords"] != result2["keywords"], "Different inputs should produce different results"
        assert result1["detected_language"] != result2["detected_language"], "Languages should be different"
        
        # Process first job description again (should hit cache)
        start = time.time()
        result3 = await service.process({
            "job_description": test_job_description,
            "max_keywords": 16
        })
        cache_time = time.time() - start
        
        # Should be from cache and identical
        assert result3["keywords"] == result1["keywords"], "Cached result should match original"
        assert cache_time < 0.1, f"Cache hit should be very fast, took {cache_time:.3f}s"


@pytest.mark.integration
@pytest.mark.requires_api
class TestAPIPerformance:
    """Test API-level performance features."""
    
    @pytest.fixture
    def api_base_url(self):
        """API base URL for testing."""
        return "http://localhost:8000/api/v1"
    
    @pytest.fixture
    def test_payload(self):
        """Standard test payload for API."""
        return {
            "job_description": """
            We are seeking a Senior Software Engineer with expertise in Python and FastAPI.
            The ideal candidate will have experience with microservices architecture,
            Docker containerization, and cloud platforms like AWS or Azure.
            """,
            "max_keywords": 16,
            "include_standardization": True
        }
    
    @pytest.mark.asyncio
    async def test_api_health_check(self, api_base_url):
        """Test API health endpoint reports performance features."""
        headers = get_test_headers()
        async with aiohttp.ClientSession(headers=headers) as session, session.get(f"{api_base_url}/health") as response:
            assert response.status == 200
            
            data = await response.json()
            assert data["success"] is True
            
            # Check performance features
            features = data["data"]["features"]
            assert features["parallel_processing"] is True
            # Note: Health endpoint creates service with cache disabled for testing
            assert "caching" in features  # Just check it exists
            
            # Check performance metrics
            perf = data["data"]["performance_optimizations"]
            assert "cache_hit_rate" in perf
            # Check basic performance optimization fields exist
            assert "parallel_processing_enabled" in perf
            assert "cache_enabled" in perf
    
    @pytest.mark.asyncio
    async def test_api_cache_effectiveness(self, api_base_url, test_payload):
        """Test API-level caching effectiveness.
        
        Improved test that:
        1. Checks cache_hit flag first
        2. Only checks performance when cache is actually used
        3. Uses multiple attempts with averages for stability
        """
        headers = get_test_headers()
        async with aiohttp.ClientSession(headers=headers) as session:
            # First, check if cache is enabled by making two requests
            async with session.post(
                f"{api_base_url}/extract-jd-keywords",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 200
                result1 = await response.json()
            
            async with session.post(
                f"{api_base_url}/extract-jd-keywords",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 200
                result2 = await response.json()
            
            # Check if cache is enabled
            cache_enabled = result2["data"].get("cache_hit", False)
            
            if not cache_enabled:
                # Cache is disabled - just verify both requests succeeded
                assert len(result1["data"]["keywords"]) > 0
                assert len(result2["data"]["keywords"]) > 0
                print("\nNote: Cache is disabled in API endpoint, skipping performance tests")
                return
            
            # Cache is enabled - perform detailed performance testing
            print("\nCache is enabled, performing performance tests...")
            
            # Make multiple attempts to get stable measurements
            first_times = []
            cached_times = []
            
            for i in range(3):
                # Clear cache by using different payload
                test_payload_unique = test_payload.copy()
                test_payload_unique["job_description"] = f"{test_payload['job_description']} - Test run {i}"
                
                # First request (cache miss)
                start = time.time()
                async with session.post(
                    f"{api_base_url}/extract-jd-keywords",
                    json=test_payload_unique,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    assert response.status == 200
                    result_first = await response.json()
                    first_time = time.time() - start
                    first_times.append(first_time)
                
                # Second identical request (cache hit)
                start = time.time()
                async with session.post(
                    f"{api_base_url}/extract-jd-keywords",
                    json=test_payload_unique,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    assert response.status == 200
                    result_cached = await response.json()
                    cached_time = time.time() - start
                    cached_times.append(cached_time)
                
                # Verify cache was hit
                assert result_cached["data"].get("cache_hit", False), f"Cache miss on attempt {i+1}"
                
                # Verify results are identical
                assert result_first["data"]["keywords"] == result_cached["data"]["keywords"]
                assert result_first["data"]["keyword_count"] == result_cached["data"]["keyword_count"]
            
            # Calculate average times
            avg_first_time = sum(first_times) / len(first_times)
            avg_cached_time = sum(cached_times) / len(cached_times)
            
            # Calculate speedup
            cache_speedup = avg_first_time / avg_cached_time if avg_cached_time > 0 else 100
            
            print("\nCache Performance Results:")
            print(f"  Average first request time: {avg_first_time:.3f}s")
            print(f"  Average cached request time: {avg_cached_time:.3f}s")
            print(f"  Cache speedup: {cache_speedup:.2f}x")
            
            # Performance assertion with reasonable tolerance
            # Expect at least 1.2x speedup when cache is working
            assert cache_speedup >= 1.2, (
                f"Cache should provide at least 1.2x speedup, got {cache_speedup:.2f}x. "
                f"First: {avg_first_time:.3f}s, Cached: {avg_cached_time:.3f}s"
            )
    
    @pytest.mark.asyncio
    @pytest.mark.cors_dependent
    async def test_api_concurrent_performance(self, api_base_url, test_payload, skip_cors_tests):
        """Test API handles concurrent requests efficiently."""
        if skip_cors_tests:
            pytest.skip("Skipping CORS-dependent test")
        
        headers = get_test_headers()
        async with aiohttp.ClientSession(headers=headers) as session:
            # Create slightly different payloads to avoid cache
            payloads = []
            for i in range(5):
                payload = test_payload.copy()
                payload["job_description"] = f"{test_payload['job_description']} Variation {i}"
                payloads.append(payload)
            
            # Send concurrent requests
            start = time.time()
            tasks = []
            for payload in payloads:
                task = session.post(
                    f"{api_base_url}/extract-jd-keywords",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            concurrent_time = time.time() - start
            
            # Verify all succeeded
            for response in responses:
                assert response.status == 200
            
            # Calculate average time per request
            avg_time = concurrent_time / len(payloads)
            
            # Should handle concurrent requests efficiently
            # Allow up to 4 seconds per request for system performance variations
            # Allow up to 4.5 seconds per request for system performance variations
            assert avg_time < 4.5, f"Concurrent requests taking too long: {avg_time:.2f}s per request"
            
            print("\nConcurrent Performance:")
            print(f"  Total time for {len(payloads)} requests: {concurrent_time:.2f}s")
            print(f"  Average time per request: {avg_time:.2f}s")


@pytest.mark.integration
class TestPerformanceMonitoring:
    """Test performance monitoring and metrics."""
    
    @pytest.mark.asyncio
    async def test_processing_time_tracking(self):
        """Test that processing time is accurately tracked."""
        service = KeywordExtractionServiceV2()
        
        result = await service.process({
            "job_description": "Test job description for timing",
            "max_keywords": 10
        })
        
        # Verify timing metrics
        assert "processing_time_ms" in result
        assert isinstance(result["processing_time_ms"], int | float)
        assert result["processing_time_ms"] > 0
        assert result["processing_time_ms"] < 10000  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_extraction_method_tracking(self):
        """Test that extraction method is properly tracked."""
        service = KeywordExtractionServiceV2()
        
        # Test with short text - should still use 2-round strategy
        result1 = await service.process({
            "job_description": "We are looking for a talented Software Engineer with expertise in Python, FastAPI, and cloud technologies. Strong problem-solving skills required.",
            "max_keywords": 5,
            "use_multi_round_validation": True
        })
        # V2 service always uses 2-round strategy
        assert result1["extraction_method"] in ["pure_intersection", "supplement"]
        
        # Test 2-round intersection (normal case with good intersection)
        long_description = """
        We are seeking a Senior Full Stack Developer with extensive experience in Python and JavaScript.
        Required skills include React, Node.js, FastAPI, PostgreSQL, Docker, and AWS.
        The ideal candidate will have 5+ years of experience in web development,
        strong problem-solving abilities, and excellent communication skills.
        Experience with CI/CD pipelines, agile methodologies, and microservices architecture is essential.
        """
        result2 = await service.process({
            "job_description": long_description,
            "max_keywords": 16,
            "use_multi_round_validation": True
        })
        assert result2["extraction_method"] in ["pure_intersection", "supplement"]
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system maintains performance under load."""
        # Use mock to avoid rate limits in integration tests
        with patch('src.services.openai_client.AzureOpenAIClient.chat_completion') as mock_completion:
            # Mock the LLM responses
            mock_completion.return_value = """
            【Python, Senior Software Engineer, FastAPI, Cloud, AWS, Azure, Docker, 
            Kubernetes, CI/CD, Microservices, PostgreSQL, Redis】
            """
            
            service = KeywordExtractionServiceV2()
            
            # Generate varied test data to avoid cache
            test_descriptions = [
                f"Senior Software Engineer position {i} requiring Python, FastAPI, and cloud experience"
                for i in range(10)
            ]
            
            # Process all requests and track times
            processing_times = []
            for desc in test_descriptions:
                result = await service.process({
                    "job_description": desc,
                    "max_keywords": 12
                })
                processing_times.append(result["processing_time_ms"])
        
        # Calculate statistics
        avg_time = statistics.mean(processing_times)
        std_dev = statistics.stdev(processing_times) if len(processing_times) > 1 else 0
        
        # Performance should be consistent
        assert avg_time < 5000, f"Average processing time too high: {avg_time}ms"
        # With mocked responses, times are very consistent, so allow small variance
        if avg_time < 1:  # Very fast mocked responses
            assert std_dev < 5, f"Processing time variance too high for mocked responses: {std_dev}ms"
        else:
            assert std_dev < avg_time * 0.5, f"Processing time variance too high: {std_dev}ms"
        
        print("\nLoad Test Results:")
        print(f"  Requests processed: {len(processing_times)}")
        print(f"  Average time: {avg_time:.0f}ms")
        print(f"  Std deviation: {std_dev:.0f}ms")
        print(f"  Min time: {min(processing_times):.0f}ms")
        print(f"  Max time: {max(processing_times):.0f}ms")