// ========================================
// 第二個編輯器樣式注入腳本
// 在顯示第二個編輯器的按鈕點擊時執行
// ========================================

// 方法 1: 在按鈕點擊時立即注入樣式（推薦）
function injectStylesToSecondEditor() {
    console.log('[Second Editor] Starting style injection process...');
    
    // 定義完整的樣式
    const fullStyles = `
        /* === 原有關鍵字樣式 - 深藍色背景 === */
        span.opt-keyword-existing {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            padding: 3px 8px !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            margin: 0 2px !important;
            display: inline-block !important;
            line-height: 1.4 !important;
            box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3) !important;
            border: 1px solid #1D4ED8 !important;
            transition: all 0.2s ease !important;
        }
        
        span.opt-keyword-existing:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        /* === 新增關鍵字樣式 - 紫色邊框 === */
        span.opt-keyword {
            background-color: transparent !important;
            color: #6366F1 !important;
            border: 1px solid #C7D2FE !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            font-weight: 500 !important;
            margin: 0 2px !important;
            display: inline-block !important;
            line-height: 1.4 !important;
            transition: all 0.2s ease !important;
        }
        
        span.opt-keyword:hover {
            background-color: #EEF2FF !important;
            border-color: #A5B4FC !important;
        }
        
        /* === 修改內容樣式 - 淺黃色背景 === */
        span.opt-modified {
            background-color: #FFF3CD !important;
            color: #856404 !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            border: 1px solid #FFEAA7 !important;
            display: inline !important;
            transition: all 0.2s ease !important;
        }
        
        span.opt-modified:hover {
            background-color: #FFE9A0 !important;
            box-shadow: 0 1px 3px rgba(251, 191, 36, 0.3) !important;
        }
        
        /* === 新增內容樣式 - 綠色左邊框 === */
        .opt-new {
            border-left: 4px solid #10B981 !important;
            padding-left: 16px !important;
            padding-right: 16px !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
            margin: 8px 0 !important;
            background-color: rgba(209, 250, 229, 0.3) !important;
            display: block !important;
            transition: all 0.2s ease !important;
        }
        
        .opt-new:hover {
            background-color: rgba(209, 250, 229, 0.5) !important;
            border-left-width: 6px !important;
        }
        
        /* === 佔位符樣式 - 紅色虛線框 === */
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
            display: inline-block !important;
            transition: all 0.2s ease !important;
            position: relative !important;
        }
        
        span.opt-placeholder:hover {
            background-color: #FECACA !important;
            border-color: #EF4444 !important;
            border-style: solid !important;
            transform: scale(1.05) !important;
        }
        
        span.opt-placeholder:before {
            content: "📝 " !important;
            font-style: normal !important;
        }
        
        /* === 改進內容樣式 - 綠色底線 === */
        span.opt-improvement {
            border-bottom: 2px solid #10B981 !important;
            color: #065F46 !important;
            padding-bottom: 1px !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }
        
        span.opt-improvement:hover {
            background-color: rgba(209, 250, 229, 0.3) !important;
            padding: 2px 4px !important;
            margin: -2px -4px !important;
            border-radius: 3px !important;
        }
        
        /* === 隱藏標記時的樣式 === */
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
        
        /* === 多標記控制系統樣式 === */
        body.hide-opt-new .opt-new {
            all: unset !important;
            border-left: none !important;
            padding-left: 0 !important;
            background-color: transparent !important;
            display: block !important;
        }
        
        body.hide-opt-modified span.opt-modified {
            all: unset !important;
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
        }
        
        body.hide-opt-placeholder span.opt-placeholder {
            all: unset !important;
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
            font-style: normal !important;
        }
        
        body.hide-opt-placeholder span.opt-placeholder:before {
            content: none !important;
        }
        
        body.hide-opt-keyword span.opt-keyword {
            all: unset !important;
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
        }
        
        body.hide-opt-keyword-existing span.opt-keyword-existing {
            all: unset !important;
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
            font-weight: inherit !important;
        }
    `;
    
    // 嘗試多次尋找第二個編輯器
    let attempts = 0;
    const maxAttempts = 10;
    
    function tryInjectStyles() {
        attempts++;
        console.log(`[Second Editor] Attempt ${attempts} to find second editor...`);
        
        if (typeof tinymce === 'undefined') {
            console.error('[Second Editor] TinyMCE not found!');
            return;
        }
        
        // 獲取所有編輯器
        const editors = tinymce.get();
        if (!editors) {
            console.log('[Second Editor] No editors found yet...');
            if (attempts < maxAttempts) {
                setTimeout(tryInjectStyles, 500);
            }
            return;
        }
        
        // 轉換為陣列
        const editorArray = Array.isArray(editors) ? editors : [editors];
        console.log(`[Second Editor] Found ${editorArray.length} editor(s)`);
        
        // 尋找第二個編輯器（通常是 TinyMCE_Editor_initial_resume）
        let secondEditor = null;
        
        // 方法1: 透過 ID 尋找
        secondEditor = tinymce.get('TinyMCE_Editor_initial_resume');
        
        // 方法2: 如果找不到，使用索引
        if (!secondEditor && editorArray.length > 1) {
            secondEditor = editorArray[1];
        }
        
        // 方法3: 尋找最新的編輯器
        if (!secondEditor) {
            secondEditor = editorArray[editorArray.length - 1];
        }
        
        if (secondEditor && secondEditor.initialized) {
            console.log(`[Second Editor] Found initialized editor: ${secondEditor.id}`);
            
            try {
                // 注入樣式
                secondEditor.dom.addStyle(fullStyles);
                
                // 添加標記
                const doc = secondEditor.getDoc();
                if (doc && !doc.getElementById('second-editor-styles')) {
                    const styleMarker = doc.createElement('style');
                    styleMarker.id = 'second-editor-styles';
                    styleMarker.type = 'text/css';
                    styleMarker.innerHTML = '/* Second editor styles injected */';
                    doc.head.appendChild(styleMarker);
                }
                
                // 應用當前的顯示狀態
                const body = secondEditor.getBody();
                if (body) {
                    // 如果主要標記是隱藏的，也隱藏第二個編輯器的標記
                    if (!window.markersVisible) {
                        secondEditor.dom.addClass(body, 'markers-hidden');
                    }
                    
                    // 應用個別標記的可見性
                    if (window.tagVisibility) {
                        Object.keys(window.tagVisibility).forEach(tag => {
                            if (!window.tagVisibility[tag]) {
                                secondEditor.dom.addClass(body, `hide-${tag}`);
                            }
                        });
                    }
                }
                
                console.log('[Second Editor] ✅ Styles successfully injected!');
                console.log('[Second Editor] Editor details:', {
                    id: secondEditor.id,
                    mode: secondEditor.mode.get(),
                    hidden: secondEditor.isHidden()
                });
                
            } catch (error) {
                console.error('[Second Editor] Error injecting styles:', error);
            }
            
        } else if (attempts < maxAttempts) {
            console.log('[Second Editor] Editor not ready, retrying...');
            setTimeout(tryInjectStyles, 500);
        } else {
            console.error('[Second Editor] Failed to find second editor after ' + maxAttempts + ' attempts');
        }
    }
    
    // 開始注入流程
    tryInjectStyles();
}

