# Language Detection Decision Tree for Keyword Extraction

## Refined Language Detection Logic

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

### Detailed Rules:

1. **Unsupported Language Detection (First Check)**
   - If (Simplified Chinese + Japanese + Korean + Spanish + Other) > 10% → Unsupported
   - **Important**: Simplified Chinese (zh-CN) is considered unsupported
   - This allows up to 10% tolerance for brands, special terms, or noise

2. **Traditional Chinese Detection**
   - Count ONLY Traditional Chinese characters
   - Simplified Chinese does NOT count toward zh-TW
   - If Traditional Chinese ≥ 20% of supported content → Use zh-TW prompt
   - **Calculation**: zh-TW% = zh-TW chars / (EN + zh-TW + numbers/symbols) × 100
   - Denominator excludes other languages since they've been filtered in step 1

3. **English Detection**
   - If unsupported ≤ 10% AND zh-TW < 20% → Use EN prompt
   - This becomes the default for content that passes the checks

4. **Character Classification**
   ```
   Total Characters = EN + zh-TW + zh-CN + JA + KO + Other
   
   - English (EN): A-Z, a-z, common punctuation
   - Traditional Chinese (zh-TW): 繁體中文字符
   - Simplified Chinese (zh-CN): 简体中文字符 (NOT counted as zh-TW)
   - Japanese (JA): Hiragana, Katakana, Kanji
   - Korean (KO): Hangul characters
   - Other: Everything else (numbers, special symbols excluded)
   ```

## Detailed Decision Logic

### 1. Language Detection Phase
```
Input: job_description text
Process: SimpleLanguageDetector.detect_language()

Counts characters by type:
- Traditional Chinese characters
- English characters
- Simplified Chinese characters
- Other (Japanese, Korean, etc.)

Calculates percentages of each type
```

### 2. Updated Language Classification Rules

| Priority | Condition | Decision | Action |
|----------|-----------|----------|--------|
| 1 | Contains (zh-CN + ja + ko + es + other) > 10% of total | `other` | Skip LLM, Track with JD preview |
| 2 | zh-TW ≥ 20% of (EN + zh-TW + numbers/symbols) | `zh-TW` | Use zh-TW prompt |
| 3 | zh-TW < 20% of (EN + zh-TW + numbers/symbols) | `en` | Use EN prompt (default) |

**Note**: For statistics and pie charts, all unsupported languages are grouped as `other` for simplicity.

### Examples:

1. **Pure English with brand names**
   - Composition: EN=92%, Other=8% (brands like "Côte d'Ivoire", "François")
   - Decision: `en` (within 10% tolerance)

2. **Mixed EN/zh-TW**
   - Composition: EN=75%, zh-TW=25%
   - Step 1: No unsupported languages ✓
   - Step 2: zh-TW / (EN + zh-TW) = 25/100 = 25% ≥ 20%
   - Decision: `zh-TW`

3. **English with some Simplified Chinese**
   - Composition: EN=80%, zh-CN=20%
   - Decision: `other` (zh-CN 20% > 10%, considered unsupported)

4. **Mixed with Japanese**
   - Composition: EN=70%, zh-TW=15%, JA=15%
   - Decision: `unsupported` (JA > 10%)
   
5. **English with acceptable noise**
   - Composition: EN=85%, Other=10%, zh-TW=5%
   - Step 1: Unsupported 10% ≤ 10% ✓ Pass
   - Step 2: zh-TW / (EN + zh-TW) = 5/90 = 5.6% < 20%
   - Decision: `en`

### 3. Tracking Logic

#### For Supported Languages (en, zh-TW):
```yaml
Event: keyword_extraction_processing_time (metric)
Properties:
  - language: "en" or "zh-TW"
  - prompt_version: "1.4.0"
  - jd_length: <number>
  - keyword_count: <number>
```

#### For Unsupported Languages:
```yaml
Event: UnsupportedLanguageSkipped
Properties:
  - detected_language: "ja", "ko", "es", "other", etc.
  - jd_preview: <first 100 chars>
  - jd_length: <number>
  - requested_language: "auto", "en", "zh-TW"
  - processing_time_ms: <number>
```

## Unified Event Tracking for Easy Statistics

### Single Event for All Requests
```python
# ALL requests use the same LanguageDetected event
monitoring_service.track_event(
    "LanguageDetected",
    {
        "detected_language": "en" | "zh-TW" | "other",  # Only 3 categories
        "language_composition": {
            "en_percent": 75.5,
            "zh_tw_percent": 20.3,
            "zh_cn_percent": 2.1,
            "ja_percent": 1.5,
            "ko_percent": 0.0,
            "es_percent": 0.6,
            "other_percent": 0.0
        },
        "decision_reason": "...",
        "will_process": True/False,
        "jd_preview": "..." if detected_language == "other" else None
    }
)
```

