# Bubble.io JavaScript 設定指南

## 📋 Page Loaded 時執行的 JavaScript

### 🚀 快速設定步驟

1. **在 Bubble Editor 中**:
   - 選擇您的頁面
   - 在 Workflow 中添加 "Page is loaded" 事件
   - 添加 Action: "Run JavaScript"

2. **複製以下代碼到 JavaScript Action**:
   ```javascript
   // 直接複製 bubble_page_loaded_script.js 的內容
   ```

### 📱 JavaScript 功能概覽

#### 1. **TinyMCE 增強樣式** 
- 自動載入三層標記系統的 CSS 樣式
- 支援響應式設計和印刷友好格式
- 包含動畫效果和工具提示

#### 2. **API 回應處理**
- `handleResumeTailoringResponse(apiResponse)` - 處理 API 回應
- `addTooltips(container)` - 添加互動式工具提示
- `updateIndexCalculationDisplay(data)` - 更新相似度統計
- `updateVisualMarkersDisplay(data)` - 更新標記統計

#### 3. **實用工具函數**
- `calculateMarkerStats(html)` - 計算標記統計
- `cleanResumeHTML(html)` - 清除所有標記
- `getPrintFriendlyHTML(html)` - 生成印刷友好格式

#### 4. **錯誤處理**
- `handleAPIError(error, context)` - 統一錯誤處理
- 自動顯示用戶友好的錯誤訊息

## 🎨 樣式效果

### 標記樣式
- **`.opt-new`**: 綠色邊框 + "NEW" 標籤
- **`.opt-modified`**: 黃色邊框 + "ENHANCED" 標籤  
- **`.opt-placeholder`**: 紅色背景 + 等寬字體
- **`.opt-keyword`**: 藍色背景 + 懸浮效果
- **`.opt-keyword-existing`**: 綠色背景 + 懸浮效果

### 互動效果
- 懸浮時的縮放效果
- 工具提示顯示
- 平滑的過渡動畫

## 🔧 在 Bubble Workflow 中使用

### 1. 處理 API 回應
```javascript
// 在 API Call 成功後執行
window.handleResumeTailoringResponse(Result of step X);
```

### 2. 更新 HTML 顯示元件
```javascript
// 假設您有一個 HTML Element 叫 "ResumeDisplay"
document.getElementById('ResumeDisplay').innerHTML = Result of step X's optimized_resume;
window.addTooltips(document.getElementById('ResumeDisplay'));
```

### 3. 顯示統計數據
```javascript
// 更新各種統計顯示
window.updateIndexCalculationDisplay(Result of step X's index_calculation);
window.updateVisualMarkersDisplay(Result of step X's visual_markers);
window.updateKeywordsAnalysisDisplay(Result of step X's keywords_analysis);
```

## 📊 所需的 HTML 元件 ID

在您的 Bubble 頁面中，請確保有以下 ID 的元件：

### 主要顯示區域
- `optimized-resume-container` - 顯示優化後履歷的 HTML Element
- `error-message-container` - 顯示錯誤訊息的容器

### Index Calculation 統計
- `original-similarity` - 原始相似度
- `optimized-similarity` - 優化後相似度  
- `similarity-improvement` - 相似度改善
- `original-keyword-coverage` - 原始關鍵字覆蓋率
- `optimized-keyword-coverage` - 優化後關鍵字覆蓋率
- `keyword-coverage-improvement` - 關鍵字覆蓋率改善

### Visual Markers 統計
- `keyword-count` - 新關鍵字數量
- `keyword-existing-count` - 原有關鍵字數量
- `placeholder-count` - 佔位符數量
- `new-content-count` - 新內容區塊數量
- `modified-content-count` - 修改內容數量

### Keywords Analysis
- `original-keywords-list` - 原有關鍵字列表
- `added-keywords-list` - 新增關鍵字列表  
- `new-keywords-list` - 新增關鍵字列表（來自 index_calculation）
- `total-keywords-count` - 總關鍵字數

## 🎯 事件監聽

JavaScript 會觸發以下自定義事件：

### 1. 初始化完成
```javascript
document.addEventListener('aiResumeAdvisorReady', function(event) {
    console.log('AIResumeAdvisor ready at:', event.detail.timestamp);
    // 您的初始化邏輯
});
```

### 2. Resume Tailoring 完成
```javascript
document.addEventListener('resumeTailoringComplete', function(event) {
    const response = event.detail.response;
    const stats = event.detail.stats;
    const markers = event.detail.markers;
    
    // 您的後續處理邏輯
    console.log('Resume tailoring completed:', stats);
});
```

## 🛠️ 除錯和測試

### 開啟瀏覽器控制台查看日誌
- `🚀 AIResumeAdvisor: Initializing page loaded script`
- `✅ Enhanced styles loaded successfully`
- `✅ API response handlers initialized`
- `🎉 AIResumeAdvisor page loaded script initialized successfully`

### 測試函數
```javascript
// 在瀏覽器控制台中測試
console.log(window.calculateMarkerStats('<p class="opt-new">Test</p>'));
console.log(window.cleanResumeHTML('<span class="opt-keyword">Python</span>'));
```

## 📱 響應式設計

JavaScript 包含以下響應式特性：
- 行動裝置優化的樣式
- 印刷友好格式
- 自適應字體大小
- 觸控友好的互動元素

## 🔒 錯誤處理機制

### 自動錯誤處理
- 401: 認證失敗
- 422: 輸入驗證錯誤  
- 500: 伺服器錯誤
- Timeout: 請求超時

### 錯誤顯示
- 自動顯示在 `error-message-container`
- 10 秒後自動隱藏
- Bootstrap Alert 樣式

---

**設定完成後，您的 Bubble.io 應用就能完美顯示 API 回應的增強標記效果！** 🎉