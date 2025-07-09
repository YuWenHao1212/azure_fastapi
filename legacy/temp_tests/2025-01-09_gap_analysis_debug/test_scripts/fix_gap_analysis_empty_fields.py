#!/usr/bin/env python3
"""
Fix for gap analysis empty fields issue.
This script shows the proposed changes to handle empty or missing fields.
"""

def parse_gap_response_fixed(content: str) -> dict[str, Any]:
    """
    Enhanced version of parse_gap_response with better handling of empty fields.
    """
    import re
    import logging
    
    # Extract each section using regex
    cs = re.search(r'<core_strengths>(.*?)</core_strengths>', content, re.S)
    kg = re.search(r'<key_gaps>(.*?)</key_gaps>', content, re.S)
    qi = re.search(r'<quick_improvements>(.*?)</quick_improvements>', content, re.S)
    oa = re.search(r'<overall_assessment>(.*?)</overall_assessment>', content, re.S)
    sdp = re.search(r'<skill_development_priorities>(.*?)</skill_development_priorities>', content, re.S)
    
    # Process each section with fallback
    strengths = clean_and_process_lines(cs.group(1) if cs else None)
    gaps = clean_and_process_lines(kg.group(1) if kg else None)
    improvements = clean_and_process_lines(qi.group(1) if qi else None)
    
    # Enhanced overall assessment processing with detailed logging
    assessment_text = ''
    if oa:
        raw_assessment = oa.group(1).strip()
        logging.info(f"[GAP_ANALYSIS] Raw assessment length: {len(raw_assessment)}")
        
        if raw_assessment:
            # Log first 100 chars for debugging
            logging.debug(f"[GAP_ANALYSIS] Raw assessment preview: {repr(raw_assessment[:100])}")
            
            # Join lines
            joined_text = ' '.join(line.strip() for line in raw_assessment.splitlines() if line.strip())
            logging.debug(f"[GAP_ANALYSIS] Joined text length: {len(joined_text)}")
            
            # Convert to HTML
            assessment_text = convert_markdown_to_html(joined_text)
            logging.debug(f"[GAP_ANALYSIS] HTML converted length: {len(assessment_text)}")
            
            # Fallback if conversion resulted in empty
            if not assessment_text and joined_text:
                logging.warning("[GAP_ANALYSIS] Markdown conversion resulted in empty text, using raw content")
                assessment_text = joined_text
        else:
            logging.warning("[GAP_ANALYSIS] Overall assessment tag found but content is empty")
            # Provide a default message instead of empty
            assessment_text = "Unable to generate overall assessment. Please review the strengths and gaps above."
    else:
        logging.warning("[GAP_ANALYSIS] Overall assessment tag not found in response")
        # Provide a default message
        assessment_text = "Overall assessment not available. Please refer to the detailed analysis above."
    
    # Process skill development priorities
    skill_queries = []
    if sdp:
        try:
            skill_content = sdp.group(1).strip()
            logging.info(f"[GAP_ANALYSIS] Processing skill content: {len(skill_content)} characters")
            skill_queries = parse_skill_development_priorities(skill_content)
            logging.info(f"[GAP_ANALYSIS] Parsed {len(skill_queries)} skills")
        except Exception as e:
            logging.error(f"[GAP_ANALYSIS] Error processing skill_development_priorities: {e}")
            skill_queries = []
    
    # Ensure no field is None or empty list
    return {
        "strengths": strengths or ["Analysis in progress"],
        "gaps": gaps or ["Analysis in progress"],
        "improvements": improvements or ["Analysis in progress"],
        "assessment": assessment_text or "Analysis in progress",
        "skill_queries": skill_queries or []
    }


def format_gap_analysis_html_fixed(parsed_response: dict[str, Any]) -> dict[str, Any]:
    """
    Enhanced version with better empty field handling.
    """
    # Convert lists to HTML ordered lists with fallback
    def format_list(items: list[str], field_name: str) -> str:
        if items and items != ["Analysis in progress"]:
            return '<ol>' + ''.join(f'<li>{item}</li>' for item in items) + '</ol>'
        else:
            logging.warning(f"[GAP_ANALYSIS] {field_name} is empty or default")
            return f'<ol><li>Unable to analyze {field_name.lower()}. Please try again.</li></ol>'
    
    core_strengths = format_list(parsed_response['strengths'], 'CoreStrengths')
    key_gaps = format_list(parsed_response['gaps'], 'KeyGaps')
    quick_improvements = format_list(parsed_response['improvements'], 'QuickImprovements')
    
    # Overall assessment with better fallback
    assessment = parsed_response.get('assessment', '')
    if assessment and assessment not in ["Analysis in progress", ""]:
        overall_assessment = f'<p>{assessment}</p>'
    else:
        logging.warning("[GAP_ANALYSIS] Empty or default overall assessment detected")
        overall_assessment = '<p>Unable to generate a comprehensive assessment. Please review the individual sections above for detailed analysis.</p>'
    
    # Log final output for debugging
    if overall_assessment == '<p></p>':
        logging.error("[GAP_ANALYSIS] CRITICAL: Still producing empty <p></p> for OverallAssessment!")
    
    return {
        "CoreStrengths": core_strengths,
        "KeyGaps": key_gaps,
        "QuickImprovements": quick_improvements,
        "OverallAssessment": overall_assessment,
        "SkillSearchQueries": parsed_response.get('skill_queries', [])
    }


# Additional monitoring function
def monitor_gap_analysis_response(result: dict[str, Any], request_id: str) -> None:
    """
    Monitor and log gap analysis results for empty fields.
    """
    import json
    from datetime import datetime
    
    empty_fields = []
    
    # Check each field
    for field, empty_values in {
        "CoreStrengths": ["<ol></ol>", "<ol><li>Unable to analyze corestrengths. Please try again.</li></ol>"],
        "KeyGaps": ["<ol></ol>", "<ol><li>Unable to analyze keygaps. Please try again.</li></ol>"],
        "QuickImprovements": ["<ol></ol>", "<ol><li>Unable to analyze quickimprovements. Please try again.</li></ol>"],
        "OverallAssessment": ["<p></p>", "<p>Unable to generate a comprehensive assessment. Please review the individual sections above for detailed analysis.</p>"],
    }.items():
        value = result.get(field, "")
        if value in empty_values or not value:
            empty_fields.append(field)
    
    if empty_fields:
        # Log to monitoring service
        logging.error(f"[GAP_ANALYSIS_EMPTY] Request {request_id} has empty fields: {empty_fields}")
        
        # Save debug info
        debug_file = f"gap_analysis_debug_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"debug_logs/{debug_file}", "w") as f:
            json.dump({
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "empty_fields": empty_fields,
                "result": result
            }, f, indent=2)


print("Proposed fixes for gap analysis empty fields:")
print("=" * 80)
print("1. Enhanced logging to track where content is lost")
print("2. Fallback messages instead of empty <p></p>")
print("3. Better error handling and recovery")
print("4. Monitoring to track empty field occurrences")
print("5. Debug file generation for problematic responses")
print("\nThese changes will help identify the root cause and provide better user experience.")