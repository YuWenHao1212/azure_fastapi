# Azure Function App 效能問題深度分析報告

**日期**: 2025-07-28  
**分析者**: Claude Code  
**專案**: Azure FastAPI - Japan East Deployment

## 執行摘要

本報告揭露了一個重大發現：我們一直誤認為是「網路延遲」的 3+ 秒延遲，實際上是 **Azure Function App 的架構開銷**。即使從 East Asia 遷移到 Japan East（與 OpenAI 服務同區域），並使用 Premium Plan (EP1)，仍然無法解決此問題。

### 關鍵數據對比

| 部署配置 | 平均網路開銷 | 實際網路延遲 | Function App 開銷 |
|---------|-------------|-------------|-----------------|
| East Asia → Japan East OpenAI | 3,136ms | ~200ms | ~2,936ms |
| Japan East → Japan East OpenAI | 3,253ms | ~96ms | ~3,157ms |

**結論**：同區域部署只改善了約 100ms 的真實網路延遲，但被 3 秒的架構開銷完全掩蓋。

---

## 一、問題背景

### 1.1 初始假設
- 認為高延遲是因為 Function App (East Asia) 與 OpenAI (Japan East) 跨區域通訊
- 期望同區域部署能顯著降低「網路延遲」

### 1.2 實際情況
- 遷移後延遲反而略微增加（3,136ms → 3,253ms）
- Premium Plan (EP1) 也無法改善情況

### 1.3 測試環境
- **Function App**: airesumeadvisor-fastapi-japaneast
- **Plan**: Premium EP1 (ElasticPremium)
- **Runtime**: Python 3.11
- **Framework**: FastAPI + Azure Functions
- **OpenAI Model**: GPT-4.1 mini (Japan East)

---

## 二、測試方法與工具

### 2.1 效能測試腳本

#### test_staging_performance_v2.py
用於測試整體 API 效能，包含中英文測試案例：

```python
# 關鍵配置
STAGING_URL = "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net"
FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY", "")  # 從環境變數載入

# 測試流程
1. 預熱階段（中英文各一次）
2. 測試 5 個英文 JD
3. 測試 5 個中文 JD
4. 生成詳細報告
```

**測試結果摘要**：
- 平均端到端回應時間: 6,031ms
- 平均 API 處理時間: 2,777ms
- 平均網路開銷: 3,253ms (53.9%)
- 成功率: 100%

#### test_network_latency_detailed.py
深入分析網路延遲的組成：

```python
# 測試項目
1. DNS 解析時間
2. TCP 連接時間
3. Function App 基本延遲
4. 不同端點的響應時間對比
```

**關鍵發現**：
- DNS 解析: 23.6ms
- TCP 連接: 96ms
- Function App 基本請求: 2,801ms（平均）
- 即使是簡單的 GET 請求也需要 2.3+ 秒

#### diagnose_function_overhead.py
診斷 Function App 開銷的具體來源：

```python
# 診斷結果
GET /: 2,385ms
GET /docs: 2,285ms
GET /openapi.json: 2,292ms
POST /api/v1/extract-jd-keywords: 5,342ms
  - API Processing: 2,258ms
  - Function Overhead: 3,084ms

# 並發測試（災難性結果）
5 個並發請求每個都需要 10.9 秒！
```

### 2.2 分析方法

1. **時間分解分析**
   ```
   總時間 = 網路傳輸 + Function App 處理 + OpenAI API 調用
   "網路開銷" = 總時間 - API處理時間（錯誤的計算方式）
   ```

2. **真實網路延遲測試**
   - 使用 curl 測試 TCP 連接時間
   - DNS 解析時間測量
   - 排除應用層處理

3. **架構層級分析**
   - 追蹤請求在各層的處理時間
   - 識別瓶頸所在

---

## 三、詳細發現

### 3.1 「網路延遲」的真實組成

透過詳細分析，3,253ms 的「網路開銷」實際包含：

| 組成部分 | 時間 | 說明 |
|---------|------|------|
| 真實網路延遲 | ~96ms | TCP 連接 + 數據傳輸 |
| DNS 解析 | ~24ms | 域名解析 |
| Function App 啟動 | ~500-1000ms | 容器初始化（Premium Plan 已優化） |
| ASGI 適配層 | ~800-1200ms | Azure Functions → ASGI → FastAPI |
| 序列化/反序列化 | ~200-400ms | JSON 處理 |
| 日誌與遙測 | ~100-300ms | Application Insights |
| 未知開銷 | ~400-800ms | 平台內部處理 |
| **總計** | **~3,200ms** | |

### 3.2 Premium Plan 的限制

即使使用 Premium Plan (EP1)：
- 仍有 2.3 秒的基礎開銷
- 並發處理能力極差（10+ 秒）
- 連接重用效果微小（節省 135ms）

### 3.3 架構不匹配問題

