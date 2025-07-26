# Resume Tailoring API Documentation

**Version**: 1.0  
**Last Updated**: 2025-07-10  
**Endpoint**: `/api/v1/tailor-resume`

## Overview

The Resume Tailoring API optimizes resumes based on job descriptions and gap analysis results. It uses AI to enhance resume content, integrate missing keywords naturally, and highlight strengths while maintaining a professional format.

### Key Features
- 🎯 AI-powered resume optimization
- 🔤 Flexible input format support (Bubble.io compatible)
- 📝 Plain text and HTML support
- 🌐 Multi-language support (English, Traditional Chinese)
- 🎨 Visual optimization markers
- 📊 Detailed optimization statistics

## API Endpoint

### Base URL
```
Production: https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume
Local: http://localhost:8000/api/v1/tailor-resume
```

### Method
`POST`

### Headers
```http
Content-Type: application/json
```

## Request Format

### Request Body Structure
```json
{
  "job_description": "string",
  "original_resume": "string",
  "gap_analysis": {
    "core_strengths": "string | array",
    "key_gaps": "string | array",
    "quick_improvements": "string | array",
    "covered_keywords": "string | array",
    "missing_keywords": "string | array"
  },
  "options": {
    "include_visual_markers": boolean,
    "language": "en | zh-TW"
  }
}
```

### Field Descriptions

#### Required Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `job_description` | string | Target job description | Min: 50 chars, Max: 10,000 chars |
| `original_resume` | string | Original resume content | Min: 100 chars, Max: 50,000 chars |
| `gap_analysis` | object | Gap analysis results | Required object |

#### Gap Analysis Fields

The API accepts **flexible input formats** for all gap analysis fields:

| Field | Accepted Formats | Description |
|-------|-----------------|-------------|
| `core_strengths` | Multi-line text, Array, HTML list | 3-5 identified strengths |
| `key_gaps` | Multi-line text, Array, HTML list | 3-5 identified gaps |
| `quick_improvements` | Multi-line text, Array, HTML list | 3-5 actionable improvements |
| `covered_keywords` | Comma/semicolon separated, Array | Keywords already in resume |
| `missing_keywords` | Comma/semicolon separated, Array | Keywords to be added |

#### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `options.include_visual_markers` | boolean | true | Include CSS classes for visual highlighting |
| `options.language` | string | "en" | Output language ("en" or "zh-TW") |

### Flexible Input Format Examples

#### Multi-line Text Format (Bubble.io Style)
```json
{
  "gap_analysis": {
    "core_strengths": "Strong Python programming skills\nMachine learning expertise\nProven track record",
    "key_gaps": "Limited cloud experience\nNo formal leadership roles\nMissing containerization skills",
    "quick_improvements": "Add AWS certification section\nHighlight team collaboration\nInclude Docker projects"
  }
}
```

#### Comma-Separated Keywords
```json
{
  "gap_analysis": {
    "covered_keywords": "Python, Machine Learning, Data Analysis",
    "missing_keywords": "AWS,Docker,Kubernetes,Senior,Leadership"
  }
}
```

#### Mixed Separators (Semicolon, Newline, etc.)
```json
{
  "gap_analysis": {
    "covered_keywords": "Python; Machine Learning\nData Analysis",
    "missing_keywords": "AWS;Docker,Kubernetes\nSenior;Leadership"
  }
}
```

#### HTML Bullet Points
```json
{
  "gap_analysis": {
    "core_strengths": "<ul><li>Strong Python skills</li><li>ML expertise</li></ul>"
  }
}
```

#### Array Format (Traditional)
```json
{
  "gap_analysis": {
    "core_strengths": ["Strong Python skills", "ML expertise"],
    "key_gaps": ["Cloud experience", "Leadership roles"]
  }
}
```

