# Bubble.io TinyMCE 標記切換 - 完整設置指南

## 步驟 1：Page HTML Header
將 `page_html_header_complete.html` 的完整內容複製到 Bubble Page 的 HTML header。

## 步驟 2：Page is loaded workflow
替換成以下代碼：

```javascript
// === 更新的 Page Load JavaScript ===

console.log('🚀 Page is loading - Initializing marker system...');

// 初始化標記系統
if (typeof window.initializeMarkerSystem === 'function') {
    window.initializeMarkerSystem();
    console.log('✅ Marker system initialization started');
} else {
    console.log('⚠️ Marker system not ready, will auto-initialize when ready');
}

// 設置初始狀態
setTimeout(function() {
    console.log('🔍 Checking initial toggle state...');
    
    const toggleElement = document.getElementById('btnToggleTags');
    if (toggleElement) {
        const isChecked = toggleElement.checked;
        console.log(`📌 Toggle found - Checked: ${isChecked}`);
        
        window.markersCurrentlyVisible = isChecked;
        
        if (!isChecked && typeof window.toggleTinyMCEMarkers === 'function') {
            window.toggleTinyMCEMarkers(true);
            console.log('🔴 Initial state: Markers hidden');
        } else {
            console.log('🟢 Initial state: Markers visible');
        }
    } else {
        console.log('⚠️ Toggle not found, default: markers visible');
        window.markersCurrentlyVisible = true;
    }
}, 2000);
```

## 步驟 3：btnToggleTags changed event workflow
使用以下代碼：

```javascript
// === Toggle 切換事件 ===

if (typeof window.markersCurrentlyVisible === 'undefined') {
    window.markersCurrentlyVisible = true;
}

window.markersCurrentlyVisible = !window.markersCurrentlyVisible;

if (typeof window.toggleTinyMCEMarkers === 'function') {
    window.toggleTinyMCEMarkers(!window.markersCurrentlyVisible);
    console.log('Markers are now:', window.markersCurrentlyVisible ? 'VISIBLE' : 'HIDDEN');
} else {
    console.error('Toggle function not found');
}
```

## 重要：移除舊代碼
確保移除所有引用以下內容的代碼：
- `TinyMCETagControl`
- `toggleTinyMCETags` （注意是 Tags 不是 Markers）
- `injectTinyMCEStyles`

## 預期行為
1. 頁面載入時，根據 toggle 的初始狀態顯示/隱藏標記
2. 點擊 toggle 時正確切換標記的顯示狀態
3. Toggle checked = 顯示標記
4. Toggle unchecked = 隱藏標記