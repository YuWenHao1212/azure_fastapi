// ========================================
// Checkbox 功能診斷腳本
// 在 Console 中執行以診斷問題
// ========================================

function runCheckboxDiagnostic() {
    console.log('='.repeat(60));
    console.log('🔍 開始 Checkbox 功能診斷');
    console.log('='.repeat(60));
    
    // 1. 檢查基本環境
    console.log('\n📋 1. 基本環境檢查:');
    console.log('TinyMCE 載入:', typeof tinymce !== 'undefined' ? '✅' : '❌');
    console.log('markersVisible:', window.markersVisible);
    console.log('tagVisibility 存在:', typeof window.tagVisibility !== 'undefined' ? '✅' : '❌');
    
    if (typeof window.tagVisibility !== 'undefined') {
        console.log('tagVisibility 內容:', window.tagVisibility);
    }
    
    // 2. 檢查編輯器狀態
    console.log('\n📝 2. 編輯器狀態檢查:');
    if (typeof getAllTinyMCEEditors === 'function') {
        const editors = getAllTinyMCEEditors();
        console.log('編輯器數量:', editors.length);
        
        editors.forEach((editor, i) => {
            console.log(`編輯器 ${i + 1}:`);
            console.log(`  - ID: ${editor.id}`);
            console.log(`  - 已初始化: ${editor.initialized}`);
            
            const body = editor.getBody();
            if (body) {
                console.log(`  - Body 存在: ✅`);
                console.log(`  - Body classes: ${body.className}`);
                console.log(`  - Has hide-opt-new: ${body.classList.contains('hide-opt-new')}`);
            } else {
                console.log(`  - Body 存在: ❌`);
            }
        });
    } else {
        console.log('❌ getAllTinyMCEEditors 函數不存在');
    }
    
    // 3. 檢查函數存在性
    console.log('\n🔧 3. 關鍵函數檢查:');
    const functions = [
        'toggleSingleTag',
        'getAllTinyMCEEditors', 
        'forEachEditor',
        'diagnoseMarkerSystem'
    ];
    
    functions.forEach(funcName => {
        const exists = typeof window[funcName] === 'function';
        console.log(`${funcName}: ${exists ? '✅' : '❌'}`);
    });
    
    // 4. 測試 opt-new 具體標記
    console.log('\n🎯 4. opt-new 標記檢查:');
    if (typeof tinymce !== 'undefined') {
        const editors = getAllTinyMCEEditors();
        editors.forEach((editor, i) => {
            const optNewElements = editor.dom.select('.opt-new');
            console.log(`編輯器 ${i + 1} 中的 .opt-new 元素數量: ${optNewElements.length}`);
            
            if (optNewElements.length > 0) {
                console.log('找到的 opt-new 元素:', optNewElements);
            }
        });
    }
    
    // 5. 手動測試 toggleSingleTag
    console.log('\n🧪 5. 手動測試 toggleSingleTag:');
    if (typeof window.toggleSingleTag === 'function') {
        console.log('準備測試 opt-new 切換...');
        
        // 記錄切換前狀態
        const beforeState = window.tagVisibility ? window.tagVisibility['opt-new'] : undefined;
        console.log('切換前狀態:', beforeState);
        
        // 執行切換
        try {
            window.toggleSingleTag('opt-new');
            
            // 記錄切換後狀態
            const afterState = window.tagVisibility ? window.tagVisibility['opt-new'] : undefined;
            console.log('切換後狀態:', afterState);
            
            if (beforeState !== afterState) {
                console.log('✅ 狀態切換成功');
            } else {
                console.log('❌ 狀態沒有改變');
            }
        } catch (error) {
            console.error('❌ toggleSingleTag 執行錯誤:', error);
        }
    } else {
        console.log('❌ toggleSingleTag 函數不存在');
    }
    
    // 6. CSS 樣式檢查
    console.log('\n🎨 6. CSS 樣式檢查:');
    if (typeof tinymce !== 'undefined') {
        const editors = getAllTinyMCEEditors();
        editors.forEach((editor, i) => {
            const hasMultiTagStyles = editor.dom.get('multi-tag-styles');
            console.log(`編輯器 ${i + 1} 多標記樣式已注入: ${hasMultiTagStyles ? '✅' : '❌'}`);
        });
    }
    
    console.log('\n='.repeat(60));
    console.log('🏁 診斷完成');
    console.log('='.repeat(60));
    
    // 7. 建議修復步驟
    console.log('\n💡 建議修復步驟:');
    console.log('1. 如果編輯器數量為 0，請等待 TinyMCE 完全載入');
    console.log('2. 如果 Body 不存在，可能是編輯器初始化問題');
    console.log('3. 如果多標記樣式未注入，執行: window.injectMultiTagStyles()');
    console.log('4. 如果狀態沒有改變，可能是雙重切換問題');
    console.log('5. 如果有 .opt-new 元素但不響應，可能是 CSS 優先級問題');
}

// 立即執行診斷
runCheckboxDiagnostic();