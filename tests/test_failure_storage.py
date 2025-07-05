"""
Tests for failure storage system.
"""
import pytest
import asyncio
from datetime import datetime, timezone

from src.core.monitoring.storage.failure_storage import FailureStorage


class TestFailureStorage:
    """Test failure storage functionality."""
    
    @pytest.mark.asyncio
    async def test_store_failure(self):
        """Test storing a failure case."""
        storage = FailureStorage(storage_path="/tmp/test_failures", max_storage_size=10)
        
        # Store a failure
        failure_id = await storage.store_failure(
            category="language_detection",
            job_description="これは日本語のジョブ説明です。" * 50,  # Long Japanese text
            failure_reason="Unsupported language: ja",
            language="ja",
            additional_info={"confidence": 0.95}
        )
        
        assert failure_id.startswith("language_detection_")
        assert len(storage.failures) == 1
        
        # Check truncation
        stored_failure = storage.failures[0]
        assert len(stored_failure["job_description"]) <= 500
        assert stored_failure["job_description_length"] > 500
    
    def test_get_recent_failures(self):
        """Test retrieving recent failures."""
        storage = FailureStorage(max_storage_size=10)
        
        # Add multiple failures
        asyncio.run(storage.store_failure(
            "keyword_extraction",
            "Short JD",
            "Too few keywords extracted"
        ))
        asyncio.run(storage.store_failure(
            "language_detection",
            "Mixed language content",
            "Multiple languages detected"
        ))
        
        # Get all recent failures
        recent = storage.get_recent_failures(limit=5)
        assert len(recent) == 2
        assert recent[0]["category"] == "language_detection"  # Most recent first
        
        # Get by category
        keyword_failures = storage.get_recent_failures(category="keyword_extraction", limit=5)
        assert len(keyword_failures) == 1
        assert keyword_failures[0]["failure_reason"] == "Too few keywords extracted"
    
    def test_failure_patterns(self):
        """Test pattern analysis."""
        storage = FailureStorage(max_storage_size=20)
        
        # Add failures with patterns
        for i in range(5):
            asyncio.run(storage.store_failure(
                "language_detection",
                f"Japanese text {i}",
                "Unsupported language: ja",
                language="ja"
            ))
        
        for i in range(3):
            asyncio.run(storage.store_failure(
                "keyword_extraction",
                f"Short text {i}",
                "Insufficient content",
                language="en"
            ))
        
        patterns = storage.get_failure_patterns()
        
        # Check category patterns
        assert "language_detection" in patterns["by_category"]
        assert patterns["by_category"]["language_detection"]["count"] == 5
        
        # Check language patterns
        assert "ja" in patterns["by_language"]
        assert patterns["by_language"]["ja"]["count"] == 5
    
    def test_export_analysis_report(self):
        """Test exporting analysis report."""
        storage = FailureStorage(max_storage_size=10)
        
        # Add some failures
        asyncio.run(storage.store_failure(
            "validation_error",
            "Invalid JD",
            "Job description too short",
            language="en"
        ))
        
        report = storage.export_analysis_report()
        
        assert "summary" in report
        assert "patterns" in report
        assert "recent_failures" in report
        assert "generated_at" in report
        
        assert report["summary"]["total_failures"] == 1
        assert report["summary"]["failures_by_category"]["validation_error"] == 1