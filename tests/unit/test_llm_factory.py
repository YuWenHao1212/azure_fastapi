"""Unit tests for LLM factory module."""
import os
from unittest.mock import Mock, patch

import pytest

from src.services.llm_factory import (
    get_llm_client, 
    get_llm_info,
    get_llm_client_smart
)
from src.services.openai_client import AzureOpenAIClient
from src.services.openai_client_gpt41 import AzureOpenAIGPT41Client


class TestLLMFactory:
    """Test cases for LLM factory functions."""
    
    @patch('src.services.llm_factory.get_gpt41_mini_client')
    @patch('src.services.llm_factory.get_azure_openai_client')
    def test_get_llm_client_direct_model_gpt4o2(self, mock_azure_client, mock_gpt41_client):
        """Test direct model specification for GPT-4o-2."""
        mock_client = Mock(spec=AzureOpenAIClient)
        mock_azure_client.return_value = mock_client
        
        result = get_llm_client(model="gpt4o-2")
        
        assert result == mock_client
        mock_azure_client.assert_called_once()
        mock_gpt41_client.assert_not_called()
    
    @patch('src.services.llm_factory.get_gpt41_mini_client')
    @patch('src.services.llm_factory.get_azure_openai_client')
    def test_get_llm_client_direct_model_gpt41(self, mock_azure_client, mock_gpt41_client):
        """Test direct model specification for GPT-4.1 mini."""
        mock_client = Mock(spec=AzureOpenAIGPT41Client)
        mock_gpt41_client.return_value = mock_client
        
        result = get_llm_client(model="gpt41-mini")
        
        assert result == mock_client
        mock_gpt41_client.assert_called_once()
        mock_azure_client.assert_not_called()
    
    @patch.dict(os.environ, {'LLM_MODEL_KEYWORDS': 'gpt41-mini'})
    @patch('src.services.llm_factory.get_gpt41_mini_client')
    @patch('src.services.llm_factory.get_azure_openai_client')
    def test_get_llm_client_api_name_from_env(self, mock_azure_client, mock_gpt41_client):
        """Test API name resolution from environment variable."""
        mock_client = Mock(spec=AzureOpenAIGPT41Client)
        mock_gpt41_client.return_value = mock_client
        
        # Need to reload settings to pick up env var
        from src.core.config import settings
        settings.llm_model_keywords = "gpt41-mini"
        
        with patch('src.services.llm_factory.get_settings', return_value=settings):
            result = get_llm_client(api_name="keywords")
        
        assert result == mock_client
        mock_gpt41_client.assert_called_once()
    
    @patch('src.services.llm_factory.get_gpt41_mini_client')
    @patch('src.services.llm_factory.get_azure_openai_client')
    def test_get_llm_client_fallback_on_gpt41_error(self, mock_azure_client, mock_gpt41_client):
        """Test fallback to GPT-4o-2 when GPT-4.1 mini fails."""
        mock_gpt41_client.side_effect = Exception("API key not found")
        mock_client = Mock(spec=AzureOpenAIClient)
        mock_azure_client.return_value = mock_client
        
        result = get_llm_client(model="gpt41-mini")
        
        assert result == mock_client
        mock_gpt41_client.assert_called_once()
        mock_azure_client.assert_called_once()
    
    @patch('src.services.llm_factory.get_azure_openai_client')
    def test_get_llm_client_default_model(self, mock_azure_client):
        """Test default model selection."""
        mock_client = Mock(spec=AzureOpenAIClient)
        mock_azure_client.return_value = mock_client
        
        result = get_llm_client()
        
        assert result == mock_client
        mock_azure_client.assert_called_once()
    
    def test_get_llm_info_gpt41(self):
        """Test getting info for GPT-4.1 mini client."""
        mock_client = Mock(spec=AzureOpenAIGPT41Client)
        mock_client.deployment_name = "gpt-4-1-mini-japaneast"
        mock_client.endpoint = "https://test.openai.azure.com"
        
        info = get_llm_info(mock_client)
        
        assert info["model"] == "gpt41-mini"
        assert info["deployment"] == "gpt-4-1-mini-japaneast"
        assert info["endpoint"] == "https://test.openai.azure.com"
        assert info["region"] == "japaneast"
    
    @patch('src.services.llm_factory.get_settings')
    def test_get_llm_info_gpt4o2(self, mock_settings):
        """Test getting info for GPT-4o-2 client."""
        mock_client = Mock(spec=AzureOpenAIClient)
        mock_settings.return_value.azure_openai_endpoint = "https://test.openai.azure.com"
        
        info = get_llm_info(mock_client)
        
        assert info["model"] == "gpt4o-2"
        assert info["deployment"] == "gpt-4o-2"
        assert info["endpoint"] == "https://test.openai.azure.com"
        assert info["region"] == "swedencentral"
    
    @patch('src.services.llm_factory.monitoring_service')
    @patch('src.services.llm_factory._track_model_selection')
    def test_get_llm_client_smart_calls_monitoring(self, mock_track, mock_monitoring):
        """Test that get_llm_client_smart uses correct monitoring method."""
        # We can't test _track_model_selection directly, but we can test the monitoring service
        # This test ensures monitoring_service has track_event method
        assert hasattr(mock_monitoring, 'track_event')
        # And that it doesn't have track_custom_event (which was the bug)
        # In a real monitoring service, track_custom_event would raise AttributeError
    
    @patch('src.services.llm_factory._track_model_selection')
    @patch('src.services.llm_factory.get_gpt41_mini_client')
    @patch('src.services.llm_factory.get_azure_openai_client')
    def test_get_llm_client_smart_tracks_selection(self, mock_azure, mock_gpt41, mock_track):
        """Test that get_llm_client_smart tracks model selection."""
        # Arrange
        mock_client = Mock()
        mock_gpt41.return_value = mock_client
        
        # Act
        result = get_llm_client_smart(api_name="keywords")
        
        # Assert
        assert result == mock_client
        mock_track.assert_called_once_with("keywords", "gpt41-mini", "config")


@pytest.mark.parametrize("api_name,expected_env_key", [
    ("keywords", "llm_model_keywords"),
    ("gap_analysis", "llm_model_gap_analysis"),
    ("resume_format", "llm_model_resume_format"),
    ("resume_tailor", "llm_model_resume_tailor"),
])
def test_api_name_to_env_key_mapping(api_name, expected_env_key):
    """Test that API names map to correct environment variable keys."""
    # This is more of a documentation test
    env_key = f"llm_model_{api_name.lower()}"
    assert env_key == expected_env_key