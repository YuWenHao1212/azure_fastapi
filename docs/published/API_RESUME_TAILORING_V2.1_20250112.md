# Resume Tailoring API Documentation v2.1

**Version**: 2.1  
**Last Updated**: 2025-01-12  
**Endpoint**: `/api/v1/tailor-resume`

## 🚀 Version 2.1 Changes

- 📋 **Simplified Response Structure**: Removed redundant fields based on user feedback
- 🎯 **Clearer Field Names**: Shorter, more intuitive naming
- ✂️ **Removed Duplicates**: Eliminated overlap between `optimization_stats` and `visual_markers`
- 📊 **Enhanced Coverage Details**: Added missed keywords lists

## API Endpoint

### Base URL (Azure Function App)
```
Production: https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume?code=[YOUR_FUNCTION_KEY]
```

### Authentication
- **Method**: URL Parameter
- **Parameter**: `code`
- **Value**: Azure Function Key
- **Example**: `?code=[YOUR_FUNCTION_KEY]`

### HTTP Method
`POST`

### Headers
```http
Content-Type: application/json
```

## Request Format

### Complete Request Structure
```json
{
  "job_description": "string (HTML/Text, min 200 chars)",
  "original_resume": "string (HTML/Text, min 200 chars)",
  "gap_analysis": {
    "core_strengths": ["string", "string", ...],
    "key_gaps": ["string", "string", ...],
    "quick_improvements": ["string", "string", ...],
    "covered_keywords": ["string", "string", ...],
    "missing_keywords": ["string", "string", ...]
  },
  "options": {
    "include_visual_markers": true,
    "language": "en"
  }
}
```

### Field Descriptions

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `job_description` | string | ✅ | Target job description (HTML or text) | Min: 200 chars |
| `original_resume` | string | ✅ | Original resume content (HTML or text) | Min: 200 chars |
| `gap_analysis` | object | ✅ | Structured gap analysis data | See below |
| `options` | object | ✅ | Tailoring options | See below |

#### Gap Analysis Object
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `core_strengths` | array[string] | ✅ | 3-5 identified strengths |
| `key_gaps` | array[string] | ✅ | 3-5 identified gaps |
| `quick_improvements` | array[string] | ✅ | 3-5 improvement suggestions |
| `covered_keywords` | array[string] | ✅ | Keywords already in resume |
| `missing_keywords` | array[string] | ✅ | Keywords to be added |

#### Options Object
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `include_visual_markers` | boolean | ✅ | true | Enable visual marking system |
| `language` | string | ✅ | "en" | Language code (en, zh-TW) |

## Response Format

### Simplified Success Response Structure (v2.1)
```json
{
  "success": true,
  "data": {
    "resume": "string (HTML with enhanced markers)",
    "improvements": "string (HTML formatted improvement list)",
    "markers": {
      "keyword_new": "number",        // 新增的關鍵字數量 (原本沒有的)
      "keyword_existing": "number",   // 原有的關鍵字數量 (加強標記)
      "placeholder": "number",        // 佔位符數量 [PERCENTAGE] 等
      "new_section": "number",        // 新增區塊數量 (opt-new)
      "modified": "number"            // 修改內容數量 (opt-modified)
    },
    "similarity": {
      "before": "number (0-100)",
      "after": "number (0-100)",
      "improvement": "number"
    },
    "coverage": {
      "before": {
        "percentage": "number (0-100)",
        "covered": ["string", ...],
        "missed": ["string", ...]
      },
      "after": {
        "percentage": "number (0-100)",
        "covered": ["string", ...],
        "missed": ["string", ...]
      },
      "improvement": "number",
      "newly_added": ["string", ...]
    }
  },
  "error": {
    "has_error": false,
    "code": "",
    "message": "",
    "details": ""
  },
  "warning": {
    "has_warning": false,
    "message": ""
  },
  "timestamp": "2025-01-12T13:41:55.123456"
}
```

