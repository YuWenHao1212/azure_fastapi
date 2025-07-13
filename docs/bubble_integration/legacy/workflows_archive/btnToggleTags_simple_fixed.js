// === 簡化版 - 在 btnToggleTags changed event 中使用 ===

// 獲取 toggle 的當前狀態
// 假設您可以從 Bubble 獲取 checkbox 的狀態
// 如果可以，請使用: var isChecked = Current cell's btnToggleTags is checked;

// 如果無法獲取 Bubble checkbox 狀態，使用全局變數追蹤
if (typeof window.toggleChecked === 'undefined') {
    // 初始狀態：checked（顯示標記）
    window.toggleChecked = true;
} else {
    // 切換狀態
    window.toggleChecked = !window.toggleChecked;
}

// 調用切換函數
// toggleChecked = true 表示要顯示標記，所以 hideMarkers = false
// toggleChecked = false 表示要隱藏標記，所以 hideMarkers = true
toggleTinyMCEMarkers(!window.toggleChecked);

// 調試輸出
console.log('Toggle state:', window.toggleChecked ? 'Checked (Show markers)' : 'Unchecked (Hide markers)');