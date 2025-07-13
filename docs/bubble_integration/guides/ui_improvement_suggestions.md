# Resume Tailoring UI 改善建議

## 現有問題分析

### 1. 關鍵字標記過於廣泛
**現狀**：整個段落或列表項被標記為黃色
**改善**：只標記具體的關鍵字詞

### 2. 視覺標記建議

#### A. 關鍵字標記 (opt-keyword)
```css
.opt-keyword {
    background-color: #FEF3C7;  /* 淺黃色背景 */
    color: #92400E;             /* 深棕色文字 */
    padding: 0 3px;             /* 小內距 */
    border-radius: 2px;         /* 圓角 */
    font-weight: 500;           /* 稍微粗體 */
}
```

#### B. 強化內容標記 (opt-strength)
```css
.opt-strength {
    background-color: #DBEAFE;  /* 淺藍色背景 */
    color: #1E40AF;             /* 深藍色文字 */
    padding: 0 3px;
    border-radius: 2px;
    font-weight: 500;
}
```

#### C. 佔位符標記 (opt-placeholder)
```css
.opt-placeholder {
    background-color: #FEE2E2;  /* 淺紅色背景 */
    color: #991B1B;             /* 深紅色文字 */
    border: 1px dashed #F87171; /* 虛線邊框 */
    padding: 2px 8px;
    border-radius: 4px;
    font-style: italic;
    cursor: pointer;
}
```

#### D. 新增內容標記 (opt-new)
```css
.opt-new {
    background-color: #D1FAE5;  /* 淺綠色背景 */
    padding: 8px 12px;          /* 整段標記 */
    border-left: 4px solid #10B981; /* 左邊框 */
    margin: 8px 0;
}
```

#### E. 改善內容標記 (opt-improvement)
```css
.opt-improvement {
    border-bottom: 2px solid #10B981; /* 綠色底線 */
    color: #065F46;                   /* 深綠色文字 */
}
```

## 3. API 層面的改善建議

### A. 更精準的關鍵字標記策略

**現有問題**：
```html
<!-- 不好的標記方式 -->
<li class="opt-keyword">Data Visualization: Tableau, Power BI, Superset</li>
```

**改善後**：
```html
<!-- 好的標記方式 -->
<li>Data Visualization: <span class="opt-keyword">Tableau</span>, <span class="opt-keyword">Power BI</span>, <span class="opt-keyword">Superset</span></li>
```

### B. 分層標記策略

1. **句子級別標記**：用於新增或大幅改寫的內容
   - 使用 `opt-new` 或 `opt-improvement` 在段落或列表項級別

2. **詞彙級別標記**：用於關鍵字和具體改進
   - 使用 `opt-keyword` 只標記具體的關鍵字
   - 使用 `opt-strength` 標記突出的優勢詞彙
   - 使用 `opt-placeholder` 標記需要填寫的佔位符

### C. 實施範例

```python
def apply_keyword_markers(text: str, keywords: List[str]) -> str:
    """只在具體關鍵字上應用標記，而非整個句子"""
    for keyword in keywords:
        # 使用正則表達式進行全詞匹配
        pattern = r'\b' + re.escape(keyword) + r'\b'
        replacement = f'<span class="opt-keyword">{keyword}</span>'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def apply_improvement_markers(original_text: str, improved_text: str, improvements: List[str]) -> str:
    """分層應用改進標記"""
    # 如果是全新內容
    if not original_text.strip():
        return f'<p class="opt-new">{improved_text}</p>'
    
    # 如果是改進的內容
    if has_significant_changes(original_text, improved_text):
        # 先在段落級別標記
        result = f'<div class="opt-improvement">{improved_text}</div>'
        # 然後標記具體的關鍵字
        for keyword in extract_new_keywords(original_text, improved_text):
            result = apply_keyword_markers(result, [keyword])
        return result
    
    # 否則只標記新增的關鍵字
    return apply_keyword_markers(improved_text, extract_new_keywords(original_text, improved_text))
```

## 4. CSS 優化建議

```css
/* 確保標記不會影響排版 */
.opt-keyword,
.opt-strength,
.opt-placeholder {
    display: inline;
    line-height: inherit;
    margin: 0;
    transition: background-color 0.2s ease;
}

/* 滑鼠懸停效果 */
.opt-keyword:hover {
    background-color: #FDE68A;
}

.opt-strength:hover {
    background-color: #BFDBFE;
}

.opt-placeholder:hover {
    background-color: #FECACA;
    border-color: #EF4444;
}

/* 列印樣式 */
@media print {
    .opt-keyword,
    .opt-strength {
        background-color: transparent !important;
        font-weight: 600;
        text-decoration: underline;
    }
    
    .opt-placeholder {
        border: 1px solid #000;
        background-color: transparent !important;
    }
}
```

## 5. 實施優先順序

1. **立即改善**：修改關鍵字標記邏輯，只標記具體詞彙
2. **短期改善**：優化 CSS 樣式，改善視覺層次
3. **中期改善**：實施分層標記策略
4. **長期改善**：加入互動功能（如點擊關鍵字查看說明）

## 6. 預期效果

- 更清晰的視覺層次
- 更精準的改進指示
- 更好的可讀性
- 保持專業的外觀