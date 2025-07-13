// === 主 Toggle (btnToggleTags) 的 Workflow - 包含同步機制 ===

// 追蹤當前是否顯示所有標記
if (typeof window.markersCurrentlyVisible === 'undefined') {
    window.markersCurrentlyVisible = true;
}

// 切換狀態
window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

// 使用原本的函數控制所有標記
if (typeof window.toggleTinyMCEMarkers === 'function') {
    window.toggleTinyMCEMarkers(!window.markersCurrentlyVisible);
}

// 同步更新所有個別標記的狀態變數
window.newSectionVisible = window.markersCurrentlyVisible;
window.modificationVisible = window.markersCurrentlyVisible;
window.placeholdersVisible = window.markersCurrentlyVisible;
window.newKeywordsVisible = window.markersCurrentlyVisible;
window.existingKeywordsVisible = window.markersCurrentlyVisible;

// 可選：同步更新 checkbox 的視覺狀態（如果 Bubble 支援）
// 這部分可能需要使用 Bubble 的 custom state 或其他機制

console.log('Main toggle:', window.markersCurrentlyVisible ? 'Show ALL' : 'Hide ALL');
console.log('All individual states synced to:', window.markersCurrentlyVisible);