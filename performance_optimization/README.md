# Performance Optimization 專案文件

本目錄包含 Azure FastAPI 專案的效能優化分析和架構提案。

## 📁 目錄結構

```
performance_optimization/
├── current/                          # 當前有效的文件
│   ├── PERFORMANCE_ANALYSIS_REPORT_20250728.md
│   ├── SIMPLIFIED_ARCHITECTURE_PROPOSAL_20250728.md
│   └── README.md
│
├── archive/                          # 歷史文件歸檔
│   ├── architecture_analysis/        # 架構分析演進
│   ├── initial_analysis/            # 初期分析文件
│   └── README.md
│
├── extract-jd-keywords/             # 關鍵字提取 API 測試
│   ├── test_staging_performance_v2.py
│   ├── test_network_latency_detailed.py
│   ├── diagnose_function_overhead.py
│   └── [測試結果檔案]
│
└── [其他 API 測試目錄]
```

## 🎯 專案成果

### 問題發現
- Azure Function App 造成 3+ 秒固定開銷
- 影響所有 API endpoints
- Premium Plan (EP1) 也無法解決

### 解決方案
- 統一遷移到 Azure Container Apps
- 預期效能提升 40-90%
- 成本降低 11%

## 📊 關鍵數據

| 指標 | 當前 | 目標 | 改善 |
|------|------|------|------|
| 響應時間 (P95) | 3-11 秒 | 0.3-8 秒 | 40-91% |
| 並發能力 | < 0.5 QPS | 20-50 QPS | 40-100x |
| 月成本 | $280 | $250 | -11% |

## 🚀 快速開始

1. **查看當前提案**：
   ```
   current/SIMPLIFIED_ARCHITECTURE_PROPOSAL_20250728.md
   ```

2. **了解問題分析**：
   ```
   current/PERFORMANCE_ANALYSIS_REPORT_20250728.md
   ```

3. **執行測試工具**：
   ```bash
   cd extract-jd-keywords
   python test_staging_performance_v2.py
   ```

## 📅 時間軸

- 2025-07-28：完成效能分析，發現根本問題
- 2025-07-28：提出並簡化架構方案
- 下一步：開始 Container Apps POC

## 👥 聯絡人

- 架構分析：Claude Code
- 專案負責人：WenHao