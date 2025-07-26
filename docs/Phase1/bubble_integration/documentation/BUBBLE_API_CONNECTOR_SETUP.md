# Bubble.io API Connector 設定指南

## 📋 目錄
1. [API Connector 基本設定](#api-connector-基本設定)
2. [認證設定](#認證設定)
3. [API Call 設定](#api-call-設定)
4. [Data Types 設定](#data-types-設定)
5. [測試與驗證](#測試與驗證)
6. [錯誤處理](#錯誤處理)

---

## API Connector 基本設定

### 1. 新增 API Connector
```
Plugin Name: AIResumeAdvisor FastAPI
Description: Enhanced resume tailoring with keyword marking and index calculation
API Root URL: https://airesumeadvisor-fastapi.azurewebsites.net/api/v1
```

### 2. 認證設定
```
Authentication: API Key Authentication
Key name: code
Key value: [YOUR_FUNCTION_KEY]
Add to: URL Parameters (Query String)
```

---

## API Call 設定

### 1. Health Check API Call

**基本設定:**
```
Name: HealthCheck
Use as: Action
HTTP Method: GET
Endpoint: /health
```

**Parameters:** 
```
code: text (自動填入 Function Key)
```

**Headers:**
```
Content-Type: application/json
```

**Return Data Type:**
```javascript
{
  "success": boolean,
  "data": {
    "service": text,
    "status": text,
    "version": text,
    "features": {
      "2_round_intersection": boolean,
      "azure_openai_integration": boolean,
      "parallel_processing": boolean,
      "caching": boolean,
      "bubble_io_compatible": boolean,
      "bilingual_support": boolean
    }
  }
}
```

### 2. Resume Tailoring API Call

**基本設定:**
```
Name: TailorResume
Use as: Action
HTTP Method: POST
Endpoint: /tailor-resume
```

**Parameters:**
```javascript
code: text (自動填入 Function Key)
job_description: text (required)
original_resume: text (required)
gap_analysis: object (required)
options: object (required)
```

**Headers:**
```
Content-Type: application/json
```

**Body Type:** JSON

**Body:**
```json
{
  "job_description": "<job_description>",
  "original_resume": "<original_resume>",
  "gap_analysis": <gap_analysis>,
  "options": <options>
}
```

**Return Data Type:**
```javascript
{
  "success": boolean,
  "data": {
    "optimized_resume": text,
    "applied_improvements": list of text,
    "applied_improvements_html": text,
    "optimization_stats": {
      "sections_modified": number,
      "keywords_added": number,
      "strengths_highlighted": number,
      "placeholders_added": number
    },
    "visual_markers": {
      "keyword_count": number,
      "keyword_existing_count": number,
      "placeholder_count": number,
      "new_content_count": number,
      "modified_content_count": number
    },
    "index_calculation": {
      "original_similarity": number,
      "optimized_similarity": number,
      "similarity_improvement": number,
      "original_keyword_coverage": number,
      "optimized_keyword_coverage": number,
      "keyword_coverage_improvement": number,
      "new_keywords_added": list of text
    },
    "keywords_analysis": {
      "original_keywords": list of text,
      "new_keywords": list of text,
      "total_keywords": number,
      "coverage_details": object
    }
  },
  "error": {
    "has_error": boolean,
    "code": text,
    "message": text,
    "details": text
  },
  "warning": {
    "has_warning": boolean,
    "message": text
  },
  "timestamp": text
}
```

---

## Data Types 設定

### 1. Gap Analysis Input
```javascript
core_strengths: list of text
key_gaps: list of text
quick_improvements: list of text
covered_keywords: list of text
missing_keywords: list of text
```

### 2. Tailoring Options
```javascript
include_visual_markers: boolean
language: text
```

### 3. Index Calculation Result
```javascript
original_similarity: number
optimized_similarity: number
similarity_improvement: number
original_keyword_coverage: number
optimized_keyword_coverage: number
keyword_coverage_improvement: number
new_keywords_added: list of text
```

### 4. Keywords Analysis
```javascript
original_keywords: list of text
new_keywords: list of text
total_keywords: number
coverage_details: text
```

### 5. Visual Markers
```javascript
keyword_count: number
keyword_existing_count: number
placeholder_count: number
new_content_count: number
modified_content_count: number
```

### 6. Optimization Stats
```javascript
sections_modified: number
keywords_added: number
strengths_highlighted: number
placeholders_added: number
```

---

## 測試設定

### 測試用 Gap Analysis 數據
```json
{
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
}
```

### 測試用 Options 數據
```json
{
  "include_visual_markers": true,
  "language": "en"
}
```

### 測試用 Job Description (長度 > 200 字元)
```html
<h2>Senior Software Engineer - Data Science Platform</h2>
<p>We are seeking a Senior Software Engineer to join our Data Science Platform team. 
The ideal candidate will have extensive experience in Python development, machine learning frameworks, 
and cloud infrastructure. You will be responsible for building scalable data pipelines, 
implementing ML models in production, and collaborating with data scientists to deliver insights.</p>

<h3>Key Requirements:</h3>
<ul>
    <li>5+ years of experience in Python development</li>
    <li>Strong knowledge of machine learning libraries (scikit-learn, TensorFlow, PyTorch)</li>
    <li>Experience with cloud platforms (AWS, Azure, GCP)</li>
    <li>Proficiency in SQL and database optimization</li>
    <li>Experience with containerization (Docker, Kubernetes)</li>
    <li>Knowledge of data visualization tools (Tableau, Power BI)</li>
    <li>Strong communication and teamwork skills</li>
</ul>

<h3>Preferred Qualifications:</h3>
<ul>
    <li>Experience with big data technologies (Spark, Hadoop)</li>
    <li>Knowledge of MLOps practices and tools</li>
    <li>Experience with API development using FastAPI or Flask</li>
    <li>Understanding of DevOps practices and CI/CD pipelines</li>
</ul>
```

### 測試用 Original Resume (長度 > 200 字元)
```html
<h1>Alex Chen</h1>
<p>Email: alex.chen@email.com | Phone: (555) 123-4567</p>
<p>Software Developer with 4 years of experience in web development and data analysis</p>

<h3>Work Experience</h3>
<h4>Software Developer - TechCorp Inc. (2020-2024)</h4>
<ul>
    <li>Developed web applications using Python and JavaScript frameworks</li>
    <li>Analyzed user behavior data to improve application performance</li>
    <li>Collaborated with cross-functional teams to deliver features on time</li>
    <li>Maintained and optimized existing codebase for better performance</li>
</ul>

<h4>Junior Developer - StartupXYZ (2019-2020)</h4>
<ul>
    <li>Built REST APIs using Python Flask framework</li>
    <li>Implemented data collection and processing scripts</li>
    <li>Participated in code reviews and agile development processes</li>
</ul>

<h3>Skills</h3>
<ul>
    <li>Programming Languages: Python, JavaScript, HTML, CSS</li>
    <li>Frameworks: Flask, React, Node.js</li>
    <li>Databases: MySQL, PostgreSQL</li>
    <li>Tools: Git, Jenkins, Linux</li>
</ul>

<h3>Education</h3>
<p>Bachelor of Science in Computer Science<br>
State University (2015-2019)</p>
```

---

## 錯誤處理設定

### 常見錯誤代碼處理
```javascript
// 在 Bubble 工作流程中檢查錯誤
When API call returns:
  If success = false:
    Show error message: API call's error message
  If has_warning = true:
    Show warning: API call's warning message
  Else:
    Continue with success flow
```

### 超時處理
```
Timeout: 180 seconds (3 minutes)
Retry policy: 1 retry with 5 second delay
```

---

## 使用範例

### 在 Bubble 工作流程中使用

1. **觸發條件**: Button is clicked
2. **動作**: TailorResume API Call
3. **參數設定**:
   ```
   job_description: Input JobDescription's value
   original_resume: Input OriginalResume's value
   gap_analysis: Custom State GapAnalysis
   options: Custom State TailoringOptions
   ```
4. **成功處理**: 
   ```
   Set element's text to: Result of step 2's optimized_resume
   Set state IndexResult to: Result of step 2's index_calculation
   ```

### HTML 顯示設定

在 HTML Element 中顯示優化結果:
```html
<!-- 確保包含 TinyMCE 樣式 -->
<style>
.opt-new { background-color: #e8f5e8; border-left: 4px solid #4CAF50; }
.opt-modified { background-color: #fff3cd; border-left: 4px solid #ffc107; }
.opt-placeholder { background-color: #f8d7da; border-left: 4px solid #dc3545; }
.opt-keyword { background-color: #d1ecf1; color: #0c5460; font-weight: bold; }
.opt-keyword-existing { background-color: #d4edda; color: #155724; font-weight: bold; }
</style>

<!-- 顯示優化後的履歷 -->
<div class="resume-container">
  [API Result's optimized_resume]
</div>
```

---

## 完成檢查清單

在設定完成後，請確認以下項目：

- [ ] API Connector 基本資訊正確
- [ ] Function Key 認證設定完成
- [ ] Health Check API Call 測試成功
- [ ] Resume Tailoring API Call 設定完成
- [ ] 所有 Data Types 已建立
- [ ] 測試數據可以正常呼叫 API
- [ ] 錯誤處理機制設定完成
- [ ] HTML 樣式已準備好顯示標記

---

**設定完成時間**: 預計 15-20 分鐘  
**測試驗證時間**: 預計 10-15 分鐘  
**總計時間**: 約 30 分鐘

等您休息回來後，我們就可以直接開始整合和調適！🚀