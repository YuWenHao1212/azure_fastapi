# 🎯 Bubble.io TinyMCE 標記切換完整整合指南

## ✅ 解決方案已驗證成功！

經過詳細測試，我們已經成功解決了 TinyMCE 標記切換的問題。

## 🔧 完整整合步驟

### 步驟 1: 添加 JavaScript 代碼

在你的 Bubble.io 頁面的 **HTML header** 中添加以下代碼：

```html
<script>
// 複製 bubble_tinymce_toggle_final.js 的完整內容到這裡
</script>
```

### 步驟 2: 設置 Toggle 元件

1. **Toggle 元件**：
   - 元件名稱：`btnToggleTags`
   - 預設狀態：根據你的需求設定（checked = 顯示標記）

### 步驟 3: 創建 Workflow

1. **When btnToggleTags is changed**：
   ```
   Element: btnToggleTags
   Event: Value is changed
   ```

2. **Action: Run JavaScript**：
   ```javascript
   // 取得 Toggle 的當前狀態
   var toggleElement = document.querySelector('[data-element-name="btnToggleTags"] input[type="checkbox"]');
   var isChecked = toggleElement ? toggleElement.checked : false;
   
   // 當 Toggle 被選中時 (checked = true) = 顯示標記
   // 當 Toggle 未被選中時 (checked = false) = 隱藏標記
   var hideMarkers = !isChecked;
   
   var success = toggleTinyMCEMarkers(hideMarkers);
   
   if (success) {
       console.log('標記切換成功: ' + (hideMarkers ? '隱藏' : '顯示'));
   } else {
       console.log('標記切換失敗');
   }
   ```

**簡化版本**（如果 Bubble 可以傳遞 Toggle 狀態）：
   ```javascript
   // 使用 Bubble 的動態數據
   var isChecked = properties.bubble_element_btnToggleTags.value;
   var hideMarkers = !isChecked;
   toggleTinyMCEMarkers(hideMarkers);
   ```

## 🎮 使用方式

### 在 Workflow 中直接調用

```javascript
// 隱藏所有標記
hideTinyMCEMarkers();

// 顯示所有標記  
showTinyMCEMarkers();

// 或使用主函數
toggleTinyMCEMarkers(true);  // 隱藏
toggleTinyMCEMarkers(false); // 顯示
```

### 直接基於 Toggle 狀態

```javascript
// 直接讀取 btnToggleTags 的狀態
var toggleElement = document.querySelector('[data-element-name="btnToggleTags"] input[type="checkbox"]');
if (toggleElement) {
    var hideMarkers = !toggleElement.checked;
    toggleTinyMCEMarkers(hideMarkers);
}
```

## 🎨 標記顏色說明

成功整合後，你將看到以下顏色的標記：

- **🟢 opt-new**: 淡綠色背景 + 綠色左邊框 (新增區段)
- **🟡 opt-modified**: 淡黃色背景 (修改內容)  
- **🔴 opt-placeholder**: 紅色背景 + 虛線邊框 (佔位符)
- **🔵 opt-keyword**: 藍色邊框 + 紫色文字 (新關鍵字)
- **🔷 opt-keyword-existing**: 藍色背景 + 白色文字 (現有關鍵字)

## 🐛 故障排除

### 1. 標記沒有顯示顏色
**原因**: 樣式沒有正確注入
**解決**: 重新載入頁面，或手動調用 `showTinyMCEMarkers()`

### 2. Toggle 沒有作用
**檢查步驟**:
```javascript
// 在瀏覽器控制台檢查
console.log('TinyMCE available:', typeof tinymce !== 'undefined');
console.log('Active editor:', tinymce && tinymce.activeEditor ? tinymce.activeEditor.id : 'None');
console.log('Toggle function:', typeof toggleTinyMCEMarkers);
```

### 3. JavaScript 錯誤
**常見問題**:
- 確保 TinyMCE 已完全載入
- 檢查是否有語法錯誤
- 使用瀏覽器開發者工具查看錯誤訊息

## 📝 測試步驟

1. **載入頁面**後，打開瀏覽器控制台
2. **查看**: 應該看到 "TinyMCE Marker Toggle script loaded"
3. **測試顯示**: 調用 `showTinyMCEMarkers()` - 應該看到彩色標記
4. **測試隱藏**: 調用 `hideTinyMCEMarkers()` - 標記應該消失
5. **測試 Toggle**: 點擊你的 Toggle 元件 - 標記應該顯示/隱藏

## 🔄 最佳實踐

### 1. 初始化檢查
在頁面載入時自動檢查 TinyMCE 狀態：

```javascript
// 在 Page is loaded 事件中
if (typeof toggleTinyMCEMarkers === 'function') {
    // 根據預設狀態設置標記顯示
    var defaultShow = true; // 或根據你的需求設定
    toggleTinyMCEMarkers(!defaultShow);
}
```

### 2. 錯誤處理
```javascript
// 在調用函數時加入錯誤處理
try {
    var success = toggleTinyMCEMarkers(hideMarkers);
    if (!success) {
        // 處理失敗情況
        console.warn('無法切換標記，請檢查 TinyMCE 狀態');
    }
} catch (error) {
    console.error('標記切換發生錯誤:', error);
}
```

### 3. 狀態同步
確保 UI 狀態與實際標記狀態同步：

```javascript
// 在成功切換後更新 Custom State
if (toggleTinyMCEMarkers(hideMarkers)) {
    // 更新相關的 Custom State
    // Set Group Tag Control's HTML Tag Display = !hideMarkers
}
```

## 📚 API 參考

### 主要函數

- `toggleTinyMCEMarkers(hideMarkers)` - 主切換函數
- `showTinyMCEMarkers()` - 顯示所有標記
- `hideTinyMCEMarkers()` - 隱藏所有標記

### 內部函數 (進階使用)

- `TinyMCEMarkerToggle.getActiveEditor()` - 獲取活動編輯器
- `TinyMCEMarkerToggle.injectMarkerStyles(doc)` - 注入樣式
- `TinyMCEMarkerToggle.forceRefresh(editor, doc)` - 強制刷新

## 🎉 完成！

按照這個指南，你應該能夠在 Bubble.io 中成功實現 TinyMCE 標記的顯示/隱藏功能。

如果遇到任何問題，請檢查瀏覽器控制台的錯誤訊息，並確保所有步驟都正確執行。