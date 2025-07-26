# TinyMCE 多編輯器標記控制系統 v2.0

## 🎯 專案概述

本專案為 Bubble.io 平台開發了一套完整的 TinyMCE 多編輯器標記控制系統，支援同步控制多個編輯器中的不同類型標記顯示/隱藏。

### ✨ 核心功能

- ✅ **多編輯器同步支援** - 同時控制多個 TinyMCE 編輯器
- ✅ **五種標記類型控制** - New Section, Keywords, Existing Keywords, Modifications, Placeholders
- ✅ **雙層控制系統** - 主開關 + 個別標記開關
- ✅ **Bubble.io 環境相容** - 解決了 `return` 語句錯誤問題
- ✅ **佔位符編輯功能** - 點擊編輯佔位符內容
- ✅ **完整診斷工具** - 提供調試和問題排除工具

## 📁 目錄結構

```
docs/bubble_integration/
├── README.md                    # 📋 專案總覽（本檔案）
├── production/                  # 🚀 生產就緒代碼
│   ├── bubble_code/            # 核心 JavaScript 代碼
│   │   ├── checkboxes/         # 個別標記控制
│   │   ├── page_header.html    # 頁面 Header 代碼
│   │   ├── page_loaded.js      # 頁面載入腳本
│   │   └── toggle_button.js    # 主切換按鈕
│   ├── debug_tools/            # 調試和診斷工具
│   ├── documentation/          # 技術文檔
│   └── examples/               # 使用範例
├── documentation/              # 📚 整合文檔
├── examples/                   # 📋 完整範例
├── demos/                      # 🧪 剩餘測試檔案
├── guides/                     # 📖 核心指南
├── test_data/                  # 📊 測試數據
└── legacy/                     # 📦 歷史檔案
    ├── workflows_archive/      # 舊版工作流程
    ├── demos_archive/          # 舊版調試檔案
    └── guides_archive/         # 舊版指南
```

## 🚀 快速開始

### 1. 基本設置

1. **複製核心代碼**
   ```
   production/bubble_code/page_header.html    → Bubble Page Header
   production/bubble_code/page_loaded.js      → Bubble Page Loaded workflow
   production/bubble_code/toggle_button.js    → Toggle Button workflow
   ```

2. **設置個別標記控制**
   ```
   production/bubble_code/checkboxes/new_section.js       → New Section checkbox
   production/bubble_code/checkboxes/new_keywords.js      → New Keywords checkbox
   production/bubble_code/checkboxes/existing_keywords.js → Existing Keywords checkbox
   production/bubble_code/checkboxes/modification.js      → Modification checkbox
   production/bubble_code/checkboxes/placeholders.js      → Placeholders checkbox
   ```

### 2. 重要檔案說明

| 檔案 | 功能 | 必需性 |
|------|------|--------|
| `page_header.html` | 核心樣式和函數定義 | ✅ 必需 |
| `page_loaded.js` | 佔位符處理和初始化 | ✅ 必需 |
| `toggle_button.js` | 主開關控制 | ✅ 必需 |
| `checkboxes/*.js` | 個別標記控制 | 🔧 可選 |

## 🔧 技術特點

### 解決的關鍵問題

1. **多編輯器同步問題** - 原版只能控制 activeEditor
2. **Bubble.io 語法限制** - 移除了所有 `return` 語句
3. **狀態同步問題** - 統一使用 `window.tagVisibility` 系統
4. **樣式注入問題** - 自動監測新編輯器並注入樣式

### 架構設計

- **頁面 Header** - 定義所有核心函數和樣式
- **頁面載入** - 初始化系統和佔位符處理
- **按鈕工作流程** - 各種切換和控制邏輯
- **診斷工具** - 問題排除和調試支援

## 📚 文檔說明

- **`documentation/`** - 完整的技術文檔和設置指南
- **`production/documentation/`** - 生產版本的詳細文檔
- **`guides/`** - 快速開始和疑難排解指南

## 🧪 測試和調試

使用 `production/debug_tools/` 中的工具進行問題診斷：

- `checkbox_diagnostic.js` - 檢查 checkbox 功能
- `simple_checkbox_test.js` - 簡化版測試
- `debug_console.html` - 調試控制台

## 📝 版本記錄

### v2.0 (2025-07-13)
- ✅ 實現多編輯器同步支援
- ✅ 修復 Bubble.io 相容性問題
- ✅ 添加完整的診斷工具
- ✅ 建立生產就緒的代碼結構

### v1.0 (歷史版本)
- 📦 移至 `legacy/` 目錄保存

## 🤝 貢獻

本專案由 Claude Code 協助開發，所有核心功能已完成並測試通過。

---

**最後更新**: 2025-07-13  
**版本**: v2.0  
**狀態**: 生產就緒 ✅