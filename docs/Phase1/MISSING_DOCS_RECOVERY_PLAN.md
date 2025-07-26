# 文檔恢復計劃

## 現況分析

經過詳細搜索，發現：
1. 在 git 歷史中找不到 `docs/published/` 下的 API 文檔
2. Azure DevOps Wiki 訪問需要額外配置
3. `.serena` 記憶系統中提到文檔已建立，但實際文件缺失
4. CLAUDE.md 中引用了這些文檔，但文件不存在

## 可能原因
- 文檔創建後未正確提交到 git
- 文檔被意外刪除或移動
- 文檔可能只存在於 Azure DevOps Wiki 中

## 恢復方案

### 方案 A：從 Azure DevOps Wiki 恢復
```bash
# 1. 獲取 Wiki 內容
az devops wiki page show --path "/API/Published/Design" --wiki "API"

# 2. 下載所有文檔
# 需要具體的 Wiki 路徑結構
```

### 方案 B：基於代碼重建（推薦）
基於現有代碼實現，我已經能夠重建核心文檔：

1. **API_SPECIFICATION_V3.md** - 從 `src/api/v1/` 代碼重建 ✅
2. **ARCHITECTURE_FHS.md** - 從項目結構重建 ✅
3. **REQUIREMENTS_KEYWORD_EXTRACTION.md** - 從代碼註釋和 CLAUDE.md 重建 ✅

### 方案 C：從 .serena 記錄恢復
檢查 `.serena/memories/` 中的詳細記錄，可能包含文檔內容片段。

## 建議行動

1. **立即行動**：使用方案 B 重建的文檔（已完成）
2. **後續行動**：
   - 嘗試從 Azure DevOps Wiki 獲取原始文檔
   - 對比重建文檔與原始文檔（如果找到）
   - 建立文檔版本控制最佳實踐

## 已重建的文檔清單
- [x] API_SPECIFICATION_V3.md - API 端點規格
- [x] ARCHITECTURE_FHS.md - 系統架構
- [x] REQUIREMENTS_KEYWORD_EXTRACTION.md - 需求規格
- [ ] DESIGN_KEYWORD_EXTRACTION.md - 詳細設計
- [ ] API_QUICK_REFERENCE.md - API 快速參考
- [ ] IMPLEMENTATION_GUIDE.md - 實施指南

## 文檔管理建議
1. 所有文檔必須及時提交到 git
2. 重要文檔保持多份備份（git + Wiki）
3. 使用文檔索引追蹤所有文檔狀態
4. 定期審查文檔完整性