// ========================================
// 修正版：解決 Toggle 狀態同步問題
// 替換您的 toggle 按鈕 workflow
// ========================================

// 統一所有狀態變數
window.markersVisible = true;  // 確保初始狀態一致
window.markersCurrentlyVisible = true;

// 切換狀態（使用單一變數避免混亂）
window.markersVisible = !window.markersVisible;
window.markersCurrentlyVisible = window.markersVisible;

console.log('[Toggle Fix] 狀態切換到:', window.markersVisible ? '顯示' : '隱藏');

// 清理所有可能的干擾 classes
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        editorArray.forEach((editor, index) => {
            if (editor && editor.initialized) {
                const body = editor.getBody();
                if (body) {
                    // 先清理所有個別的 hide- classes
                    const hideClasses = ['hide-opt-new', 'hide-opt-modified', 'hide-opt-placeholder', 
                                       'hide-opt-keyword', 'hide-opt-keyword-existing'];
                    
                    hideClasses.forEach(cls => {
                        body.classList.remove(cls);
                    });
                    
                    // 然後設置正確的 markers-hidden 狀態
                    if (window.markersVisible) {
                        body.classList.remove('markers-hidden');
                        console.log(`[Toggle Fix] 編輯器 ${index + 1}: 顯示標記`);
                    } else {
                        body.classList.add('markers-hidden');
                        console.log(`[Toggle Fix] 編輯器 ${index + 1}: 隱藏標記`);
                    }
                }
            }
        });
    }
}

// 同步個別標記狀態（但不使用 hide- classes）
window.newSectionVisible = window.markersVisible;
window.modificationVisible = window.markersVisible;
window.placeholdersVisible = window.markersVisible;
window.newKeywordsVisible = window.markersVisible;
window.existingKeywordsVisible = window.markersVisible;

// 更新 tagVisibility（如果存在）
if (typeof window.tagVisibility !== 'undefined') {
    Object.keys(window.tagVisibility).forEach(tag => {
        window.tagVisibility[tag] = window.markersVisible;
    });
}

console.log('[Toggle Fix] 狀態同步完成');