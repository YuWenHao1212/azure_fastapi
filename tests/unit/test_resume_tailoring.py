"""
Unit tests for Resume Tailoring Service.
Tests the core functionality without external dependencies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from src.services.resume_tailoring import ResumeTailoringService
from src.models.api.resume_tailoring import (
    GapAnalysisInput,
    TailoringOptions,
    TailorResumeRequest,
    TailoringResult,
    OptimizationStats,
    VisualMarkerStats
)
from src.models.domain.tailoring import (
    OptimizationType,
    TailoringContext
)


@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies"""
    with patch('src.services.resume_tailoring.get_azure_openai_client') as mock_client, \
         patch('src.services.resume_tailoring.monitoring_service') as mock_monitoring, \
         patch('src.services.resume_tailoring.UnifiedPromptService') as mock_prompt_service, \
         patch('src.services.resume_tailoring.EnglishStandardizer') as mock_en_standardizer, \
         patch('src.services.resume_tailoring.TraditionalChineseStandardizer') as mock_zh_standardizer, \
         patch('src.services.resume_tailoring.HTMLProcessor') as mock_html_processor, \
         patch('src.services.resume_tailoring.STARFormatter') as mock_star_formatter, \
         patch('src.services.resume_tailoring.SectionProcessor') as mock_section_processor, \
         patch('src.services.resume_tailoring.LanguageHandler') as mock_language_handler:
        
        # Configure mocks
        mock_client_instance = AsyncMock()
        mock_client.return_value = mock_client_instance
        mock_monitoring.track_event = Mock()
        
        # Mock prompt service
        mock_prompt_instance = Mock()
        mock_prompt_config = Mock()
        mock_prompt_config.get_system_prompt.return_value = "System prompt"
        mock_prompt_config.format_user_prompt.return_value = "User prompt"
        mock_prompt_config.llm_config.temperature = 0.7
        mock_prompt_config.llm_config.max_tokens = 4000
        mock_prompt_config.llm_config.top_p = 0.9
        mock_prompt_instance.get_prompt_config.return_value = mock_prompt_config
        mock_prompt_service.return_value = mock_prompt_instance
        
        # Mock standardizers
        mock_en_instance = Mock()
        mock_en_instance.standardize_keywords.return_value = Mock(standardized_keywords=["python", "machine learning"])
        mock_en_instance.is_standardization_available.return_value = True
        mock_en_standardizer.return_value = mock_en_instance
        
        mock_zh_instance = Mock()
        mock_zh_instance.standardize_keywords.return_value = Mock(standardized_keywords=["機器學習", "深度學習"])
        mock_zh_instance.is_standardization_available.return_value = True
        mock_zh_standardizer.return_value = mock_zh_instance
        
        # Mock HTML processor
        mock_html_instance = Mock()
        mock_html_instance.parse_resume.return_value = Mock(sections={}, has_summary=True, total_sections=3)
        mock_html_instance.validate_html_structure.return_value = (True, None)
        mock_html_instance.count_markers.return_value = {
            "strength": 2, "keyword": 3, "placeholder": 1, "new": 0, "improvement": 2
        }
        mock_html_instance.remove_markers.return_value = '<div class="contact">John Doe</div><h2>Summary</h2><p>Experienced engineer.</p>'
        mock_html_processor.return_value = mock_html_instance
        
        # Mock STAR formatter
        mock_star_instance = Mock()
        mock_star_instance.remove_format_markers.side_effect = lambda x: x  # Return unchanged
        mock_star_formatter.return_value = mock_star_instance
        
        # Mock section processor
        mock_section_instance = Mock()
        mock_section_processor.return_value = mock_section_instance
        
        # Mock language handler
        mock_language_instance = Mock()
        mock_language_instance.is_supported_language.return_value = True
        mock_language_instance.get_output_language.side_effect = lambda lang: "English" if lang == "en" else "Traditional Chinese (繁體中文)"
        mock_language_handler.return_value = mock_language_instance
        
        yield {
            'client': mock_client,
            'client_instance': mock_client_instance,
            'monitoring': mock_monitoring,
            'prompt_service': mock_prompt_service,
            'en_standardizer': mock_en_standardizer,
            'zh_standardizer': mock_zh_standardizer,
            'html_processor': mock_html_processor,
            'star_formatter': mock_star_formatter,
            'section_processor': mock_section_processor,
            'language_handler': mock_language_handler
        }


