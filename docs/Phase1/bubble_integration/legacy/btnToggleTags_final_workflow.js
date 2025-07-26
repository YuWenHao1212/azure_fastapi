// === 最終版本 - 在 btnToggleTags changed event 中使用 ===

// 如果無法獲取 Bubble checkbox 狀態，使用全局變數追蹤
if (typeof window.toggleChecked === 'undefined') {
    // 初始狀態：checked（顯示標記）- 與頁面載入時一致
    window.toggleChecked = true;
}

// 切換狀態
window.toggleChecked = !window.toggleChecked;

// 調用切換函數
// 注意：這裡的邏輯是正確的
// toggleChecked = true 表示 checkbox 被勾選 = 要顯示標記 = hideMarkers 應該是 false
// toggleChecked = false 表示 checkbox 未勾選 = 要隱藏標記 = hideMarkers 應該是 true
var shouldHideMarkers = !window.toggleChecked;
toggleTinyMCEMarkers(shouldHideMarkers);

// 調試輸出
console.log('Toggle clicked:', {
    'checkbox state': window.toggleChecked ? 'Checked' : 'Unchecked',
    'action': window.toggleChecked ? 'Show markers' : 'Hide markers',
    'hideMarkers param': shouldHideMarkers
});