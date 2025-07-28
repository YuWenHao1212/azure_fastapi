# Azure Function App Japan East 部署方案

**文件版本**: 1.0.0  
**建立日期**: 2025-07-28  
**目標**: 將 Function App 遷移至 Japan East 以優化網路延遲

## 1. 執行摘要

### 目標效益
- **網路延遲**: 從 3,100ms 降至 500-1,000ms（改善 67-84%）
- **總回應時間**: 從 5,800ms 降至 3,000-3,500ms（改善 40-48%）
- **使用者體驗**: 顯著提升 API 回應速度

### 部署策略
採用**藍綠部署**策略，確保零停機時間：
1. 在 Japan East 建立新環境（綠）
2. 完整測試新環境
3. 逐步切換流量
4. 確認穩定後關閉舊環境（藍）

## 2. 前置準備

### 2.1 資源檢查
```bash
# 檢查 Japan East 的資源配額
az vm list-usage --location japaneast --output table

# 檢查可用的 App Service Plan SKU
az appservice list-skus --location japaneast
```

### 2.2 成本評估
| 資源 | East Asia (目前) | Japan East (新) | 差異 |
|------|-----------------|----------------|------|
| Function App (Premium) | ~$180/月 | ~$180/月 | 無差異 |
| Storage Account | ~$20/月 | ~$20/月 | 無差異 |
| Application Insights | ~$5/月 | ~$5/月 | 無差異 |
| **總計** | ~$205/月 | ~$205/月 | 無顯著差異 |

### 2.3 相依性檢查
- [x] GPT-4.1 mini 已在 Japan East
- [ ] PostgreSQL 資料庫位置（如需要，考慮 Read Replica）
- [ ] 其他外部服務連接性

## 3. 部署步驟

### Phase 1: 建立新資源 (Day 1)

#### 3.1 創建資源群組（選擇性）
```bash
# 選項 1: 使用新的資源群組
az group create \
  --name airesumeadvisorfastapi-japaneast \
  --location japaneast

# 選項 2: 使用現有資源群組
RESOURCE_GROUP="airesumeadvisorfastapi"
```

#### 3.2 創建 Storage Account
```bash
# 創建儲存帳戶（Function App 需要）
az storage account create \
  --name airesumeadvisorjpeast \
  --resource-group $RESOURCE_GROUP \
  --location japaneast \
  --sku Standard_LRS \
  --kind StorageV2
```

#### 3.3 創建 Application Insights
```bash
# 創建 Application Insights
az monitor app-insights component create \
  --app airesumeadvisorfastapi-japaneast \
  --location japaneast \
  --resource-group $RESOURCE_GROUP \
  --application-type web
```

#### 3.4 創建 Premium Plan
```bash
# 創建 Premium Plan (EP1)
az functionapp plan create \
  --name airesumeadvisor-plan-japaneast \
  --resource-group $RESOURCE_GROUP \
  --location japaneast \
  --sku EP1 \
  --is-linux
```

#### 3.5 創建 Function App
```bash
# 創建 Function App
az functionapp create \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --plan airesumeadvisor-plan-japaneast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --storage-account airesumeadvisorjpeast
```

### Phase 2: 配置設定 (Day 1-2)

#### 3.6 複製應用程式設定
```bash
# 匯出現有設定
az functionapp config appsettings list \
  --name airesumeadvisor-fastapi-premium \
  --resource-group $RESOURCE_GROUP \
  --slot staging \
  > app_settings_staging.json

# 應用到新 Function App
# 注意：需要手動編輯 JSON 移除 location 相關設定
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --settings @app_settings_staging.json
```

#### 3.7 設定重要環境變數
```bash
# 設定 Application Insights
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app airesumeadvisorfastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSIGHTS_KEY"

# 設定 GPT-4.1 mini (已在 Japan East)
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --settings \
    GPT41_MINI_JAPANEAST_ENDPOINT="https://airesumeadvisor.openai.azure.com/" \
    GPT41_MINI_JAPANEAST_API_KEY="<YOUR_API_KEY>" \
    GPT41_MINI_JAPANEAST_DEPLOYMENT="gpt-4-1-mini-japaneast" \
    LLM_MODEL_KEYWORDS="gpt41-mini"
```

### Phase 3: 部署程式碼 (Day 2)

#### 3.8 設定部署來源
```bash
# 選項 1: 從 GitHub 部署
az functionapp deployment source config \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --repo-url https://github.com/YuWenHao1212/azure_fastapi \
  --branch main \
  --manual-integration

# 選項 2: 使用 ZIP 部署
# 先在本地打包
cd /Users/yuwenhao/Documents/GitHub/azure_fastapi
zip -r deploy.zip . -x "*.git*" -x "*.venv*" -x "*__pycache__*"

# 部署
az functionapp deployment source config-zip \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --src deploy.zip
```

### Phase 4: 測試驗證 (Day 2-3)

#### 3.9 功能測試
```bash
# 取得新的 Function Key
NEW_FUNCTION_KEY=$(az functionapp keys list \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group $RESOURCE_GROUP \
  --query functionKeys.default -o tsv)

# 測試健康檢查
curl -X GET "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/health?code=$NEW_FUNCTION_KEY"

# 測試關鍵字提取
curl -X POST "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/extract-jd-keywords?code=$NEW_FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We need a Python developer with FastAPI experience",
    "language": "en",
    "max_keywords": 10
  }'
```

