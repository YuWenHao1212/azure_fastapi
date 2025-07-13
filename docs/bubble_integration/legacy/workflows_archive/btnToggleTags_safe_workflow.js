// === 安全版本 - 在 btnToggleTags changed event 中使用 ===

// 檢查函數是否存在
if (typeof window.toggleTinyMCEMarkers !== 'function') {
    console.error('toggleTinyMCEMarkers function not found!');
    console.log('Available functions:', Object.keys(window).filter(key => typeof window[key] === 'function' && key.includes('toggle')));
    return;
}

// 追蹤當前是否顯示標記
if (typeof window.markersCurrentlyVisible === 'undefined') {
    // 初始狀態：顯示（與頁面載入一致）
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

// 安全調用函數
try {
    window.toggleTinyMCEMarkers(!window.markersCurrentlyVisible);
    console.log('✅ Markers are now:', window.markersCurrentlyVisible ? 'VISIBLE' : 'HIDDEN');
} catch (error) {
    console.error('❌ Error calling toggleTinyMCEMarkers:', error);
}