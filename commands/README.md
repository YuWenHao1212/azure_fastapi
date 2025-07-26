# 專案斜線指令說明

本目錄包含 Azure FastAPI 專案的專屬斜線指令。

## 指令清單

### `/organize-api-notes`
整理專案的開發筆記，生成階段性總結報告。

**使用方式**：
```
/organize-api-notes
/organize-api-notes --period=week
/organize-api-notes --from=2025-07-01 --to=2025-07-15
```

**詳細說明**：[organize-api-notes.md](./organize-api-notes.md)

## 自動同步機制

所有斜線指令都會透過 `sync-notes.sh` 腳本自動同步內容到：

1. **Obsidian Quick Notes**
   - 路徑：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Root/WenHao/Inbox/Qiuck Note/`
   - 格式：`API_[類型]_YYYY-MM-DD_HH-MM.md`

2. **專案記憶系統**
   - 開發日誌：`.serena/memories/development_logs/`
   - 技術決策：`.serena/memories/technical_decisions/`
   - 進度總結：`.serena/memories/development_progress/`

3. **專案文檔**（重要內容）
   - 週總結：`docs/published/WEEKLY_SUMMARY_YYYYMMDD.md`
   - API 變更：`docs/published/API_CHANGES_YYYYMMDD.md`

## 設定方式

這些斜線指令已經在專案的 `CLAUDE.md` 中註冊，Claude Code 會自動識別。

如需在其他專案使用類似功能，可以：
1. 複製 `commands/` 目錄
2. 修改路徑設定
3. 在專案 `CLAUDE.md` 中添加引用

## 與全域指令的關係

- 全域指令（`/take-note`、`/organize-notes`）：通用知識管理，包括 API 開發筆記
- 專案指令（`/organize-api-notes`）：專門整理 API 開發總結

建議統一使用 `/take-note` 記錄所有筆記，保持簡單。

## 維護說明

- 指令定義：`*.md` 檔案
- 同步腳本：`sync-notes.sh`
- 路徑配置：在腳本中的變數區塊

如需修改同步路徑或行為，編輯 `sync-notes.sh` 中的相關設定。