@pytest.fixture
def sample_gap_analysis():
    """Sample gap analysis input"""
    return GapAnalysisInput(
        core_strengths=["Strong Python skills", "Experience with ML frameworks"],
        quick_improvements=["Add cloud platform experience", "Include more metrics"],
        overall_assessment="Good technical background, needs more leadership examples",
        covered_keywords=["Python", "Machine Learning", "TensorFlow"],
        missing_keywords=["AWS", "Docker", "Kubernetes"]
    )


@pytest.fixture
def sample_resume_html():
    """Sample resume HTML"""
    return """
    <div class="contact">John Doe</div>
    <h2>Summary</h2>
    <p>Experienced software engineer with 5 years of experience.</p>
    <h2>Experience</h2>
    <ul>
        <li>Developed Python applications for data processing</li>
        <li>Built machine learning models using TensorFlow</li>
    </ul>
    <h2>Skills</h2>
    <ul>
        <li>Python</li>
        <li>Machine Learning</li>
        <li>Data Analysis</li>
    </ul>
    """


class TestResumeTailoringService:
    """Test ResumeTailoringService class"""
    
    def test_initialization(self, mock_dependencies):
        """Test service initialization"""
        service = ResumeTailoringService()
        assert service.llm_client is not None
        assert service.monitoring is not None
        assert service.prompt_service is not None
        assert service.en_standardizer is not None
        assert service.zh_tw_standardizer is not None
    
    @pytest.mark.asyncio
    async def test_tailor_resume_success(self, mock_dependencies, sample_gap_analysis, sample_resume_html):
        """Test successful resume tailoring"""
        # Setup
        service = ResumeTailoringService()
        
        # Mock LLM response
        mock_llm_response = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        "optimized_resume": '<div class="contact">John Doe</div><h2>Summary</h2><p class="opt-improvement">Experienced software engineer with 5 years of experience in <span class="opt-keyword">Python</span> and <span class="opt-keyword">Machine Learning</span>.</p>',
                        "applied_improvements": [
                            "[Section: Summary] Added keywords Python and Machine Learning",
                            "[Section: Skills] Added missing keywords AWS, Docker"
                        ]
                    })
                }
            }],
            'usage': {
                'prompt_tokens': 1000,
                'completion_tokens': 500,
                'total_tokens': 1500
            }
        }
        service.llm_client.chat_completion.return_value = mock_llm_response
        
        # Execute
        result = await service.tailor_resume(
            job_description="We are looking for an experienced Python developer with strong machine learning experience and cloud platform knowledge. The ideal candidate should have 5+ years of experience.",
            original_resume=sample_resume_html,
            gap_analysis=sample_gap_analysis,
            language="en",
            include_markers=True
        )
        
        # Verify
        assert isinstance(result, TailoringResult)
        assert result.optimized_resume is not None
        assert len(result.applied_improvements) == 2
        assert result.optimization_stats.sections_modified > 0
        assert result.visual_markers.keyword_count > 0
        
        # Verify monitoring was called
        mock_dependencies['monitoring'].track_event.assert_called()
    
    @pytest.mark.asyncio
    async def test_tailor_resume_with_chinese(self, mock_dependencies, sample_gap_analysis, sample_resume_html):
        """Test resume tailoring with Chinese language"""
        # Setup
        service = ResumeTailoringService()
        
        # Mock LLM response in Chinese
        mock_llm_response = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        "optimized_resume": '<div class="contact">張三</div><h2>摘要</h2><p class="opt-improvement">具有5年經驗的軟體工程師，專精<span class="opt-keyword">Python</span>和<span class="opt-keyword">機器學習</span>。</p>',
                        "applied_improvements": [
                            "[章節: 摘要] 新增關鍵字 Python 和機器學習",
                            "[章節: 技能] 新增缺少的關鍵字 AWS、Docker"
                        ]
                    })
                }
            }]
        }
        service.llm_client.chat_completion.return_value = mock_llm_response
        
        # Execute
        result = await service.tailor_resume(
            job_description="我們正在尋找具有豐富機器學習經驗的Python開發人員。理想的候選人應該具有5年以上的工作經驗，熟悉雲端平台和容器化技術。",
            original_resume=sample_resume_html,
            gap_analysis=sample_gap_analysis,
            language="zh-TW",
            include_markers=True
        )
        
        # Verify
        assert isinstance(result, TailoringResult)
        assert result.optimized_resume is not None
        assert "張三" in result.optimized_resume
        assert len(result.applied_improvements) == 2
    
    @pytest.mark.asyncio
    async def test_tailor_resume_without_markers(self, mock_dependencies, sample_gap_analysis, sample_resume_html):
        """Test resume tailoring without visual markers"""
        # Setup
        service = ResumeTailoringService()
        
        # Mock LLM response
        mock_llm_response = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        "optimized_resume": '<div class="contact">John Doe</div><h2>Summary</h2><p class="opt-improvement">Experienced engineer.</p>',
                        "applied_improvements": ["Summary updated"]
                    })
                }
            }]
        }
        service.llm_client.chat_completion.return_value = mock_llm_response
        
        # Execute
        result = await service.tailor_resume(
            job_description="We are seeking a talented software engineer to join our team. The ideal candidate will have strong programming skills and experience with modern development practices.",
            original_resume=sample_resume_html,
            gap_analysis=sample_gap_analysis,
            language="en",
            include_markers=False
        )
        
        # Verify markers are removed
        assert "opt-improvement" not in result.optimized_resume
        assert "opt-keyword" not in result.optimized_resume
    
    @pytest.mark.asyncio
    async def test_validation_errors(self, mock_dependencies, sample_gap_analysis):
        """Test validation errors"""
        service = ResumeTailoringService()
        
        # Test short job description
        with pytest.raises(ValueError, match="Job description too short"):
            await service.tailor_resume(
                job_description="Too short",
                original_resume="<h1>Resume</h1>" * 20,
                gap_analysis=sample_gap_analysis,
                language="en"
            )
        
        # Test short resume
        with pytest.raises(ValueError, match="Resume too short"):
            await service.tailor_resume(
                job_description="A" * 60,
                original_resume="<p>Short</p>",
                gap_analysis=sample_gap_analysis,
                language="en"
            )
        
        # Test unsupported language
        # Mock language handler to return False for unsupported language
        service.language_handler.is_supported_language.side_effect = lambda lang: lang in ["en", "zh-TW"]
        
        with pytest.raises(ValueError, match="Unsupported language"):
            await service.tailor_resume(
                job_description="A" * 60,
                original_resume="<h1>Resume</h1>" * 20,
                gap_analysis=sample_gap_analysis,
                language="fr"
            )
    
    @pytest.mark.asyncio
    async def test_llm_retry_mechanism(self, mock_dependencies, sample_gap_analysis, sample_resume_html):
        """Test LLM retry mechanism on failure"""
        # Setup
        service = ResumeTailoringService()
        
        # Mock LLM to fail twice then succeed
        service.llm_client.chat_completion.side_effect = [
            Exception("Network error"),
            Exception("Timeout error"),
            {
                'choices': [{
                    'message': {
                        'content': json.dumps({
                            "optimized_resume": "<h1>Optimized</h1>",
                            "applied_improvements": ["Improved"]
                        })
                    }
                }]
            }
        ]
        
        # Execute
        result = await service.tailor_resume(
            job_description="A" * 60,
            original_resume=sample_resume_html,
            gap_analysis=sample_gap_analysis,
            language="en"
        )
        
        # Verify
        assert result.optimized_resume == "<h1>Optimized</h1>"
        assert service.llm_client.chat_completion.call_count == 3
    
    def test_parse_llm_response_valid_json(self, mock_dependencies):
        """Test parsing valid JSON LLM response"""
        service = ResumeTailoringService()
        
        valid_json = json.dumps({
            "optimized_resume": "<h1>Resume</h1>",
            "applied_improvements": ["Improvement 1", "Improvement 2"]
        })
        
        result = service._parse_llm_response(valid_json)
        assert result["optimized_resume"] == "<h1>Resume</h1>"
        assert len(result["applied_improvements"]) == 2
    
    def test_parse_llm_response_invalid_json(self, mock_dependencies):
        """Test parsing invalid JSON with fallback"""
        service = ResumeTailoringService()
        
        invalid_json = '''
        Some text before
        "optimized_resume": "<h1>Resume</h1>",
        "applied_improvements": ["Improvement 1", "Improvement 2"]
        Some text after
        '''
        
        result = service._parse_llm_response(invalid_json)
        assert result["optimized_resume"] == "<h1>Resume</h1>"
        assert len(result["applied_improvements"]) == 2
    
    def test_calculate_optimization_stats(self, mock_dependencies):
        """Test optimization statistics calculation"""
        service = ResumeTailoringService()
        
        applied_improvements = [
            "[Section: Summary] Added keywords",
            "[Section: Experience] Improved bullet points",
            "Added keyword Python",
            "Highlighted strength in ML",
            "General improvement"
        ]
        
        optimized_resume = "Resume with [PLACEHOLDER] and [ANOTHER]"
        
        stats = service._calculate_optimization_stats(
            "<h1>Original</h1>",
            optimized_resume,
            applied_improvements
        )
        
        assert stats.sections_modified == 2
        assert stats.keywords_added == 2  # Fixed: "keyword" appears twice in improvements
        assert stats.strengths_highlighted == 1
        assert stats.placeholders_added == 1  # Rough estimate
    
    def test_remove_format_markers(self):
        """Test STAR/PAR format marker removal"""
        # Test the actual STARFormatter class without mocks
        from src.core.star_formatter import STARFormatter
        
        formatter = STARFormatter()
        text_with_markers = "This is (S) situation. (T) Task was defined. (A) Action taken. (R) Result achieved."
        cleaned = formatter.remove_format_markers(text_with_markers)
        
        assert "(S)" not in cleaned
        assert "(T)" not in cleaned
        assert "(A)" not in cleaned
        assert "(R)" not in cleaned
        assert "situation" in cleaned
        assert "Result achieved" in cleaned
    
    @pytest.mark.asyncio
    async def test_plain_text_support(self, mock_dependencies, sample_gap_analysis):
        """Test that plain text inputs are supported"""
        service = ResumeTailoringService()
        
        # Mock the LLM response
        service.llm_client.chat_completion.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        "optimized_resume": "<h1>John Doe</h1><p>Senior Software Engineer</p>",
                        "applied_improvements": ["Added senior positioning"]
                    })
                }
            }],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150}
        }
        
        plain_text_jd = "We are looking for a Senior Python Developer with 5+ years of experience in building scalable applications."
        plain_text_resume = """John Doe
Software Engineer

Experience:
- Developed Python applications
- Built machine learning models
- Led team of 3 developers

Skills: Python, JavaScript, Machine Learning"""
        
        result = await service.tailor_resume(
            job_description=plain_text_jd,
            original_resume=plain_text_resume,
            gap_analysis=sample_gap_analysis
        )
        
        assert result is not None
        assert result.optimized_resume is not None
        # Should contain HTML tags after processing
        assert '<h1>' in result.optimized_resume or '<p>' in result.optimized_resume