## Field Changes Summary (v2.1)

### Renamed Fields
- `optimized_resume` → `resume`
- `applied_improvements_html` → `improvements`
- `visual_markers` → `markers`
- `index_calculation` → Split into `similarity` and `coverage`

### Removed Fields
- ~~`applied_improvements`~~ (array version removed, keep HTML only)
- ~~`optimization_stats`~~ (merged into `markers`)
- ~~`strengths_highlighted`~~ (no longer used in v1.1.0)
- ~~`keywords_analysis`~~ (redundant with `coverage`)
- ~~`total_keywords`~~ (not needed)
- ~~`covered_count`~~ (percentage is enough)

### Added Fields
- `coverage.before.missed` (keywords not covered in original)
- `coverage.after.missed` (keywords still not covered after optimization)

### Simplified Names
- `keyword_count` → `keyword_new` (澄清：這是新增的關鍵字數量)
- `keyword_existing_count` → `keyword_existing`
- `placeholder_count` → `placeholder`
- `new_content_count` → `new_section`
- `modified_content_count` → `modified`
- `original_similarity` → `before`
- `optimized_similarity` → `after`

## Enhanced Visual Marking System

### Three-Level Hierarchy

#### 1. Section Level - `opt-new`
- **Purpose**: Entirely new sections added
- **Example**: New "Summary" or "Projects" section
- **CSS Class**: `class="opt-new"`

#### 2. Content Level - `opt-modified`  
- **Purpose**: Modified existing content
- **Example**: Rewritten work experience bullets
- **CSS Class**: `class="opt-modified"`
- **Note**: v1.0.0 may still return `opt-strength` (will be phased out)

#### 3. Data Level - `opt-placeholder`
- **Purpose**: Placeholders for specific data
- **Example**: `[PERCENTAGE]`, `[NUMBER]` placeholders
- **CSS Class**: `class="opt-placeholder"`

### Keyword Marking (Python-Based)

#### New Keywords - `opt-keyword`
- **Purpose**: Keywords not in original resume
- **Accuracy**: 100% precise matching
- **CSS Class**: `class="opt-keyword"`
- **Example**: `<span class="opt-keyword">Machine Learning</span>`

#### Existing Keywords - `opt-keyword-existing`
- **Purpose**: Keywords already in original resume
- **Features**: Case correction for protected terms
- **CSS Class**: `class="opt-keyword-existing"` 
- **Example**: `<span class="opt-keyword-existing">JavaScript</span>`

## Example Request

```json
{
  "job_description": "<h2>Senior Software Engineer - Data Science Platform</h2><p>We are seeking a Senior Software Engineer to join our Data Science Platform team. The ideal candidate will have extensive experience in Python development, machine learning frameworks, and cloud infrastructure.</p>",
  "original_resume": "<h1>Alex Chen</h1><p>Software Developer with 4 years of experience in web development and data analysis</p><h3>Work Experience</h3><h4>Software Developer - TechCorp Inc. (2020-2024)</h4><ul><li>Developed web applications using Python and JavaScript frameworks</li></ul>",
  "gap_analysis": {
    "core_strengths": [
      "Solid Python programming foundation with 4 years of experience",
      "Proven ability to work with data analysis and processing",
      "Experience in full-stack development and API creation",
      "Strong collaboration and teamwork skills"
    ],
    "key_gaps": [
      "Limited experience with machine learning frameworks",
      "Missing cloud platform expertise (AWS, Azure, GCP)",
      "No experience with containerization technologies"
    ],
    "quick_improvements": [
      "Highlight data analysis work and quantify achievements",
      "Emphasize Python experience and technical problem-solving",
      "Add any cloud or ML coursework from university"
    ],
    "covered_keywords": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git"],
    "missing_keywords": ["Machine Learning", "AWS", "Docker", "Kubernetes", "Senior", "Cloud"]
  },
  "options": {
    "include_visual_markers": true,
    "language": "en"
  }
}
```

