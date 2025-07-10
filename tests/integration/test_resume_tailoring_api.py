"""
Integration tests for Resume Tailoring API endpoints.
Tests the full API flow including request/response handling.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.main import app
from src.models.api.resume_tailoring import (
    OptimizationStats,
    TailoringResult,
    VisualMarkerStats,
)


@pytest.fixture
def sample_request_data():
    """Sample request data for testing"""
    return {
        "job_description": """
        We are looking for a Senior Software Engineer with expertise in Python and Machine Learning.
        The ideal candidate should have experience with cloud platforms (AWS preferred), 
        containerization (Docker, Kubernetes), and building scalable ML pipelines.
        5+ years of experience required.
        """,
        "original_resume": """
        <div class="header">
            <h1>John Doe</h1>
            <p>Software Engineer | john.doe@email.com</p>
        </div>
        <h2>Summary</h2>
        <p>Experienced software engineer with strong background in Python development.</p>
        <h2>Experience</h2>
        <div class="job">
            <h3>Software Engineer - TechCorp (2019-Present)</h3>
            <ul>
                <li>Developed Python applications for data processing and analysis</li>
                <li>Built machine learning models for customer behavior prediction</li>
                <li>Collaborated with cross-functional teams to deliver features</li>
            </ul>
        </div>
        <h2>Skills</h2>
        <ul>
            <li>Programming: Python, JavaScript, SQL</li>
            <li>Machine Learning: TensorFlow, Scikit-learn</li>
            <li>Tools: Git, JIRA, VS Code</li>
        </ul>
        <h2>Education</h2>
        <p>B.S. Computer Science - State University (2018)</p>
        """,
        "gap_analysis": {
            "core_strengths": [
                "Strong Python programming skills demonstrated through multiple projects",
                "Machine learning experience with practical applications",
                "Collaborative team player with cross-functional experience"
            ],
            "quick_improvements": [
                "Add specific metrics to achievements (e.g., improved performance by X%)",
                "Include cloud platform experience (AWS/Azure/GCP)",
                "Highlight leadership or mentoring experiences",
                "Add containerization skills (Docker/Kubernetes)"
            ],
            "overall_assessment": "Strong technical foundation with Python and ML. To better match the senior role, emphasize leadership experiences and add cloud/DevOps skills.",
            "covered_keywords": ["Python", "Machine Learning", "Software Engineer", "TensorFlow"],
            "missing_keywords": ["AWS", "Docker", "Kubernetes", "scalable", "pipelines", "Senior"]
        },
        "options": {
            "include_visual_markers": True,
            "language": "en"
        }
    }


@pytest.fixture
def sample_chinese_request_data():
    """Sample Chinese request data for testing"""
    return {
        "job_description": """
        我們正在尋找資深軟體工程師，需要精通Python和機器學習。
        理想的候選人應該有雲端平台經驗（優先AWS），容器化技術（Docker、Kubernetes），
        以及建構可擴展ML管道的經驗。需要5年以上工作經驗。
        """,
        "original_resume": """
        <div class="header">
            <h1>張三</h1>
            <p>軟體工程師 | zhangsan@email.com</p>
        </div>
        <h2>摘要</h2>
        <p>經驗豐富的軟體工程師，擅長Python開發。</p>
        <h2>工作經歷</h2>
        <div class="job">
            <h3>軟體工程師 - 科技公司 (2019-至今)</h3>
            <ul>
                <li>開發Python應用程式進行資料處理和分析</li>
                <li>建構機器學習模型預測客戶行為</li>
                <li>與跨部門團隊合作交付功能</li>
            </ul>
        </div>
        <h2>技能</h2>
        <ul>
            <li>程式語言：Python、JavaScript、SQL</li>
            <li>機器學習：TensorFlow、Scikit-learn</li>
            <li>工具：Git、JIRA、VS Code</li>
        </ul>
        """,
        "gap_analysis": {
            "core_strengths": [
                "扎實的Python程式設計能力",
                "機器學習實務經驗",
                "良好的團隊合作能力"
            ],
            "quick_improvements": [
                "加入具體的成就指標",
                "增加雲端平台經驗說明",
                "突顯領導或指導經驗"
            ],
            "overall_assessment": "技術基礎扎實，建議強調領導經驗並補充雲端技能。",
            "covered_keywords": ["Python", "機器學習", "軟體工程師"],
            "missing_keywords": ["AWS", "Docker", "Kubernetes", "資深"]
        },
        "options": {
            "include_visual_markers": True,
            "language": "zh-TW"
        }
    }


class TestResumeTailoringAPI:
    """Test Resume Tailoring API endpoints"""
    
    @pytest.mark.asyncio
    async def test_tailor_resume_endpoint_success(self, sample_request_data):
        """Test successful resume tailoring via API"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Mock the service at the module level where it's instantiated
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                # Mock successful response
                mock_service.tailor_resume = AsyncMock(return_value=TailoringResult(
                    optimized_resume='<h1>Optimized Resume</h1><p class="opt-keyword">Python</p>',
                    applied_improvements=[
                        "[Section: Summary] Added senior-level positioning",
                        "[Section: Skills] Added AWS, Docker, Kubernetes"
                    ],
                    optimization_stats=OptimizationStats(
                        sections_modified=2,
                        keywords_added=3,
                        strengths_highlighted=2,
                        placeholders_added=1
                    ),
                    visual_markers=VisualMarkerStats(
                        strength_count=2,
                        keyword_count=3,
                        placeholder_count=1,
                        new_content_count=0,
                        improvement_count=2
                    )
                ))
                
                # Make request
                response = await client.post(
                    "/api/v1/tailor-resume",
                    json=sample_request_data
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"] is not None
                assert "optimized_resume" in data["data"]
                assert "applied_improvements" in data["data"]
                assert len(data["data"]["applied_improvements"]) == 2
                assert data["data"]["optimization_stats"]["sections_modified"] == 2
                assert data["data"]["visual_markers"]["keyword_count"] == 3
    
    @pytest.mark.asyncio
    async def test_tailor_resume_chinese_language(self, sample_chinese_request_data):
        """Test resume tailoring with Chinese language"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                # Mock Chinese response
                mock_service.tailor_resume = AsyncMock(return_value=TailoringResult(
                    optimized_resume='<h1>優化後的履歷</h1><p class="opt-keyword">Python</p>',
                    applied_improvements=[
                        "[章節: 摘要] 加入資深工程師定位",
                        "[章節: 技能] 新增AWS、Docker、Kubernetes"
                    ],
                    optimization_stats=OptimizationStats(
                        sections_modified=2,
                        keywords_added=3,
                        strengths_highlighted=1,
                        placeholders_added=0
                    ),
                    visual_markers=VisualMarkerStats(
                        strength_count=1,
                        keyword_count=3,
                        placeholder_count=0,
                        new_content_count=1,
                        improvement_count=2
                    )
                ))
                
                # Make request
                response = await client.post(
                    "/api/v1/tailor-resume",
                    json=sample_chinese_request_data
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "優化後的履歷" in data["data"]["optimized_resume"]
    
    @pytest.mark.asyncio
    async def test_tailor_resume_without_markers(self, sample_request_data):
        """Test resume tailoring without visual markers"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                # Mock response without markers
                mock_service.tailor_resume = AsyncMock(return_value=TailoringResult(
                    optimized_resume='<h1>Optimized Resume</h1><p>Clean text without markers</p>',
                    applied_improvements=["Improvements applied"],
                    optimization_stats=OptimizationStats(
                        sections_modified=1,
                        keywords_added=0,
                        strengths_highlighted=0,
                        placeholders_added=0
                    ),
                    visual_markers=VisualMarkerStats(
                        strength_count=0,
                        keyword_count=0,
                        placeholder_count=0,
                        new_content_count=0,
                        improvement_count=0
                    )
                ))
                
                # Modify request to disable markers
                request_data = sample_request_data.copy()
                request_data["options"]["include_visual_markers"] = False
                
                response = await client.post(
                    "/api/v1/tailor-resume",
                    json=request_data
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "opt-" not in data["data"]["optimized_resume"]
    
    @pytest.mark.asyncio
    async def test_tailor_resume_validation_error(self, sample_request_data):
        """Test validation error handling"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                mock_service.tailor_resume = AsyncMock(side_effect=ValueError("Invalid input data"))
                
                response = await client.post(
                    "/api/v1/tailor-resume",
                    json=sample_request_data
                )
                
                assert response.status_code == 200  # Bubble.io compatibility
                data = response.json()
                assert data["success"] is False
                assert data["error"]["code"] == "INVALID_REQUEST"
                assert "Invalid input data" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_tailor_resume_server_error(self, sample_request_data):
        """Test server error handling"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                mock_service.tailor_resume = AsyncMock(side_effect=Exception("Internal server error"))
                
                response = await client.post(
                    "/api/v1/tailor-resume",
                    json=sample_request_data
                )
                
                assert response.status_code == 200  # Bubble.io compatibility
                data = response.json()
                assert data["success"] is False
                assert data["error"]["code"] == "TAILORING_ERROR"
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                mock_service.en_standardizer.is_standardization_available.return_value = True
                mock_service.zh_tw_standardizer.is_standardization_available.return_value = True
                
                response = await client.get("/api/v1/tailor-resume/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["status"] == "healthy"
                assert data["data"]["service"] == "resume_tailoring"
                assert data["data"]["standardizers"]["en"] is True
                assert data["data"]["standardizers"]["zh-TW"] is True
    
    @pytest.mark.asyncio
    async def test_supported_languages_endpoint(self):
        """Test supported languages endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/tailor-resume/supported-languages")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "en" in data["data"]["languages"]
            assert "zh-TW" in data["data"]["languages"]
            assert data["data"]["default"] == "en"
    
    @pytest.mark.asyncio
    async def test_bubble_io_response_format(self, sample_request_data):
        """Test that responses follow Bubble.io format requirements"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('src.api.v1.resume_tailoring.tailoring_service') as mock_service:
                # Test success case
                mock_service.tailor_resume = AsyncMock(return_value=TailoringResult(
                    optimized_resume='<h1>Resume</h1>',
                    applied_improvements=[],
                    optimization_stats=OptimizationStats(
                        sections_modified=0,
                        keywords_added=0,
                        strengths_highlighted=0,
                        placeholders_added=0
                    ),
                    visual_markers=VisualMarkerStats(
                        strength_count=0,
                        keyword_count=0,
                        placeholder_count=0,
                        new_content_count=0,
                        improvement_count=0
                    )
                ))
                
                response = await client.post(
                    "/api/v1/tailor-resume",
                    json=sample_request_data
                )
                
                data = response.json()
                
                # Check required fields exist
                assert "success" in data
                assert "data" in data
                assert "error" in data
                
                # Check error structure exists even on success
                assert "code" in data["error"]
                assert "message" in data["error"]
                assert "details" in data["error"]
                
                # Verify no Optional types (all fields present)
                assert data["error"]["code"] == ""
                assert data["error"]["message"] == ""
                assert data["error"]["details"] == ""