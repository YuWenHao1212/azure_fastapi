// TinyMCE 樣式注入腳本
// 用於 Bubble.io "page is loaded" workflow
// 更新日期: 2025-01-12

function injectTinyMCEStyles() {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor && !tinymce.activeEditor.isHidden()) {
        var editor = tinymce.activeEditor;
        
        // 定義要注入的完整 CSS
        var fullCSS = `
            /* 1. 新增內容 - 綠色左邊框 */
            .opt-new {
                border-left: 4px solid #10B981 !important;
                padding-left: 16px !important;
                background-color: rgba(209, 250, 229, 0.1) !important;
                margin-left: -20px !important;
                padding-right: 16px !important;
            }
            
            h2.opt-new, h3.opt-new {
                background-color: transparent !important;
            }
            
            /* 2. 修改內容 - 淺黃色背景 - 只在 span 上 */
            span.opt-modified {
                background-color: #FFF3CD !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                display: inline !important;
                line-height: inherit !important;
            }
            
            /* 防止錯誤使用在區塊元素上 */
            li.opt-modified,
            p.opt-modified,
            h1.opt-modified,
            h2.opt-modified,
            h3.opt-modified,
            h4.opt-modified,
            h5.opt-modified {
                background-color: transparent !important;
                background: none !important;
                color: inherit !important;
                padding: 0 !important;
                border-radius: 0 !important;
            }
            
            /* 3. 新增關鍵字 - 紫色邊框（低調，需確認） */
            span.opt-keyword {
                background-color: transparent !important;
                color: #6366F1 !important;
                border: 1px solid #C7D2FE !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                font-weight: 500 !important;
                margin: 0 2px !important;
            }
            
            /* 4. 原有關鍵字 - 深藍色背景（醒目強調） */
            span.opt-keyword-existing {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                padding: 3px 8px !important;
                border-radius: 4px !important;
                font-weight: 600 !important;
                margin: 0 2px !important;
                box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3) !important;
            }
            
            /* 5. 佔位符 - 紅色虛線框 */
            span.opt-placeholder {
                background-color: #FEE2E2 !important;
                color: #991B1B !important;
                border: 1px dashed #F87171 !important;
                padding: 2px 8px !important;
                border-radius: 4px !important;
                font-style: italic !important;
                font-weight: 500 !important;
                cursor: pointer !important;
                margin: 0 2px !important;
            }
            
            span.opt-placeholder:hover {
                background-color: #FECACA !important;
                border-color: #EF4444 !important;
            }
            
            /* 6. 已編輯內容 - 綠色底線 */
            span.opt-improvement {
                border-bottom: 2px solid #10B981 !important;
                color: #065F46 !important;
                padding-bottom: 1px !important;
                font-weight: 500 !important;
            }
            
            /* 防止關鍵字標記錯誤應用在區塊元素上 */
            li.opt-keyword,
            p.opt-keyword,
            h1.opt-keyword,
            h2.opt-keyword,
            h3.opt-keyword,
            h4.opt-keyword,
            h5.opt-keyword,
            li.opt-keyword-existing,
            p.opt-keyword-existing,
            h1.opt-keyword-existing,
            h2.opt-keyword-existing,
            h3.opt-keyword-existing,
            h4.opt-keyword-existing,
            h5.opt-keyword-existing {
                background-color: transparent !important;
                background: none !important;
                color: inherit !important;
                padding: 0 !important;
                border: none !important;
                border-radius: 0 !important;
            }
        `;
        
        // 注入樣式
        editor.dom.addStyle(fullCSS);
        console.log('TinyMCE 樣式已成功注入');
        
        // 返回 true 表示成功
        return true;
    } else {
        // 如果 TinyMCE 還沒準備好，1秒後再試
        console.log('TinyMCE 尚未準備好，1秒後重試...');
        setTimeout(injectTinyMCEStyles, 1000);
        return false;
    }
}

// 開始注入流程
injectTinyMCEStyles();

// 可選：設置一個全局函數以便手動重新注入
window.reinjectTinyMCEStyles = injectTinyMCEStyles;