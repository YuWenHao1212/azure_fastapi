# 故障排除指南

## 🚨 常見問題與解決方案

### 1. Toggle 功能問題

#### 問題：點擊 Toggle 按鈕沒有反應
**症狀**：
- 按鈕點擊後沒有切換標記顯示/隱藏
- Console 無錯誤訊息

**診斷步驟**：
```javascript
// 在 Console 中執行
console.log('markersVisible:', window.markersVisible);
console.log('tinymce:', typeof tinymce);
console.log('editors:', tinymce ? tinymce.get() : 'TinyMCE not loaded');
```

**可能原因與解決方法**：

1. **TinyMCE 未載入**
   ```javascript
   // 檢查 TinyMCE 狀態
   if (typeof tinymce === 'undefined') {
       console.log('TinyMCE 尚未載入，請等待或檢查載入');
   }
   ```

2. **變數未初始化**
   ```javascript
   // 手動初始化
   window.markersVisible = true;
   window.markersCurrentlyVisible = true;
   ```

3. **編輯器未初始化**
   ```javascript
   // 檢查編輯器狀態
   const editors = tinymce.get();
   editors.forEach((editor, i) => {
       console.log(`Editor ${i}: initialized=${editor.initialized}`);
   });
   ```

#### 問題：Toggle 後狀態不一致
**症狀**：
- 有些編輯器顯示標記，有些隱藏
- Checkbox 狀態與實際顯示不符

**解決方法**：
```javascript
// 重置所有狀態
window.resetAllMarkerStates();

// 或手動同步
window.diagnoseMarkerSystem();
```

### 2. Placeholder 編輯問題

#### 問題：點擊 Placeholder 無法編輯
**症狀**：
- 點擊紅色虛線框無反應
- 無法進入編輯模式

**診斷步驟**：
```javascript
// 檢查 Placeholder 狀態
window.getPlaceholderStatus();

// 檢查編輯器模式
const editor = tinymce.activeEditor;
console.log('Editor mode:', editor ? editor.mode.get() : 'No active editor');
```

**可能原因與解決方法**：

1. **編輯器在 readonly 模式**
   ```javascript
   // 檢查並切換模式
   const editor = tinymce.activeEditor;
   if (editor && editor.mode.get() === 'readonly') {
       console.log('編輯器在唯讀模式，這是正常的');
       // 系統會自動處理模式切換
   }
   ```

2. **事件處理器未設置**
   ```javascript
   // 檢查處理器設置
   const editor = tinymce.activeEditor;
   console.log('Placeholder handler setup:', editor ? editor.placeholderHandlerSetup : 'No editor');
   ```

3. **第一次點擊問題**
   ```javascript
   // 重置第一次點擊標記
   window.resetFirstClick();
   
   // 手動激活
   window.activateCurrentPlaceholder();
   ```

#### 問題：Placeholder 編輯後格式化錯誤
**症狀**：
- 輸入數字後沒有自動添加單位
- 格式化結果不正確

**解決方法**：
1. 檢查 placeholder 的 `type` 是否正確設置
2. 確認格式化規則是否符合需求
3. 手動測試格式化邏輯

### 3. 多編輯器同步問題

#### 問題：新增的編輯器沒有標記控制
**症狀**：
- 動態添加的編輯器無法控制標記
- 樣式沒有正確應用

**診斷步驟**：
```javascript
// 檢查編輯器監控
console.log('監控系統是否運行：', setInterval ? '是' : '否');

// 檢查編輯器數量
const editors = getAllTinyMCEEditors();
console.log('編輯器數量:', editors.length);
```

**解決方法**：
```javascript
// 手動處理新編輯器
window.injectDefaultMarkerStyles();
window.injectMultiTagStyles();

// 重新啟動監控
// (需要修改 monitorNewEditors 函數中的 setInterval)
```

#### 問題：編輯器樣式注入失敗
**症狀**：
- 標記沒有顏色或樣式
- 標記看起來像普通文字

**解決方法**：
```javascript
// 檢查樣式注入狀態
const editor = tinymce.activeEditor;
if (editor) {
    const hasDefaultStyles = editor.dom.get('default-marker-styles');
    const hasMultiTagStyles = editor.dom.get('multi-tag-styles');
    console.log('Default styles:', hasDefaultStyles ? '已注入' : '未注入');
    console.log('Multi-tag styles:', hasMultiTagStyles ? '已注入' : '未注入');
}

// 手動重新注入
window.injectDefaultMarkerStyles();
window.injectMultiTagStyles();
```

### 4. Checkbox 控制問題

