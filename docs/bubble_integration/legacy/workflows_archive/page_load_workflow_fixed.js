// === 修正的 Page Load JavaScript ===

console.log('🚀 Page is loading - Initializing marker system...');

// 初始化標記系統
if (typeof window.initializeMarkerSystem === 'function') {
    window.initializeMarkerSystem();
    console.log('✅ Marker system initialization started');
} else {
    console.log('⚠️ Marker system not ready, will auto-initialize when ready');
}

// 設置初始狀態變數 - 但不自動切換顯示狀態
// 標記預設應該是顯示的（除非用戶手動點擊 toggle）
window.markersCurrentlyVisible = true;

console.log('🟢 Initial state set: Markers visible by default');
console.log('ℹ️ User can toggle markers using the btnToggleTags button');