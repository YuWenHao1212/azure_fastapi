// ========================================
// 添加 TinyMCE Placeholder 編輯功能
// 在 Page is Loaded workflow 中執行
// ========================================

// 全局變數
window.activeInput = null;
window.placeholderData = null;
window.originalMode = 'readonly';
window.hasClickedBefore = false;

// 調試
function debugLog(message, data) {
    console.log(`[TinyMCE-Placeholder] ${message}`, data || '');
}

// 初始化 TinyMCE Placeholder 處理器
function initTinyMCEPlaceholderHandler() {
    debugLog('開始初始化 TinyMCE placeholder 處理器...');
    
    if (typeof tinymce === 'undefined') {
        setTimeout(initTinyMCEPlaceholderHandler, 100);
        return;
    }
    
    // 處理現有編輯器
    tinymce.get().forEach(editor => {
        if (editor.initialized) {
            setupTinyMCEPlaceholderHandler(editor);
        } else {
            editor.on('init', function() {
                setupTinyMCEPlaceholderHandler(editor);
            });
        }
    });
    
    // 處理新編輯器
    tinymce.on('AddEditor', function(e) {
        e.editor.on('init', function() {
            setupTinyMCEPlaceholderHandler(e.editor);
        });
    });
}

// 設置處理器
function setupTinyMCEPlaceholderHandler(editor) {
    if (editor.placeholderHandlerSetup) return;
    editor.placeholderHandlerSetup = true;
    
    debugLog('設置編輯器:', editor.id);
    
    // 添加編輯時的樣式
    editor.dom.addStyle(`
        .editing-placeholder {
            background-color: #fff !important;
            border: 2px solid #2563EB !important;
            padding: 6px 10px !important;
            border-radius: 3px !important;
            color: #1F2937 !important;
            font-style: normal !important;
            font-size: inherit !important;
            min-width: 80px !important;
            min-height: 32px !important;
            line-height: 1.5 !important;
            display: inline-block !important;
            vertical-align: middle !important;
            outline: none !important;
            cursor: text !important;
        }
        
        .opt-improvement {
            border-bottom: 2px solid #10B981 !important;
            padding-bottom: 1px !important;
            color: #065F46 !important;
            font-weight: 500 !important;
        }
        
        /* 確保 placeholder 在隱藏標記時也可點擊 */
        body.markers-hidden span.opt-placeholder {
            cursor: pointer !important;
            pointer-events: auto !important;
        }
    `);
    
    // 設置點擊處理
    const editorBody = editor.getBody();
    if (editorBody) {
        // 使用 capture phase 捕獲點擊
        editorBody.addEventListener('mousedown', function(e) {
            handleTinyMCEPlaceholderClick(e, editor);
        }, true);
        
        debugLog('點擊處理器已設置');
    }
    
    // 監聽鍵盤
    editor.on('keydown', function(e) {
        if (window.activeInput && editor.mode.get() === 'design') {
            if (e.key === 'Enter') {
                e.preventDefault();
                finishEditingPlaceholder(editor);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEditingPlaceholder(editor);
            }
        }
    });
    
    // 記錄初始模式
    setTimeout(() => {
        window.originalMode = editor.mode.get();
        debugLog('初始模式:', window.originalMode);
    }, 500);
}

// 處理點擊
function handleTinyMCEPlaceholderClick(e, editor) {
    const target = e.target;
    
    if (target && target.classList && target.classList.contains('opt-placeholder')) {
        e.preventDefault();
        e.stopPropagation();
        
        debugLog('點擊 placeholder:', target.innerText);
        
        // 如果在唯讀模式，需要切換
        if (editor.mode.get() === 'readonly') {
            debugLog('在唯讀模式，切換到編輯模式');
            window.originalMode = 'readonly';
            
            // 切換到編輯模式
            editor.mode.set('design');
            
            // 等待模式切換完成
            setTimeout(() => {
                startEditingPlaceholder(target, editor);
            }, 200);
        } else if (!window.activeInput) {
            startEditingPlaceholder(target, editor);
        }
    }
    // 點擊其他地方，完成編輯
    else if (window.activeInput && !target.classList.contains('editing-placeholder')) {
        finishEditingPlaceholder(editor);
    }
}

