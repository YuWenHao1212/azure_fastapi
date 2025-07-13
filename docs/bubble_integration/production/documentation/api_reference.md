# API 參考文檔

## 🔧 全局函數

### 標記控制函數

#### `window.toggleMarkers()`
切換所有標記的顯示/隱藏狀態。

```javascript
window.toggleMarkers();
```

**行為**：
- 切換 `window.markersVisible` 狀態
- 應用到所有 TinyMCE 編輯器
- 同步所有個別標記狀態
- 更新 checkbox 視覺狀態

---

#### `window.showMarkers()`
顯示所有標記。

```javascript
window.showMarkers();
```

**行為**：
- 設置 `window.markersVisible = true`
- 移除所有編輯器的 `markers-hidden` class
- 應用個別標記可見性設置

---

#### `window.hideMarkers()`
隱藏所有標記。

```javascript
window.hideMarkers();
```

**行為**：
- 設置 `window.markersVisible = false`
- 添加 `markers-hidden` class 到所有編輯器

---

#### `window.toggleSingleTag(tagType)`
切換特定類型標記的顯示/隱藏。

```javascript
window.toggleSingleTag('opt-keyword-existing');
```

**參數**：
- `tagType` (string): 標記類型，可選值：
  - `'opt-keyword-existing'` - 原有關鍵字
  - `'opt-keyword'` - 新增關鍵字
  - `'opt-modified'` - 修改內容
  - `'opt-new'` - 新增內容
  - `'opt-placeholder'` - 佔位符

**行為**：
- 切換 `window.tagVisibility[tagType]` 狀態
- 應用到所有編輯器
- 更新對應的 checkbox 狀態

---

#### `window.showAllTags()`
顯示所有類型的標記。

```javascript
window.showAllTags();
```

---

#### `window.hideAllTags()`
隱藏所有類型的標記。

```javascript
window.hideAllTags();
```

### 樣式注入函數

#### `window.injectDefaultMarkerStyles()`
注入預設的標記樣式到所有編輯器。

```javascript
window.injectDefaultMarkerStyles();
```

**行為**：
- 檢查是否已注入樣式（避免重複）
- 注入完整的標記樣式 CSS
- 創建樣式標記元素
- 記錄注入狀態

---

#### `window.injectMultiTagStyles()`
注入多標記控制樣式。

```javascript
window.injectMultiTagStyles();
```

**行為**：
- 注入 `hide-*` class 的樣式規則
- 支援個別標記類型的隱藏

### 診斷與調試函數

#### `window.diagnoseMarkerSystem()`
執行完整的系統診斷。

```javascript
window.diagnoseMarkerSystem();
```

**輸出**：
```
===== 標記系統診斷 =====
主開關: true
個別標記狀態: {
  opt-new: true,
  opt-modified: true,
  opt-placeholder: true,
  opt-keyword: true,
  opt-keyword-existing: true
}
編輯器數量: 2
編輯器 1 (tinymce_1): {markers-hidden: false, mode: "readonly"}
編輯器 2 (tinymce_2): {markers-hidden: false, mode: "readonly"}
```

---

#### `window.resetAllMarkerStates()`
重置所有標記狀態為顯示。

```javascript
window.resetAllMarkerStates();
```

**行為**：
- 重置所有全局變數為 `true`
- 顯示所有標記
- 更新所有 checkbox 狀態

### Placeholder 函數

#### `window.getPlaceholderStatus()`
獲取 Placeholder 系統狀態。

```javascript
const status = window.getPlaceholderStatus();
console.log(status);
```

**回傳值**：
```javascript
{
  mode: "readonly",           // 編輯器模式
  placeholders: 3,           // placeholder 數量
  completed: 1,              // 已完成數量
  hasClickedBefore: true     // 是否已點擊過
}
```

---

#### `window.testPlaceholderClick()`
模擬點擊第一個 placeholder。

```javascript
window.testPlaceholderClick();
```

**行為**：
- 尋找第一個 `.opt-placeholder` 元素
- 模擬 mousedown 事件
- 測試 placeholder 編輯功能

---

#### `window.resetFirstClick()`
重置第一次點擊標記。

```javascript
window.resetFirstClick();
```

**用途**：當 placeholder 第一次點擊有問題時使用

---

#### `window.activateCurrentPlaceholder()`
手動激活當前正在編輯的 placeholder。

```javascript
window.activateCurrentPlaceholder();
```

**用途**：當 placeholder 失去焦點時手動重新激活

### 輔助函數

#### `getAllTinyMCEEditors()`
獲取所有 TinyMCE 編輯器實例。

```javascript
const editors = getAllTinyMCEEditors();
console.log('編輯器數量:', editors.length);
```

**回傳值**：編輯器實例陣列

---

#### `forEachEditor(callback)`
對所有編輯器執行回調函數。

```javascript
forEachEditor(function(editor, index) {
    console.log(`編輯器 ${index}: ${editor.id}`);
});
```

**參數**：
- `callback` (function): 回調函數，接收 `(editor, index)` 參數

