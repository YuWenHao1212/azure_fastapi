<script>
/**
 * TinyMCE Placeholder Handler for Bubble.io - Final Version
 * 功能：點擊 placeholder 進行編輯，自動添加單位
 * 
 * 版本：1.0.0
 * 日期：2025-01-11
 */

// 全局變數
let activeInput = null;
let placeholderData = null;
let originalMode = 'readonly';
let hasClickedBefore = false; // 追蹤是否已經點擊過

// 調試
function debugLog(message, data) {
    console.log(`[Placeholder-Handler] ${message}`, data || '');
}

// 初始化
function initBubblePlaceholderHandler() {
    debugLog('開始初始化...');
    
    if (typeof tinymce === 'undefined') {
        setTimeout(initBubblePlaceholderHandler, 100);
        return;
    }
    
    // 處理編輯器
    tinymce.on('AddEditor', function(e) {
        e.editor.on('init', function() {
            setupPlaceholderHandler(e.editor);
        });
    });
    
    tinymce.get().forEach(editor => {
        if (editor.initialized) {
            setupPlaceholderHandler(editor);
        }
    });
}

// 設置處理器
function setupPlaceholderHandler(editor) {
    if (editor.placeholderHandlerSetup) return;
    editor.placeholderHandlerSetup = true;
    
    debugLog('設置編輯器:', editor.id);
    
    // 添加樣式
    editor.dom.addStyle(`
        .opt-placeholder { 
            background-color: #fee2e2 !important;
            color: #991b1b !important;
            border: 1px dashed #f87171 !important;
            padding: 2px 8px !important;
            border-radius: 4px !important;
            font-style: italic !important;
            font-weight: 500 !important;
            display: inline-block !important;
            cursor: pointer !important;
            position: relative !important;
        }
        .opt-placeholder:hover {
            background-color: #fecaca !important;
            border-color: #ef4444 !important;
        }
        .editing-placeholder {
            background-color: #fff !important;
            border: 2px solid #721c24 !important;
            padding: 6px 10px !important;
            border-radius: 3px !important;
            color: #721c24 !important;
            font-style: normal !important;
            font-size: inherit !important;
            min-width: 80px !important;
            min-height: 32px !important;
            line-height: 1.5 !important;
            display: inline-block !important;
            vertical-align: middle !important;
            outline: none !important;
        }
        .opt-improvement {
            border-bottom: 2px solid #28a745 !important;
            padding-bottom: 1px !important;
            color: #155724 !important;
        }
    `);
    
    // 設置點擊處理
    const editorBody = editor.getBody();
    if (editorBody) {
        // 使用 capture phase 捕獲點擊
        editorBody.addEventListener('mousedown', function(e) {
            handlePlaceholderClick(e, editor);
        }, true);
        
        debugLog('點擊處理器已設置');
    }
    
    // 監聽鍵盤
    editor.on('keydown', function(e) {
        if (activeInput && editor.mode.get() === 'design') {
            if (e.key === 'Enter') {
                e.preventDefault();
                finishEditingAndSwitch(editor);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelEditingAndSwitch(editor);
            }
        }
    });
    
    // 記錄初始模式
    setTimeout(() => {
        originalMode = editor.mode.get();
        debugLog('初始模式:', originalMode);
    }, 500);
}

// 處理點擊
function handlePlaceholderClick(e, editor) {
    const target = e.target;
    
    if (target && target.classList && target.classList.contains('opt-placeholder')) {
        e.preventDefault();
        e.stopPropagation();
        
        debugLog('點擊 placeholder:', target.innerText);
        
        // 如果在唯讀模式
        if (editor.mode.get() === 'readonly') {
            debugLog('在唯讀模式，需要切換');
            originalMode = 'readonly';
            
            // 切換到編輯模式
            editor.mode.set('design');
            
            // 等待模式切換完成
            waitForModeChange(editor, 'design', () => {
                debugLog('模式切換完成');
                
                // 第一次點擊需要特殊處理
                if (!hasClickedBefore) {
                    debugLog('第一次點擊，使用特殊聚焦策略');
                    hasClickedBefore = true;
                    
                    // 延遲較長時間確保 DOM 完全就緒
                    setTimeout(() => {
                        startEditingWithFocus(target, editor, true);
                    }, 300);
                } else {
                    startEditingWithFocus(target, editor, false);
                }
            });
        } else if (!activeInput) {
            startEditingWithFocus(target, editor, false);
        }
    }
    // 點擊其他地方
    else if (activeInput && !target.classList.contains('editing-placeholder')) {
        finishEditingAndSwitch(editor);
    }
}

