#!/usr/bin/env python3
"""
Debug script to investigate empty values in ALL gap analysis fields.
This script will:
1. Run gap analysis 30 times with English language
2. Save raw LLM output and post-processed results
3. Track empty/missing values for ALL fields: CoreStrengths, KeyGaps, QuickImprovements, OverallAssessment, SkillSearchQueries
4. Identify patterns in empty field occurrences
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, List, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.services.gap_analysis import GapAnalysisService
from src.core.config import get_settings
from src.core.monitoring_service import monitoring_service

# Sample test data
SAMPLE_RESUME = """
Python Developer with 4 years of experience
- Strong expertise in Python programming and backend development
- Built and maintained microservices architecture
- Experience with REST API development
- Proficient in PostgreSQL, MongoDB, and Redis
- Hands-on experience with CI/CD pipelines using Jenkins and GitLab
- Contributed to distributed systems serving millions of users
"""

SAMPLE_JOB_DESCRIPTION = """
We are looking for a Senior Python Developer to join our team.

Requirements:
- 3+ years of experience with Python
- Strong knowledge of FastAPI framework
- Experience with microservices architecture
- Proficient in Docker and Kubernetes
- Experience with cloud platforms (AWS or Azure)
- Knowledge of CI/CD practices
- Experience with REST API development
- Strong database skills
- Team leadership experience
- Familiarity with monitoring tools
"""

def check_field_empty(value: Any) -> bool:
    """Check if a field value is empty."""
    if value is None:
        return True
    if isinstance(value, str):
        # Check for empty string, empty HTML, or whitespace only
        cleaned = value.strip()
        return cleaned == "" or cleaned == "<p></p>" or cleaned == "<ol></ol>" or cleaned == "<ul></ul>"
    if isinstance(value, list):
        return len(value) == 0
    return False

def analyze_raw_response(raw_response: str) -> Dict[str, Any]:
    """Analyze raw LLM response for missing or malformed tags."""
    analysis = {
        "has_core_strengths": False,
        "has_key_gaps": False,
        "has_quick_improvements": False,
        "has_overall_assessment": False,
        "has_skill_priorities": False,
        "malformed_tags": [],
        "empty_tags": []
    }
    
    if not raw_response:
        return analysis
    
    # Check for each expected tag
    tags_to_check = [
        ("core_strengths", "has_core_strengths"),
        ("key_gaps", "has_key_gaps"),
        ("quick_improvements", "has_quick_improvements"),
        ("overall_assessment", "has_overall_assessment"),
        ("skill_development_priorities", "has_skill_priorities")
    ]
    
    for tag_name, flag_name in tags_to_check:
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        
        if start_tag in raw_response:
            analysis[flag_name] = True
            
            # Check if tag is properly closed
            if end_tag not in raw_response:
                analysis["malformed_tags"].append(tag_name)
            else:
                # Extract content between tags
                start_idx = raw_response.find(start_tag) + len(start_tag)
                end_idx = raw_response.find(end_tag)
                content = raw_response[start_idx:end_idx].strip()
                
                if not content:
                    analysis["empty_tags"].append(tag_name)
    
    return analysis

async def debug_gap_analysis():
    """Run gap analysis multiple times and collect debug data for all fields."""
    settings = get_settings()
    service = GapAnalysisService()
    
    # Create debug directory
    debug_dir = Path("debug_gap_analysis_results")
    debug_dir.mkdir(exist_ok=True)
    
    # Initialize results storage
    results = []
    field_empty_counts = {
        "core_strengths": 0,
        "key_gaps": 0,
        "quick_improvements": 0,
        "overall_assessment": 0,
        "skill_search_queries": 0
    }
    
    print(f"Starting comprehensive gap analysis debug session at {datetime.now()}")
    print(f"Running 30 gap analysis tests with language='en'...")
    print(f"Tracking ALL fields: CoreStrengths, KeyGaps, QuickImprovements, OverallAssessment, SkillSearchQueries")
    print("-" * 100)
    
    for i in range(30):
        try:
            print(f"\nTest {i+1}/30...")
            
            # Capture raw LLM response
            raw_response = None
            
            # Import the module-level parse function
            from src.services import gap_analysis as gap_module
            
            # Monkey patch to capture raw response
            original_parse = gap_module.parse_gap_response
            
            def debug_parse(response_text):
                nonlocal raw_response
                raw_response = response_text
                return original_parse(response_text)
            
            gap_module.parse_gap_response = debug_parse
            
            # Execute gap analysis - use the analyze_gap method
            # First need to extract some keywords for the analysis
            job_keywords = ["Python", "FastAPI", "microservices", "Docker", "Kubernetes", "AWS", "Azure", "CI/CD", "REST API", "database", "team leadership", "monitoring tools"]
            matched_keywords = ["Python", "microservices", "CI/CD", "REST API", "database"]
            missing_keywords = ["FastAPI", "Docker", "Kubernetes", "AWS", "Azure", "team leadership", "monitoring tools"]
            
            result = await service.analyze_gap(
                job_description=SAMPLE_JOB_DESCRIPTION,
                resume=SAMPLE_RESUME,
                job_keywords=job_keywords,
                matched_keywords=matched_keywords,
                missing_keywords=missing_keywords,
                language="en"
            )
            
            # Restore original method
            gap_module.parse_gap_response = original_parse
            
            # Check each field for emptiness
            field_status = {
                "core_strengths": check_field_empty(result.get("CoreStrengths")),
                "key_gaps": check_field_empty(result.get("KeyGaps")),
                "quick_improvements": check_field_empty(result.get("QuickImprovements")),
                "overall_assessment": check_field_empty(result.get("OverallAssessment")),
                "skill_search_queries": check_field_empty(result.get("SkillSearchQueries"))
            }
            
            # Count empty fields
            empty_fields = []
            for field, is_empty in field_status.items():
                if is_empty:
                    field_empty_counts[field] += 1
                    empty_fields.append(field)
            
            # Analyze raw response
            raw_analysis = analyze_raw_response(raw_response)
            
            # Print status
            if empty_fields:
                print(f"  ⚠️  EMPTY fields detected: {', '.join(empty_fields)}")
            else:
                print(f"  ✓  All fields have content")
            
            # Save detailed results
            test_result = {
                "test_number": i + 1,
                "timestamp": datetime.now().isoformat(),
                "empty_fields": empty_fields,
                "field_status": field_status,
                "raw_llm_response": raw_response,
                "raw_response_analysis": raw_analysis,
                "parsed_result": {
                    "core_strengths": result.get("CoreStrengths"),
                    "key_gaps": result.get("KeyGaps"),
                    "quick_improvements": result.get("QuickImprovements"),
                    "overall_assessment": result.get("OverallAssessment"),
                    "skill_search_queries": result.get("SkillSearchQueries", [])
                }
            }
            
            results.append(test_result)
            
            # Save individual result if it has empty fields or is in first 5
            if empty_fields or i < 5:
                result_file = debug_dir / f"test_{i+1:03d}_{'empty_' + '_'.join(empty_fields) if empty_fields else 'ok'}.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(test_result, f, ensure_ascii=False, indent=2)
            
            # Small delay between requests
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Error in test {i+1}: {str(e)}")
            results.append({
                "test_number": i + 1,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "empty_fields": None
            })
    
    # Summary
    print("\n" + "=" * 100)
    print("COMPREHENSIVE DEBUG SESSION SUMMARY")
    print("=" * 100)
    print(f"Total tests: 30")
    print(f"\nEmpty field occurrences:")
    for field, count in field_empty_counts.items():
        percentage = count / 30 * 100
        print(f"  - {field}: {count} times ({percentage:.1f}%)")
    
    # Pattern analysis
    print(f"\nPattern Analysis:")
    # Count tests with any empty field
    tests_with_empty = sum(1 for r in results if r.get("empty_fields"))
    print(f"  - Tests with at least one empty field: {tests_with_empty} ({tests_with_empty/30*100:.1f}%)")
    
    # Check for correlated empty fields
    field_combinations = {}
    for r in results:
        if r.get("empty_fields"):
            combo = tuple(sorted(r["empty_fields"]))
            field_combinations[combo] = field_combinations.get(combo, 0) + 1
    
    if field_combinations:
        print(f"\n  - Empty field combinations:")
        for combo, count in sorted(field_combinations.items(), key=lambda x: x[1], reverse=True):
            print(f"    • {' + '.join(combo)}: {count} times")
    
    # Save full results
    summary_file = debug_dir / f"comprehensive_debug_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_tests": 30,
                "field_empty_counts": field_empty_counts,
                "tests_with_any_empty": tests_with_empty,
                "field_combinations": field_combinations,
                "test_datetime": datetime.now().isoformat()
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: {summary_file}")
    
    # Detailed analysis of problematic cases
    if tests_with_empty > 0:
        print("\n" + "-" * 100)
        print("DETAILED ANALYSIS OF PROBLEMATIC CASES")
        print("-" * 100)
        
        problematic_cases = [r for r in results if r.get("empty_fields")]
        for case in problematic_cases[:3]:  # Show first 3 problematic cases
            print(f"\nProblematic case #{case['test_number']}:")
            print(f"  Empty fields: {', '.join(case['empty_fields'])}")
            
            if 'raw_response_analysis' in case:
                analysis = case['raw_response_analysis']
                print(f"  Raw response analysis:")
                print(f"    - Malformed tags: {', '.join(analysis['malformed_tags']) if analysis['malformed_tags'] else 'None'}")
                print(f"    - Empty tags: {', '.join(analysis['empty_tags']) if analysis['empty_tags'] else 'None'}")
                
                # Check which tags are missing entirely
                missing_tags = []
                for tag, flag in [
                    ("core_strengths", "has_core_strengths"),
                    ("key_gaps", "has_key_gaps"),
                    ("quick_improvements", "has_quick_improvements"),
                    ("overall_assessment", "has_overall_assessment"),
                    ("skill_development_priorities", "has_skill_priorities")
                ]:
                    if not analysis[flag]:
                        missing_tags.append(tag)
                
                if missing_tags:
                    print(f"    - Missing tags: {', '.join(missing_tags)}")

if __name__ == "__main__":
    asyncio.run(debug_gap_analysis())