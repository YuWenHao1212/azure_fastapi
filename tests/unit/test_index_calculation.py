"""
Unit tests for index calculation service.
Tests similarity calculation and keyword coverage analysis.
"""
from unittest.mock import AsyncMock, patch

import pytest

from src.services.index_calculation import (
    IndexCalculationService,
    analyze_keyword_coverage,
    compute_similarity,
    sigmoid_transform,
)


class TestSigmoidTransform:
    """Test sigmoid_transform function."""
    
    def test_sigmoid_transform_default_params(self):
        """Test sigmoid transform with default parameters."""
        # Default x0 is 0.373 based on config
        # Test with x = x0 (should be 0.5)
        assert abs(sigmoid_transform(0.373) - 0.5) < 0.01
        
        # Test with x > x0
        assert sigmoid_transform(0.9) > 0.5
        assert sigmoid_transform(0.5) > 0.5
        
        # Test with x < x0
        assert sigmoid_transform(0.2) < 0.5
    
    def test_sigmoid_transform_custom_params(self):
        """Test sigmoid transform with custom parameters."""
        # Custom x0 and k
        result = sigmoid_transform(0.5, x0=0.5, k=5.0)
        assert abs(result - 0.5) < 0.01
        
        # Test extreme values
        assert sigmoid_transform(1.0, x0=0.5, k=10.0) > 0.99
        assert sigmoid_transform(0.0, x0=0.5, k=10.0) < 0.01
    
    def test_sigmoid_overflow_handling(self):
        """Test sigmoid overflow handling."""
        # Should not raise overflow error
        result = sigmoid_transform(10.0, x0=0.5, k=100.0)
        assert result == 1.0
        
        result = sigmoid_transform(-10.0, x0=0.5, k=100.0)
        assert result == 0.0


class TestAnalyzeKeywordCoverage:
    """Test analyze_keyword_coverage function."""
    
    def test_basic_keyword_coverage(self):
        """Test basic keyword coverage analysis."""
        resume = "I have experience with Python and JavaScript programming"
        keywords = ["Python", "JavaScript", "Java", "SQL"]
        
        result = analyze_keyword_coverage(resume, keywords)
        
        assert result["total_keywords"] == 4
        assert result["covered_count"] == 2
        assert result["coverage_percentage"] == 50
        assert "Python" in result["covered_keywords"]
        assert "JavaScript" in result["covered_keywords"]
        assert "Java" in result["missed_keywords"]
        assert "SQL" in result["missed_keywords"]
    
    def test_case_insensitive_matching(self):
        """Test case insensitive keyword matching."""
        resume = "I have experience with python and JAVASCRIPT"
        keywords = ["Python", "JavaScript"]
        
        result = analyze_keyword_coverage(resume, keywords)
        
        assert result["covered_count"] == 2
        assert result["coverage_percentage"] == 100
    
    def test_plural_matching(self):
        """Test plural form matching."""
        resume = "I work with databases and frameworks"
        keywords = ["database", "framework"]
        
        result = analyze_keyword_coverage(resume, keywords)
        
        # Should match plural forms
        assert result["covered_count"] == 2
        assert result["coverage_percentage"] == 100
    
    def test_string_keywords_input(self):
        """Test comma-separated string keywords input."""
        resume = "Python developer with SQL experience"
        keywords = "Python, SQL, Java, C++"
        
        result = analyze_keyword_coverage(resume, keywords)
        
        assert result["total_keywords"] == 4
        assert result["covered_count"] == 2
        assert result["coverage_percentage"] == 50
    
    def test_empty_inputs(self):
        """Test empty input handling."""
        # Empty resume
        result = analyze_keyword_coverage("", ["Python", "Java"])
        assert result["covered_count"] == 0
        assert result["coverage_percentage"] == 0
        
        # Empty keywords
        result = analyze_keyword_coverage("Python developer", [])
        assert result["total_keywords"] == 0
        assert result["coverage_percentage"] == 0
        
        # Both empty
        result = analyze_keyword_coverage("", [])
        assert result["total_keywords"] == 0
    
    def test_html_content_cleaning(self):
        """Test HTML content is cleaned before analysis."""
        resume = "<p>I have <strong>Python</strong> and JavaScript skills</p>"
        keywords = ["Python", "JavaScript"]
        
        result = analyze_keyword_coverage(resume, keywords)
        
        assert result["covered_count"] == 2
        assert result["coverage_percentage"] == 100
    
    def test_word_boundary_matching(self):
        """Test word boundary matching."""
        resume = "I use Java but not JavaScript"
        keywords = ["Java", "JavaScript"]
        
        result = analyze_keyword_coverage(resume, keywords)
        
        # Both keywords are present as separate words in the text
        assert "Java" in result["covered_keywords"]
        assert "JavaScript" in result["covered_keywords"]
        
        # Test that "Java" doesn't match inside "JavaScript" only
        resume2 = "I use JavaScript only"
        result2 = analyze_keyword_coverage(resume2, ["Java"])
        assert "Java" not in result2["covered_keywords"]


