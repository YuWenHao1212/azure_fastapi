// === 診斷版本 - 幫助理解 toggle 狀態 ===

console.log('=== Toggle Event Triggered ===');

// 檢查初始狀態
if (typeof window.toggleClicks === 'undefined') {
    window.toggleClicks = 0;
}
window.toggleClicks++;

console.log('Click number:', window.toggleClicks);

// 根據點擊次數決定行為
// 奇數次點擊 = 隱藏（因為初始是顯示）
// 偶數次點擊 = 顯示
var shouldHideMarkers = (window.toggleClicks % 2 === 1);

console.log('Action:', shouldHideMarkers ? 'HIDE markers' : 'SHOW markers');

// 調用函數
toggleTinyMCEMarkers(shouldHideMarkers);

// 更新預期的 checkbox 狀態
var expectedCheckboxState = !shouldHideMarkers;
console.log('Expected checkbox state:', expectedCheckboxState ? 'Checked (showing)' : 'Unchecked (hidden)');