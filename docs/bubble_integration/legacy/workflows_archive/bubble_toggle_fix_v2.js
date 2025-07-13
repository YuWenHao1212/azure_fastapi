/**
 * 修正版本 - 解決標記無法再次顯示的問題
 * Fixed version for btnToggleTags toggle functionality
 */

// 全局函數 - 放在 Page HTML header
window.toggleTinyMCEMarkersFixed = function(hideMarkers) {
    console.log('🔄 Toggle called - ' + (hideMarkers ? 'HIDE' : 'SHOW') + ' markers');
    
    try {
        // 獲取 TinyMCE 編輯器
        if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
            console.error('❌ TinyMCE editor not found');
            return false;
        }
        
        var editor = tinymce.activeEditor;
        var iframeDoc = editor.getDoc();
        var body = iframeDoc.body;
        
        // 每次都重新注入樣式（確保樣式存在）
        var existingStyle = iframeDoc.getElementById('bubble-marker-styles');
        if (existingStyle) {
            existingStyle.remove();
            console.log('🗑️ Removed existing styles');
        }
        
        // 注入新樣式
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
            
            /* 隱藏標記樣式 - 使用更高的優先級 */
            body.hide-all-tags .opt-new {
                background-color: transparent !important;
                border-left: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            body.hide-all-tags .opt-modified {
                background-color: transparent !important;
                padding: 0 !important;
                border-radius: 0 !important;
            }
            
            body.hide-all-tags .opt-placeholder {
                background-color: transparent !important;
                color: inherit !important;
                border: none !important;
                padding: 0 !important;
                font-style: normal !important;
            }
            
            body.hide-all-tags .opt-keyword {
                background-color: transparent !important;
                color: inherit !important;
                border: none !important;
                padding: 0 !important;
                font-weight: normal !important;
            }
            
            body.hide-all-tags .opt-keyword-existing {
                background-color: transparent !important;
                color: inherit !important;
                padding: 0 !important;
                font-weight: normal !important;
            }
        `;
        iframeDoc.head.appendChild(style);
        console.log('✅ Styles injected');
        
        // 切換 hide-all-tags 類別
        if (hideMarkers) {
            body.classList.add('hide-all-tags');
            console.log('➕ Added hide-all-tags class');
        } else {
            body.classList.remove('hide-all-tags');
            console.log('➖ Removed hide-all-tags class');
        }
        
        // 強制多種刷新方法
        // 方法 1: 強制重排
        body.style.display = 'none';
        void body.offsetHeight; // 強制瀏覽器計算
        body.style.display = '';
        
        // 方法 2: 修改並恢復內容
        var content = editor.getContent();
        editor.setContent(content + ' ');
        editor.setContent(content);
        
        // 方法 3: 觸發事件
        if (editor.fire) {
            editor.fire('change');
            editor.fire('input');
            editor.fire('keyup');
        }
        
        // 方法 4: 節點變更
        if (editor.nodeChanged) {
            editor.nodeChanged();
        }
        
        console.log('✅ Toggle completed successfully');
        
        // 驗證當前狀態
        var hasHideClass = body.classList.contains('hide-all-tags');
        console.log('📊 Current state - Hide class: ' + hasHideClass);
        
        return true;
        
    } catch (error) {
        console.error('❌ Error in toggle:', error);
        return false;
    }
};

// 替換原有的 toggleTinyMCEMarkers 函數
window.toggleTinyMCEMarkers = window.toggleTinyMCEMarkersFixed;

// 診斷函數 - 檢查當前狀態
window.checkMarkerState = function() {
    try {
        if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
            var editor = tinymce.activeEditor;
            var iframeDoc = editor.getDoc();
            var body = iframeDoc.body;
            
            console.log('=== Marker State Check ===');
            console.log('Body classes:', body.className);
            console.log('Has hide-all-tags:', body.classList.contains('hide-all-tags'));
            
            var markers = iframeDoc.querySelectorAll('.opt-new, .opt-modified, .opt-placeholder, .opt-keyword, .opt-keyword-existing');
            console.log('Total markers found:', markers.length);
            
            if (markers.length > 0) {
                var firstMarker = markers[0];
                var style = iframeDoc.defaultView.getComputedStyle(firstMarker);
                console.log('First marker class:', firstMarker.className);
                console.log('Background:', style.backgroundColor);
                console.log('Border:', style.borderLeft);
                console.log('Padding:', style.padding);
            }
            
            var styleElement = iframeDoc.getElementById('bubble-marker-styles');
            console.log('Style element exists:', !!styleElement);
        }
    } catch (e) {
        console.error('Error checking state:', e);
    }
};

// 初始化函數 - 在頁面載入時顯示標記
window.initializeMarkers = function() {
    console.log('🚀 Initializing markers...');
    
    var checkInterval = setInterval(function() {
        if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
            // 確保標記初始是顯示的
            toggleTinyMCEMarkersFixed(false);
            clearInterval(checkInterval);
            console.log('✅ Markers initialized');
        }
    }, 500);
    
    // 30秒後停止檢查
    setTimeout(function() {
        clearInterval(checkInterval);
    }, 30000);
};

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', initializeMarkers);