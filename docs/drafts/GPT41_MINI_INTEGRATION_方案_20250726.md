# GPT-4.1 mini 整合方案

**日期**: 2025-07-26  
**作者**: Claude Code  
**狀態**: 待審核  

## 背景

根據 Azure Application Insights 的實際監控數據，`/api/v1/extract-jd-keywords` API 的平均回應時間約 5.9 秒，主要瓶頸為：
- 網路延遲：East Asia (Function App) → Sweden Central (GPT-4o-2)
- LLM 處理時間：GPT-4o-2 模型處理

為了達成 P95 < 4 秒的效能目標，我們需要：
1. 減少網路延遲：使用更近的資料中心
2. 降低成本：GPT-4.1 mini 提供 90% 成本節省

## 目標

1. 將關鍵字提取 API 的預設模型從 GPT-4o-2 (Sweden Central) 切換到 GPT-4.1 mini (Japan East)
2. 保持向後相容性，允許通過配置切換回 GPT-4o-2
3. 確保關鍵字提取品質不受影響
4. 達成 P95 回應時間 < 4 秒的目標

## 技術方案

### 1. 新增 GPT-4.1 mini 客戶端

已實作 `src/services/openai_client_gpt41.py`：
- 支援 GPT-4.1 mini 的專用客戶端
- 實作重試機制和錯誤處理
- 相容現有的 AzureOpenAIClient 介面

### 2. 修改 KeywordExtractionServiceV2

在 `src/services/keyword_extraction_v2.py` 中新增：

```python
def __init__(
    self,
    openai_client: AzureOpenAIClient | None = None,
    prompt_version: str = "latest",
    enable_cache: bool = True,
    cache_ttl_minutes: int = 60,
    enable_parallel_processing: bool = True,
    use_gpt41_mini: bool = True  # 新增參數
):
    """Initialize the service with unified prompt management."""
    super().__init__()
    
    # Core services - Use GPT-4.1 mini if specified
    if openai_client:
        self.openai_client = openai_client
    elif use_gpt41_mini:
        # Use GPT-4.1 mini Japan East for better performance
        from src.services.openai_client_gpt41 import get_gpt41_mini_client
        try:
            self.openai_client = get_gpt41_mini_client()
            self.logger.info("Using GPT-4.1 mini Japan East for keyword extraction")
        except Exception as e:
            self.logger.warning(f"Failed to initialize GPT-4.1 mini client: {e}. Falling back to GPT-4o-2")
            self.openai_client = get_azure_openai_client()
    else:
        self.openai_client = get_azure_openai_client()
```

### 3. API 端點配置

修改 `src/api/v1/keyword_extraction.py`：

```python
service = get_keyword_extraction_service_v2(
    prompt_version=request.prompt_version,
    enable_cache=True,
    cache_ttl_minutes=60,
    enable_parallel_processing=True,
    use_gpt41_mini=settings.use_gpt41_mini_for_keywords  # 從配置讀取
)
```

### 4. 環境變數配置

在 `src/core/config.py` 中新增：

```python
# GPT-4.1 mini Japan East Configuration
gpt41_mini_japaneast_endpoint: str = Field(...)
gpt41_mini_japaneast_api_key: str = Field(...)
gpt41_mini_japaneast_deployment: str = Field(default="gpt-4-1-mini-japaneast", ...)
gpt41_mini_japaneast_api_version: str = Field(default="2025-01-01-preview", ...)

# Feature flag
use_gpt41_mini_for_keywords: bool = Field(default=True, ...)
```

### 5. 降級機制

如果 GPT-4.1 mini 初始化失敗，自動降級到 GPT-4o-2，確保服務可用性。

## 實施步驟

1. **建立功能分支**：`feature/gpt41-mini-integration`
2. **實作程式碼修改**：
   - ✅ 更新 `keyword_extraction_v2.py`
   - ✅ 更新 API 端點
   - ✅ 修復程式碼風格問題
3. **測試**：
   - ✅ 單元測試
   - ✅ 整合測試
   - ✅ 效能測試
4. **文檔更新**：
   - 更新 API 文檔
   - 更新部署指南
5. **部署**：
   - 更新 Azure Function App 環境變數
   - 監控效能指標

## 測試計畫

### 1. 功能測試
- [x] GPT-4.1 mini 客戶端基本功能
- [x] 關鍵字提取服務整合
- [x] API 端點正確使用新模型
- [x] 降級機制運作正常

### 2. 效能測試
- [x] 本地測試：~3.5 秒（GPT-4o-2 和 GPT-4.1 mini 相近）
- [ ] 生產環境測試：預期 < 4 秒（網路延遲大幅降低）

### 3. 品質測試
- [x] 關鍵字提取品質與 GPT-4o-2 相當
- [x] 支援英文和繁體中文

## 風險評估

1. **品質風險**：低 - 測試顯示 GPT-4.1 mini 的關鍵字提取品質良好
2. **相容性風險**：低 - 保留降級機制和配置開關
3. **部署風險**：中 - 需要更新生產環境配置

## 預期成果

1. **效能提升**：
   - 網路延遲：顯著降低（Sweden → Japan 的距離優勢）
   - 總回應時間：從 ~5.9 秒降至 < 4 秒

2. **成本節省**：
   - API 使用成本降低 90%

3. **用戶體驗**：
   - 回應速度顯著提升
   - 保持相同的功能和品質

4. **效能驗證**：
   - 部署後可通過 API 參數動態切換模型（GPT-4o-2 vs GPT-4.1 mini）
   - 支援 side-by-side 效能比較測試
   - 方便 A/B 測試和效能監控

## 回滾計畫

如果出現問題，可以通過以下方式快速回滾：

1. **配置回滾**：設置 `USE_GPT41_MINI_FOR_KEYWORDS=false`
2. **程式碼回滾**：revert 相關 commits
3. **無需修改客戶端**：API 介面保持不變

## 決策記錄

1. **為什麼選擇 GPT-4.1 mini？**
   - 成本效益最佳（90% 成本節省）
   - Japan East 資料中心距離最近
   - 效能測試顯示品質滿足需求

2. **為什麼保留 GPT-4o-2？**
   - 作為降級選項
   - 某些特殊場景可能需要更強大的模型

## 審核檢查清單

- [ ] 程式碼符合 FHS 架構
- [ ] 測試覆蓋率 > 80%
- [ ] 文檔完整
- [ ] 環境變數已配置
- [ ] 回滾計畫可行