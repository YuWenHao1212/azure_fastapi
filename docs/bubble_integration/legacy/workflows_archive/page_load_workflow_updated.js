// === 更新的 Page Load JavaScript ===

console.log('🚀 Page is loading - Initializing marker system...');

// 移除舊的 TinyMCETagControl 引用
// TinyMCETagControl.init(); // <-- 這行造成錯誤，已移除

// 初始化我們的標記系統（使用新的函數）
if (typeof window.initializeMarkerSystem === 'function') {
    window.initializeMarkerSystem();
    console.log('✅ Marker system initialization started');
} else {
    console.log('⚠️ Marker system not ready, will auto-initialize when ready');
}

// 設置初始狀態 - 延遲執行以確保 Toggle 元素已載入
setTimeout(function() {
    console.log('🔍 Checking initial toggle state...');
    
    // 嘗試獲取 Toggle 元素
    const toggleElement = document.getElementById('btnToggleTags');
    if (toggleElement) {
        // 檢查 Toggle 是否被勾選
        const isChecked = toggleElement.checked;
        console.log(`📌 Toggle found - Checked: ${isChecked}`);
        
        // 設置初始狀態
        window.markersCurrentlyVisible = isChecked;
        
        // 如果未勾選，隱藏標記
        if (!isChecked && typeof window.toggleTinyMCEMarkers === 'function') {
            window.toggleTinyMCEMarkers(true); // true = hide markers
            console.log('🔴 Initial state: Markers hidden (toggle unchecked)');
        } else {
            console.log('🟢 Initial state: Markers visible (toggle checked)');
        }
    } else {
        console.log('⚠️ Toggle element not found, using default state (markers visible)');
        window.markersCurrentlyVisible = true;
    }
}, 2000);