# AI Resume Advisor API

基於 FastAPI 的履歷優化服務，整合 Azure Functions 部署。

## 快速開始

```bash
# 安裝相依套件
pip install -r requirements.txt

# 本地執行
uvicorn src.main:app --reload

# 執行測試
./run_precommit_tests.sh --level-2 --parallel
```

## API 端點

| Endpoint | Method | 說明 | 文檔 |
|----------|--------|------|------|
| `/api/v1/extract-jd-keywords` | POST | 從職缺描述提取關鍵字 | [詳細說明](features/keyword_extraction.md) |
| `/api/v1/calculate-resume-jd-index` | POST | 計算履歷與職缺的匹配指數 | [詳細說明](features/index_calculation.md) |
| `/api/v1/analyze-resume-gaps` | POST | 分析履歷與職缺的差距 | [詳細說明](features/gap_analysis.md) |
| `/api/v1/format-resume` | POST | 格式化履歷並標記關鍵字 | [詳細說明](features/resume_format.md) |
| `/api/v1/tailor-resume` | POST | 生成客製化履歷內容 | [詳細說明](features/resume_tailoring.md) |
| `/api/v1/search-relevant-courses` | POST | 搜尋相關 Coursera 課程 | [詳細說明](features/course_search.md) |

## 核心特色

- **語言支援**：英文與繁體中文
- **LLM 整合**：Azure OpenAI GPT-4o
- **部署方式**：Azure Functions 搭配 CI/CD
- **效能優化**：優化回應時間
- **前端整合**：Bubble.io 整合就緒

## 架構

採用 FHS (Functional Hierarchy Structure) 架構 - 詳見 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 測試

```bash
# Level 0: 僅驗證 Prompt 檔案
./run_precommit_tests.sh --level-0

# Level 1: 程式碼風格檢查
./run_precommit_tests.sh --level-1

# Level 2: 風格 + 單元測試（預設）
./run_precommit_tests.sh --level-2 --parallel

# Level 3: 完整測試套件
./run_precommit_tests.sh --level-3 --parallel
```

## 文檔

- [架構設計](ARCHITECTURE.md)
- [API 參考](API_REFERENCE.md)
- [部署指南](DEPLOYMENT.md)
- [功能文檔](features/)

## 效能目標

### API 回應時間 (p95)
- 關鍵字提取：< 2.5s
- 匹配指數計算：< 3s
- 差距分析：< 3s
- 履歷格式化：< 1.5s
- 履歷客製化：< 5s
- 課程搜尋：< 2s

### 系統容量
- 並發使用者：50+
- 每月成本：< $500 USD

## 開發指南

參見 [CLAUDE.md](/CLAUDE.md) 了解開發規範。