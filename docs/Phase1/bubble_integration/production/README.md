# TinyMCE Multi-Editor Marker Control System

完整的 TinyMCE 多編輯器標記控制系統，支援 Bubble.io 平台。

## 🚀 快速開始

### 1. 基本設置

1. **Page Header**: 複製 `bubble_code/page_header.html` 到 Bubble 頁面的 HTML Header
2. **Page Loaded**: 複製 `bubble_code/page_loaded.js` 到 "Page is Loaded" workflow
3. **Toggle 按鈕**: 複製 `bubble_code/toggle_button.js` 到主要 toggle 按鈕的 workflow
4. **Checkbox 控制**: 複製 `bubble_code/checkboxes/` 下對應的檔案到各個 checkbox workflows

### 2. 功能特色

- ✅ **多編輯器支援**: 自動偵測並處理多個 TinyMCE 編輯器
- ✅ **標記控制**: 統一的標記顯示/隱藏控制
- ✅ **Placeholder 編輯**: 點擊編輯 placeholder，自動格式化
- ✅ **狀態同步**: 全局和個別標記狀態完美同步
- ✅ **調試工具**: 完整的調試和診斷工具

### 3. 支援的標記類型

| 標記類型 | CSS Class | 描述 |
|---------|-----------|------|
| 原有關鍵字 | `opt-keyword-existing` | 深藍色背景 |
| 新增關鍵字 | `opt-keyword` | 紫色邊框 |
| 修改內容 | `opt-modified` | 淺黃色背景 |
| 新增內容 | `opt-new` | 綠色左邊框 |
| 佔位符 | `opt-placeholder` | 紅色虛線框 |
| 改進內容 | `opt-improvement` | 綠色底線 |

## 📁 文件結構

```
bubble_code/
├── page_header.html        # Page Header 完整代碼
├── page_loaded.js         # Page is Loaded workflow
├── toggle_button.js       # Overall Toggle 按鈕
└── checkboxes/            # 各個 checkbox workflows

debug_tools/
├── debug_console.html     # 完整調試控制台
├── marker_inspector.html  # 標記檢查器
└── placeholder_tester.html # Placeholder 測試工具

documentation/
├── setup_guide.md         # 詳細設置指南
├── troubleshooting.md     # 故障排除指南
├── api_reference.md       # API 參考文檔
└── architecture.md        # 系統架構說明
```

## 🛠️ 調試工具

### 快速診斷命令
```javascript
// 在 Console 中執行
window.diagnoseMarkerSystem();           // 系統診斷
window.getPlaceholderStatus();          // Placeholder 狀態
window.resetAllMarkerStates();          // 重置所有狀態
```

### 調試 HTML 工具
- `debug_tools/debug_console.html`: 完整的調試控制台
- `debug_tools/marker_inspector.html`: 標記檢查器
- `debug_tools/placeholder_tester.html`: Placeholder 測試工具

## 📚 文檔

- [詳細設置指南](documentation/setup_guide.md)
- [故障排除](documentation/troubleshooting.md)
- [API 參考](documentation/api_reference.md)
- [系統架構](documentation/architecture.md)

## 🔧 故障排除

### 常見問題

1. **Toggle 功能不工作**
   - 確認 `window.markersVisible` 變數已正確初始化
   - 檢查是否有 JavaScript 錯誤

2. **Placeholder 點擊無反應**
   - 確認編輯器模式（readonly/design）
   - 執行 `window.testPlaceholderClick()` 測試

3. **多編輯器不同步**
   - 執行 `window.diagnoseMarkerSystem()` 檢查狀態
   - 確認所有編輯器都已初始化

## 📋 版本記錄

查看 [CHANGELOG.md](CHANGELOG.md) 了解詳細的版本更新記錄。

## 👥 貢獻

此系統由 Claude Code 和 WenHao 協作開發，專為 Azure FastAPI + Bubble.io 整合專案設計。

---

**版本**: v2.0.0  
**最後更新**: 2025-01-12  
**相容性**: TinyMCE 6.8.3+, Bubble.io