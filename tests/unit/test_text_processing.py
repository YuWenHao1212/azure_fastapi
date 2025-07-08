"""
Unit tests for text processing utilities.
Tests HTML cleaning, sanitization, and text manipulation functions.
"""

from src.services.text_processing import (
    basic_security_cleanup,
    clean_html_text,
    clean_llm_output,
    convert_markdown_to_html,
    normalize_keywords,
    remove_dangerous_content,
    sanitize_html_content,
    validate_html_for_tinymce,
)


class TestCleanHtmlText:
    """Test clean_html_text function."""
    
    def test_removes_html_tags(self):
        """Test HTML tag removal."""
        html = "<p>Hello <strong>World</strong></p>"
        assert clean_html_text(html) == "Hello World"
    
    def test_decodes_html_entities(self):
        """Test HTML entity decoding."""
        html = "AT&amp;T &lt;test&gt;"
        assert clean_html_text(html) == "AT&T <test>"
    
    def test_normalizes_whitespace(self):
        """Test whitespace normalization."""
        html = "Hello   \n\t  World"
        assert clean_html_text(html) == "Hello World"
    
    def test_handles_empty_input(self):
        """Test empty input handling."""
        assert clean_html_text("") == ""
        assert clean_html_text(None) == ""
    
    def test_complex_html(self):
        """Test complex HTML cleaning."""
        html = """
        <div class="resume">
            <h1>John Doe</h1>
            <p>Software Engineer with <em>5 years</em> experience</p>
            <ul>
                <li>Python</li>
                <li>JavaScript</li>
            </ul>
        </div>
        """
        expected = "John Doe Software Engineer with 5 years experience Python JavaScript"
        assert clean_html_text(html) == expected


class TestRemoveDangerousContent:
    """Test remove_dangerous_content function."""
    
    def test_removes_script_tags(self):
        """Test script tag removal."""
        html = '<p>Hello</p><script>alert("XSS")</script><p>World</p>'
        assert remove_dangerous_content(html) == '<p>Hello</p><p>World</p>'
    
    def test_removes_style_tags(self):
        """Test style tag removal."""
        html = '<p>Hello</p><style>body{display:none}</style><p>World</p>'
        assert remove_dangerous_content(html) == '<p>Hello</p><p>World</p>'
    
    def test_removes_iframe_tags(self):
        """Test iframe tag removal."""
        html = '<p>Content</p><iframe src="evil.com"></iframe>'
        assert remove_dangerous_content(html) == '<p>Content</p>'
    
    def test_removes_comments(self):
        """Test comment removal."""
        html = '<p>Hello</p><!-- malicious comment --><p>World</p>'
        assert remove_dangerous_content(html) == '<p>Hello</p><p>World</p>'
    
    def test_handles_empty_input(self):
        """Test empty input handling."""
        assert remove_dangerous_content("") == ""
        assert remove_dangerous_content(None) == ""


class TestBasicSecurityCleanup:
    """Test basic_security_cleanup function."""
    
    def test_removes_javascript_protocol(self):
        """Test javascript protocol removal."""
        html = '<a href="javascript:alert(1)">Click</a>'
        assert 'javascript:' not in basic_security_cleanup(html)
        assert '#' in basic_security_cleanup(html)
    
    def test_removes_event_handlers(self):
        """Test event handler removal."""
        html = '<div onclick="alert(1)" onload="hack()">Content</div>'
        result = basic_security_cleanup(html)
        assert 'onclick' not in result
        assert 'onload' not in result
    
    def test_removes_css_expressions(self):
        """Test CSS expression removal."""
        html = '<div style="width:expression(alert(1))">Content</div>'
        assert 'expression' not in basic_security_cleanup(html)
    
    def test_removes_illegal_characters(self):
        """Test illegal character removal."""
        html = "Hello\x00World\x0B"
        assert basic_security_cleanup(html) == "HelloWorld"
    
    def test_preserves_safe_content(self):
        """Test that safe content is preserved."""
        html = '<p class="safe">Normal content with <a href="/page">link</a></p>'
        result = basic_security_cleanup(html)
        assert 'class="safe"' in result
        assert 'href="/page"' in result


