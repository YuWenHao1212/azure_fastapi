# 關鍵字標準化系統變更記錄

本文檔記錄所有對關鍵字標準化字典和規則的重要變更。

---

## 變更格式說明

每個變更條目應包含：
- **日期**: YYYY-MM-DD
- **類型**: Added/Changed/Deprecated/Removed/Fixed
- **影響**: 哪些檔案被修改
- **描述**: 具體變更內容
- **原因**: 為什麼需要這個變更
- **影響範圍**: 可能影響的功能

---

## [1.0.0] - 2025-07-02

### 🎉 初始版本發布

#### Added
- 建立完整的字典外部化系統
- 創建 4 個 YAML 配置檔案：
  - `skills.yaml`: 250 個技能映射
  - `positions.yaml`: 95 個職位映射
  - `tools.yaml`: 170 個工具映射
  - `patterns.yaml`: 66 個模式規則
- 實作 `validate_dictionaries.py` 驗證工具
- 建立完整的維護文檔系統

#### Changed
- 將 `KeywordStandardizer` 從硬編碼改為 YAML 載入
- 重構程式碼支援熱更新功能

#### Fixed
- 修正重複映射問題（15 個條目）
- 修正 scikit-learn 自引用問題
- 改進驗證邏輯，減少誤報

---

## 變更模板

```markdown
## [版本號] - YYYY-MM-DD

### Added (新增)
- 新增 X 個 [類別] 映射到 [檔案名]
  - 具體映射列表...
  - 原因：...

### Changed (修改)
- 修改 [原映射] 為 [新映射]
  - 檔案：[檔案名]
  - 原因：...
  - 影響：...

### Deprecated (棄用)
- 標記 [映射] 為棄用
  - 計劃移除日期：...
  - 替代方案：...

### Removed (移除)
- 移除 [映射]
  - 原因：...
  - 遷移指南：...

### Fixed (修復)
- 修正 [問題描述]
  - 影響範圍：...
  - 解決方案：...
```

---

## 即將進行的變更

### 計劃中 - 2025-07

#### Planned Additions
- [ ] Rust 生態系統術語（預計 15-20 個）
- [ ] AI/ML 新工具（LangChain, Hugging Face 等）
- [ ] 雲端原生技術（Service Mesh, Istio, Linkerd）
- [ ] 前端新框架（Svelte, Solid.js, Qwik）

#### Planned Changes
- [ ] 統一所有 ML 相關術語的標準形式
- [ ] 調整部分職位名稱以符合業界標準

#### Planned Removals
- [ ] 移除過時的技術術語（評估中）

---

## 版本策略

### 版本號規則（語意化版本）
- **主版本**（X.0.0）: 不相容的 API 變更
- **次版本**（0.X.0）: 向後相容的功能新增
- **修訂版**（0.0.X）: 向後相容的問題修正

### 發布週期
- **修訂版**: 隨時（bug 修復）
- **次版本**: 每月（新增映射）
- **主版本**: 每季度評估

---

## 貢獻指南

### 提交變更時請：
1. 更新對應的 YAML 檔案
2. 執行驗證腳本確保無誤
3. 在本文檔記錄變更
4. 提交有意義的 commit 訊息

### Commit 訊息格式
```
feat(skills): 新增 Rust 相關映射

- 新增 rust programming → Rust
- 新增 rust development → Rust
- 新增 rustlang → Rust

原因：支援 Rust 開發者職位需求
影響：改善 Rust 相關職位的關鍵字提取
```

---

## 歷史統計

### 映射數量趨勢
| 日期 | Skills | Positions | Tools | Patterns | 總計 |
|------|--------|-----------|-------|----------|------|
| 2025-07-02 | 250 | 95 | 170 | 66 | 581 |

### 熱門變更類別
1. 新增程式語言和框架
2. 更新職位名稱標準
3. 修正拼寫錯誤
4. 新增縮寫展開規則

---

## 相關文件

- [標準化指南](STANDARDIZATION_GUIDE.md)
- [字典目錄](DICTIONARY_CATALOG.md)
- [README](../../src/data/standardization/README.md)

---

**維護者**: AI Resume Advisor 開發團隊  
**最後更新**: 2025-07-02