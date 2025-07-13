# 多個 TinyMCE 編輯器樣式問題診斷指南

**問題描述**：在 Bubble 頁面添加第二個 TinyMCE Rich Text Editor 後，原本的 HTML 標籤渲染效果消失。

**創建日期**：2025-07-13

## 問題原因分析

### 1. 單一編輯器假設
原本的樣式注入腳本使用 `tinymce.activeEditor`，只會影響當前活躍的編輯器：
```javascript
// 問題代碼
var editor = tinymce.activeEditor;  // 只取得一個編輯器
editor.dom.addStyle(css);           // 只注入到這個編輯器
```

### 2. 編輯器初始化時序
- 第一個編輯器：頁面載入時初始化，樣式正常注入
- 第二個編輯器：稍後初始化，錯過了樣式注入時機

### 3. 樣式隔離
每個 TinyMCE 編輯器都有獨立的 iframe，樣式必須分別注入到每個編輯器中。

## 解決方案

### 方案 1：使用多編輯器樣式注入腳本（推薦）

在 Bubble 的 "When page is loaded" workflow 中使用新的腳本：

```javascript
// 使用 tinymce_multi_editor_styles.js
// 這個腳本會：
// 1. 自動檢測所有編輯器
// 2. 為每個編輯器注入樣式
// 3. 監聽新編輯器的創建
```

### 方案 2：為特定編輯器注入樣式

如果您知道編輯器的 ID，可以針對性注入：

```javascript
function injectStylesToSpecificEditor(editorId) {
    var editor = tinymce.get(editorId);
    if (editor) {
        editor.dom.addStyle(/* 您的 CSS */);
    }
}

// 例如：
injectStylesToSpecificEditor('tinymce-1');  // 第一個編輯器
injectStylesToSpecificEditor('tinymce-2');  // 第二個編輯器
```

### 方案 3：使用 TinyMCE 初始化回調

在 Bubble 中設置 TinyMCE 時，添加初始化回調：

```javascript
// 在 TinyMCE 插件設置中
{
    setup: function(editor) {
        editor.on('init', function() {
            // 編輯器初始化完成後注入樣式
            editor.dom.addStyle(/* 您的 CSS */);
        });
    }
}
```

## 診斷步驟

### 1. 檢查編輯器數量
在瀏覽器控制台執行：
```javascript
console.log('編輯器數量:', tinymce.editors.length);
tinymce.editors.forEach((e, i) => {
    console.log(`編輯器 ${i+1}: ID=${e.id}, 可見=${!e.isHidden()}`);
});
```

### 2. 檢查樣式是否已注入
```javascript
tinymce.editors.forEach((editor, i) => {
    var hasStyles = editor.dom.hasClass(editor.getBody(), 'styles-injected');
    console.log(`編輯器 ${i+1} 樣式注入狀態:`, hasStyles);
});
```

### 3. 手動測試樣式注入
```javascript
// 測試第二個編輯器
var editor2 = tinymce.editors[1];  // 索引從 0 開始
if (editor2) {
    editor2.dom.addStyle('span.test { background: red !important; }');
    editor2.setContent('<span class="test">測試文字</span>');
}
```

## 實施步驟

### Step 1：替換原有腳本
將原本的 `tinymce_styles_injection.js` 替換為 `tinymce_multi_editor_styles.js`。

### Step 2：在 Bubble 中更新 Workflow
1. 進入 Bubble 編輯器
2. 找到 "When page is loaded" workflow
3. 更新 "Run JavaScript" action，使用新腳本

### Step 3：測試驗證
1. 重新載入頁面
2. 檢查兩個編輯器是否都有樣式
3. 使用診斷命令確認：
   ```javascript
   checkAllTinyMCEStyles();
   ```

## 常見問題

### Q1：樣式只在第一個編輯器生效
**原因**：使用了 `activeEditor` 而非遍歷所有編輯器。
**解決**：使用 `tinymce.editors.forEach()` 處理所有編輯器。

### Q2：第二個編輯器延遲載入時沒有樣式
**原因**：樣式注入在編輯器初始化前執行。
**解決**：監聽 `AddEditor` 事件，動態注入樣式。

### Q3：樣式被覆蓋或衝突
**原因**：多個樣式源造成優先級問題。
**解決**：
1. 使用更具體的選擇器
2. 確保使用 `!important`
3. 檢查是否有其他 CSS 源

## 最佳實踐

1. **統一管理**：將所有 TinyMCE 樣式集中在一個地方管理
2. **延遲注入**：確保編輯器完全初始化後再注入樣式
3. **標記狀態**：使用 class 標記已注入樣式的編輯器，避免重複
4. **提供除錯工具**：保留診斷函數以便問題排查

## 相關檔案

- `/workflows/tinymce_multi_editor_styles.js` - 多編輯器支援腳本
- `/workflows/tinymce_styles_injection.js` - 原始單編輯器腳本
- `/guides/BUBBLE_TINYMCE_INTEGRATION.md` - TinyMCE 整合總覽

## 快速修復清單

- [ ] 確認有多個 TinyMCE 編輯器
- [ ] 更換為多編輯器支援腳本
- [ ] 驗證所有編輯器都有樣式
- [ ] 測試動態添加編輯器的情況
- [ ] 記錄編輯器 ID 以便後續維護