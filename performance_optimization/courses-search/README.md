# 課程搜尋 API 效能優化

## API 端點
`/api/v1/courses/search`

## 當前狀態
- **目標 P95**: < 2 秒
- **實測效能**: 待測試
- **技術**: PostgreSQL + pgvector
- **優化狀態**: 尚未開始

## 資料庫資訊
- **Host**: airesumeadvisor-courses-db-eastasia.postgres.database.azure.com
- **向量維度**: 3072 (text-embedding-3-large)
- **索引**: 已建立多個索引

## 優化計畫

### 短期目標
1. 建立基準效能測試
2. 分析向量搜尋效能
3. 優化 SQL 查詢

### 中期目標
1. 實作搜尋結果快取
2. 優化向量索引（IVFFlat/HNSW）
3. 加入搜尋結果預載入

## 測試方法

```bash
# 待開發效能測試腳本
python test_course_search_performance.py
```

## 相關文檔
- [API 規格說明](../../docs/API_REFERENCE.md#courses-search)
- [架構設計](../../docs/features/course_search.md)
- [資料庫設計](../../docs/Phase1/published/DATABASE_DESIGN_COURSES_UPDATE_20250716.md)