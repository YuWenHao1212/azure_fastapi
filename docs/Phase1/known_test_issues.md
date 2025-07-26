# Known Test Issues

This document tracks known test failures that exist in the codebase but don't affect functionality.

## Resume Format Tests - RESOLVED (2025-07-09)

All previously failing tests have been fixed:

### Unit Tests (tests/unit/test_resume_format_services.py) - ✅ All Passing
- Phone number correction now works correctly (O→0, I→1)
- Date standardization implemented (YYYY/MM → mmm YYYY)
- Script tag removal fixed using decompose()
- Summary section detection fixed with proper h2 heading
- All 17 unit tests passing

### Integration Tests (tests/integration/test_resume_format_integration.py) - ✅ All Passing
- Mock responses updated to include Summary and Skills sections
- Test data extended to meet 100 character minimum
- Rate limit error handling fixed to return HTTP 503
- Validation error status code corrected (422 for Pydantic)
- All 8 integration tests passing

## Resolution Summary (2025-07-09)

1. **YAML Prompt Updates** (`src/prompts/resume_format/v1.0.0-en.yaml`):
   - Added explicit Summary section with `<h2>` heading
   - Added Skills section template
   - Ensures consistent HTML structure generation

2. **Service Improvements** (`src/services/resume_format.py`):
   - Added proper rate limit error handling
   - Fixed exception propagation for HTTP 503 responses

3. **Test Fixes**:
   - Updated mock responses to match expected format
   - Fixed test data length requirements
   - Corrected status code expectations

## Current Status

✅ All resume format tests are now passing
✅ No known test issues remaining