// 開始編輯
function startEditingPlaceholder(placeholder, editor) {
    // 保存資料
    window.placeholderData = {
        text: placeholder.innerText,
        type: placeholder.innerText.replace(/[\[\]]/g, '')
    };
    
    debugLog('開始編輯:', window.placeholderData.type);
    
    // 轉換樣式
    placeholder.classList.remove('opt-placeholder');
    placeholder.classList.add('editing-placeholder');
    placeholder.contentEditable = 'true';
    
    // 設置初始值
    const hints = {
        'PERCENTAGE': '25',
        'TEAM SIZE': '5-10',
        'AMOUNT': '1000',
        'NUMBER': '100',
        'TIME PERIOD': '3',
        'USER COUNT': '10000',
        'YOUR NAME': '',
        'YOUR EMAIL': '',
        'YOUR PHONE': ''
    };
    
    let initialValue = hints[window.placeholderData.type] || '';
    placeholder.innerText = initialValue;
    window.activeInput = placeholder;
    
    // 聚焦並選中
    setTimeout(() => {
        placeholder.focus();
        // 選中全部內容
        try {
            const range = editor.getDoc().createRange();
            range.selectNodeContents(placeholder);
            const sel = editor.getWin().getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
        } catch (e) {
            debugLog('選中內容錯誤:', e);
        }
    }, 100);
}

// 完成編輯
function finishEditingPlaceholder(editor) {
    if (!window.activeInput || !window.placeholderData) return;
    
    const value = window.activeInput.innerText.trim();
    debugLog('完成編輯:', value);
    
    if (value) {
        // 格式化輸入值
        let formatted = value;
        
        // 根據類型添加單位
        switch(window.placeholderData.type) {
            case 'PERCENTAGE':
                if (!value.includes('%')) {
                    formatted = value + '%';
                }
                break;
            case 'AMOUNT':
                if (!value.match(/[$¥€£]/)) {
                    formatted = '$' + value;
                }
                break;
            case 'TEAM SIZE':
                if (value.match(/^\d+$/) || value.match(/^\d+-\d+$/)) {
                    formatted = value + ' people';
                }
                break;
            case 'TIME PERIOD':
                if (value.match(/^\d+$/)) {
                    formatted = value + ' months';
                }
                break;
            case 'USER COUNT':
                if (value.match(/^\d+$/)) {
                    const num = parseInt(value);
                    if (num >= 1000000) {
                        formatted = (num / 1000000).toFixed(1) + 'M';
                    } else if (num >= 1000) {
                        formatted = (num / 1000).toFixed(1) + 'K';
                    }
                }
                break;
        }
        
        // 轉換為已完成的樣式
        window.activeInput.classList.remove('editing-placeholder');
        window.activeInput.classList.add('opt-improvement');
        window.activeInput.contentEditable = 'false';
        window.activeInput.innerText = formatted;
    } else {
        // 恢復為 placeholder
        window.activeInput.classList.remove('editing-placeholder');
        window.activeInput.classList.add('opt-placeholder');
        window.activeInput.contentEditable = 'false';
        window.activeInput.innerText = window.placeholderData.text;
    }
    
    window.activeInput = null;
    window.placeholderData = null;
    
    // 觸發變更事件
    editor.fire('change');
    
    // 切回唯讀模式（如果原本是唯讀）
    if (window.originalMode === 'readonly') {
        setTimeout(() => {
            debugLog('切回唯讀模式');
            editor.mode.set('readonly');
        }, 200);
    }
}

// 取消編輯
function cancelEditingPlaceholder(editor) {
    if (!window.activeInput || !window.placeholderData) return;
    
    debugLog('取消編輯');
    
    window.activeInput.classList.remove('editing-placeholder');
    window.activeInput.classList.add('opt-placeholder');
    window.activeInput.contentEditable = 'false';
    window.activeInput.innerText = window.placeholderData.text;
    
    window.activeInput = null;
    window.placeholderData = null;
    
    if (window.originalMode === 'readonly') {
        setTimeout(() => {
            editor.mode.set('readonly');
        }, 200);
    }
}

// 初始化
debugLog('TinyMCE Placeholder Handler 載入完成');

// 延遲初始化，確保 TinyMCE 已經載入
setTimeout(initTinyMCEPlaceholderHandler, 1000);