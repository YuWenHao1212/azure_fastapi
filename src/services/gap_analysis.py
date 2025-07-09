"""
Gap analysis service for analyzing differences between resume and job requirements.
Following FHS architecture principles.
"""
import logging
import re
import time
from typing import Any

from src.core.config import get_settings
from src.core.monitoring_service import monitoring_service
from src.services.openai_client import get_azure_openai_client
from src.services.text_processing import clean_llm_output, convert_markdown_to_html
from src.services.token_tracking_mixin import TokenTrackingMixin
from src.services.unified_prompt_service import UnifiedPromptService


def clean_and_process_lines(section_content: str | None) -> list[str]:
    """
    Clean and process text lines into HTML list items.
    
    Args:
        section_content: Raw text content
        
    Returns:
        List of HTML-formatted lines
    """
    lines = []
    if section_content:
        for line in section_content.strip().splitlines():
            # Remove bullet points and numbering
            text = re.sub(r'^\s*[-*•]\s*', '', line.strip())
            text = re.sub(r'^\s*\d+\.\s*', '', text)
            if text:
                lines.append(convert_markdown_to_html(text))
    return lines




def parse_skill_development_priorities(skill_content: str) -> list[dict[str, str]]:
    """
    Parse skill development priorities from formatted string.
    
    Expected format: SKILL_N::SkillName::CATEGORY::Description
    
    Args:
        skill_content: Raw skill content
        
    Returns:
        List of skill dictionaries
    """
    skills = []
    if not skill_content:
        return skills
    
    lines = skill_content.strip().splitlines()
    
    for line in lines:
        line = line.strip()
        if not line or '::' not in line:
            continue
        
        parts = line.split('::', 3)
        if len(parts) >= 4:
            skill_id, skill_name, category, description = parts
            
            # Skip if skill_name is empty
            if not skill_name.strip():
                continue
            
            # Validate category
            category = category.upper()
            if category not in ['TECHNICAL', 'NON_TECHNICAL']:
                category = 'TECHNICAL'  # Default
            
            skills.append({
                "skill_name": skill_name.strip(),
                "skill_category": category,
                "description": description.strip()
            })
    
    return skills


def parse_gap_response(content: str) -> dict[str, Any]:
    """
    Parse LLM gap analysis response from XML format.
    
    Args:
        content: Raw LLM response with XML tags
        
    Returns:
        Parsed gap analysis dictionary
    """
    # Extract each section using regex
    cs = re.search(r'<core_strengths>(.*?)</core_strengths>', content, re.S)
    kg = re.search(r'<key_gaps>(.*?)</key_gaps>', content, re.S)
    qi = re.search(r'<quick_improvements>(.*?)</quick_improvements>', content, re.S)
    oa = re.search(r'<overall_assessment>(.*?)</overall_assessment>', content, re.S)
    sdp = re.search(r'<skill_development_priorities>(.*?)</skill_development_priorities>', content, re.S)
    
    # Process each section
    strengths = clean_and_process_lines(cs.group(1) if cs else None)
    gaps = clean_and_process_lines(kg.group(1) if kg else None)
    improvements = clean_and_process_lines(qi.group(1) if qi else None)
    
    # Process overall assessment (paragraph format)
    assessment_text = ''
    if oa:
        raw_assessment = oa.group(1).strip()
        logging.info(f"[GAP_ANALYSIS] Raw assessment length: {len(raw_assessment)}")
        
        if raw_assessment:
            # Log FULL assessment for debugging (not just preview)
            logging.info(f"[GAP_ANALYSIS] Raw assessment FULL content: {repr(raw_assessment)}")
            
            # Join lines
            joined_text = ' '.join(line.strip() for line in raw_assessment.splitlines() if line.strip())
            logging.info(f"[GAP_ANALYSIS] Joined text length: {len(joined_text)}")
            logging.debug(f"[GAP_ANALYSIS] Joined text FULL: {repr(joined_text)}")
            
            # Convert to HTML
            assessment_text = convert_markdown_to_html(joined_text)
            logging.info(f"[GAP_ANALYSIS] HTML converted length: {len(assessment_text)}")
            logging.debug(f"[GAP_ANALYSIS] HTML converted FULL: {repr(assessment_text)}")
            
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
            logging.info(f"Processing skill content: {len(skill_content)} characters")
            skill_queries = parse_skill_development_priorities(skill_content)
            logging.info(f"Parsed {len(skill_queries)} skills")
        except Exception as e:
            logging.error(f"Error processing skill_development_priorities: {e}")
            skill_queries = []
    
    return {
        "strengths": strengths,
        "gaps": gaps,
        "improvements": improvements,
        "assessment": assessment_text,
        "skill_queries": skill_queries
    }


