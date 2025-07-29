#\!/bin/bash

# 檢查 GitHub Actions Service Principal 的權限
# 需要從 GitHub Secrets 中的 AZURE_CREDENTIALS 獲取資訊

echo "請提供 GitHub Secrets 中 AZURE_CREDENTIALS 的 clientId，我們可以檢查權限："
echo ""
echo "或者在 Azure Portal 中："
echo "1. 前往 Azure Active Directory"
echo "2. 選擇 App registrations"
echo "3. 找到你的 Service Principal"
echo "4. 檢查 API permissions 和 Role assignments"
echo ""
echo "Service Principal 需要的權限："
echo "- Container Apps Contributor"
echo "- AcrPush (for ACR)"
echo "- 在 Resource Group 層級的 Contributor 角色"
