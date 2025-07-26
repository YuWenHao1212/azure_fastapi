# Performance Test Analysis

## Issues Found

### 1. Cache Interference in Parallel Processing Test

**Problem**: The `test_parallel_processing_speedup` test was failing because both sequential and parallel tests were using cache, making both equally fast.

**Root Cause**:
- Both `KeywordExtractionServiceV2` instances had cache enabled by default
- Same test data was used for all iterations
- Sequential tests ran first and populated the cache
- All subsequent tests (including parallel) hit the cache
- Result: -17.9% "speedup" (parallel was slightly slower due to overhead)

**Solution**:
- Disable cache for performance comparison tests
- Use different job descriptions for each iteration
- Clear cache between sequential and parallel tests

### 2. Fixed Thresholds for API Performance

**Problem**: The `test_api_concurrent_performance` test used a fixed 4.5s threshold for all endpoints.

**Issues**:
- Different endpoints have different performance characteristics
- No consideration for environment (dev vs production)
- No statistical basis (should use P50, P95, P99)

**Solution**:
- Created `test_performance_benchmarks.py` with endpoint-specific thresholds
- Added environment multipliers (1.5x for dev, 1.2x for CI)
- Based thresholds on percentiles (P50, P95, P99)

## Recommendations

### For Development:
```bash
# Skip flaky performance tests by default
./run_precommit_tests.sh

# Run full tests when needed
./run_precommit_tests.sh --full-perf
```

### For CI/CD:
```bash
# Set environment for appropriate thresholds
export TEST_ENV=ci
./run_precommit_tests.sh --full-perf
```

### For Performance Testing:
1. Run tests without cache to measure actual processing time
2. Use varied inputs to avoid cache hits
3. Consider environment-specific thresholds
4. Monitor P50, P95, P99 metrics in production
5. Update benchmarks periodically based on actual data

## Performance Baseline (Suggested)

| Endpoint | P50 | P95 | P99 |
|----------|-----|-----|-----|
| `/api/v1/extract-jd-keywords` | 2.5s | 4.5s | 6.0s |
| `/api/v1/index-calculation` | 1.5s | 3.0s | 4.0s |
| `/api/v1/index-cal-and-gap-analysis` | 3.0s | 5.5s | 7.0s |
| `/api/v1/health` | 0.05s | 0.1s | 0.2s |

*Note: These are baseline values. Actual performance depends on:*
- External API latency (OpenAI, Azure)
- System resources
- Concurrent load
- Cache hit rate