def format_gap_analysis_html(parsed_response: dict[str, Any]) -> dict[str, Any]:
    """
    Format parsed gap analysis into HTML structure.
    
    Args:
        parsed_response: Parsed gap analysis data
        
    Returns:
        HTML formatted gap analysis
    """
    # Convert lists to HTML ordered lists with fallback for empty lists
    def format_list_with_fallback(items: list[str], field_name: str) -> str:
        if items:
            return '<ol>' + ''.join(f'<li>{item}</li>' for item in items) + '</ol>'
        else:
            logging.warning(f"[GAP_ANALYSIS] {field_name} is empty")
            return f'<ol><li>Unable to analyze {field_name.lower().replace("_", " ")}. Please try again.</li></ol>'
    
    core_strengths = format_list_with_fallback(parsed_response.get('strengths', []), 'core_strengths')
    key_gaps = format_list_with_fallback(parsed_response.get('gaps', []), 'key_gaps')
    quick_improvements = format_list_with_fallback(parsed_response.get('improvements', []), 'quick_improvements')
    
    # Overall assessment is already in paragraph format
    assessment = parsed_response.get('assessment', '')
    if assessment and assessment not in ["", "Unable to generate overall assessment. Please review the strengths and gaps above.", "Overall assessment not available. Please refer to the detailed analysis above."]:
        overall_assessment = f'<p>{assessment}</p>'
    else:
        logging.warning("[GAP_ANALYSIS] Empty or default overall assessment detected in formatting")
        overall_assessment = '<p>Unable to generate a comprehensive assessment. Please review the individual sections above for detailed analysis.</p>'
    
    # Log the final HTML output
    logging.info(f"[GAP_ANALYSIS_HTML] Final OverallAssessment HTML: {repr(overall_assessment[:200])}...")
    
    # Log if we're still producing empty result
    if overall_assessment == '<p></p>':
        logging.error("[GAP_ANALYSIS] CRITICAL: Still producing empty <p></p> for OverallAssessment!")
        logging.error(f"[GAP_ANALYSIS] Assessment value was: {repr(assessment)}")
    
    return {
        "CoreStrengths": core_strengths,
        "KeyGaps": key_gaps,
        "QuickImprovements": quick_improvements,
        "OverallAssessment": overall_assessment,
        "SkillSearchQueries": parsed_response['skill_queries']
    }


