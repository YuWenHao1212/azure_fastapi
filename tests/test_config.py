"""
Test configuration management for Azure FastAPI tests.
Centralizes test settings to avoid hardcoding and improve maintainability.
"""
import logging
import os

logger = logging.getLogger(__name__)


class TestConfig:
    """Centralized test configuration management."""
    
    @staticmethod
    def get_default_prompt_version() -> str:
        """
        Get the default prompt version for tests.
        Priority: Environment variable > Actual default from code
        """
        # Check environment variable first
        env_version = os.getenv("TEST_PROMPT_VERSION")
        if env_version:
            logger.info(f"Using TEST_PROMPT_VERSION from environment: {env_version}")
            return env_version
        
        # Otherwise, get from actual default in code
        try:

            from src.models.keyword_extraction import KeywordExtractionRequest
            
            # Get the default value from the field
            default_version = KeywordExtractionRequest.__fields__["prompt_version"].default
            logger.info(f"Using default prompt version from code: {default_version}")
            return default_version
        except Exception as e:
            logger.warning(f"Failed to get default prompt version: {e}")
            # Fallback to a known version
            return "1.4.0"
    
    @staticmethod
    def get_test_prompt_versions() -> list[str]:
        """Get list of prompt versions to test."""
        env_versions = os.getenv("TEST_PROMPT_VERSIONS")
        if env_versions:
            return [v.strip() for v in env_versions.split(",")]
        # Default test versions
        return ["1.0.0", "1.3.0", "1.4.0", "latest"]
    
    @staticmethod
    def should_skip_external_api_tests() -> bool:
        """Check if external API tests should be skipped."""
        return os.getenv("SKIP_EXTERNAL_API_TESTS", "false").lower() == "true"
    
    @staticmethod
    def should_skip_cors_tests() -> bool:
        """Check if CORS-dependent tests should be skipped."""
        return os.getenv("SKIP_CORS_TESTS", "false").lower() == "true"
    
    @staticmethod
    def get_test_api_base_url() -> str:
        """Get the API base URL for tests."""
        return os.getenv("TEST_API_BASE_URL", "http://localhost:8000")
    
    @staticmethod
    def get_test_cors_origins() -> list[str]:
        """Get allowed CORS origins for testing."""
        env_origins = os.getenv("TEST_CORS_ORIGINS")
        if env_origins:
            return [origin.strip() for origin in env_origins.split(",")]
        # Default includes localhost for testing
        return [
            "http://localhost:8000",
            "http://localhost:3000",
            "https://airesumeadvisor.bubbleapps.io"
        ]
    
    @staticmethod
    def get_rate_limit_delay() -> float:
        """Get delay between API calls to avoid rate limits."""
        return float(os.getenv("TEST_RATE_LIMIT_DELAY", "1.0"))
    
    @staticmethod
    def is_ci_environment() -> bool:
        """Check if running in CI environment."""
        return any([
            os.getenv("CI"),
            os.getenv("GITHUB_ACTIONS"),
            os.getenv("AZURE_DEVOPS")
        ])