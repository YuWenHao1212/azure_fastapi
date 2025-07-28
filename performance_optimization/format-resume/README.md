# 履歷格式化 API 效能優化

## API 端點
`/api/v1/format-resume`

## 當前狀態
- **目標 P95**: < 15 秒
- **實測效能**: 待測試
- **LLM 模型**: GPT-4o-2 (Sweden Central)
- **優化狀態**: 尚未開始

## 功能增強計畫
- 考慮整合內部 OCR 功能（目前使用外部 OCR API）

## 優化計畫

### 短期目標
1. 建立基準效能測試
2. 分析 OCR API 呼叫時間
3. 評估 HTML 處理效能

### 中期目標
1. 評估內建 OCR 方案
2. 優化 HTML 生成邏輯
3. 實作模板快取

## 測試方法

```bash
# 待開發效能測試腳本
python test_format_resume_performance.py
```

## 相關文檔
- [API 規格說明](../../docs/API_REFERENCE.md#format-resume)
- [架構設計](../../docs/features/resume_format.md)