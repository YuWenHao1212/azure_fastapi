# 履歷優化 API 效能優化

## API 端點
`/api/v1/tailor-resume`

## 當前狀態
- **目標 P95**: < 20 秒
- **實測效能**: 待測試
- **LLM 模型**: GPT-4.1 mini (計畫中)
- **優化狀態**: 尚未開始

## 已知問題
- Rich Editor 在前端機率性不顯示（可能是前端問題）

## 優化計畫

### 短期目標
1. 建立基準效能測試
2. 切換到 GPT-4.1 mini 測試品質
3. 分析 HTML 處理瓶頸

### 中期目標
1. 優化 prompt 減少 token 使用
2. 實作分段處理（長履歷）
3. 加入智慧快取機制

## 測試方法

```bash
# 待開發效能測試腳本
python test_tailor_resume_performance.py
```

## 相關文檔
- [API 規格說明](../../docs/API_REFERENCE.md#tailor-resume)
- [架構設計](../../docs/features/resume_tailoring.md)