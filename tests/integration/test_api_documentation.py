"""
API Documentation Tests
Ensure OpenAPI spec consistency and documentation accuracy
"""

import re
from typing import Any

import httpx
import pytest


class TestAPIDocumentation:
    """Test suite for API documentation and OpenAPI spec validation"""
    
    @pytest.fixture
    def client(self):
        """Create HTTP client for testing"""
        return httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0)
    
    @pytest.fixture
    async def openapi_spec(self, client) -> dict[str, Any]:
        """Fetch and cache OpenAPI specification"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200, "Failed to fetch OpenAPI spec"
        return response.json()
    
    @pytest.mark.asyncio
    async def test_openapi_spec_available(self, client):
        """Test that OpenAPI spec is accessible"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
        
        # Validate OpenAPI version
        assert spec["openapi"].startswith("3."), "Should use OpenAPI 3.x"
    
    @pytest.mark.asyncio
    async def test_api_info_completeness(self, openapi_spec):
        """Test that API info section is complete"""
        info = openapi_spec.get("info", {})
        
        # Required fields
        assert "title" in info, "API title is missing"
        assert "version" in info, "API version is missing"
        
        # Recommended fields
        assert "description" in info, "API description is missing"
        
        # Validate content
        assert len(info["title"]) > 0, "API title is empty"
        assert re.match(r"\d+\.\d+\.\d+", info["version"]), "Version should follow semver"
    
    @pytest.mark.asyncio
    async def test_all_endpoints_documented(self, openapi_spec):
        """Test that all endpoints are documented"""
        paths = openapi_spec.get("paths", {})
        
        # Expected endpoints based on the codebase
        expected_endpoints = [
            "/api/v1/health",
            "/api/v1/extract-jd-keywords",
            "/api/v1/index-calculation",
            "/api/v1/index-cal-and-gap-analysis",
            "/api/v1/format-resume",
            "/api/v1/tailor-resume",
            "/api/v1/supported-languages",
        ]
        
        documented_endpoints = list(paths.keys())
        
        for endpoint in expected_endpoints:
            assert endpoint in documented_endpoints, f"Endpoint {endpoint} is not documented"
    
    @pytest.mark.asyncio
    async def test_endpoint_methods_documented(self, openapi_spec):
        """Test that all endpoint methods are properly documented"""
        paths = openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            # Skip if it's a reference
            if "$ref" in methods:
                continue
                
            # Check common HTTP methods
            for method in methods:
                if method in ["get", "post", "put", "delete", "patch"]:
                    method_spec = methods[method]
                    
                    # Should have summary or description
                    assert "summary" in method_spec or "description" in method_spec, \
                        f"{method.upper()} {path} lacks summary/description"
                    
                    # Should have responses
                    assert "responses" in method_spec, \
                        f"{method.upper()} {path} lacks response documentation"
                    
                    # Should have at least 200 response
                    assert "200" in method_spec["responses"], \
                        f"{method.upper()} {path} lacks 200 response documentation"
    
    @pytest.mark.asyncio
    async def test_request_body_schemas(self, openapi_spec):
        """Test that request bodies have proper schemas"""
        paths = openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            if "$ref" in methods:
                continue
                
            for method in ["post", "put", "patch"]:
                if method in methods:
                    method_spec = methods[method]
                    
                    # POST/PUT/PATCH should typically have request body
                    if "requestBody" in method_spec:
                        request_body = method_spec["requestBody"]
                        
                        # Should have content
                        assert "content" in request_body, \
                            f"{method.upper()} {path} request body lacks content"
                        
                        # Should support application/json
                        assert "application/json" in request_body["content"], \
                            f"{method.upper()} {path} doesn't support JSON"
                        
                        # Should have schema
                        json_content = request_body["content"]["application/json"]
                        assert "schema" in json_content, \
                            f"{method.upper()} {path} lacks request schema"
    
    @pytest.mark.asyncio
    async def test_response_schemas(self, openapi_spec):
        """Test that responses have proper schemas"""
        paths = openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            if "$ref" in methods:
                continue
                
            for method, method_spec in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    responses = method_spec.get("responses", {})
                    
                    # Check 200 response has schema
                    if "200" in responses:
                        response_200 = responses["200"]
                        
                        # Should have content for non-DELETE
                        if method != "delete" and "content" in response_200:
                            content = response_200["content"]
                            
                            # Should support application/json
                            if "application/json" in content:
                                json_content = content["application/json"]
                                assert "schema" in json_content, \
                                    f"{method.upper()} {path} 200 response lacks schema"
    
    @pytest.mark.asyncio
    async def test_error_responses_documented(self, openapi_spec):
        """Test that error responses are documented"""
        paths = openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            if "$ref" in methods:
                continue
                
            for method, method_spec in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    responses = method_spec.get("responses", {})
                    
                    # Should document common error responses
                    common_errors = ["400", "422", "500"]
                    documented_errors = [code for code in common_errors if code in responses]
                    
                    # At least one error response should be documented
                    assert len(documented_errors) > 0, \
                        f"{method.upper()} {path} lacks error response documentation"
    
    @pytest.mark.asyncio
    async def test_schema_definitions(self, openapi_spec):
        """Test that schema definitions are complete"""
        components = openapi_spec.get("components", {})
        schemas = components.get("schemas", {})
        
        # Should have schema definitions
        assert len(schemas) > 0, "No schema definitions found"
        
        # Check each schema
        for schema_name, schema_def in schemas.items():
            # Should have type or allOf/oneOf/anyOf
            assert any(key in schema_def for key in ["type", "allOf", "oneOf", "anyOf"]), \
                f"Schema {schema_name} lacks type definition"
            
            # If object type, should have properties
            if schema_def.get("type") == "object" and "allOf" not in schema_def:
                assert "properties" in schema_def, \
                    f"Object schema {schema_name} lacks properties"
    
    @pytest.mark.asyncio
    async def test_actual_vs_documented_responses(self, client, openapi_spec):
        """Test that actual API responses match documentation"""
        # Test a few key endpoints
        test_cases = [
            {
                "endpoint": "/api/v1/health",
                "method": "get",
                "data": None,
            },
            {
                "endpoint": "/api/v1/supported-languages",
                "method": "get",
                "data": None,
            },
            {
                "endpoint": "/api/v1/extract-jd-keywords",
                "method": "post",
                "data": {
                    "job_description": "Software Engineer with Python",
                    "max_keywords": 10
                },
            },
        ]
        
        paths = openapi_spec.get("paths", {})
        
        for test_case in test_cases:
            endpoint = test_case["endpoint"]
            method = test_case["method"]
            data = test_case["data"]
            
            # Make actual request
            if method == "get":
                response = await client.get(endpoint)
            else:
                response = await client.post(endpoint, json=data)
            
            # Get documented response schema
            if endpoint in paths and method in paths[endpoint]:
                method_spec = paths[endpoint][method]
                responses = method_spec.get("responses", {})
                
                status_code = str(response.status_code)
                assert status_code in responses, \
                    f"Status {status_code} not documented for {method.upper()} {endpoint}"
                
                # If successful, validate response structure
                if response.status_code == 200:
                    actual_data = response.json()
                    
                    # Basic structure validation
                    assert isinstance(actual_data, dict), "Response should be object"
                    
                    # Check for common response structure
                    if "success" in actual_data:
                        assert isinstance(actual_data["success"], bool)
                    if "data" in actual_data:
                        assert actual_data["data"] is not None
    
    @pytest.mark.asyncio
    async def test_parameter_documentation(self, openapi_spec):
        """Test that parameters are properly documented"""
        paths = openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            if "$ref" in methods:
                continue
                
            for method, method_spec in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    # Check path parameters
                    if "{" in path:  # Has path parameters
                        assert "parameters" in method_spec, \
                            f"{method.upper()} {path} lacks parameter documentation"
                        
                        # Extract parameter names from path
                        param_names = re.findall(r"{(\w+)}", path)
                        documented_params = [
                            p["name"] for p in method_spec.get("parameters", [])
                            if p.get("in") == "path"
                        ]
                        
                        for param_name in param_names:
                            assert param_name in documented_params, \
                                f"Path parameter {param_name} not documented"
                    
                    # Check query parameters if any
                    if "parameters" in method_spec:
                        for param in method_spec["parameters"]:
                            # Should have required fields
                            assert "name" in param, "Parameter missing name"
                            assert "in" in param, "Parameter missing 'in' field"
                            assert "schema" in param, "Parameter missing schema"
    
    @pytest.mark.asyncio
    async def test_security_documentation(self, openapi_spec):
        """Test that security schemes are documented if used"""
        components = openapi_spec.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        
        # Check if any endpoints require security
        paths = openapi_spec.get("paths", {})
        requires_security = False
        
        for path, methods in paths.items():
            if "$ref" in methods:
                continue
                
            for method, method_spec in methods.items():
                if "security" in method_spec:
                    requires_security = True
                    break
            
            if requires_security:
                break
        
        # If security is required, should have security schemes
        if requires_security:
            assert len(security_schemes) > 0, \
                "Security is required but no security schemes documented"
    
    @pytest.mark.asyncio
    async def test_example_values(self, openapi_spec):
        """Test that schemas include example values"""
        components = openapi_spec.get("components", {})
        schemas = components.get("schemas", {})
        
        # Count schemas with examples
        schemas_with_examples = 0
        total_schemas = len(schemas)
        
        for schema_name, schema_def in schemas.items():
            if "example" in schema_def or "examples" in schema_def:
                schemas_with_examples += 1
            elif schema_def.get("type") == "object" and "properties" in schema_def:
                # Check if properties have examples
                props_with_examples = sum(
                    1 for prop in schema_def["properties"].values()
                    if "example" in prop or "examples" in prop
                )
                if props_with_examples > 0:
                    schemas_with_examples += 1
        
        # At least 50% of schemas should have examples
        example_ratio = schemas_with_examples / total_schemas if total_schemas > 0 else 0
        assert example_ratio >= 0.5, \
            f"Only {example_ratio:.1%} of schemas have examples (should be >= 50%)"
    
    @pytest.mark.asyncio
    async def test_deprecated_endpoints_marked(self, openapi_spec):
        """Test that deprecated endpoints are properly marked"""
        paths = openapi_spec.get("paths", {})
        
        for path, methods in paths.items():
            if "$ref" in methods:
                continue
                
            for method, method_spec in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    # If deprecated, should be marked
                    if "deprecated" in method_spec:
                        assert isinstance(method_spec["deprecated"], bool), \
                            f"Deprecated flag should be boolean for {method.upper()} {path}"
                        
                        # Deprecated endpoints should have explanation
                        assert "description" in method_spec, \
                            f"Deprecated endpoint {method.upper()} {path} should explain why"


# Run documentation tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])