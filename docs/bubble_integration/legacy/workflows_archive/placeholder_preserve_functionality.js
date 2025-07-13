// === 保留 Placeholder 原有功能的方案 ===

// 方案 1: 修改 toggleSingleTag 函數，特殊處理 placeholder
window.toggleSingleTagWithPreserve = function(tagType, show) {
    // 如果是 placeholder，使用不同的處理方式
    if (tagType === 'opt-placeholder') {
        try {
            if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
                console.error('❌ TinyMCE 編輯器未找到');
                return false;
            }
            
            const editor = tinymce.activeEditor;
            const iframeDoc = editor.getDoc();
            
            // 確保有特殊的 placeholder 樣式
            let placeholderStyle = iframeDoc.getElementById('placeholder-special-style');
            if (!placeholderStyle) {
                placeholderStyle = iframeDoc.createElement('style');
                placeholderStyle.id = 'placeholder-special-style';
                iframeDoc.head.appendChild(placeholderStyle);
            }
            
            if (show) {
                // 顯示：移除特殊樣式
                placeholderStyle.textContent = '';
                console.log('🟢 顯示 placeholder（完整功能）');
            } else {
                // "隱藏"：只是視覺上變淡，保持所有功能
                placeholderStyle.textContent = `
                    .opt-placeholder {
                        opacity: 0.4 !important;
                        /* 保留所有其他樣式和功能 */
                    }
                    
                    .opt-placeholder:hover {
                        opacity: 1 !important;
                        cursor: pointer !important;
                    }
                `;
                console.log('🔴 Placeholder 視覺變淡（功能保留）');
            }
            
            return true;
            
        } catch (error) {
            console.error('❌ 處理 placeholder 時發生錯誤:', error);
            return false;
        }
    } else {
        // 其他標記使用原本的函數
        return window.toggleSingleTag(tagType, show);
    }
};

// 方案 2: 檢查並保護 placeholder 的原有事件
window.protectPlaceholderEvents = function() {
    console.log('🛡️ 保護 Placeholder 事件...');
    
    try {
        if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
            return false;
        }
        
        const editor = tinymce.activeEditor;
        
        // 保存原有的 placeholder 處理邏輯
        if (!window._originalPlaceholderHandler) {
            // 嘗試找到原有的事件處理器
            const originalClickHandler = editor.getBody().onclick;
            if (originalClickHandler) {
                window._originalPlaceholderHandler = originalClickHandler;
                console.log('✅ 已保存原有的點擊處理器');
            }
        }
        
        // 確保 placeholder 始終可編輯
        const placeholders = editor.getBody().querySelectorAll('.opt-placeholder');
        placeholders.forEach(ph => {
            // 不要設置 contenteditable="false"
            ph.removeAttribute('contenteditable');
            // 確保有正確的樣式
            ph.style.cursor = 'pointer';
        });
        
        return true;
        
    } catch (error) {
        console.error('❌ 保護事件時發生錯誤:', error);
        return false;
    }
};