# 架構設計

## 概述

本專案採用 FHS (Functional Hierarchy Structure) 架構模式，將功能邏輯組織成清晰的層次結構。

## 架構原則

### 1. 功能分層
```
src/
├── api/          # API 端點定義
├── services/     # 業務邏輯層
├── core/         # 核心功能（配置、錯誤處理）
├── models/       # 資料模型
├── prompts/      # LLM prompts
└── utils/        # 工具函數
```

### 2. 關注點分離
- **API 層**：處理 HTTP 請求/回應
- **Service 層**：實作業務邏輯
- **Core 層**：提供基礎設施支援

### 3. 相依性方向
- API → Services → Core/Utils
- 避免循環相依

## 技術選型

### 核心框架
- **FastAPI**：現代化、高效能的 Python web framework
- **Pydantic**：資料驗證與序列化
- **Azure Functions**：Serverless 部署平台

### AI/ML 整合
- **Azure OpenAI**：GPT-4 模型存取
- **Embedding API**：語義相似度計算
- **LangChain**：LLM 應用開發框架

### 資料存儲
- **PostgreSQL + pgvector**：課程資料庫與向量搜尋
- **Azure Blob Storage**：大型檔案儲存（未來擴展）

## 設計決策

### 1. Prompt 版本管理

#### 目錄結構
```yaml
prompts/
└── [task]/                    # 任務名稱（如 keyword_extraction）
    ├── v1.0.0.yaml           # 基礎版本
    ├── v1.0.0-zh-TW.yaml    # 語言特定版本
    ├── v1.1.0.yaml           # 更新版本
    └── v2.0.0.yaml           # 主要版本更新
```

#### Prompt Manager 架構
- **SimplePromptManager**：處理 prompt 載入與版本選擇
- **BilingualPromptManager**：處理多語言 prompt 選擇
- **版本解析**：自動選擇最新版本或指定版本
- **快取機制**：避免重複載入

#### 優勢
- 支援多版本並存，便於 A/B 測試
- 語言特定優化（如 `v1.1.0-zh-TW.yaml`）
- 版本回滾機制
- 統一的 YAML 格式配置

### 2. 錯誤處理策略
- 統一的錯誤回應格式
- 詳細的錯誤日誌
- 使用者友善的錯誤訊息

### 3. 效能優化
- 非同步處理
- 連線池管理
- 快取策略（計劃中）

## 安全考量

### API 安全
- Host key 認證（Azure Functions）
- 輸入驗證與清理
- Rate limiting（透過 Azure）

### 資料保護
- 敏感資料不記錄
- 環境變數管理 secrets
- HTTPS only

## 監控與可觀測性

### Application Insights
- 請求追蹤
- 效能指標
- 自訂事件記錄

### 健康檢查
- `/health` endpoint
- 依賴服務檢查
- 版本資訊暴露

## 擴展性設計

### 水平擴展
- Stateless 設計
- Azure Functions 自動擴展
- 資料庫連線池

### 垂直擴展
- 可調整的 Function App plan
- 記憶體配置優化

## 部署架構

```
GitHub (main) 
    ↓ (push)
GitHub Actions
    ↓ (deploy)
Azure Function App
    ↓ (serve)
Bubble.io Frontend
```

## 未來演進

### Phase 5 優化重點
1. **快取層**：Redis 整合
2. **批次處理**：大量請求優化
3. **監控增強**：自訂 dashboard
4. **多區域部署**：降低延遲

### 長期規劃
- GraphQL API 支援
- WebSocket 即時通訊
- 微服務拆分（如需要）