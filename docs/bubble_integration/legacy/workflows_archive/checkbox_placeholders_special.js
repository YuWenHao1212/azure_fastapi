// === 特殊版本 - Checkbox Placeholders 的 Workflow ===
// 替換原本的 Checkbox Placeholders workflow 代碼

if (typeof window.placeholdersVisible === 'undefined') {
    window.placeholdersVisible = true;
}
window.placeholdersVisible = !window.placeholdersVisible;

// Placeholder 需要特殊處理 - 不能完全隱藏
if (window.placeholdersVisible) {
    // 顯示：恢復完整樣式
    console.log('🟢 Placeholder markers: VISIBLE (full style)');
    
    // 移除任何 opacity 樣式
    if (tinymce && tinymce.activeEditor) {
        const style = tinymce.activeEditor.getDoc().getElementById('placeholder-dim-style');
        if (style) style.remove();
    }
} else {
    // "隱藏"：只是變淡，不影響功能
    console.log('🔴 Placeholder markers: DIMMED (still clickable)');
    
    if (tinymce && tinymce.activeEditor) {
        const iframeDoc = tinymce.activeEditor.getDoc();
        
        // 檢查是否已有 dim 樣式
        let dimStyle = iframeDoc.getElementById('placeholder-dim-style');
        if (!dimStyle) {
            dimStyle = iframeDoc.createElement('style');
            dimStyle.id = 'placeholder-dim-style';
            iframeDoc.head.appendChild(dimStyle);
        }
        
        // 只降低透明度，保留所有功能
        dimStyle.textContent = `
            .opt-placeholder {
                opacity: 0.3 !important;
                transition: opacity 0.2s ease;
            }
            
            .opt-placeholder:hover {
                opacity: 1 !important;
            }
            
            /* 確保可點擊 */
            .opt-placeholder {
                cursor: pointer !important;
                pointer-events: auto !important;
            }
        `;
    }
}

// 不使用 toggleSingleTag，因為它會破壞功能