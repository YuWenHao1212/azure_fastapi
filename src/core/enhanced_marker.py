"""
Enhanced marker for precise keyword marking in HTML content.
Handles both new and existing keywords with proper overlap detection.
"""

import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EnhancedMarker:
    """Enhanced marker for keyword marking with overlap handling."""
    
    def __init__(self):
        """Initialize the enhanced marker with protected terms."""
        # Terms that have specific capitalization
        self.protected_terms = {
            'JavaScript': ['javascript', 'Javascript', 'JAVASCRIPT'],
            'TypeScript': ['typescript', 'Typescript', 'TYPESCRIPT'],
            'PowerShell': ['powershell', 'Powershell', 'POWERSHELL'],
            'GitHub': ['github', 'Github', 'GITHUB'],
            'GitLab': ['gitlab', 'Gitlab', 'GITLAB'],
            'PostgreSQL': ['postgresql', 'Postgresql', 'POSTGRESQL'],
            'MongoDB': ['mongodb', 'Mongodb', 'MONGODB'],
            'MySQL': ['mysql', 'Mysql', 'MYSQL'],
            'NoSQL': ['nosql', 'Nosql', 'NOSQL'],
            'GraphQL': ['graphql', 'Graphql', 'GRAPHQL'],
            'RESTful': ['restful', 'Restful', 'RESTFUL'],
            'OAuth': ['oauth', 'Oauth', 'OAUTH'],
            'DevOps': ['devops', 'Devops', 'DEVOPS'],
            'CI/CD': ['ci/cd', 'CI/cd', 'CICD', 'cicd'],
            'Node.js': ['nodejs', 'NodeJS', 'node.js', 'Node.JS', 'Nodejs'],
            'Vue.js': ['vuejs', 'VueJS', 'vue.js', 'Vue.JS'],
            'iOS': ['ios', 'IOS', 'Ios'],
            'macOS': ['macos', 'MacOS', 'MacOs', 'MACOS'],
            'API': ['api', 'Api'],
            'REST': ['rest', 'Rest'],
            'SQL': ['sql', 'Sql'],
            'HTML': ['html', 'Html'],
            'CSS': ['css', 'Css'],
            'XML': ['xml', 'Xml'],
            'JSON': ['json', 'Json'],
            'YAML': ['yaml', 'Yaml'],
            'PhD': ['phd', 'PHD', 'Ph.D', 'ph.d'],
            'MBA': ['mba', 'Mba'],
        }
        
        # Reverse mapping for quick lookup
        self.term_mapping = {}
        for correct, variants in self.protected_terms.items():
            for variant in variants:
                self.term_mapping[variant.lower()] = correct
    
    def mark_keywords(
        self,
        html: str,
        original_keywords: list[str],
        new_keywords: list[str]
    ) -> str:
        """
        Mark keywords in HTML content.
        
        Args:
            html: HTML content to process
            original_keywords: Keywords from original resume (mark as opt-keyword-existing)
            new_keywords: New keywords added during optimization (mark as opt-keyword)
            
        Returns:
            HTML with marked keywords
        """
        if not html:
            return html
            
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Prepare keywords lists
        original_keywords = [kw for kw in (original_keywords or []) if kw.strip()]
        new_keywords = [kw for kw in (new_keywords or []) if kw.strip()]
        
        # Log for debugging
        logger.info(f"Marking keywords - Original: {len(original_keywords)}, New: {len(new_keywords)}")
        
        # Process all text nodes
        text_nodes = []
        for element in soup.find_all(text=True):
            # Skip if parent is script, style, or already marked
            if element.parent.name in ['script', 'style']:
                continue
                
            # Skip if already in a marked span
            if (element.parent.name == 'span' and 
                element.parent.get('class') and
                any(cls in element.parent.get('class', []) 
                    for cls in ['opt-keyword', 'opt-keyword-existing', 
                               'opt-placeholder', 'opt-modified'])):
                continue
                
            text_nodes.append(element)
        
        # Mark keywords in each text node
        for text_node in text_nodes:
            new_html = self._mark_keywords_in_text(
                str(text_node),
                original_keywords,
                new_keywords
            )
            
            if new_html != str(text_node):
                # Replace the text node with marked HTML
                new_soup = BeautifulSoup(new_html, 'html.parser')
                # Extract just the content (not the wrapper tags BeautifulSoup adds)
                if new_soup.body:
                    # BeautifulSoup wraps in html/body, extract contents
                    for child in list(new_soup.body.children):
                        text_node.insert_before(child)
                else:
                    # Simple case - direct content
                    for child in list(new_soup.children):
                        text_node.insert_before(child)
                text_node.extract()
        
        return str(soup)
    
    def _mark_keywords_in_text(
        self,
        text: str,
        original_keywords: list[str],
        new_keywords: list[str]
    ) -> str:
        """
        Mark keywords in plain text, handling overlaps.
        
        Args:
            text: Plain text to process
            original_keywords: Original keywords to mark as opt-keyword-existing
            new_keywords: New keywords to mark as opt-keyword
            
        Returns:
            Text with HTML spans for keywords
        """
        if not text.strip():
            return text
        
        # Combine all keywords with their CSS classes
        all_keywords = []
        
        # Add original keywords
        for kw in original_keywords:
            all_keywords.append((kw, 'opt-keyword-existing'))
            
        # Add new keywords
        for kw in new_keywords:
            all_keywords.append((kw, 'opt-keyword'))
        
        # Sort by length (longest first) to handle overlaps
        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
        
        # Track marked positions to avoid overlaps
        marked_positions = []
        
        # Create result by marking keywords
        result = text
        replacements = []
        
        for keyword, css_class in all_keywords:
            pattern = self._create_keyword_pattern(keyword)
            
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                
                # Check if this position overlaps with already marked keywords
                overlap = False
                for marked_start, marked_end in marked_positions:
                    if (start < marked_end and end > marked_start):
                        overlap = True
                        break
                
                if not overlap:
                    matched_text = match.group()
                    
                    # Check if this needs case correction
                    corrected_text = self._get_corrected_case(matched_text)
                    
                    replacements.append({
                        'start': start,
                        'end': end,
                        'original': matched_text,
                        'replacement': f'<span class="{css_class}">{corrected_text}</span>'
                    })
                    marked_positions.append((start, end))
        
        # Apply replacements in reverse order to maintain positions
        replacements.sort(key=lambda x: x['start'], reverse=True)
        for repl in replacements:
            result = (
                result[:repl['start']] + 
                repl['replacement'] + 
                result[repl['end']:]
            )
        
        return result
    
    def _create_keyword_pattern(self, keyword: str) -> str:
        """
        Create regex pattern for keyword matching.
        
        Args:
            keyword: Keyword to create pattern for
            
        Returns:
            Regex pattern string
        """
        # Check if this keyword has variants we should match
        if keyword in self.protected_terms:
            # Create pattern that matches any variant
            variants = [keyword] + self.protected_terms[keyword]
            escaped_variants = [re.escape(v) for v in variants]
            # Join with | and wrap in word boundaries where appropriate
            pattern_parts = []
            for variant in escaped_variants:
                if any(char in variant for char in ['+', '#', '.', '-', '/']):
                    pattern_parts.append(variant)
                else:
                    pattern_parts.append(r'\b' + variant + r'\b')
            return '(' + '|'.join(pattern_parts) + ')'
        
        # Standard keyword handling
        escaped = re.escape(keyword)
        
        # For acronyms and special terms, match exact case
        if keyword.isupper() or any(char in keyword for char in ['+', '#', '.', '-', '/']):
            return escaped
        
        # For compound words with spaces, ensure word boundaries
        if ' ' in keyword:
            # Match the whole phrase with word boundaries
            return r'\b' + escaped + r'\b'
        
        # For single words, use word boundaries
        return r'\b' + escaped + r'\b'
    
    def _get_corrected_case(self, text: str) -> str:
        """
        Get the correctly cased version of a term if it's protected.
        
        Args:
            text: Text to check for case correction
            
        Returns:
            Correctly cased text or original if not protected
        """
        lower_text = text.lower()
        if lower_text in self.term_mapping:
            return self.term_mapping[lower_text]
        return text