#### 3.10 效能測試
創建測試腳本 `test_japaneast_performance.py`：
```python
import httpx
import time
import statistics

JAPANEAST_URL = "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net"
FUNCTION_KEY = "YOUR_NEW_FUNCTION_KEY"

def test_performance():
    times = []
    for i in range(10):
        start = time.time()
        response = httpx.post(
            f"{JAPANEAST_URL}/api/v1/extract-jd-keywords?code={FUNCTION_KEY}",
            json={
                "job_description": "Python developer needed with cloud experience",
                "language": "en"
            }
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"Test {i+1}: {elapsed:.0f}ms")
    
    print(f"\n平均回應時間: {statistics.mean(times):.0f}ms")
    print(f"中位數: {statistics.median(times):.0f}ms")

if __name__ == "__main__":
    test_performance()
```

### Phase 5: 流量切換 (Day 3-4)

#### 3.11 使用 Azure Traffic Manager（建議）
```bash
# 創建 Traffic Manager Profile
az network traffic-manager profile create \
  --name airesumeadvisor-tm \
  --resource-group $RESOURCE_GROUP \
  --routing-method Priority \
  --unique-dns-name airesumeadvisor-api

# 添加端點
# Japan East (優先級 1)
az network traffic-manager endpoint create \
  --name japaneast-endpoint \
  --profile-name airesumeadvisor-tm \
  --resource-group $RESOURCE_GROUP \
  --type azureEndpoints \
  --target-resource-id $(az functionapp show --name airesumeadvisor-fastapi-japaneast --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --priority 1

# East Asia (優先級 2 - 備援)
az network traffic-manager endpoint create \
  --name eastasia-endpoint \
  --profile-name airesumeadvisor-tm \
  --resource-group $RESOURCE_GROUP \
  --type azureEndpoints \
  --target-resource-id $(az functionapp show --name airesumeadvisor-fastapi-premium --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --priority 2
```

#### 3.12 DNS 更新（如果使用自訂網域）
```bash
# 更新 DNS CNAME 記錄指向 Traffic Manager
# 或直接指向新的 Function App
```

### Phase 6: 監控與優化 (Day 4-7)

#### 3.13 設定監控告警
```bash
# CPU 使用率告警
az monitor metrics alert create \
  --name high-cpu-japaneast \
  --resource-group $RESOURCE_GROUP \
  --scopes $(az functionapp show --name airesumeadvisor-fastapi-japaneast --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --condition "avg CpuPercentage > 80" \
  --window-size 5m \
  --evaluation-frequency 1m

# 回應時間告警
az monitor metrics alert create \
  --name slow-response-japaneast \
  --resource-group $RESOURCE_GROUP \
  --scopes $(az functionapp show --name airesumeadvisor-fastapi-japaneast --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --condition "avg ResponseTime > 3000" \
  --window-size 5m \
  --evaluation-frequency 1m
```

#### 3.14 效能調優
- 啟用 Always On（Premium Plan 已包含）
- 調整 Scale Out 規則
- 優化應用程式設定

## 4. 回滾計畫

如果新環境出現問題：

### 立即回滾（使用 Traffic Manager）
```bash
# 停用 Japan East 端點
az network traffic-manager endpoint update \
  --name japaneast-endpoint \
  --profile-name airesumeadvisor-tm \
  --resource-group $RESOURCE_GROUP \
  --endpoint-status Disabled
```

### 完整回滾
1. 更新 DNS 指回原始 Function App
2. 通知用戶更新 API 端點
3. 保留 Japan East 資源 7 天後刪除

## 5. 檢查清單

### 部署前
- [ ] 備份現有配置
- [ ] 記錄當前效能基準
- [ ] 準備測試案例
- [ ] 通知相關團隊

### 部署中
- [ ] 資源創建成功
- [ ] 設定正確複製
- [ ] 程式碼部署成功
- [ ] 基本功能測試通過
- [ ] 效能測試達標

### 部署後
- [ ] 監控設定完成
- [ ] 文檔更新
- [ ] 團隊培訓
- [ ] 效能持續監控

## 6. 預期成果

### 效能提升
| 指標 | East Asia | Japan East | 改善 |
|-----|-----------|------------|------|
| 網路延遲 | 3,100ms | 800ms | -74% |
| API 處理 | 2,500ms | 2,500ms | 0% |
| 總回應時間 | 5,800ms | 3,300ms | -43% |

### 成本影響
- 月度成本維持不變（~$205）
- 可能有一次性遷移成本（~$50）
- 長期節省因效能提升帶來的間接成本

## 7. 風險與緩解

| 風險 | 可能性 | 影響 | 緩解措施 |
|-----|--------|------|---------|
| 部署失敗 | 低 | 高 | 完整測試、分階段部署 |
| 效能未達預期 | 低 | 中 | 保留回滾選項 |
| 服務中斷 | 低 | 高 | 使用 Traffic Manager |
| 成本超支 | 低 | 低 | 預先成本評估 |

## 8. 後續優化

完成遷移後的進一步優化：
1. 實施多區域部署（Front Door）
2. 資料庫讀取複本在 Japan East
3. CDN 整合
4. 自動擴展優化

---

**下一步行動**：
1. 確認資源配額和預算
2. 選擇部署時間窗口
3. 開始執行 Phase 1

**預計時程**：4-7 天完成完整遷移