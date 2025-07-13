// ========================================
// Checkbox Modification workflow
// 控制 opt-modified 標記的顯示/隱藏
// ========================================

// 檢查主開關狀態
if (typeof window.markersVisible !== 'undefined' && !window.markersVisible) {
    console.log('[Checkbox] 主開關已關閉，需要先開啟主開關');
} else {
    // 使用統一的 tagVisibility 狀態
    if (typeof window.tagVisibility === 'undefined') {
        window.tagVisibility = {};
    }
    if (typeof window.tagVisibility['opt-modified'] === 'undefined') {
        window.tagVisibility['opt-modified'] = true;
    }

    toggleSingleTag('opt-modified');

    // 同步舊的狀態變數（為了向後相容）
    window.modificationVisible = window.tagVisibility['opt-modified'];

    console.log('Modification markers:', window.tagVisibility['opt-modified'] ? 'VISIBLE' : 'HIDDEN');
}