// === 延遲執行版本 - 確保函數已載入 ===

// 延遲執行以確保所有腳本都已載入
setTimeout(function() {
    // 檢查函數是否可用
    if (typeof window.toggleTinyMCEMarkers !== 'function') {
        console.error('❌ toggleTinyMCEMarkers is not defined');
        
        // 列出所有可用的全局函數
        console.log('Available global functions:');
        for (let key in window) {
            if (typeof window[key] === 'function' && (key.includes('toggle') || key.includes('marker') || key.includes('TinyMCE'))) {
                console.log('- ' + key);
            }
        }
        return;
    }
    
    // 追蹤當前是否顯示標記
    if (typeof window.markersCurrentlyVisible === 'undefined') {
        window.markersCurrentlyVisible = true;
    }
    
    // 切換狀態
    window.markersCurrentlyVisible = !window.markersCurrentlyVisible;
    
    // 調用函數
    window.toggleTinyMCEMarkers(!window.markersCurrentlyVisible);
    console.log('✅ Toggle successful. Markers:', window.markersCurrentlyVisible ? 'VISIBLE' : 'HIDDEN');
    
}, 100); // 延遲 100ms