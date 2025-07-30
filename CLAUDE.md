# CLAUDE.md - FHS + FastAPI 重構專案協作指南 v2.9.0

> 最後更新：2025-07-28 16:35:13 CST

## ⚠️ 關鍵提醒 (CRITICAL REMINDERS)

### 🕐 時間處理規則 (TIME HANDLING RULE)
**任何需要日期或時間時，必須先執行**：
```bash
TZ='Asia/Taipei' date '+%Y-%m-%d %H:%M:%S %Z'
```
- 文檔命名：`[TYPE]_[MODULE]_YYYYMMDD.md`
- 日誌記錄：`YYYY-MM-DD HH:MM:SS CST`
- 絕不使用 <env> 中的日期或憑空推測！

### 🚫 Git 提交規則 (GIT COMMIT RULE)
Claude Code **絕對不可以**自行執行 `git commit`
- 必須根據修改類型執行對應層級的預提交測試：
  - Prompt 修改：`./precommit.sh --level-0`
  - 程式碼格式/註解：`./precommit.sh --level-1`
  - 功能邏輯修改：`./precommit.sh --level-2 --parallel`
  - API/核心修改：`./precommit.sh --level-3 --parallel`
  - 預部署驗證：`./precommit.sh --level-4`
- 向用戶展示完整測試結果
- 獲得用戶明確同意後才能提交

### 🧪 測試執行規則 (TESTING RULE)
**根據修改類型選擇適當的測試層級**：
```bash
# Level 0: Prompt 修改（不需要 AI）
./precommit.sh --level-0

# Level 1: 程式碼風格（不需要 AI）
./precommit.sh --level-1

# Level 2: 單元測試（建議使用 --parallel）
./precommit.sh --level-2 --parallel

# Level 3: 整合測試（建議使用 --parallel）
./precommit.sh --level-3 --parallel

# Level 4: Azure Functions 本地測試（預部署驗證）
./precommit.sh --level-4
```
- Level 0-1：不需要 AI 憑證，執行快速
- Level 2-3：需要真實 API 憑證（從 .env 讀取）
- Level 4：需要 Azure Functions Core Tools + 真實 API 憑證
- 使用 `--parallel` 加速測試執行（Level 2-3）

---

本文件為 Claude Code + Cursor + Azure DevOps 協作開發指南，專門為 API 重構專案（FHS + FastAPI）設計。

## 📋 目錄

