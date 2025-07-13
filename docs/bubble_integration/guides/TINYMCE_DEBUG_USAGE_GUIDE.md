# TinyMCE Debug 工具使用指南

## 🎯 工具目的

在 Bubble.io 中找出 TinyMCE Rich Text Editor 的確切物件名稱和 HTML 結構，以便正確獲取和插入內容。

## 🔧 工具版本

### 1. 完整版除錯工具 (`tinymce_debug_tool.html`)
- 功能最完整，適合深度分析
- 大型介面，適合桌面使用

### 2. 快速測試工具 (`bubble_tinymce_quick_test.html`) ⭐ **推薦**
- 輕量級，載入快速
- 浮動介面，不影響 Bubble.io 操作
- 位置：左下角，可最小化

## 🚀 使用步驟

### Step 1: 整合到 Bubble.io

1. **添加 HTML Element**
   - 在 Bubble Editor 中新增 HTML Element
   - 將 `bubble_tinymce_quick_test.html` 的完整內容貼入

2. **預覽頁面**
   - 確保頁面包含 Rich Text Editor
   - 工具會自動出現在左下角

### Step 2: 基本檢測流程

#### 🔍 **檢測** (第一步)
- 檢查 TinyMCE 是否載入
- 顯示版本和編輯器數量
- 確認基本狀態

#### 🌐 **全域物件** (第二步)
- 搜尋所有可能的編輯器全域物件
- 檢查 `window.tinymce`, `window.bubble` 等
- 找出物件的屬性和方法

#### 🔍 **深度掃描** (第三步)
- 掃描所有包含關鍵字的 HTML 元素
- 搜尋 ID, Class, Data 屬性
- 找出所有可編輯元素

#### 🫧 **Bubble元素** (第四步)
- 專門掃描 Bubble.io 特有元素
- 檢查 `.bubble-element`, `.RichTextEditor` 等
- 分析元素的 data 屬性和事件處理器

#### 🔄 **監控DOM** (關鍵功能)
- **即時監控** DOM 變化
- 捕捉動態載入的編輯器
- 自動識別新增的編輯器元素

## 🎯 重點功能說明

### 監控 DOM 功能 ⭐
```
點擊「監控DOM」→ 開始即時監控
在 Bubble.io 中點擊 Rich Text Editor → 會捕捉到編輯器初始化
工具會自動識別並報告新增的編輯器元素
```

### 全域物件搜尋
- 檢查常見編輯器物件：`tinymce`, `editor`, `bubble`
- 搜尋 window 物件中的所有編輯器相關屬性
- 顯示物件的方法和屬性

### 深度 HTML 掃描
- 使用關鍵字搜尋：`editor`, `rich`, `text`, `mce`, `tiny`, `bubble`
- 檢查 ID, Class, Data 屬性
- 找出所有 `contentEditable="true"` 元素

## 📋 常見發現和解決方案

### 情況 1: TinyMCE 已載入但沒有編輯器
```
現象：✅ TinyMCE v6.8.3 已載入，🔧 編輯器數量: 0
原因：Bubble.io 延遲初始化編輯器
解決：使用「監控DOM」功能，然後點擊 Rich Text Editor
```

### 情況 2: 編輯器在 iframe 中
```
現象：深度掃描找到 iframe 元素
解決：工具會自動檢查 iframe 內容並設置 currentIframeEditor
```

### 情況 3: 找不到可編輯元素
```
原因：編輯器可能使用自定義實現
解決：使用「Bubble元素」掃描，檢查所有 .bubble-element
```

### 情況 4: 動態載入的編輯器
```
現象：初始掃描沒找到，但用戶互動後出現
解決：「監控DOM」會即時捕捉動態載入的元素
```

## 🔧 除錯技巧

### 1. 按順序使用功能
```
檢測 → 全域物件 → 深度掃描 → Bubble元素 → 監控DOM
```

### 2. 關注日誌輸出
- ✅ 綠色：成功找到重要元素
- ⚠️ 黃色：警告或可能的問題
- ❌ 紅色：錯誤或找不到

### 3. 使用監控功能
```javascript
// 開啟監控後，在 Bubble.io 中：
1. 點擊 Rich Text Editor
2. 開始輸入內容
3. 觀察工具的即時報告
```

### 4. 查看瀏覽器 Console
- 所有日誌同時輸出到 Console
- 使用 `[TinyMCE Quick Test]` 前綴
- 方便複製和分析

## 📊 實際使用範例

### 找到編輯器後的操作

```javascript
// 如果工具找到了編輯器，可以在 Console 中測試：

// 方法 1: 使用 TinyMCE API
if (tinymce.editors.length > 0) {
    const editor = tinymce.editors[0];
    console.log('編輯器內容:', editor.getContent());
    editor.setContent('<p>測試內容</p>');
}

// 方法 2: 使用 iframe 編輯器
if (window.currentIframeEditor) {
    console.log('iframe 內容:', window.currentIframeEditor.innerHTML);
    window.currentIframeEditor.innerHTML = '<p>測試內容</p>';
}

// 方法 3: 直接操作可編輯元素
const editableEl = document.querySelector('[contenteditable="true"]');
if (editableEl) {
    console.log('可編輯元素內容:', editableEl.innerHTML);
    editableEl.innerHTML = '<p>測試內容</p>';
}
```

## 🎯 目標輸出

成功使用工具後，您應該能夠：

1. **確認編輯器類型**
   - TinyMCE 版本
   - 是否在 iframe 中
   - 具體的 DOM 結構

2. **獲取編輯器物件**
   - `tinymce.editors[0]` (如果是標準 TinyMCE)
   - `window.currentIframeEditor` (如果在 iframe 中)
   - 具體的 DOM 元素選擇器

3. **操作方法**
   - `getContent()` / `setContent()` (TinyMCE API)
   - `.innerHTML` (直接 DOM 操作)
   - 元素的具體 ID 或 Class

## 🔍 故障排除

### 工具無法載入
- 檢查 HTML Element 是否正確貼入完整代碼
- 確認沒有 JavaScript 錯誤

### 找不到編輯器
- 使用「監控DOM」功能
- 確保在編輯器載入後才開始檢測
- 嘗試與 Rich Text Editor 互動

### 無法獲取內容
- 確認編輯器已完全初始化
- 檢查是否有跨域限制 (iframe)
- 使用多種方法嘗試獲取

---

**🎉 使用這個工具，您將能夠完全掌握 Bubble.io 中 TinyMCE 的實現細節，並成功整合 Resume Tailoring API 的視覺標記功能！**