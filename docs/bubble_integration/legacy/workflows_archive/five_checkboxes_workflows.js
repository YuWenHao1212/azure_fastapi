// === 5個 Checkbox 的 Workflow 代碼 ===

// 1. Checkbox New_Section (控制 opt-new)
// 在 "When Checkbox New_Section's value is changed" workflow 中使用：
if (typeof window.newSectionVisible === 'undefined') {
    window.newSectionVisible = true;  // 預設顯示
}
window.newSectionVisible = !window.newSectionVisible;
toggleSingleTag('opt-new', window.newSectionVisible);
console.log('New Section markers:', window.newSectionVisible ? 'VISIBLE' : 'HIDDEN');

// ----------------------------------------

// 2. Checkbox Modification (控制 opt-modified)
// 在 "When Checkbox Modification's value is changed" workflow 中使用：
if (typeof window.modificationVisible === 'undefined') {
    window.modificationVisible = true;  // 預設顯示
}
window.modificationVisible = !window.modificationVisible;
toggleSingleTag('opt-modified', window.modificationVisible);
console.log('Modification markers:', window.modificationVisible ? 'VISIBLE' : 'HIDDEN');

// ----------------------------------------

// 3. Checkbox Placeholders (控制 opt-placeholder)
// 在 "When Checkbox Placeholders's value is changed" workflow 中使用：
if (typeof window.placeholdersVisible === 'undefined') {
    window.placeholdersVisible = true;  // 預設顯示
}
window.placeholdersVisible = !window.placeholdersVisible;
toggleSingleTag('opt-placeholder', window.placeholdersVisible);
console.log('Placeholder markers:', window.placeholdersVisible ? 'VISIBLE' : 'HIDDEN');

// ----------------------------------------

// 4. Checkbox New_Keywords_Added (控制 opt-keyword)
// 在 "When Checkbox New_Keywords_Added's value is changed" workflow 中使用：
if (typeof window.newKeywordsVisible === 'undefined') {
    window.newKeywordsVisible = true;  // 預設顯示
}
window.newKeywordsVisible = !window.newKeywordsVisible;
toggleSingleTag('opt-keyword', window.newKeywordsVisible);
console.log('New Keywords markers:', window.newKeywordsVisible ? 'VISIBLE' : 'HIDDEN');

// ----------------------------------------

// 5. Checkbox Existing_Keywords (控制 opt-keyword-existing)
// 在 "When Checkbox Existing_Keywords's value is changed" workflow 中使用：
if (typeof window.existingKeywordsVisible === 'undefined') {
    window.existingKeywordsVisible = true;  // 預設顯示
}
window.existingKeywordsVisible = !window.existingKeywordsVisible;
toggleSingleTag('opt-keyword-existing', window.existingKeywordsVisible);
console.log('Existing Keywords markers:', window.existingKeywordsVisible ? 'VISIBLE' : 'HIDDEN');