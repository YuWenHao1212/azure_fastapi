"""
Marker Fixer - Ensures optimization markers are only applied to specific keywords, not entire elements.
"""

import re

from bs4 import BeautifulSoup, NavigableString


class MarkerFixer:
    """Fix incorrectly applied optimization markers in HTML"""
    
    # Optimization CSS classes that should only be on spans
    SPAN_ONLY_CLASSES = ["opt-keyword", "opt-strength", "opt-placeholder", "opt-improvement"]
    
    # Classes that can be on block elements
    BLOCK_ALLOWED_CLASSES = ["opt-new"]
    
    def fix_markers(self, html: str) -> str:
        """Fix optimization markers to ensure they're only on appropriate elements"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all elements with optimization classes
        for class_name in self.SPAN_ONLY_CLASSES:
            # Find elements that shouldn't have this class (not spans)
            for element in soup.find_all(class_=class_name):
                if element.name != 'span':
                    self._fix_element_marker(element, class_name)
        
        return str(soup)
    
    def _fix_element_marker(self, element, class_name: str):
        """Fix an incorrectly marked element"""
        # Remove the class from the element
        if element.get('class'):
            classes = element['class']
            if class_name in classes:
                classes.remove(class_name)
                if classes:
                    element['class'] = classes
                else:
                    del element['class']
        
        # For keyword and strength markers, we need to identify and mark specific keywords
        if class_name in ["opt-keyword", "opt-strength"]:
            # This is more complex - we'd need to know which keywords to mark
            # For now, we'll just remove the incorrect marking
            # In a full implementation, we'd need the list of keywords to mark
            pass
    
    def apply_keyword_markers(self, html: str, keywords: list[str]) -> str:
        """Apply keyword markers to specific keywords in the HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process text nodes to mark keywords
        for element in soup.find_all(text=True):
            if isinstance(element, NavigableString) and element.strip():
                # Skip if already inside a span with opt- class
                parent = element.parent
                if parent and parent.name == 'span' and parent.get('class'):
                    if any(cls.startswith('opt-') for cls in parent['class']):
                        continue
                
                # Check if text contains any keywords
                new_html = self._mark_keywords_in_text(str(element), keywords)
                if new_html != str(element):
                    # Replace the text node with parsed HTML
                    new_soup = BeautifulSoup(new_html, 'html.parser')
                    element.replace_with(new_soup)
        
        return str(soup)
    
    def _mark_keywords_in_text(self, text: str, keywords: list[str]) -> str:
        """Mark keywords in a text string"""
        # Sort keywords by length (longest first) to avoid partial matches
        sorted_keywords = sorted(keywords, key=len, reverse=True)
        
        # Track positions already marked to avoid overlaps
        marked_positions = []
        result = text
        
        for keyword in sorted_keywords:
            # Use word boundaries to match whole words only
            pattern = r'\b' + re.escape(keyword) + r'\b'
            
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                
                # Check if this position overlaps with already marked text
                overlap = any(
                    start < marked_end and end > marked_start
                    for marked_start, marked_end in marked_positions
                )
                
                if not overlap:
                    marked_positions.append((start, end))
        
        # Sort positions by start index (reverse to replace from end to start)
        marked_positions.sort(reverse=True)
        
        # Apply markers
        for start, end in marked_positions:
            keyword = text[start:end]
            marked_keyword = f'<span class="opt-keyword">{keyword}</span>'
            result = result[:start] + marked_keyword + result[end:]
        
        return result
    
    def fix_and_enhance_markers(self, html: str, keywords: list[str] = None, 
                               strengths: list[str] = None) -> str:
        """Complete fix and enhancement of markers"""
        # First, fix incorrectly placed markers
        html = self.fix_markers(html)
        
        # Then, apply keyword markers if keywords are provided
        if keywords:
            html = self.apply_keyword_markers(html, keywords)
        
        # Apply strength markers if strengths are provided
        if strengths:
            # Similar to keywords but with opt-strength class
            # Implementation would be similar to apply_keyword_markers
            pass
        
        return html