# Integration Tests for Keyword Extraction API

**Work Item**: #349 - 撰寫整合測試  
**Created**: 2025-07-02  
**Author**: Claude Code (Opus 4)

## Overview

This directory contains integration tests for the keyword extraction API functionality. These tests verify the end-to-end operation of the system, including API endpoints, service interactions, and real-world scenarios.

## Test Files

### 1. `test_keyword_extraction_acceptance.py`
Acceptance tests based on test cases from TEST_KEYWORD_EXTRACTION_20250630:
- TC001: Standard job description extraction
- TC002: Quality warning mechanism
- TC003: Long job description performance
- TC004: Error handling for invalid input
- TC005: Standardization functionality
- TC006: Concurrent request handling
- TC007: Prompt version handling
- TC008: Response consistency

### 2. `test_service_integration.py`
Service-level integration tests:
- Integration with KeywordStandardizer
- Prompt manager integration
- Multi-round validation flow
- Error propagation
- Hot reload functionality
- Performance with caching
- Concurrent service calls
- Quality metrics calculation

### 3. `test_end_to_end_scenarios.py`
Real-world scenario tests:
- Job board integration
- Resume matching
- Skill gap analysis
- Multilingual job handling
- Rate limiting scenarios
- Edge cases handling
- Performance monitoring
- Consistency verification

## Running Integration Tests

### Prerequisites
1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export AZURE_OPENAI_ENDPOINT="your-endpoint"
   export AZURE_OPENAI_API_KEY="your-key"
   export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
   export AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"
   ```

### Running All Integration Tests
```bash
# From project root
pytest tests/integration/ -v

# With coverage
pytest tests/integration/ --cov=src --cov-report=html

# Run specific test file
pytest tests/integration/test_keyword_extraction_acceptance.py -v

# Run specific test
pytest tests/integration/test_keyword_extraction_acceptance.py::TestKeywordExtractionAcceptance::test_tc001_standard_job_description_extraction -v
```

### Running with Markers
```bash
# Run only integration tests
pytest -m integration

# Run integration tests excluding slow ones
pytest -m "integration and not slow"
```

## Test Configuration

Integration tests use mocked OpenAI responses by default to ensure:
- Consistent test results
- No API costs during testing
- Fast test execution
- Predictable behavior

To run against real Azure OpenAI API (not recommended for CI/CD):
```python
# Set environment variable
export USE_REAL_OPENAI=true
```

## Expected Test Results

All tests should pass with the following characteristics:
- Response times < 10 seconds for standard requests
- Consistency rate > 80% for identical inputs
- All required fields present in responses (Bubble.io compatibility)
- Proper error handling and validation

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from project root
   - Check PYTHONPATH includes src directory

2. **Timeout Errors**
   - Increase timeout in test configuration
   - Check network connectivity

3. **Mock Failures**
   - Verify mock patches match actual import paths
   - Check for version compatibility

### Debug Mode

Run tests with debug output:
```bash
pytest tests/integration/ -v -s --log-cli-level=DEBUG
```

## Coverage Goals

Target coverage for integration tests:
- API endpoints: 100%
- Service integration points: 90%
- Error handling paths: 85%
- Edge cases: 80%

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:
```yaml
# Example GitHub Actions configuration
- name: Run Integration Tests
  run: |
    pytest tests/integration/ -v --junit-xml=test-results.xml
  env:
    AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
    AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
```

## Future Improvements

- [ ] Add performance benchmarking suite
- [ ] Implement load testing scenarios
- [ ] Add contract testing for API compatibility
- [ ] Create integration with real Azure OpenAI (optional flag)
- [ ] Add monitoring and metrics collection tests