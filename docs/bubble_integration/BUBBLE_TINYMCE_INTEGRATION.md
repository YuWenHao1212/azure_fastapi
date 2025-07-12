# Bubble.io + TinyMCE Integration Guide

**關鍵技術記錄**  
**創建日期**: 2025-01-11  
**重要性**: 🔴 Critical

## 核心概念

在 Bubble.io 平台上使用 TinyMCE Rich Text Editor 時，必須使用 JavaScript 動態注入 CSS 樣式。

## 為什麼需要 JavaScript 注入？

1. **Bubble 平台限制**：無法直接在 TinyMCE 編輯器設置內部樣式
2. **TinyMCE 隔離**：編輯器內容在 iframe 中，外部 CSS 無法直接影響
3. **動態載入**：TinyMCE 是動態初始化的，需要等待其完全載入

## 實作方法

### Step 1: Page Header (靜態定義)
```html
<!-- 在 Bubble page 的 HTML header 中 -->
<style>
/* 定義基礎樣式，但這些不會直接影響 TinyMCE 內部 */
span.opt-keyword {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
}
</style>
```

### Step 2: Page is Loaded (動態注入)
```javascript
// 在 Bubble 的 "When page is loaded" workflow 中執行
function injectTinyMCEStyles() {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
        var editor = tinymce.activeEditor;
        
        // 這裡定義要注入的 CSS
        var cssToInject = `
            span.opt-keyword {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                padding: 3px 8px !important;
                border-radius: 4px !important;
                font-weight: 600 !important;
                box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3) !important;
            }
            
            span.opt-keyword-existing {
                background-color: transparent !important;
                color: #6366F1 !important;
                border: 1px solid #C7D2FE !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
            }
            
            /* 修改內容 - 淺黃色背景 - 只在 span 上 */
            span.opt-modified {
                background-color: #FFF3CD !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                display: inline !important;
            }
            
            /* 防止錯誤使用在區塊元素上 */
            li.opt-modified,
            p.opt-modified {
                background-color: transparent !important;
                background: none !important;
            }
            
            /* 其他樣式... */
        `;
        
        // 注入到 TinyMCE
        editor.dom.addStyle(cssToInject);
        console.log('TinyMCE 樣式已成功注入');
    } else {
        // 如果 TinyMCE 還沒準備好，1 秒後重試
        setTimeout(injectTinyMCEStyles, 1000);
    }
}

// 開始注入流程
injectTinyMCEStyles();
```

## 實際案例：2025-01-11 除錯記錄

### 問題描述
- 關鍵字顯示為黃色背景，而非預期的藍色
- 整個列表項被標記，而非特定關鍵字

### 根本原因
1. Page header 定義了藍色樣式
2. Page is loaded JavaScript 注入了黃色樣式
3. JavaScript 注入的樣式優先級更高，覆蓋了 header 樣式

### 解決方案
統一兩處的樣式定義，確保一致性。

## 最佳實踐

### 1. 單一來源原則
選擇其中一種方法：
- **推薦**：只使用 JavaScript 注入（確保 TinyMCE 載入後生效）
- 避免：同時在 header 和 JavaScript 定義相同選擇器

### 2. 優先級管理
```css
/* 使用更具體的選擇器和 !important */
.mce-content-body span.opt-keyword {
    background-color: #2563EB !important;
}
```

### 3. 除錯方法
```javascript
// 檢查實際應用的樣式
function checkTinyMCEStyles() {
    var editor = tinymce.activeEditor;
    if (!editor) {
        console.log('No active editor');
        return;
    }
    
    var body = editor.getBody();
    var testElement = body.querySelector('.opt-keyword');
    
    if (testElement) {
        var styles = editor.getWin().getComputedStyle(testElement);
        console.log('Element:', testElement.tagName);
        console.log('Background:', styles.backgroundColor);
        console.log('Color:', styles.color);
        console.log('Display:', styles.display);
    } else {
        console.log('No opt-keyword element found');
    }
}

// 執行檢查
checkTinyMCEStyles();
```

## 相關檔案

- **完整實作範例**: `/docs/bubble_integration/corrected_header.html`
- **視覺化展示**: `/docs/demo/resume_marking_demo.html`
- **技術決策記錄**: `.serena/memories/technical_decisions/bubble_tinymce_css_injection.md`
- **專案指南**: `CLAUDE.md` (Bubble.io API 相容性章節)

## 快速檢查清單

- [ ] 是否使用 page is loaded 事件？
- [ ] 是否等待 TinyMCE 完全載入？
- [ ] 是否使用 `editor.dom.addStyle()` 方法？
- [ ] 是否有重試機制？
- [ ] 是否檢查了樣式衝突？

---

**記住這個關鍵點**：Bubble.io + TinyMCE = JavaScript 注入 CSS！

不要依賴外部 CSS 檔案或 page header 的 style 標籤來設置 TinyMCE 內部樣式。