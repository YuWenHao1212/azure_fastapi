# Resume Tailoring API Documentation v2.0

**Version**: 2.0  
**Last Updated**: 2025-07-12  
**Endpoint**: `/api/v1/tailor-resume`

## 🚀 Version 2.0 New Features

- ✨ **Enhanced Keyword Marking**: Python-based precise keyword marking with 100% accuracy
- 📊 **Index Calculation Integration**: Similarity scoring and keyword coverage analysis
- 🏷️ **Three-Level Marking System**: opt-new, opt-modified, opt-placeholder hierarchy
- 🤖 **LLM v1.1.0**: Aggressive optimization strategy with transparent marking
- 🎯 **Advanced Analytics**: Comprehensive optimization statistics and insights

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

### Success Response Structure
```json
{  <- WenHao: 許多命名都太長了 請make it short and easy understand
  "success": true,
  "data": {
    "optimized_resume": "string (HTML with enhanced markers)",
    "applied_improvements": ["string", "string", ...],  <- WenHao: 取消這個fields
    "applied_improvements_html": "string  (HTML formatted)",
    "optimization_stats": {<- WenHao: 這部份和 visual_markers 是一樣的
      "sections_modified": "number",
      "keywords_added": "number",
      "strengths_highlighted": "number",  <- WenHao: 我們現在LLM prompt 應該沒有 strentg 了吧?   
      "placeholders_added": "number"
    },
    "visual_markers": {
      "keyword_count": "number",
      "keyword_existing_count": "number", 
      "placeholder_count": "number",
      "new_content_count": "number",
      "modified_content_count": "number"
    },
    "index_calculation": {
      "original_similarity": "number (0-100)",
      "optimized_similarity": "number (0-100)",
      "similarity_improvement": "number",
      "original_keyword_coverage": "number (0-100)",
      "optimized_keyword_coverage": "number (0-100)",
      "keyword_coverage_improvement": "number",
      "new_keywords_added": ["string", "string", ...]
      <- WenHao: optimized keywords covered list and missed list                        
    },
    "keywords_analysis": {<- WenHao: 取消這個fields
      "original_keywords": ["string", "string", ...],
      "new_keywords": ["string", "string", ...],
      "total_keywords": "number",  <- WenHao: 取消這個fields
      "coverage_details": {
        "original": {
          "total_keywords": "number",  <- WenHao: 取消這個fields
          "covered_count": "number",   <- WenHao: 取消這個fields
          "coverage_percentage": "number",<- WenHao: 取消這個fields
          "covered_keywords": ["string", ...]
                                             <- WenHao: 加上 keywords missed 
        },
        "optimized": {
          "total_keywords": "number", <- WenHao: 取消這個fields
          "covered_count": "number",<- WenHao: 取消這個fields
          "coverage_percentage": "number",<- WenHao: 取消這個fields
          "covered_keywords": ["string", ...]
                                <- WenHao: 加上 keywords missed
        }
      }
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
  "timestamp": "2025-07-12T13:41:55.123456"
}
```

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

## Index Calculation Metrics

### Similarity Analysis
- **Original Similarity**: Document similarity before optimization (0-100%)
- **Optimized Similarity**: Document similarity after optimization (0-100%)
- **Similarity Improvement**: Absolute improvement in percentage points

### Keyword Coverage Analysis
- **Original Coverage**: Keywords covered before optimization (0-100%)
- **Optimized Coverage**: Keywords covered after optimization (0-100%)  
- **Coverage Improvement**: Absolute improvement in percentage points
- **New Keywords Added**: List of specific keywords integrated

## Example Request

```json
{
  "job_description": "<h2>Senior Software Engineer - Data Science Platform</h2><p>We are seeking a Senior Software Engineer to join our Data Science Platform team. The ideal candidate will have extensive experience in Python development, machine learning frameworks, and cloud infrastructure. You will be responsible for building scalable data pipelines, implementing ML models in production, and collaborating with data scientists to deliver insights.</p><h3>Key Requirements:</h3><ul><li>5+ years of experience in Python development</li><li>Strong knowledge of machine learning libraries (scikit-learn, TensorFlow, PyTorch)</li><li>Experience with cloud platforms (AWS, Azure, GCP)</li><li>Proficiency in SQL and database optimization</li><li>Experience with containerization (Docker, Kubernetes)</li><li>Knowledge of data visualization tools (Tableau, Power BI)</li><li>Strong communication and teamwork skills</li></ul>",
  "original_resume": "<h1>Alex Chen</h1><p>Email: alex.chen@email.com | Phone: (555) 123-4567</p><p>Software Developer with 4 years of experience in web development and data analysis</p><h3>Work Experience</h3><h4>Software Developer - TechCorp Inc. (2020-2024)</h4><ul><li>Developed web applications using Python and JavaScript frameworks</li><li>Analyzed user behavior data to improve application performance</li><li>Collaborated with cross-functional teams to deliver features on time</li><li>Maintained and optimized existing codebase for better performance</li></ul><h3>Skills</h3><ul><li>Programming Languages: Python, JavaScript, HTML, CSS</li><li>Frameworks: Flask, React, Node.js</li><li>Databases: MySQL, PostgreSQL</li><li>Tools: Git, Jenkins, Linux</li></ul>",
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
      "No experience with containerization technologies",
      "Lack of big data and MLOps knowledge",
      "Missing data visualization tools experience"
    ],
    "quick_improvements": [
      "Highlight data analysis work and quantify achievements",
      "Emphasize Python experience and technical problem-solving",
      "Add any cloud or ML coursework from university",
      "Mention any personal projects involving data or analytics",
      "Restructure skills section to emphasize relevant technologies"
    ],
    "covered_keywords": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git"],
    "missing_keywords": [
      "Machine Learning", "scikit-learn", "TensorFlow", "PyTorch",
      "AWS", "Azure", "GCP", "Docker", "Kubernetes", 
      "Tableau", "Power BI", "SQL", "Spark", "MLOps", "FastAPI"
    ]
  },
  "options": {
    "include_visual_markers": true,
    "language": "en"
  }
}
```

