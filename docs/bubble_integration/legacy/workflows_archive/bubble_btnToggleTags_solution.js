/**
 * Simplified TinyMCE Marker Toggle Solution for btnToggleTags
 * 專為 btnToggleTags 設計的簡化解決方案
 * 
 * 直接在 Bubble.io 的 btnToggleTags changed event 中使用
 */

// === 方法 1: 在 btnToggleTags changed event 中使用 ===
// 將此代碼放在 "Run javascript" action 中

// 首先確保有樣式
if (!document.getElementById('tinymce-marker-styles-injected')) {
    // 找到 TinyMCE 編輯器
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
        var editor = tinymce.activeEditor;
        var iframeDoc = editor.getDoc();
        
        // 注入樣式
        var style = iframeDoc.createElement('style');
        style.id = 'bubble-marker-styles';
        style.textContent = `
            /* 可見標記樣式 */
            .opt-new {
                background-color: rgba(16, 185, 129, 0.1) !important;
                border-left: 4px solid #10B981 !important;
                padding-left: 16px !important;
                margin: 4px 0 !important;
            }
            
            .opt-modified {
                background-color: #fef3c7 !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
            }
            
            .opt-placeholder {
                background-color: #fee2e2 !important;
                color: #991b1b !important;
                border: 1px dashed #f87171 !important;
                padding: 2px 8px !important;
                border-radius: 4px !important;
                font-style: italic !important;
            }
            
            .opt-keyword {
                background-color: transparent !important;
                color: #6366f1 !important;
                border: 1px solid #c7d2fe !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                font-weight: 500 !important;
            }
            
            .opt-keyword-existing {
                background-color: #2563eb !important;
                color: white !important;
                padding: 3px 8px !important;
                border-radius: 4px !important;
                font-weight: 600 !important;
            }
            
            /* 隱藏標記樣式 */
            .hide-all-tags .opt-new {
                background-color: transparent !important;
                border-left: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            .hide-all-tags .opt-modified {
                background-color: transparent !important;
                padding: 0 !important;
                border-radius: 0 !important;
            }
            
            .hide-all-tags .opt-placeholder {
                background-color: transparent !important;
                color: inherit !important;
                border: none !important;
                padding: 0 !important;
                font-style: normal !important;
            }
            
            .hide-all-tags .opt-keyword {
                background-color: transparent !important;
                color: inherit !important;
                border: none !important;
                padding: 0 !important;
                font-weight: normal !important;
            }
            
            .hide-all-tags .opt-keyword-existing {
                background-color: transparent !important;
                color: inherit !important;
                padding: 0 !important;
                font-weight: normal !important;
            }
        `;
        iframeDoc.head.appendChild(style);
        
        // 標記已注入
        var marker = document.createElement('div');
        marker.id = 'tinymce-marker-styles-injected';
        marker.style.display = 'none';
        document.body.appendChild(marker);
    }
}

// 執行切換
if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
    var editor = tinymce.activeEditor;
    var iframeDoc = editor.getDoc();
    var body = iframeDoc.body;
    
    // 假設 checked = true 表示顯示標記
    // 這裡需要獲取 btnToggleTags 的實際狀態
    var isChecked = true; // 這裡需要替換為實際的 toggle 狀態
    
    // 嘗試多種方式獲取 toggle 狀態
    try {
        // 方法 1: 從 Bubble 的 properties 獲取
        if (typeof properties !== 'undefined' && properties.bubble_element_btnToggleTags) {
            isChecked = properties.bubble_element_btnToggleTags.value;
        }
        // 方法 2: 從 DOM 獲取
        else {
            var toggleInput = document.querySelector('[data-element-name="btnToggleTags"] input[type="checkbox"]');
            if (toggleInput) {
                isChecked = toggleInput.checked;
            }
        }
    } catch (e) {
        console.log('無法獲取 toggle 狀態，使用預設值');
    }
    
    // 根據 toggle 狀態切換標記
    if (isChecked) {
        // 顯示標記
        body.classList.remove('hide-all-tags');
        console.log('標記已顯示');
    } else {
        // 隱藏標記
        body.classList.add('hide-all-tags');
        console.log('標記已隱藏');
    }
    
    // 強制刷新
    body.style.display = 'none';
    body.offsetHeight;
    body.style.display = '';
    
    // 重設內容觸發 TinyMCE 刷新
    var content = editor.getContent();
    editor.setContent(content);
}


// === 方法 2: 完整的函數版本（放在 Page HTML header） ===
// 如果你想要一個可重複使用的函數

window.toggleMarkersForBtnToggleTags = function() {
    try {
        // 獲取 toggle 狀態
        var isChecked = false;
        
        // 嘗試從 DOM 獲取
        var toggleInput = document.querySelector('[data-element-name="btnToggleTags"] input[type="checkbox"]');
        if (toggleInput) {
            isChecked = toggleInput.checked;
        }
        
        // 調用主要的 toggle 函數
        if (typeof toggleTinyMCEMarkers === 'function') {
            var hideMarkers = !isChecked;
            toggleTinyMCEMarkers(hideMarkers);
        } else {
            console.error('toggleTinyMCEMarkers 函數未定義');
        }
        
    } catch (error) {
        console.error('切換標記時發生錯誤:', error);
    }
};