// 等待模式切換
function waitForModeChange(editor, targetMode, callback) {
    let attempts = 0;
    const maxAttempts = 20;
    
    const checkMode = () => {
        attempts++;
        if (editor.mode.get() === targetMode) {
            callback();
        } else if (attempts < maxAttempts) {
            setTimeout(checkMode, 50);
        } else {
            debugLog('模式切換超時');
        }
    };
    
    setTimeout(checkMode, 50);
}

// 開始編輯並確保聚焦
function startEditingWithFocus(placeholder, editor, isFirstTime) {
    // 保存資料
    placeholderData = {
        text: placeholder.innerText,
        type: placeholder.innerText.replace(/[\[\]]/g, '')
    };
    
    debugLog('開始編輯:', placeholderData.type);
    
    // 轉換樣式
    placeholder.classList.remove('opt-placeholder');
    placeholder.classList.add('editing-placeholder');
    placeholder.contentEditable = 'true';
    
    // 設置初始值（不包含單位，因為完成時會自動添加）
    const hints = {
        'PERCENTAGE': '25',
        'TEAM SIZE': '5-10',
        'AMOUNT': '1',
        'NUMBER': '100',
        'TIME PERIOD': '3',
        'USER COUNT': '10000',
        '35M units': '35',
        '70%': '70'
    };
    
    let initialValue = hints[placeholderData.type] || '';
    if (placeholderData.text.match(/\[.+\]/) && !hints[placeholderData.type]) {
        initialValue = placeholderData.text.replace(/[\[\]]/g, '');
    }
    
    placeholder.innerText = initialValue;
    activeInput = placeholder;
    
    // 聚焦策略
    if (isFirstTime) {
        debugLog('使用第一次點擊聚焦策略');
        
        // 策略1: 立即嘗試聚焦
        setTimeout(() => {
            placeholder.focus();
            selectAllContent(placeholder, editor);
            debugLog('第一次聚焦嘗試完成');
        }, 100);
        
        // 策略2: 延遲後再次聚焦
        setTimeout(() => {
            // 檢查是否仍需要聚焦
            const doc = editor.getDoc();
            if (doc.activeElement !== placeholder) {
                debugLog('需要第二次聚焦');
                placeholder.focus();
                selectAllContent(placeholder, editor);
            }
        }, 500);
        
        // 策略3: 使用 execCommand 來確保可編輯
        setTimeout(() => {
            editor.focus();
            placeholder.focus();
            
            // 嘗試使用 execCommand 使元素可編輯
            try {
                editor.getDoc().execCommand('enableObjectResizing', false, false);
                editor.getDoc().execCommand('enableInlineTableEditing', false, false);
                selectAllContent(placeholder, editor);
                debugLog('最終聚焦嘗試完成');
            } catch (e) {
                debugLog('execCommand 錯誤:', e);
            }
        }, 800);
        
    } else {
        // 非第一次，正常聚焦
        setTimeout(() => {
            placeholder.focus();
            selectAllContent(placeholder, editor);
        }, 100);
    }
}

// 選中全部內容
function selectAllContent(element, editor) {
    try {
        const range = editor.getDoc().createRange();
        range.selectNodeContents(element);
        const sel = editor.getWin().getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    } catch (e) {
        debugLog('選中內容錯誤:', e);
    }
}

