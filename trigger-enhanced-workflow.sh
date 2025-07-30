#!/bin/bash

# 觸發增強診斷 workflow 的腳本

echo "觸發 Container Apps CI/CD Enhanced workflow..."

# 使用 GitHub API 觸發 workflow
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/YuWenHao1212/azure_fastapi/actions/workflows/container-cicd-enhanced.yml/dispatches \
  -d '{
    "ref": "container",
    "inputs": {
      "deploy_mode": "test"
    }
  }'

echo "\n如果需要 GitHub Token，請："
echo "1. 訪問 https://github.com/settings/tokens"
echo "2. 生成新的 Personal Access Token (classic)"
echo "3. 勾選 'repo' 和 'workflow' 權限"
echo "4. 運行: export GITHUB_TOKEN=your_token_here"