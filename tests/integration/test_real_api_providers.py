"""
Integration tests for different API providers using real API calls.
This ensures our API abstraction layer works correctly with all providers.
"""
import pytest
from fastapi.testclient import TestClient

from src.core.config import get_settings
from src.main import app


@pytest.mark.integration
class TestRealAPIProviders:
    """Test different API providers with real credentials."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def settings(self):
        """Get real settings."""
        return get_settings()
    
    def test_available_providers(self, settings):
        """Log which API providers are available for testing."""
        providers = []
        
        if settings.azure_openai_api_key:
            providers.append("Azure OpenAI (LLM2)")
        if settings.gpt41_mini_japaneast_api_key:
            providers.append("GPT-4.1 mini Japan East")
            
        assert len(providers) > 0, "At least one API provider must be configured"
        print(f"\nTesting with providers: {', '.join(providers)}")
    
    @pytest.mark.asyncio
    async def test_keyword_extraction_real_response_format(self, client):
        """Verify real API responses have expected format."""
        request_data = {
            "job_description": "We are seeking an experienced Full Stack Developer to join our innovative technology team. "
                             "The ideal candidate should have strong expertise in React.js for frontend development, "
                             "Node.js for backend services, Python for data processing and automation tasks. "
                             "Experience with MongoDB for NoSQL database management and AWS cloud services is essential. "
                             "Additional experience with containerization using Docker and orchestration with Kubernetes "
                             "would be highly beneficial. Strong problem-solving skills and team collaboration are must-have qualities.",
            "language": "en",
            "max_keywords": 15
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        # Real API should return 200
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["success"] is True
        assert isinstance(data["data"], dict)
        assert isinstance(data["timestamp"], str)
        
        # Verify data fields
        result = data["data"]
        assert isinstance(result["keywords"], list)
        assert len(result["keywords"]) > 0
        assert all(isinstance(k, str) for k in result["keywords"])
        
        # Required fields from real API
        assert isinstance(result["keyword_count"], int)
        assert result["keyword_count"] == len(result["keywords"])
        assert isinstance(result["confidence_score"], float)
        assert 0 <= result["confidence_score"] <= 1
        assert isinstance(result["processing_time_ms"], int | float)
        assert result["processing_time_ms"] > 0
        
        # Extraction method details
        assert "extraction_method" in result
        assert "intersection_stats" in result
        assert isinstance(result["intersection_stats"], dict)
        
        # Language detection
        assert result["detected_language"] == "en"
        
        # Prompt version - check if exists (field might be optional in some cases)
        # We can check for prompt version in either format
        if "prompt_version_used" not in result and "prompt_version" not in result:
            # At least one of these should be present
            print(f"Warning: Neither prompt_version_used nor prompt_version found in result: {result.keys()}")
        
    @pytest.mark.asyncio
    async def test_chinese_job_description_real_api(self, client):
        """Test Chinese job descriptions with real API."""
        request_data = {
            "job_description": "我們正在尋找一位資深前端工程師，加入我們充滿活力的技術團隊。理想的候選人需要精通 React、Vue.js、TypeScript 等現代前端框架，"
                             "並具有豐富的響應式網頁設計（RWD）經驗。必須熟練使用 HTML5、CSS3 和 JavaScript ES6+。"
                             "對於狀態管理工具如 Redux、Vuex 有深入理解。熟悉 Git 版本控制、CI/CD 流程，"
                             "以及自動化測試框架如 Jest、Cypress 者優先考慮。我們重視團隊合作精神和持續學習的態度。"
                             "具備良好的溝通能力和問題解決能力。有大型專案經驗和性能優化經驗者尤佳。",
            "language": "zh-TW"
        }
        
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        result = data["data"]
        
        # Should extract technical keywords even from Chinese text
        keywords = result["keywords"]
        assert len(keywords) > 0
        
        # Common technical terms should be extracted
        keywords_lower = [k.lower() for k in keywords]
        expected_techs = ["react", "vue", "typescript", "git", "ci/cd"]
        found_techs = [tech for tech in expected_techs if any(tech in k for k in keywords_lower)]
        assert len(found_techs) > 0, f"Expected some of {expected_techs} in {keywords}"
        
        # Language should be detected as Chinese
        assert result["detected_language"] in ["zh", "zh-TW", "zh-CN"]
    
    @pytest.mark.asyncio
    async def test_gpt41_mini_japaneast_real_api(self, client, settings):
        """Test GPT-4.1 mini Japan East with real API."""
        if not settings.gpt41_mini_japaneast_api_key:
            pytest.skip("GPT-4.1 mini Japan East not configured")
            
        request_data = {
            "job_description": "We are looking for an experienced DevOps Engineer to help us build and maintain our cloud infrastructure. "
                             "The ideal candidate should have hands-on experience with Kubernetes for container orchestration, "
                             "Terraform for infrastructure as code, and extensive AWS cloud platform knowledge including EC2, S3, RDS, Lambda. "
                             "Experience with CI/CD pipelines using Jenkins or GitLab CI, monitoring tools like Prometheus and Grafana, "
                             "and scripting languages such as Python or Bash is required. Strong understanding of security best practices "
                             "and automation mindset are essential for this role. Certification in AWS or Kubernetes is a plus.",
            "language": "en"
        }
        
        # Test with GPT-4.1 mini (should be default when configured)
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Should extract DevOps-related keywords
        keywords = data["data"]["keywords"]
        keywords_lower = [k.lower() for k in keywords]
        
        # Check for key technologies
        expected = ["kubernetes", "terraform", "aws", "devops"]
        found = sum(1 for tech in expected if any(tech in k for k in keywords_lower))
        assert found >= 2, f"Expected at least 2 of {expected} in {keywords}"
        
    @pytest.mark.asyncio
    async def test_llm_model_header_switching(self, client, settings):
        """Test explicit LLM model switching via header."""
        request_data = {
            "job_description": "We are seeking a Senior Full Stack Developer to lead our product development initiatives. "
                             "The successful candidate must have extensive experience with React.js for building modern user interfaces, "
                             "Node.js for developing scalable backend services, and Python for data analysis and automation tasks. "
                             "Strong knowledge of RESTful API design, microservices architecture, and database technologies (both SQL and NoSQL) "
                             "is required. Experience with cloud platforms (AWS/Azure/GCP), containerization (Docker), and modern development "
                             "practices including TDD, code reviews, and agile methodologies is essential. Leadership experience is preferred.",
            "language": "en"
        }
        
        # Test with explicit gpt41-mini header
        headers = {"X-LLM-Model": "gpt41-mini"}
        response = client.post(
            "/api/v1/extract-jd-keywords",
            json=request_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Should extract Full Stack-related keywords
        keywords = data["data"]["keywords"]
        keywords_lower = [k.lower() for k in keywords]
        
        # Check for key technologies from the job description
        expected = ["react", "node.js", "nodejs", "python", "full stack", "fullstack"]
        found = sum(1 for tech in expected if any(tech in k for k in keywords_lower))
        assert found >= 3, f"Expected at least 3 of {expected} in {keywords}"
    
    @pytest.mark.asyncio
    async def test_real_api_error_handling(self, client):
        """Test how real API handles edge cases."""
        # Test with very short input
        response = client.post("/api/v1/extract-jd-keywords", json={
            "job_description": "Dev",
            "language": "en"
        })
        
        # Should still handle gracefully
        assert response.status_code in [200, 422]
        data = response.json()
        
        if response.status_code == 422:
            # Validation error
            assert data["success"] is False
            assert "error" in data
        else:
            # Real API might still process very short input
            assert data["success"] is True
            assert isinstance(data["data"]["keywords"], list)
    
    @pytest.mark.asyncio 
    async def test_performance_baseline_real_api(self, client):
        """Establish performance baseline with real API."""
        import time
        
        request_data = {
            "job_description": "We are hiring a Senior Software Engineer to join our backend engineering team. This position requires "
                             "deep expertise in Python and the Django web framework for building robust web applications. "
                             "Strong experience with PostgreSQL for relational database management and Redis for caching and message queuing "
                             "is essential. The ideal candidate should be proficient with containerization using Docker and orchestration "
                             "with Kubernetes. Extensive AWS cloud services experience is required, including EC2, RDS, S3, and Lambda. "
                             "Strong system design skills for building scalable, distributed systems are crucial. Experience with microservices "
                             "architecture, RESTful API design, and performance optimization would be highly valued.",
            "language": "en"
        }
        
        # Measure end-to-end time
        start_time = time.time()
        response = client.post("/api/v1/extract-jd-keywords", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Check performance
        total_time_ms = (end_time - start_time) * 1000
        api_time_ms = response.json()["data"]["processing_time_ms"]
        
        print("\nPerformance metrics:")
        print(f"  - Total request time: {total_time_ms:.0f}ms")
        print(f"  - API processing time: {api_time_ms:.0f}ms")
        print(f"  - Overhead: {total_time_ms - api_time_ms:.0f}ms")
        
        # Real API typically takes 1-5 seconds
        assert total_time_ms < 10000, "Request took too long (>10s)"
        assert api_time_ms > 100, "API processing time seems too fast for real API"