# 雙系統設置總結 - 單一控制 + 個別控制

## 系統架構
1. **主控制** (`btnToggleTags`) - 控制所有標記的顯示/隱藏
2. **個別控制** - 5個 checkbox 分別控制不同類型的標記

## 設置步驟

### 1. Page HTML Header
需要包含兩個系統的代碼：
- 原本的 `page_html_header_complete.html`
- 新增的 `multi_tag_control_header.html`

### 2. Page Load Workflow
使用 `page_load_dual_system.js` 的代碼，初始化兩個系統

### 3. 主 Toggle (btnToggleTags) Workflow
使用 `btnToggleTags_with_sync.js` 的代碼（包含同步機制）

### 4. 5個 Checkbox 的 Workflows
為每個 checkbox 創建 "When value is changed" workflow：
- **Checkbox New_Section** → 使用 `five_checkboxes_workflows.js` 中的第1段代碼
- **Checkbox Modification** → 使用第2段代碼
- **Checkbox Placeholders** → 使用第3段代碼
- **Checkbox New_Keywords_Added** → 使用第4段代碼
- **Checkbox Existing_Keywords** → 使用第5段代碼

## 標記對應關係

| Checkbox 名稱 | 控制的標記類型 | 顏色 | 用途 |
|--------------|---------------|------|------|
| New_Section | opt-new | 綠色 | 新增的段落 |
| Modification | opt-modified | 黃色 | 修改的內容 |
| Placeholders | opt-placeholder | 紅色 | 需要填寫的佔位符 |
| New_Keywords_Added | opt-keyword | 紫色 | 新增的關鍵字 |
| Existing_Keywords | opt-keyword-existing | 藍色 | 已存在的關鍵字 |

## 使用邏輯

### 情境 1：使用主 Toggle
- 點擊 `btnToggleTags` → 顯示/隱藏所有標記
- 所有個別 checkbox 的狀態會同步更新

### 情境 2：使用個別 Checkbox
- 點擊任一 checkbox → 只影響對應的標記類型
- 其他標記保持不變
- 主 toggle 不受影響

### 情境 3：混合使用
1. 先用主 toggle 隱藏所有標記
2. 再勾選特定 checkbox 顯示需要的標記
3. 例如：只顯示 Placeholders 和 New Keywords

## 優點
- ✅ 靈活性高：可以快速控制全部，也可以精細控制個別
- ✅ 狀態清晰：每個 checkbox 直觀顯示該類型標記的狀態
- ✅ 使用簡單：每個控制都是獨立的 toggle 邏輯
- ✅ 擴展性好：容易添加新的標記類型

## 注意事項
1. 所有 checkbox 預設為 checked（與頁面載入時標記顯示一致）
2. 主 toggle 會覆蓋個別設定（使用時會同步所有狀態）
3. 確保在 TinyMCE 完全載入後才操作標記