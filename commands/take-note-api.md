# /take-note-api

記錄 API 開發相關的重要內容到 Obsidian 和專案文檔。

## 功能說明

當你使用 `/take-note-api` 指令時，我會：

1. **擷取當前對話內容**
   - API 設計決策
   - 技術實作細節
   - 問題解決方案
   - 效能優化策略
   - 錯誤處理方案

2. **生成結構化筆記**
   ```markdown
   # API Development Note - YYYY-MM-DD HH:mm
   
   ## 📍 Context
   - Module: [API 模組名稱]
   - Feature: [功能名稱]
   - Type: [Design/Implementation/Debug/Optimization]
   
   ## 🎯 Key Points
   [核心要點整理]
   
   ## 💻 Code/Solution
   [程式碼片段或解決方案]
   
   ## 📊 Performance/Metrics
   [效能指標或測試結果]
   
   ## 🔍 Considerations
   [注意事項或後續優化建議]
   
   ## 🔗 Related
   - API Endpoint: [相關端點]
   - Files: [相關檔案]
   - Issues: [相關議題]
   ```

3. **儲存到多個位置**
   - **Obsidian Quick Notes**: `/Users/yuwenhao/Library/Mobile Documents/iCloud~md~obsidian/Documents/Root/WenHao/Inbox/Qiuck Note/API_[功能]_YYYYMMDD.md`
   - **專案記憶**: `.serena/memories/development_logs/YYYY-MM-DD_[功能]_notes.md`
   - **重要決策**: 如果是架構決策，額外儲存到 `.serena/memories/technical_decisions/`

## 使用時機

- ✅ 完成新 API 端點開發
- ✅ 解決複雜的技術問題
- ✅ 做出重要的架構決策
- ✅ 發現並修復效能瓶頸
- ✅ 實作新的安全機制
- ✅ 整合第三方服務

## 範例

```
User: 我們剛完成了關鍵字提取 API 的優化，執行時間從 2.5 秒降到 0.8 秒
Assistant: /take-note-api
```

## 進階選項

- `/take-note-api --type=design` - 專注於設計決策
- `/take-note-api --type=performance` - 專注於效能優化
- `/take-note-api --type=security` - 專注於安全考量
- `/take-note-api --type=integration` - 專注於整合議題

## 與全域 /take-note 的差異

| 特性 | /take-note | /take-note-api |
|-----|------------|----------------|
| 範圍 | 所有主題 | API 開發專用 |
| 格式 | 通用格式 | API 特定格式 |
| 儲存 | 僅 Obsidian | Obsidian + 專案 |
| 標籤 | 自動判斷 | API 相關標籤 |
| 整合 | 無 | 與專案文檔整合 |

## 自動標籤

筆記會自動加上相關標籤：
- `#api-development`
- `#azure-fastapi`
- `#fhs-architecture`
- 模組特定標籤（如 `#keyword-extraction`）
- 類型標籤（如 `#performance-optimization`）