## 🔧 全局變數

### 狀態變數

#### `window.markersVisible`
主要標記顯示狀態。
- **類型**: boolean
- **預設值**: true

#### `window.markersCurrentlyVisible`
當前標記顯示狀態（用於同步）。
- **類型**: boolean
- **預設值**: true

#### `window.markerStylesInjected`
樣式注入狀態標記。
- **類型**: boolean
- **預設值**: false

### 個別標記狀態

#### `window.newSectionVisible`
新增內容標記顯示狀態。
- **類型**: boolean
- **預設值**: true

#### `window.modificationVisible`
修改內容標記顯示狀態。
- **類型**: boolean
- **預設值**: true

#### `window.placeholdersVisible`
佔位符標記顯示狀態。
- **類型**: boolean
- **預設值**: true

#### `window.newKeywordsVisible`
新增關鍵字標記顯示狀態。
- **類型**: boolean
- **預設值**: true

#### `window.existingKeywordsVisible`
原有關鍵字標記顯示狀態。
- **類型**: boolean
- **預設值**: true

### 標記可見性配置

#### `window.tagVisibility`
標記類型可見性配置物件。

```javascript
window.tagVisibility = {
    'opt-keyword': true,
    'opt-keyword-existing': true,
    'opt-modified': true,
    'opt-new': true,
    'opt-placeholder': true
};
```

## 🎨 CSS Classes

### 標記樣式 Classes

#### `.opt-keyword-existing`
原有關鍵字標記。
- **樣式**: 深藍色背景，白色文字
- **用途**: 標記已存在的關鍵字

#### `.opt-keyword`
新增關鍵字標記。
- **樣式**: 紫色邊框，透明背景
- **用途**: 標記新添加的關鍵字

#### `.opt-modified`
修改內容標記。
- **樣式**: 淺黃色背景
- **用途**: 標記被修改的內容

#### `.opt-new`
新增內容標記。
- **樣式**: 綠色左邊框
- **用途**: 標記新添加的內容區塊

#### `.opt-placeholder`
佔位符標記。
- **樣式**: 紅色虛線框，italic 字體
- **用途**: 可編輯的佔位符
- **行為**: 點擊可編輯

#### `.opt-improvement`
改進內容標記。
- **樣式**: 綠色底線
- **用途**: 標記已完成編輯的內容

### 控制 Classes

#### `.markers-hidden`
應用到編輯器 body，隱藏所有標記。

#### `.hide-{tagType}`
隱藏特定類型的標記：
- `.hide-opt-keyword`
- `.hide-opt-keyword-existing`
- `.hide-opt-modified`
- `.hide-opt-new`
- `.hide-opt-placeholder`

### Placeholder 編輯 Classes

#### `.editing-placeholder`
正在編輯的 placeholder 樣式。
- **樣式**: 白色背景，深色邊框
- **行為**: contentEditable = true

## 🔧 事件系統

### TinyMCE 事件

系統監聽以下 TinyMCE 事件：

#### `AddEditor`
當新編輯器添加時觸發。
```javascript
tinymce.on('AddEditor', function(e) {
    // 自動設置新編輯器
});
```

#### `init`
編輯器初始化完成時觸發。
```javascript
editor.on('init', function() {
    // 設置 placeholder 處理器
});
```

#### `keydown`
鍵盤按下事件（在 placeholder 編輯模式中）。
- **Enter**: 完成編輯
- **Escape**: 取消編輯

### DOM 事件

#### `mousedown`
Placeholder 點擊事件（使用 capture phase）。

#### `DOMContentLoaded`
頁面載入完成事件，觸發系統初始化。

## ⚡ 快捷鍵

### 全局快捷鍵

#### `Ctrl + M`
切換所有標記顯示/隱藏。

```javascript
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'm') {
        e.preventDefault();
        window.toggleMarkers();
    }
});
```

## 🔧 配置選項

### Placeholder 格式化配置

在 `page_loaded.js` 中修改 `hints` 物件：

```javascript
const hints = {
    'PERCENTAGE': '25',
    'TEAM SIZE': '5-10',
    'AMOUNT': '1',
    'NUMBER': '100',
    'TIME PERIOD': '3',
    'USER COUNT': '10000',
    '35M units': '35',
    '70%': '70'
};
```

### 監控間隔配置

在 Page Header 中修改：

```javascript
// 編輯器監控間隔（毫秒）
setInterval(checkForNewEditors, 2500);
```

## 🐛 錯誤處理

### 常見錯誤代碼

所有函數都包含 try-catch 錯誤處理：

```javascript
try {
    // 主要邏輯
} catch (e) {
    console.error(`Error processing editor ${editor.id}:`, e);
}
```

### 安全檢查

函數執行前會進行必要的安全檢查：

```javascript
// 檢查 TinyMCE 是否可用
if (typeof tinymce === 'undefined') return [];

// 檢查編輯器是否初始化
if (editor && editor.initialized) {
    // 安全操作
}
```