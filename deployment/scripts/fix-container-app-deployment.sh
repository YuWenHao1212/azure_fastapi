#!/bin/bash

# 修復 Container App 部署問題
set -e

echo "🔧 Container App 部署修復工具"
echo "============================"

RESOURCE_GROUP="airesumeadvisorfastapi"
APP_NAME="airesumeadvisor-api-production"
REGISTRY="airesumeadvisorregistry"

# 1. 停止所有非活躍的 revisions
echo "1. 清理非活躍的 revisions..."
INACTIVE_REVISIONS=$(az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[?properties.active==\`false\`].name" \
  -o tsv)

if [ ! -z "$INACTIVE_REVISIONS" ]; then
  for REVISION in $INACTIVE_REVISIONS; do
    echo "停用 revision: $REVISION"
    az containerapp revision deactivate \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --revision $REVISION || echo "無法停用 $REVISION"
  done
else
  echo "沒有需要清理的非活躍 revisions"
fi

# 2. 確保所有必要的 secrets 都已設置
echo ""
echo "2. 檢查並設置必要的 secrets..."
REQUIRED_SECRETS=(
  "azure-openai-key"
  "embedding-api-key"
  "gpt41-mini-key"
  "jwt-secret"
  "container-app-api-key"
)

EXISTING_SECRETS=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.secrets[].name" \
  -o tsv)

for SECRET in "${REQUIRED_SECRETS[@]}"; do
  if ! echo "$EXISTING_SECRETS" | grep -q "^$SECRET$"; then
    echo "⚠️  缺少 secret: $SECRET"
    echo "請手動設置此 secret"
  else
    echo "✅ Secret 已存在: $SECRET"
  fi
done

# 3. 驗證環境變數引用的 secrets
echo ""
echo "3. 驗證環境變數配置..."
ENV_VARS=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" \
  -o json)

echo "$ENV_VARS" | jq -r '.[] | select(.secretRef != null) | "\(.name) -> \(.secretRef)"' | while read line; do
  VAR_NAME=$(echo $line | cut -d' ' -f1)
  SECRET_REF=$(echo $line | cut -d' ' -f3)
  
  if echo "$EXISTING_SECRETS" | grep -q "^$SECRET_REF$"; then
    echo "✅ $VAR_NAME 正確引用 secret: $SECRET_REF"
  else
    echo "❌ $VAR_NAME 引用的 secret 不存在: $SECRET_REF"
  fi
done

# 4. 使用最新的穩定映像重新部署
echo ""
echo "4. 獲取最新的穩定映像..."
LATEST_TAG=$(az acr repository show-tags \
  --name $REGISTRY \
  --repository airesumeadvisor-api \
  --orderby time_desc \
  --top 1 \
  -o tsv)

CURRENT_IMAGE=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].image" \
  -o tsv)

echo "當前映像: $CURRENT_IMAGE"
echo "最新標籤: $LATEST_TAG"

read -p "是否要使用最新映像重新部署？(yes/no): " REDEPLOY
if [ "$REDEPLOY" = "yes" ]; then
  FULL_IMAGE="$REGISTRY.azurecr.io/airesumeadvisor-api:$LATEST_TAG"
  REVISION_SUFFIX=$(date +%s | tail -c 10)
  
  echo "部署新映像: $FULL_IMAGE"
  az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $FULL_IMAGE \
    --revision-suffix $REVISION_SUFFIX
  
  # 等待部署完成
  echo "等待部署完成..."
  sleep 30
  
  # 檢查新 revision 狀態
  LATEST_REVISION=$(az containerapp revision list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[0].name" \
    -o tsv)
  
  REVISION_STATE=$(az containerapp revision show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --revision $LATEST_REVISION \
    --query "properties.runningState" \
    -o tsv)
  
  if [ "$REVISION_STATE" = "Running" ]; then
    echo "✅ 部署成功！新 revision 正在運行"
  else
    echo "❌ 部署失敗！Revision 狀態: $REVISION_STATE"
    echo "查看日誌："
    az containerapp logs show \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --revision $LATEST_REVISION \
      --tail 50
  fi
fi

# 5. 重置流量分配（如果需要）
echo ""
echo "5. 檢查流量分配..."
TRAFFIC=$(az containerapp ingress traffic show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  -o json)

echo "當前流量分配："
echo "$TRAFFIC" | jq

echo ""
echo "修復程序完成！"
echo ""
echo "後續步驟："
echo "1. 運行診斷腳本查看當前狀態: ./diagnose-container-app.sh"
echo "2. 如果仍有問題，檢查 Application Insights 日誌"
echo "3. 確保所有必要的 secrets 都已正確設置"