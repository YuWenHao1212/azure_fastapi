// ========================================
// Toggle 功能診斷腳本
// 直接在瀏覽器 Console 執行
// ========================================

console.log('===== 開始 Toggle 功能診斷 =====');

// 1. 檢查 TinyMCE 狀態
console.log('\n1. TinyMCE 狀態檢查:');
if (typeof tinymce === 'undefined') {
    console.error('❌ TinyMCE 未載入！');
} else {
    console.log('✅ TinyMCE 已載入');
    const editors = tinymce.get();
    console.log(`編輯器數量: ${editors ? editors.length : 0}`);
    
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        editorArray.forEach((editor, i) => {
            console.log(`\n編輯器 ${i + 1}:`);
            console.log(`  ID: ${editor.id}`);
            console.log(`  初始化: ${editor.initialized}`);
            console.log(`  模式: ${editor.mode.get()}`);
            
            const body = editor.getBody();
            if (body) {
                console.log(`  Body classes: ${body.className}`);
                console.log(`  Has markers-hidden: ${body.classList.contains('markers-hidden')}`);
                
                // 檢查樣式標籤
                const doc = editor.getDoc();
                const styles = doc ? doc.querySelectorAll('style') : [];
                console.log(`  Style 標籤數量: ${styles.length}`);
                
                // 列出所有 style 標籤的 ID
                styles.forEach((style, j) => {
                    if (style.id) {
                        console.log(`    Style ${j + 1} ID: ${style.id}`);
                    }
                });
            }
        });
    }
}

// 2. 檢查全局函數
console.log('\n2. 全局函數檢查:');
const functionsToCheck = [
    'toggleMarkers',
    'showMarkers', 
    'hideMarkers',
    'toggleTinyMCEMarkers',
    'injectDefaultMarkerStyles',
    'forEachEditor',
    'getAllTinyMCEEditors'
];

functionsToCheck.forEach(func => {
    const exists = typeof window[func] === 'function';
    console.log(`  window.${func}: ${exists ? '✅ 存在' : '❌ 不存在'}`);
});

// 3. 檢查全局變數
console.log('\n3. 全局變數檢查:');
console.log(`  window.markersVisible: ${window.markersVisible}`);
console.log(`  window.markerStylesInjected: ${window.markerStylesInjected}`);
console.log(`  window.tagVisibility:`, window.tagVisibility);

// 4. 測試 toggle 功能
console.log('\n4. 測試 Toggle 功能:');

// 測試 hideMarkers
if (typeof window.hideMarkers === 'function') {
    console.log('執行 hideMarkers()...');
    try {
        window.hideMarkers();
        console.log('✅ hideMarkers 執行成功');
        
        // 檢查結果
        setTimeout(() => {
            const editors = tinymce.get();
            if (editors) {
                const editorArray = Array.isArray(editors) ? editors : [editors];
                editorArray.forEach((editor, i) => {
                    const body = editor.getBody();
                    if (body) {
                        console.log(`  編輯器 ${i + 1} markers-hidden: ${body.classList.contains('markers-hidden')}`);
                    }
                });
            }
        }, 500);
        
    } catch (e) {
        console.error('❌ hideMarkers 錯誤:', e);
    }
} else {
    console.error('❌ hideMarkers 函數不存在');
}

// 5. 手動測試 toggle
console.log('\n5. 手動 Toggle 測試:');
console.log('嘗試手動切換標記...');

// 直接操作編輯器
if (tinymce && tinymce.activeEditor) {
    const editor = tinymce.activeEditor;
    const body = editor.getBody();
    
    if (body) {
        const currentHidden = body.classList.contains('markers-hidden');
        console.log(`當前狀態 markers-hidden: ${currentHidden}`);
        
        if (currentHidden) {
            body.classList.remove('markers-hidden');
            console.log('已移除 markers-hidden class');
        } else {
            body.classList.add('markers-hidden');
            console.log('已添加 markers-hidden class');
        }
        
        console.log(`新狀態 markers-hidden: ${body.classList.contains('markers-hidden')}`);
    }
}

// 6. 檢查樣式內容
console.log('\n6. 檢查樣式是否正確注入:');
if (tinymce && tinymce.activeEditor) {
    const editor = tinymce.activeEditor;
    const doc = editor.getDoc();
    
    // 檢查是否有標記元素
    const markerElements = {
        'opt-keyword-existing': editor.dom.select('span.opt-keyword-existing').length,
        'opt-keyword': editor.dom.select('span.opt-keyword').length,
        'opt-modified': editor.dom.select('span.opt-modified').length,
        'opt-new': editor.dom.select('.opt-new').length,
        'opt-placeholder': editor.dom.select('span.opt-placeholder').length
    };
    
    console.log('標記元素數量:');
    Object.entries(markerElements).forEach(([className, count]) => {
        console.log(`  .${className}: ${count} 個`);
    });
}

console.log('\n===== 診斷完成 =====');
console.log('\n建議的修復步驟:');
console.log('1. 如果函數不存在，需要重新載入 page header');
console.log('2. 如果標記元素存在但樣式無效，檢查 CSS 優先級');
console.log('3. 使用下方的快速修復函數');

// 提供快速修復函數
window.quickFixToggle = function() {
    console.log('\n執行快速修復...');
    
    // 確保函數存在
    if (typeof window.toggleMarkers !== 'function') {
        window.toggleMarkers = function() {
            if (typeof tinymce === 'undefined') return;
            
            const editors = tinymce.get();
            if (!editors) return;
            
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
            
            console.log('Toggle 完成！');
        };
        
        console.log('✅ toggleMarkers 函數已重建');
    }
    
    // 重新注入樣式
    const styles = `
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
    `;
    
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        editorArray.forEach(editor => {
            editor.dom.addStyle(styles);
        });
        console.log('✅ 樣式已重新注入');
    }
    
    console.log('修復完成！現在可以使用 toggleMarkers() 或 quickFixToggle()');
};

console.log('\n💡 提示: 執行 quickFixToggle() 來嘗試快速修復');