// === 修正版 - 在 btnToggleTags changed event 中使用 ===
// 邏輯修正：確保 toggle checked = 顯示標記

// 初始化狀態變數（如果不存在）
if (typeof window.markersVisible === 'undefined') {
    // 初始狀態：顯示標記（與頁面載入時的狀態一致）
    window.markersVisible = true;
}

// 切換狀態
window.markersVisible = !window.markersVisible;

// 調用切換函數
// 重要：toggleTinyMCEMarkers 的參數是 hideMarkers (true = 隱藏, false = 顯示)
// 所以當 markersVisible = true 時，hideMarkers 應該 = false
toggleTinyMCEMarkers(!window.markersVisible);

// 調試輸出
console.log('Toggle clicked:', {
    'markersVisible': window.markersVisible,
    'hideMarkers parameter': !window.markersVisible,
    'expected result': window.markersVisible ? '顯示標記' : '隱藏標記'
});