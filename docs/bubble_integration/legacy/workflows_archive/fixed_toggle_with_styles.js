// ========================================
// 修正版：Toggle 按鈕 - 確保樣式存在
// 替換原本的 toggle 按鈕 workflow
// ========================================

// 追蹤當前是否顯示所有標記
if (typeof window.markersCurrentlyVisible === 'undefined') {
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

console.log('[Toggle] 切換到:', window.markersCurrentlyVisible ? '顯示所有標記' : '隱藏所有標記');

// 確保顯示樣式存在（這是關鍵！）
const ensureDisplayStyles = `
    /* 確保顯示樣式 */
    body:not(.markers-hidden) span.opt-keyword-existing {
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
    
    body:not(.markers-hidden) span.opt-keyword {
        background-color: transparent !important;
        color: #6366F1 !important;
        border: 1px solid #C7D2FE !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
        font-weight: 500 !important;
        margin: 0 2px !important;
        display: inline-block !important;
    }
    
    body:not(.markers-hidden) span.opt-modified {
        background-color: #FFF3CD !important;
        color: #856404 !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
        border: 1px solid #FFEAA7 !important;
        display: inline !important;
    }
    
    body:not(.markers-hidden) .opt-new {
        border-left: 4px solid #10B981 !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
        margin: 8px 0 !important;
        background-color: rgba(209, 250, 229, 0.3) !important;
        display: block !important;
    }
    
    body:not(.markers-hidden) span.opt-placeholder {
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px dashed #F87171 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        font-style: italic !important;
        font-weight: 500 !important;
        display: inline-block !important;
    }
    
    /* 隱藏樣式 */
    body.markers-hidden span.opt-keyword-existing,
    body.markers-hidden span.opt-keyword,
    body.markers-hidden span.opt-modified,
    body.markers-hidden .opt-new,
    body.markers-hidden span.opt-placeholder {
        all: unset !important;
        color: inherit !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-weight: inherit !important;
        font-style: inherit !important;
        display: inline !important;
    }
    
    body.markers-hidden .opt-new {
        display: block !important;
    }
`;

// 獲取所有編輯器
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        editorArray.forEach((editor, index) => {
            if (editor && editor.initialized) {
                const body = editor.getBody();
                const doc = editor.getDoc();
                
                // 確保樣式存在（每次都注入，避免遺漏）
                if (doc && !doc.getElementById('toggle-ensure-styles')) {
                    editor.dom.addStyle(ensureDisplayStyles);
                    
                    // 添加標記
                    const marker = doc.createElement('style');
                    marker.id = 'toggle-ensure-styles';
                    marker.innerHTML = '/* Toggle styles ensured */';
                    doc.head.appendChild(marker);
                    
                    console.log(`[Toggle] 確保編輯器 ${index + 1} 有完整樣式`);
                }
                
                // 執行 toggle
                if (body) {
                    if (window.markersCurrentlyVisible) {
                        body.classList.remove('markers-hidden');
                        console.log(`[Toggle] 編輯器 ${index + 1}: 顯示標記`);
                    } else {
                        body.classList.add('markers-hidden');
                        console.log(`[Toggle] 編輯器 ${index + 1}: 隱藏標記`);
                    }
                }
            }
        });
    }
}

// 同步個別標記狀態
window.newSectionVisible = window.markersCurrentlyVisible;
window.modificationVisible = window.markersCurrentlyVisible;
window.placeholdersVisible = window.markersCurrentlyVisible;
window.newKeywordsVisible = window.markersCurrentlyVisible;
window.existingKeywordsVisible = window.markersCurrentlyVisible;

console.log('[Toggle] 完成！');