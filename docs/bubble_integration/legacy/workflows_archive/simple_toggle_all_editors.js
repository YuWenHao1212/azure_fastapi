// ========================================
// 簡化版：Toggle 所有編輯器
// 直接替換原本的 toggle 按鈕 workflow
// ========================================

// 追蹤狀態
if (typeof window.markersCurrentlyVisible === 'undefined') {
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

// 獲取所有編輯器並切換
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        // 確保是陣列格式
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        // 對每個編輯器執行切換
        editorArray.forEach(editor => {
            if (editor && editor.initialized) {
                const body = editor.getBody();
                if (body) {
                    if (window.markersCurrentlyVisible) {
                        body.classList.remove('markers-hidden');
                    } else {
                        body.classList.add('markers-hidden');
                    }
                }
            }
        });
        
        console.log(`[Toggle] 已${window.markersCurrentlyVisible ? '顯示' : '隱藏'}所有編輯器的標記`);
    }
}

// 同步個別標記狀態
window.newSectionVisible = window.markersCurrentlyVisible;
window.modificationVisible = window.markersCurrentlyVisible;
window.placeholdersVisible = window.markersCurrentlyVisible;
window.newKeywordsVisible = window.markersCurrentlyVisible;
window.existingKeywordsVisible = window.markersCurrentlyVisible;