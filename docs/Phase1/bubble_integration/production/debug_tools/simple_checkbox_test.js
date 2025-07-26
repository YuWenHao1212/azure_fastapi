// ========================================
// 簡化版 Checkbox 測試代碼
// 用於替代原有 checkbox 代碼進行測試
// ========================================

// 簡化版 New Section Checkbox
function simpleNewSectionToggle() {
    console.log('🔄 開始簡化版 New Section 切換...');
    
    // 1. 基本檢查
    if (typeof tinymce === 'undefined') {
        console.error('❌ TinyMCE 未載入');
        return;
    }
    
    if (!window.markersVisible) {
        console.warn('⚠️ 主開關已關閉');
        return;
    }
    
    // 2. 獲取編輯器
    const editors = tinymce.get();
    if (!editors || editors.length === 0) {
        console.error('❌ 未找到編輯器');
        return;
    }
    
    const editorArray = Array.isArray(editors) ? editors : [editors];
    console.log(`📝 找到 ${editorArray.length} 個編輯器`);
    
    // 3. 初始化 tagVisibility
    if (!window.tagVisibility) {
        window.tagVisibility = {};
    }
    
    if (typeof window.tagVisibility['opt-new'] === 'undefined') {
        window.tagVisibility['opt-new'] = true;
    }
    
    // 4. 切換狀態
    const oldState = window.tagVisibility['opt-new'];
    window.tagVisibility['opt-new'] = !window.tagVisibility['opt-new'];
    const newState = window.tagVisibility['opt-new'];
    
    console.log(`🔄 狀態切換: ${oldState} -> ${newState}`);
    
    // 5. 應用到所有編輯器
    let successCount = 0;
    editorArray.forEach((editor, index) => {
        if (!editor || !editor.initialized) {
            console.warn(`⚠️ 編輯器 ${index + 1} 未初始化`);
            return;
        }
        
        const body = editor.getBody();
        if (!body) {
            console.warn(`⚠️ 編輯器 ${index + 1} 無 body 元素`);
            return;
        }
        
        const className = 'hide-opt-new';
        
        try {
            if (newState) {
                // 顯示標記 - 移除 hide 類
                body.classList.remove(className);
                console.log(`✅ 編輯器 ${index + 1}: 移除 ${className}`);
            } else {
                // 隱藏標記 - 添加 hide 類
                body.classList.add(className);
                console.log(`✅ 編輯器 ${index + 1}: 添加 ${className}`);
            }
            
            // 驗證
            const hasClass = body.classList.contains(className);
            console.log(`🔍 編輯器 ${index + 1} 驗證: has '${className}' = ${hasClass}`);
            
            successCount++;
        } catch (error) {
            console.error(`❌ 編輯器 ${index + 1} 處理失敗:`, error);
        }
    });
    
    console.log(`✅ 成功處理 ${successCount}/${editorArray.length} 個編輯器`);
    console.log(`📊 最終狀態: opt-new = ${newState ? 'VISIBLE' : 'HIDDEN'}`);
    
    return {
        success: successCount > 0,
        processedEditors: successCount,
        totalEditors: editorArray.length,
        finalState: newState
    };
}

// 測試所有標記類型的函數
function testAllMarkerTypes() {
    console.log('🧪 測試所有標記類型...');
    
    const markerTypes = [
        'opt-new',
        'opt-modified', 
        'opt-placeholder',
        'opt-keyword',
        'opt-keyword-existing'
    ];
    
    markerTypes.forEach(markerType => {
        console.log(`\n--- 測試 ${markerType} ---`);
        testSingleMarkerType(markerType);
    });
}

function testSingleMarkerType(markerType) {
    // 基本檢查
    if (typeof tinymce === 'undefined') {
        console.error('❌ TinyMCE 未載入');
        return;
    }
    
    const editors = tinymce.get();
    if (!editors || editors.length === 0) {
        console.error('❌ 未找到編輯器');
        return;
    }
    
    const editorArray = Array.isArray(editors) ? editors : [editors];
    
    // 初始化狀態
    if (!window.tagVisibility) {
        window.tagVisibility = {};
    }
    
    if (typeof window.tagVisibility[markerType] === 'undefined') {
        window.tagVisibility[markerType] = true;
    }
    
    // 切換狀態
    const oldState = window.tagVisibility[markerType];
    window.tagVisibility[markerType] = !window.tagVisibility[markerType];
    const newState = window.tagVisibility[markerType];
    
    console.log(`🔄 ${markerType}: ${oldState} -> ${newState}`);
    
    // 應用到編輯器
    const className = `hide-${markerType}`;
    editorArray.forEach((editor, index) => {
        if (editor && editor.initialized) {
            const body = editor.getBody();
            if (body) {
                if (newState) {
                    body.classList.remove(className);
                } else {
                    body.classList.add(className);
                }
                console.log(`編輯器 ${index + 1}: ${className} = ${body.classList.contains(className)}`);
            }
        }
    });
}

// 檢查頁面上的實際標記元素
function checkActualMarkers() {
    console.log('🔍 檢查頁面上的實際標記元素...');
    
    if (typeof tinymce === 'undefined') {
        console.error('❌ TinyMCE 未載入');
        return;
    }
    
    const editors = tinymce.get();
    if (!editors || editors.length === 0) {
        console.error('❌ 未找到編輯器');
        return;
    }
    
    const editorArray = Array.isArray(editors) ? editors : [editors];
    
    editorArray.forEach((editor, index) => {
        if (editor && editor.initialized) {
            console.log(`\n📝 編輯器 ${index + 1} (${editor.id}):`);
            
            const markerTypes = ['opt-new', 'opt-modified', 'opt-placeholder', 'opt-keyword', 'opt-keyword-existing'];
            
            markerTypes.forEach(type => {
                const elements = editor.dom.select(`.${type}`);
                console.log(`  ${type}: ${elements.length} 個元素`);
                
                if (elements.length > 0 && type === 'opt-new') {
                    elements.forEach((el, i) => {
                        const style = window.getComputedStyle(el);
                        console.log(`    元素 ${i + 1}: border-left = ${style.borderLeft}`);
                    });
                }
            });
        }
    });
}

// 提供簡單的調用方法
console.log('🛠️ 簡化版測試工具已載入');
console.log('💡 可用命令:');
console.log('  simpleNewSectionToggle() - 測試 New Section 切換');
console.log('  testAllMarkerTypes() - 測試所有標記類型');
console.log('  checkActualMarkers() - 檢查實際標記元素');
console.log('  testSingleMarkerType("opt-new") - 測試特定標記類型');