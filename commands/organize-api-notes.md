# /organize-api-notes

整理本專案的 API 開發筆記和記錄，生成階段性總結。

## 功能說明

當你使用 `/organize-api-notes` 指令時，我會：

1. **收集專案記錄**
   - `.serena/memories/development_logs/` 中的開發日誌
   - `.serena/memories/technical_decisions/` 中的技術決策
   - `.serena/memories/api_analysis/` 中的 API 分析
   - `docs/` 中的相關文檔

2. **分析並整理內容**
   - 按時間軸整理開發進度
   - 歸納技術決策和理由
   - 總結已完成的功能
   - 識別待解決的問題
   - 提取經驗教訓

3. **生成總結報告**
   ```markdown
   # API Development Summary - [Period]
   
   ## 📈 Progress Overview
   - Period: [開始日期] ~ [結束日期]
   - Completed Features: [數量]
   - API Endpoints: [新增/修改的端點]
   - Test Coverage: [測試覆蓋率]
   
   ## ✅ Completed Work
   ### [功能名稱]
   - Description: [簡述]
   - API Changes: [變更內容]
   - Key Decisions: [關鍵決策]
   - Performance: [效能指標]
   
   ## 🚧 Ongoing Tasks
   [進行中的工作項目]
   
   ## 📊 Metrics & Performance
   - API Response Time: [平均回應時間]
   - Error Rate: [錯誤率]
   - Test Pass Rate: [測試通過率]
   
   ## 💡 Key Learnings
   [本期學到的重要經驗]
   
   ## 🎯 Next Steps
   [下一階段的計劃]
   
   ## 📝 Technical Decisions Log
   [重要技術決策記錄]
   ```

4. **輸出到指定位置**
   - 預設：`.serena/memories/development_progress/SUMMARY_[YYYYMMDD].md`
   - 週總結：`docs/published/WEEKLY_SUMMARY_[YYYYMMDD].md`
   - Obsidian：同步到個人知識庫

## 使用方式

### 基本用法
```
/organize-api-notes
```
整理最近 7 天的開發記錄

### 進階選項
```
/organize-api-notes --period=week    # 週總結（預設）
/organize-api-notes --period=month   # 月總結
/organize-api-notes --period=sprint  # Sprint 總結
/organize-api-notes --from=2025-07-01 --to=2025-07-15  # 自訂時間範圍
```

### 特定主題整理
```
/organize-api-notes --topic=performance     # 效能相關總結
/organize-api-notes --topic=security       # 安全相關總結
/organize-api-notes --topic=architecture   # 架構相關總結
/organize-api-notes --module=keyword-extraction  # 特定模組總結
```

## 自動化觸發

建議設定以下時機自動執行：
- **每週五下午**：生成週總結
- **Sprint 結束時**：生成 Sprint 總結
- **重大版本發布前**：生成版本總結

## 整合功能

### 1. Work Item 追蹤
- 自動關聯 Azure DevOps Work Items
- 統計完成率和進度

### 2. Git 歷史分析
- 分析 commit 記錄
- 統計代碼變更量
- 識別熱點檔案

### 3. 測試報告整合
- 整合測試覆蓋率報告
- 追蹤測試通過率趨勢
- 標記需要改進的測試

### 4. API 文檔更新
- 檢查 API 文檔是否同步
- 標記需要更新的文檔
- 生成變更日誌

## 輸出範例

```markdown
# API Development Summary - Week 2025-07-15 to 2025-07-21

## 📈 Progress Overview
- Period: 2025-07-15 ~ 2025-07-21
- Completed Features: 3
- API Endpoints: 2 new, 3 modified
- Test Coverage: 85.3% (+2.1%)

## ✅ Completed Work

### Course Search API Optimization
- Description: Simplified response format for better frontend integration
- API Changes: Added `course_type` field, converted similarity_score to percentage
- Key Decisions: Merged 7 course types into 5 for simplicity
- Performance: Response time unchanged, better UX

### Test Environment Enhancement
- Description: Added --real-creds option for integration testing
- API Changes: None
- Key Decisions: Support both test and real credentials
- Performance: Reduced false test failures by 90%

[... 更多內容 ...]
```

## 與其他工具的配合

1. **配合 /take-note-api**
   - 先用 `/take-note-api` 記錄單次討論
   - 再用 `/organize-api-notes` 生成總結

2. **配合 CI/CD**
   - 部署成功後自動觸發總結
   - 包含部署指標和監控數據

3. **配合專案管理**
   - 生成進度報告供會議使用
   - 自動更新專案看板