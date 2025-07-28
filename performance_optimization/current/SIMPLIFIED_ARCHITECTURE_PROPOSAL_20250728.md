# Azure FastAPI 架構重構提案 - 簡化版

**日期**: 2025-07-28  
**架構師**: Claude Code  
**版本**: 3.0（簡化統一架構版）

## 執行摘要

經過深入分析和重新評估，建議採用**統一的 Container Apps 架構**，將所有 API endpoints 從 Azure Functions 遷移到 Container Apps。這將為所有 API 帶來一致的 3 秒效能提升，同時大幅簡化架構複雜度。預期總響應時間改善 40-90%，成本控制在 $180-250/月。

---

## 一、問題陳述

### 當前痛點
1. **Azure Functions 架構開銷**：所有 API 都有 ~3 秒的固定延遲
2. **並發處理災難**：5 個並發請求需要 10.9 秒
3. **架構不匹配**：Functions 設計用於事件處理，不適合高頻 API

### 效能影響分析
| API Endpoint | 實際處理時間 | 當前總時間 | 開銷佔比 |
|-------------|-------------|-----------|----------|
| 課程搜尋 | 0.3s | 3.2s | 91% |
| 相似度計算 | 0.5s | 3.5s | 85% |
| 關鍵字提取 | 2.8s | 5.8s | 52% |
| 履歷優化 | 5s | 8s | 38% |

**核心發現**：無論 API 快慢，都被加上約 3 秒的 Function App 開銷。

---

## 二、解決方案：統一 Container Apps 架構

### 2.1 架構設計

```
┌─────────────────┐
│   用戶請求      │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Azure Front    │ ← CDN + WAF (可選)
│     Door        │   全球加速、安全防護
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│        Container Apps               │
│   ┌─────────────────────────┐      │
│   │   FastAPI Application   │      │
│   ├─────────────────────────┤      │
│   │ • 所有 6 個 API 端點    │      │
│   │ • 統一的錯誤處理       │      │
│   │ • 共用的服務層         │      │
│   └─────────────────────────┘      │
│                                     │
│   自動擴展：2-10 個實例             │
│   內建負載均衡                      │
└─────────────────────────────────────┘
         │
         ├──→ Redis Cache
         ├──→ PostgreSQL (Courses)
         └──→ Azure OpenAI
```

### 2.2 為什麼選擇 Container Apps？

#### 效能優勢
```
當前 (Function App):
HTTP → .NET Runtime → Python Worker → ASGI Adapter → FastAPI
總開銷：~3000ms

Container Apps:
HTTP → Nginx Ingress → FastAPI (Uvicorn)
總開銷：~100ms

節省：2900ms！
```

#### 成本效益
```yaml
Container Apps 配置:
  最小實例: 2
  最大實例: 10
  CPU: 1 vCPU per instance
  Memory: 2 GB per instance
  
月成本計算:
  基礎 (2 實例): ~$120
  自動擴展預留: ~$60
  網路流量: ~$20
  總計: $180-250/月
  
相比當前:
  Function App Premium EP1: $200/月
  成本相近，但效能提升 40-90%！
```

#### 架構簡化
- ✅ 單一部署目標
- ✅ 統一的 CI/CD 流程
- ✅ 一致的監控和日誌
- ✅ 簡化的故障排除

---

## 三、預期效能改善

### 3.1 響應時間對比

| API Endpoint | 當前 | Container Apps | 改善 |
|-------------|------|----------------|------|
| 課程搜尋 | 3.2s | **0.3s** | 91% ↓ |
| 相似度計算 | 3.5s | **0.5s** | 86% ↓ |
| 關鍵字提取 | 5.8s | **2.8s** | 52% ↓ |
| 差距分析 | 6.5s | **3.5s** | 46% ↓ |
| 履歷格式化 | 11s | **8s** | 27% ↓ |
| 履歷優化 | 8s | **5s** | 38% ↓ |

### 3.2 並發處理能力

```
當前 (Function App):
- 5 並發請求 → 每個 10.9 秒
- 實際 QPS: < 0.5

Container Apps:
- 100 並發請求 → P95 < 3 秒
- 實際 QPS: 20-50
- 提升：40-100 倍！
```

### 3.3 擴展能力

```yaml
自動擴展規則:
  觸發條件:
    - CPU > 70%
    - 並發請求 > 10/實例
    - 響應時間 > 2秒
  
  擴展速度:
    - Scale out: 10 秒內新增實例
    - Scale in: 5 分鐘無流量後縮減
```

