#!/bin/bash

# 診斷 Container App 部署問題
set -e

echo "🔍 Container App 部署診斷工具"
echo "============================"

RESOURCE_GROUP="airesumeadvisorfastapi"
APP_NAME="airesumeadvisor-api-production"
REGISTRY="airesumeadvisorregistry"

# 1. 檢查當前狀態
echo ""
echo "1. 檢查 Container App 當前狀態："
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{name:name, state:properties.provisioningState, environment:properties.managedEnvironmentId}" \
  -o table

# 2. 檢查最新的 revisions
echo ""
echo "2. 最近的 Revisions："
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[0:5].{name:name, active:properties.active, state:properties.runningState, created:properties.createdTime, replicas:properties.replicas}" \
  -o table

# 3. 檢查失敗的 revision 詳情
echo ""
echo "3. 檢查非 Running 狀態的 Revision："
FAILED_REVISIONS=$(az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[?properties.runningState!='Running'].name" \
  -o tsv)

if [ ! -z "$FAILED_REVISIONS" ]; then
  for REVISION in $FAILED_REVISIONS; do
    echo ""
    echo "檢查 Revision: $REVISION"
    echo "------------------------"
    
    # 獲取 revision 詳情
    az containerapp revision show \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --revision $REVISION \
      --query "{state:properties.runningState, replicas:properties.replicas, traffic:properties.trafficWeight}" \
      -o json
    
    # 嘗試獲取日誌
    echo ""
    echo "Revision 日誌："
    az containerapp logs show \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --revision $REVISION \
      --tail 20 2>&1 || echo "無法獲取日誌"
  done
fi

# 4. 檢查 ACR 中的映像
echo ""
echo "4. 檢查 ACR 中最新的映像："
az acr repository show-tags \
  --name $REGISTRY \
  --repository airesumeadvisor-api \
  --orderby time_desc \
  --top 5 \
  -o table

# 5. 檢查環境變數配置
echo ""
echo "5. 檢查環境變數配置："
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env[].name" \
  -o tsv | sort

# 6. 檢查 secrets
echo ""
echo "6. 檢查已配置的 Secrets："
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.secrets[].name" \
  -o tsv | sort

# 7. 檢查資源限制
echo ""
echo "7. 檢查資源配置："
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].resources" \
  -o json

# 8. 檢查 Container App Environment
echo ""
echo "8. 檢查 Container App Environment："
ENV_ID=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.managedEnvironmentId" \
  -o tsv)

ENV_NAME=$(basename $ENV_ID)
az containerapp env show \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{name:name, state:properties.provisioningState}" \
  -o table

# 9. 測試應用健康狀態
echo ""
echo "9. 測試應用健康狀態："
APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" \
  -o tsv)

if [ ! -z "$APP_URL" ]; then
  echo "應用 URL: https://$APP_URL"
  echo "測試 /health 端點..."
  curl -s -w "\nHTTP Status: %{http_code}\n" https://$APP_URL/health || echo "健康檢查失敗"
fi

echo ""
echo "診斷完成！"