# Azure FastAPI 架構分析與重構建議

**日期**: 2025-07-28  
**架構師**: Claude Code (SW Architecture Agent)  
**專案**: Azure FastAPI Performance Optimization

## 執行摘要

基於效能分析報告顯示的 3+ 秒架構開銷問題，本報告提供現有架構的深度分析及三個可行的新架構方案。推薦採用 **Azure Container Apps** 方案，預期可將響應時間從 5.8 秒降至 3 秒以內，同時提升並發處理能力 10 倍。

---

## 一、現有架構深度分析

### 1.1 架構層級與延遲分析

```
┌─────────────────┐
│   用戶請求      │ 
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│ Azure Functions │ ← 固定開銷: ~500ms
│  (Premium EP1)  │   平台路由與初始化
└────────┬────────┘
         │ 
         ▼
┌─────────────────┐
│ .NET Runtime    │ ← 跨語言通訊: ~300ms
│ → Python Worker │   序列化/反序列化
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ function_app.py │ ← ASGI 適配: ~800ms
│ (ASGI Adapter)  │   請求轉換開銷
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │ ← 應用處理: ~200ms
│   Application   │   路由與驗證
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Azure OpenAI    │ ← API 調用: ~2800ms
│  GPT-4.1 mini   │   實際 AI 處理
└─────────────────┘

總延遲 = 500 + 300 + 800 + 200 + 2800 = 4600ms
加上網路往返與其他開銷 ≈ 5800ms
```

### 1.2 關鍵問題識別

#### 問題 1：架構不匹配
- **根因**：Azure Functions 設計用於短期事件處理，不適合常駐 API 服務
- **影響**：每個請求都有 1.6 秒的固定開銷
- **嚴重性**：高

#### 問題 2：多層轉換開銷
- **根因**：HTTP → .NET → Python → ASGI → FastAPI 的複雜轉換鏈
- **影響**：增加 800-1200ms 延遲
- **嚴重性**：高

#### 問題 3：並發處理瓶頸
- **根因**：Python GIL + Function App 實例限制
- **影響**：5 個並發請求需要 10.9 秒
- **嚴重性**：極高

#### 問題 4：成本效益不佳
- **根因**：Premium Plan 月費 $200 但未解決架構問題
- **影響**：高成本低效能
- **嚴重性**：中

### 1.3 現有架構優勢（需保留）
1. **Serverless 自動縮放**（但執行不佳）
2. **整合 Application Insights 監控**
3. **現有 CI/CD 流程**
4. **Function Key 安全機制**

---

## 二、新架構方案對比

### 方案 A：Azure Container Apps（推薦）⭐

#### 架構設計
```
┌─────────────────┐
│   用戶請求      │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Azure Front    │ ← 智能路由: ~20ms
│     Door        │   全球加速
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Container Apps  │ ← 容器啟動: ~100ms
│   Ingress       │   內建負載均衡
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FastAPI Native  │ ← 直接處理: ~50ms
│  (Uvicorn)      │   無轉換開銷
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Redis Cache   │ ← 快取命中: ~10ms
│  (if cached)    │   
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Azure OpenAI    │ ← API 調用: ~2800ms
└─────────────────┘

預期總延遲 = 20 + 100 + 50 + 2800 = 2970ms
```

#### 優勢
- ✅ 原生 FastAPI 運行，無 ASGI 開銷
- ✅ 自動縮放（2-10 實例）
- ✅ 內建健康檢查與負載均衡
- ✅ 支援藍綠部署
- ✅ 成本按使用量計費

#### 劣勢
- ❌ 需要容器化知識
- ❌ 冷啟動仍存在（但較輕）
- ❌ 監控需要額外配置

#### 成本估算
```
基礎費用：$0（無閒置成本）
vCPU：$0.000024/秒 × 2 vCPU × 86400 秒/天 × 使用率 20% = $8.29/天
記憶體：$0.000003/GiB/秒 × 4 GiB × 86400 秒/天 × 使用率 20% = $2.07/天
月費用：約 $310（但可透過預留實例降至 $150-200）
```

### 方案 B：Azure App Service

