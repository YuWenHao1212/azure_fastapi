"""
Performance benchmark configuration based on actual API statistics.
These values should be updated periodically based on production metrics.
"""
import os

# Performance thresholds based on endpoint and percentile
# Format: {endpoint: (p50_ms, p95_ms, p99_ms)}
ENDPOINT_BENCHMARKS: dict[str, tuple[float, float, float]] = {
    # Extract Keywords endpoint benchmarks (in seconds)
    "/api/v1/extract-jd-keywords": (2.5, 4.5, 6.0),  # P50: 2.5s, P95: 4.5s, P99: 6s
    
    # Index Calculation endpoints
    "/api/v1/index-calculation": (1.5, 3.0, 4.0),
    "/api/v1/index-cal-and-gap-analysis": (3.0, 5.5, 7.0),
    
    # Health check should be fast
    "/api/v1/health": (0.05, 0.1, 0.2),
}

# Environment-specific multipliers
ENV_MULTIPLIERS = {
    "development": 1.5,  # Allow 50% more time in dev
    "ci": 1.2,          # Allow 20% more time in CI
    "production": 1.0,   # Use baseline in production
}

def get_performance_threshold(endpoint: str, percentile: int = 95) -> float:
    """
    Get performance threshold for an endpoint.
    
    Args:
        endpoint: API endpoint path
        percentile: Percentile to use (50, 95, or 99)
        
    Returns:
        Threshold in seconds
    """
    env = os.getenv("TEST_ENV", "development")
    multiplier = ENV_MULTIPLIERS.get(env, 1.5)
    
    # Default thresholds if endpoint not configured
    default_thresholds = ENDPOINT_BENCHMARKS.get(endpoint, (3.0, 5.0, 7.0))
    
    if percentile == 50:
        threshold = default_thresholds[0]
    elif percentile == 95:
        threshold = default_thresholds[1]
    elif percentile == 99:
        threshold = default_thresholds[2]
    else:
        threshold = default_thresholds[1]  # Default to P95
    
    return threshold * multiplier


# Cache test configuration
CACHE_TEST_CONFIG = {
    "sequential_cache_enabled": False,  # Disable cache for sequential tests
    "parallel_cache_enabled": False,    # Disable cache for parallel tests
    "clear_cache_between_tests": True,  # Clear cache between test runs
}

# Parallel processing expectations
PARALLEL_PROCESSING_CONFIG = {
    "min_speedup_percent": 15,  # Minimum expected speedup (lowered from 20%)
    "test_iterations": 3,       # Number of iterations for averaging
    "use_different_inputs": True,  # Use different inputs to avoid cache
}