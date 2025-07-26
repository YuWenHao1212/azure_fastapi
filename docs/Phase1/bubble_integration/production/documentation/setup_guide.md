# 詳細設置指南

## 🎯 概述

本指南將詳細說明如何在 Bubble.io 中設置 TinyMCE 多編輯器標記控制系統。

## 📋 前置需求

- Bubble.io 應用程式
- TinyMCE 6.8.3 或更高版本
- 基本的 JavaScript 知識

## 🚀 步驟 1：Page Header 設置

1. 在 Bubble 編輯器中，進入你的頁面設置
2. 找到 "Page HTML header" 部分
3. 複製 `bubble_code/page_header.html` 的完整內容
4. 貼上到 Page HTML header 中

### 重要事項
- 確保完整複製所有內容，包括 `<style>` 和 `<script>` 標籤
- 不要修改任何變數名稱或函數名稱

## 🚀 步驟 2：Page Loaded Workflow

1. 在 Workflow 編輯器中，找到 "When Page is loaded" 事件
2. 添加一個 "Run Javascript" action
3. 複製 `bubble_code/page_loaded.js` 的內容
4. 貼上到 Javascript 代碼框中

### 配置選項
```javascript
// 可以修改的初始值提示
const hints = {
    'PERCENTAGE': '25',      // 百分比預設值
    'TEAM SIZE': '5-10',     // 團隊規模預設值
    'AMOUNT': '1',           // 金額預設值
    'NUMBER': '100',         // 數字預設值
    'TIME PERIOD': '3',      // 時間週期預設值
    'USER COUNT': '10000'    // 用戶數量預設值
};
```

## 🚀 步驟 3：Toggle 按鈕設置

1. 創建一個按鈕元素作為主要的標記切換按鈕
2. 為該按鈕添加 "When Button is clicked" workflow
3. 添加 "Run Javascript" action
4. 複製 `bubble_code/toggle_button.js` 的內容

### 按鈕樣式建議
```css
/* 添加到按鈕的 CSS classes */
.toggle-button {
    padding: 8px 16px;
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}
```

## 🚀 步驟 4：Checkbox 控制設置

為每種標記類型設置獨立的 checkbox 控制：

### 4.1 Existing Keywords Checkbox
1. 創建一個 checkbox 元素
2. 設置 "When Checkbox's value is changed" workflow
3. 複製 `bubble_code/checkboxes/existing_keywords.js`

### 4.2 New Keywords Checkbox
重複上述步驟，使用 `bubble_code/checkboxes/new_keywords.js`

### 4.3 Modification Checkbox
重複上述步驟，使用 `bubble_code/checkboxes/modification.js`

### 4.4 New Section Checkbox
重複上述步驟，使用 `bubble_code/checkboxes/new_section.js`

### 4.5 Placeholders Checkbox
重複上述步驟，使用 `bubble_code/checkboxes/placeholders.js`

## 🎨 步驟 5：樣式自訂

### 5.1 標記顏色自訂
在 Page Header 中找到樣式部分，可以修改各種標記的顏色：

```css
/* 原有關鍵字 - 藍色 */
span.opt-keyword-existing {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
}

/* 新增關鍵字 - 紫色 */
span.opt-keyword {
    color: #6366F1 !important;
    border: 1px solid #C7D2FE !important;
}

/* 修改內容 - 黃色 */
span.opt-modified {
    background-color: #FFF3CD !important;
    color: #856404 !important;
}
```

### 5.2 Placeholder 樣式
```css
/* 佔位符樣式 */
span.opt-placeholder {
    background-color: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px dashed #F87171 !important;
}
```

## 🔧 步驟 6：測試與驗證

### 6.1 基本功能測試
1. 重新載入頁面
2. 檢查 Console 是否有錯誤訊息
3. 測試主要 Toggle 按鈕
4. 測試各個 checkbox 功能

### 6.2 Placeholder 測試
1. 在編輯器中添加一些 placeholder 元素：
   ```html
   <span class="opt-placeholder">[PERCENTAGE]</span>
   <span class="opt-placeholder">[TEAM SIZE]</span>
   ```
2. 點擊 placeholder 測試編輯功能
3. 確認自動格式化正常運作

### 6.3 多編輯器測試
如果頁面有多個 TinyMCE 編輯器：
1. 確認所有編輯器都能正常切換標記
2. 確認狀態同步正常
3. 測試 placeholder 在所有編輯器中都能編輯

## 🐛 常見問題解決

### 問題 1：Toggle 功能不工作
**可能原因**：
- TinyMCE 尚未完全載入
- JavaScript 錯誤

**解決方法**：
1. 檢查 Console 錯誤訊息
2. 確認 TinyMCE 版本相容性
3. 增加載入延遲時間

### 問題 2：Placeholder 點擊無反應
**可能原因**：
- 編輯器在 readonly 模式
- 事件處理器未正確設置

**解決方法**：
1. 執行 `window.getPlaceholderStatus()` 檢查狀態
2. 執行 `window.testPlaceholderClick()` 測試功能
3. 確認編輯器初始化完成

### 問題 3：多編輯器不同步
**可能原因**：
- 編輯器監控未正常運作
- 樣式注入失敗

**解決方法**：
1. 執行 `window.diagnoseMarkerSystem()` 診斷
2. 檢查編輯器數量和狀態
3. 手動執行 `window.injectDefaultMarkerStyles()`

## 📊 性能優化

### 減少載入時間
```javascript
// 在 Page Header 中，可以調整監控間隔
setInterval(checkForNewEditors, 5000); // 改為 5 秒
```

### 減少樣式重複注入
系統會自動檢查是否已注入樣式，避免重複注入。

## 🔧 進階配置

### 自訂格式化規則
在 `page_loaded.js` 中修改 `finishEditingAndSwitch` 函數：

```javascript
switch(placeholderData.type) {
    case 'CUSTOM_TYPE':
        if (value.match(/^\d+$/)) {
            formatted = value + ' 自訂單位';
        }
        break;
}
```

### 添加新的標記類型
1. 在 Page Header 的樣式中添加新的 CSS 規則
2. 在 `tagVisibility` 物件中添加新的標記類型
3. 創建對應的 checkbox workflow

## 📝 部署檢查清單

- [ ] Page Header 代碼已正確貼上
- [ ] Page Loaded workflow 已設置
- [ ] Toggle 按鈕 workflow 已設置
- [ ] 所有 checkbox workflows 已設置
- [ ] 測試所有基本功能
- [ ] 測試 placeholder 編輯功能
- [ ] 檢查 Console 無錯誤訊息
- [ ] 多編輯器環境測試通過

## 🆘 技術支援

如果遇到問題：
1. 使用 `debug_tools/debug_console.html` 進行診斷
2. 檢查 `troubleshooting.md` 故障排除指南
3. 查看 Console 錯誤訊息
4. 執行內建的診斷函數