@pytest.mark.asyncio
class TestComputeSimilarity:
    """Test compute_similarity function."""
    
    @patch('src.services.index_calculation.get_azure_embedding_client')
    async def test_compute_similarity_basic(self, mock_get_client):
        """Test basic similarity computation."""
        # Mock embedding client
        mock_client = AsyncMock()
        mock_embeddings = [
            [0.1, 0.2, 0.3, 0.4],  # Resume embedding
            [0.1, 0.2, 0.3, 0.4]   # Job description embedding (same = similarity 1.0)
        ]
        mock_client.create_embeddings.return_value = mock_embeddings
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        resume = "Python developer with 5 years experience"
        job_desc = "Looking for Python developer"
        
        raw_pct, trans_pct = await compute_similarity(resume, job_desc)
        
        # With identical embeddings, cosine similarity should be 100%
        assert raw_pct == 100
        # With default sigmoid parameters (x0=0.373, k=15), 100% input gives 100% output
        assert trans_pct == 100
        
        mock_client.create_embeddings.assert_called_once()
        mock_client.close.assert_called_once()
    
    @patch('src.services.index_calculation.get_azure_embedding_client')
    async def test_compute_similarity_different_vectors(self, mock_get_client):
        """Test similarity with different vectors."""
        # Mock embedding client
        mock_client = AsyncMock()
        mock_embeddings = [
            [1.0, 0.0, 0.0, 0.0],  # Resume embedding
            [0.0, 1.0, 0.0, 0.0]   # Job description embedding (orthogonal = similarity 0)
        ]
        mock_client.create_embeddings.return_value = mock_embeddings
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        resume = "Python developer"
        job_desc = "Java developer"
        
        raw_pct, trans_pct = await compute_similarity(resume, job_desc)
        
        # With orthogonal vectors, cosine similarity should be 0%
        assert raw_pct == 0
        assert trans_pct < 50  # After sigmoid transform
    
    @patch('src.services.index_calculation.get_azure_embedding_client')
    async def test_compute_similarity_empty_inputs(self, mock_get_client):
        """Test similarity with empty inputs."""
        # Should return 0, 0 without calling embedding API
        raw_pct, trans_pct = await compute_similarity("", "Job description")
        assert raw_pct == 0
        assert trans_pct == 0
        
        raw_pct, trans_pct = await compute_similarity("Resume", "")
        assert raw_pct == 0
        assert trans_pct == 0
        
        # Embedding client should not be called
        mock_get_client.assert_not_called()
    
    @patch('src.services.index_calculation.get_azure_embedding_client')
    async def test_compute_similarity_html_cleaning(self, mock_get_client):
        """Test HTML is cleaned before similarity computation."""
        # Mock embedding client
        mock_client = AsyncMock()
        mock_embeddings = [[0.5, 0.5], [0.5, 0.5]]
        mock_client.create_embeddings.return_value = mock_embeddings
        mock_client.close = AsyncMock()
        mock_get_client.return_value = mock_client
        
        resume = "<p>Python <strong>developer</strong></p>"
        job_desc = "<div>Looking for Python developer</div>"
        
        await compute_similarity(resume, job_desc)
        
        # Check that cleaned text was passed to embedding
        call_args = mock_client.create_embeddings.call_args[0][0]
        assert "<p>" not in call_args[0]
        assert "<strong>" not in call_args[0]
        assert "Python developer" in call_args[0]


@pytest.mark.asyncio
class TestIndexCalculationService:
    """Test IndexCalculationService class."""
    
    @patch('src.services.index_calculation.compute_similarity')
    @patch('src.services.index_calculation.analyze_keyword_coverage')
    async def test_calculate_index(self, mock_analyze, mock_compute):
        """Test complete index calculation."""
        # Mock functions
        mock_compute.return_value = (75, 85)  # raw, transformed
        mock_analyze.return_value = {
            "total_keywords": 10,
            "covered_count": 7,
            "coverage_percentage": 70,
            "covered_keywords": ["Python", "SQL", "API"],
            "missed_keywords": ["Java", "React", "Docker"]
        }
        
        service = IndexCalculationService()
        result = await service.calculate_index(
            resume="Python developer with SQL and API experience",
            job_description="Looking for Python developer",
            keywords=["Python", "SQL", "API", "Java", "React", "Docker"]
        )
        
        assert result["raw_similarity_percentage"] == 75
        assert result["similarity_percentage"] == 85
        assert result["keyword_coverage"]["coverage_percentage"] == 70
        assert len(result["keyword_coverage"]["covered_keywords"]) == 3
        assert len(result["keyword_coverage"]["missed_keywords"]) == 3
        
        # Verify function calls
        mock_compute.assert_called_once()
        mock_analyze.assert_called_once()
    
    @patch('src.services.index_calculation.compute_similarity')
    @patch('src.services.index_calculation.analyze_keyword_coverage')
    async def test_calculate_index_with_string_keywords(self, mock_analyze, mock_compute):
        """Test index calculation with string keywords."""
        # Mock functions
        mock_compute.return_value = (80, 90)
        mock_analyze.return_value = {
            "total_keywords": 3,
            "covered_count": 2,
            "coverage_percentage": 67,
            "covered_keywords": ["Python", "Django"],
            "missed_keywords": ["React"]
        }
        
        service = IndexCalculationService()
        result = await service.calculate_index(
            resume="Python Django developer",
            job_description="Full stack developer needed",
            keywords="Python, Django, React"
        )
        
        assert result["similarity_percentage"] == 90
        assert result["keyword_coverage"]["coverage_percentage"] == 67