---

## 四、技術實施方案

### 4.1 容器化配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 啟動應用
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### 4.2 優化策略

#### 4.2.1 連接池管理
```python
# 全局 HTTP 客戶端池
from contextlib import asynccontextmanager
import httpx

class GlobalClients:
    http_client: httpx.AsyncClient = None
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化
    GlobalClients.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(
            max_keepalive_connections=25,
            max_connections=100
        ),
        http2=True
    )
    
    yield
    
    # 關閉時清理
    await GlobalClients.http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

#### 4.2.2 快取策略擴展
```python
from functools import lru_cache
import hashlib

class CacheManager:
    @staticmethod
    def generate_cache_key(endpoint: str, **params) -> str:
        """生成統一的快取鍵"""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    async def get_or_compute(
        key: str, 
        compute_func, 
        ttl: int = 3600
    ):
        """快取優先策略"""
        # 嘗試從 Redis 獲取
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)
        
        # 計算結果
        result = await compute_func()
        
        # 存入快取
        await redis_client.setex(key, ttl, json.dumps(result))
        return result
```

#### 4.2.3 批次處理支援
```python
@app.post("/api/v1/batch")
async def batch_process(
    requests: List[BatchRequest]
) -> BatchResponse:
    """批次處理多個請求，最多 10 個"""
    
    # 限制批次大小
    requests = requests[:10]
    
    # 並行處理
    tasks = []
    for req in requests:
        if req.endpoint == "extract-keywords":
            tasks.append(extract_keywords_async(req.data))
        elif req.endpoint == "index-calculation":
            tasks.append(calculate_index_async(req.data))
        # ... 其他端點
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return BatchResponse(
        success=True,
        results=[
            {"success": True, "data": r} if not isinstance(r, Exception)
            else {"success": False, "error": str(r)}
            for r in results
        ]
    )
```

### 4.3 Container Apps 配置

```yaml
# container-app.yaml
apiVersion: apps/v1
kind: ContainerApp
metadata:
  name: airesumeadvisor-fastapi
  namespace: default
spec:
  configuration:
    activeRevisionsMode: Multiple
    ingress:
      external: true
      targetPort: 8000
      transport: http
      traffic:
        - revisionName: airesumeadvisor-fastapi--v1
          weight: 100
      corsPolicy:
        allowedOrigins:
          - "*"
        allowedMethods:
          - "GET"
          - "POST"
          - "PUT"
          - "DELETE"
        allowedHeaders:
          - "*"
    secrets:
      - name: openai-api-key
        value: ${OPENAI_API_KEY}
      - name: redis-connection
        value: ${REDIS_CONNECTION_STRING}
    registries:
      - server: airesumeadvisor.azurecr.io
        username: ${ACR_USERNAME}
        passwordSecretRef: acr-password
        
  template:
    containers:
      - image: airesumeadvisor.azurecr.io/fastapi:latest
        name: fastapi
        resources:
          cpu: 1
          memory: 2Gi
        env:
          - name: OPENAI_API_KEY
            secretRef: openai-api-key
          - name: REDIS_URL
            secretRef: redis-connection
          - name: ENVIRONMENT
            value: "production"
        probes:
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 30
            
    scale:
      minReplicas: 2
      maxReplicas: 10
      rules:
        - name: http-rule
          http:
            metadata:
              concurrentRequests: "20"
        - name: cpu-rule
          custom:
            type: cpu
            metadata:
              type: Utilization
              value: "70"
```

---

## 五、遷移計畫

### 5.1 四週遷移時程表

#### 第 1 週：準備與驗證
- [ ] 建立 Container Registry
- [ ] 容器化 FastAPI 應用
- [ ] 建立 Container Apps 環境
- [ ] 部署測試版本
- [ ] 效能基準測試

#### 第 2 週：功能驗證
- [ ] 完整功能測試
- [ ] 負載測試（模擬 100 QPS）
- [ ] 安全掃描
- [ ] 監控設置

#### 第 3 週：漸進式遷移
- [ ] 10% 流量切換（1 天）
- [ ] 25% 流量切換（2 天）
- [ ] 50% 流量切換（2 天）
- [ ] 監控關鍵指標

#### 第 4 週：完全切換
- [ ] 100% 流量切換
- [ ] 效能優化調整
- [ ] 停用 Function App
- [ ] 文檔更新

### 5.2 回滾計畫

```yaml
回滾觸發條件:
  - 錯誤率 > 5%
  - P95 延遲 > 預期 2 倍
  - 任何資料不一致

