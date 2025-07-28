# 指標計算 API 效能優化

## API 端點
`/api/v1/index-calculation`

## 當前狀態
- **目標 P95**: < 5 秒
- **實測效能**: 待測試
- **LLM 模型**: GPT-4o-2 (Sweden Central)
- **優化狀態**: 尚未開始

## 優化計畫

### 短期目標
1. 建立基準效能測試
2. 分析處理瓶頸
3. 評估是否適合使用 GPT-4.1 mini

### 中期目標
1. 實作批次處理
2. 優化相似度計算演算法
3. 加入快取機制

## 測試方法

```bash
# 待開發效能測試腳本
python test_index_calculation_performance.py
```

## 相關文檔
- [API 規格說明](../../docs/API_REFERENCE.md#index-calculation)
- [架構設計](../../docs/features/index_calculation.md)