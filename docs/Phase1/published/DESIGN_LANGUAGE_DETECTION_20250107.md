# Language Detection Design Specification

**Document ID**: DESIGN_LANGUAGE_DETECTION_20250107  
**Version**: 1.0  
**Date**: 2025-01-07  
**Author**: Claude Code  
**Status**: Approved for Implementation

## Executive Summary

This document specifies the enhanced language detection and tracking system for the keyword extraction API. The system will provide consistent language detection rules with proper handling of mixed language content and comprehensive tracking for analytics.

## Requirements

### Functional Requirements

1. **Language Detection**
   - Detect and classify job descriptions into three categories: `en`, `zh-TW`, `other`
   - Support mixed language content with clear rules for classification
   - Provide 10% tolerance for non-supported characters (brands, special terms)

2. **Language Support**
   - Supported languages: English (en), Traditional Chinese (zh-TW)
   - Unsupported languages: Simplified Chinese (zh-CN), Japanese, Korean, Spanish, and others

3. **Tracking and Analytics**
   - Track all language detection results in a unified event
   - Enable easy creation of language distribution statistics
   - Preserve detailed language composition for debugging

### Non-Functional Requirements

1. **Performance**: Language detection should complete within 10ms
2. **Accuracy**: Correctly differentiate between Traditional and Simplified Chinese
3. **Maintainability**: Clear separation of detection logic and tracking

## Technical Design

### Language Detection Flow

```mermaid
graph TD
    A[Keyword Extraction Request] --> B[Language Detection]
    B --> C[Calculate Character Composition]
    
    C --> D{Check Unsupported Languages}
    D -->|zh-CN/ja/ko/es/other > 10%| E[Unsupported Language]
    D -->|zh-CN/ja/ko/es/other ≤ 10%| F{Analyze EN/zh-TW}
    
    F --> G{zh-TW Characters?}
    G -->|zh-TW ≥ 20%| H[detected_language: 'zh-TW']
    G -->|zh-TW < 20%| J[detected_language: 'en']
    
    E --> K[detected_language: 'other']
    
    H --> L[Process with zh-TW LLM]
    J --> M[Process with EN LLM]
    K --> N[Skip LLM Processing]
    
    L --> O[Track LanguageDetected Event]
    M --> O
    N --> O
    
    O --> P{All requests record:<br/>- detected_language<br/>- language_composition<br/>- will_process<br/>- jd_preview (if unsupported)}
    
    style E fill:#f96
    style K fill:#f96
    style N fill:#f96
```

### Detection Rules

| Priority | Condition | Decision | Action |
|----------|-----------|----------|--------|
| 1 | (zh-CN + ja + ko + es + other) > 10% of total | `other` | Skip LLM, Track with JD preview |
| 2 | zh-TW ≥ 20% of (EN + zh-TW + numbers/symbols) | `zh-TW` | Use zh-TW prompt |
| 3 | zh-TW < 20% of (EN + zh-TW + numbers/symbols) | `en` | Use EN prompt (default) |

**Important Clarification**: 
- Step 1: Check if unsupported languages > 10% of **total characters** (reject if true)
- Step 2: If passed, calculate zh-TW percentage based on **supported content only**
- Formula: `zh-TW% = zh-TW chars / (EN + zh-TW + numbers/symbols) × 100`
- This excludes other languages from the denominator since they've already been filtered out

### Character Classification

```python
# Character categories
- English (EN): A-Z, a-z, common punctuation
- Traditional Chinese (zh-TW): 繁體中文字符
- Simplified Chinese (zh-CN): 简体中文字符 (UNSUPPORTED)
- Japanese (JA): Hiragana, Katakana, Kanji
- Korean (KO): Hangul characters
- Spanish (ES): Special Spanish characters (ñ, á, é, etc.)
- Other: Everything else (excluding numbers and common symbols)
```

## Event Tracking Specification

### Unified LanguageDetected Event

All keyword extraction requests will track a single unified event:

```python
{
    "name": "LanguageDetected",
    "properties": {
        "detected_language": "en" | "zh-TW" | "other",  # Only 3 values
        "language_composition": {
            "en_percent": 75.5,
            "zh_tw_percent": 20.3,
            "zh_cn_percent": 2.1,  # Tracked separately
            "ja_percent": 1.5,
            "ko_percent": 0.0,
            "es_percent": 0.6,
            "other_percent": 0.0
        },
        "decision_reason": "zh_tw_dominant" | "english_default" | "unsupported_content",
        "will_process": true | false,  # false for "other"
        "requested_language": "auto" | "en" | "zh-TW",
        "jd_length": 165,
        "jd_preview": "..." | null  # Only populated for detected_language="other"
    }
}
```

### Decision Reasons

- `zh_tw_dominant`: Traditional Chinese ≥ 20%
- `english_default`: Passed unsupported check, zh-TW < 20%
- `unsupported_content`: Contains > 10% unsupported languages

## Implementation Examples

