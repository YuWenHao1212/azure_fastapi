"""
Pytest configuration and shared fixtures for Work Item #348.
Provides common test utilities for unit testing keyword extraction functionality.
"""
import asyncio

# Add src to Python path for imports
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.config import Settings
from src.models.keyword_extraction import (
    KeywordExtractionData,
    KeywordExtractionRequest,
)
from src.models.response import ErrorDetail, UnifiedResponse
from tests.test_config import TestConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock Settings for testing."""
    settings = Mock(spec=Settings)
    settings.azure_openai_endpoint = "https://test.openai.azure.com/"
    settings.azure_openai_api_key = "test-api-key"
    settings.azure_openai_api_version = "2023-12-01-preview"
    settings.azure_openai_deployment_name = "gpt-4o-2"
    settings.openai_timeout = 30.0
    settings.openai_max_retries = 3
    settings.debug = True
    settings.log_level = "INFO"
    return settings


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    We are seeking a Senior Python Developer with experience in FastAPI, machine learning, 
    and cloud technologies. The ideal candidate should have strong backend development skills, 
    experience with databases, API design, and modern software development practices. 
    Knowledge of Azure, Docker, and CI/CD pipelines is preferred.
    """


@pytest.fixture
def sample_keyword_extraction_request():
    """Sample keyword extraction request for testing."""
    return KeywordExtractionRequest(
        job_description="We are seeking a Senior Python Developer with experience in FastAPI, machine learning, and backend development. The ideal candidate should have 5+ years of experience with Python frameworks and cloud deployment. Experience with Docker and microservices is preferred.",
        max_keywords=20,  # Updated to correct default
        include_standardization=True,
        use_multi_round_validation=True,
        prompt_version=TestConfig.get_default_prompt_version()
    )


@pytest.fixture
def default_prompt_version():
    """Get the default prompt version for tests."""
    return TestConfig.get_default_prompt_version()


@pytest.fixture
def test_prompt_versions():
    """Get list of prompt versions to test."""
    return TestConfig.get_test_prompt_versions()


@pytest.fixture
def skip_external_api():
    """Check if external API tests should be skipped."""
    return TestConfig.should_skip_external_api_tests()


@pytest.fixture
def skip_cors_tests():
    """Check if CORS tests should be skipped."""
    return TestConfig.should_skip_cors_tests()


@pytest.fixture
def test_api_base_url():
    """Get the test API base URL."""
    return TestConfig.get_test_api_base_url()


@pytest.fixture
def sample_keyword_extraction_data():
    """Sample KeywordExtractionData for testing."""
    return KeywordExtractionData(
        keywords=["Python", "FastAPI", "Machine Learning", "Backend", "API Design"],
        keyword_count=5,
        confidence_score=0.85,
        extraction_method="2_round_intersection",
        intersection_stats={
            "intersection_count": 3,
            "round1_count": 8,
            "round2_count": 7,
            "total_available": 10,
            "final_count": 5,
            "supplement_count": 2,
            "strategy_used": "2_round_intersection_with_supplement",
            "warning": False,
            "warning_message": ""
        },
        warning={
            "has_warning": False,
            "message": "",
            "expected_minimum": 12,
            "actual_extracted": 5,
            "suggestion": ""
        },
        processing_time_ms=2500.0
    )


@pytest.fixture
def sample_unified_response_success(sample_keyword_extraction_data):
    """Sample successful UnifiedResponse for testing."""
    return UnifiedResponse(
        success=True,
        data=sample_keyword_extraction_data.model_dump(),
        error=ErrorDetail(),
        timestamp=datetime.utcnow().isoformat()
    )


@pytest.fixture
def sample_unified_response_error():
    """Sample error UnifiedResponse for testing."""
    return UnifiedResponse(
        success=False,
        data={},
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message="輸入參數驗證失敗",
            details="Job description too short"
        ),
        timestamp=datetime.utcnow().isoformat()
    )


