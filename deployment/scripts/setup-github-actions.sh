#!/bin/bash

# GitHub Actions 設置腳本
# 此腳本幫助設置 GitHub Actions 所需的 secrets

set -e

echo "🚀 GitHub Actions CI/CD 設置腳本"
echo "================================"

# 檢查是否已登入 Azure
if ! az account show &>/dev/null; then
    echo "❌ 請先執行 'az login' 登入 Azure"
    exit 1
fi

# 設定變數
SUBSCRIPTION_ID="5396d388-8261-464e-8ee4-112770674fba"
RESOURCE_GROUP="airesumeadvisorfastapi"
ACR_NAME="airesumeadvisorregistry"
GITHUB_REPO="azure_fastapi"

echo ""
echo "📋 將使用以下設定："
echo "   Subscription ID: $SUBSCRIPTION_ID"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   ACR Name: $ACR_NAME"
echo ""

# 1. 建立 Service Principal
echo "1. 建立 Service Principal..."
SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "github-actions-sp-${GITHUB_REPO}" \
    --role contributor \
    --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
    --sdk-auth)

echo "✅ Service Principal 建立成功"
echo ""

# 2. 獲取 ACR 認證
echo "2. 獲取 ACR 認證..."
ACR_USERNAME=$ACR_NAME
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo "✅ ACR 認證獲取成功"
echo ""

# 3. 顯示需要設置的 Secrets
echo "📝 請在 GitHub 專案的 Settings → Secrets and variables → Actions 中設置以下 secrets："
echo ""
echo "====== AZURE_CREDENTIALS ======"
echo "$SP_OUTPUT"
echo ""
echo "====== ACR_USERNAME ======"
echo "$ACR_USERNAME"
echo ""
echo "====== ACR_PASSWORD ======"
echo "$ACR_PASSWORD"
echo ""

# 4. 從 .env 檔案讀取其他必要的 secrets
if [ -f ".env" ]; then
    echo "====== 其他必要的 Secrets (從 .env 讀取) ======"
    echo ""
    
    # 使用更安全的方式讀取 .env
    while IFS='=' read -r key value; do
        # 跳過註解和空行
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        # 移除引號
        value="${value%\"}"
        value="${value#\"}"
        
        case "$key" in
            AZURE_OPENAI_ENDPOINT|AZURE_OPENAI_API_KEY|GPT41_MINI_JAPANEAST_ENDPOINT|GPT41_MINI_JAPANEAST_API_KEY|EMBEDDING_ENDPOINT|EMBEDDING_API_KEY|DATABASE_URL|VALID_API_KEYS)
                echo "$key=$value"
                echo ""
                ;;
        esac
    done < .env
else
    echo "⚠️  找不到 .env 檔案，請手動設置以下 secrets："
    echo "   - AZURE_OPENAI_ENDPOINT"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - GPT41_MINI_JAPANEAST_ENDPOINT"
    echo "   - GPT41_MINI_JAPANEAST_API_KEY"
    echo "   - EMBEDDING_ENDPOINT"
    echo "   - EMBEDDING_API_KEY"
    echo "   - DATABASE_URL"
    echo "   - VALID_API_KEYS"
fi

echo ""
echo "📌 設置步驟："
echo "1. 前往 https://github.com/[your-username]/${GITHUB_REPO}/settings/secrets/actions"
echo "2. 點擊 'New repository secret'"
echo "3. 貼上上述的 secret 名稱和值"
echo "4. 重複步驟 2-3 直到所有 secrets 都設置完成"
echo ""
echo "✅ 設置完成後，GitHub Actions 將在推送到 container 分支時自動執行！"

# 5. 選擇性：自動使用 GitHub CLI 設置 secrets
echo ""
read -p "是否要使用 GitHub CLI 自動設置 secrets？(需要先安裝 gh) [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 檢查 gh 是否安裝
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI (gh) 未安裝"
        echo "   請參考 https://cli.github.com/ 安裝"
        exit 1
    fi
    
    # 檢查是否已登入
    if ! gh auth status &>/dev/null; then
        echo "請先執行 'gh auth login' 登入 GitHub"
        exit 1
    fi
    
    echo "設置 GitHub Secrets..."
    
    # 設置 secrets
    echo "$SP_OUTPUT" | gh secret set AZURE_CREDENTIALS
    echo "$ACR_USERNAME" | gh secret set ACR_USERNAME  
    echo "$ACR_PASSWORD" | gh secret set ACR_PASSWORD
    
    # 從 .env 設置其他 secrets
    if [ -f ".env" ]; then
        while IFS='=' read -r key value; do
            [[ $key =~ ^#.*$ ]] && continue
            [[ -z $key ]] && continue
            
            value="${value%\"}"
            value="${value#\"}"
            
            case "$key" in
                AZURE_OPENAI_ENDPOINT|AZURE_OPENAI_API_KEY|GPT41_MINI_JAPANEAST_ENDPOINT|GPT41_MINI_JAPANEAST_API_KEY|EMBEDDING_ENDPOINT|EMBEDDING_API_KEY|DATABASE_URL|VALID_API_KEYS)
                    echo "設置 $key..."
                    echo "$value" | gh secret set "$key"
                    ;;
            esac
        done < .env
    fi
    
    echo "✅ 所有 secrets 已自動設置完成！"
fi

echo ""
echo "🎉 GitHub Actions CI/CD 設置完成！"