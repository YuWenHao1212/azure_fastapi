// === 個別 Toggle 的 Workflow 代碼 ===

// 1. 新增區段 Toggle (btnToggleOptNew)
// 在 btnToggleOptNew changed event 中使用：
if (typeof window.optNewVisible === 'undefined') {
    window.optNewVisible = true;
}
window.optNewVisible = !window.optNewVisible;
toggleSingleTag('opt-new', window.optNewVisible);

// ----------------------------------------

// 2. 修改內容 Toggle (btnToggleOptModified)
// 在 btnToggleOptModified changed event 中使用：
if (typeof window.optModifiedVisible === 'undefined') {
    window.optModifiedVisible = true;
}
window.optModifiedVisible = !window.optModifiedVisible;
toggleSingleTag('opt-modified', window.optModifiedVisible);

// ----------------------------------------

// 3. 佔位符 Toggle (btnToggleOptPlaceholder)
// 在 btnToggleOptPlaceholder changed event 中使用：
if (typeof window.optPlaceholderVisible === 'undefined') {
    window.optPlaceholderVisible = true;
}
window.optPlaceholderVisible = !window.optPlaceholderVisible;
toggleSingleTag('opt-placeholder', window.optPlaceholderVisible);

// ----------------------------------------

// 4. 新關鍵字 Toggle (btnToggleOptKeyword)
// 在 btnToggleOptKeyword changed event 中使用：
if (typeof window.optKeywordVisible === 'undefined') {
    window.optKeywordVisible = true;
}
window.optKeywordVisible = !window.optKeywordVisible;
toggleSingleTag('opt-keyword', window.optKeywordVisible);

// ----------------------------------------

// 5. 現有關鍵字 Toggle (btnToggleOptKeywordExisting)
// 在 btnToggleOptKeywordExisting changed event 中使用：
if (typeof window.optKeywordExistingVisible === 'undefined') {
    window.optKeywordExistingVisible = true;
}
window.optKeywordExistingVisible = !window.optKeywordExistingVisible;
toggleSingleTag('opt-keyword-existing', window.optKeywordExistingVisible);

// ----------------------------------------

// 6. 全部顯示按鈕 (btnShowAllTags)
// 在 btnShowAllTags clicked event 中使用：
showAllTags();
// 重置所有狀態
window.optNewVisible = true;
window.optModifiedVisible = true;
window.optPlaceholderVisible = true;
window.optKeywordVisible = true;
window.optKeywordExistingVisible = true;

// ----------------------------------------

// 7. 全部隱藏按鈕 (btnHideAllTags)
// 在 btnHideAllTags clicked event 中使用：
hideAllTags();
// 重置所有狀態
window.optNewVisible = false;
window.optModifiedVisible = false;
window.optPlaceholderVisible = false;
window.optKeywordVisible = false;
window.optKeywordExistingVisible = false;