## Response Format

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "optimized_resume": "string",
    "applied_improvements": ["string"],
    "applied_improvements_html": "string",
    "optimization_stats": {
      "sections_modified": integer,
      "keywords_added": integer,
      "strengths_highlighted": integer,
      "placeholders_added": integer
    },
    "visual_markers": {
      "strength_count": integer,
      "keyword_count": integer,
      "placeholder_count": integer,
      "new_content_count": integer,
      "improvement_count": integer
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

### Error Response (200 OK - Bubble.io Compatible)
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": "Additional error details"
  }
}
```

### Response Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `optimized_resume` | string | HTML resume with optimizations and visual markers |
| `applied_improvements` | array | List of improvements applied by section |
| `applied_improvements_html` | string | HTML formatted list (`<ul>`) ready for display in Bubble.io |
| `optimization_stats` | object | Statistics about the optimization process |
| `visual_markers` | object | Count of different visual marker types applied |

### Visual Marker CSS Classes

When `include_visual_markers` is true, the optimized resume includes CSS classes:

| CSS Class | Purpose | Example |
|-----------|---------|---------|
| `opt-strength` | Highlighted strengths | `<span class="opt-strength">team leadership</span>` |
| `opt-keyword` | Added keywords | `<span class="opt-keyword">Docker</span>` |
| `opt-placeholder` | Metric placeholders | `<span class="opt-placeholder">[PERCENTAGE]</span>` |
| `opt-new` | New content sections | `<p class="opt-new">New summary paragraph</p>` |
| `opt-improvement` | Enhanced content | `<li class="opt-improvement">Improved bullet point</li>` |

## Complete Examples

### Example 1: Basic Resume Tailoring
```bash
curl -X POST "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are seeking a Senior Data Scientist with expertise in machine learning, Python, and cloud platforms. The ideal candidate should have 5+ years of experience in building ML pipelines and deploying models to production.",
    "original_resume": "<h1>John Doe</h1><p>Data Scientist with 4 years of experience</p><h2>Experience</h2><ul><li>Built predictive models using Python</li><li>Analyzed large datasets</li></ul>",
    "gap_analysis": {
      "core_strengths": "Strong Python skills\nMachine learning expertise\nData analysis experience",
      "key_gaps": "Limited cloud experience\nNo production deployment mentioned\nMissing senior-level positioning",
      "quick_improvements": "Add cloud platform experience\nHighlight production deployments\nEmphasize leadership roles",
      "covered_keywords": "Python, Machine Learning, Data Scientist",
      "missing_keywords": "Senior, Cloud, Pipeline, Production, Deployment"
    }
  }'
```

### Example 2: Bubble.io Integration Format
```javascript
// Bubble.io API Connector Configuration
{
  "name": "Tailor Resume",
  "method": "POST",
  "url": "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "job_description": "<jd>",
    "original_resume": "<resume>",
    "gap_analysis": {
      "core_strengths": "<core_strengths_text>",
      "key_gaps": "<key_gaps_text>",
      "quick_improvements": "<improvements_text>",
      "covered_keywords": "<covered_keywords_csv>",
      "missing_keywords": "<missing_keywords_csv>"
    },
    "options": {
      "include_visual_markers": true,
      "language": "en"
    }
  }
}
```

### Example 3: Chinese Language Support
```json
{
  "job_description": "我們正在尋找資深數據科學家，需要精通機器學習、Python和雲端平台。",
  "original_resume": "<h1>張三</h1><p>數據科學家，4年經驗</p>",
  "gap_analysis": {
    "core_strengths": "扎實的Python技能\n機器學習專業知識\n數據分析經驗",
    "key_gaps": "雲端經驗有限\n未提及生產部署\n缺少資深級別定位",
    "quick_improvements": "增加雲端平台經驗\n突出生產部署\n強調領導角色",
    "covered_keywords": "Python,機器學習,數據科學家",
    "missing_keywords": "資深,雲端,管道,生產,部署"
  },
  "options": {
    "language": "zh-TW"
  }
}
```

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_REQUEST` | Invalid input data | Check field formats and constraints |
| `TAILORING_ERROR` | Processing failed | Retry request or contact support |
| `VALIDATION_ERROR` | Input validation failed | Review minimum length requirements |
| `LLM_ERROR` | AI processing failed | Retry after a few seconds |