1. [專案概述](#專案概述)
2. [安全配置指南](#安全配置指南)
3. [協作角色與職責](#協作角色與職責)
4. [開發階段與里程碑](#開發階段與里程碑)
5. [任務管理方式](#任務管理方式)
6. [文檔工作流程](#文檔工作流程)
7. [測試策略與管理](#測試策略與管理)
8. [Azure CLI 命令參考](#azure-cli-命令參考)
9. [快速參考卡](#快速參考卡)
10. [Bubble.io API 相容性](#bubbleio-api-相容性)
11. [注意事項](#注意事項)
12. [Claude Code Sub-agents 參考](#claude-code-sub-agents-參考)

---

## 專案概述

### 技術棧

#### 當前部署架構 (Functions 版本)
- **架構模式**: FHS (Functional Hierarchy Structure) 
- **框架**: FastAPI
- **Python 版本**: 3.11.8 (使用 .venv 虛擬環境)
- **虛擬環境**: `/Users/yuwenhao/Documents/GitHub/azure_fastapi/.venv/`
- **部署平台**: Azure Function App (Premium Plan EP1)
- **主要部署**: Japan East (airesumeadvisor-fastapi-japaneast)
- **版本控制**: GitHub (主要) + Azure DevOps Repos (鏡像)
- **CI/CD**: ✅ GitHub Actions → Azure Functions（已完成設置，push to main 自動部署）

#### 目標架構 (Container Apps 版本) 🎯
- **架構模式**: 雲原生容器化架構
- **框架**: FastAPI (原生運行，無 ASGI 適配層)
- **容器技術**: Docker + Azure Container Apps
- **部署區域**: Japan East (與 OpenAI 同區域)
- **自動縮放**: 2-10 實例
- **預期效能**: 40-91% 響應時間改善

#### 開發工具
- **協作工具**: Claude Code + WenHao (Cursor 僅作為 IDE，不使用其 LLM)
- **記憶系統**: Serena MCP (提供歷史記錄查詢，但非日常開發工具)
- **Sub-agents**: 37 個專門 agents，詳見 `/Users/yuwenhao/.claude/agents/`

### Azure DevOps 專案資訊
- **組織**: airesumeadvisor
- **專案**: API
- **URL**: https://dev.azure.com/airesumeadvisor/API

### Azure 資源資訊
- **Subscription ID**: 5396d388-8261-464e-8ee4-112770674fba
- **Resource Group**: airesumeadvisorfastapi
- **Application Insights**: airesumeadvisorfastapi
- **Tenant**: wenhaoairesumeadvisor.onmicrosoft.com
- **Portal URL**: https://portal.azure.com/#@wenhaoairesumeadvisor.onmicrosoft.com/resource/subscriptions/5396d388-8261-464e-8ee4-112770674fba/resourceGroups/airesumeadvisorfastapi/providers/Microsoft.Insights/components/airesumeadvisorfastapi/overview

### Azure Function App 資訊 (當前部署)

#### 主要生產環境 - Japan East 🌏
- **Function App 名稱**: airesumeadvisor-fastapi-japaneast
- **基礎 URL**: https://airesumeadvisor-fastapi-japaneast.azurewebsites.net
- **Host Key**: 從環境變數 `AZURE_FUNCTION_KEY_JAPAN_EAST` 獲取
- **計畫類型**: Premium Plan (EP1)
- **部署區域**: Japan East
- **狀態**: 主要生產環境 ✅
- **特色**: 與 GPT-4.1 mini 同區域，網路延遲最低

#### 備用環境

**Standard 環境 (備用)**:
- **Function App 名稱**: airesumeadvisor-fastapi
- **基礎 URL**: https://airesumeadvisor-fastapi.azurewebsites.net
- **計畫類型**: Flex Consumption Plan
- **狀態**: 備用環境

**Premium 環境 (East Asia)**:
- **Function App 名稱**: airesumeadvisor-fastapi-premium
- **基礎 URL**: https://airesumeadvisor-fastapi-premium.azurewebsites.net
- **計畫類型**: Premium Plan (EP1)
- **部署區域**: East Asia
- **狀態**: 備用環境

**注意**: 
- 當前主要使用 Japan East 環境，效能最佳
- 所有 Function Keys 已改為環境變數管理，提升安全性
- 其他環境作為備用，用於災難恢復或 A/B 測試

### PostgreSQL 資料庫資訊
- **Host**: airesumeadvisor-courses-db-eastasia.postgres.database.azure.com
- **Database**: coursesdb
- **Port**: 5432
- **SSL Mode**: require
- **SKU**: Standard_B1ms (Burstable)
- **Location**: East Asia
- **連接字串格式**:
  ```
  postgresql://[USER]:[PASSWORD]@airesumeadvisor-courses-db-eastasia.postgres.database.azure.com/coursesdb?sslmode=require
  ```

### PostgreSQL Schema (2025-07-26 版本)

**資料表結構**：

1. **courses** - 課程主表
   ```sql
   id VARCHAR(255) PRIMARY KEY                   -- 格式: {platform}_{external_id}
   platform VARCHAR(50) NOT NULL DEFAULT 'coursera'
   external_id VARCHAR(255) NOT NULL             -- 原始平台 ID
   name TEXT NOT NULL                            -- 課程名稱
   description TEXT                              -- 課程描述
   provider VARCHAR(500)                         -- 原始提供者名稱
   provider_standardized VARCHAR(255)            -- 標準化提供者名稱
   provider_logo_url VARCHAR(1000)              -- 提供者 Logo URL
   category VARCHAR(500)                         -- 類別
   course_type VARCHAR(50)                       -- 原始課程類型
   course_type_standard VARCHAR(50)              -- 標準化課程類型
   price NUMERIC DEFAULT 0                       -- 價格
   currency VARCHAR(10) DEFAULT 'USD'            -- 貨幣
   image_url TEXT                                -- 課程圖片
   affiliate_url TEXT NOT NULL                   -- 聯盟行銷連結
   difficulty_level VARCHAR(20)                  -- 難度等級
   rating NUMERIC                                -- 評分
   ratings_count INTEGER                         -- 評分數量
   enrolled_count INTEGER                        -- 註冊人數
   estimated_hours INTEGER                       -- 預估學習時數
   embedding vector(3072)                        -- 向量嵌入 (pgvector)
   metadata JSONB                                -- 額外元資料
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   
   UNIQUE(platform, external_id)
   ```

2. **search_logs** - 搜尋記錄
   ```sql
   id SERIAL PRIMARY KEY
   query TEXT NOT NULL                           -- 搜尋查詢
   results_count INTEGER DEFAULT 0               -- 結果數量
   response_time_ms INTEGER                      -- 回應時間(毫秒)
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   ```

3. **sync_logs** - 同步記錄
   ```sql
   id SERIAL PRIMARY KEY
   sync_type VARCHAR(50) NOT NULL                -- 同步類型
   platform VARCHAR(50)                          -- 平台
   total_processed INTEGER DEFAULT 0             -- 處理總數
   new_courses INTEGER DEFAULT 0                 -- 新增課程數
   updated_courses INTEGER DEFAULT 0             -- 更新課程數
   status VARCHAR(50) NOT NULL                   -- 狀態
   error_message TEXT                            -- 錯誤訊息
   started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   completed_at TIMESTAMP
   ```

**索引**：
- idx_courses_platform (platform)
- idx_courses_provider (provider)
- idx_courses_provider_standardized (provider_standardized)
- idx_courses_category (category)
- idx_courses_type (course_type)
- idx_course_type_standard (course_type_standard)
- idx_courses_price (price)

### 已部署的 API 端點

#### 🌏 主要生產環境 - Japan East (推薦使用)
```bash
# 關鍵字提取 (優化後：平均 2.8 秒)
https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/extract-jd-keywords?code=${AZURE_FUNCTION_KEY_JAPAN_EAST}

# 指標計算
https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/index-calculation?code=${AZURE_FUNCTION_KEY_JAPAN_EAST}

# 指標計算與間隙分析
https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/index-cal-and-gap-analysis?code=${AZURE_FUNCTION_KEY_JAPAN_EAST}

# 履歷格式化
https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/format-resume?code=${AZURE_FUNCTION_KEY_JAPAN_EAST}

# 履歷優化
https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/tailor-resume?code=${AZURE_FUNCTION_KEY_JAPAN_EAST}

# 課程搜尋
https://airesumeadvisor-fastapi-japaneast.azurewebsites.net/api/v1/courses/search?code=${AZURE_FUNCTION_KEY_JAPAN_EAST}
```

#### 🔄 備用環境

**Standard 環境 (Flex Consumption)**:
```bash
# 基礎 URL（備用）
https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/[endpoint]?code=${AZURE_FUNCTION_KEY_STANDARD}
```

**Premium 環境 - East Asia (備用)**:
```bash
# 基礎 URL（備用）  
https://airesumeadvisor-fastapi-premium.azurewebsites.net/api/v1/[endpoint]?code=${AZURE_FUNCTION_KEY_PREMIUM}
```

**使用建議**:
- ✅ **主要使用**: Japan East 環境 (最佳效能)
- ⚠️ **備用**: 其他環境僅在 Japan East 不可用時使用
- 🔐 **安全**: 所有 Function Keys 已改為環境變數管理

### FHS + FastAPI 架構規範

```
azure_fastapi/
├── CLAUDE.md                    # 本協作指南
├── README.md                    # 專案說明文件
├── requirements.txt             # Python 套件依賴
├── pyproject.toml              # Python 專案配置
├── pytest.ini                  # pytest 測試配置
├── function.json               # Azure Function 配置
├── function_app.py             # Azure Function 入口點
├── host.json                   # Azure Function Host 配置
├── .venv/                      # Python 虛擬環境 (3.11.8)
├── .claude/                    # Claude Code 全域設定
├── .cursor/                    # Cursor IDE 配置 (僅作為 IDE)
├── .serena/                    # Serena MCP 記憶系統
│   ├── memories/              # 開發記憶與決策記錄
│   ├── cache/                 # 快取資料
│   └── project.yml            # Serena 專案配置
├── .github/                    # GitHub Actions CI/CD
│   └── workflows/             # 自動部署工作流程
├── src/                        # FHS 架構原始碼
│   ├── main.py               # FastAPI 應用主程式
│   ├── api/                  # API 路由端點
│   │   ├── v1/              # v1 版本 API
│   │   └── endpoints/       # 特定功能端點
│   ├── core/                # 核心功能
│   │   ├── config.py       # 配置管理
│   │   └── monitoring/     # 監控相關
│   ├── services/           # 業務邏輯服務
│   │   ├── language_detection/  # 語言偵測
│   │   ├── standardization/     # 標準化處理
│   │   └── etl/                 # ETL 處理
│   ├── models/             # 資料模型
│   ├── prompts/            # LLM Prompt 模板
│   ├── data/               # 靜態資料
│   └── utils/              # 工具函數
├── tests/                      # 測試檔案
│   ├── unit/                  # 單元測試
│   ├── integration/           # 整合測試
│   ├── functional/            # 功能測試
│   └── temp/                  # 臨時測試檔案
├── docs/                       # 文檔管理
│   ├── published/             # 已發布文檔
│   ├── bubble_integration/    # Bubble.io 整合文檔
│   └── local/                 # 本地文檔
├── temp/                       # 臨時檔案統一管理
│   ├── tests/                # 測試相關臨時檔案
│   ├── demos/                # 展示檔案
│   └── dev/                  # 開發暫存檔案
├── tools/                      # 開發工具
│   ├── testing/              # 測試工具
│   ├── monitoring/           # 監控工具
│   └── coursera_db_manager/  # Coursera 資料庫管理
├── legacy/                     # 舊版參考資料
├── archive/                    # 歸檔資料
├── azure/                      # Azure 部署相關配置
├── commands/                   # 自定義指令
├── custom/                     # 自定義擴充
├── data/                       # 專案資料檔案
├── htmlcov/                   # 測試覆蓋率報告
└── wiki-export/               # Wiki 匯出檔案
```

---

## 安全配置指南

### 環境變數管理

```yaml
# 當前 Azure OpenAI 配置（可提交）
AZURE_OPENAI_ENDPOINT: https://airesumeadvisor-japaneast.openai.azure.com
AZURE_OPENAI_GPT4_DEPLOYMENT: gpt-4o-mini
AZURE_OPENAI_API_VERSION: 2024-02-15-preview

# 向量嵌入配置 (目前使用 Sweden Central)
EMBEDDING_ENDPOINT: https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com

# 敏感配置（絕不提交）- 存放位置：
# 1. Azure Key Vault (生產環境) 
# 2. local.settings.json (本地開發)
# 3. GitHub Secrets (CI/CD)
# 4. Azure Function App Configuration (部署環境)

# Function Keys (環境變數)
AZURE_FUNCTION_KEY_JAPAN_EAST: # Japan East 主要環境
AZURE_FUNCTION_KEY_STANDARD: # Standard 備用環境
AZURE_FUNCTION_KEY_PREMIUM: # Premium 備用環境

# OpenAI API Keys
AZURE_OPENAI_API_KEY: # Japan East OpenAI 服務金鑰
EMBEDDING_API_KEY: # Sweden Central 嵌入服務金鑰
```

### 配置範例

```python
# src/core/config.py
from pydantic_settings import BaseSettings
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class Settings(BaseSettings):
    # 公開配置
    embedding_endpoint: str = "https://..."
    llm2_endpoint: str = "https://..."
    
    # 敏感配置 - 從環境變數或 Key Vault 讀取
    llm2_api_key: str = ""
    openai_api_key: str = ""
    
    def load_from_keyvault(self):
        """生產環境從 Key Vault 載入敏感資訊"""
        keyvault_url = "https://your-keyvault.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=keyvault_url, credential=credential)
        
        self.llm2_api_key = client.get_secret("LLM2-API-KEY").value
        self.openai_api_key = client.get_secret("OPENAI-API-KEY").value
```

### 安全檢查清單
- [ ] 確保 .gitignore 包含所有敏感檔案
- [ ] API Keys 存放在環境變數或 Key Vault
- [ ] local.settings.json 不提交到版本控制
- [ ] 使用 Managed Identity 存取 Azure 資源

---

## 協作角色與職責

### 責任分配矩陣 (RACI) - 更新版

| 任務 | Claude Code | WenHao |
|------|-------------|--------|
| 需求分析 | R | A |
| 架構設計 | R | A |
| 文檔撰寫 | R | A |
| Work Item 建立 | R | A |
| 程式碼實作 | R | A |
| 單元測試 | R | A |
| 整合測試 | R | A |
| 部署執行 | C | R |
| 文檔上傳 | I | R |
| 除錯與修復 | R | A |

*R=負責執行, A=最終負責, C=需諮詢, I=需通知*

### 各角色職責說明

**🤖 Claude Code**
- 高層次規劃、架構設計、風險評估
- 生成需求、測試、設計、部署文檔
- Work Items 規劃與建立
- 測試案例設計
- 程式碼實作與測試執行
- **必須依照測試分級策略執行對應層級的測試，全部通過才能回報完成**
- 協助除錯與問題解決

**💻 Cursor (僅作為 IDE)**
- 提供開發環境
- 程式碼編輯介面
- 不使用 Cursor 的 LLM 功能

**👤 WenHao**
- 審核確認文檔和規劃
- 執行部署與環境配置
- 同步文檔到 DevOps Wiki
- 最終決策與品質把關

---

## 開發階段與里程碑

### ✅ 已完成階段（至 2025-07-28）

**V1.0 MVP 完成**：
- **MVP 開發**：所有核心 API 端點實作完成
- **Azure 部署**：成功部署至 Azure Function App
- **CI/CD 設置**：GitHub Actions 自動化測試與部署
- **監控系統**：Application Insights 整合完成
- **效能分析**：完成深度效能分析，發現 Azure Functions 3+ 秒架構開銷

🚀 **已上線的 API 端點**（Azure Functions 版本）：
- `/api/v1/extract-jd-keywords` - 關鍵字提取
- `/api/v1/index-calculation` - 相似度計算
- `/api/v1/index-cal-and-gap-analysis` - 差距分析
- `/api/v1/format-resume` - 履歷格式化
- `/api/v1/tailor-resume` - 履歷優化
- `/api/v1/courses/search` - 課程搜尋

📊 **效能分析成果**（2025-07-28）：
- **根本問題發現**：Azure Functions 架構不適合 API 服務
- **固定開銷識別**：每個請求 3+ 秒開銷，影響所有端點
- **解決方案確定**：Container Apps 架構重構
- **Git Checkpoint**：`v1.0-pre-migration` 標籤已建立

### 🚀 當前階段：Container Apps 架構重構（2025-07-28 開始）

**目標**：5個工作天完成從 Azure Functions 到 Container Apps 的完整遷移

```mermaid
graph TD
    A[2025-07-28: Git Checkpoint] --> B[Day 1: 基礎架構]
    B --> C[Day 2: API 遷移 1-3]
    C --> D[Day 3: API 遷移 4-6]
    D --> E[Day 4: 測試與切換]
    E --> F[Day 5: 優化與文檔]
    
    G[main 分支] --> H[container 分支]
    H --> I[feature/api-xxx 分支]
    I --> J[merge 到 container]
    J --> K[最終 merge 到 main]
```

#### 重構計畫詳情

**Day 1: 基礎架構設置**
- ✅ 建立 `container` 主分支
- [ ] Container Apps 環境創建
- [ ] Dockerfile 與容器配置
- [ ] CI/CD 管道調整
- [ ] 第一個 API (extract-jd-keywords) 遷移

**Day 2-3: API 端點遷移**
- [ ] API 1: `/api/v1/extract-jd-keywords`
- [ ] API 2: `/api/v1/index-calculation`
- [ ] API 3: `/api/v1/index-cal-and-gap-analysis`
- [ ] API 4: `/api/v1/format-resume`
- [ ] API 5: `/api/v1/tailor-resume`
- [ ] API 6: `/api/v1/courses/search`

**Day 4: 整合測試與流量切換**
- [ ] 完整功能測試
- [ ] 效能基準測試
- [ ] 流量分割部署（10% → 50% → 100%）
- [ ] 監控配置驗證

**Day 5: 優化與收尾**
- [ ] 效能調優
- [ ] 文檔更新
- [ ] 舊環境清理
- [ ] 知識轉移

#### 預期成果

| 指標 | 當前 (Functions) | 目標 (Container Apps) | 改善 |
|------|-----------------|---------------------|------|
| P95 響應時間 | 6-11 秒 | 2-8 秒 | 40-91% |
| 並發能力 | < 0.5 QPS | 20-50 QPS | 40-100x |
| 冷啟動時間 | 2-3 秒 | 0.1-0.5 秒 | 80-95% |
| 月成本 | $280 | $250 | -11% |

#### 分支管理策略

```
main (穩定生產版本)
├── v1.0-pre-migration (Functions 版本檢查點)
└── container (Container Apps 主分支)
    ├── feature/api-extract-keywords
    ├── feature/api-index-calculation
    ├── feature/api-gap-analysis
    ├── feature/api-format-resume
    ├── feature/api-tailor-resume
    └── feature/api-courses-search
```

**工作流程**：
1. 每個 API 在獨立 feature 分支開發
2. 完成後 merge 到 `container` 分支
3. `container` 分支持續部署測試
4. 最終從 `container` merge 到 `main`

#### 風險緩解

- **回滾計畫**：保留 Functions 版本 30 天
- **漸進式遷移**：API 逐一遷移，降低風險
- **監控覆蓋**：Application Insights 全程監控
- **效能驗證**：每個 API 遷移後立即效能測試

---

## 任務管理方式

### 使用 GitHub 原生功能

由於團隊規模精簡（Claude Code + WenHao），我們採用 GitHub 的輕量級工作流程：

#### GitHub Issues 分類
- **🐛 Bug**：程式錯誤或異常行為
- **✨ Enhancement**：功能改進或新功能
- **📚 Documentation**：文檔相關任務
- **🚀 Performance**：效能優化相關
- **❓ Question**：需要討論的問題

#### 任務分工
- **Claude Code**：
  - 技術方案設計
  - 程式碼實作
  - 單元測試撰寫
  - 技術文檔
  
- **WenHao**：
  - 需求確認與優先級
  - 測試驗證
  - 部署執行
  - 監控與回饋

### 整合式開發流程

將任務管理與文檔流程整合，確保每個功能都有完整的文檔記錄：

```mermaid
graph LR
    A[GitHub Issue] --> B[Claude 撰寫方案文檔]
    B --> C[docs/drafts/]
    C --> D[WenHao 審核方案]
    D --> E{批准?}
    E -->|否| B
    E -->|是| F[Claude Code 實作]
    F --> G[建立 PR]
    G --> H[測試 & Review]
    H --> I{通過?}
    I -->|否| F
    I -->|是| J[合併到 main]
    J --> K[自動部署]
    K --> L[更新文檔至 docs/published/]
```

### 文檔驅動開發（Documentation-Driven Development）

1. **方案先行**：
   - 每個新功能/修復先寫技術方案
   - 儲存至 `docs/drafts/[功能名稱]_方案_YYYYMMDD.md`
   - 包含：背景、目標、技術方案、預期結果

2. **實作追蹤**：
   - 方案批准後開始實作
   - PR 描述連結到方案文檔
   - 程式碼註解引用文檔決策

3. **知識累積**：
   - 部署成功後，將方案整合到相關文檔
   - `docs/published/` 保存最終實作版本
   - 重要決策記錄到 `.serena/memories/`

### 文檔管理原則

1. **極簡主義**：一個功能一個文檔，避免過度分類
2. **整合內容**：每個文檔包含該功能的需求、設計、實作說明
3. **方案討論**：新功能先在 `drafts/[功能]_方案_YYYYMMDD.md` 討論
4. **知識沉澱**：實作完成後更新到對應的 `features/` 文檔

### 協作原則
1. **No Code Without Doc**：先有文檔，後有程式碼
2. **Review Everything**：方案和程式碼都需審核
3. **Keep It Simple**：流程簡單，但該有的都有
4. **Knowledge Sharing**：重要知識及時記錄

### 檔案管理與命名規範

#### 極簡文檔結構
```yaml
docs/
├── README.md               # API 總覽與快速開始
├── ARCHITECTURE.md         # 架構設計決策
├── API_REFERENCE.md        # 所有 API 的參考文檔
├── DEPLOYMENT.md           # 部署與維運指南
└── features/               # 各功能的詳細說明
    ├── keyword_extraction.md         # /extract-jd-keywords
    ├── index_calculation.md          # /index-calculation
    ├── gap_analysis.md               # /index-cal-and-gap-analysis
    ├── resume_format.md              # /format-resume
    ├── resume_tailoring.md           # /tailor-resume
    └── course_search.md              # /courses/search
```

#### 臨時檔案建立規則
```yaml
# Claude Code 建立臨時檔案時必須遵循
測試腳本:  temp/tests/scripts/test_[功能]_[日期].py
測試日誌:  temp/tests/logs/[功能]_test_[日期].log  
測試結果:  temp/tests/results/[功能]_results_[日期].json
Demo檔案:  temp/demos/html/[功能]_demo_[日期].html
Shell腳本: temp/dev/scripts/[功能]_[用途].sh
實驗代碼:  temp/dev/experiments/[實驗名稱].py
# 筆記請使用 /take-note 指令儲存到 Obsidian
```

#### 命名約定
- **日期格式**: YYYYMMDD (例：20250714)
- **功能描述**: 使用底線分隔 (gap_analysis, api_performance)  
- **包含用途**: test, debug, demo, experiment

#### 檔案存放位置與用途區分

**正式檔案** (版本控制內)：
- `tests/unit/`, `tests/integration/` - 正式測試程式碼
- `docs/` - 所有專案文檔
  - `drafts/` - 討論中的技術方案
  - `features/` - 各功能的完整說明
  - 根目錄的通用文檔（README、ARCHITECTURE 等）

**臨時檔案** (不納入版本控制)：
- `temp/` - 所有臨時性、實驗性的檔案（測試腳本、實驗代碼等）

**開發筆記**：
- 使用 `/take-note` 指令儲存到 Obsidian 知識庫
- 路徑：`/Users/yuwenhao/Library/Mobile Documents/iCloud~md~obsidian/Documents/Root/WenHao/Inbox/Qiuck Note/`

**記憶系統**：
- `.serena/memories/` - Serena MCP 的持久化記憶（API分析、開發進度、架構決策）

---

---

## 斜線指令與知識管理

### 統一使用全域指令
本專案使用全域 `/take-note` 指令記錄所有開發筆記（包括 API 相關）：

#### `/take-note`
記錄重要討論和技術決策到 Obsidian：
- **輸出路徑**: `/Users/yuwenhao/Library/Mobile Documents/iCloud~md~obsidian/Documents/Root/WenHao/Inbox/Qiuck Note/`
- **檔名格式**: `[主題] - YYYY-MM-DD HH-mm.md`
- **自動擷取**: 核心概念、解決方案、關鍵決策、學到的知識
- **API 開發**: 會自動識別 API 相關內容並加上適當標籤

使用範例：
```
/take-note  # 記錄任何重要討論，包括 API 開發
```

#### `/organize-api-notes`
專案特定指令，用於整理 API 開發總結：
- **功能**: 收集並整理專案記錄，生成週期性總結
- **使用時機**: 每週或每個開發階段結束時
- **詳細說明**: 見 `commands/organize-api-notes.md`

### 筆記格式範例
```markdown
# [主題] - YYYY-MM-DD HH:mm

## 📍 Context
- Project: azure_fastapi
- Topic: [討論主題]

## 🎯 Key Points
[重點整理]

## 💡 Solutions/Code
[解決方案或程式碼]

## 📚 Learnings
[學到的知識]

## 🔗 References
[相關連結或檔案]
```

---

## 程式碼品質管理

### Ruff - Python Code Style 檢查工具

**Ruff** 是一個極快速的 Python linter，用於確保程式碼品質和一致性。

#### 核心規則
- **F**: 未使用的變數、import (F401, F841)
- **E**: PEP 8 風格（行長度 88 字元）
- **I**: Import 排序 (I001)
- **UP**: 使用現代 Python 語法 (UP006, UP035)
- **SIM**: 簡化程式碼建議

#### Claude Code 自動檢查流程

每次修改程式碼後，Claude Code 必須：

```bash
# 1. 執行檢查
ruff check src/ tests/ --exclude=legacy,archive

# 2. 如有問題，自動修復
ruff check src/ tests/ --exclude=legacy,archive --fix

# 3. 確認看到
All checks passed!
```

只有確認程式碼風格通過後，才能回報任務完成。

---

## 測試策略與管理

### 程式碼修改測試分級策略 (強制執行！)

**⚠️ 強制要求**：Claude Code 必須根據修改類型執行對應層級的測試，全部通過後才能回報完成！

#### Level 0: Prompt 修改（YAML 檔案）
**適用範圍**：
- 修改 prompt 檔案（src/prompts/**/*.yaml）
- 調整 prompt 內容、格式或參數
- 新增 prompt 版本

**必須通過**：
- ✅ YAML 格式驗證（確認檔案可正確解析）
- ✅ 確認版本命名正確（v[X.Y.Z]-[language].yaml）

**執行時間**：< 5 秒

---

#### Level 1: 程式碼風格檢查（基礎修改）
**適用範圍**：
- 文檔修改（docstring、註解）
- 程式碼格式調整（空白、換行）
- Import 語句調整
- 變數重命名（不影響邏輯）
- 型別標註（type hints）

**必須通過**：
- ✅ `ruff check src/ tests/ --exclude=legacy,archive`
- 如有錯誤：`ruff check src/ tests/ --exclude=legacy,archive --fix`

**執行時間**：< 1 秒

---

#### Level 2: 單元測試（功能修改）
**適用範圍**：
- 修改函數內部邏輯
- 新增輔助函數
- 修改資料模型（models/）
- 修改工具函數（utils/）
- 修改服務層邏輯（services/）
- 修改 prompt 載入邏輯或預設版本

**必須通過**：
- ✅ `ruff check src/ tests/ --exclude=legacy,archive`
- ✅ `pytest tests/unit/test_[相關模組].py -v`
- ✅ 如果新增功能，必須同時新增對應的單元測試

**執行時間**：10-30 秒

---

#### Level 3: 整合測試（API/核心功能修改）
**適用範圍**：
- 修改 API 端點（api/v1/）
- 修改主程式（main.py）
- 修改核心配置（core/config.py）
- 修改中間件（middleware/）
- 修改資料庫相關功能
- 修改外部服務整合（OpenAI、Azure）
- 修改會影響 API 輸出的任何邏輯

**必須通過**：
- ✅ `ruff check src/ tests/ --exclude=legacy,archive`
- ✅ `pytest tests/unit/test_[相關模組].py -v`
- ✅ `pytest tests/integration/test_[相關功能].py -v`
- ✅ 確認沒有破壞現有 API 契約

**執行時間**：1-2 分鐘

---

#### Level 4: Azure Functions 本地測試（預部署驗證）
**適用範圍**：
- 部署前的最終驗證
- 使用真實 API 測試功能是否正常
- 避免 Mock 維護問題，直接使用真實 API
- 模擬 Azure Functions 環境執行

**必須通過**：
- ✅ 安裝 Azure Functions Core Tools：`brew install azure-functions-core-tools@4`
- ✅ 設定真實 API 憑證（.env 檔案）
- ✅ 啟動本地 Azure Functions（port 7071）
- ✅ 執行真實 API 呼叫測試

**執行時間**：< 3 分鐘

**使用時機**：
- 開發階段：使用 Level 0-3
- 預提交時：執行 Level 4 確保部署後正常運作

---

#### 快速決策表

| 修改內容 | 測試層級 | 執行命令 |
|---------|---------|---------|
| Prompt YAML | Level 0 | `./precommit.sh --level-0` |
| 程式碼註解 | Level 1 | `./precommit.sh --level-1` |
| 工具函數邏輯 | Level 2 | `./precommit.sh --level-2 --parallel` |
| API 端點 | Level 3 | `./precommit.sh --level-3 --parallel` |
| Prompt + 預設版本 | Level 0 + 2 | YAML 檢查 + Level 2 測試 |
| 預部署驗證 | Level 4 | `./precommit.sh --level-4` |
| 不確定 | Level 3 | 執行完整測試 |

### 核心測試原則

- **單元測試覆蓋率**: > 80%
- **Bubble.io 相容性**: 文本長度 200-5000 字元（前端已驗證）
- **安全測試**: 使用安全標記避免觸發真實攻擊
- **效能優化**: 使用 pytest-xdist 平行化測試

### 重要測試實踐

1. **邊界測試精簡化**
   ```yaml
   # Bubble.io 前端已驗證
   min_length: 200   # 前端保證
   max_length: 5000  # 前端限制
   
   # 只測試關鍵邊界
   test_cases:
     - 199 chars     # 低於最小值
     - 200 chars     # 剛好最小值
     - 5000 chars    # 剛好最大值
     - 5001 chars    # 略超最大值
   ```

2. **安全測試標記**
   ```python
   # ✅ 使用安全標記
   payload = "SAFE_SQL_TEST_DROP_KEYWORD"
   
   # ❌ 避免真實攻擊碼
   payload = "'; DROP TABLE users; --"  # 可能觸發 IP 封鎖
   ```

3. **測試隔離原則**
   - 使用 pytest fixture 自動清理
   - 每個測試用獨立資料
   - 不依賴執行順序
   - 清理所有建立的資源

4. **明確的錯誤訊息**
   ```python
   # 提供上下文資訊
   assert response.status_code == 200, \
       f"Expected 200 but got {response.status_code}. " \
       f"Response: {response.text[:500]}"
   ```

5. **測試覆蓋率智慧分配**
   ```yaml
   覆蓋率目標:
     核心業務邏輯: 90%+
     API 端點: 100%
     錯誤處理: 80%+
     工具函數: 70%+
   ```

### 測試執行策略

#### 開發階段（針對性測試）
- 只測試**被修改的檔案/模組**
- 快速反饋，專注於當前工作
- 範例：修改 keyword_extraction.py
  ```bash
  ruff check src/services/keyword_extraction.py
  pytest tests/unit/test_keyword_extraction.py -v
  pytest tests/integration/test_api_endpoints.py::test_extract_keywords -v
  ```

#### 提交前（全面性測試）
- 對**整個 codebase** 執行對應層級測試
- 確保沒有破壞其他功能
- 使用 `./run_precommit_tests.sh --level-X`

### 處理 Timeout 限制與效能優化

由於 Bash 工具有 2 分鐘執行限制，採用分段執行 + 平行處理策略：

#### 分段執行 + 平行處理
```bash
# Level 1-2 平行執行（< 1 分鐘）
(ruff check src/ tests/ --exclude=legacy,archive) &
(pytest tests/unit/test_[修改的模組].py -v -n auto) &
wait

# Level 3 分段執行（每段 < 2 分鐘）
# 步驟 1：基礎檢查
ruff check && pytest unit tests
# 步驟 2：整合測試
pytest integration tests
```

### 預提交測試命令

```bash
# 開發階段 - 各層級測試
./precommit.sh --level-0                      # Prompt only (不需要 --parallel)
./precommit.sh --level-1                      # + Code style (不需要 --parallel)
./precommit.sh --level-2 --parallel           # + Unit tests (建議使用 --parallel)
./precommit.sh --level-3 --parallel           # + Integration (建議使用 --parallel)

# 預部署驗證 - Level 4（需要真實 API）
./precommit.sh --level-4                      # Azure Functions 本地測試

# 測試選項
--parallel                                    # 平行執行測試（Level 2-3）
--no-coverage                                 # 跳過覆蓋率報告

# 建議工作流程
# 1. 開發時：執行對應的 Level 0-3
# 2. 提交前：執行 Level 4 確保部署正常
```

### API 文檔測試設計原則

1. **區分端點類型**
   ```python
   # 業務端點 vs 資訊端點
   BUSINESS_ENDPOINTS = ["/extract-jd-keywords", "/tailor-resume"]
   INFO_ENDPOINTS = ["/health", "/version", "/status"]
   
   # 不同類型有不同的測試要求
   if endpoint in BUSINESS_ENDPOINTS:
       assert has_error_responses(endpoint)
       assert has_request_validation(endpoint)
   ```

2. **漸進式品質標準**
   ```yaml
   文檔品質階段:
     MVP:
       example_coverage: 10%
       error_responses: 僅業務端點
       descriptions: 基本描述
     
     v1.0:
       example_coverage: 30%
       error_responses: 所有端點
       descriptions: 詳細描述
     
     v2.0:
       example_coverage: 50%
       error_responses: 詳細錯誤碼
       descriptions: 多語言支援
   ```

3. **實用的測試工具**
   ```bash
   # 檢查 API 文檔完整性
   make check-api-docs
   
   # 生成缺失的文檔報告
   python tools/api_doc_analyzer.py --report missing
   
   # 驗證實際響應符合文檔
   python tools/contract_test.py
   ```

4. **Async 測試最佳實踐**
   ```python
   # 使用 httpx.AsyncClient 而非混用 sync/async
   async with httpx.AsyncClient() as client:
       response = await client.get("/openapi.json")
   
   # 避免不必要的 async fixture
   # 簡單的數據獲取用同步即可
   ```
    job_description: |
    We are looking for an experienced Software Engineer to join our dynamic team.
    The ideal candidate will have strong programming skills in Python and JavaScript,
    extensive experience with cloud technologies including AWS and Azure,
    and excellent problem-solving abilities. You will be working on cutting-edge
    projects in a collaborative environment with opportunities for growth.
    Minimum 5 years of experience required.
   
  # 邊界測試案例  
  job_description: "合理的長文本" * 100  # 約 500 字，不需要測試 5000+ 字
```

### 測試修復流程
```markdown
### [時間] 測試修復進度
**問題**: [描述]
**根因**: [分析]
**修復**: [方案]
**狀態**: 
- HH:MM - 發現問題
- HH:MM - 實施修復
- HH:MM - 驗證通過
```

---

## Azure CLI 命令參考

### 初始設置
```bash
az login
az account set --subscription "5396d388-8261-464e-8ee4-112770674fba"
az configure --defaults group=airesumeadvisorfastapi
az devops configure --defaults organization=https://dev.azure.com/airesumeadvisor project=API
```

### Work Item 管理
```bash
# 建立 Work Item
az boards work-item create \
  --title "[標題]" \
  --type [類型] \
  --project API \
  --assigned-to "[email]"

# 更新狀態
az boards work-item update --id [ID] --state [狀態]

# 查詢 Work Items
az boards query --wiql "[查詢語句]"
```

### Application Insights 查詢
```bash
# 查詢最近的 customEvents
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --analytics-query "customEvents | take 10"

# 查詢不支援語言的 JD preview
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --analytics-query "customEvents | where name == 'UnsupportedLanguageSkipped' | project timestamp, customDimensions.detected_language, customDimensions.jd_preview | take 5"

# 查詢 API 效能指標
az monitor app-insights query \
  --app airesumeadvisorfastapi \
  --analytics-query "customEvents | where name == 'RequestTracked' | summarize avg(todouble(customDimensions.duration_ms)) by tostring(customDimensions.endpoint)"
```

### 常用查詢
```bash
# 進行中項目
"SELECT [System.Id], [System.Title] FROM workitems WHERE [System.State] = 'Active'"

# 本週變更
"SELECT * FROM workitems WHERE [System.ChangedDate] >= @Today-7"
```

---

## 快速參考卡

### 日常開發命令
```bash
# 本地測試
pytest tests/unit/
uvicorn src.main:app --reload

# 預提交測試（開發階段）
./precommit.sh --level-3 --parallel

# 預部署驗證（提交前）
./precommit.sh --level-4

# 測試 Azure Function App
curl -X POST "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords?code=[YOUR_HOST_KEY]" \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Python developer needed", "language": "en"}'

# Git 提交（含 Work Item）
git commit -m "AB#[ID] [說明]"

# 記錄進度
claude "將今日開發成果記錄到 Serena"
```

### 文檔管理命令
```bash
# 生成文檔
claude "為 [模組] 生成需求文檔"

# 建立 Work Items
claude "建立文檔中的 Work Items"

# 檢查待同步
claude "列出待上傳的文檔"
```

### 部署相關命令
```bash
# 環境檢查
python --version

# 部署準備
claude "生成部署檢查清單"

# 配置環境
az functionapp config appsettings set ...
```

---

## Bubble.io API 相容性

### 關鍵約束
- **絕對禁止** 使用 `Optional[Type]` 欄位
- **必須確保** 所有欄位始終存在
- **失敗情況** 回傳空值而非 `null`
- **HTTP 200** 必須使用相同 JSON 結構

### 正確範例
```python
class ApiResponse(BaseModel):
    success: bool
    data: DataModel              # 總是存在
    error: ErrorModel           # 固定結構
    
class DataModel(BaseModel):
    results: List[str] = []     # 失敗時空陣列
    count: int = 0              # 失敗時為 0
    message: str = ""           # 失敗時空字串
```

### Bubble.io + TinyMCE 整合注意事項

**重要**：在 Bubble.io 使用 TinyMCE Rich Text Editor 時，CSS 樣式必須透過 JavaScript 動態注入！

1. **方法**：使用 "When page is loaded" workflow 執行 JavaScript
2. **原因**：Bubble 平台限制，無法直接設置 TinyMCE 內部樣式
3. **實作**：
   ```javascript
   function injectTinyMCEStyles() {
       if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
           var editor = tinymce.activeEditor;
           editor.dom.addStyle('/* CSS 內容 */');
       }
   }
   ```
4. **除錯**：檢查是否有多個 CSS 來源造成衝突（page header vs page loaded）

詳細說明：`.serena/memories/technical_decisions/bubble_tinymce_css_injection.md`

---

## 注意事項

### 重要提醒
1. 敏感資訊絕不提交到版本控制
2. 使用 Azure CLI 存取 DevOps（無需 PAT token）
4. ✅ CI/CD 已完成設置，push to main 自動部署到 Azure
6. 注意 Azure 成本監控

### 環境變數問題解決方案

#### 問題：EMBEDDING_API_KEY environment variable is required

**根本原因**：
1. `embedding_client.py` 使用 `os.getenv()` 直接讀取環境變數
2. `main.py` 沒有載入 `.env` 檔案
3. pydantic_settings 只對 Settings 類別有效，不影響 `os.getenv()`

**解決方案**：

1. **本地開發** - 在啟動前載入 .env：
   ```bash
   # 方法 1: 使用 python-dotenv
   python -c "from dotenv import load_dotenv; load_dotenv()" && uvicorn src.main:app --reload
   
   # 方法 2: 設置環境變數
   export EMBEDDING_API_KEY="your-api-key"
   uvicorn src.main:app --reload
   
   # 方法 3: 在 main.py 添加 (推薦)
   from dotenv import load_dotenv
   load_dotenv()  # 在 import 後立即載入
   ```

2. **生產環境** - Azure Function App 配置：
   ```bash
   az functionapp config appsettings set \
     --name airesumeadvisorfastapi \
     --resource-group airesumeadvisorfastapi \
     --settings EMBEDDING_API_KEY="your-api-key"
   ```

3. **統一解決方案** - 修改 embedding_client.py 使用 settings：
   ```python
   # 改為從 settings 讀取
   from src.core.config import get_settings
   
   def get_azure_embedding_client():
       settings = get_settings()
       return AzureEmbeddingClient(
           endpoint=settings.embedding_endpoint,
           api_key=settings.embedding_api_key
       )
   ```

**建議**：使用方法 3，確保所有環境變數都通過統一的 Settings 管理。



### LLM 呼叫最佳實踐

**核心保護機制**:
- **空白內容檢測** + **重試機制** (3次，指數退避)  
- **預設訊息回傳** + **完整日誌記錄**
- **監控與追蹤** (duration, retry_count, success率)

**實作範例**: `src/services/gap_analysis.py`

**詳細指南**: `docs/published/TEST_BEST_PRACTICES_20250714.md`

### API 測試最佳實踐

**基本原則**: 記錄完整請求/回應內容便於 debug

**必須包含**:
- 完整請求/回應記錄
- 每個欄位實際值統計  
- 失敗時詳細資訊
- 個別回應檔案保存
- 無緩衝輸出 (`flush=True`)

**詳細範例與完整腳本**: `docs/published/TEST_BEST_PRACTICES_20250714.md`

---

## Azure Monitor Workbook 格式注意事項

### Workbook JSON 格式要求

在建立或編輯 Azure Monitor Workbook 時，使用 Advanced Editor 需要注意以下 JSON 格式要求：

1. **查詢字串格式**：
   - `query` 欄位的值必須是**單行字串**（不能有換行符號）
   - 所有 KQL 查詢語句必須在同一行，使用空格分隔不同的子句
   - 範例：
     ```json
     "query": "customEvents | where timestamp {TimeRange} | where name == \"RequestTracked\" | summarize count() by endpoint"
     ```

2. **字串中的引號處理**：
   - 在查詢字串中的引號必須使用反斜線逃脫：`\"`
   - 正確：`"query": "customEvents | where name == \"RequestTracked\""`
   - 錯誤：`"query": "customEvents | where name == "RequestTracked""`

3. **物件格式一致性**：
   - 保持 JSON 物件的格式一致
   - 陣列元素格式：`{"durationMs": 300000}` 而非 `{"durationMs":300000}`

4. **常見錯誤訊息**：
   - `Bad control character in string literal in JSON` - 通常是因為查詢字串中有換行符號
   - 解決方法：將多行查詢合併為單行，使用管道符號 `|` 和空格分隔

### 最佳實踐

1. **先在 Query Explorer 測試**：
   - 在 Application Insights 的 Logs 介面測試 KQL 查詢
   - 確認查詢正確後，再複製到 Workbook

2. **逐步建立 Workbook**：
   - 使用 UI 介面逐個添加元件，而非直接編輯 JSON
   - 每個元件測試無誤後再添加下一個

3. **JSON 編輯技巧**：
   - 使用 JSON 格式化工具先驗證格式
   - 將長查詢先在文字編輯器中編寫為單行
   - 使用查找替換功能處理引號逃脫

---

**文檔版本**: 2.9.1  
**最後更新**: 2025-07-28  
**維護者**: Claude Code + WenHao  
**適用專案**: FHS + FastAPI → Container Apps 重構專案

### v2.9.1 更新內容 (2025-07-28)
- **全面更新過時資訊**：移除過時的 Premium/Standard 環境配置
- **主要環境調整**：Japan East 環境設為主要生產環境
- **技術棧更新**：加入當前架構與目標 Container Apps 架構對比
- **API 端點精簡**：突出 Japan East 環境，其他環境標記為備用
- **安全配置現代化**：更新 Azure OpenAI 配置，環境變數管理策略
- **文檔結構優化**：移除冗餘資訊，聚焦當前重構任務

### v2.9.0 更新內容 (2025-07-28)
- **重大里程碑**：完成 Azure Functions 效能分析，發現 3+ 秒架構開銷
- **架構決策**：決定遷移到 Azure Container Apps
- **Git Checkpoint**：建立 `v1.0-pre-migration` 標籤作為重構前檢查點
- **分支策略更新**：建立 `container` 主分支用於 Container Apps 開發
- **5天重構計畫**：詳細規劃從 Functions 到 Container Apps 的遷移流程
- **更新開發階段與里程碑**：反映當前 Container Apps 重構階段
- **安全改善**：所有測試工具中的硬編碼 Function Keys 改為環境變數

### v2.8.4 更新內容 (2025-07-27)
- 新增 Level 4 測試策略：Azure Functions 本地測試（預部署驗證）
- 更新所有測試相關命令從 `run_precommit_tests.sh` 改為 `precommit.sh`
- 加入 Level 4 測試的詳細說明，解決 Mock 維護問題
- 更新快速決策表，包含 Level 4 測試

### v2.8.3 更新內容 (2025-07-27)
- 新增 Premium Function App 環境資訊（airesumeadvisor-fastapi-premium）
- 包含 Production 和 Staging 兩個部署槽位的完整配置
- 更新所有 API 端點列表，包含完整的 host key
- 標註 Premium 環境可用來取代 Standard 環境

### v2.8.2 更新內容 (2025-07-26)
- 移除 `/take-note-api` 指令，統一使用全域 `/take-note`
- 更新斜線指令章節，簡化為一個通用指令 + 一個整理指令
- 保持簡單，避免重複功能

### v2.8.1 更新內容 (2025-07-26)
- 移除過時的「協作記錄指南」章節（已無 Cursor 協作）
- 更正 features 文檔為 6 個（對應實際的 6 個 API 端點）
- 清理目錄連結和序號

### v2.8.0 更新內容 (2025-07-26)
- 採用極簡主義文檔結構，從複雜的分類改為簡單的功能導向
- 移除過度分類的文檔命名規範（REQ、TEST、DESIGN 等）
- 統一為 4 個通用文檔 + features 目錄下的 6 個功能文檔（對應 6 個 API 端點）

### v2.7.9 更新內容 (2025-07-26)
- 整合任務管理與文檔流程為「整合式開發流程」
- 引入文檔驅動開發（Documentation-Driven Development）概念
- 明確 docs/drafts/（方案討論）和 docs/published/（最終實作）的用途

### v2.7.8 更新內容 (2025-07-26)
- 移除 Azure DevOps Work Items 流程，改用 GitHub Issues
- 簡化文檔工作流程，移除不必要的複雜步驟
- 反映實際團隊規模（Claude Code + WenHao）的協作方式

### v2.7.7 更新內容 (2025-07-26)
- 更新「開發階段與里程碑」章節，反映當前已完成 V1 部署的狀態
- 新增 Phase 5-7 的效能優化與功能增強計畫
- 列出所有已上線的 API 端點清單

### v2.7.6 更新內容 (2025-07-26)
- 統一使用 Obsidian 作為開發筆記系統
- 移除 `temp/dev/notes/`，改用 `/take-note` 指令
- 避免重複的筆記管理系統

### v2.7.5 更新內容 (2025-07-26)
- 釐清 `docs/drafts/` 與 `temp/dev/` 的區別
- 將 `temp/dev/drafts/` 改為 `temp/dev/notes/` 避免混淆
- 明確說明正式檔案與臨時檔案的用途區分

### v2.7.4 更新內容 (2025-07-26)
- 合併「文檔命名規範」和「檔案管理」為單一章節
- 整合正式文檔和臨時檔案的命名規範
- 簡化重複內容，提升可讀性

### v2.7.3 更新內容 (2025-07-26)
- 移動 Code Style 相關內容到「測試策略與管理」之前
- 新增「程式碼品質管理」章節，簡化 Ruff 說明
- 改進文檔結構的邏輯順序

### v2.7.2 更新內容 (2025-07-26)
- 更新 Git 提交規則，明確指出要執行對應層級的預提交測試
- 刪除重複的「LLM Prompt 修改規則」（使用過時的 --no-api 參數）

### v2.7.1 更新內容 (2025-07-26)
- 移除舊的「預提交測試流程」章節（使用過時的 --no-api 和 --real-creds 參數）
- 保留新的「測試執行策略」章節（使用 --level-X 參數）

### v2.7.0 更新內容 (2025-07-26)
- 重構並精簡「測試策略與管理」章節
- 整合「程式碼修改測試分級策略」與舊的測試管理內容
- 新增 Code Style 自動檢查規則章節
- 移除重複的測試執行策略內容
- 優化預提交測試流程說明

### v2.6.0 更新內容 (2025-07-26)
- 更新開發環境資訊：Python 3.11.8 + .venv 虛擬環境
- 新增已部署的生產環境 API 端點列表
- 更新協作模式說明：Claude Code + WenHao
- 更新完整的專案檔案樹結構
- 簡化 RACI 矩陣，移除 Cursor 角色
- 加入 Serena MCP 使用說明

---

## 附錄：核心工作流程

### 1. 分析與設計
```bash
# 分析原始 API
claude "分析 legacy/old_api_code/ 識別重構點"

# 設計架構
claude "設計 [模組] 的 FHS 架構"

# 生成文檔
claude "生成含 Work Items 的設計文檔"
```

### 2. 開發與測試
```bash
# 實作功能
@docs/published/design/DESIGN_[模組].md
"基於設計文檔實作功能"

# 執行測試
pytest tests/unit/test_[模組].py

# 整合測試
pytest tests/integration/ --env=local
```

### 3. 部署與維運
```bash
# 手動部署
claude "生成 Azure 部署步驟"

# 配置環境變數
az functionapp config appsettings set \
  --name airesumeadvisorfastapi \
  --resource-group airesumeadvisorfastapi \
  --settings KEY=VALUE

# 查看 Function App 日誌
az functionapp logs --name airesumeadvisorfastapi --type application

# 驗證部署
claude "生成部署驗證清單"
```

### 4. 持續改進
```bash
# 技術債務評估
claude "評估當前技術債務"

# 效能優化
claude "分析效能瓶頸並提出優化方案"

# 文檔更新
claude "更新相關文檔確保一致性"
```

---

## Claude Code Sub-agents 參考

Claude Code 提供 37 個專門的 sub-agents 來協助各種開發任務。

- **快速參考**: [`.claude/AGENTS_QUICK_REFERENCE.md`](./.claude/AGENTS_QUICK_REFERENCE.md)
- **完整文檔**: `/Users/yuwenhao/.claude/agents/`

### 🔴 主動觸發 Agents

以下 agents 應在特定情況下自動觸發，無需用戶明確要求：

| Agent | 觸發時機 | 用途 |
|-------|---------|------|
| `whimsy-injector` | UI/UX 變更後 | 為介面添加愉悅元素 |
| `test-writer-fixer` | 程式碼修改後 | 確保測試通過 |
| `project-shipper` | 接近發布里程碑 | 協調發布流程 |
| `studio-producer` | 團隊協調需求出現 | 跨團隊資源管理 |
| `experiment-tracker` | 實驗開始或修改時 | A/B 測試追蹤 |
| `studio-coach` | 複雜任務或 agent 遇困時 | Agent 績效指導 |

### 📊 常用 Agents 快速選擇

**開發任務**：
- 複雜研究 → `general-purpose`
- 前端開發 → `frontend-developer`
- 後端架構 → `backend-architect`
- 快速原型 → `rapid-prototyper`

**部署與維運**：
- CI/CD 設置 → `devops-automator`
- 效能測試 → `performance-benchmarker`
- 系統維護 → `infrastructure-maintainer`

**產品與策略**：
- 衝刺規劃 → `sprint-prioritizer`
- 市場研究 → `trend-researcher`
- 用戶反饋 → `feedback-synthesizer`

### 使用範例

```python
# 單一 agent 執行
Task(
    description="分析 Container Apps 架構",
    prompt="分析當前 container 分支的架構設計並提供改進建議",
    subagent_type="backend-architect"
)

# 並發執行多個 agents（推薦）
# 在單一訊息中使用多個 Task 調用以提升效率
```
