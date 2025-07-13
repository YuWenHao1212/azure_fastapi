// === 最簡單的解決方案 - 在 btnToggleTags changed event 中使用 ===

// 追蹤當前是否顯示標記
if (typeof window.markersCurrentlyVisible === 'undefined') {
    // 初始狀態：顯示（與頁面載入一致）
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

// 如果現在應該顯示，則不隱藏（hideMarkers = false）
// 如果現在應該隱藏，則隱藏（hideMarkers = true）
toggleTinyMCEMarkers(!window.markersCurrentlyVisible);

console.log('Markers are now:', window.markersCurrentlyVisible ? 'VISIBLE' : 'HIDDEN');