#### 架構設計
```
┌─────────────────┐
│   用戶請求      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  App Service    │ ← 平台開銷: ~200ms
│   (Linux B2)    │   
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FastAPI + Gunicorn │ ← 應用處理: ~100ms
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Azure OpenAI    │ ← API 調用: ~2800ms
└─────────────────┘

預期總延遲 = 200 + 100 + 2800 = 3100ms
```

#### 優勢
- ✅ 簡單部署，低學習曲線
- ✅ 成熟穩定
- ✅ 內建 SSL 與自定義域名
- ✅ 成本較低

#### 劣勢
- ❌ 縮放能力有限
- ❌ 並發處理受限於實例大小
- ❌ 較少的部署彈性

#### 成本估算
```
B2 實例（2 vCPU, 3.5 GB RAM）：$100/月
預留實例折扣：-30%
實際月費：約 $70-100
```

### 方案 C：Azure Kubernetes Service (AKS)

#### 架構設計
```
┌─────────────────┐
│   用戶請求      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AKS Ingress     │ ← NGINX: ~30ms
│  Controller     │   
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ FastAPI Pods    │ ← Pod 處理: ~50ms
│ (Auto-scaling)  │   HPA 自動縮放
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Service Mesh    │ ← 可選：~20ms
│   (Istio)       │   進階流量管理
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Azure OpenAI    │ ← API 調用: ~2800ms
└─────────────────┘

預期總延遲 = 30 + 50 + 20 + 2800 = 2900ms
```

#### 優勢
- ✅ 最大彈性與控制
- ✅ 優秀的並發處理
- ✅ 完整的可觀測性
- ✅ 支援複雜的部署策略

#### 劣勢
- ❌ 高複雜度
- ❌ 需要 K8s 專業知識
- ❌ 運維成本高
- ❌ 基礎設施成本高

#### 成本估算
```
控制平面：免費
節點池（2 × D2v3）：$200/月
負載均衡器：$20/月
監控與日誌：$80/月
總計：約 $300-500/月
```

---

## 三、推薦方案詳細設計（Container Apps）

### 3.1 技術架構

```yaml
# 容器配置
apiVersion: apps/v1
kind: ContainerApp
metadata:
  name: airesumeadvisor-fastapi
spec:
  configuration:
    ingress:
      external: true
      targetPort: 8000
      transport: http
      corsPolicy:
        allowedOrigins: ["*"]
    secrets:
      - name: openai-api-key
        value: ${OPENAI_API_KEY}
    registries:
      - server: airesumeadvisor.azurecr.io
        username: ${ACR_USERNAME}
        passwordSecretRef: acr-password
  template:
    containers:
      - image: airesumeadvisor.azurecr.io/fastapi:latest
        name: fastapi
        resources:
          cpu: 2
          memory: 4Gi
        env:
          - name: OPENAI_API_KEY
            secretRef: openai-api-key
          - name: REDIS_URL
            value: ${REDIS_CONNECTION_STRING}
    scale:
      minReplicas: 2
      maxReplicas: 10
      rules:
        - name: http-requests
          http:
            metadata:
              concurrentRequests: "10"
```

### 3.2 優化策略