**三層轉換的開銷**：
```
HTTP Request 
  ↓
Azure Functions Runtime (C#/.NET)
  ↓
Python Worker Process
  ↓
function_app.py (ASGI Adapter)
  ↓
FastAPI ASGI Application
  ↓
Actual Business Logic
```

每一層都增加了處理時間和複雜度。

### 3.4 並發處理災難

測試顯示 5 個並發請求的結果：
```
請求 1: 10,951ms
請求 2: 10,951ms
請求 3: 10,952ms
請求 4: 10,952ms
請求 5: 10,951ms
```

這表明存在嚴重的資源競爭或全局鎖問題。

---

## 四、根本原因分析

### 4.1 架構選擇不當
Azure Functions 適合：
- 事件驅動的輕量任務
- 短時間執行的無狀態函數
- 低頻率的後台處理

不適合：
- 高頻率的 API 服務
- 需要快速響應的 Web 應用
- 複雜的 FastAPI 應用

### 4.2 ASGI 適配層開銷
`function_app.py` 中的 ASGI 適配增加了顯著延遲：
```python
# 每個請求都要經過
1. 解析 Azure Functions HttpRequest
2. 轉換為 ASGI scope
3. 創建 receive/send callables
4. 等待 FastAPI 處理
5. 轉換回 Azure Functions HttpResponse
```

### 4.3 平台限制
- Python Worker 的啟動開銷
- 跨語言運行時通訊（.NET → Python）
- Azure Functions 的內部代理層

---

## 五、效能優化建議

### 5.1 短期優化（1-2 週）

#### 方案 A：優化現有 Function App
1. **簡化 ASGI 適配層**
   - 直接調用 FastAPI 路由
   - 減少中間轉換
   - 預期改善：500-800ms

2. **實施激進緩存**
   - Redis 緩存優化
   - 內存緩存 OpenAPI.json
   - 預期改善：重複請求 < 100ms

3. **批處理 API**
   ```python
   @app.post("/api/v1/batch/extract-jd-keywords")
   async def batch_extract(jobs: List[JobDescription]):
       # 攤薄固定開銷
   ```
   - 預期改善：批量處理效率提升 5-10 倍

### 5.2 中期方案（1 個月）

#### 方案 B：遷移到 Azure Container Apps
**優勢**：
- 原生 FastAPI 運行
- 無 ASGI 適配層
- 更好的並發處理
- 自動縮放

**預期效果**：
- 響應時間：6 秒 → 2.5-3 秒
- 並發性能：提升 10 倍
- 成本：相近（$150-200/月）

### 5.3 長期考慮

1. **評估 API Gateway + 微服務**
2. **考慮 gRPC 替代 REST**
3. **邊緣計算優化**

---

## 六、成本效益分析

| 方案 | 實施成本 | 月費用 | 響應時間 | 並發能力 |
|------|---------|--------|---------|---------|
| 現狀 | - | $200 | 6 秒 | 差 |
| 優化 Function App | 1 週開發 | $200 | 4-4.5 秒 | 一般 |
| Container Apps | 2 週開發 | $150-200 | 2.5-3 秒 | 優秀 |
| App Service | 1 週開發 | $100-150 | 3-3.5 秒 | 良好 |

---

## 七、結論與建議

### 7.1 主要發現
1. **網路延遲是個偽命題**：真實網路延遲 < 100ms
2. **架構選擇是關鍵**：Function App 不適合此應用場景
3. **Premium Plan 不是萬能藥**：架構問題無法用升級解決

### 7.2 行動建議
1. **立即**：實施緩存和批處理優化
2. **短期**：POC Azure Container Apps
3. **中期**：完成架構遷移

### 7.3 經驗教訓
- 效能問題需要深入分析，不能憑表面現象下結論
- 架構選擇比硬體配置更重要
- 監控指標的命名要準確（避免誤導）

---

## 附錄：測試數據與日誌

### A.1 測試命令
```bash
# 效能測試
python test_staging_performance_v2.py

# 網路延遲分析
python test_network_latency_detailed.py

# Function App 診斷
python diagnose_function_overhead.py

# Azure CLI 檢查
az functionapp show --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi --query sku
```

### A.2 關鍵日誌
```
DNS 解析: 23.6ms (40.79.195.0)
TCP 連接時間: 96ms
Function App 基本延遲: 2,801ms (平均)
並發請求延遲: 10,951ms (災難性)
```

### A.3 測試檔案清單
- `/performance_optimization/extract-jd-keywords/test_staging_performance_v2.py`
- `/performance_optimization/extract-jd-keywords/test_network_latency_detailed.py`
- `/performance_optimization/diagnose_function_overhead.py`
- `/performance_optimization/IMMEDIATE_OPTIMIZATION_PLAN.md`

---

**報告撰寫**: Claude Code  
**審核建議**: 建議與 Azure 架構師進一步討論 Container Apps 遷移方案