// ========================================
// 簡化版：第二個編輯器樣式注入
// 在按鈕點擊時執行這段代碼
// ========================================

// 將這段代碼放在顯示第二個編輯器的按鈕 workflow 中
(function() {
    console.log('[注入樣式] 開始為第二個編輯器注入樣式...');
    
    // 定義要注入的完整樣式
    const editorStyles = `
        /* 原有關鍵字 - 深藍色背景 */
        span.opt-keyword-existing {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            padding: 3px 8px !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            margin: 0 2px !important;
            display: inline-block !important;
            line-height: 1.4 !important;
            box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3) !important;
        }
        
        /* 新增關鍵字 - 紫色邊框 */
        span.opt-keyword {
            background-color: transparent !important;
            color: #6366F1 !important;
            border: 1px solid #C7D2FE !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            font-weight: 500 !important;
            margin: 0 2px !important;
            display: inline-block !important;
        }
        
        /* 修改內容 - 淺黃色背景 */
        span.opt-modified {
            background-color: #FFF3CD !important;
            color: #856404 !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            border: 1px solid #FFEAA7 !important;
            display: inline !important;
        }
        
        /* 新增內容 - 綠色左邊框 */
        .opt-new {
            border-left: 4px solid #10B981 !important;
            padding-left: 16px !important;
            padding-right: 16px !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
            margin: 8px 0 !important;
            background-color: rgba(209, 250, 229, 0.3) !important;
            display: block !important;
        }
        
        /* 佔位符 - 紅色虛線框 */
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
            display: inline-block !important;
        }
        
        /* 改進內容 - 綠色底線 */
        span.opt-improvement {
            border-bottom: 2px solid #10B981 !important;
            color: #065F46 !important;
            padding-bottom: 1px !important;
            font-weight: 500 !important;
        }
        
        /* 隱藏標記的樣式 */
        body.markers-hidden span.opt-keyword-existing,
        body.markers-hidden span.opt-keyword,
        body.markers-hidden span.opt-modified,
        body.markers-hidden .opt-new,
        body.markers-hidden span.opt-placeholder,
        body.markers-hidden span.opt-improvement {
            all: unset !important;
            color: inherit !important;
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            font-weight: inherit !important;
            font-style: inherit !important;
            text-decoration: none !important;
            display: inline !important;
            box-shadow: none !important;
        }
        
        body.markers-hidden .opt-new {
            display: block !important;
        }
    `;
    
    // 等待並注入樣式的函數
    function injectStyles() {
        // 檢查 TinyMCE 是否載入
        if (typeof tinymce === 'undefined') {
            console.log('[注入樣式] TinyMCE 尚未載入，500ms 後重試...');
            setTimeout(injectStyles, 500);
            return;
        }
        
        // 嘗試找到第二個編輯器
        let secondEditor = tinymce.get('TinyMCE_Editor_initial_resume');
        
        // 如果找不到特定 ID，嘗試用索引
        if (!secondEditor) {
            const allEditors = tinymce.get();
            if (allEditors && allEditors.length > 1) {
                secondEditor = allEditors[1];
            }
        }
        
        if (secondEditor && secondEditor.initialized) {
            try {
                // 注入樣式
                secondEditor.dom.addStyle(editorStyles);
                
                // 檢查並同步標記顯示狀態
                const body = secondEditor.getBody();
                if (body && window.markersVisible === false) {
                    secondEditor.dom.addClass(body, 'markers-hidden');
                }
                
                console.log('[注入樣式] ✅ 成功！編輯器 ID:', secondEditor.id);
                
            } catch (error) {
                console.error('[注入樣式] ❌ 錯誤:', error);
            }
        } else {
            console.log('[注入樣式] 編輯器尚未就緒，500ms 後重試...');
            setTimeout(injectStyles, 500);
        }
    }
    
    // 立即開始嘗試注入
    injectStyles();
})();