@pytest.fixture
def mock_azure_openai_response():
    """Mock Azure OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"keywords": ["Python", "FastAPI", "Machine Learning", "Backend", "API Design"]}'
                }
            }
        ],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 50,
            "total_tokens": 200
        }
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = AsyncMock()
    client.chat_completion = AsyncMock()
    client.close = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    # Add properties that AzureOpenAIClient would have
    client.endpoint = "https://test.openai.azure.com"
    client.api_key = "test-api-key"
    client.api_version = "2024-02-15-preview"
    client.deployment_id = "gpt-4o-2"
    return client


@pytest.fixture
def mock_prompt_manager():
    """Mock SimplePromptManager for testing."""
    manager = Mock()
    manager.load_prompt_config = Mock(return_value={
        "system_prompt": "You are an expert at extracting keywords from job descriptions.",
        "user_prompt_template": "Extract keywords from: {job_description}",
        "max_keywords": 25,
        "temperature": 0.1,
        "max_tokens": 500
    })
    manager.get_prompt = Mock(return_value="Extract keywords from job description")
    return manager


@pytest.fixture  
def mock_base_service():
    """Mock BaseService for testing."""
    service = Mock()
    service.start_operation = Mock()
    service.end_operation = Mock()
    service.log_info = Mock()
    service.log_error = Mock()
    service.log_warning = Mock()
    return service


@pytest.fixture
def sample_round1_keywords():
    """Sample round 1 keywords for intersection testing."""
    return [
        "Python", "FastAPI", "Machine Learning", "Backend Development", 
        "API Design", "Database", "Cloud Technologies", "Software Engineering"
    ]


@pytest.fixture
def sample_round2_keywords():
    """Sample round 2 keywords for intersection testing."""
    return [
        "Python", "FastAPI", "ML", "Backend", "APIs", 
        "Azure", "Docker", "CI/CD", "Development"
    ]


@pytest.fixture
def sample_intersection_result():
    """Sample intersection calculation result."""
    return ["Python", "FastAPI", "Backend"]


# Test data for different scenarios
@pytest.fixture
def short_job_description():
    """Job description that's too short for validation."""
    return "Python dev"


@pytest.fixture
def long_job_description():
    """Very long job description for stress testing."""
    return """
    We are seeking an exceptional Senior Python Developer to join our dynamic team in building 
    next-generation applications using cutting-edge technologies. The ideal candidate will have 
    extensive experience in Python programming, FastAPI framework, machine learning algorithms, 
    deep learning, natural language processing, computer vision, cloud computing platforms including 
    Azure, AWS, Google Cloud, containerization technologies like Docker and Kubernetes, 
    microservices architecture, API design and development, database technologies including SQL 
    and NoSQL databases, data engineering, ETL processes, big data technologies, DevOps practices, 
    CI/CD pipelines, infrastructure as code, monitoring and logging, security best practices, 
    agile development methodologies, code review processes, software testing, unit testing, 
    integration testing, performance optimization, scalability considerations, system design, 
    software architecture patterns, design patterns, clean code principles, technical leadership, 
    mentoring junior developers, project management, stakeholder communication, and continuous 
    learning mindset.
    """ * 10


@pytest.fixture
def malformed_openai_response():
    """Malformed OpenAI response for error testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Invalid JSON: {keywords: [missing quotes]}"
                }
            }
        ]
    }


# Mock patches for common dependencies
@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient for testing."""
    client = AsyncMock()
    client.post = AsyncMock()
    client.close = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing."""
    env_vars = {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-api-key",
        "AZURE_OPENAI_API_VERSION": "2023-12-01-preview",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-2"
    }
    with patch.dict("os.environ", env_vars):
        yield env_vars


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to all tests in tests/unit/
        if "tests/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to all tests in tests/integration/
        elif "tests/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def azure_openai_credentials():
    """Credentials for AzureOpenAIClient testing."""
    return {
        "endpoint": "https://test.openai.azure.com",
        "api_key": "test-api-key",
        "api_version": "2024-02-15-preview"
    } 