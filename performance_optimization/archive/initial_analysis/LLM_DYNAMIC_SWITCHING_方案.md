# LLM 動態切換技術方案

**日期**: 2025-01-27  
**作者**: Claude Code + WenHao  
**狀態**: 草案

## 背景

目前系統使用固定的 LLM 模型（GPT-4o-2），但我們需要：
1. 在 staging 環境測試 GPT-4.1 mini 的效能
2. 能夠根據不同 API 的需求選擇最適合的模型
3. 未來支援更多模型的擴展性

## 目標

1. **短期**：支援 staging 環境使用 GPT-4.1 mini 進行效能測試
2. **中期**：實現不同 API 使用不同模型的能力
3. **長期**：建立完整的模型選擇和監控機制

## 技術方案：混合方案

### 架構設計

```
┌─────────────────┐     ┌──────────────────┐
│   API Request   │────▶│  LLM Factory     │
└─────────────────┘     └──────────────────┘
                               │
                        ┌──────┴──────┐
                        ▼             ▼
                 ┌────────────┐ ┌────────────┐
                 │ GPT-4o-2   │ │GPT-4.1 mini│
                 └────────────┘ └────────────┘
```

### 核心組件

1. **LLM Factory (`src/services/llm_factory.py`)**
   - 統一的 LLM 客戶端建立介面
   - 支援多種選擇策略（環境變數、請求參數、HTTP Header）
   - 自動 fallback 機制

2. **配置管理 (`src/core/config.py`)**
   - 新增 LLM 模型映射配置
   - Feature flags 控制

3. **監控整合**
   - 記錄每個請求使用的模型
   - 效能和成本追蹤

### 實作細節

#### 1. 環境變數配置
```yaml
# 每個 API 的模型配置
LLM_MODEL_KEYWORDS: gpt41-mini
LLM_MODEL_GAP_ANALYSIS: gpt4o-2
LLM_MODEL_RESUME_FORMAT: gpt4o-2
LLM_MODEL_RESUME_TAILOR: gpt41-mini
LLM_MODEL_DEFAULT: gpt4o-2

# Feature flags
ENABLE_LLM_MODEL_OVERRIDE: true
ENABLE_LLM_MODEL_HEADER: true
```

#### 2. 優先級規則
1. 請求參數（最高優先級）
2. HTTP Header (`X-LLM-Model`)
3. 環境變數配置
4. 預設值

#### 3. API 整合範例
```python
# 使用 factory 方法
from src.services.llm_factory import get_llm_client_smart

class KeywordExtractionServiceV2:
    def __init__(self, request_model=None, headers=None):
        self.openai_client = get_llm_client_smart(
            api_name="keywords",
            request_model=request_model,
            headers=headers
        )
```

## 實施計畫

### Phase 1: 基礎建設（第 1 週）
- [ ] 實作 `llm_factory.py`
- [ ] 更新 `config.py`
- [ ] 單元測試

### Phase 2: API 整合（第 2 週）
- [ ] 整合關鍵字提取 API
- [ ] 整合履歷優化 API
- [ ] 整合測試

### Phase 3: 監控與優化（第 3-4 週）
- [ ] 實作監控和日誌
- [ ] 效能測試
- [ ] 成本分析

## 風險評估

1. **相容性風險**：確保不影響現有 API 功能
   - 緩解：保留現有介面，新功能為選用
   
2. **效能風險**：模型切換可能增加延遲
   - 緩解：實作客戶端快取機制

3. **成本風險**：不當使用可能增加成本
   - 緩解：實作配額和監控

## 成功指標

1. **功能指標**
   - 所有 API 支援模型選擇
   - 零停機時間部署

2. **效能指標**
   - GPT-4.1 mini 回應時間 < 2 秒（P95）
   - 模型選擇開銷 < 10ms

3. **成本指標**
   - 關鍵字提取 API 成本降低 50%+

## 決策點

需要團隊決定：
1. 是否在生產環境啟用請求層級的模型選擇？
2. 是否需要實作配額限制？
3. 監控數據保留期限？

## 附錄

- [詳細設計文檔](/temp/dev/LLM_SWITCHING_PROPOSAL.md)
- [配置範例](/temp/dev/LLM_CONFIGURATION_EXAMPLES.md)