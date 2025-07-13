// === Page Load Workflow - 雙系統共存版本 ===

console.log('🚀 Page is loading - Initializing dual marker systems...');

// 1. 初始化原本的單一控制系統
if (typeof window.initializeMarkerSystem === 'function') {
    window.initializeMarkerSystem();
    console.log('✅ Single control system initialized');
}

// 2. 初始化多標記控制系統
if (typeof window.initializeMultiTagSystem === 'function') {
    window.initializeMultiTagSystem();
    console.log('✅ Multi-tag control system initialized');
}

// 3. 設置所有狀態變數（與 checkbox 預設值一致）
window.markersCurrentlyVisible = true;      // btnToggleTags 的狀態
window.newSectionVisible = true;            // Checkbox New_Section
window.modificationVisible = true;          // Checkbox Modification
window.placeholdersVisible = true;          // Checkbox Placeholders
window.newKeywordsVisible = true;           // Checkbox New_Keywords_Added
window.existingKeywordsVisible = true;      // Checkbox Existing_Keywords

console.log('🟢 All markers visible by default (matching checkbox states)');
console.log('ℹ️ Users can control markers individually or all at once');