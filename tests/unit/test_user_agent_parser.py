"""
Unit tests for User-Agent parser.
"""
from src.utils.user_agent_parser import get_client_category, parse_user_agent


class TestUserAgentParser:
    """Test User-Agent parsing functionality."""
    
    def test_bubble_io_detection(self):
        """Test Bubble.io User-Agent detection."""
        user_agents = [
            "Bubble",
            "bubble.io/1.0",
            "Bubble.io API Client"
        ]
        
        for ua in user_agents:
            result = parse_user_agent(ua)
            assert result["client_type"] == "bubble.io"
            assert result["is_api_client"] is True
            assert result["is_browser"] is False
    
    def test_curl_detection(self):
        """Test curl User-Agent detection."""
        result = parse_user_agent("curl/7.79.1")
        assert result["client_type"] == "curl"
        assert result["client_details"] == "curl 7.79.1"
        assert result["is_api_client"] is True
    
    def test_python_requests_detection(self):
        """Test Python requests library detection."""
        result = parse_user_agent("python-requests/2.28.1")
        assert result["client_type"] == "python-requests"
        assert "2.28.1" in result["client_details"]
        assert result["is_api_client"] is True
    
    def test_browser_detection(self):
        """Test browser User-Agent detection."""
        chrome_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        result = parse_user_agent(chrome_ua)
        assert result["client_type"] == "browser"
        assert "Chrome" in result["client_details"]
        assert result["is_browser"] is True
        assert result["is_api_client"] is False
    
    def test_postman_detection(self):
        """Test Postman User-Agent detection."""
        result = parse_user_agent("PostmanRuntime/7.32.1")
        assert result["client_type"] == "postman"
        assert result["is_api_client"] is True
    
    def test_empty_user_agent(self):
        """Test empty User-Agent handling."""
        result = parse_user_agent("")
        assert result["client_type"] == "unknown"
        assert result["is_api_client"] is True
    
    def test_unknown_user_agent(self):
        """Test unknown User-Agent handling."""
        result = parse_user_agent("MyCustomBot/1.0")
        assert result["client_type"] == "other"
        assert result["client_details"] == "MyCustomBot/1.0"
    
    def test_client_categories(self):
        """Test client category classification."""
        assert get_client_category("curl") == "api_testing"
        assert get_client_category("postman") == "api_testing"
        assert get_client_category("bubble.io") == "automation"
        assert get_client_category("python-requests") == "automation"
        assert get_client_category("browser") == "browser"
        assert get_client_category("mobile-app") == "mobile"
        assert get_client_category("unknown") == "other"