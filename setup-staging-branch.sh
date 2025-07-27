#!/bin/bash

# Setup script for staging branch and deployment
# This script helps set up the staging branch with proper protection rules

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Setting up Staging Branch and Deployment${NC}"
echo "============================================"

# Check if we're in the right repository
if [ ! -f "function_app.py" ]; then
    echo -e "${RED}❌ This script must be run from the azure_fastapi repository root${NC}"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "Current branch: ${YELLOW}$CURRENT_BRANCH${NC}"

# Step 1: Create staging branch if it doesn't exist
if git show-ref --verify --quiet refs/heads/staging; then
    echo -e "${YELLOW}⚠️  Staging branch already exists${NC}"
else
    echo -e "${GREEN}Creating staging branch from main...${NC}"
    git checkout main
    git pull origin main
    git checkout -b staging
    echo -e "${GREEN}✅ Staging branch created${NC}"
fi

# Step 2: Push staging branch to origin
echo -e "\n${GREEN}Pushing staging branch to origin...${NC}"
git push -u origin staging

# Step 3: Install pre-commit hooks
echo -e "\n${GREEN}Installing pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️  pre-commit not found. Install with: pip install pre-commit${NC}"
fi

# Step 4: Create necessary GitHub Secrets reminder
echo -e "\n${YELLOW}📋 GitHub Secrets Required:${NC}"
echo "Please add the following secrets to your GitHub repository:"
echo ""
echo "1. ${GREEN}AZURE_FUNCTIONAPP_STAGING_PUBLISH_PROFILE${NC}"
echo "   - Go to Azure Portal > Function App > Deployment Center"
echo "   - Download publish profile for staging slot"
echo ""
echo "2. ${GREEN}STAGING_HOST_KEY${NC}"
echo "   - Go to Azure Portal > Function App (staging slot) > App keys"
echo "   - Copy the default host key"
echo ""
echo "3. API Keys (if not already set):"
echo "   - ${GREEN}AZURE_OPENAI_API_KEY${NC}"
echo "   - ${GREEN}AZURE_OPENAI_ENDPOINT${NC}"
echo "   - ${GREEN}LLM2_API_KEY${NC}"
echo "   - ${GREEN}LLM2_ENDPOINT${NC}"
echo "   - ${GREEN}GPT41_MINI_JAPANEAST_API_KEY${NC}"
echo "   - ${GREEN}GPT41_MINI_JAPANEAST_ENDPOINT${NC}"
echo "   - ${GREEN}EMBEDDING_API_KEY${NC}"
echo "   - ${GREEN}EMBEDDING_ENDPOINT${NC}"

# Step 5: Branch protection rules reminder
echo -e "\n${YELLOW}🔒 Branch Protection Rules:${NC}"
echo "Please configure the following in GitHub Settings > Branches:"
echo ""
echo "${GREEN}For 'staging' branch:${NC}"
echo "  ✓ Require pull request reviews (1 approval)"
echo "  ✓ Require status checks to pass (PR Tests - Level 3)"
echo "  ✓ Require branches to be up to date"
echo ""
echo "${YELLOW}📋 注意：main 分支目前不設定，未來再討論${NC}"

# Step 6: Create staging slot in Azure (if needed)
echo -e "\n${YELLOW}☁️  Azure Staging Slot:${NC}"
echo "To create a staging slot (if not exists):"
echo ""
echo "az functionapp deployment slot create \\"
echo "  --name airesumeadvisor-fastapi \\"
echo "  --resource-group airesumeadvisorfastapi \\"
echo "  --slot staging"

# Step 7: Test the setup
echo -e "\n${GREEN}🧪 Testing the setup...${NC}"

# Check if workflows exist
if [ -f ".github/workflows/deploy-staging.yml" ] && [ -f ".github/workflows/pr-tests.yml" ]; then
    echo -e "${GREEN}✅ GitHub Actions workflows found${NC}"
else
    echo -e "${RED}❌ GitHub Actions workflows missing${NC}"
fi

# Check if pre-commit config exists
if [ -f ".pre-commit-config.yaml" ]; then
    echo -e "${GREEN}✅ Pre-commit configuration found${NC}"
else
    echo -e "${RED}❌ Pre-commit configuration missing${NC}"
fi

# Check if precommit.sh is executable
if [ -x "precommit.sh" ]; then
    echo -e "${GREEN}✅ precommit.sh is executable${NC}"
else
    echo -e "${YELLOW}⚠️  Making precommit.sh executable...${NC}"
    chmod +x precommit.sh
fi

echo -e "\n${GREEN}✨ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Add the required GitHub Secrets"
echo "2. Configure branch protection rules for staging"
echo "3. Create Azure staging slot (if needed)"
echo "4. Test the workflow:"
echo "   - Create a feature branch: git checkout -b feature/test-staging"
echo "   - Use Claude Code to develop (will run Level 0-3 tests)"
echo "   - Push and create PR to staging (will run Level 3)"
echo "   - Merge PR → Auto deploy to Azure Staging"
echo "   - Manually run Level 4 test locally: ./precommit.sh --level-4"
echo ""
echo "${YELLOW}⚠️  重要提醒:${NC}"
echo "- Claude Code 會根據修改範圍執行適當層級測試 (Level 0-3)"
echo "- Merge/Push to Staging 會自動部署到 Azure Staging Slot"
echo "- Level 4 是您手動在本地執行的測試，用於驗證部署後功能"
echo "- 請參閱 CLAUDE.md 了解測試分級策略"

# Return to original branch
git checkout $CURRENT_BRANCH