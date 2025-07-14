"""
Test helpers for bypassing security checks during testing.
"""

def get_test_headers():
    """
    Get headers that will pass security checks.
    Simulates requests from allowed origins.
    """
    return {
        "Origin": "http://localhost:3000",  # Allowed origin
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",  # Browser UA
        "Referer": "http://localhost:3000/test",
        "X-Test-Bypass-Security": "true"  # Bypass security for testing
    }


def get_bubble_headers():
    """
    Get headers that simulate Bubble.io requests.
    """
    return {
        "Origin": "https://airesumeadvisor.bubbleapps.io",
        "User-Agent": "Mozilla/5.0 (compatible; Bubble)",
        "Referer": "https://airesumeadvisor.bubbleapps.io/version-test"
    }