# Bubble.io 完整整合指南 - API v2.0

**版本**: 3.0  
**最後更新**: 2025-07-12  
**API 版本**: v2.0  
**狀態**: ✅ **測試通過 - 可立即使用**

## 🚀 快速開始

### 📋 前置準備檢查清單

- [ ] Azure Function App 可正常存取
- [ ] API Key 可用：`[YOUR_FUNCTION_KEY]`
- [ ] Bubble.io 專案已建立
- [ ] 對 API Connector 和 Workflow 有基本了解

## 🔗 Step 1: API Connector 設定

### 在 Bubble Editor 中：

1. **前往 Plugins → API Connector**
2. **新增 API**：
   - **Name**: `Resume Tailoring API v2`
   - **Use as**: Action

3. **填入以下設定**：

```yaml
# API 基本資訊
Name: TailorResume
Data type: JSON
Use as: Action

# API 呼叫設定
Method: POST
URL: https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume

# 認證設定 (重要！)
Authentication: None (we use URL parameter)

# Headers
Content-Type: application/json

# Parameters (URL Parameters)
code: [YOUR_FUNCTION_KEY]
  (Type: text, checked ✓)

# Body (JSON)
{
  "job_description": "<job_description>",
  "original_resume": "<original_resume>",
  "gap_analysis": <gap_analysis>,
  "options": <options>
}
```

### 參數對應：

| Bubble Parameter | Type | Example Value |
|-----------------|------|---------------|
| `job_description` | text | `Dynamic: InputJobDescription's value` |
| `original_resume` | text | `Dynamic: InputOriginalResume's value` |
| `gap_analysis` | object | `Dynamic: State GapAnalysisData` |
| `options` | object | `Dynamic: State TailoringOptions` |

## 📱 Step 2: 前端 UI 設計

### 必要元件清單：

```yaml
# 輸入區域
- InputJobDescription (Multiline Input, min height: 150px)
- InputOriginalResume (Multiline Input, min height: 200px)
- ButtonTailorResume (Button, style: Primary)
- ButtonClear (Button, style: Secondary)

# 結果顯示區域  
- GroupResults (Group, initially hidden)
- HTMLElementResults (HTML Element, ID: "optimized-resume-container")
- HTMLElementStats (HTML Element, for statistics display)

# 狀態管理
- GroupLoading (Group with loading indicator)
- HTMLElementMessages (HTML Element, ID: "message-container")

# 統計顯示元件
- TextOriginalSimilarity (Text, ID: "original-similarity")
- TextOptimizedSimilarity (Text, ID: "optimized-similarity")  
- TextSimilarityImprovement (Text, ID: "similarity-improvement")
- TextKeywordCount (Text, ID: "keyword-count")
- TextPlaceholderCount (Text, ID: "placeholder-count")
```

## 🔧 Step 3: 初始化 JavaScript (Page Loaded)

