# Changelog

All notable changes to this project will be documented in this file.

## [1.6.0] - 2025-07-11

### Added
- Resume Tailoring API (`/api/v1/resume-tailoring`) - New endpoint for optimizing resumes based on job requirements
- Integration with Gap Analysis for intelligent content adjustments
- Support for plain text input format (Bubble.io compatibility)
- Flexible input parsing for various resume formats
- Comprehensive API documentation for Resume Tailoring endpoint

### Fixed
- Unit test compatibility issues with language normalization
- Response validator to properly flag invalid Bubble.io responses
- Monitoring middleware test to include client_type parameter

### Changed
- Gap Analysis now uses v1.2.0 prompts for zh-TW language for improved stability
- Improved LLM response parsing for better error handling
- Enhanced API documentation structure

## [1.5.0] - 2025-01-06

### Added
- ASGI interface implementation for proper Azure Functions telemetry collection
- ASGIHandler class for managing ASGI communication state
- Application Insights monitoring dashboard configurations
- Comprehensive monitoring documentation

### Fixed
- Application Insights requests table now receives telemetry data
- Event loop handling for pytest compatibility using nest_asyncio
- Monitoring service automatically disables in test environment

### Changed
- Replaced TestClient with direct ASGI implementation
- Updated requirements.txt to include nest_asyncio dependency
- Enhanced error handling and logging in function_app.py

### Security
- Removed hardcoded function keys from test scripts
- Added secure template for test data generation

## [1.4.0] - 2025-01-05

### Added
- Monitoring middleware implementation
- Security monitoring and threat detection
- Endpoint metrics collection
- Custom telemetry points

### Changed
- Updated prompt versions for keyword extraction
- Enhanced bilingual support