# 指標計算與間隙分析 API 效能優化

## API 端點
`/api/v1/index-cal-and-gap-analysis`

## 當前狀態
- **目標 P95**: < 30 秒
- **實測效能**: 待測試
- **LLM 模型**: GPT-4o-2 (Sweden Central)
- **優化狀態**: 尚未開始

## 功能增強計畫
- 加入課程推薦功能
- 提供更詳細的技能差距分析

## 優化計畫

### 短期目標
1. 建立基準效能測試
2. 分析複合操作的時間分配
3. 識別可平行處理的部分

### 中期目標
1. 將指標計算和差距分析平行化
2. 實作結果快取
3. 優化 LLM prompt 減少 token 使用

## 測試方法

```bash
# 待開發效能測試腳本
python test_gap_analysis_performance.py
```

## 相關文檔
- [API 規格說明](../../docs/API_REFERENCE.md#index-cal-and-gap-analysis)
- [架構設計](../../docs/features/gap_analysis.md)