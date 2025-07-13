// TinyMCE 多編輯器樣式注入腳本
// 支援同一頁面多個 TinyMCE 實例
// 用於 Bubble.io "page is loaded" workflow
// 創建日期: 2025-07-13

function injectStylesToAllEditors() {
    if (typeof tinymce === 'undefined') {
        console.log('TinyMCE 未載入，1秒後重試...');
        setTimeout(injectStylesToAllEditors, 1000);
        return;
    }
    
    // 定義要注入的完整 CSS
    var fullCSS = `
        /* 1. 新增內容 - 綠色左邊框 */
        .opt-new {
            border-left: 4px solid #10B981 !important;
            padding-left: 16px !important;
            background-color: rgba(209, 250, 229, 0.1) !important;
            margin-left: -20px !important;
            padding-right: 16px !important;
        }
        
        h2.opt-new, h3.opt-new {
            background-color: transparent !important;
        }
        
        /* 2. 修改內容 - 淺黃色背景 - 只在 span 上 */
        span.opt-modified {
            background-color: #FFF3CD !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            display: inline !important;
            line-height: inherit !important;
        }
        
        /* 防止錯誤使用在區塊元素上 */
        li.opt-modified,
        p.opt-modified,
        h1.opt-modified,
        h2.opt-modified,
        h3.opt-modified,
        h4.opt-modified,
        h5.opt-modified {
            background-color: transparent !important;
            background: none !important;
            color: inherit !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }
        
        /* 3. 新增關鍵字 - 紫色邊框（低調，需確認） */
        span.opt-keyword {
            background-color: transparent !important;
            color: #6366F1 !important;
            border: 1px solid #C7D2FE !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            font-weight: 500 !important;
            margin: 0 2px !important;
        }
        
        /* 4. 原有關鍵字 - 深藍色背景（醒目強調） */
        span.opt-keyword-existing {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            padding: 3px 8px !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            margin: 0 2px !important;
            box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3) !important;
        }
        
        /* 5. 佔位符 - 紅色虛線框 */
        span.opt-placeholder {
            background-color: #FEE2E2 !important;
            color: #991B1B !important;
            border: 1px dashed #F87171 !important;
            padding: 2px 8px !important;
            border-radius: 4px !important;
            font-style: italic !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            margin: 0 2px !important;
        }
        
        span.opt-placeholder:hover {
            background-color: #FECACA !important;
            border-color: #EF4444 !important;
        }
        
        /* 6. 已編輯內容 - 綠色底線 */
        span.opt-improvement {
            border-bottom: 2px solid #10B981 !important;
            color: #065F46 !important;
            padding-bottom: 1px !important;
            font-weight: 500 !important;
        }
        
        /* 防止關鍵字標記錯誤應用在區塊元素上 */
        li.opt-keyword,
        p.opt-keyword,
        h1.opt-keyword,
        h2.opt-keyword,
        h3.opt-keyword,
        h4.opt-keyword,
        h5.opt-keyword,
        li.opt-keyword-existing,
        p.opt-keyword-existing,
        h1.opt-keyword-existing,
        h2.opt-keyword-existing,
        h3.opt-keyword-existing,
        h4.opt-keyword-existing,
        h5.opt-keyword-existing {
            background-color: transparent !important;
            background: none !important;
            color: inherit !important;
            padding: 0 !important;
            border: none !important;
            border-radius: 0 !important;
        }
    `;
    
    // 獲取所有編輯器
    var editors = tinymce.editors;
    var injectedCount = 0;
    
    if (editors.length === 0) {
        console.log('尚無 TinyMCE 編輯器，1秒後重試...');
        setTimeout(injectStylesToAllEditors, 1000);
        return;
    }
    
    // 為每個編輯器注入樣式
    editors.forEach(function(editor, index) {
        if (editor && !editor.isHidden()) {
            // 檢查是否已經注入過樣式（避免重複）
            if (!editor.dom || editor.dom.hasClass(editor.getBody(), 'styles-injected')) {
                console.log(`編輯器 ${index + 1} 尚未準備好或已注入樣式`);
                return;
            }
            
            // 注入樣式
            editor.dom.addStyle(fullCSS);
            
            // 標記已注入
            editor.dom.addClass(editor.getBody(), 'styles-injected');
            
            injectedCount++;
            console.log(`已向編輯器 ${index + 1} (ID: ${editor.id}) 注入樣式`);
        }
    });
    
    console.log(`總共向 ${injectedCount} 個編輯器注入了樣式`);
    
    // 監聽新編輯器的初始化
    if (!window.tinyMCEStylesListener) {
        tinymce.on('AddEditor', function(e) {
            console.log('檢測到新編輯器:', e.editor.id);
            
            // 等待編輯器完全初始化
            e.editor.on('init', function() {
                setTimeout(function() {
                    if (!e.editor.dom.hasClass(e.editor.getBody(), 'styles-injected')) {
                        e.editor.dom.addStyle(fullCSS);
                        e.editor.dom.addClass(e.editor.getBody(), 'styles-injected');
                        console.log('已向新編輯器注入樣式:', e.editor.id);
                    }
                }, 500);
            });
        });
        
        window.tinyMCEStylesListener = true;
    }
}

// 開始注入流程
injectStylesToAllEditors();

// 提供手動重新注入的方法
window.reinjectAllTinyMCEStyles = function() {
    // 移除所有已注入標記，強制重新注入
    if (tinymce && tinymce.editors) {
        tinymce.editors.forEach(function(editor) {
            if (editor.dom && editor.getBody()) {
                editor.dom.removeClass(editor.getBody(), 'styles-injected');
            }
        });
    }
    injectStylesToAllEditors();
};

// 提供檢查樣式的除錯工具
window.checkAllTinyMCEStyles = function() {
    if (!tinymce || !tinymce.editors) {
        console.log('TinyMCE 未載入');
        return;
    }
    
    tinymce.editors.forEach(function(editor, index) {
        console.log(`\n=== 編輯器 ${index + 1} (ID: ${editor.id}) ===`);
        
        if (!editor.getBody()) {
            console.log('編輯器主體未載入');
            return;
        }
        
        var hasInjectedClass = editor.dom.hasClass(editor.getBody(), 'styles-injected');
        console.log('已注入樣式標記:', hasInjectedClass);
        
        // 檢查各種樣式類別
        var classesToCheck = [
            'opt-keyword',
            'opt-keyword-existing',
            'opt-modified',
            'opt-new',
            'opt-placeholder',
            'opt-improvement'
        ];
        
        classesToCheck.forEach(function(className) {
            var elements = editor.dom.select('.' + className);
            if (elements.length > 0) {
                console.log(`找到 ${elements.length} 個 .${className} 元素`);
                
                // 檢查第一個元素的樣式
                var firstElement = elements[0];
                var styles = editor.getWin().getComputedStyle(firstElement);
                console.log(`  - 背景色: ${styles.backgroundColor}`);
                console.log(`  - 文字色: ${styles.color}`);
            }
        });
    });
};

console.log('多編輯器樣式注入腳本已載入。可用命令：');
console.log('- reinjectAllTinyMCEStyles() : 重新注入所有樣式');
console.log('- checkAllTinyMCEStyles() : 檢查所有編輯器的樣式狀態');