class TestCleanLlmOutput:
    """Test clean_llm_output function."""
    
    def test_removes_markdown_code_blocks(self):
        """Test markdown code block removal."""
        text = "```python\ncode here\n```"
        assert clean_llm_output(text) == "code here"
    
    def test_removes_extra_blank_lines(self):
        """Test extra blank line removal."""
        text = "Line 1\n\n\n\nLine 2"
        assert clean_llm_output(text) == "Line 1\n\nLine 2"
    
    def test_handles_encoding_issues(self):
        """Test encoding issue handling."""
        text = "Hello 😀 World"
        result = clean_llm_output(text)
        assert "Hello" in result
        assert "World" in result
    
    def test_handles_empty_input(self):
        """Test empty input handling."""
        assert clean_llm_output("") == ""
        assert clean_llm_output(None) == ""


class TestValidateHtmlForTinymce:
    """Test validate_html_for_tinymce function."""
    
    def test_validates_normal_html(self):
        """Test normal HTML validation."""
        html = "<p>Hello <strong>World</strong></p>"
        result = validate_html_for_tinymce(html)
        assert "<p>" in result
        assert "<strong>" in result
    
    def test_removes_dangerous_content(self):
        """Test dangerous content removal during validation."""
        html = '<p>Safe</p><script>alert(1)</script>'
        result = validate_html_for_tinymce(html)
        assert '<p>' in result
        assert '<script>' not in result
    
    def test_handles_empty_content(self):
        """Test empty content handling."""
        result = validate_html_for_tinymce("")
        assert "Content processing failed" in result
    
    def test_extracts_body_content(self):
        """Test body content extraction."""
        html = '<html><body><p>Content</p></body></html>'
        result = validate_html_for_tinymce(html)
        assert '<p>Content</p>' in result


class TestSanitizeHtmlContent:
    """Test sanitize_html_content function."""
    
    def test_complete_sanitization_pipeline(self):
        """Test complete sanitization pipeline."""
        html = '''
        <p>Normal content</p>
        <script>alert("XSS")</script>
        <div onclick="hack()">Click me</div>
        '''
        result = sanitize_html_content(html)
        assert '<p>' in result
        assert '<script>' not in result
        assert 'onclick' not in result


class TestNormalizeKeywords:
    """Test normalize_keywords function."""
    
    def test_normalizes_keywords(self):
        """Test keyword normalization."""
        keywords = ["Python", "  JavaScript  ", "machine learning"]
        result = normalize_keywords(keywords)
        assert result == ["python", "javascript", "machine learning"]
    
    def test_removes_empty_keywords(self):
        """Test empty keyword removal."""
        keywords = ["Python", "", "   ", "JavaScript"]
        result = normalize_keywords(keywords)
        assert result == ["python", "javascript"]
    
    def test_handles_empty_list(self):
        """Test empty list handling."""
        assert normalize_keywords([]) == []


class TestConvertMarkdownToHtml:
    """Test convert_markdown_to_html function."""
    
    def test_converts_bold_text(self):
        """Test bold text conversion."""
        text = "This is **bold** text"
        assert convert_markdown_to_html(text) == "This is <strong>bold</strong> text"
    
    def test_converts_italic_text(self):
        """Test italic text conversion."""
        text = "This is *italic* text"
        assert convert_markdown_to_html(text) == "This is <em>italic</em> text"
    
    def test_converts_code_text(self):
        """Test code text conversion."""
        text = "Use `print()` function"
        assert convert_markdown_to_html(text) == "Use <code>print()</code> function"
    
    def test_removes_illegal_characters(self):
        """Test illegal character removal."""
        text = "Hello\x00World"
        assert convert_markdown_to_html(text) == "HelloWorld"
    
    def test_handles_empty_input(self):
        """Test empty input handling."""
        assert convert_markdown_to_html("") == ""
        assert convert_markdown_to_html(None) == ""
    
    def test_mixed_markdown(self):
        """Test mixed markdown conversion."""
        text = "**Bold** and *italic* with `code`"
        result = convert_markdown_to_html(text)
        assert "<strong>Bold</strong>" in result
        assert "<em>italic</em>" in result
        assert "<code>code</code>" in result