## Best Practices

### 1. Input Preparation
- Ensure job description is detailed (min 50 chars)
- Provide complete resume content (min 100 chars)
- Use any convenient format for gap analysis fields

### 2. Keyword Formatting
- Keywords can be separated by commas, semicolons, or newlines
- Mixed separators are automatically handled
- No need to pre-process or clean the input

### 3. Multi-line Text
- Line breaks are preserved and processed correctly
- HTML lists are automatically parsed
- Bullet points and numbering are removed during parsing

### 4. Error Handling
- Always check the `success` field first
- Error details are in the `error` object
- All responses return HTTP 200 (Bubble.io compatibility)

### 5. Visual Markers
- Use CSS to style the optimization markers
- Markers help users understand what was changed
- Can be disabled by setting `include_visual_markers: false`

## TinyMCE Integration for Bubble.io

### Overview

For Bubble.io users displaying the optimized resume in a TinyMCE Rich Text Editor, we provide a JavaScript handler that enables interactive editing of placeholder values (e.g., `[PERCENTAGE]`, `[AMOUNT]`).

### Features

- **Click-to-Edit**: Click on red-bordered placeholders to edit values
- **Smart Formatting**: Automatically adds appropriate units based on placeholder type
- **Mode Switching**: Handles TinyMCE's readonly/design mode transitions
- **Keyboard Shortcuts**: 
  - Enter: Save and finish editing
  - Escape: Cancel editing

### Installation

Add the following script to your Bubble.io page's HTML header:

```html
<script src="https://raw.githubusercontent.com/YuWenHao1212/azure_fastapi/main/docs/bubble_integration/tinymce_placeholder_handler_final.js"></script>
```

Or copy the content from: `/docs/bubble_integration/tinymce_placeholder_handler_final.js`

### Placeholder Types and Auto-Formatting

| Placeholder | User Input | Auto-Formatted Result |
|-------------|-----------|---------------------|
| `[PERCENTAGE]` | `30` | `30%` |
| `[AMOUNT]` | `5` | `$5` |
| `[TEAM SIZE]` | `10` | `10 people` |
| `[TIME PERIOD]` | `6` | `6 months` |
| `[USER COUNT]` | `5000` | `5.0K` |
| `[35M units]` | `50` | `50M units` |

### CSS Styling

The script applies the following CSS classes:

```css
.opt-placeholder {
    background-color: #fee2e2;
    border: 1px dashed #f87171;
    /* Clickable placeholder style */
}

.editing-placeholder {
    background-color: #fff;
    border: 2px solid #721c24;
    /* Active editing style */
}

.opt-improvement {
    border-bottom: 2px solid #28a745;
    /* Completed edit style */
}
```

### API Functions

```javascript
// Get current status
getPlaceholderStatus()
// Returns: { mode, placeholders, completed, hasClickedBefore }

// Test placeholder functionality
testPlaceholderClick()

// Reset first-click tracking (for testing)
resetFirstClick()

// Manually activate current placeholder
activateCurrentPlaceholder()
```

### Known Limitations

- First placeholder click may require a second click to start typing (TinyMCE iframe focus limitation)
- Works best with TinyMCE's standard readonly/design mode implementation

## Rate Limits

- **Requests per minute**: 10
- **Maximum request size**: 100KB
- **Timeout**: 60 seconds

## Support

For technical support or questions:
- GitHub Issues: [azure_fastapi/issues](https://github.com/YuWenHao1212/azure_fastapi/issues)
- Email: support@airesumeadvisor.com

---

*Last updated: 2025-07-11*  
*TinyMCE Integration added: 2025-07-11*