# Bubble.io Workflow 設定範例

## 🔄 完整的 Resume Tailoring 工作流程

### 1. Page Loaded 事件

```
Event: Page is loaded
Action: Run JavaScript
JavaScript Code: [複製 bubble_page_loaded_script.js 的內容]
```

### 2. 用戶輸入收集

假設您有以下輸入元件：
- `InputJobDescription` (Multiline Input)
- `InputOriginalResume` (Multiline Input)
- `ButtonTailorResume` (Button)

### 3. 主要 Tailoring 工作流程

```
Event: ButtonTailorResume is clicked

Action 1: Only when...
Condition: InputJobDescription's value count of characters > 200 AND InputOriginalResume's value count of characters > 200

Action 2: [API Connector] TailorResume
Parameters:
  code: [YOUR_FUNCTION_KEY]
  job_description: InputJobDescription's value
  original_resume: InputOriginalResume's value
  gap_analysis: Custom State GapAnalysisData
  options: Custom State TailoringOptions

Action 3: Run JavaScript (Only when step 2 is successful)
JavaScript Code:
```javascript
// 處理 API 回應
const apiResponse = {API_RESULT_REFERENCE};
const success = window.handleResumeTailoringResponse(apiResponse);

if (success) {
    console.log('✅ Resume tailoring completed successfully');
    
    // 顯示成功訊息
    const successContainer = document.getElementById('success-message-container');
    if (successContainer) {
        successContainer.innerHTML = `
            <div class="alert alert-success" role="alert">
                <strong>Success!</strong> Your resume has been optimized successfully.
            </div>
        `;
        
        // 3秒後隱藏成功訊息
        setTimeout(() => {
            successContainer.innerHTML = '';
        }, 3000);
    }
    
    // 滾動到結果區域
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
} else {
    console.error('❌ Failed to process resume tailoring response');
}
```

Action 4: Set State (Only when step 2 is successful)
```
State: OptimizationResults
Value: Result of step 2's data
```

Action 5: Show/Hide Elements
```
Show: GroupResults
Hide: GroupLoading
```

Action 6: Run JavaScript (Only when step 2 is not successful)
```javascript
// 處理錯誤
const error = {
    status: {HTTP_STATUS_CODE},
    message: {ERROR_MESSAGE}
};

window.handleAPIError(error, 'Resume Tailoring');
```
```

### 4. 準備 Gap Analysis 數據

創建一個 Custom State 叫 `GapAnalysisData`，類型為 Object：

```
Event: Page is loaded (After step 1)
Action: Set State
State: GapAnalysisData
Value: {
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

### 5. 準備 Tailoring Options

創建一個 Custom State 叫 `TailoringOptions`，類型為 Object：

```
Event: Page is loaded (After step 1)
Action: Set State
State: TailoringOptions
Value: {
  "include_visual_markers": true,
  "language": "en"
}
```

### 6. 清除和重置功能

```
Event: ButtonClear is clicked

Action 1: Set State
State: OptimizationResults
Value: empty

Action 2: Run JavaScript
```javascript
// 清除顯示
const containers = [
    'optimized-resume-container',
    'error-message-container', 
    'success-message-container'
];

containers.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.innerHTML = '';
    }
});

// 重置統計顯示
const stats = [
    'original-similarity',
    'optimized-similarity', 
    'similarity-improvement',
    'original-keyword-coverage',
    'optimized-keyword-coverage',
    'keyword-coverage-improvement',
    'keyword-count',
    'placeholder-count',
    'new-content-count'
];

stats.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = '0';
    }
});

console.log('🧹 Interface cleared successfully');
```

Action 3: Show/Hide Elements
```
Hide: GroupResults
Show: GroupInputs
```

### 7. 匯出功能

```
Event: ButtonExportClean is clicked

Action 1: Run JavaScript
```javascript
// 匯出清潔版本（無標記）
const optimizedResume = `{Current State OptimizationResults's optimized_resume}`;
if (optimizedResume) {
    const cleanHTML = window.cleanResumeHTML(optimizedResume);
    
    // 創建並下載檔案
    const blob = new Blob([cleanHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'optimized_resume_clean.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('📄 Clean resume exported successfully');
} else {
    console.warn('⚠️ No optimized resume to export');
}
```

Action 2: Run JavaScript (Alternative: Copy to clipboard)
```javascript
// 複製到剪貼板
const optimizedResume = `{Current State OptimizationResults's optimized_resume}`;
if (optimizedResume) {
    const cleanHTML = window.cleanResumeHTML(optimizedResume);
    navigator.clipboard.writeText(cleanHTML).then(() => {
        alert('Clean resume copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy to clipboard:', err);
    });
}
```

### 8. 印刷友好格式

```
Event: ButtonPrintPreview is clicked

Action 1: Run JavaScript
```javascript
// 開啟印刷預覽
const optimizedResume = `{Current State OptimizationResults's optimized_resume}`;
if (optimizedResume) {
    const printHTML = window.getPrintFriendlyHTML(optimizedResume);
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Optimized Resume - Print Preview</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                @media print { body { margin: 0; } }
            </style>
        </head>
        <body>
            ${printHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    
    // 自動開啟列印對話框
    printWindow.onload = function() {
        printWindow.print();
    };
    
    console.log('🖨️ Print preview opened');
} else {
    console.warn('⚠️ No optimized resume to print');
}
```

## 📱 所需的 UI 元件

### 輸入區域 (GroupInputs)
- `InputJobDescription` - Multiline Input
- `InputOriginalResume` - Multiline Input  
- `ButtonTailorResume` - Button
- `ButtonClear` - Button

### 結果區域 (GroupResults)
- `optimized-resume-container` - HTML Element (ID: optimized-resume-container)
- `ButtonExportClean` - Button
- `ButtonPrintPreview` - Button

### 統計顯示區域
- Text elements with IDs matching the statistics (见上面的 ID 列表)

### 訊息區域
- `success-message-container` - HTML Element (ID: success-message-container)
- `error-message-container` - HTML Element (ID: error-message-container)

### 載入區域 (GroupLoading)
- Loading spinner or progress indicator

---

**這個工作流程提供了完整的 Resume Tailoring 功能，包括 API 呼叫、結果顯示、錯誤處理和匯出功能！** 🚀