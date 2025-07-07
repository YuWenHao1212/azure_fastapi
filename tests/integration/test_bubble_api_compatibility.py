#!/usr/bin/env python3
"""
Bubble.io API 格式相容性整合測試 (完整 8 測試案例)
測試 API 組裝和回應格式，不涉及真實 AI 功能

用法: python test_api_format_bubble_integration.py

功能:
- 驗證 Bubble.io 相容的統一回應格式 (TC001-TC008)
- 測試 API 端點整合和錯誤處理
- 使用 Mock 模擬，快速可靠執行
- 不呼叫真實 OpenAI API
- 包含標準化、並行、版本處理、一致性測試

測試案例:
- TC001: 標準工作描述提取
- TC002: 品質警告機制
- TC003: 長文本效能處理
- TC004: 錯誤處理驗證
- TC005: 關鍵字標準化功能
- TC006: 並行請求處理
- TC007: 提示版本處理
- TC008: 回應一致性驗證

Author: Claude Code
Date: 2025-07-04
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent  # Go up to project root
sys.path.insert(0, str(project_root))

# Import test dependencies
from fastapi.testclient import TestClient

from src.main import app


class BubbleApiFormatTests:
    """Bubble.io API 格式相容性測試 - 使用 Mock 驗證 API 組裝和回應格式"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_info(self, message):
        """Log info message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🔍 {message}")
        
    def log_success(self, message):
        """Log success message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✅ {message}")
        
    def log_error(self, message):
        """Log error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ {message}")
        
    def print_header(self):
        """Print test header."""
        print("=" * 60)
        print("🔧 Bubble.io API 格式相容性整合測試 (完整 8 測試案例)")
        print("📋 測試 API 組裝和統一回應格式 (使用 Mock)")
        print("📝 TC001-TC008: 涵蓋所有驗收測試案例")
        print("=" * 60)
        print(f"專案目錄: {project_root}")
        print(f"Python 版本: {sys.version}")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        self.total_tests += 1
        self.log_info(f"執行 {test_name}...")
        
        try:
            test_func()
            self.passed_tests += 1
            self.log_success(f"{test_name} 通過")
            self.results[test_name] = "PASSED"
        except Exception as e:
            self.log_error(f"{test_name} 失敗: {str(e)}")
            self.results[test_name] = f"FAILED: {str(e)}"
    
    def test_tc001_standard_job_description_extraction(self):
        """TC001: Standard job description extraction test."""
        tsmc_job_description = """We are seeking a Senior Python Developer to join our data analytics team at TSMC. The ideal candidate will have 5+ years of experience in Python development, strong knowledge of data structures and algorithms, and expertise in SQL and data visualization tools like Tableau. Experience with machine learning frameworks such as TensorFlow or PyTorch is highly desired. The role involves developing scalable data processing pipelines, implementing ML models, and creating insightful dashboards. Strong communication skills and the ability to work in a fast-paced environment are essential."""
        
        request_data = {
            "job_description": tsmc_job_description,
            "max_keywords": 20,
            "include_standardization": True,
            "use_multi_round_validation": True
        }
        
        mock_service_response = {
            "keywords": [
                "Senior Python Developer", "Data Analytics", "Python", "SQL",
                "Data Structures", "Algorithms", "Tableau", "Machine Learning",
                "TensorFlow", "PyTorch", "Data Processing", "ML Models",
                "Dashboards", "Communication Skills", "TSMC", "5+ Years Experience"
            ],
            "keyword_count": 16,
            "standardized_terms": [],
            "confidence_score": 0.95,
            "processing_time_ms": 1500,
            "extraction_method": "intersection_with_supplement",
            "intersection_stats": {
                "intersection_count": 16,
                "round1_count": 20,
                "round2_count": 21,
                "total_available": 25,
                "final_count": 16,
                "supplement_count": 0,
                "strategy_used": "intersection_with_supplement",
                "warning": False,
                "warning_message": ""
            },
            "detected_language": "en",
            "prompt_version_used": "1.3.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            mock_process.return_value = mock_service_response
            
            response = self.client.post(
                "/api/v1/extract-jd-keywords",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        
        # Verify response structure
        assert result["success"] is True
        assert "data" in result
        assert "error" in result
        assert "warning" in result
        assert "timestamp" in result
        
        # Verify data fields
        data = result["data"]
        assert "keywords" in data
        assert "keyword_count" in data
        assert 12 <= data["keyword_count"] <= 22
        assert data["confidence_score"] > 0.9
        assert result["warning"]["has_warning"] is False
    
    def test_tc002_quality_warning_mechanism(self):
        """TC002: Quality warning mechanism test."""
        poor_quality_job_description = "Looking for a developer with programming skills and some experience in software development."
        
        request_data = {
            "job_description": poor_quality_job_description,
            "max_keywords": 20,
            "include_standardization": True,
            "use_multi_round_validation": True
        }
        
        mock_service_response = {
            "keywords": ["Developer", "Programming Skills"],
            "keyword_count": 2,
            "standardized_terms": [],
            "confidence_score": 0.45,
            "processing_time_ms": 800,
            "extraction_method": "quality_insufficient",
            "intersection_stats": {
                "intersection_count": 2,
                "round1_count": 3,
                "round2_count": 2,
                "total_available": 3,
                "final_count": 2,
                "supplement_count": 0,
                "strategy_used": "quality_insufficient",
                "warning": True,
                "warning_message": "Insufficient quality for reliable extraction"
            },
            "detected_language": "en",
            "prompt_version_used": "1.3.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            mock_process.return_value = mock_service_response
            
            response = self.client.post(
                "/api/v1/extract-jd-keywords",
                json=request_data
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify warning is triggered
        assert result["warning"]["has_warning"] is True
        assert "insufficient" in result["warning"]["message"].lower()
        assert result["warning"]["suggestion"] != ""
        assert result["data"]["keyword_count"] < 12
        assert result["data"]["confidence_score"] < 0.7
    
    def test_tc003_long_job_description_performance(self):
        """TC003: Long job description performance test."""
        import time
        
        bcg_job_description = """Boston Consulting Group is seeking an exceptional Data Scientist to join our Advanced Analytics team. This role requires a unique blend of technical expertise, business acumen, and client engagement skills.

