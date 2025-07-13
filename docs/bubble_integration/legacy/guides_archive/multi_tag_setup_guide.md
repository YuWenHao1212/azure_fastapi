# 多標記獨立控制 - 設置指南

## 概述
這個系統允許您分別控制5種不同的 opt-tag 顯示/隱藏：
- `opt-new` - 新增區段（綠色）
- `opt-modified` - 修改內容（黃色）
- `opt-placeholder` - 佔位符（紅色）
- `opt-keyword` - 新關鍵字（紫色）
- `opt-keyword-existing` - 現有關鍵字（藍色）

## 設置步驟

### 步驟 1：更新 Page HTML Header
將 `multi_tag_control_header.html` 的內容添加到您的 Page HTML Header。

**注意**：這個可以和原本的單一 toggle 系統共存，不會衝突。

### 步驟 2：創建個別的 Toggle 元素
在 Bubble 中創建5個 Toggle（Checkbox）元素：
1. `btnToggleOptNew` - 控制新增區段
2. `btnToggleOptModified` - 控制修改內容
3. `btnToggleOptPlaceholder` - 控制佔位符
4. `btnToggleOptKeyword` - 控制新關鍵字
5. `btnToggleOptKeywordExisting` - 控制現有關鍵字

### 步驟 3：設置 Workflow
為每個 Toggle 創建 "When input's value is changed" workflow，並添加 "Run JavaScript" action。

從 `individual_toggle_workflows.js` 複製對應的代碼到各個 workflow。

### 步驟 4：（可選）添加全部顯示/隱藏按鈕
創建兩個按鈕：
- `btnShowAllTags` - 顯示所有標記
- `btnHideAllTags` - 隱藏所有標記

### 步驟 5：更新 Page Load Workflow
```javascript
// 初始化多標記系統
if (typeof window.initializeMultiTagSystem === 'function') {
    window.initializeMultiTagSystem();
    console.log('✅ Multi-tag system initialization started');
}
```

## 使用範例

### 在 JavaScript 中控制特定標記
```javascript
// 隱藏所有 placeholder
toggleSingleTag('opt-placeholder', false);

// 顯示所有 keyword
toggleSingleTag('opt-keyword', true);
toggleSingleTag('opt-keyword-existing', true);

// 檢查狀態
console.log(window.tagTypes['opt-new'].visible); // true or false
```

### 批量操作
```javascript
// 只顯示關鍵字相關標記
hideAllTags();
toggleSingleTag('opt-keyword', true);
toggleSingleTag('opt-keyword-existing', true);
```

## 優點
1. **獨立控制**：每種標記可以單獨顯示/隱藏
2. **狀態追蹤**：系統會記住每種標記的狀態
3. **簡單整合**：每個 toggle 只需要幾行代碼
4. **相容性**：可以和原本的全部顯示/隱藏系統共存

## 注意事項
- 確保 TinyMCE 編輯器已載入後才執行操作
- Toggle 的初始狀態預設為 checked（顯示）
- 樣式使用 class 切換，性能良好