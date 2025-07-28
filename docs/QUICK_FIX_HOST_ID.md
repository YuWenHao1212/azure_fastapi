# 快速修復 Host ID Collision (AZFD0004)

## 立即執行修復

### 方法 1：使用 GitHub Actions（推薦）
1. 前往 [GitHub Actions](https://github.com/YuWenHao1212/azure_fastapi/actions/workflows/fix-host-id-collision.yml)
2. 點擊 "Run workflow"
3. 選擇 "Apply fix" = "yes"
4. 點擊 "Run workflow"
5. 等待約 2 分鐘完成

### 方法 2：使用本地腳本
```bash
# 從專案根目錄執行
./scripts/fix_host_id_collision.sh
```

### 方法 3：手動執行 Azure CLI
```bash
# 設置 Production Host ID
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --settings "AzureFunctionsWebHost__hostId=ara-api-je-prod-v2"

# 設置 Staging Host ID（如果有）
az functionapp config appsettings set \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi \
  --slot staging \
  --settings "AzureFunctionsWebHost__hostId=ara-api-je-stg-v2"

# 重啟 Function App
az functionapp restart \
  --name airesumeadvisor-fastapi-japaneast \
  --resource-group airesumeadvisorfastapi
```

## 驗證修復

1. 等待 5 分鐘
2. 檢查 Azure Portal > Function App > Diagnose and solve problems
3. 確認 AZFD0004 錯誤不再出現
4. 測試 API：
   ```bash
   curl https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/health?code=YOUR_HOST_KEY
   ```

## 如果問題持續

請參考完整文檔：[HOST_ID_COLLISION_DEEP_INVESTIGATION.md](./HOST_ID_COLLISION_DEEP_INVESTIGATION.md)