#### 3.2.1 連接池優化
```python
# 全域 HTTP 客戶端池
import httpx
from contextlib import asynccontextmanager

_http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _http_client
    # 啟動時創建
    _http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=50
        ),
        http2=True
    )
    yield
    # 關閉時清理
    await _http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

#### 3.2.2 快取策略強化
```python
# Redis 快取裝飾器
def redis_cache(expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 嘗試從快取讀取
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 執行函數
            result = await func(*args, **kwargs)
            
            # 寫入快取
            await redis_client.setex(
                cache_key, 
                expire, 
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator
```

#### 3.2.3 批處理 API
```python
@app.post("/api/v1/batch/extract-jd-keywords")
async def batch_extract_keywords(
    request: BatchJobDescriptionRequest
) -> BatchKeywordsResponse:
    """批處理關鍵字提取，最多 10 個 JD"""
    
    # 並行處理
    tasks = [
        extract_keywords_async(jd) 
        for jd in request.job_descriptions[:10]
    ]
    
    results = await asyncio.gather(*tasks)
    
    return BatchKeywordsResponse(
        success=True,
        results=results,
        processing_time_ms=sum(r.processing_time for r in results)
    )
```

### 3.3 部署流程

#### 第一階段：環境準備（第 1 週）
1. **創建 Container Registry**
   ```bash
   az acr create --name airesumeadvisor \
     --resource-group airesumeadvisorfastapi \
     --sku Basic
   ```

2. **準備 Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # 安裝依賴
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # 複製應用
   COPY . .
   
   # 啟動
   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **建立 Container Apps 環境**
   ```bash
   az containerapp env create \
     --name airesumeadvisor-env \
     --resource-group airesumeadvisorfastapi \
     --location japaneast
   ```

#### 第二階段：平行運行（第 2 週）
1. **部署 Container App**
2. **配置流量分割**（10% → 50%）
3. **監控關鍵指標**

#### 第三階段：完全遷移（第 3 週）
1. **100% 流量切換**
2. **優化與調整**
3. **停用舊 Function App**

---

## 四、風險評估與緩解

### 4.1 技術風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|----------|
| 容器冷啟動 | 中 | 中 | 維持最小 2 實例 |
| API 相容性問題 | 低 | 高 | 完整的整合測試 |
| 監控盲點 | 中 | 中 | 配置 Application Insights |
| 安全配置錯誤 | 低 | 高 | 使用 Azure Policy |

### 4.2 業務風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|----------|
| 服務中斷 | 低 | 極高 | 藍綠部署 + 回滾計畫 |
| 效能未達預期 | 中 | 高 | POC 驗證 + 壓力測試 |
| 成本超支 | 低 | 中 | 自動縮放限制 + 預算警報 |

---

## 五、監控與維運

### 5.1 關鍵效能指標 (KPIs)

```kusto
// Application Insights 查詢
// P95 響應時間
requests
| where timestamp > ago(1h)
| summarize percentile(duration, 95) by bin(timestamp, 5m)
| render timechart

// 每秒請求數
requests
| where timestamp > ago(1h)
| summarize count() by bin(timestamp, 1s)
| render timechart

// 錯誤率
requests
| where timestamp > ago(1h)
| summarize 
    total = count(),
    failed = countif(success == false)
| extend error_rate = failed * 100.0 / total
```

### 5.2 警報配置

```json
{
  "alerts": [
    {
      "name": "High Response Time",
      "condition": "P95 > 4000ms for 5 minutes",
      "severity": "Warning",
      "action": "Scale out + investigate"
    },
    {
      "name": "High Error Rate",
      "condition": "Error rate > 5% for 3 minutes",
      "severity": "Critical",
      "action": "Rollback + page on-call"
    }
  ]
}
```

### 5.3 維運檢查清單

- [ ] 每日：檢查錯誤日誌與效能趨勢
- [ ] 每週：審查成本與資源使用率
- [ ] 每月：更新依賴與安全修補
- [ ] 每季：災難恢復演練

---

## 六、結論與下一步

### 6.1 結論
Azure Container Apps 提供了最佳的效能、成本和複雜度平衡。預期可實現：
- ✅ 響應時間降低 48%（5.8s → 3s）
- ✅ 並發能力提升 10 倍
- ✅ 成本維持在預算內（$150-250/月）
- ✅ 保持現有 API 介面不變

### 6.2 建議的行動計畫

**第 1 週**：
1. 建立 Container Apps POC 環境
2. 容器化現有 FastAPI 應用
3. 執行效能基準測試

**第 2 週**：
4. 實施連接池與快取優化
5. 配置監控與警報
6. 開始流量逐步遷移

**第 3 週**：
7. 完成 100% 流量切換
8. 效能調優
9. 文檔更新與知識轉移

**第 4 週**：
10. 停用舊環境
11. 成本優化
12. 建立長期維運流程

---

**報告撰寫**: Claude Code (SW Architecture Agent)  
**日期**: 2025-07-28  
**版本**: 1.0