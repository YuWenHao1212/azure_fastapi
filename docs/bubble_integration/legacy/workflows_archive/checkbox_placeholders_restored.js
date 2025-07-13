// === Checkbox Placeholders 的 Workflow - 標準版本 ===
// 在 "When Checkbox Placeholders's value is changed" workflow 中使用：

if (typeof window.placeholdersVisible === 'undefined') {
    window.placeholdersVisible = true;  // 預設顯示
}
window.placeholdersVisible = !window.placeholdersVisible;
toggleSingleTag('opt-placeholder', window.placeholdersVisible);
console.log('Placeholder markers:', window.placeholdersVisible ? 'VISIBLE' : 'HIDDEN');