Key Responsibilities:
- Lead data science projects for Fortune 500 clients across industries
- Develop machine learning models using Python, R, and cloud platforms
- Build predictive models and optimization algorithms for business problems
- Create data visualization dashboards using Tableau, Power BI, and D3.js
- Implement deep learning solutions using TensorFlow and PyTorch
- Design and deploy scalable data pipelines on AWS and Azure
- Conduct statistical analysis and A/B testing for client recommendations
- Present findings to C-level executives and stakeholders
- Mentor junior data scientists and analysts
- Contribute to BCG's analytics intellectual property

Required Qualifications:
- Advanced degree in Computer Science, Statistics, or related field
- 5+ years of experience in data science and machine learning
- Expert proficiency in Python, SQL, and statistical programming
- Strong experience with big data technologies (Spark, Hadoop)
- Cloud platform expertise (AWS, Azure, GCP)
- Excellent communication and presentation skills
- Strategy consulting experience preferred
- Track record of delivering high-impact analytics solutions

Technical Skills:
- Programming Languages: Python, R, SQL, Scala
- ML Frameworks: TensorFlow, PyTorch, Scikit-learn, XGBoost
- Big Data: Apache Spark, Hadoop, Hive, Kafka
- Cloud Platforms: AWS (SageMaker, EMR), Azure ML, GCP
- Databases: PostgreSQL, MongoDB, Cassandra, Redshift
- Visualization: Tableau, Power BI, Matplotlib, Plotly
- DevOps: Docker, Kubernetes, Git, Jenkins
- Statistics: Hypothesis testing, Regression, Time series analysis"""
        
        request_data = {
            "job_description": bcg_job_description,
            "max_keywords": 20,
            "include_standardization": True,
            "use_multi_round_validation": True
        }
        
        mock_service_response = {
            "keywords": [
                "Data Scientist", "Boston Consulting Group", "Advanced Analytics",
                "Machine Learning", "Python", "R", "Cloud Platforms", "Fortune 500",
                "Predictive Models", "Optimization Algorithms", "Data Visualization",
                "Tableau", "Power BI", "Deep Learning", "TensorFlow", "PyTorch",
                "AWS", "Azure", "Statistical Analysis", "A/B Testing"
            ],
            "keyword_count": 20,
            "standardized_terms": [],
            "confidence_score": 0.92,
            "processing_time_ms": 2800,
            "extraction_method": "intersection_with_supplement",
            "intersection_stats": {
                "intersection_count": 18,
                "round1_count": 25,
                "round2_count": 24,
                "total_available": 30,
                "final_count": 20,
                "supplement_count": 2,
                "strategy_used": "intersection_with_supplement",
                "warning": False,
                "warning_message": ""
            },
            "detected_language": "en",
            "prompt_version_used": "1.3.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            mock_process.return_value = mock_service_response
            
            start_time = time.time()
            response = self.client.post(
                "/api/v1/extract-jd-keywords",
                json=request_data
            )
            end_time = time.time()
        
        # Verify response time < 10 seconds
        response_time = end_time - start_time
        assert response_time < 10.0, f"Response time {response_time}s exceeds 10s limit"
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert 12 <= result["data"]["keyword_count"] <= 22
    
    def test_tc004_error_handling_invalid_input(self):
        """TC004: Error handling for invalid input."""
        # Test 1: Empty job description
        response = self.client.post(
            "/api/v1/extract-jd-keywords",
            json={
                "job_description": "",
                "max_keywords": 20
            }
        )
        
        assert response.status_code == 422  # FastAPI returns 422 for Pydantic validation errors
        result = response.json()
        # Our app uses custom validation error handler with unified response format
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"
        # Check for more specific error message
        assert ("validation failed" in result["error"]["message"].lower() or 
                "too short" in result["error"]["message"].lower())
    
    def test_tc005_standardization_functionality(self):
        """TC005: Keyword standardization test."""
        request_data = {
            "job_description": "We need someone with ml experience, aws knowledge, and python programming skills. Experience with k8s and ci/cd pipelines required.",
            "max_keywords": 15,
            "include_standardization": True,
            "use_multi_round_validation": True
        }
        
        mock_service_response = {
            "keywords": ["Machine Learning", "AWS", "Python", "Kubernetes", "CI/CD"],
            "keyword_count": 5,
            "standardized_terms": [
                {"original": "ml", "standardized": "Machine Learning", "method": "dictionary_lookup"},
                {"original": "aws", "standardized": "AWS", "method": "dictionary_lookup"},
                {"original": "python programming", "standardized": "Python", "method": "dictionary_lookup"},
                {"original": "k8s", "standardized": "Kubernetes", "method": "dictionary_lookup"},
                {"original": "ci/cd pipelines", "standardized": "CI/CD", "method": "dictionary_lookup"}
            ],
            "confidence_score": 0.88,
            "processing_time_ms": 1200,
            "extraction_method": "intersection_with_supplement",
            "intersection_stats": {
                "intersection_count": 5,
                "round1_count": 6,
                "round2_count": 5,
                "total_available": 7,
                "final_count": 5,
                "supplement_count": 0,
                "strategy_used": "intersection_with_supplement",
                "warning": False,
                "warning_message": ""
            },
            "detected_language": "en",
            "prompt_version_used": "1.3.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            mock_process.return_value = mock_service_response
            
            response = self.client.post(
                "/api/v1/extract-jd-keywords",
                json=request_data
            )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify standardization occurred
        data = result["data"]
        assert len(data["standardized_terms"]) > 0
        
        # Check specific standardizations
        standardized_map = {item["original"]: item["standardized"] for item in data["standardized_terms"]}
        
        # These should be standardized based on the dictionary
        expected_standardizations = {
            "ml": "Machine Learning",
            "aws": "AWS",
            "python programming": "Python",
            "k8s": "Kubernetes",
            "ci/cd pipelines": "CI/CD"
        }
        
        for original, expected in expected_standardizations.items():
            if original in standardized_map:
                assert standardized_map[original] == expected, f"Expected {original} -> {expected}"
    
    def test_tc006_concurrent_requests(self):
        """TC006: Concurrent request handling test."""
        tsmc_job_description = """We are seeking a Senior Python Developer to join our data analytics team at TSMC. The ideal candidate will have 5+ years of experience in Python development, strong knowledge of data structures and algorithms, and expertise in SQL and data visualization tools like Tableau. Experience with machine learning frameworks such as TensorFlow or PyTorch is highly desired. The role involves developing scalable data processing pipelines, implementing ML models, and creating insightful dashboards. Strong communication skills and the ability to work in a fast-paced environment are essential."""
        
        request_data = {
            "job_description": tsmc_job_description,
            "max_keywords": 20,
            "include_standardization": True,
            "use_multi_round_validation": True
        }
        
        mock_service_response = {
            "keywords": ["Python", "Data Analytics", "Machine Learning", "SQL", "Tableau", "TSMC", "Senior", "Developer", "Django", "PostgreSQL", "Data Processing", "ML Models", "Dashboards", "Communication Skills", "Backend", "API"],
            "keyword_count": 16,
            "standardized_terms": [],
            "confidence_score": 0.95,
            "processing_time_ms": 1500,
            "extraction_method": "intersection_with_supplement",
            "intersection_stats": {
                "intersection_count": 16,
                "round1_count": 20,
                "round2_count": 21,
                "total_available": 25,
                "final_count": 16,
                "supplement_count": 0,
                "strategy_used": "intersection_with_supplement",
                "warning": False,
                "warning_message": ""
            },
            "detected_language": "en",
            "prompt_version_used": "1.3.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            mock_process.return_value = mock_service_response
            
            # Create 5 sequential requests to simulate concurrent behavior
            results = []
            for i in range(5):
                response = self.client.post("/api/v1/extract-jd-keywords", json=request_data)
                results.append((response.json(), response.status_code))
            
            # Verify all requests succeeded
            for result, status_code in results:
                assert status_code == 200
                assert result["success"] is True
                assert result["data"]["keyword_count"] > 0
    
    def test_tc007_prompt_version_handling(self):
        """TC007: Prompt version handling test."""
        tsmc_job_description = """We are seeking a Senior Python Developer to join our data analytics team at TSMC. The ideal candidate will have 5+ years of experience in Python development, strong knowledge of data structures and algorithms, and expertise in SQL and data visualization tools like Tableau. Experience with machine learning frameworks such as TensorFlow or PyTorch is highly desired. The role involves developing scalable data processing pipelines, implementing ML models, and creating insightful dashboards. Strong communication skills and the ability to work in a fast-paced environment are essential."""
        
        # Test with v1.2.0
        request_v2 = {
            "job_description": tsmc_job_description,
            "max_keywords": 20,
            "include_standardization": True,
            "use_multi_round_validation": True,
            "prompt_version": "v1.2.0"
        }
        
        # Test with latest
        request_latest = {
            "job_description": tsmc_job_description,
            "max_keywords": 20,
            "include_standardization": True,
            "use_multi_round_validation": True,
            "prompt_version": "latest"
        }
        
        mock_v2_service_response = {
            "keywords": ["Python", "Data Analytics", "SQL", "Machine Learning", "TensorFlow"] * 4,  # v1.2.0 extracts 20
            "keyword_count": 20,
            "standardized_terms": [],
            "confidence_score": 0.92,
            "processing_time_ms": 1600,
            "extraction_method": "intersection_with_supplement",
            "intersection_stats": {
                "intersection_count": 20,
                "strategy_used": "intersection_with_supplement",
                "warning": False
            },
            "detected_language": "en",
            "prompt_version_used": "v1.2.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            # Test v1.2.0
            mock_process.return_value = mock_v2_service_response
            response_v2 = self.client.post("/api/v1/extract-jd-keywords", json=request_v2)
            
            # Test latest (should use v1.2.0)
            mock_process.return_value = mock_v2_service_response
            response_latest = self.client.post("/api/v1/extract-jd-keywords", json=request_latest)
        
        # Verify all versions work
        assert response_v2.status_code == 200
        assert response_latest.status_code == 200
        
        # Verify version-specific behavior
        result_v2 = response_v2.json()
        result_latest = response_latest.json()
        
        # Latest should behave like v1.2.0
        assert result_latest["data"]["extraction_method"] == result_v2["data"]["extraction_method"]
    
    def test_tc008_response_consistency(self):
        """TC008: Response consistency test."""
        tsmc_job_description = """We are seeking a Senior Python Developer to join our data analytics team at TSMC. The ideal candidate will have 5+ years of experience in Python development, strong knowledge of data structures and algorithms, and expertise in SQL and data visualization tools like Tableau. Experience with machine learning frameworks such as TensorFlow or PyTorch is highly desired. The role involves developing scalable data processing pipelines, implementing ML models, and creating insightful dashboards. Strong communication skills and the ability to work in a fast-paced environment are essential."""
        
        request_data = {
            "job_description": tsmc_job_description,
            "max_keywords": 16,  # Using the new limit
            "include_standardization": True,
            "use_multi_round_validation": True
        }
        
        # Fixed mock service response for consistency
        mock_service_response = {
            "keywords": [
                "Senior Python Developer", "Data Analytics", "Python", "SQL",
                "Data Structures", "Algorithms", "Tableau", "Machine Learning",
                "TensorFlow", "PyTorch", "Data Processing", "ML Models",
                "Dashboards", "Communication Skills", "TSMC", "5+ Years Experience"
            ],
            "keyword_count": 16,
            "standardized_terms": [],
            "confidence_score": 0.95,
            "processing_time_ms": 1500,
            "extraction_method": "intersection_with_supplement",
            "intersection_stats": {
                "intersection_count": 16,
                "round1_count": 20,
                "round2_count": 21,
                "total_available": 25,
                "final_count": 16,
                "supplement_count": 0,
                "strategy_used": "intersection_with_supplement",
                "warning": False,
                "warning_message": ""
            },
            "detected_language": "en",
            "prompt_version_used": "1.3.0"
        }
        
        with patch('src.services.keyword_extraction_v2.KeywordExtractionServiceV2.process') as mock_process:
            mock_process.return_value = mock_service_response
            
            # Make 5 identical requests
            responses = []
            for _ in range(5):
                response = self.client.post("/api/v1/extract-jd-keywords", json=request_data)
                responses.append(response.json())
        
        # Verify all responses are successful
        for response in responses:
            assert response["success"] is True
            assert response["data"]["keyword_count"] == 16  # Fixed at 16
        
        # Compare keyword sets (order might vary)
        keyword_sets = [set(r["data"]["keywords"]) for r in responses]
        first_set = keyword_sets[0]
        
        # At least 80% of responses should be identical
        identical_count = sum(1 for s in keyword_sets if s == first_set)
        consistency_rate = identical_count / len(keyword_sets)
        assert consistency_rate >= 0.8, f"Consistency rate {consistency_rate} is below 80%"
    
    def run_all_tests(self):
        """Run all acceptance tests."""
        self.print_header()
        
        # Run individual tests
        test_methods = [
            ("格式測試001 - 標準成功回應格式", self.test_tc001_standard_job_description_extraction),
            ("格式測試002 - 警告欄位格式", self.test_tc002_quality_warning_mechanism),
            ("格式測試003 - 長文本回應格式", self.test_tc003_long_job_description_performance),
            ("格式測試004 - 錯誤回應格式", self.test_tc004_error_handling_invalid_input),
            ("格式測試005 - 標準化功能格式", self.test_tc005_standardization_functionality),
            ("格式測試006 - 並行請求格式", self.test_tc006_concurrent_requests),
            ("格式測試007 - 提示版本處理格式", self.test_tc007_prompt_version_handling),
            ("格式測試008 - 回應一致性格式", self.test_tc008_response_consistency),
        ]
        
        for test_name, test_func in test_methods:
            self.run_test(test_name, test_func)
            print("-" * 40)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("=" * 60)
        print("📊 測試結果總結")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result == "PASSED" else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result != "PASSED":
                print(f"   詳情: {result}")
        
        success_rate = (self.passed_tests / self.total_tests) * 100
        print("-" * 60)
        print(f"總測試數: {self.total_tests}")
        print(f"通過測試: {self.passed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 測試整體通過！")
        else:
            print("⚠️  部分測試失敗，請檢查問題")
        
        print("=" * 60)

def main():
    """Main entry point."""
    print("🚀 啟動 Bubble.io API 格式相容性測試...")
    print("📋 這是整合測試，使用 Mock 模擬，不呼叫真實 AI")
    print("")
    
    # Set up environment
    os.environ['PYTHONPATH'] = str(project_root) + ":" + os.environ.get('PYTHONPATH', '')
    
    # Run tests
    test_suite = BubbleApiFormatTests()
    test_suite.run_all_tests()
    
    return test_suite.passed_tests == test_suite.total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)