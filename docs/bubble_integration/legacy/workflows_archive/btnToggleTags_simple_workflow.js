// === 超級簡單版本 - 在 btnToggleTags changed event 中使用 ===

// 使用靜態變量追蹤狀態（因為獲取 checkbox 狀態可能有問題）
if (typeof window.markersVisible === 'undefined') {
    // 初始狀態：顯示標記
    window.markersVisible = true;
}

// 每次點擊時切換狀態
window.markersVisible = !window.markersVisible;

// 調用切換函數
if (typeof toggleMarkers === 'function') {
    // markersVisible = true 表示要顯示，所以 hideMarkers = false
    toggleMarkers(!window.markersVisible);
} else if (typeof toggleTinyMCEMarkers === 'function') {
    toggleTinyMCEMarkers(!window.markersVisible);
} else {
    console.error('Toggle 函數未定義');
}

console.log('標記狀態:', window.markersVisible ? '顯示' : '隱藏');