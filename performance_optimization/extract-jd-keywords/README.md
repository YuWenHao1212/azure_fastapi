# 關鍵字提取 API 效能優化

## API 端點
`/api/v1/extract-jd-keywords`

## 當前狀態
- **目標 P95**: < 4 秒
- **實測效能**: 5.8 秒（含網路延遲）
- **LLM 模型**: GPT-4.1 mini (Japan East)
- **優化成果**: API 處理時間從 4.2-4.5 秒降至 2.5 秒（改善 44%）

## 測試結果摘要

### 效能指標（基於 10 次測試）
- **平均端到端回應時間**: 5,789ms
- **平均 API 處理時間**: 2,487ms  
- **平均網路開銷**: 3,136ms (54.2%)
- **成功率**: 100%

### 語言別比較
| 語言 | 平均總時間 | 平均 API 時間 | 平均關鍵字數 |
|------|-----------|--------------|-------------|
| 英文 | 5,753ms   | 2,423ms      | 16          |
| 中文 | 5,824ms   | 2,552ms      | 16          |

## 檔案清單
- `test_staging_performance.py` - Staging 環境效能測試腳本
- `test_keywords_detailed_performance_20250726.py` - 詳細效能分析
- `test_keywords_performance_20250726.py` - 關鍵字效能測試
- `GPT41_MINI_INTEGRATION_方案.md` - GPT-4.1 mini 整合技術方案

## 優化重點

### 已實施
1. ✅ 切換到 GPT-4.1 mini（成本降低 60x）
2. ✅ 部署到 Japan East 區域
3. ✅ 實作 LLM 動態切換機制

### 待實施
1. 🔄 啟用快取機制（預期 100x 加速）
2. 🔄 調整 max_keywords（16→12，預期減少 25% 處理時間）
3. 🔄 批次處理支援

## 測試方法

```bash
# 設定環境變數
export PREMIUM_STAGING_HOST_KEY="your-key"

# 執行效能測試
python test_staging_performance.py
```

## 關鍵發現
- 網路延遲是主要瓶頸（佔 54.2%）
- GPT-4.1 mini 對中英文處理效能相當（差異僅 5.3%）
- 雙語預熱可避免首次請求的異常延遲