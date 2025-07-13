// === 同步 Toggle 狀態的 Page Load JavaScript ===

console.log('🚀 Page is loading - Initializing marker system...');

// 初始化標記系統
if (typeof window.initializeMarkerSystem === 'function') {
    window.initializeMarkerSystem();
    console.log('✅ Marker system initialization started');
} else {
    console.log('⚠️ Marker system not ready, will auto-initialize when ready');
}

// 延遲檢查 Toggle 狀態並同步（但要修正邏輯）
setTimeout(function() {
    console.log('🔍 Syncing with toggle state...');
    
    // 嘗試獲取 Toggle 元素
    const toggleElement = document.getElementById('btnToggleTags');
    if (toggleElement) {
        const isChecked = toggleElement.checked;
        console.log(`📌 Toggle state: ${isChecked ? 'Checked' : 'Unchecked'}`);
        
        // 同步內部狀態變數
        window.markersCurrentlyVisible = isChecked;
        
        // 只有當 toggle 是 unchecked 時才隱藏
        // 注意：這裡我們假設初始狀態標記已經是顯示的
        if (!isChecked) {
            if (typeof window.toggleTinyMCEMarkers === 'function') {
                window.toggleTinyMCEMarkers(true); // true = hide markers
                console.log('🔴 Hiding markers to match toggle state');
            }
        } else {
            console.log('🟢 Markers remain visible (toggle is checked)');
        }
    } else {
        console.log('⚠️ Toggle element not found');
        console.log('🟢 Keeping default state: markers visible');
        window.markersCurrentlyVisible = true;
    }
}, 3000); // 延長到 3 秒，確保 TinyMCE 完全載入