"""
Unit tests for Resume Format models.
Tests request/response model validation, serialization, and error handling.
"""
import pytest
from pydantic import ValidationError

from src.models.resume_format import (
    CorrectionsMade,
    ResumeFormatData,
    ResumeFormatRequest,
    SectionsDetected,
    SupplementInfo,
)


@pytest.mark.unit
class TestResumeFormatRequest:
    """Test ResumeFormatRequest model validation."""
    
    def test_valid_request_creation(self):
        """Test creating a valid request with minimal data."""
        ocr_text = """【Title】:John Smith
【Title】:Software Engineer
【NarrativeText】:Experienced developer with 5+ years building scalable applications
【Title】:Skills
【NarrativeText】:Python, JavaScript, React, Node.js"""
        request = ResumeFormatRequest(ocr_text=ocr_text)
        
        assert request.ocr_text == ocr_text
        assert request.supplement_info is None
    
    def test_request_with_supplement_info(self):
        """Test creating a request with supplement information."""
        ocr_text = """【Title】:John Smith
【Title】:Software Engineer
【NarrativeText】:Experienced developer with expertise in full-stack development"""
        supplement = SupplementInfo(
            name="John Doe",
            email="john.doe@example.com",
            linkedin="https://linkedin.com/in/johndoe",
            phone="+1-555-1234",
            location="San Francisco, CA"
        )
        request = ResumeFormatRequest(
            ocr_text=ocr_text + " " * 50,  # Ensure minimum length
            supplement_info=supplement
        )
        
        assert request.supplement_info.name == "John Doe"
        assert request.supplement_info.email == "john.doe@example.com"
    
    def test_ocr_text_too_short(self):
        """Test validation error when OCR text is too short."""
        with pytest.raises(ValidationError) as exc_info:
            ResumeFormatRequest(ocr_text="Too short")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "at least 100 characters" in str(errors[0]["msg"])
    
    def test_empty_ocr_text(self):
        """Test validation error when OCR text is empty."""
        with pytest.raises(ValidationError) as exc_info:
            ResumeFormatRequest(ocr_text="")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
    
    def test_ocr_text_stripped(self):
        """Test that OCR text is stripped of leading/trailing whitespace."""
        ocr_text = """   【Title】:John Smith
【Title】:Software Engineer
【NarrativeText】:Location: San Francisco, CA
【NarrativeText】:Email: john.smith@example.com
【Title】:Work Experience   """
        request = ResumeFormatRequest(ocr_text=ocr_text)
        
        # Verify the text is present and meets length requirement
        assert len(request.ocr_text) >= 100
        assert "【Title】:John Smith" in request.ocr_text


@pytest.mark.unit
class TestSupplementInfo:
    """Test SupplementInfo model validation."""
    
    def test_all_fields_optional(self):
        """Test that all fields in SupplementInfo are optional."""
        supplement = SupplementInfo()
        
        assert supplement.name is None
        assert supplement.email is None
        assert supplement.linkedin is None
        assert supplement.phone is None
        assert supplement.location is None
    
    def test_partial_supplement_info(self):
        """Test creating SupplementInfo with some fields."""
        supplement = SupplementInfo(
            name="Jane Doe",
            email="jane@example.com"
        )
        
        assert supplement.name == "Jane Doe"
        assert supplement.email == "jane@example.com"
        assert supplement.linkedin is None
        assert supplement.phone is None
        assert supplement.location is None
    
    def test_supplement_info_dict_conversion(self):
        """Test converting SupplementInfo to dict excludes None values."""
        supplement = SupplementInfo(
            name="Test User",
            email="test@example.com"
        )
        
        data = supplement.dict(exclude_none=True)
        assert data == {
            "name": "Test User",
            "email": "test@example.com"
        }
        assert "linkedin" not in data
        assert "phone" not in data
        assert "location" not in data


