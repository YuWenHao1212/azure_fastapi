# Host ID Collision Fix (AZFD0004)

## 問題描述

Azure Functions 報告錯誤：
```
AZFD0004: A collision for Host ID 'airesumeadvisor-fastapi-japaneas' was detected in the configured storage account.
```

## 根本原因

1. **Host ID 長度限制**：Azure Functions 的 Host ID 有 32 個字符的限制
2. **不必要的配置**：我們的 host.json 包含了 `durableTask` 配置，但實際上並未使用 Durable Functions
3. **Host ID 被截斷**：原始 Host ID "airesumeadvisor-fastapi-japaneast-prod" 超過了長度限制，被截斷為 "airesumeadvisor-fastapi-japaneas"

## 解決方案

移除 host.json 中不必要的 `durableTask` 配置：

```json
// 移除這段配置
"durableTask": {
  "hostId": "airesumeadvisor-fastapi-japaneast-prod"
}
```

## 驗證

1. 專案中沒有使用 Durable Functions：
   - 沒有 DurableOrchestration 或 DurableActivity 相關代碼
   - requirements.txt 中沒有 durable-functions 套件

2. 移除此配置後，Azure Functions 會自動生成唯一的 Host ID

## 預期結果

- 消除 Host ID collision 錯誤
- Function App 正常運行
- 不影響任何功能（因為我們本來就沒有使用 Durable Functions）

## 部署後驗證

部署後請檢查：
1. Azure Portal > Function App > Diagnose and solve problems
2. 確認 AZFD0004 錯誤不再出現
3. 確認所有 API 端點正常運作