### Easy Pie Chart Query
```kusto
// Simple language distribution pie chart
customEvents
| where name == "LanguageDetected"
| where timestamp > ago(7d)
| summarize count() by tostring(customDimensions.detected_language)
| render piechart

// Result will show:
// - en: X%
// - zh-TW: Y%
// - other: Z%
```

## Key Points to Implement

### 1. Enhanced Language Detection for Mixed Content
```python
# Current logic (simplified)
if zh_tw_percentage >= 20:
    return "zh-TW"
elif english_percentage > 0:
    return "en"
```

### 2. Comprehensive Language Tracking Implementation

```python
# Track ALL language detection results (new unified event)
monitoring_service.track_event(
    "LanguageDetected",
    {
        "detected_language": detected_language,  # "en", "zh-TW", "ja", "ko", "other"
        "language_composition": {
            "en_percent": 75.5,
            "zh_tw_percent": 20.3,
            "zh_cn_percent": 2.1,  # Track separately, NOT included in zh-TW
            "ja_percent": 1.5,
            "ko_percent": 0.0,
            "other_percent": 0.6
        },
        "decision_reason": decision_reason,  # See below
        "will_process": detected_language in ["en", "zh-TW"],
        "requested_language": "auto",  # User's language parameter
        "jd_length": 165,
        "jd_preview": jd_preview if detected_language not in ["en", "zh-TW"] else None
    }
)

# Decision reasons:
# - "zh_tw_dominant": zh-TW ≥ 20%
# - "english_dominant": EN ≥ 90%
# - "english_default": EN < 90% but no other supported language
# - "unsupported_content": Contains ≥ 5% unsupported languages
```

### Example Tracking Scenarios:

1. **English with technical terms**
   ```json
   {
     "detected_language": "en",
     "language_composition": {
       "en_percent": 91.2,
       "zh_tw_percent": 0,
       "other_percent": 8.8
     },
     "decision_reason": "english_dominant",
     "will_process": true,
     "jd_preview": null
   }
   ```

2. **Mixed EN/zh-TW**
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

3. **Unsupported language**
   ```json
   {
     "detected_language": "ja",
     "language_composition": {
       "en_percent": 40.0,
       "ja_percent": 60.0
     },
     "decision_reason": "unsupported_content",
     "will_process": false,
     "jd_preview": "DjangoとFastAPIで5年の経験を持つ..."
   }
   ```

### 3. Current Gaps to Fix

1. **Missing universal language tracking** - Only tracking unsupported languages with JD preview
2. **No composition details** - Not recording the actual percentages that led to the decision
3. **Limited visibility** - Can't see language distribution for successful requests easily

## Implementation Checklist

### Phase 1: Core Logic Updates
- [ ] Update language detection to properly separate zh-TW and zh-CN
- [ ] Implement 10% threshold for unsupported language rejection
- [ ] Remove specific English percentage check (use as default after checks)
- [ ] Ensure zh-TW ≥ 20% rule only counts Traditional Chinese

### Phase 2: Tracking Enhancements
- [ ] Implement unified `LanguageDetected` event for ALL requests
- [ ] Include detailed language composition percentages
- [ ] Add decision_reason field to explain the logic path
- [ ] Add jd_preview ONLY for unsupported languages

### Phase 3: Testing & Validation
- [ ] Test English with brand names (should pass with <10% other)
- [ ] Test zh-CN content (should NOT trigger zh-TW prompt)
- [ ] Test mixed content edge cases
- [ ] Verify Application Insights tracking

## Summary of Key Changes

1. **Simplified & Consistent Logic**
   - First check: Reject if (zh-CN + ja + ko + es + other) > 10%
   - Second check: Use zh-TW if Traditional Chinese ≥ 20%
   - Default: Use EN for all other cases
   - **10% tolerance** applies universally

2. **Clear Language Categories**
   - **Supported**: `en`, `zh-TW` (processed by LLM)
   - **Unsupported**: Everything else grouped as `other` (including zh-CN)
   - Simplified Chinese (zh-CN) is explicitly unsupported

3. **Unified Event Tracking**
   - Single `LanguageDetected` event for ALL requests
   - Only 3 values for `detected_language`: `en`, `zh-TW`, `other`
   - Easy to create pie charts and statistics
   - Detailed composition still tracked for debugging