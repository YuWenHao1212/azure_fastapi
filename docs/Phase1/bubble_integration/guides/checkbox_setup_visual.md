# Checkbox 設置視覺化指南

## 對應關係圖

```
┌─────────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Checkbox New_Section   │ ───► │  Workflow Event     │ ───► │  opt-new (綠色)     │
│  ☑ (預設勾選)          │      │  value changed      │      │  新增區段標記        │
└─────────────────────────┘      └─────────────────────┘      └─────────────────────┘
              ↓
    使用 Checkbox 1 的代碼

┌─────────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Checkbox Modification  │ ───► │  Workflow Event     │ ───► │  opt-modified (黃)  │
│  ☑ (預設勾選)          │      │  value changed      │      │  修改內容標記        │
└─────────────────────────┘      └─────────────────────┘      └─────────────────────┘
              ↓
    使用 Checkbox 2 的代碼

┌─────────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Checkbox Placeholders  │ ───► │  Workflow Event     │ ───► │  opt-placeholder    │
│  ☑ (預設勾選)          │      │  value changed      │      │  (紅) 佔位符標記     │
└─────────────────────────┘      └─────────────────────┘      └─────────────────────┘
              ↓
    使用 Checkbox 3 的代碼

┌─────────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Checkbox               │ ───► │  Workflow Event     │ ───► │  opt-keyword (紫)   │
│  New_Keywords_Added     │      │  value changed      │      │  新關鍵字標記        │
│  ☑ (預設勾選)          │      │                     │      │                     │
└─────────────────────────┘      └─────────────────────┘      └─────────────────────┘
              ↓
    使用 Checkbox 4 的代碼

┌─────────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  Checkbox               │ ───► │  Workflow Event     │ ───► │  opt-keyword-       │
│  Existing_Keywords      │      │  value changed      │      │  existing (藍)      │
│  ☑ (預設勾選)          │      │                     │      │  現有關鍵字標記      │
└─────────────────────────┘      └─────────────────────┘      └─────────────────────┘
              ↓
    使用 Checkbox 5 的代碼
```

## Bubble Workflow 設置步驟

### 步驟 1：選擇 Checkbox
1. 在 Bubble 編輯器中點擊 checkbox 元素
2. 確認元素名稱（如 "Checkbox New_Section"）

### 步驟 2：創建 Workflow
1. 點擊 "Start/Edit workflow"
2. 選擇觸發事件：
   - Event: "Elements" → "An input's value is changed"
   - Element: 選擇對應的 checkbox

### 步驟 3：添加 JavaScript Action
1. 點擊 "Add an action"
2. 選擇 "Plugins" → "Run javascript"
3. 在 "JavaScript to run" 欄位貼入對應的代碼

### 步驟 4：重複其他 Checkbox
對每個 checkbox 重複步驟 1-3，使用各自的代碼

## 快速檢查清單

- [ ] Checkbox New_Section → 使用第 1 段代碼
- [ ] Checkbox Modification → 使用第 2 段代碼
- [ ] Checkbox Placeholders → 使用第 3 段代碼
- [ ] Checkbox New_Keywords_Added → 使用第 4 段代碼
- [ ] Checkbox Existing_Keywords → 使用第 5 段代碼

## 測試方法
1. 重新載入頁面，確認所有標記都顯示
2. 逐一測試每個 checkbox
3. 開啟瀏覽器 Console 查看日誌訊息
4. 確認對應的標記類型正確顯示/隱藏