// 完成編輯
function finishEditingAndSwitch(editor) {
    if (!activeInput || !placeholderData) return;
    
    const value = activeInput.innerText.trim();
    debugLog('完成編輯:', value);
    
    if (value) {
        // 增強的格式化邏輯
        let formatted = value;
        
        // 根據 placeholder 類型格式化
        switch(placeholderData.type) {
            case 'PERCENTAGE':
            case '70%':
                // 移除現有的 % 符號，然後添加
                formatted = value.replace(/%/g, '').trim();
                if (formatted && !isNaN(formatted)) {
                    formatted = formatted + '%';
                }
                break;
                
            case 'AMOUNT':
                // 檢查是否已有貨幣符號
                if (!value.match(/[$¥€£]/)) {
                    // 如果是純數字，添加 $
                    const numValue = value.replace(/[^0-9.KMB]/gi, '');
                    if (numValue) {
                        formatted = '$' + value;
                    }
                }
                break;
                
            case 'TEAM SIZE':
                // 如果輸入的是純數字，可以加上 "人" 或保持原樣
                if (value.match(/^\d+$/)) {
                    formatted = value + ' people';
                } else if (value.match(/^\d+-\d+$/)) {
                    formatted = value + ' people';
                }
                break;
                
            case 'TIME PERIOD':
                // 檢查是否需要添加時間單位
                if (value.match(/^\d+$/)) {
                    formatted = value + ' months';
                }
                break;
                
            case 'USER COUNT':
                // 處理用戶數量，例如 10K, 1M 等
                if (value.match(/^\d+$/)) {
                    const num = parseInt(value);
                    if (num >= 1000000) {
                        formatted = (num / 1000000).toFixed(1) + 'M';
                    } else if (num >= 1000) {
                        formatted = (num / 1000).toFixed(1) + 'K';
                    }
                }
                break;
                
            case '35M units':
                // 處理單位數量
                if (value.match(/^\d+$/)) {
                    formatted = value + 'M units';
                }
                break;
        }
        
        debugLog('格式化結果:', formatted);
        
        activeInput.classList.remove('editing-placeholder');
        activeInput.classList.add('opt-improvement');
        activeInput.contentEditable = 'false';
        activeInput.innerText = formatted;
    } else {
        // 恢復 placeholder
        activeInput.classList.remove('editing-placeholder');
        activeInput.classList.add('opt-placeholder');
        activeInput.contentEditable = 'false';
        activeInput.innerText = placeholderData.text;
    }
    
    activeInput = null;
    placeholderData = null;
    
    editor.fire('change');
    
    // 切回唯讀
    if (originalMode === 'readonly') {
        setTimeout(() => {
            debugLog('切回唯讀模式');
            editor.mode.set('readonly');
        }, 200);
    }
}

// 取消編輯
function cancelEditingAndSwitch(editor) {
    if (!activeInput || !placeholderData) return;
    
    activeInput.classList.remove('editing-placeholder');
    activeInput.classList.add('opt-placeholder');
    activeInput.contentEditable = 'false';
    activeInput.innerText = placeholderData.text;
    
    activeInput = null;
    placeholderData = null;
    
    if (originalMode === 'readonly') {
        setTimeout(() => {
            editor.mode.set('readonly');
        }, 200);
    }
}

// API 函數
window.getPlaceholderStatus = function() {
    const editor = tinymce.activeEditor;
    if (!editor) return null;
    
    const placeholders = editor.dom.select('.opt-placeholder');
    const improvements = editor.dom.select('.opt-improvement');
    
    return {
        mode: editor.mode.get(),
        placeholders: placeholders.length,
        completed: improvements.length,
        hasClickedBefore: hasClickedBefore
    };
};

// 測試函數
window.testPlaceholderClick = function() {
    const editor = tinymce.activeEditor;
    if (!editor) return;
    
    const placeholder = editor.dom.select('.opt-placeholder')[0];
    if (placeholder) {
        debugLog('模擬點擊 placeholder');
        const event = new MouseEvent('mousedown', {
            bubbles: true,
            cancelable: true,
            view: window
        });
        placeholder.dispatchEvent(event);
    }
};

// 重置第一次點擊標記
window.resetFirstClick = function() {
    hasClickedBefore = false;
    debugLog('已重置第一次點擊標記');
};

// 手動激活當前編輯的 placeholder
window.activateCurrentPlaceholder = function() {
    const editor = tinymce.activeEditor;
    if (!editor || !activeInput) {
        debugLog('沒有正在編輯的 placeholder');
        return;
    }
    
    debugLog('手動激活 placeholder');
    
    // 簡單的聚焦方法
    editor.focus();
    activeInput.focus();
    
    // 選中全部文字
    selectAllContent(activeInput, editor);
    
    debugLog('手動激活完成');
};

// 初始化
debugLog('腳本載入完成');

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBubblePlaceholderHandler);
} else {
    setTimeout(initBubblePlaceholderHandler, 500);
}
</script>