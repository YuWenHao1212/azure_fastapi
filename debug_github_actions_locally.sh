#!/bin/bash

# 模擬 GitHub Actions 部署行為的本地除錯腳本

echo "=== GitHub Actions 部署除錯腳本 ==="
echo "這個腳本模擬 GitHub Actions 的部署步驟"
echo ""

# 環境變數
REGISTRY="airesumeadvisorregistry.azurecr.io"
IMAGE_NAME="airesumeadvisor-api"
RESOURCE_GROUP="airesumeadvisorfastapi"
CONTAINER_APP_NAME="airesumeadvisor-api-production"

echo "1. 檢查當前 Azure 登入狀態"
az account show --query "{name: name, user: user.name}" -o table

echo ""
echo "2. 獲取最新的映像標籤"
LATEST_TAG=$(az acr repository show-tags \
  --name airesumeadvisorregistry \
  --repository $IMAGE_NAME \
  --orderby time_desc \
  --top 1 \
  -o tsv)

echo "最新標籤: $LATEST_TAG"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$LATEST_TAG"

echo ""
echo "3. 創建 revision suffix (模擬 GitHub SHA)"
# 使用時間戳的最後 10 位作為 revision suffix
REVISION_SUFFIX=$(date +%s | tail -c 10)
echo "Revision suffix: $REVISION_SUFFIX"

echo ""
echo "4. 顯示將要執行的部署命令"
echo "az containerapp update \\"
echo "  --name $CONTAINER_APP_NAME \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --image $FULL_IMAGE \\"
echo "  --revision-suffix $REVISION_SUFFIX"

echo ""
read -p "是否執行部署？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "執行部署..."
    
    # 使用 debug 模式
    az containerapp update \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --image $FULL_IMAGE \
      --revision-suffix $REVISION_SUFFIX \
      --debug 2>&1 | tee debug_deploy.log
    
    echo ""
    echo "等待 30 秒..."
    sleep 30
    
    echo ""
    echo "5. 檢查部署狀態"
    LATEST_REVISION=$(az containerapp revision list \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --query "[0].name" -o tsv)
    
    echo "最新 revision: $LATEST_REVISION"
    
    REVISION_STATUS=$(az containerapp revision show \
      --name $CONTAINER_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --revision $LATEST_REVISION \
      --query "properties.runningState" -o tsv)
    
    echo "Revision 狀態: $REVISION_STATUS"
    
    if [ "$REVISION_STATUS" != "Running" ]; then
        echo ""
        echo "部署失敗！嘗試獲取日誌..."
        az containerapp logs show \
          --name $CONTAINER_APP_NAME \
          --resource-group $RESOURCE_GROUP \
          --revision $LATEST_REVISION \
          --tail 50 || echo "無法獲取日誌"
    else
        echo ""
        echo "部署成功！"
    fi
    
    echo ""
    echo "除錯日誌已保存到: debug_deploy.log"
else
    echo "取消部署"
fi