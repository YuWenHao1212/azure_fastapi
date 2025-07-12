"""Unit tests for EnhancedMarker class."""


from src.core.enhanced_marker import EnhancedMarker


class TestEnhancedMarker:
    """Test cases for EnhancedMarker."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.marker = EnhancedMarker()
    
    def test_basic_keyword_marking(self):
        """Test basic keyword marking functionality."""
        html = "<p>Experience with Python and Java development</p>"
        original_keywords = ["Python"]
        new_keywords = ["Java"]
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        assert '<span class="opt-keyword-existing">Python</span>' in result
        assert '<span class="opt-keyword">Java</span>' in result
        assert "Experience with" in result
        assert "development" in result
    
    def test_case_insensitive_matching(self):
        """Test that keyword matching is case insensitive."""
        html = "<p>Working with python, PYTHON, and Python</p>"
        original_keywords = ["Python"]
        new_keywords = []
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # All variations should be marked
        assert result.count('<span class="opt-keyword-existing">') == 3
    
    def test_protected_term_case_correction(self):
        """Test that protected terms maintain correct casing."""
        html = "<p>Experience with javascript, nodejs, and mysql</p>"
        original_keywords = ["JavaScript", "Node.js", "MySQL"]
        new_keywords = []
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Check correct casing is applied
        assert '<span class="opt-keyword-existing">JavaScript</span>' in result
        assert '<span class="opt-keyword-existing">Node.js</span>' in result
        assert '<span class="opt-keyword-existing">MySQL</span>' in result
        assert 'javascript' not in result.replace('JavaScript', '')
        assert 'nodejs' not in result.replace('Node.js', '')
        assert 'mysql' not in result.replace('MySQL', '')
    
    def test_overlapping_keywords(self):
        """Test handling of overlapping keywords."""
        html = "<p>JavaScript and Java developer working on JavaScript</p>"
        original_keywords = ["JavaScript", "Java"]
        new_keywords = []
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Both JavaScript instances and Java should be marked
        assert '<span class="opt-keyword-existing">JavaScript</span>' in result
        assert '<span class="opt-keyword-existing">Java</span>' in result
        # Should have 3 spans total (2 JavaScript + 1 Java)
        assert result.count('<span class="opt-keyword-existing">') == 3
    
    def test_compound_keywords(self):
        """Test marking of compound keywords."""
        html = "<p>Experience with machine learning and data science</p>"
        original_keywords = []
        new_keywords = ["machine learning", "data science"]
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        assert '<span class="opt-keyword">machine learning</span>' in result
        assert '<span class="opt-keyword">data science</span>' in result
    
    def test_special_characters_in_keywords(self):
        """Test keywords with special characters."""
        html = "<p>Skills include C++, C#, and .NET framework</p>"
        original_keywords = []
        new_keywords = ["C++", "C#", ".NET"]
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        assert '<span class="opt-keyword">C++</span>' in result
        assert '<span class="opt-keyword">C#</span>' in result
        assert '<span class="opt-keyword">.NET</span>' in result
    
    def test_skip_already_marked_content(self):
        """Test that already marked content is not re-marked."""
        html = '''<p>Working with <span class="opt-keyword">Python</span> and Java</p>'''
        original_keywords = ["Python", "Java"]
        new_keywords = []
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Python should not be re-marked
        assert result.count('<span class="opt-keyword">Python</span>') == 1
        # Java should be marked as existing
        assert '<span class="opt-keyword-existing">Java</span>' in result
    
    def test_skip_script_and_style_tags(self):
        """Test that content in script and style tags is ignored."""
        html = """
        <div>
            <style>Python { color: blue; }</style>
            <script>var Python = 'language';</script>
            <p>Learning Python programming</p>
        </div>
        """
        original_keywords = ["Python"]
        new_keywords = []
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Only the Python in paragraph should be marked
        assert result.count('<span class="opt-keyword-existing">Python</span>') == 1
        assert 'Python { color: blue; }' in result  # Style content unchanged
        assert "var Python = 'language';" in result  # Script content unchanged
    
    def test_skills_list_marking(self):
        """Test marking keywords in a typical skills list."""
        html = """
        <ul>
            <li>Programming Languages: Python, Java, JavaScript, TypeScript</li>
            <li>Databases: MySQL, PostgreSQL, MongoDB</li>
            <li>Cloud: AWS, Azure, GCP</li>
        </ul>
        """
        original_keywords = ["Python", "JavaScript", "MySQL"]
        new_keywords = ["TypeScript", "MongoDB", "AWS", "Azure"]
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Check original keywords
        assert '<span class="opt-keyword-existing">Python</span>' in result
        assert '<span class="opt-keyword-existing">JavaScript</span>' in result
        assert '<span class="opt-keyword-existing">MySQL</span>' in result
        
        # Check new keywords
        assert '<span class="opt-keyword">TypeScript</span>' in result
        assert '<span class="opt-keyword">MongoDB</span>' in result
        assert '<span class="opt-keyword">AWS</span>' in result
        assert '<span class="opt-keyword">Azure</span>' in result
        
        # Check unmarked keywords
        assert '>Java<' in result or 'Java,' in result
        assert '>PostgreSQL<' in result or 'PostgreSQL,' in result
        assert '>GCP<' in result or 'GCP</li>' in result
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Empty HTML
        result = self.marker.mark_keywords("", ["Python"], ["Java"])
        assert result == ""
        
        # Empty keywords
        html = "<p>Some content</p>"
        result = self.marker.mark_keywords(html, [], [])
        assert result == html
        
        # None keywords
        result = self.marker.mark_keywords(html, None, None)
        assert "Some content" in result
    
    def test_nested_html_structure(self):
        """Test marking in nested HTML structures."""
        html = """
        <div>
            <h3>Technical Skills</h3>
            <p>
                <strong>Languages:</strong> Python, JavaScript<br>
                <em>Frameworks:</em> React, Django
            </p>
        </div>
        """
        original_keywords = ["Python"]
        new_keywords = ["JavaScript", "React", "Django"]
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Check structure is preserved
        assert "<strong>Languages:</strong>" in result
        assert "<em>Frameworks:</em>" in result
        
        # Check keywords are marked
        assert '<span class="opt-keyword-existing">Python</span>' in result
        assert '<span class="opt-keyword">JavaScript</span>' in result
        assert '<span class="opt-keyword">React</span>' in result
        assert '<span class="opt-keyword">Django</span>' in result
    
    def test_keyword_at_boundaries(self):
        """Test keywords at text boundaries."""
        html = "<p>Python, Java. JavaScript! TypeScript?</p>"
        original_keywords = ["Python", "Java"]
        new_keywords = ["JavaScript", "TypeScript"]
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # All keywords should be properly marked
        assert '<span class="opt-keyword-existing">Python</span>,' in result
        assert '<span class="opt-keyword-existing">Java</span>.' in result
        assert '<span class="opt-keyword">JavaScript</span>!' in result
        assert '<span class="opt-keyword">TypeScript</span>?' in result
    
    def test_word_boundary_matching(self):
        """Test that word boundaries are respected."""
        html = "<p>Working with Java, not JavaScript or Javanese</p>"
        original_keywords = ["Java"]
        new_keywords = []
        
        result = self.marker.mark_keywords(html, original_keywords, new_keywords)
        
        # Only standalone Java should be marked
        assert '<span class="opt-keyword-existing">Java</span>,' in result
        assert 'JavaScript' in result  # Should not be marked
        assert 'Javanese' in result  # Should not be marked
        assert result.count('<span class="opt-keyword-existing">') == 1