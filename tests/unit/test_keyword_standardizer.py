"""
Unit tests for Keyword Standardizer.
Tests keyword standardization logic including SQL, title case, and position-specific standardizations.
"""

import pytest

from src.services.keyword_standardizer import KeywordStandardizer


class TestKeywordStandardizer:
    """Test keyword standardization functionality."""
    
    @pytest.fixture
    def standardizer(self):
        """Create standardizer instance."""
        return KeywordStandardizer()
    
    def test_sql_standardization(self, standardizer):
        """Test SQL-related keyword standardization."""
        test_cases = [
            # Direct SQL variations
            ("SQL", "SQL"),
            ("sql", "SQL"),
            ("Sql", "SQL"),
            
            # Expanded forms
            ("structured query language", "SQL"),
            ("Structured Query Language", "SQL"),
            ("STRUCTURED QUERY LANGUAGE", "SQL"),
            
            # SQL with context
            ("sql queries", "SQL"),
            ("sql programming", "SQL"),
            ("sql server", "SQL Server"),
            ("mysql", "MySQL"),
            ("postgresql", "PostgreSQL"),
            ("nosql", "NoSQL"),
            
            # Other database terms
            ("database", "database"),
            ("database administration", "Database Administration"),
            ("dba", "Database Administration"),
        ]
        
        for input_keyword, expected in test_cases:
            result = standardizer.standardize(input_keyword)
            assert result == expected, f"Failed: {input_keyword} -> {result} (expected {expected})"
    
    def test_title_case_standardization(self, standardizer):
        """Test title case standardization for multi-word terms."""
        test_cases = [
            # Programming concepts
            ("machine learning", "Machine Learning"),
            ("artificial intelligence", "Artificial Intelligence"),
            ("deep learning", "Deep Learning"),
            ("natural language processing", "Natural Language Processing"),
            
            # Job titles and roles
            ("project manager", "Project Manager"),
            ("product manager", "Product Manager"),
            ("data scientist", "Data Scientist"),
            ("software engineer", "Software Engineer"),
            ("lead data scientist", "Lead Data Scientist"),
            
            # Technical terms
            ("version control", "Version Control"),
            ("continuous integration", "Continuous Integration"),
            ("test driven development", "Test Driven Development"),
            ("object oriented programming", "Object-Oriented Programming"),
            
            # Frameworks and tools
            ("spring boot", "Spring Boot"),
            ("react native", "React Native"),
            
            # Special cases
            ("ci/cd", "CI/CD"),
            ("ui/ux", "UI/UX"),
            ("restful api", "RESTful API"),
        ]
        
        for input_keyword, expected in test_cases:
            result = standardizer.standardize(input_keyword)
            assert result == expected, f"Failed: {input_keyword} -> {result} (expected {expected})"
    
    def test_position_specific_standardization(self, standardizer):
        """Test standardization for specific job positions."""
        # Lead Data Scientist variations
        lead_ds_cases = [
            ("lead data scientist", "Lead Data Scientist"),
            ("Lead Data Scientist", "Lead Data Scientist"),
            ("LEAD DATA SCIENTIST", "Lead Data Scientist"),
            ("lead ds", "Lead Data Scientist"),
            ("sr. lead data scientist", "Lead Data Scientist"),
            ("senior lead data scientist", "Lead Data Scientist"),
        ]
        
        for input_keyword, expected in lead_ds_cases:
            result = standardizer.standardize(input_keyword)
            assert result == expected, f"Failed: {input_keyword} -> {result} (expected {expected})"
    
    def test_technology_standardization(self, standardizer):
        """Test standardization of technology names."""
        test_cases = [
            # Programming languages
            ("python", "Python"),
            ("PYTHON", "Python"),
            ("java", "Java"),
            ("javascript", "JavaScript"),
            ("c++", "C++"),
            ("c#", "C#"),
            ("golang", "Go"),
            ("go", "Go"),
            
            # Frameworks
            ("django", "Django"),
            ("flask", "Flask"),
            ("fastapi", "FastAPI"),
            ("nodejs", "Node.js"),
            ("node.js", "Node.js"),
            ("react", "React"),
            ("angular", "Angular"),
            ("vue", "Vue.js"),
            ("vuejs", "Vue.js"),
            
            # Cloud platforms
            ("aws", "AWS"),
            ("amazon web services", "AWS"),
            ("azure", "Azure"),
            ("microsoft azure", "Azure"),
            ("gcp", "Google Cloud Platform"),
            ("google cloud", "Google Cloud Platform"),
            
            # DevOps tools
            ("docker", "Docker"),
            ("kubernetes", "Kubernetes"),
            ("k8s", "Kubernetes"),
            ("jenkins", "Jenkins"),
            ("gitlab", "GitLab"),
            ("github", "GitHub"),
            
            # Data tools
            ("spark", "Apache Spark"),
            ("apache spark", "Apache Spark"),
            ("hadoop", "Hadoop"),
            ("kafka", "Apache Kafka"),
            ("apache kafka", "Apache Kafka"),
        ]
        
        for input_keyword, expected in test_cases:
            result = standardizer.standardize(input_keyword)
            assert result == expected, f"Failed: {input_keyword} -> {result} (expected {expected})"
    
    def test_acronym_standardization(self, standardizer):
        """Test standardization of common acronyms."""
        test_cases = [
            ("api", "API"),
            ("rest", "REST"),
            ("soap", "SOAP"),
            ("http", "HTTP"),
            ("https", "HTTPS"),
            ("css", "CSS"),
            ("html", "HTML"),
            ("xml", "XML"),
            ("json", "JSON"),
            ("yaml", "YAML"),
            ("sdk", "SDK"),
            ("ide", "IDE"),
            ("orm", "ORM"),
            ("mvc", "MVC"),
            ("mvp", "MVP"),
            ("poc", "POC"),
            ("kpi", "KPI"),
            ("roi", "ROI"),
            ("sla", "SLA"),
            ("etl", "ETL"),
            ("elt", "ELT"),
        ]
        
        for input_keyword, expected in test_cases:
            result = standardizer.standardize(input_keyword)
            assert result == expected, f"Failed: {input_keyword} -> {result} (expected {expected})"
    
    def test_batch_standardization(self, standardizer):
        """Test batch standardization of multiple keywords."""
        keywords = [
            "python",
            "machine learning",
            "sql",
            "lead data scientist",
            "aws",
            "ci/cd",
            "api",
            "docker"
        ]
        
        expected = [
            "Python",
            "Machine Learning",
            "SQL",
            "Lead Data Scientist",
            "AWS",
            "CI/CD",
            "API",
            "Docker"
        ]
        
        results = [standardizer.standardize(kw) for kw in keywords]
        assert results == expected
    
    def test_edge_cases(self, standardizer):
        """Test edge cases and special scenarios."""
        test_cases = [
            # Empty and whitespace
            ("", ""),
            ("   ", ""),
            ("  python  ", "Python"),
            
            # Mixed case with special characters
            ("node.JS", "Node.js"),
            ("c/C++", "C++"),
            
            # Already correct
            ("Machine Learning", "Machine Learning"),
            ("SQL", "SQL"),
            ("Lead Data Scientist", "Lead Data Scientist"),
            
            # Numbers in keywords
            ("python3", "Python"),
            ("python 3", "Python"),
            ("es6", "ES6"),
            
            # Hyphenated terms
            ("front-end", "Front-End"),
            ("back-end", "Back-End"),
            ("full-stack", "Full-Stack"),
            ("object-oriented", "Object-Oriented"),
        ]
        
        for input_keyword, expected in test_cases:
            result = standardizer.standardize(input_keyword)
            assert result == expected, f"Failed: {input_keyword} -> {result} (expected {expected})"
    
    def test_preserve_unknown_keywords(self, standardizer):
        """Test that unknown keywords are preserved with basic formatting."""
        unknown_keywords = [
            "quantum computing",
            "blockchain technology",
            "edge computing",
            "5g networks"
        ]
        
        for keyword in unknown_keywords:
            result = standardizer.standardize(keyword)
            # Should apply title case but not change the term
            expected = keyword.title()
            assert result == expected or result == keyword


if __name__ == "__main__":
    pytest.main([__file__, "-v"])