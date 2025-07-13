// === 在 btnToggleTags changed event 的 Run JavaScript action 中使用這段代碼 ===

// 調試：顯示當前狀態
console.log('=== btnToggleTags Changed Event ===');

// 獲取 toggle 狀態的多種方法
var isChecked = false;

// 方法 1: 嘗試從 Bubble 的當前元素獲取
try {
    // 如果 Bubble 支持這種語法
    isChecked = Current cell's btnToggleTags is checked;
    console.log('方法1 - Bubble syntax: checked =', isChecked);
} catch (e1) {
    // 方法 2: 從 DOM 查找
    try {
        var toggleInput = document.querySelector('[data-element-name="btnToggleTags"] input[type="checkbox"]');
        if (!toggleInput) {
            // 嘗試其他選擇器
            toggleInput = document.querySelector('input[type="checkbox"][id*="btnToggleTags"]');
        }
        if (!toggleInput) {
            // 嘗試尋找最近變更的 checkbox
            toggleInput = event.target;
        }
        
        if (toggleInput) {
            isChecked = toggleInput.checked;
            console.log('方法2 - DOM查找: checked =', isChecked);
        }
    } catch (e2) {
        console.log('無法從 DOM 獲取狀態');
    }
}

// 方法 3: 如果上述都失敗，使用一個全局變量來追蹤狀態
if (typeof window.btnToggleTagsState === 'undefined') {
    window.btnToggleTagsState = true; // 初始狀態
}
// 每次點擊時切換狀態
window.btnToggleTagsState = !window.btnToggleTagsState;
isChecked = window.btnToggleTagsState;
console.log('方法3 - 全局變量: checked =', isChecked);

// 執行切換
console.log('執行切換 - ' + (isChecked ? '顯示' : '隱藏') + '標記');

// 調用修正版的 toggle 函數
if (typeof toggleTinyMCEMarkersFixed === 'function') {
    var hideMarkers = !isChecked;  // checked = 顯示，所以要反轉
    toggleTinyMCEMarkersFixed(hideMarkers);
} else if (typeof toggleTinyMCEMarkers === 'function') {
    var hideMarkers = !isChecked;
    toggleTinyMCEMarkers(hideMarkers);
} else {
    console.error('Toggle 函數未定義！');
}

// 驗證結果
setTimeout(function() {
    if (typeof checkMarkerState === 'function') {
        checkMarkerState();
    }
}, 100);