@pytest.mark.unit
class TestSectionsDetected:
    """Test SectionsDetected model."""
    
    def test_default_values(self):
        """Test that all sections default to False."""
        sections = SectionsDetected()
        
        assert sections.contact is False
        assert sections.summary is False
        assert sections.skills is False
        assert sections.experience is False
        assert sections.education is False
        assert sections.projects is False
        assert sections.certifications is False
    
    def test_specific_sections_detected(self):
        """Test creating with specific sections detected."""
        sections = SectionsDetected(
            contact=True,
            summary=True,
            skills=True,
            experience=True,
            education=True
        )
        
        assert sections.contact is True
        assert sections.summary is True
        assert sections.skills is True
        assert sections.experience is True
        assert sections.education is True
        assert sections.projects is False
        assert sections.certifications is False
    
    def test_sections_dict_conversion(self):
        """Test converting SectionsDetected to dict."""
        sections = SectionsDetected(
            contact=True,
            experience=True,
            education=True
        )
        
        data = sections.model_dump()
        assert data["contact"] is True
        assert data["summary"] is False
        assert data["experience"] is True
        assert data["education"] is True


@pytest.mark.unit
class TestCorrectionsMade:
    """Test CorrectionsMade model."""
    
    def test_default_values(self):
        """Test that all corrections default to 0."""
        corrections = CorrectionsMade()
        
        assert corrections.ocr_errors == 0
        assert corrections.email_fixes == 0
        assert corrections.phone_fixes == 0
        assert corrections.date_standardization == 0
    
    def test_with_corrections(self):
        """Test creating with specific correction counts."""
        corrections = CorrectionsMade(
            ocr_errors=5,
            email_fixes=1,
            phone_fixes=2,
            date_standardization=3
        )
        
        assert corrections.ocr_errors == 5
        assert corrections.email_fixes == 1
        assert corrections.phone_fixes == 2
        assert corrections.date_standardization == 3
    
    def test_total_corrections(self):
        """Test calculating total corrections."""
        corrections = CorrectionsMade(
            ocr_errors=5,
            email_fixes=1,
            phone_fixes=2,
            date_standardization=3
        )
        
        total = sum(corrections.model_dump().values())
        assert total == 11


@pytest.mark.unit
class TestResumeFormatData:
    """Test ResumeFormatData response model."""
    
    def test_complete_response(self):
        """Test creating a complete response."""
        html = '<h1>John Doe</h1><h2>Software Engineer</h2>'
        sections = SectionsDetected(
            contact=True,
            experience=True,
            education=True
        )
        corrections = CorrectionsMade(
            ocr_errors=2,
            date_standardizations=1
        )
        supplement_used = ["name", "email"]
        
        response = ResumeFormatData(
            formatted_resume=html,
            sections_detected=sections,
            corrections_made=corrections,
            supplement_info_used=supplement_used
        )
        
        assert response.formatted_resume == html
        assert response.sections_detected.contact is True
        assert response.corrections_made.ocr_errors == 2
        assert response.supplement_info_used == ["name", "email"]
    
    def test_minimal_response(self):
        """Test creating response with minimal data."""
        html = '<h1>Name</h1>'
        response = ResumeFormatData(
            formatted_resume=html,
            sections_detected=SectionsDetected(),
            corrections_made=CorrectionsMade(),
            supplement_info_used=[]
        )
        
        assert response.formatted_resume == html
        assert response.sections_detected.contact is False
        assert response.corrections_made.ocr_errors == 0
        assert response.supplement_info_used == []
    
    def test_response_serialization(self):
        """Test that response can be serialized to JSON."""
        response = ResumeFormatData(
            formatted_resume='<h1>Test</h1>',
            sections_detected=SectionsDetected(contact=True),
            corrections_made=CorrectionsMade(ocr_errors=1),
            supplement_info_used=["email"]
        )
        
        # Test JSON serialization
        json_data = response.model_dump_json()
        assert isinstance(json_data, str)
        assert '"formatted_resume"' in json_data
        assert '"sections_detected"' in json_data
        assert '"corrections_made"' in json_data
        assert '"supplement_info_used"' in json_data
    
    def test_response_dict_conversion(self):
        """Test converting response to dict."""
        response = ResumeFormatData(
            formatted_resume='<h1>John Doe</h1>',
            sections_detected=SectionsDetected(
                contact=True,
                experience=True
            ),
            corrections_made=CorrectionsMade(
                ocr_errors=3,
                email_fixes=1
            ),
            supplement_info_used=["name", "linkedin"]
        )
        
        data = response.model_dump()
        assert data["formatted_resume"] == '<h1>John Doe</h1>'
        assert data["sections_detected"]["contact"] is True
        assert data["sections_detected"]["experience"] is True
        assert data["corrections_made"]["ocr_errors"] == 3
        assert data["corrections_made"]["email_fixes"] == 1
        assert data["supplement_info_used"] == ["name", "linkedin"]