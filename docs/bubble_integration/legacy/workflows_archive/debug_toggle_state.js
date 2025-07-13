// ========================================
// 診斷 Toggle 狀態問題
// 在 Console 執行來了解狀態
// ========================================

console.log('===== Toggle 狀態診斷 =====');

// 1. 檢查所有相關變數
console.log('\n1. 全局變數狀態:');
console.log('window.markersVisible:', window.markersVisible);
console.log('window.markersCurrentlyVisible:', window.markersCurrentlyVisible);
console.log('window.markerStylesInjected:', window.markerStylesInjected);
console.log('window.newSectionVisible:', window.newSectionVisible);
console.log('window.modificationVisible:', window.modificationVisible);
console.log('window.placeholdersVisible:', window.placeholdersVisible);
console.log('window.newKeywordsVisible:', window.newKeywordsVisible);
console.log('window.existingKeywordsVisible:', window.existingKeywordsVisible);

// 2. 檢查編輯器實際狀態
console.log('\n2. 編輯器實際狀態:');
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        editorArray.forEach((editor, i) => {
            const body = editor.getBody();
            if (body) {
                console.log(`\n編輯器 ${i + 1} (${editor.id}):`);
                console.log('  markers-hidden:', body.classList.contains('markers-hidden'));
                
                // 檢查 hide- classes
                const hideClasses = [];
                ['hide-opt-new', 'hide-opt-modified', 'hide-opt-placeholder', 
                 'hide-opt-keyword', 'hide-opt-keyword-existing'].forEach(cls => {
                    if (body.classList.contains(cls)) {
                        hideClasses.push(cls);
                    }
                });
                
                if (hideClasses.length > 0) {
                    console.log('  hide- classes:', hideClasses.join(', '));
                }
                
                console.log('  所有 classes:', body.className);
            }
        });
    }
}

// 3. 測試手動 toggle
console.log('\n3. 測試手動 Toggle:');
console.log('執行前 markersVisible:', window.markersVisible);

// 手動執行 toggle
if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        editorArray.forEach(editor => {
            const body = editor.getBody();
            if (body) {
                if (body.classList.contains('markers-hidden')) {
                    body.classList.remove('markers-hidden');
                } else {
                    body.classList.add('markers-hidden');
                }
            }
        });
    }
}

console.log('執行後檢查編輯器...');
setTimeout(() => {
    if (typeof tinymce !== 'undefined') {
        const editors = tinymce.get();
        if (editors) {
            const editorArray = Array.isArray(editors) ? editors : [editors];
            editorArray.forEach((editor, i) => {
                const body = editor.getBody();
                if (body) {
                    console.log(`編輯器 ${i + 1}: markers-hidden =`, body.classList.contains('markers-hidden'));
                }
            });
        }
    }
}, 100);

// 4. 修復建議
console.log('\n4. 修復建議:');
console.log('執行以下命令來重置狀態:');
console.log('window.resetToggleState()');

// 提供重置函數
window.resetToggleState = function() {
    // 統一所有狀態
    window.markersVisible = true;
    window.markersCurrentlyVisible = true;
    window.newSectionVisible = true;
    window.modificationVisible = true;
    window.placeholdersVisible = true;
    window.newKeywordsVisible = true;
    window.existingKeywordsVisible = true;
    
    // 顯示所有標記
    if (typeof tinymce !== 'undefined') {
        const editors = tinymce.get();
        if (editors) {
            const editorArray = Array.isArray(editors) ? editors : [editors];
            editorArray.forEach(editor => {
                const body = editor.getBody();
                if (body) {
                    // 移除所有隱藏相關的 classes
                    body.classList.remove('markers-hidden');
                    ['hide-opt-new', 'hide-opt-modified', 'hide-opt-placeholder', 
                     'hide-opt-keyword', 'hide-opt-keyword-existing'].forEach(cls => {
                        body.classList.remove(cls);
                    });
                }
            });
        }
    }
    
    console.log('✅ 狀態已重置，所有標記應該顯示');
};