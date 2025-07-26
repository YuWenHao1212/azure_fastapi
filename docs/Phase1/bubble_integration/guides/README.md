# TinyMCE Placeholder Handler for Bubble.io

## 最終版本

請使用 `tinymce_placeholder_handler_final.js` - 這是經過測試的穩定版本。

## 功能特點

1. **點擊編輯**：點擊紅色虛線框的 placeholder 進入編輯模式
2. **智能單位**：根據 placeholder 類型自動添加適當的單位
3. **模式切換**：自動處理 readonly/design 模式切換
4. **鍵盤操作**：
   - Enter：完成編輯
   - Escape：取消編輯

## 使用方法

1. 將 `tinymce_placeholder_handler_final.js` 的內容複製到 Bubble 頁面的 HTML Header
2. 腳本會自動初始化並開始工作
3. 如需調試，可在瀏覽器控制台查看 `[Placeholder-Handler]` 開頭的日誌

## 支援的 Placeholder 類型

- `[PERCENTAGE]` → 自動添加 `%`
- `[AMOUNT]` → 自動添加 `$`
- `[TEAM SIZE]` → 純數字會添加 ` people`
- `[TIME PERIOD]` → 純數字會添加 ` months`
- `[USER COUNT]` → 大數字轉換為 `K` 或 `M`
- `[35M units]` → 純數字會添加 `M units`

## API 函數

```javascript
// 查看當前狀態
getPlaceholderStatus()

// 測試點擊第一個 placeholder
testPlaceholderClick()

// 重置第一次點擊標記（用於測試）
resetFirstClick()

// 手動激活當前編輯的 placeholder
activateCurrentPlaceholder()
```

## 已知限制

- 第一次點擊 placeholder 後，可能需要再點擊一次才能開始輸入
- 這是 TinyMCE 在 iframe 中的焦點管理限制

## 版本歷史

- v1.0.0 (2025-01-11): 最終穩定版本

## 其他檔案說明（已廢棄）

以下檔案僅供參考，請勿使用：
- `placeholder_mutation_observer.js` - 早期版本，過於複雜
- `placeholder_simple_fix.js` - 開發版本
- 其他測試檔案 - 實驗性質

請只使用 `tinymce_placeholder_handler_final.js`。