#### 問題：Checkbox 切換無效
**症狀**：
- 點擊 checkbox 後標記狀態沒有改變
- Console 顯示主開關關閉訊息

**解決方法**：
```javascript
// 檢查主開關狀態
console.log('主開關狀態:', window.markersVisible);

// 如果主開關關閉，先開啟
if (!window.markersVisible) {
    window.showMarkers();
}

// 然後再控制個別標記
window.toggleSingleTag('opt-keyword-existing');
```

#### 問題：Checkbox 視覺狀態不同步
**症狀**：
- Checkbox 選中但標記隱藏
- 狀態顯示與實際不符

**解決方法**：
```javascript
// 更新所有 checkbox 狀態
if (typeof updateAllCheckboxes === 'function') {
    updateAllCheckboxes();
} else {
    console.log('updateAllCheckboxes 函數不存在');
}
```

### 5. 性能問題

#### 問題：頁面載入緩慢
**症狀**：
- 初始化時間過長
- 編輯器響應遲緩

**優化方法**：
```javascript
// 調整監控間隔（在 Page Header 中）
// 將 2500ms 改為更大的值
setInterval(checkForNewEditors, 5000); // 改為 5 秒

// 減少診斷函數的執行頻率
```

#### 問題：記憶體使用過高
**症狀**：
- 瀏覽器變慢
- 長時間使用後性能下降

**解決方法**：
1. 定期清理不必要的監聽器
2. 避免在 Console 中執行太多診斷函數
3. 重新載入頁面清理記憶體

### 6. JavaScript 錯誤

#### 常見錯誤 1：`Cannot read property 'get' of undefined`
**原因**：嘗試在編輯器未初始化時訪問編輯器方法

**解決方法**：
```javascript
// 安全的編輯器訪問
const editor = tinymce.activeEditor;
if (editor && editor.initialized) {
    const mode = editor.mode.get();
    // 安全操作
}
```

#### 常見錯誤 2：`toggleSingleTag is not a function`
**原因**：函數未正確載入或命名錯誤

**解決方法**：
```javascript
// 檢查函數是否存在
if (typeof window.toggleSingleTag === 'function') {
    window.toggleSingleTag('opt-keyword');
} else {
    console.log('toggleSingleTag 函數不存在，檢查 Page Header 是否正確載入');
}
```

## 🔧 診斷工具使用

### 內建診斷函數
```javascript
// 完整系統診斷
window.diagnoseMarkerSystem();

// Placeholder 狀態檢查
window.getPlaceholderStatus();

// 重置所有狀態
window.resetAllMarkerStates();

// 測試 Placeholder 點擊
window.testPlaceholderClick();
```

### 調試控制台
使用 `debug_tools/debug_console.html` 進行可視化診斷：
1. 在瀏覽器中開啟 debug_console.html
2. 點擊「完整診斷」按鈕
3. 查看系統狀態和編輯器資訊
4. 使用快速控制按鈕測試功能

### 手動檢查清單

1. **基本環境檢查**
   - [ ] TinyMCE 版本 6.8.3+
   - [ ] Bubble.io 環境正常
   - [ ] 無 JavaScript 語法錯誤

2. **代碼載入檢查**
   - [ ] Page Header 代碼完整
   - [ ] Page Loaded 代碼正確
   - [ ] 所有 workflow 已設置

3. **函數可用性檢查**
   - [ ] `window.toggleMarkers` 存在
   - [ ] `window.toggleSingleTag` 存在
   - [ ] `window.diagnoseMarkerSystem` 存在

4. **編輯器狀態檢查**
   - [ ] 編輯器已初始化
   - [ ] 樣式已正確注入
   - [ ] 事件處理器已設置

## 🆘 緊急修復

如果系統完全無法運作：

```javascript
// 緊急重置腳本
(function() {
    // 重置所有全局變數
    window.markersVisible = true;
    window.markersCurrentlyVisible = true;
    window.newSectionVisible = true;
    window.modificationVisible = true;
    window.placeholdersVisible = true;
    window.newKeywordsVisible = true;
    window.existingKeywordsVisible = true;
    
    // 重新載入頁面
    setTimeout(() => {
        location.reload();
    }, 1000);
    
    console.log('緊急重置完成，頁面將在 1 秒後重新載入');
})();
```

## 📞 技術支援

當所有方法都無法解決問題時：

1. 收集錯誤訊息和 Console 輸出
2. 記錄重現步驟
3. 提供環境資訊（TinyMCE 版本、瀏覽器版本等）
4. 使用調試控制台匯出日誌檔案

記住：大部分問題都可以通過重新載入頁面或執行重置函數來解決！