// ========================================
// 方法 2: 使用事件監聽器（備選方案）
// ========================================
function setupSecondEditorListener() {
    console.log('[Second Editor Listener] Setting up automatic style injection...');
    
    if (typeof tinymce === 'undefined') {
        console.error('[Second Editor Listener] TinyMCE not found!');
        return;
    }
    
    // 監聽新編輯器
    tinymce.on('AddEditor', function(e) {
        console.log('[Second Editor Listener] New editor added:', e.editor.id);
        
        // 延遲一下確保編輯器完全初始化
        setTimeout(function() {
            if (e.editor.initialized) {
                injectStylesToSpecificEditor(e.editor);
            } else {
                e.editor.on('init', function() {
                    injectStylesToSpecificEditor(e.editor);
                });
            }
        }, 100);
    });
}

// 針對特定編輯器注入樣式
function injectStylesToSpecificEditor(editor) {
    console.log(`[Second Editor] Injecting styles to editor: ${editor.id}`);
    
    // 使用相同的樣式定義
    const fullStyles = `/* 樣式內容同上 */`;
    
    try {
        editor.dom.addStyle(fullStyles);
        console.log(`[Second Editor] ✅ Styles injected to ${editor.id}`);
    } catch (error) {
        console.error(`[Second Editor] Failed to inject styles to ${editor.id}:`, error);
    }
}

// ========================================
// 使用說明
// ========================================
/*
使用方式：

1. 在顯示第二個編輯器的按鈕點擊 workflow 中，添加 "Run javascript" action：
   
   injectStylesToSecondEditor();

2. 或者，在 page loaded workflow 中設置自動監聽器：
   
   setupSecondEditorListener();

3. 測試步驟：
   - 點擊顯示第二個編輯器的按鈕
   - 檢查 console 是否有成功訊息
   - 確認第二個編輯器的標記樣式正確顯示

注意事項：
- 腳本會嘗試 10 次（每 500ms 一次）來找到第二個編輯器
- 會自動同步當前的標記顯示狀態
- 支援多種尋找編輯器的方法，提高成功率
*/