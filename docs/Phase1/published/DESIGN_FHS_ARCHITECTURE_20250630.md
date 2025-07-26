# DESIGN_FHS_ARCHITECTURE_20250630: FHS + FastAPI 架構設計文檔

## 文檔資訊
- **文檔編號**: DESIGN_FHS_ARCHITECTURE_20250630
- **版本**: 1.0
- **建立日期**: 2025-06-30
- **作者**: Claude Code (Opus 4)
- **狀態**: 已發布
- **相關文檔**: CLAUDE.md, REQ_KEYWORD_EXTRACTION_20250630, DESIGN_PROMPT_MANAGEMENT_20250630, DESIGN_LANGUAGE_DETECTION_20250702

## Work Items 規劃

### Epic
- **[#333](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/333)**: Azure FastAPI 系統遷移
  - **Owner**: Claude
  - **描述**: 將現有 Azure Functions API 遷移至 FHS + FastAPI 架構
  - **優先級**: 高

### Feature
- **[#335](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/335)**: FHS 架構實作
  - **Owner**: Claude
  - **父項**: [#333](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/333)
  - **描述**: 建立 FHS + FastAPI 基礎架構
  - **優先級**: 高

### Tasks
- [ ] **[#339](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/339)**: 建立專案目錄結構 - Owner: Cursor - 預估: 2h
- [ ] **[#354](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/354)**: 實作核心配置模組 - Owner: Cursor - 預估: 4h
- [ ] **[#355](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/355)**: 建立依賴注入系統 - Owner: Cursor - 預估: 3h
- [ ] **[#356](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/356)**: 實作錯誤處理機制 - Owner: Cursor - 預估: 3h
- [ ] **[#357](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/357)**: 建立回應模型基礎 - Owner: Cursor - 預估: 2h
- [ ] **[#358](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/358)**: Azure Functions 整合 - Owner: Cursor - 預侐: 4h

## 架構概述

FHS (Functional Hierarchy Structure) 是一種強調功能分層和職責分離的架構模式。結合 FastAPI 框架，我們建立一個清晰、可維護、易擴展的 API 系統。

### 核心原則

1. **單一職責原則**: 每個模組只負責一個特定功能
2. **依賴倒置原則**: 高層模組不依賴低層模組，都依賴抽象
3. **開放封閉原則**: 對擴展開放，對修改封閉
4. **介面隔離原則**: 使用專門的介面而非通用介面

## 目錄結構設計

```
azure_fastapi/
├── src/
│   ├── api/                    # API 層 - 路由和端點定義
│   │   ├── __init__.py
│   │   ├── v1/                 # API 版本管理
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/     # 端點實作
│   │   │   │   ├── __init__.py
│   │   │   │   ├── keyword_extraction.py
│   │   │   │   ├── similarity.py
│   │   │   │   └── ...
│   │   │   └── router.py      # 路由聚合
│   │   └── deps.py            # API 依賴項
│   │
│   ├── core/                   # 核心層 - 配置和共用功能
│   │   ├── __init__.py
│   │   ├── config.py          # 應用配置
│   │   ├── constants.py       # 常數定義
│   │   ├── exceptions.py      # 自定義例外
│   │   ├── logging.py         # 日誌配置
│   │   ├── security.py        # 安全相關
│   │   └── simple_prompt_manager.py  # Prompt 管理器
│   │
│   ├── models/                 # 模型層 - 資料模型定義
│   │   ├── __init__.py
│   │   ├── base.py           # 基礎模型
│   │   ├── requests/         # 請求模型
│   │   │   ├── __init__.py
│   │   │   └── keyword_extraction.py
│   │   ├── responses/        # 回應模型（Bubble.io 相容）
│   │   │   ├── __init__.py
│   │   │   ├── base.py       # 統一回應格式
│   │   │   └── keyword_extraction.py
│   │   ├── domain/           # 領域模型
│   │   │   ├── __init__.py
│   │   │   └── keyword.py
│   │   └── prompt_config.py   # Prompt 配置模型
│   │
│   ├── services/              # 服務層 - 業務邏輯
│   │   ├── __init__.py
│   │   ├── base.py           # 服務基類
│   │   ├── keyword_extraction/
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py  # 提取邏輯
│   │   │   ├── parser.py     # LLM 回應解析
│   │   │   └── standardizer.py # 標準化處理
│   │   ├── language_detection/
│   │   │   ├── __init__.py
│   │   │   ├── detector.py   # 語言檢測邏輯
│   │   │   ├── validator.py  # 語言驗證
│   │   │   └── bilingual_prompt_manager.py # 雙語 Prompt 管理
│   │   └── openai/           # 外部服務整合
│   │       ├── __init__.py
│   │       └── client.py
│   │
│   ├── repositories/          # 儲存層 - 資料存取（未來擴充）
│   │   ├── __init__.py
│   │   └── base.py
│   │
│   ├── utils/                 # 工具層 - 輔助功能
│   │   ├── __init__.py
│   │   ├── validators.py     # 驗證工具
│   │   ├── formatters.py     # 格式化工具
│   │   └── helpers.py        # 通用輔助函數
│   │
│   ├── prompts/                # Prompt 版本檔案
│   │   ├── keyword_extraction/
│   │   │   ├── v1.0.0.yaml     # 英文版本
│   │   │   ├── v1.0.1.yaml     # 英文版本
│   │   │   ├── v1.2.0.yaml     # 英文優化版本
│   │   │   ├── v1.2.0-zh-TW.yaml # 繁體中文版本
│   │   │   └── latest.yaml     # 符號連結
│   │   └── standardization/
│   │       ├── english_dictionary.yaml
│   │       └── traditional_chinese_dictionary.yaml
│   │
│   └── main.py               # FastAPI 應用入口
│
├── azure/                     # Azure Functions 相關
│   ├── function_app.py       # Azure Function 入口
│   ├── function.json         # Function 配置
│   └── host.json            # Host 配置
│
├── tests/                    # 測試
│   ├── unit/                # 單元測試
│   ├── integration/         # 整合測試
│   └── conftest.py         # 測試配置
│
└── scripts/                 # 腳本
    ├── setup_dev.sh        # 開發環境設置
    └── deploy.sh           # 部署腳本
```

## 層級職責定義

### 1. API 層 (`src/api/`)
::: mermaid
graph TD
    A[API Layer] --> B[接收 HTTP 請求]
    A --> C[驗證請求資料]
    A --> D[調用服務層]
    A --> E[格式化回應]
    A --> F[處理 HTTP 錯誤]
:::

**職責**：
- 定義 API 端點和路由
- 處理 HTTP 請求和回應
- 請求資料驗證
- 依賴注入管理
- OpenAPI 文檔生成

### 2. 核心層 (`src/core/`)
::: mermaid
graph TD
    A[Core Layer] --> B[應用配置管理]
    A --> C[共用常數定義]
    A --> D[全域例外處理]
    A --> E[日誌系統配置]
    A --> F[安全機制實作]
    A --> G[Prompt 版本管理]
:::

**職責**：
- 應用程式配置管理
- 跨層級共用功能
- 全域錯誤處理策略
- 系統級別的工具

### 3. 模型層 (`src/models/`)
::: mermaid
graph TD
    A[Model Layer] --> B[Request Models]
    A --> C[Response Models]
    A --> D[Domain Models]
    B --> E[Pydantic 驗證]
    C --> F[Bubble.io 相容格式]
    D --> G[業務實體定義]
:::

**職責**：
- 定義資料結構
- 請求/回應模型驗證
- 確保 Bubble.io 相容性
- 領域模型封裝

### 4. 服務層 (`src/services/`)
::: mermaid
graph TD
    A[Service Layer] --> B[業務邏輯實作]
    A --> C[外部服務整合]
    A --> D[資料轉換處理]
    A --> E[錯誤處理邏輯]
    A --> F[交易管理]
    A --> G[Prompt 整合調用]
    A --> H[語言檢測服務]
    A --> I[多語言標準化]
:::

**職責**：
- 核心業務邏輯實作
- 協調多個元件
- 外部 API 整合
- 資料轉換和處理
- 語言檢測和驗證
- 多語言資源管理

### 5. 工具層 (`src/utils/`)
**職責**：
- 通用輔助功能
- 格式化和驗證工具
- 不含業務邏輯的純功能

### 6. Prompt 管理 (`src/prompts/` & `src/core/simple_prompt_manager.py`)
**職責**：
- 管理不同版本的 prompt 配置
- 提供 prompt 載入和快取機制
- 支援 LLM 參數配置管理
- 實現簡單的變數替換功能
- 確保 prompt 版本的一致性和可追蹤性

## 統一回應格式設計

基於 Bubble.io 相容性要求，所有 API 回應必須使用統一的 Schema：

```python
# src/models/responses/base.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class ErrorDetail(BaseModel):
    """錯誤詳情模型"""
    has_error: bool = False
    code: str = ""
    message: str = ""
    details: str = ""

class WarningDetail(BaseModel):
    """警告詳情模型"""
    has_warning: bool = False
    message: str = ""
    suggestion: str = ""

class BaseResponse(BaseModel):
    """基礎回應模型 - 所有 API 回應都繼承此模型"""
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
    error: ErrorDetail = Field(default_factory=ErrorDetail)
    warning: WarningDetail = Field(default_factory=WarningDetail)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## 依賴注入設計

使用 FastAPI 的依賴注入系統管理組件依賴：

```python
# src/api/deps.py
from typing import Generator
from src.core.config import Settings
from src.services.openai.client import OpenAIClient

def get_settings() -> Settings:
    """獲取應用設定"""
    return Settings()

def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAIClient:
    """獲取 OpenAI 客戶端"""
    return OpenAIClient(
        api_key=settings.openai_api_key,
        endpoint=settings.llm2_endpoint
    )
```

## 錯誤處理機制

### 1. 自定義例外階層
```python
# src/core/exceptions.py
class AppException(Exception):
    """應用基礎例外"""
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationException(AppException):
    """驗證例外"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")

class ExternalServiceException(AppException):
    """外部服務例外"""
    def __init__(self, message: str, service: str):
        super().__init__(message, f"{service.upper()}_ERROR")
```

### 2. 全域錯誤處理器
```python
# src/api/v1/error_handlers.py
from fastapi import Request
from src.models.responses.base import BaseResponse, ErrorDetail

async def app_exception_handler(request: Request, exc: AppException):
    """處理應用例外"""
    return JSONResponse(
        status_code=400,
        content=BaseResponse(
            success=False,
            error=ErrorDetail(
                has_error=True,
                code=exc.code,
                message=exc.message
            )
        ).dict()
    )
```

## 配置管理

使用 Pydantic Settings 進行類型安全的配置管理：

```python
# src/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 應用配置
    app_name: str = "Azure FastAPI"
    api_version: str = "v1"
    debug: bool = False
    
    # Azure OpenAI 配置
    llm2_endpoint: str
    llm2_api_key: str
    embedding_endpoint: str
    openai_api_key: str
    
    # 關鍵字提取配置
    keyword_extraction_seed1: int = 42
    keyword_extraction_seed2: int = 43
    keyword_extraction_min_keywords: int = 12
    keyword_extraction_max_keywords: int = 22
    
    # Sigmoid 參數
    sigmoid_x0: float = 0.373
    sigmoid_k: float = 15.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
```

## Azure Functions 整合

### 1. Function App 配置
```python
# azure/function_app.py
import azure.functions as func
from fastapi import FastAPI
from src.main import create_app

# 創建 FastAPI 應用
app = create_app()

# Azure Function 處理器
async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiRequest(app).handle_async(req, context)
```

### 2. Host 配置
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  },
  "functionTimeout": "00:05:00"
}
```

## 開發指南

### 1. 新增 API 端點
1. 在 `src/models/requests/` 建立請求模型
2. 在 `src/models/responses/` 建立回應模型（繼承 BaseResponse）
3. 在 `src/services/` 實作業務邏輯
4. 在 `src/api/v1/endpoints/` 建立端點
5. 在 `src/api/v1/router.py` 註冊路由

### 2. 測試策略
- **單元測試**: 測試個別組件功能
- **整合測試**: 測試 API 端點完整流程
- **Schema 測試**: 驗證 Bubble.io 相容性

### 3. 部署流程
1. 本地測試通過
2. 建立部署套件
3. 設定環境變數
4. 部署至 Azure Functions
5. 驗證線上功能

## 語言檢測服務擴展（v2.0 計劃）

### 架構擴展

基於現有 FHS 架構，v2.0 將新增語言檢測功能以支援雙語關鍵字提取：

#### 新增服務組件
```
src/services/language_detection/
├── detector.py                 # 語言檢測核心邏輯
├── validator.py               # 語言支援驗證
└── bilingual_prompt_manager.py # 雙語 Prompt 管理
```

#### 多語言資源管理
```
src/prompts/
├── keyword_extraction/
│   ├── v1.2.0.yaml           # 英文版本
│   └── v1.2.0-zh-TW.yaml     # 繁體中文版本
└── standardization/
    ├── english_dictionary.yaml
    └── traditional_chinese_dictionary.yaml
```

### 服務整合模式

語言檢測服務將與現有關鍵字提取服務透過依賴注入進行整合：

```python
class BilingualKeywordExtractionService(KeywordExtractionService):
    def __init__(
        self,
        language_detector: LanguageDetectionService,
        bilingual_prompt_manager: BilingualPromptManager,
        multilingual_standardizer: MultilingualStandardizer
    ):
        super().__init__()
        self.language_detector = language_detector
        self.bilingual_prompt_manager = bilingual_prompt_manager
        self.multilingual_standardizer = multilingual_standardizer
```

### FHS 原則遵循

新增的語言檢測功能完全符合 FHS 架構原則：
- **單一職責**: 語言檢測服務只負責語言識別
- **依賴倒置**: 通過介面定義進行整合
- **開放封閉**: 可輕易擴展支援新語言
- **介面隔離**: 提供專門的語言檢測介面

### 相關設計文檔
- [DESIGN_LANGUAGE_DETECTION_20250702](./DESIGN_LANGUAGE_DETECTION_20250702.md) - 完整語言檢測系統設計

## 技術決策記錄

### 1. 為什麼選擇 FHS 架構？
- 清晰的職責分離
- 易於測試和維護
- 符合大型專案需求
- 便於團隊協作

### 2. 為什麼不使用 Optional 類型？
- Bubble.io 需要固定的 JSON Schema
- 避免前端處理 null 值的複雜性
- 提高 API 的可預測性

### 3. 為什麼使用依賴注入？
- 便於測試（可注入 mock）
- 解耦組件依賴
- 提高程式碼重用性

---

**文檔結束**

*本設計文檔遵循 CLAUDE.md 工作流程制定，待審核通過後將建立對應的 Work Items。*