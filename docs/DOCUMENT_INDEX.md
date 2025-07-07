# Azure FastAPI 文檔索引

## ✅ 文檔狀態更新
已從代碼重建核心文檔，現在所有重要文檔都已就位。

## 應該存在的核心文檔

### 📋 需求文檔 (Requirements)
- [x] REQUIREMENTS_KEYWORD_EXTRACTION.md - 關鍵字提取需求
- [ ] REQ_BILINGUAL_KEYWORD - 雙語關鍵字需求
- [ ] REQ_LANGUAGE_DETECTION - 語言檢測需求

### 🏗️ 架構設計 (Architecture & Design)
- [x] ARCHITECTURE_FHS.md - FHS 架構設計
- [ ] DESIGN_KEYWORD_EXTRACTION - 關鍵字提取設計
- [x] DESIGN_LANGUAGE_DETECTION - 語言檢測設計（在 legacy/temp_docs）
- [ ] DESIGN_UNIFIED_PROMPT_SERVICE - 統一提示服務設計

### 📚 API 規格 (API Specifications)
- [x] API_SPECIFICATION_V3.md - 最新 API 規格
- [ ] API_QUICK_REFERENCE - API 快速參考
- [ ] API_CHANGELOG - API 變更日誌

### 📖 實施文檔 (Implementation)
- [ ] IMPLEMENTATION_BILINGUAL_SYSTEM - 雙語系統實施
- [ ] IMPL_SIMPLIFIED_LANGUAGE_DETECTOR - 語言檢測器實施

### 🔧 部署文檔 (Deployment)
- [ ] AZURE_ENVIRONMENT_SETUP - Azure 環境設置
- [ ] AZURE_FUNCTIONS_CONFIG - Azure Functions 配置
- [ ] DEPLOYMENT_TROUBLESHOOTING - 部署故障排除

### 📊 監控文檔 (Monitoring)
- [x] MONITORING_SETUP.md - 監控設置（存在）
- [ ] MONITORING_IMPLEMENTATION_FINAL - 監控實施最終文檔
- [ ] monitoring-architecture - 監控架構

## 現有文檔位置
```
docs/
├── local/
│   └── TEST_GUIDE.md
├── published/
│   ├── MONITORING_SETUP.md
│   ├── API_SPECIFICATION_V3.md      ✅ NEW
│   ├── ARCHITECTURE_FHS.md          ✅ NEW
│   └── REQUIREMENTS_KEYWORD_EXTRACTION.md  ✅ NEW
└── DOCUMENT_INDEX.md

legacy/docs/
└── temp_docs/
    └── DESIGN_LANGUAGE_DETECTION_20250107.md
```

## 建議行動
1. 從 CLAUDE.md 和代碼註釋中重建缺失的文檔
2. 檢查是否有本地未提交的文檔
3. 建立文檔管理流程確保重要文檔不會丟失