# 立即優化方案：解決 Premium Plan Function App 的 2.3 秒開銷

## 問題總結
- Premium Plan EP1 上仍有 2.3-2.4 秒的固定開銷
- 並發請求性能災難性（10+ 秒）
- ASGI 適配層是主要瓶頸

## 方案 A：優化現有 Function App（1-2 天）

### 1. 簡化 ASGI 適配層
```python
# 直接處理，跳過 ASGI
@app_func.function_name(name="HttpTrigger1")
@app_func.route(route="{*route}")
async def main(req: func.HttpRequest) -> func.HttpResponse:
    # 直接調用 FastAPI 路由，而非 ASGI
    # 減少一層轉換
```

### 2. 實施激進緩存
- 對 OpenAPI.json 實施內存緩存
- 對相同 JD 的結果緩存（已有 Redis，需要優化）
- 預期改善：重複請求 < 100ms

### 3. 關閉不必要的中間件
- 移除 GZip 中間件（Azure 已處理）
- 簡化 CORS（如果前端固定）
- 減少日誌級別

## 方案 B：遷移到 Container Apps（推薦，3-5 天）

### 優勢
- 原生 FastAPI 運行，無需 ASGI 適配
- 預期延遲：< 500ms
- 更好的並發處理
- 成本相近

### 實施步驟
1. 創建 Dockerfile
2. 部署到 Azure Container Apps
3. 配置自動縮放
4. 遷移域名

### 預期效果
- 響應時間：6 秒 → 2.5-3 秒
- 並發性能：10 倍提升
- 更簡單的架構

## 方案 C：混合方案（立即 + 長期）

### 第一階段（本週）
1. 優化 function_app.py
   - 移除不必要的異步操作
   - 簡化請求處理流程
   
2. 實施批處理端點
   ```python
   @app.post("/api/v1/batch/extract-jd-keywords")
   async def batch_extract(jobs: List[JobDescription]):
       # 批處理攤薄開銷
   ```

3. 增加快取層
   - 使用 Azure Cache for Redis
   - 實施 30 分鐘 TTL

### 第二階段（下週）
4. 評估 Container Apps POC
5. 性能測試對比
6. 制定遷移計劃

## 性能目標

| 指標 | 當前 | 目標 | 方案 |
|------|------|------|------|
| 簡單請求延遲 | 2.3s | < 0.5s | 緩存 + 優化 |
| Keywords API | 5.3s | < 3s | 批處理 + 緩存 |
| 並發處理 | 10.9s | < 4s | Container Apps |
| 成本 | $200/月 | $150-200/月 | 維持 |

## 建議

**短期**：實施方案 A 的優化，特別是緩存
**中期**：認真考慮 Container Apps
**長期**：評估是否需要 Function App 架構

Premium Plan 不是萬能藥，架構選擇更重要！