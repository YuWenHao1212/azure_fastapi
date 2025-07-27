"""
Integration test specific configuration.
All integration tests use REAL API credentials.
"""
import os
import pytest
from src.core.config import get_settings


@pytest.fixture(scope="module")
def real_settings():
    """Get real settings for integration tests."""
    settings = get_settings()
    
    # Check if we have any valid API credentials
    has_azure = bool(settings.azure_openai_api_key)
    has_gpt41 = bool(settings.gpt41_mini_japaneast_api_key)
    
    if not (has_azure or has_gpt41):
        pytest.skip(
            "Integration tests require real API credentials. "
            "Please set AZURE_OPENAI_API_KEY (or LLM2_API_KEY) or GPT41_MINI_JAPANEAST_API_KEY in .env file"
        )
    
    return settings


@pytest.fixture
def integration_test_marker():
    """Marker to identify integration tests."""
    return True


# Override the global mock_environment_variables to NOT mock in integration tests
@pytest.fixture(autouse=True)
def use_real_environment():
    """Ensure integration tests use real environment variables."""
    # Don't mock anything - use real .env values
    yield


# Log which API is being used for transparency
@pytest.fixture(scope="session", autouse=True)
def log_api_usage():
    """Log which API credentials are available for integration tests."""
    settings = get_settings()
    
    print("\n" + "="*60)
    print("Integration Test API Configuration:")
    print("="*60)
    
    if settings.azure_openai_api_key:
        print("✅ Azure OpenAI API Key (LLM2): Available")
        print(f"   Endpoint: {settings.azure_openai_endpoint}")
    else:
        print("❌ Azure OpenAI API Key (LLM2): Not found")
        
    if settings.gpt41_mini_japaneast_api_key:
        print("✅ GPT-4.1 mini Japan East API Key: Available")
        print(f"   Endpoint: {settings.gpt41_mini_japaneast_endpoint}")
        print(f"   Deployment: {settings.gpt41_mini_japaneast_deployment}")
    else:
        print("❌ GPT-4.1 mini Japan East API Key: Not found")
    
    print("="*60 + "\n")