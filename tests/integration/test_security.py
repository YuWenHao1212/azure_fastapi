"""
Security Tests for API Endpoints
Tests for SQL injection, XSS, and input validation
"""

import json
import re

import httpx
import pytest

# Test data for various attack vectors
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1' UNION SELECT NULL--",
    "admin'--",
    "' OR 1=1--",
    "1' AND '1'='1",
    "' UNION ALL SELECT NULL,NULL,NULL--",
    "1' ORDER BY 1--",
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<iframe src='javascript:alert(\"XSS\")'></iframe>",
    "javascript:alert('XSS')",
    "<body onload=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "';alert(String.fromCharCode(88,83,83))//",
    "<input type='text' value='<script>alert(\"XSS\")</script>'>",
]

MALFORMED_INPUT_PAYLOADS = [
    None,
    "",
    " ",
    "a" * 10000,  # Very long string
    {"nested": {"deeply": {"nested": {"object": {}}}}},  # Deep nesting
    ["list"] * 1000,  # Large list
    "\\x00\\x01\\x02",  # Null bytes
    "🔥" * 1000,  # Unicode stress test
]

# Boundary value test cases
BOUNDARY_VALUES = {
    "max_keywords": [-1, 0, 51, 100, 999999],
    "prompt_version": ["", "0.0.0", "999.999.999", "invalid", "1.2.3.4.5"],
    "language": ["xx", "unknown", "en-US-invalid", "123", ""],
}