## Example Response (Partial)

```json
{
  "success": true,
  "data": {
    "optimized_resume": "<h1>Alex Chen</h1><p>Email: alex.chen@email.com | Phone: (555) 123-4567</p><p class=\"opt-new\">Senior Software Engineer with 4+ years of experience in <span class=\"opt-keyword-existing\">Python</span> development, data analysis, and full-stack web development. Proven ability to create scalable APIs and analyze complex datasets to drive insights. Currently expanding expertise in <span class=\"opt-keyword\">machine learning</span> and <span class=\"opt-keyword\">cloud platforms</span> to deliver innovative solutions.</p><h3>Work Experience</h3><h4>Software Developer - TechCorp Inc. (2020-2024)</h4><ul><li>Designed and developed web applications using <span class=\"opt-keyword\">Python</span> and <span class=\"opt-keyword\">JavaScript</span>, improving user engagement by <span class=\"opt-placeholder\">[PERCENTAGE]</span>.</li><li>Conducted data analysis on user behavior, identifying key trends that enhanced application performance by <span class=\"opt-placeholder\">[PERCENTAGE]</span>.</li><li><span class=\"opt-strength\">Collaborated with cross-functional teams</span> to deliver new features, ensuring on-time delivery for <span class=\"opt-placeholder\">[NUMBER]</span> projects.</li></ul>",
    "applied_improvements": [
      "[Section: Summary] Created new professional summary highlighting Python expertise, data analysis experience, and expanding skills in machine learning and cloud platforms.",
      "[Section: Work Experience] Converted all bullets to STAR format, emphasizing collaboration and technical problem-solving. Added placeholders for quantification.",
      "[Section: Skills] Reorganized skills into relevant categories, added missing keywords such as 'Scikit-learn', 'TensorFlow', 'AWS', 'Docker', and 'Tableau'."
    ],
    "optimization_stats": {
      "sections_modified": 5,
      "keywords_added": 13,
      "strengths_highlighted": 1,
      "placeholders_added": 6
    },
    "visual_markers": {
      "keyword_count": 29,
      "keyword_existing_count": 3,
      "placeholder_count": 6,
      "new_content_count": 1,
      "modified_content_count": 0
    },
    "index_calculation": {
      "original_similarity": 64,
      "optimized_similarity": 88,
      "similarity_improvement": 24,
      "original_keyword_coverage": 29,
      "optimized_keyword_coverage": 90,
      "keyword_coverage_improvement": 61,
      "new_keywords_added": [
        "Machine Learning", "scikit-learn", "TensorFlow", "PyTorch",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", 
        "Tableau", "Power BI", "SQL", "Spark"
      ]
    },
    "keywords_analysis": {
      "original_keywords": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git"],
      "new_keywords": ["Machine Learning", "scikit-learn", "TensorFlow", "PyTorch", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Tableau", "Power BI", "SQL", "Spark"],
      "total_keywords": 21,
      "coverage_details": {
        "original": {
          "total_keywords": 21,
          "covered_count": 6,
          "coverage_percentage": 29,
          "covered_keywords": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git"]
        },
        "optimized": {
          "total_keywords": 21,
          "covered_count": 19,
          "coverage_percentage": 90,
          "covered_keywords": ["Python", "JavaScript", "MySQL", "PostgreSQL", "Flask", "Git", "Machine Learning", "scikit-learn", "TensorFlow", "PyTorch", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Tableau", "Power BI", "SQL", "Spark"]
        }
      }
    }
  },
  "error": {
    "has_error": false,
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-07-12T13:41:55.123456"
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
  "timestamp": "2025-07-12T13:41:55.123456"
}
```

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

## Best Practices

### Input Optimization
1. **Job Description**: Include comprehensive requirements and preferred qualifications
2. **Original Resume**: Provide complete resume with all sections
3. **Gap Analysis**: Use specific, actionable insights
4. **Keywords**: Include both technical and soft skills

### Response Processing
1. **HTML Display**: Use provided CSS classes for optimal visual presentation
2. **Placeholders**: Guide users to fill in specific metrics and numbers
3. **Statistics**: Display Index Calculation results for transparency
4. **Export Options**: Offer both marked and clean versions

### Error Recovery
1. **Timeout Handling**: Implement retry logic with exponential backoff
2. **Validation**: Pre-validate input lengths and formats
3. **Fallback**: Provide graceful degradation for failed requests

---

**Version 2.0 delivers significantly enhanced capabilities with precise keyword marking, comprehensive analytics, and transparent optimization insights.** 🚀