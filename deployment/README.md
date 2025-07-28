# 部署配置目錄

此目錄包含 AI Resume Advisor API 的所有部署相關配置檔案。

## 目錄結構

```
deployment/
├── container-apps/          # Azure Container Apps 部署
│   ├── Dockerfile          # 容器映像定義
│   ├── docker-compose.yml  # 本地開發環境
│   ├── nginx.conf          # Nginx 代理配置
│   └── container-apps-environment.yaml  # Container Apps 環境配置
├── function-apps/          # Azure Functions 部署（保留參考）
│   ├── function.json       # Function 配置
│   ├── function_app.py     # Function 入口點
│   └── host.json          # Function Host 配置
└── scripts/               # 部署腳本
    ├── deploy-container-apps.sh
    ├── test-container-apps.sh
    └── rollback.sh
```

## 使用方式

### Container Apps 部署
```bash
# 本地開發
cd deployment/container-apps
docker-compose up -d

# Azure 部署
./scripts/deploy-container-apps.sh

# 測試部署
./scripts/test-container-apps.sh
```

### 快速指令（根目錄）
```bash
# 根目錄的 Makefile 已更新路徑
make build          # 建置 Docker 映像
make run            # 本地運行
make deploy-dev     # 部署到 Azure
```

所有 Makefile 和腳本都已更新為使用新的檔案路徑。