class TestAPISecurity:
    """Test suite for API security vulnerabilities"""
    
    @pytest.fixture
    def client(self):
        """Create HTTP client for testing"""
        return httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0)
    
    @pytest.mark.asyncio
    async def test_keyword_extraction_sql_injection(self, client):
        """Test keyword extraction endpoint against SQL injection"""
        endpoint = "/api/v1/extract-jd-keywords"
        
        for payload in SQL_INJECTION_PAYLOADS:
            data = {
                "job_description": f"Software Engineer {payload}",
                "max_keywords": 10
            }
            
            response = await client.post(endpoint, json=data)
            assert response.status_code in [200, 403, 422], f"Unexpected status for payload: {payload}"
            
            # If successful, check response doesn't contain SQL error messages
            if response.status_code == 200:
                result = response.json()
                response_text = json.dumps(result).lower()
                
                # Check for common SQL error indicators
                sql_error_patterns = [
                    "sql", "syntax error", "mysql", "postgresql", 
                    "sqlite", "database", "query", "table"
                ]
                
                for pattern in sql_error_patterns:
                    assert pattern not in response_text, f"Possible SQL leak with payload: {payload}"
    
    @pytest.mark.asyncio
    async def test_keyword_extraction_xss(self, client):
        """Test keyword extraction endpoint against XSS attacks"""
        endpoint = "/api/v1/extract-jd-keywords"
        
        for payload in XSS_PAYLOADS:
            data = {
                "job_description": payload,
                "max_keywords": 10
            }
            
            response = await client.post(endpoint, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check that XSS payloads are properly escaped/sanitized
                response_text = json.dumps(result)
                
                # Raw script tags should not appear in response
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
                assert "onerror=" not in response_text
                
                # Check keywords are properly sanitized
                if "data" in result and "keywords" in result["data"]:
                    for keyword in result["data"]["keywords"]:
                        assert not re.search(r'<.*?>', keyword), f"HTML tags in keyword: {keyword}"
    
    @pytest.mark.asyncio
    async def test_malformed_input_handling(self, client):
        """Test API handling of malformed inputs"""
        endpoints = [
            "/api/v1/extract-jd-keywords",
            "/api/v1/index-calculation",
            "/api/v1/format-resume",
        ]
        
        for endpoint in endpoints:
            for payload in MALFORMED_INPUT_PAYLOADS:
                # Test job_description field
                data = {"job_description": payload}
                
                if endpoint == "/api/v1/extract-jd-keywords":
                    data["max_keywords"] = 10
                elif endpoint == "/api/v1/index-calculation":
                    data["resume"] = "Test resume"
                    data["keywords"] = ["test"]
                elif endpoint == "/api/v1/format-resume":
                    data["resume_text"] = "Test resume" if payload is None else payload
                    data.pop("job_description", None)
                
                try:
                    response = await client.post(endpoint, json=data)
                    # Should either validate properly or return 422
                    assert response.status_code in [200, 422], \
                        f"Unexpected status {response.status_code} for {endpoint} with payload type {type(payload)}"
                    
                    # Check error messages don't leak sensitive info
                    if response.status_code == 422:
                        error_data = response.json()
                        error_text = json.dumps(error_data).lower()
                        
                        # Should not expose internal details
                        assert "traceback" not in error_text
                        assert "file \"/" not in error_text
                        assert "line " not in error_text
                        
                except httpx.ReadTimeout:
                    # Long payloads might timeout, which is acceptable
                    pass
    
    @pytest.mark.asyncio
    async def test_boundary_value_validation(self, client):
        """Test boundary value validation"""
        endpoint = "/api/v1/extract-jd-keywords"
        
        # Test max_keywords boundaries
        for value in BOUNDARY_VALUES["max_keywords"]:
            data = {
                "job_description": "Software Engineer with Python experience",
                "max_keywords": value
            }
            
            response = await client.post(endpoint, json=data)
            
            if value < 1 or value > 50:
                # Should reject out-of-range values
                assert response.status_code == 422, f"Should reject max_keywords={value}"
            else:
                assert response.status_code == 200, f"Should accept max_keywords={value}"
        
        # Test prompt_version validation
        for value in BOUNDARY_VALUES["prompt_version"]:
            data = {
                "job_description": "Software Engineer with Python experience",
                "max_keywords": 10,
                "prompt_version": value
            }
            
            response = await client.post(endpoint, json=data)
            
            # Invalid versions should either use default or return 422
            assert response.status_code in [200, 422], \
                f"Unexpected response for prompt_version={value}"
    
    @pytest.mark.asyncio
    async def test_content_type_validation(self, client):
        """Test that API properly validates content types"""
        endpoint = "/api/v1/extract-jd-keywords"
        data = {"job_description": "Test", "max_keywords": 10}
        
        # Test various content types
        content_types = [
            "application/xml",
            "text/plain",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "",  # Empty content type
        ]
        
        for content_type in content_types:
            headers = {"Content-Type": content_type} if content_type else {}
            
            response = await client.post(
                endpoint, 
                content=json.dumps(data),
                headers=headers
            )
            
            # Should reject non-JSON content types
            assert response.status_code in [415, 422], \
                f"Should reject content-type: {content_type}"
    
    @pytest.mark.asyncio
    async def test_large_payload_handling(self, client):
        """Test handling of large payloads"""
        endpoint = "/api/v1/extract-jd-keywords"
        
        # Create increasingly large payloads
        sizes = [1_000, 10_000, 100_000, 1_000_000]  # Characters
        
        for size in sizes:
            large_text = "A" * size
            data = {
                "job_description": large_text,
                "max_keywords": 10
            }
            
            try:
                response = await client.post(endpoint, json=data, timeout=10.0)
                
                # Should either handle it or reject with 413/422
                assert response.status_code in [200, 413, 422], \
                    f"Unexpected status for {size} character payload"
                
                # If accepted, should not take too long
                if response.status_code == 200:
                    result = response.json()
                    # Check reasonable response size
                    assert len(json.dumps(result)) < size, \
                        "Response should be smaller than input"
                        
            except httpx.ReadTimeout:
                # Timeout is acceptable for very large payloads
                if size < 100_000:
                    pytest.fail(f"Timeout for {size} character payload")
    
    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, client):
        """Test prevention of path traversal attacks"""
        # This test is for any endpoints that might handle file paths
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        endpoint = "/api/v1/extract-jd-keywords"
        
        for payload in payloads:
            data = {
                "job_description": f"Engineer needed for {payload} project",
                "max_keywords": 10
            }
            
            response = await client.post(endpoint, json=data)
            
            # Should process normally without attempting file access
            assert response.status_code == 200
            
            result = response.json()
            # Ensure no file contents in response
            assert "root:" not in json.dumps(result)
            assert "Users\\" not in json.dumps(result)
    
    @pytest.mark.asyncio
    async def test_header_injection(self, client):
        """Test prevention of header injection attacks"""
        endpoint = "/api/v1/extract-jd-keywords"
        
        injection_headers = {
            "X-Injected": "test\r\nX-Another: injected",
            "User-Agent": "Mozilla/5.0\r\nX-Injected: true",
            "Referer": "http://example.com\r\nSet-Cookie: session=hijacked",
        }
        
        data = {
            "job_description": "Software Engineer position",
            "max_keywords": 10
        }
        
        for header, value in injection_headers.items():
            headers = {header: value}
            
            response = await client.post(endpoint, json=data, headers=headers)
            
            # Should handle without allowing injection
            assert response.status_code == 200
            
            # Check response headers don't contain injected values
            assert "X-Injected" not in response.headers
            assert "session=hijacked" not in str(response.headers)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_resistance(self, client):
        """Test API behavior under rapid requests (basic DoS test)"""
        endpoint = "/api/v1/extract-jd-keywords"
        data = {
            "job_description": "Quick test",
            "max_keywords": 5
        }
        
        # Send 20 rapid requests
        responses = []
        for _ in range(20):
            response = await client.post(endpoint, json=data)
            responses.append(response.status_code)
        
        # Should handle all requests (with possible rate limiting)
        # Accept either all 200s or mix of 200s and 429s (rate limit)
        valid_statuses = {200, 429}
        assert all(status in valid_statuses for status in responses), \
            f"Unexpected statuses: {set(responses) - valid_statuses}"
        
        # At least some should succeed
        assert responses.count(200) > 0, "No requests succeeded"


