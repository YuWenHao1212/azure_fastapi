// ========================================
// 正確版本：Toggle 按鈕 workflow
// ========================================

// 初始化檢查（只在變數不存在時才設置）
if (typeof window.markersVisible === 'undefined') {
    window.markersVisible = true;
}
if (typeof window.markersCurrentlyVisible === 'undefined') {
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersVisible = !window.markersVisible;
window.markersCurrentlyVisible = window.markersVisible;

console.log('[Toggle] 狀態切換到:', window.markersVisible ? '顯示標記' : '隱藏標記');

// 應用到所有編輯器
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        editorArray.forEach((editor, index) => {
            if (editor && editor.initialized) {
                const body = editor.getBody();
                if (body) {
                    // 清理個別的 hide- classes（如果有的話）
                    const hideClasses = ['hide-opt-new', 'hide-opt-modified', 'hide-opt-placeholder', 
                                       'hide-opt-keyword', 'hide-opt-keyword-existing'];
                    hideClasses.forEach(cls => {
                        body.classList.remove(cls);
                    });
                    
                    // 設置 markers-hidden 狀態
                    if (window.markersVisible) {
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

console.log('[Toggle] 完成！');

// 更新所有 checkbox 的視覺狀態
if (typeof updateAllCheckboxes === 'function') {
    updateAllCheckboxes();
}