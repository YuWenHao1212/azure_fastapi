// ========================================
// 更新版：主 Toggle 按鈕 (btnToggleTags) 的 Workflow
// 支援多編輯器版本
// ========================================

// 追蹤當前是否顯示所有標記
if (typeof window.markersCurrentlyVisible === 'undefined') {
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

console.log('[Main Toggle] 切換到:', window.markersCurrentlyVisible ? '顯示所有標記' : '隱藏所有標記');

// === 方法 1: 使用新的多編輯器 toggle 函數（如果存在）===
if (typeof window.toggleMarkers === 'function') {
    console.log('[Main Toggle] 使用 toggleMarkers (多編輯器版本)');
    window.toggleMarkers();
} 
// === 方法 2: 使用舊版函數但改為處理所有編輯器 ===
else if (typeof window.toggleTinyMCEMarkers === 'function') {
    console.log('[Main Toggle] 使用 toggleTinyMCEMarkers (舊版)');
    window.toggleTinyMCEMarkers(!window.markersCurrentlyVisible);
} 
// === 方法 3: 直接操作所有編輯器 ===
else if (typeof tinymce !== 'undefined') {
    console.log('[Main Toggle] 直接操作所有編輯器');
    
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        editorArray.forEach((editor, index) => {
            if (editor && editor.initialized) {
                const body = editor.getBody();
                if (body) {
                    if (window.markersCurrentlyVisible) {
                        body.classList.remove('markers-hidden');
                        console.log(`[Main Toggle] 編輯器 ${index + 1} (${editor.id}): 顯示標記`);
                    } else {
                        body.classList.add('markers-hidden');
                        console.log(`[Main Toggle] 編輯器 ${index + 1} (${editor.id}): 隱藏標記`);
                    }
                }
            }
        });
    }
} else {
    console.error('[Main Toggle] 無法找到任何 toggle 方法！');
}

// 同步更新所有個別標記的狀態變數
window.newSectionVisible = window.markersCurrentlyVisible;
window.modificationVisible = window.markersCurrentlyVisible;
window.placeholdersVisible = window.markersCurrentlyVisible;
window.newKeywordsVisible = window.markersCurrentlyVisible;
window.existingKeywordsVisible = window.markersCurrentlyVisible;

// 更新 window.markersVisible（如果使用新版 header）
if (typeof window.markersVisible !== 'undefined') {
    window.markersVisible = window.markersCurrentlyVisible;
}

// 更新 tagVisibility（如果使用新版 header）
if (typeof window.tagVisibility !== 'undefined') {
    window.tagVisibility = {
        'opt-new': window.newSectionVisible,
        'opt-modified': window.modificationVisible,
        'opt-placeholder': window.placeholdersVisible,
        'opt-keyword': window.newKeywordsVisible,
        'opt-keyword-existing': window.existingKeywordsVisible
    };
}

console.log('[Main Toggle] 所有個別狀態已同步到:', window.markersCurrentlyVisible);

// === 確保樣式已注入到所有編輯器 ===
// 這是為了處理新編輯器可能還沒有樣式的情況
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        // 檢查是否需要注入樣式
        editorArray.forEach((editor, index) => {
            if (editor && editor.initialized) {
                const doc = editor.getDoc();
                if (doc && !doc.getElementById('toggle-styles-check')) {
                    console.log(`[Main Toggle] 為編輯器 ${index + 1} 注入必要樣式`);
                    
                    // 注入隱藏樣式
                    const hideStyles = `
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
                    
                    try {
                        editor.dom.addStyle(hideStyles);
                        
                        // 添加標記防止重複注入
                        const marker = doc.createElement('style');
                        marker.id = 'toggle-styles-check';
                        marker.innerHTML = '/* Toggle styles injected */';
                        doc.head.appendChild(marker);
                    } catch (e) {
                        console.error(`[Main Toggle] 注入樣式失敗:`, e);
                    }
                }
            }
        });
    }
}

// === 可選：觸發 Bubble 自定義事件（如果需要）===
// 這可以用來更新 UI 元素的狀態
if (window.bubble_fn_toggleComplete) {
    window.bubble_fn_toggleComplete(window.markersCurrentlyVisible);
}