# Changelog

All notable changes to this project will be documented in this file.

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