class GapAnalysisService(TokenTrackingMixin):
    """Service class for gap analysis operations."""
    
    def __init__(self):
        """Initialize the service."""
        self.settings = get_settings()
        self.prompt_service = UnifiedPromptService(task_path="gap_analysis")
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def analyze_gap(
        self,
        job_description: str,
        resume: str,
        job_keywords: list[str],
        matched_keywords: list[str],
        missing_keywords: list[str],
        language: str = "en"
    ) -> dict[str, Any]:
        """
        Perform gap analysis between resume and job description.
        
        Args:
            job_description: Job description text
            resume: Resume text
            job_keywords: All job keywords
            matched_keywords: Keywords found in resume
            missing_keywords: Keywords not found in resume
            language: Output language (en or zh-TW)
            
        Returns:
            Formatted gap analysis results
        """
        # Validate and normalize language (case-insensitive)
        if language.lower() == "zh-tw":
            language = "zh-TW"
        elif language.lower() != "en":
            language = "en"
        
        # Prepare prompt data
        prompt_data = {
            "job_description": job_description,
            "resume": resume,
            "job_keywords": ", ".join(job_keywords) if job_keywords else "None",
            "matched_keywords": ", ".join(matched_keywords) if matched_keywords else "None",
            "missing_keywords": ", ".join(missing_keywords) if missing_keywords else "None"
        }
        
        # Get prompt from UnifiedPromptService
        # Use v1.2.0 for zh-TW to improve stability and output English skills
        version = "1.2.0" if language == "zh-TW" else "1.0.0"
        prompt_config = self.prompt_service.get_prompt_config(
            language=language,
            version=version
        )
        
        # Log the prompt version being used
        self.logger.info(f"Using gap analysis prompt version: {version} for language: {language}")
        
        if not prompt_config:
            raise ValueError(f"Gap analysis prompt not found for language: {language}")
        
        # Format prompts
        system_prompt = prompt_config.get_system_prompt()
        user_prompt = prompt_config.format_user_prompt(**prompt_data)
        
        # Get OpenAI client
        openai_client = get_azure_openai_client()
        
        try:
            # Call LLM
            self.logger.info(f"Calling LLM for gap analysis with language: {language}")
            
            llm_start_time = time.time()
            response = await openai_client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.settings.gap_analysis_temperature,
                max_tokens=self.settings.gap_analysis_max_tokens
            )
            llm_time = time.time() - llm_start_time
            
            # Extract response content
            llm_response = response['choices'][0]['message']['content']
            finish_reason = response['choices'][0].get('finish_reason', 'unknown')
            
            # Save raw response for debugging if needed
            raw_response_before_clean = llm_response
            
            # Log FULL LLM response for debugging
            self.logger.info(f"[GAP_ANALYSIS_LLM] Full raw LLM response ({len(llm_response)} chars):")
            self.logger.info(f"[GAP_ANALYSIS_LLM] {repr(llm_response)}")
            self.logger.info(f"LLM finish reason: {finish_reason}")
            
            # Clean LLM output
            llm_response = clean_llm_output(llm_response)
            
            # Log if overall_assessment is missing
            if '<overall_assessment>' not in llm_response:
                self.logger.warning("LLM response missing <overall_assessment> tag")
                self.logger.debug(f"Full LLM response: {llm_response}")
            else:
                # Check if the tag exists but content is empty
                import re
                oa_match = re.search(r'<overall_assessment>(.*?)</overall_assessment>', llm_response, re.S)
                if oa_match and not oa_match.group(1).strip():
                    self.logger.warning("Overall assessment tag found but content is empty")
                    self.logger.debug(f"Response around overall_assessment: {llm_response[max(0, llm_response.find('<overall_assessment>')-100):llm_response.find('</overall_assessment>')+50]}")
            
            # Track token usage and metrics
            token_info = self.track_openai_usage(
                response,
                operation="gap_analysis",
                additional_properties={
                    "language": language,
                    "processing_time_ms": round(llm_time * 1000, 2),
                    "prompt_length": len(system_prompt) + len(user_prompt),
                    "response_length": len(llm_response)
                }
            )
            
            # Parse response
            parsed_response = parse_gap_response(llm_response)
            
            # Debug: Check if any field is empty and log raw response
            if (not parsed_response.get('assessment') or 
                not parsed_response.get('improvements') or
                len(parsed_response.get('strengths', [])) == 0 or
                len(parsed_response.get('gaps', [])) == 0):
                self.logger.warning("Empty fields detected in parsed response")
                self.logger.debug(f"Raw LLM response before cleaning: {raw_response_before_clean}")
                self.logger.debug(f"LLM response after cleaning: {llm_response}")
            
            # Track detailed gap analysis completion
            monitoring_service.track_event(
                "GapAnalysisCompleted",
                {
                    "language": language,
                    "prompt_tokens": token_info["prompt_tokens"],
                    "completion_tokens": token_info["completion_tokens"],
                    "total_tokens": token_info["total_tokens"],
                    "processing_time_ms": round(llm_time * 1000, 2),
                    "estimated_cost_usd": self.estimate_token_cost(
                        token_info["prompt_tokens"],
                        token_info["completion_tokens"]
                    ),
                    "skill_queries_count": len(parsed_response.get('skill_queries', [])),
                    "response_sections": {
                        "strengths": len(parsed_response.get('strengths', [])),
                        "gaps": len(parsed_response.get('gaps', [])),
                        "improvements": len(parsed_response.get('improvements', []))
                    }
                }
            )
            
            # Format as HTML
            formatted_response = format_gap_analysis_html(parsed_response)
            
            # Monitor and log empty fields
            empty_fields = []
            field_checks = {
                "CoreStrengths": (formatted_response.get("CoreStrengths"), ["<ol></ol>", "<ol><li>Unable to analyze core strengths. Please try again.</li></ol>"]),
                "KeyGaps": (formatted_response.get("KeyGaps"), ["<ol></ol>", "<ol><li>Unable to analyze key gaps. Please try again.</li></ol>"]),
                "QuickImprovements": (formatted_response.get("QuickImprovements"), ["<ol></ol>", "<ol><li>Unable to analyze quick improvements. Please try again.</li></ol>"]),
                "OverallAssessment": (formatted_response.get("OverallAssessment"), ["<p></p>", "<p>Unable to generate a comprehensive assessment. Please review the individual sections above for detailed analysis.</p>"])
            }
            
            for field_name, (value, empty_values) in field_checks.items():
                if not value or value in empty_values:
                    empty_fields.append(field_name)
            
            if empty_fields:
                self.logger.error(f"[GAP_ANALYSIS_EMPTY] Empty fields detected: {empty_fields}")
                self.logger.info(f"[GAP_ANALYSIS_DEBUG] Raw response length: {len(llm_response)}")
                # Log FULL LLM response when empty fields are detected
                self.logger.error("[GAP_ANALYSIS_EMPTY_DEBUG] Full LLM response when empty fields detected:")
                self.logger.error(f"[GAP_ANALYSIS_EMPTY_DEBUG] {repr(llm_response)}")
                self.logger.error("[GAP_ANALYSIS_EMPTY_DEBUG] Raw response before cleaning:")
                self.logger.error(f"[GAP_ANALYSIS_EMPTY_DEBUG] {repr(raw_response_before_clean)}")
                
                # Log to monitoring service
                monitoring_service.track_event(
                    "GapAnalysisEmptyFields",
                    {
                        "empty_fields": ",".join(empty_fields),
                        "language": language,
                        "raw_response_length": len(llm_response),
                        "has_overall_assessment_tag": '<overall_assessment>' in llm_response,
                        "finish_reason": finish_reason
                    }
                )
            
            self.logger.info("Gap analysis completed successfully")
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error in gap analysis: {e}")
            raise
        finally:
            await openai_client.close()