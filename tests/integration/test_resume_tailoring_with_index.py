"""Integration tests for resume tailoring with index calculation."""

from unittest.mock import AsyncMock, patch

import pytest

from src.models.api.resume_tailoring import (
    GapAnalysisInput,
    TailoringOptions,
    TailorResumeRequest,
)
from src.services.resume_tailoring import ResumeTailoringService


class TestResumeTailoringWithIndex:
    """Integration tests for resume tailoring with index calculation."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ResumeTailoringService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample tailoring request."""
        return TailorResumeRequest(
            job_description="""
            <h2>Senior Data Scientist</h2>
            <p>We are looking for a Senior Data Scientist with expertise in 
            machine learning, Python, SQL, and data visualization using Tableau.</p>
            <ul>
                <li>5+ years experience in data science</li>
                <li>Strong Python and SQL skills</li>
                <li>Experience with Tableau and Power BI</li>
                <li>Machine learning expertise</li>
            </ul>
            """,
            original_resume="""
            <h1>John Doe</h1>
            <p>Email: john@example.com</p>
            <h3>Work Experience</h3>
            <h4>Software Engineer - Tech Corp (2020-2023)</h4>
            <ul>
                <li>Developed web applications using Python</li>
                <li>Analyzed user data to improve features</li>
                <li>Created reports for management</li>
            </ul>
            <h3>Skills</h3>
            <ul>
                <li>Programming: Python, JavaScript</li>
                <li>Databases: MySQL</li>
                <li>Tools: Excel, Git</li>
            </ul>
            <h3>Education</h3>
            <p>BS Computer Science - State University (2016-2020)</p>
            """,
            gap_analysis=GapAnalysisInput(
                core_strengths=[
                    "Strong Python programming background",
                    "Data analysis experience",
                    "Technical problem-solving skills"
                ],
                key_gaps=[
                    "Limited data science specific experience",
                    "Missing key tools like Tableau",
                    "No machine learning projects mentioned"
                ],
                quick_improvements=[
                    "Highlight data analysis work in detail",
                    "Add quantitative metrics to achievements",
                    "Emphasize Python data libraries if used"
                ],
                covered_keywords=["Python", "MySQL"],
                missing_keywords=["SQL", "Tableau", "Machine Learning", "Data Science", "Power BI"]
            ),
            options=TailoringOptions(
                include_visual_markers=True,
                language="en"
            )
        )
    
    @pytest.mark.asyncio
    async def test_tailoring_with_index_calculation(self, service, sample_request):
        """Test complete tailoring flow with index calculation."""
        # Mock LLM response
        mock_llm_response = {
            "choices": [{
                "message": {
                    "content": '''{
                        "optimized_resume": "<h1>John Doe</h1><p>Email: john@example.com</p><h2 class=\\"opt-new\\">Professional Summary</h2><p class=\\"opt-new\\">Software Engineer with 3 years experience building data-driven applications. Proven expertise in Python data analysis and database optimization. Passionate about leveraging data to drive business insights.</p><h3>Work Experience</h3><h4>Software Engineer - Tech Corp (2020-2023)</h4><ul><li><span class=\\"opt-modified\\">Developed data-driven web applications using Python, processing <span class=\\"opt-placeholder\\">[VOLUME]</span> daily user interactions to improve product features by <span class=\\"opt-placeholder\\">[PERCENTAGE]</span></span></li><li><span class=\\"opt-modified\\">Conducted comprehensive data analysis using SQL queries and Python scripts, identifying patterns that led to <span class=\\"opt-placeholder\\">[IMPACT]</span> improvement in user engagement</span></li><li><span class=\\"opt-modified\\">Created automated reporting dashboards for management, enabling data-driven decision making across <span class=\\"opt-placeholder\\">[NUMBER]</span> teams</span></li></ul><h3>Skills</h3><ul><li><span class=\\"opt-modified\\">Programming: Python (pandas, numpy, scikit-learn), SQL, JavaScript</span></li><li><span class=\\"opt-modified\\">Data Tools: MySQL, PostgreSQL, Tableau, Power BI, Excel</span></li><li><span class=\\"opt-modified\\">Machine Learning: Regression, Classification, Data Preprocessing</span></li><li>Version Control: Git</li></ul><h3>Education</h3><p>BS Computer Science - State University (2016-2020)</p><p><span class=\\"opt-modified\\">Relevant Coursework: Machine Learning, Data Structures, Database Systems</span></p>",
                        "applied_improvements": [
                            "[Section: Summary] Created professional summary highlighting data analysis background and Python expertise",
                            "[Section: Work Experience] Converted 3 bullets to data-focused achievements with placeholders for metrics",
                            "[Section: Skills] Reorganized and expanded skills to include SQL, Tableau, Power BI, and ML capabilities",
                            "[Section: Education] Added relevant coursework in machine learning and data systems"
                        ]
                    }'''
                }
            }],
            "usage": {
                "prompt_tokens": 1000,
                "completion_tokens": 500,
                "total_tokens": 1500
            }
        }
        
        # Mock embedding response for similarity calculation
        mock_embeddings = [[0.1] * 1536, [0.15] * 1536]  # Slightly different embeddings
        
        with patch.object(service.llm_client, 'chat_completion', 
                         new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            with patch('src.services.index_calculation.get_azure_embedding_client') as mock_embedding:
                mock_client = AsyncMock()
                mock_client.create_embeddings = AsyncMock(return_value=mock_embeddings)
                mock_client.close = AsyncMock()
                mock_embedding.return_value = mock_client
                
                # Execute tailoring
                result = await service.tailor_resume(
                    job_description=sample_request.job_description,
                    original_resume=sample_request.original_resume,
                    gap_analysis=sample_request.gap_analysis,
                    language=sample_request.options.language,
                    include_markers=sample_request.options.include_visual_markers
                )
        
        # Verify result structure
        assert result.resume
        assert result.improvements
        assert '<ul>' in result.improvements or '<ol>' in result.improvements
        assert result.markers.new_section > 0 or result.markers.modified > 0
        
        # Verify similarity and coverage
        assert hasattr(result, 'similarity')
        assert result.similarity.before >= 0
        assert result.similarity.after >= 0
        assert result.similarity.improvement >= 0
        assert hasattr(result, 'coverage')
        assert result.coverage.before.percentage >= 0
        assert result.coverage.after.percentage >= result.coverage.before.percentage
        assert len(result.coverage.newly_added) > 0
        
        # Verify coverage details
        assert result.coverage.before.covered == ["Python", "MySQL"]
        assert len(result.coverage.newly_added) > 0
        
        # Verify visual markers
        assert result.markers.new_section > 0
        assert result.markers.modified > 0
        assert result.markers.placeholder > 0
        
        # Verify keyword marking in output
        assert '<span class="opt-keyword">' in result.resume or \
               '<span class="opt-keyword-existing">' in result.resume
    
    @pytest.mark.asyncio
    async def test_tailoring_without_markers(self, service, sample_request):
        """Test tailoring without visual markers still calculates index."""
        sample_request.options.include_visual_markers = False
        
        mock_llm_response = {
            "choices": [{
                "message": {
                    "content": '''{
                        "optimized_resume": "<h1>John Doe</h1><p>Updated resume content without markers</p>",
                        "applied_improvements": ["[Section: Summary] Added summary"]
                    }'''
                }
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        }
        
        mock_embeddings = [[0.1] * 1536, [0.15] * 1536]
        
        with patch.object(service.llm_client, 'chat_completion', 
                         new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response
            
            with patch('src.services.index_calculation.get_azure_embedding_client') as mock_embedding:
                mock_client = AsyncMock()
                mock_client.create_embeddings = AsyncMock(return_value=mock_embeddings)
                mock_client.close = AsyncMock()
                mock_embedding.return_value = mock_client
                
                result = await service.tailor_resume(
                    job_description=sample_request.job_description,
                    original_resume=sample_request.original_resume,
                    gap_analysis=sample_request.gap_analysis,
                    language="en",
                    include_markers=False
                )
        
        # Verify no markers in output
        assert 'class="opt-' not in result.resume
        
        # Verify coverage calculation still works
        assert result.coverage.before.percentage >= 0
        assert result.coverage.after.percentage >= 0
    
    @pytest.mark.asyncio
    async def test_keyword_marking_accuracy(self, service):
        """Test that keyword marking correctly distinguishes original vs new keywords."""
        from src.core.enhanced_marker import EnhancedMarker
        
        marker = EnhancedMarker()
        
        html = """
        <ul>
            <li>Programming: Python, Java, JavaScript</li>
            <li>Databases: MySQL, PostgreSQL</li>
            <li>Tools: Excel, Tableau, Power BI</li>
        </ul>
        """
        
        original_keywords = ["Python", "MySQL", "Excel"]
        new_keywords = ["JavaScript", "PostgreSQL", "Tableau", "Power BI"]
        
        result = marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Check original keywords marked correctly
        assert '<span class="opt-keyword-existing">Python</span>' in result
        assert '<span class="opt-keyword-existing">MySQL</span>' in result
        assert '<span class="opt-keyword-existing">Excel</span>' in result
        
        # Check new keywords marked correctly
        assert '<span class="opt-keyword">JavaScript</span>' in result
        assert '<span class="opt-keyword">PostgreSQL</span>' in result
        assert '<span class="opt-keyword">Tableau</span>' in result
        assert '<span class="opt-keyword">Power BI</span>' in result
        
        # Check unmarked keyword
        assert '>Java<' in result or 'Java,' in result