## Example Response (v2.1)

```json
{
  "success": true,
  "data": {
    "resume": "<h1>Alex Chen</h1><p>Email: alex.chen@email.com | Phone: (555) 123-4567</p><p class=\"opt-new\">Senior Software Engineer with 4+ years of experience in <span class=\"opt-keyword-existing\">Python</span> development, data analysis, and full-stack web development. Proven ability to create scalable APIs and analyze complex datasets to drive insights. Currently expanding expertise in <span class=\"opt-keyword\">machine learning</span> and <span class=\"opt-keyword\">cloud platforms</span> to deliver innovative solutions.</p>",
    "improvements": "<ul><li>[Section: Summary] Created new professional summary highlighting Python expertise and cloud platforms.</li><li>[Section: Work Experience] Converted bullets to STAR format with quantification placeholders.</li><li>[Section: Skills] Added missing technical keywords and reorganized categories.</li></ul>",
    "markers": {
      "keyword_new": 8,
      "keyword_existing": 3,
      "placeholder": 6,
      "new_section": 1,
      "modified": 0
    },
    "similarity": {
      "before": 64,
      "after": 88,
      "improvement": 24
    },
    "coverage": {
      "before": {
        "percentage": 29,
        "covered": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git"],
        "missed": ["Machine Learning", "AWS", "Docker", "Kubernetes", "Senior", "Cloud"]
      },
      "after": {
        "percentage": 90,
        "covered": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git", "Machine Learning", "AWS", "Docker", "Kubernetes", "Senior", "Cloud"],
        "missed": ["Kubernetes", "Senior"]
      },
      "improvement": 61,
      "newly_added": ["Machine Learning", "AWS", "Docker", "Cloud"]
    }
  },
  "error": {
    "has_error": false,
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-01-12T13:41:55.123456"
}
```

## Error Handling

### Common Error Codes
| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request - Invalid input format | Check request structure |
| 401 | Unauthorized - Invalid Function Key | Verify Function Key |
| 422 | Validation Error - Input constraints not met | Check field constraints |
| 500 | Internal Server Error | Retry request |
| 504 | Gateway Timeout | Request processing, retry later |

### Error Response Structure
```json
{
  "success": false,
  "data": null,
  "error": {
    "has_error": true,
    "code": "VALIDATION_ERROR",
    "message": "job_description must be at least 200 characters",
    "details": "Received 150 characters, minimum required is 200"
  },
  "timestamp": "2025-01-12T13:41:55.123456"
}
```

## Migration Guide (v2.0 → v2.1)

### Field Mapping
```javascript
// v2.0 → v2.1
data.optimized_resume → data.resume
data.applied_improvements_html → data.improvements
data.visual_markers → data.markers
data.visual_markers.keyword_count → data.markers.keyword_new
data.visual_markers.keyword_existing_count → data.markers.keyword_existing
data.index_calculation.original_similarity → data.similarity.before
data.index_calculation.optimized_similarity → data.similarity.after
data.keywords_analysis.coverage_details.original → data.coverage.before
data.keywords_analysis.coverage_details.optimized → data.coverage.after
```

### Removed Fields
- No longer available: `applied_improvements` (array), `optimization_stats`, `keywords_analysis`
- Use simplified structure instead

## Performance Metrics

### Typical Response Times
- **Cold Start**: 30-60 seconds (first request)
- **Warm Request**: 20-35 seconds
- **Average Processing**: 25-30 seconds

### Optimization Results
- **Similarity Improvement**: 20-35% average increase
- **Keyword Coverage**: 50-70% average increase  
- **New Keywords Added**: 10-15 keywords typically
- **Visual Markers**: 25-40 markers per resume

---

**Version 2.1 provides a cleaner, more intuitive API response while maintaining all essential functionality.** 🚀