### Event: Page is loaded
```javascript
// 複製整個 bubble_page_loaded_script.js 的內容
// 檔案位置：docs/bubble_integration/bubble_page_loaded_script.js

// 或直接使用以下核心功能：
(function() {
    'use strict';
    console.log('🚀 AIResumeAdvisor: Initializing for Bubble.io');
    
    // 載入增強樣式
    const styleSheet = document.createElement('style');
    styleSheet.id = 'resume-enhanced-styles';
    styleSheet.innerHTML = `
        .opt-new { background-color: #e8f5e8 !important; border-left: 4px solid #4CAF50 !important; }
        .opt-modified { background-color: #fff3cd !important; border-left: 4px solid #ffc107 !important; }
        .opt-placeholder { background-color: #f8d7da !important; color: #721c24 !important; font-weight: bold !important; }
        .opt-keyword { background-color: #d1ecf1 !important; color: #0c5460 !important; font-weight: bold !important; }
        .opt-keyword-existing { background-color: #d4edda !important; color: #155724 !important; font-weight: bold !important; }
    `;
    document.head.appendChild(styleSheet);
    
    // 全域處理函數
    window.handleResumeTailoringResponse = function(apiResponse) {
        if (!apiResponse || !apiResponse.success) return false;
        
        const data = apiResponse.data;
        
        // 更新履歷顯示
        const container = document.getElementById('optimized-resume-container');
        if (container && data.optimized_resume) {
            container.innerHTML = data.optimized_resume;
        }
        
        // 更新統計
        if (data.index_calculation) {
            const stats = data.index_calculation;
            document.getElementById('original-similarity').textContent = stats.original_similarity + '%';
            document.getElementById('optimized-similarity').textContent = stats.optimized_similarity + '%';
            document.getElementById('similarity-improvement').textContent = '+' + stats.similarity_improvement + '%';
        }
        
        if (data.visual_markers) {
            const markers = data.visual_markers;
            document.getElementById('keyword-count').textContent = markers.keyword_count;
            document.getElementById('placeholder-count').textContent = markers.placeholder_count;
        }
        
        return true;
    };
    
    window.handleAPIError = function(error, context) {
        const container = document.getElementById('message-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${error.message || 'Request failed. Please try again.'}
                </div>
            `;
        }
    };
    
    console.log('✅ AIResumeAdvisor initialized successfully');
})();
```

## 🔄 Step 4: 主要工作流程

### Event: ButtonTailorResume is clicked

```yaml
Action 1: Only when (條件檢查)
Condition: 
  InputJobDescription's value count of characters > 200 AND 
  InputOriginalResume's value count of characters > 200

Action 2: Set State (準備資料)
State: GapAnalysisData
Value: {
  "core_strengths": [
    "Strong programming foundation",
    "Proven problem-solving abilities", 
    "Experience with modern technologies"
  ],
  "key_gaps": [
    "Limited senior-level experience",
    "Missing specialized certifications",
    "Could strengthen leadership examples"
  ],
  "quick_improvements": [
    "Add quantified achievements",
    "Highlight technical leadership",
    "Include relevant certifications"
  ],
  "covered_keywords": ["Python", "JavaScript", "SQL", "Git"],
  "missing_keywords": ["AWS", "Docker", "Machine Learning", "Senior", "Lead"]
}

Action 3: Set State (選項設定)
State: TailoringOptions  
Value: {
  "include_visual_markers": true,
  "language": "en"
}

Action 4: Show/Hide Elements (顯示載入)
Show: GroupLoading
Hide: GroupResults

Action 5: API Call (呼叫 API)
API: TailorResume
Parameters:
  code: [YOUR_FUNCTION_KEY]
  job_description: InputJobDescription's value
  original_resume: InputOriginalResume's value  
  gap_analysis: Current State GapAnalysisData
  options: Current State TailoringOptions

Action 6: Run JavaScript (處理成功回應)
Only when: Step 5 is successful
JavaScript:
```
```javascript
// 處理 API 回應
const apiResponse = {API_RESULT_FROM_STEP_5};
const success = window.handleResumeTailoringResponse(apiResponse);

if (success) {
    // 顯示成功訊息
    const messageContainer = document.getElementById('message-container');
    if (messageContainer) {
        messageContainer.innerHTML = `
            <div class="alert alert-success">
                <strong>Success!</strong> Your resume has been optimized with 
                ${apiResponse.data.visual_markers.keyword_count} new keywords and 
                ${apiResponse.data.index_calculation.similarity_improvement}% improvement in similarity.
            </div>
        `;
        
        // 3秒後清除訊息
        setTimeout(() => {
            messageContainer.innerHTML = '';
        }, 3000);
    }
    
    console.log('✅ Resume tailoring completed successfully');
} else {
    console.error('❌ Failed to process API response');
}
```

```yaml
Action 7: Set State (儲存結果)
Only when: Step 5 is successful
State: OptimizationResults
Value: Result of step 5's data

Action 8: Show/Hide Elements (顯示結果)
Only when: Step 5 is successful
Show: GroupResults
Hide: GroupLoading

Action 9: Run JavaScript (處理錯誤)
Only when: Step 5 is not successful
JavaScript:
```
```javascript
// 錯誤處理
const error = {
    status: {HTTP_STATUS_CODE_FROM_STEP_5},
    message: {ERROR_MESSAGE_FROM_STEP_5}
};

window.handleAPIError(error, 'Resume Tailoring');
console.error('❌ API call failed:', error);
```

```yaml
Action 10: Show/Hide Elements (隱藏載入)
Only when: Step 5 is not successful  
Hide: GroupLoading
```

## 📊 Step 5: 結果顯示最佳化

### 建立統計面板：

```html
<!-- 在 HTML Element 中使用以下結構 -->
<div class="statistics-panel">
    <h4>📊 Optimization Results</h4>
    
    <div class="row">
        <div class="col-md-6">
            <h5>🎯 Similarity Analysis</h5>
            <p>Original: <span id="original-similarity" class="stat-value">0%</span></p>
            <p>Optimized: <span id="optimized-similarity" class="stat-value">0%</span></p>
            <p>Improvement: <span id="similarity-improvement" class="stat-improvement">+0%</span></p>
        </div>
        
        <div class="col-md-6">
            <h5>🏷️ Visual Markers</h5>
            <p>New Keywords: <span id="keyword-count" class="stat-value">0</span></p>
            <p>Placeholders: <span id="placeholder-count" class="stat-value">0</span></p>
            <p>New Content: <span id="new-content-count" class="stat-value">0</span></p>
        </div>
    </div>
</div>

<style>
.statistics-panel {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}

.stat-value {
    font-weight: bold;
    color: #007bff;
}

.stat-improvement {
    font-weight: bold;
    color: #28a745;
}
</style>
```

## 🔄 Step 6: 匯出功能

### Export Clean Resume (ButtonExportClean clicked):

```javascript
const optimizedResume = `{Current State OptimizationResults's optimized_resume}`;
if (optimizedResume) {
    // 移除所有標記
    const cleanHTML = optimizedResume
        .replace(/class="[^"]*opt-[^"]*"/g, '')
        .replace(/<span class="">/g, '<span>')
        .replace(/<[^>]+class=""[^>]*>/g, function(match) {
            return match.replace(' class=""', '');
        });
    
    // 下載檔案
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
}
```

## 🧹 Step 7: 清除重置功能

### Clear All (ButtonClear clicked):

```javascript
// 清除顯示內容
const containers = [
    'optimized-resume-container',
    'message-container'
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

```yaml
# 同時執行的 Action:
Set State: OptimizationResults = empty
Show: GroupInputs  
Hide: GroupResults
```

## 🎯 實際測試範例

### 測試用數據：

```json
{
  "job_description": "Senior Software Engineer with 5+ years Python experience, machine learning expertise, and cloud platform knowledge. Must have experience with Docker, Kubernetes, and AWS services.",
  
  "original_resume": "<h1>John Doe</h1><p>Software Developer with 4 years of experience in Python development and data analysis. Proficient in Flask, PostgreSQL, and Git.</p><h3>Work Experience</h3><ul><li>Developed web applications using Python and JavaScript</li><li>Analyzed user data to improve application performance</li></ul>",
  
  "gap_analysis": {
    "core_strengths": ["Strong Python programming foundation", "Experience with web development", "Data analysis skills", "Proven collaboration abilities"],
    "key_gaps": ["Limited machine learning experience", "Missing cloud platform expertise", "No containerization experience", "Lacks senior-level positioning"],
    "quick_improvements": ["Highlight Python expertise more prominently", "Add any ML coursework or projects", "Emphasize problem-solving and technical leadership", "Include any cloud-related experience"],
    "covered_keywords": ["Python", "Flask", "PostgreSQL", "Git", "JavaScript"],
    "missing_keywords": ["Machine Learning", "AWS", "Docker", "Kubernetes", "Senior", "Cloud", "ML", "DevOps"]
  }
}
```

### 預期結果：

- ✅ **API 回應時間**: ~30 秒
- ✅ **Similarity 改善**: +11% (88% → 99%)
- ✅ **Keyword Coverage 改善**: +61% (31% → 92%)
- ✅ **新增關鍵字**: 8 個 (AWS, Machine Learning, Kubernetes 等)
- ✅ **視覺標記**: 28 個新關鍵字標記，6 個佔位符

## 🛠️ 故障排除指南

### 常見問題與解決方案：

#### ❌ 401 Unauthorized
```
問題：API Key 認證失敗
解決：確認 URL parameter 'code' 設定正確
檢查：https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume?code=YOUR_KEY
```

#### ❌ 422 Validation Error
```
問題：輸入資料格式錯誤
解決：確認 job_description 和 original_resume 長度 > 200 字元
檢查：gap_analysis 物件結構正確
```

#### ❌ 504 Gateway Timeout
```
問題：請求處理時間過長
解決：正常現象，API 需要 20-30 秒處理時間
建議：顯示載入提示，不要重複提交
```

#### ❌ JavaScript 函數未定義
```
問題：window.handleResumeTailoringResponse is not defined
解決：確認 Page Loaded 事件中的 JavaScript 已正確執行
檢查：瀏覽器 Console 是否有初始化成功訊息
```

### 除錯檢查清單：

```javascript
// 在瀏覽器 Console 中執行以下檢查
console.log('Functions available:', {
    handleResponse: typeof window.handleResumeTailoringResponse,
    handleError: typeof window.handleAPIError,
    stylesLoaded: !!document.getElementById('resume-enhanced-styles')
});

// 測試 API 連接
fetch('https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/health')
    .then(r => r.text())
    .then(console.log)
    .catch(console.error);
```

## 🎉 完成確認

當您看到以下結果時，整合就成功了：

1. ✅ 輸入 Job Description 和 Resume (各 > 200 字元)
2. ✅ 點擊 "Tailor Resume" 按鈕
3. ✅ 看到載入指示器 (~30 秒)
4. ✅ 顯示優化後的履歷，包含彩色標記
5. ✅ 統計數據正確更新
6. ✅ 可以匯出清潔版本
7. ✅ Clear 功能正常運作

---

**🚀 恭喜！您的 Bubble.io 應用現在已完全整合 Resume Tailoring API v2.0，具備完整的視覺標記系統和統計分析功能！**

**📞 如需技術支援，請查看瀏覽器 Console 的錯誤訊息，或參考 GitHub Issues。**