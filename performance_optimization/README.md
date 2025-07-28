# API 效能優化專案

## 概述

本目錄按照 API Feature 組織所有效能優化相關的測試腳本、報告和文檔。

## Feature 目錄結構

```
performance_optimization/
├── extract-jd-keywords/        # 關鍵字提取 API
├── index-calculation/          # 指標計算 API  
├── index-cal-and-gap-analysis/ # 指標計算與間隙分析 API
├── format-resume/              # 履歷格式化 API
├── tailor-resume/              # 履歷優化 API
├── courses-search/             # 課程搜尋 API
└── LLM_DYNAMIC_SWITCHING_方案.md  # 通用 LLM 切換方案
```

## 各 Feature 效能目標

| Feature | API 端點 | 目標 P95 | 當前狀態 | 優化方案 |
|---------|----------|----------|----------|----------|
| extract-jd-keywords | `/api/v1/extract-jd-keywords` | < 4 秒 | 5.8 秒 | 使用 GPT-4.1 mini |
| index-calculation | `/api/v1/index-calculation` | < 5 秒 | 待測試 | - |
| index-cal-and-gap-analysis | `/api/v1/index-cal-and-gap-analysis` | < 30 秒 | 待測試 | 考慮加入課程推薦 |
| format-resume | `/api/v1/format-resume` | < 15 秒 | 待測試 | 考慮整合 OCR |
| tailor-resume | `/api/v1/tailor-resume` | < 20 秒 | 待測試 | 使用 GPT-4.1 mini |
| courses-search | `/api/v1/courses/search` | < 2 秒 | 待測試 | 優化向量搜尋 |

## 當前進度（2025年7月）

### ✅ 已完成
- extract-jd-keywords: GPT-4.1 mini 整合完成，效能提升 44%
- LLM 動態切換機制實作完成

### 🚀 進行中
- 各 Feature 的獨立效能測試
- 快取機制優化
- 批次處理支援

### 📋 待進行
- 其他 5 個 API 的效能測試和優化
- 網路延遲優化（考慮 Japan East 部署）

## 使用說明

每個 feature 目錄包含：
- 效能測試腳本 (`.py`)
- 測試結果數據 (`.json`)
- 效能分析報告 (`.md`)
- 優化方案文檔

## 測試方法

```bash
# 進入特定 feature 目錄
cd performance_optimization/extract-jd-keywords

# 執行效能測試
python test_staging_performance.py
```

## 相關資源

- [Azure Monitor Dashboard](https://portal.azure.com/)
- [API 文檔](../docs/API_REFERENCE.md)
- [部署指南](../docs/DEPLOYMENT.md)

---
最後更新：2025-07-28