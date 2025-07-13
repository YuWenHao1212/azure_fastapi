/**
 * 優雅解決方案 - 讓我們的樣式成為預設樣式
 * Elegant Solution - Making our styles the default
 * 
 * 這個方案只需要在頁面載入時注入一次樣式，之後只需切換 class
 */

// === 放在 Page HTML header ===

(function() {
    'use strict';
    
    // 標記我們的樣式是否已經注入
    window.markerStylesInjected = false;
    
    /**
     * 注入預設樣式 - 只需執行一次
     * 這會讓 opt-tags 預設就有我們定義的可見樣式
     */
    window.injectDefaultMarkerStyles = function() {
        if (window.markerStylesInjected) {
            console.log('✅ 樣式已存在，無需重複注入');
            return true;
        }
        
        try {
            // 等待 TinyMCE 準備好
            if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
                console.log('⏳ TinyMCE 尚未準備好');
                return false;
            }
            
            const editor = tinymce.activeEditor;
            const iframeDoc = editor.getDoc();
            
            // 創建樣式元素
            const style = iframeDoc.createElement('style');
            style.id = 'default-marker-styles';
            style.textContent = `
                /* === 預設樣式 - opt-tags 的可見狀態 === */
                
                /* opt-new - 新增區段 (綠色) */
                .opt-new {
                    background-color: rgba(16, 185, 129, 0.1) !important;
                    border-left: 4px solid #10B981 !important;
                    padding-left: 16px !important;
                    margin: 4px 0 !important;
                    transition: all 0.3s ease;
                }
                
                /* opt-modified - 修改內容 (黃色) */
                .opt-modified {
                    background-color: #fef3c7 !important;
                    padding: 2px 6px !important;
                    border-radius: 3px !important;
                    transition: all 0.3s ease;
                }
                
                /* opt-placeholder - 佔位符 (紅色) */
                .opt-placeholder {
                    background-color: #fee2e2 !important;
                    color: #991b1b !important;
                    border: 1px dashed #f87171 !important;
                    padding: 2px 8px !important;
                    border-radius: 4px !important;
                    font-style: italic !important;
                    transition: all 0.3s ease;
                }
                
                /* opt-keyword - 新關鍵字 (紫色) */
                .opt-keyword {
                    background-color: transparent !important;
                    color: #6366f1 !important;
                    border: 1px solid #c7d2fe !important;
                    padding: 2px 6px !important;
                    border-radius: 3px !important;
                    font-weight: 500 !important;
                    transition: all 0.3s ease;
                }
                
                /* opt-keyword-existing - 現有關鍵字 (藍色) */
                .opt-keyword-existing {
                    background-color: #2563eb !important;
                    color: white !important;
                    padding: 3px 8px !important;
                    border-radius: 4px !important;
                    font-weight: 600 !important;
                    transition: all 0.3s ease;
                }
                
                /* === 隱藏模式 - 當 body 有 markers-hidden class 時 === */
                
                body.markers-hidden .opt-new,
                body.markers-hidden .opt-modified,
                body.markers-hidden .opt-placeholder,
                body.markers-hidden .opt-keyword,
                body.markers-hidden .opt-keyword-existing {
                    background-color: transparent !important;
                    border: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    color: inherit !important;
                    font-weight: normal !important;
                    font-style: normal !important;
                    border-radius: 0 !important;
                }
            `;
            
            // 注入樣式到 iframe head
            iframeDoc.head.appendChild(style);
            
            // 標記樣式已注入
            window.markerStylesInjected = true;
            
            console.log('✅ 預設標記樣式已成功注入');
            return true;
            
        } catch (error) {
            console.error('❌ 注入樣式時發生錯誤:', error);
            return false;
        }
    };
    
    /**
     * 簡單的切換函數 - 只需切換 class
     * @param {boolean} hideMarkers - true 隱藏, false 顯示
     */
    window.toggleMarkers = function(hideMarkers) {
        try {
            if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
                console.error('❌ TinyMCE 編輯器未找到');
                return false;
            }
            
            const editor = tinymce.activeEditor;
            const iframeDoc = editor.getDoc();
            const body = iframeDoc.body;
            
            // 確保樣式已注入
            if (!window.markerStylesInjected) {
                window.injectDefaultMarkerStyles();
            }
            
            // 簡單切換 class
            if (hideMarkers) {
                body.classList.add('markers-hidden');
                console.log('🔴 標記已隱藏');
            } else {
                body.classList.remove('markers-hidden');
                console.log('🟢 標記已顯示');
            }
            
            // 輕量級刷新
            body.style.opacity = '0.99';
            setTimeout(() => {
                body.style.opacity = '1';
            }, 10);
            
            return true;
            
        } catch (error) {
            console.error('❌ 切換標記時發生錯誤:', error);
            return false;
        }
    };
    
    /**
     * 自動初始化 - 在 TinyMCE 準備好時注入樣式
     */
    window.initializeMarkerSystem = function() {
        console.log('🚀 初始化標記系統...');
        
        const checkInterval = setInterval(function() {
            if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
                // 注入預設樣式
                if (window.injectDefaultMarkerStyles()) {
                    clearInterval(checkInterval);
                    console.log('✅ 標記系統初始化完成');
                }
            }
        }, 500);
        
        // 30秒後停止嘗試
        setTimeout(() => clearInterval(checkInterval), 30000);
    };
    
    // 頁面載入時自動初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.initializeMarkerSystem);
    } else {
        window.initializeMarkerSystem();
    }
    
})();

// === 全局函數供 Bubble 使用 ===

/**
 * 主要的 toggle 函數 - 供 Bubble workflow 調用
 */
window.toggleTinyMCEMarkers = function(hideMarkers) {
    return window.toggleMarkers(hideMarkers);
};

/**
 * 便利函數
 */
window.showMarkers = function() {
    return window.toggleMarkers(false);
};

window.hideMarkers = function() {
    return window.toggleMarkers(true);
};