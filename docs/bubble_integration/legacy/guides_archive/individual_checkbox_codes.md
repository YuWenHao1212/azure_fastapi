# 5個 Checkbox 的個別 Workflow 代碼

## 1. Checkbox New_Section
在 "When Checkbox New_Section's value is changed" workflow 中，添加 Run JavaScript action，使用以下代碼：

```javascript
if (typeof window.newSectionVisible === 'undefined') {
    window.newSectionVisible = true;
}
window.newSectionVisible = !window.newSectionVisible;
toggleSingleTag('opt-new', window.newSectionVisible);
console.log('New Section markers:', window.newSectionVisible ? 'VISIBLE' : 'HIDDEN');
```

## 2. Checkbox Modification
在 "When Checkbox Modification's value is changed" workflow 中，添加 Run JavaScript action，使用以下代碼：

```javascript
if (typeof window.modificationVisible === 'undefined') {
    window.modificationVisible = true;
}
window.modificationVisible = !window.modificationVisible;
toggleSingleTag('opt-modified', window.modificationVisible);
console.log('Modification markers:', window.modificationVisible ? 'VISIBLE' : 'HIDDEN');
```

## 3. Checkbox Placeholders
在 "When Checkbox Placeholders's value is changed" workflow 中，添加 Run JavaScript action，使用以下代碼：

```javascript
if (typeof window.placeholdersVisible === 'undefined') {
    window.placeholdersVisible = true;
}
window.placeholdersVisible = !window.placeholdersVisible;
toggleSingleTag('opt-placeholder', window.placeholdersVisible);
console.log('Placeholder markers:', window.placeholdersVisible ? 'VISIBLE' : 'HIDDEN');
```

## 4. Checkbox New_Keywords_Added
在 "When Checkbox New_Keywords_Added's value is changed" workflow 中，添加 Run JavaScript action，使用以下代碼：

```javascript
if (typeof window.newKeywordsVisible === 'undefined') {
    window.newKeywordsVisible = true;
}
window.newKeywordsVisible = !window.newKeywordsVisible;
toggleSingleTag('opt-keyword', window.newKeywordsVisible);
console.log('New Keywords markers:', window.newKeywordsVisible ? 'VISIBLE' : 'HIDDEN');
```

## 5. Checkbox Existing_Keywords
在 "When Checkbox Existing_Keywords's value is changed" workflow 中，添加 Run JavaScript action，使用以下代碼：

```javascript
if (typeof window.existingKeywordsVisible === 'undefined') {
    window.existingKeywordsVisible = true;
}
window.existingKeywordsVisible = !window.existingKeywordsVisible;
toggleSingleTag('opt-keyword-existing', window.existingKeywordsVisible);
console.log('Existing Keywords markers:', window.existingKeywordsVisible ? 'VISIBLE' : 'HIDDEN');
```

## 設置步驟說明

1. 在 Bubble 編輯器中，選擇第一個 checkbox (New_Section)
2. 點擊 "Start/Edit workflow"
3. 添加 Event: "When an input's value is changed"
4. 添加 Action: "Run JavaScript"
5. 將上面對應的代碼貼入 "JavaScript to run" 欄位
6. 對其他 4 個 checkbox 重複步驟 1-5，使用各自對應的代碼

## 重要提醒
- 每個 checkbox 必須使用自己對應的代碼
- 不要把所有代碼放在一起
- 確保 workflow 觸發條件是 "When value is changed"