class TestResumeTailoringSecurity:
    """Security tests specific to resume tailoring endpoint"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0)
    
    @pytest.mark.asyncio
    async def test_html_injection_in_resume(self, client):
        """Test HTML injection prevention in resume content"""
        endpoint = "/api/v1/tailor-resume"
        
        malicious_resume = """
        <h1>John Doe</h1>
        <script>alert('XSS')</script>
        <p onmouseover="alert('XSS')">Software Engineer</p>
        <iframe src="javascript:alert('XSS')"></iframe>
        """
        
        data = {
            "job_description": "Looking for Software Engineer",
            "original_resume": malicious_resume,
            "gap_analysis": {
                "core_strengths": ["Programming"],
                "key_gaps": ["Leadership"],
                "quick_improvements": ["Add metrics"],
                "covered_keywords": ["Python"],
                "missing_keywords": ["Java"]
            },
            "options": {
                "include_visual_markers": True,
                "language": "en"
            }
        }
        
        response = await client.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            tailored_resume = result["data"]["resume"]
            
            # Check that script tags are sanitized
            assert "<script>" not in tailored_resume
            assert "javascript:" not in tailored_resume
            assert "onmouseover=" not in tailored_resume
            assert "<iframe" not in tailored_resume
    
    @pytest.mark.asyncio
    async def test_gap_analysis_injection(self, client):
        """Test injection attacks via gap analysis fields"""
        endpoint = "/api/v1/tailor-resume"
        
        data = {
            "job_description": "Software Engineer needed",
            "original_resume": "<h1>Test Resume</h1><p>Engineer</p>",
            "gap_analysis": {
                "core_strengths": ["<script>alert('XSS')</script>"],
                "key_gaps": ["'; DROP TABLE users; --"],
                "quick_improvements": ["Add <img src=x onerror=alert('XSS')>"],
                "covered_keywords": ["Python<script>alert('XSS')</script>"],
                "missing_keywords": ["Java'); DELETE FROM users; --"]
            },
            "options": {
                "include_visual_markers": True,
                "language": "en"
            }
        }
        
        response = await client.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            response_text = json.dumps(result)
            
            # Ensure no unescaped malicious content
            assert "<script>" not in response_text
            assert "DROP TABLE" not in response_text
            assert "DELETE FROM" not in response_text


# Run security tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])