### Example 1: Pure English with Brand Names
```json
{
    "detected_language": "en",
    "language_composition": {
        "en_percent": 92.0,
        "zh_tw_percent": 0.0,
        "other_percent": 8.0
    },
    "decision_reason": "english_default",
    "will_process": true,
    "jd_preview": null
}
```

### Example 2: Mixed EN/zh-TW
```json
{
    "detected_language": "zh-TW",
    "language_composition": {
        "en_percent": 65.0,
        "zh_tw_percent": 35.0
    },
    "decision_reason": "zh_tw_dominant",
    "will_process": true,
    "jd_preview": null
}
```
**Calculation Example**: 
- Total: 100 characters
- EN: 65 chars
- zh-TW: 35 chars
- Other languages: 0 chars
- Supported content: 65 + 35 = 100 chars
- zh-TW percentage: 35/100 = 35% ≥ 20%, use zh-TW prompt

### Example 3: Contains Simplified Chinese
```json
{
    "detected_language": "other",
    "language_composition": {
        "en_percent": 80.0,
        "zh_cn_percent": 20.0
    },
    "decision_reason": "unsupported_content",
    "will_process": false,
    "jd_preview": "We need a developer with experience in 北京..."
}
```

## Analytics Queries

### Language Distribution Pie Chart
```kusto
customEvents
| where name == "LanguageDetected"
| where timestamp > ago(7d)
| summarize count() by tostring(customDimensions.detected_language)
| render piechart
```

### Detailed Language Composition Analysis
```kusto
customEvents
| where name == "LanguageDetected"
| where timestamp > ago(1d)
| extend 
    lang = tostring(customDimensions.detected_language),
    zh_tw_pct = todouble(customDimensions.language_composition.zh_tw_percent),
    en_pct = todouble(customDimensions.language_composition.en_percent),
    zh_cn_pct = todouble(customDimensions.language_composition.zh_cn_percent)
| summarize 
    avg_zh_tw = avg(zh_tw_pct),
    avg_en = avg(en_pct),
    avg_zh_cn = avg(zh_cn_pct)
    by lang
```

### Example 4: Edge Case - With Minor Unsupported Content
```json
{
    "detected_language": "zh-TW",
    "language_composition": {
        "en_percent": 60.0,
        "zh_tw_percent": 25.0,
        "zh_cn_percent": 5.0,
        "other_percent": 5.0,
        "numbers_symbols_percent": 5.0
    },
    "decision_reason": "zh_tw_dominant",
    "will_process": true,
    "jd_preview": null
}
```
**Calculation Example**: 
- Total: 100 characters
- EN: 60 chars
- zh-TW: 25 chars
- zh-CN: 5 chars
- Other: 5 chars
- Numbers/Symbols: 5 chars
- Step 1: Unsupported (zh-CN 5% + other 5%) = 10% ≤ 10% ✓ Pass
- Step 2: Supported content = EN 60 + zh-TW 25 + numbers 5 = 90 chars
- zh-TW percentage: 25/90 = 27.8% ≥ 20%, use zh-TW prompt

### Example 5: Edge Case - Mixed with Numbers
```json
{
    "detected_language": "en",
    "language_composition": {
        "en_percent": 45.0,
        "zh_tw_percent": 15.0,
        "numbers_symbols_percent": 40.0
    },
    "decision_reason": "english_default",
    "will_process": true,
    "jd_preview": null
}
```
**Calculation Example**: 
- Total: 100 characters
- EN: 45 chars
- zh-TW: 15 chars
- Numbers/Symbols: 40 chars
- Other languages: 0 chars
- Supported content: 45 + 15 + 40 = 100 chars
- zh-TW percentage: 15/100 = 15% < 20%, use EN prompt

## Testing Requirements

### Unit Tests
1. Test pure English detection
2. Test pure Traditional Chinese detection
3. Test mixed EN/zh-TW with various ratios
4. Test Simplified Chinese rejection
5. Test other language rejection
6. Test edge cases (exactly 10% unsupported, exactly 20% zh-TW)

### Integration Tests
1. Verify LanguageDetected event is tracked for all requests
2. Verify jd_preview is only included for unsupported languages
3. Verify Application Insights query functionality

## Migration Plan

1. **Phase 1**: Implement new detection logic
2. **Phase 2**: Add LanguageDetected event tracking
3. **Phase 3**: Deprecate UnsupportedLanguageSkipped event (keep for backward compatibility)
4. **Phase 4**: Update dashboards to use new event

## Success Criteria

1. All keyword extraction requests have language detection tracked
2. Language distribution pie chart shows accurate data
3. Simplified Chinese content is properly rejected
4. 10% tolerance for special characters works correctly
5. Traditional Chinese threshold (20%) works as specified

## Appendix

### Related Documents
- [Language Detection Decision Tree](./language_detection_decision_tree.md)
- [Monitoring Implementation Guide](./MONITORING_SETUP.md)

### Work Items
- [PENDING_FEATURE_ID] Implement enhanced language detection logic
- [PENDING_TASK_ID] Add LanguageDetected event tracking
- [PENDING_TEST_ID] Create comprehensive test suite
- [PENDING_TASK_ID] Update Application Insights dashboards