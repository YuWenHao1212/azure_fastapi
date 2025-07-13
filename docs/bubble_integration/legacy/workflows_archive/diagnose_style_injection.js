// ========================================
// 診斷：檢查樣式注入狀況
// 在 Console 執行來了解問題
// ========================================

console.log('===== 開始診斷樣式注入問題 =====\n');

// 1. 檢查編輯器狀態
console.log('1. 編輯器狀態:');
if (typeof tinymce === 'undefined') {
    console.error('❌ TinyMCE 未載入');
} else {
    const editors = tinymce.get();
    const editorArray = Array.isArray(editors) ? editors : [editors];
    
    editorArray.forEach((editor, i) => {
        console.log(`\n編輯器 ${i + 1} (${editor.id}):`);
        
        const body = editor.getBody();
        const doc = editor.getDoc();
        
        // 檢查 body class
        console.log(`  markers-hidden class: ${body ? body.classList.contains('markers-hidden') : 'N/A'}`);
        
        // 檢查 style 標籤
        if (doc) {
            const styles = doc.querySelectorAll('style');
            console.log(`  <style> 標籤數量: ${styles.length}`);
            
            // 列出所有 style 標籤的 ID
            styles.forEach((style, j) => {
                if (style.id) {
                    console.log(`    - ${style.id}`);
                }
            });
            
            // 檢查是否有包含關鍵字樣式的 style 標籤
            let hasKeywordStyles = false;
            let hasHiddenStyles = false;
            
            styles.forEach(style => {
                const content = style.textContent || style.innerHTML;
                if (content.includes('opt-keyword-existing')) {
                    hasKeywordStyles = true;
                }
                if (content.includes('markers-hidden')) {
                    hasHiddenStyles = true;
                }
            });
            
            console.log(`  包含關鍵字樣式: ${hasKeywordStyles ? '✅' : '❌'}`);
            console.log(`  包含隱藏樣式: ${hasHiddenStyles ? '✅' : '❌'}`);
        }
        
        // 檢查實際元素
        if (editor.dom) {
            const testElements = {
                'opt-keyword-existing': editor.dom.select('span.opt-keyword-existing'),
                'opt-keyword': editor.dom.select('span.opt-keyword'),
                'opt-modified': editor.dom.select('span.opt-modified'),
                'opt-new': editor.dom.select('.opt-new'),
                'opt-placeholder': editor.dom.select('span.opt-placeholder')
            };
            
            console.log(`  標記元素:`);
            Object.entries(testElements).forEach(([className, elements]) => {
                if (elements.length > 0) {
                    console.log(`    - .${className}: ${elements.length} 個`);
                    
                    // 檢查第一個元素的實際樣式
                    if (elements[0]) {
                        const computed = editor.getWin().getComputedStyle(elements[0]);
                        const isHidden = computed.backgroundColor === 'rgba(0, 0, 0, 0)' || 
                                       computed.backgroundColor === 'transparent';
                        console.log(`      背景色: ${computed.backgroundColor} ${isHidden ? '(透明)' : ''}`);
                    }
                }
            });
        }
    });
}

// 2. 測試樣式注入
console.log('\n\n2. 測試重新注入顯示樣式:');

const displayStyles = `
    /* 測試：強制顯示樣式 */
    span.opt-keyword-existing {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        padding: 3px 8px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        margin: 0 2px !important;
        display: inline-block !important;
    }
    
    span.opt-keyword {
        background-color: transparent !important;
        color: #6366F1 !important;
        border: 1px solid #C7D2FE !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
        font-weight: 500 !important;
        margin: 0 2px !important;
        display: inline-block !important;
    }
    
    span.opt-modified {
        background-color: #FFF3CD !important;
        color: #856404 !important;
        padding: 2px 6px !important;
        border-radius: 3px !important;
        border: 1px solid #FFEAA7 !important;
        display: inline !important;
    }
    
    .opt-new {
        border-left: 4px solid #10B981 !important;
        padding-left: 16px !important;
        background-color: rgba(209, 250, 229, 0.3) !important;
        display: block !important;
    }
    
    span.opt-placeholder {
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        border: 1px dashed #F87171 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
        font-style: italic !important;
        display: inline-block !important;
    }
`;

if (typeof tinymce !== 'undefined') {
    const editors = tinymce.get();
    const editorArray = Array.isArray(editors) ? editors : [editors];
    
    editorArray.forEach((editor, i) => {
        if (editor && editor.initialized) {
            try {
                // 先移除 markers-hidden（確保顯示狀態）
                const body = editor.getBody();
                if (body) {
                    body.classList.remove('markers-hidden');
                }
                
                // 注入顯示樣式
                editor.dom.addStyle(displayStyles);
                console.log(`✅ 已重新注入顯示樣式到編輯器 ${i + 1}`);
                
            } catch (e) {
                console.error(`❌ 無法注入樣式到編輯器 ${i + 1}:`, e);
            }
        }
    });
}

// 3. 提供修復函數
console.log('\n\n3. 修復函數已準備:');

window.fixToggleDisplay = function() {
    console.log('執行修復...');
    
    const fullStyles = `
        /* 顯示樣式 */
        span.opt-keyword-existing {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            padding: 3px 8px !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            margin: 0 2px !important;
            display: inline-block !important;
        }
        
        span.opt-keyword {
            color: #6366F1 !important;
            border: 1px solid #C7D2FE !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            display: inline-block !important;
        }
        
        span.opt-modified {
            background-color: #FFF3CD !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
        }
        
        .opt-new {
            border-left: 4px solid #10B981 !important;
            padding-left: 16px !important;
            background-color: rgba(209, 250, 229, 0.3) !important;
        }
        
        span.opt-placeholder {
            background-color: #FEE2E2 !important;
            color: #991B1B !important;
            border: 1px dashed #F87171 !important;
            padding: 2px 8px !important;
            font-style: italic !important;
        }
        
        /* 隱藏樣式 */
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
            display: inline !important;
        }
    `;
    
    const editors = tinymce.get();
    if (editors) {
        const editorArray = Array.isArray(editors) ? editors : [editors];
        editorArray.forEach(editor => {
            if (editor.initialized) {
                editor.dom.addStyle(fullStyles);
            }
        });
        console.log('✅ 樣式已重新注入到所有編輯器');
    }
};

console.log('執行 fixToggleDisplay() 來修復顯示問題');

console.log('\n===== 診斷完成 =====');