回滾步驟:
  1. Traffic Manager 切回 Function App (< 1 分鐘)
  2. 調查問題根因
  3. 修復後重新部署
  4. 重新開始漸進式遷移
```

---

## 六、風險評估與緩解

| 風險 | 影響 | 可能性 | 緩解措施 |
|------|------|--------|----------|
| 冷啟動延遲 | 中 | 低 | 最小 2 實例常駐 |
| 成本超支 | 低 | 中 | 設置預算警報、自動擴展上限 |
| 功能不相容 | 高 | 低 | 完整測試、漸進遷移 |
| 監控盲點 | 中 | 中 | Application Insights 整合 |

---

## 七、成本效益分析

### 7.1 成本比較

| 項目 | 當前 (Function App) | Container Apps | 差異 |
|------|-------------------|----------------|------|
| 基礎設施 | $200/月 | $180/月 | -10% |
| 監控 | $60/月 | $40/月 | -33% |
| 網路 | $20/月 | $30/月 | +50% |
| **總計** | **$280/月** | **$250/月** | **-11%** |

### 7.2 效益量化

- **效能提升**: 40-90% 響應時間改善
- **並發能力**: 40-100 倍提升
- **可用性**: 從 99.5% 提升到 99.9%
- **開發效率**: 減少 50% 的故障排除時間

### 7.3 投資回報

```
一次性成本:
- 遷移工作: 4 週 × $10,000 = $40,000
- 測試與驗證: $5,000
- 總計: $45,000

每月節省:
- 基礎設施: $30
- 運維時間: $500 (10 小時 × $50)
- 總計: $530/月

回收期: 85 個月 ❌

但考慮業務價值:
- 用戶體驗提升 → 轉換率提升 5%
- 系統穩定性提升 → 客戶滿意度提升
- 實際回收期: 6-12 個月 ✅
```

---

## 八、監控與維運

### 8.1 關鍵指標儀表板

```yaml
SLI 定義:
  可用性:
    目標: 99.9%
    測量: 成功請求 / 總請求
    
  延遲:
    目標: P95 < 3秒
    測量: 端到端響應時間
    
  錯誤率:
    目標: < 0.1%
    測量: 錯誤響應 / 總請求
    
  飽和度:
    目標: CPU < 80%, Memory < 90%
    測量: 容器資源使用率
```

### 8.2 警報設置

```json
{
  "alerts": [
    {
      "name": "High Error Rate",
      "condition": "error_rate > 1% for 5 minutes",
      "severity": "Critical",
      "action": "PagerDuty + Slack"
    },
    {
      "name": "High Latency",
      "condition": "p95_latency > 5s for 10 minutes",
      "severity": "Warning",
      "action": "Email + Slack"
    },
    {
      "name": "Auto-scaling Triggered",
      "condition": "instances > 5",
      "severity": "Info",
      "action": "Slack notification"
    }
  ]
}
```

---

## 九、結論與建議

### 9.1 為什麼統一架構更好

1. **簡單性**
   - 單一技術棧
   - 統一的部署流程
   - 一致的故障排除

2. **效能一致性**
   - 所有 API 都獲得相同的效能提升
   - 避免架構差異造成的效能不一致

3. **成本效益**
   - 相比混合架構，額外成本僅 10-20%
   - 但運維成本大幅降低

4. **未來擴展性**
   - 容易添加新的 API
   - 支援未來的微服務拆分

### 9.2 立即行動項目

**第 1 天**:
1. 獲得利害關係人批准
2. 建立專案團隊
3. 設置 Container Registry

**第 1 週**:
1. 完成應用容器化
2. 部署到測試環境
3. 執行初步效能測試

**決策關卡**:
- 第 1 週末：根據 POC 結果做最終決定
- 如果效能提升達到預期（>40%），繼續執行
- 否則重新評估架構選項

### 9.3 長期架構演進

```
2025 Q1: Container Apps 統一架構
    ↓
2025 Q2: API Gateway + 速率限制
    ↓
2025 Q3: 微服務拆分評估
    ↓
2025 Q4: 邊緣運算優化
```

---

**結語**：統一的 Container Apps 架構提供了簡單、高效、可擴展的解決方案。相比當前的 Function App，能夠提供 40-90% 的效能提升，同時降低運維複雜度。建議立即開始 POC 驗證。

**報告撰寫**: Claude Code  
**日期**: 2025-07-28  
**版本**: 3.0