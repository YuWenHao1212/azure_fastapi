// ========================================
// 緊急修復：Toggle 功能恢復
// 直接在 Console 執行或放入 Bubble workflow
// ========================================

// 立即執行的修復函數
(function emergencyFix() {
    console.log('[緊急修復] 開始恢復 Toggle 功能...');
    
    // 1. 重建 toggleMarkers 函數（簡單版本）
    window.toggleMarkers = function() {
        console.log('[Toggle] 執行切換...');
        
        if (typeof tinymce === 'undefined') {
            console.error('[Toggle] TinyMCE 未載入！');
            return;
        }
        
        const editors = tinymce.get();
        if (!editors) {
            console.error('[Toggle] 沒有找到編輯器！');
            return;
        }
        
        // 轉換為陣列
        const editorArray = Array.isArray(editors) ? editors : [editors];
        console.log(`[Toggle] 找到 ${editorArray.length} 個編輯器`);
        
        // 對每個編輯器切換狀態
        editorArray.forEach((editor, index) => {
            if (!editor.initialized) {
                console.log(`[Toggle] 編輯器 ${index + 1} 未初始化，跳過`);
                return;
            }
            
            const body = editor.getBody();
            if (!body) {
                console.log(`[Toggle] 編輯器 ${index + 1} 沒有 body，跳過`);
                return;
            }
            
            // 切換 markers-hidden class
            if (body.classList.contains('markers-hidden')) {
                body.classList.remove('markers-hidden');
                console.log(`[Toggle] 編輯器 ${index + 1} (${editor.id}): 顯示標記`);
            } else {
                body.classList.add('markers-hidden');
                console.log(`[Toggle] 編輯器 ${index + 1} (${editor.id}): 隱藏標記`);
            }
        });
        
        // 更新全局狀態
        if (window.markersVisible !== undefined) {
            window.markersVisible = !window.markersVisible;
        }
        
        console.log('[Toggle] 切換完成！');
    };
    
    // 2. 重建 showMarkers 函數
    window.showMarkers = function() {
        console.log('[Toggle] 顯示所有標記...');
        
        const editors = tinymce.get();
        if (!editors) return;
        
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        editorArray.forEach(editor => {
            const body = editor.getBody();
            if (body) {
                body.classList.remove('markers-hidden');
            }
        });
        
        window.markersVisible = true;
    };
    
    // 3. 重建 hideMarkers 函數
    window.hideMarkers = function() {
        console.log('[Toggle] 隱藏所有標記...');
        
        const editors = tinymce.get();
        if (!editors) return;
        
        const editorArray = Array.isArray(editors) ? editors : [editors];
        
        editorArray.forEach(editor => {
            const body = editor.getBody();
            if (body) {
                body.classList.add('markers-hidden');
            }
        });
        
        window.markersVisible = false;
    };
    
    // 4. 確保樣式存在
    const criticalStyles = `
        /* 隱藏標記的核心樣式 */
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
            border-left: none !important;
            padding-left: 0 !important;
            background-color: transparent !important;
        }
    `;
    
    // 注入樣式到所有編輯器
    if (typeof tinymce !== 'undefined') {
        const editors = tinymce.get();
        if (editors) {
            const editorArray = Array.isArray(editors) ? editors : [editors];
            
            editorArray.forEach((editor, index) => {
                if (editor.initialized) {
                    try {
                        // 注入樣式
                        editor.dom.addStyle(criticalStyles);
                        console.log(`[緊急修復] ✅ 樣式已注入到編輯器 ${index + 1} (${editor.id})`);
                    } catch (e) {
                        console.error(`[緊急修復] ❌ 無法注入樣式到編輯器 ${index + 1}:`, e);
                    }
                }
            });
        }
    }
    
    console.log('\n[緊急修復] ✅ 修復完成！');
    console.log('[緊急修復] 可用命令:');
    console.log('  - toggleMarkers()  // 切換標記顯示/隱藏');
    console.log('  - showMarkers()    // 顯示所有標記');
    console.log('  - hideMarkers()    // 隱藏所有標記');
    
    // 5. 自動測試
    console.log('\n[緊急修復] 執行測試...');
    if (window.toggleMarkers) {
        window.toggleMarkers();
        setTimeout(() => {
            window.toggleMarkers();
            console.log('[緊急修復] 測試完成！Toggle 功能應該已經恢復。');
        }, 1000);
    }
    
})();

// 額外提供一個簡單的測試函數
window.testToggle = function() {
    console.log('=== 測試 Toggle 功能 ===');
    
    const editors = tinymce.get();
    if (!editors) {
        console.error('沒有找到編輯器');
        return;
    }
    
    const editorArray = Array.isArray(editors) ? editors : [editors];
    
    console.log('當前狀態:');
    editorArray.forEach((editor, i) => {
        const body = editor.getBody();
        if (body) {
            console.log(`  編輯器 ${i + 1}: markers-hidden = ${body.classList.contains('markers-hidden')}`);
        }
    });
    
    console.log('\n執行 toggle...');
    window.toggleMarkers();
    
    setTimeout(() => {
        console.log('\n新狀態:');
        editorArray.forEach((editor, i) => {
            const body = editor.getBody();
            if (body) {
                console.log(`  編輯器 ${i + 1}: markers-hidden = ${body.classList.contains('markers-hidden')}`);
            }
        });
    }, 500);
};