# 關鍵字提取 API 詳細設計文檔（最終整合版）

**文檔編號**: DESIGN_KEYWORD_EXTRACTION_20250701_FINAL  
**版本**: 2.0  
**建立日期**: 2025-07-01  
**作者**: Claude Code  
**狀態**: 已發布  
**相關文檔**: REQ_KEYWORD_EXTRACTION_20250630, DESIGN_FHS_ARCHITECTURE_20250630, DESIGN_PROMPT_MANAGEMENT_20250630, TEST_CONSISTENCY_KPI_20250701, DESIGN_LANGUAGE_DETECTION_20250702

---

## Work Items 規劃

### 實作任務
- [x] **[#339](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/339)**: 建立專案目錄結構 - Owner: Cursor - 完成
- [x] **[#340](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/340)**: 實作 OpenAI 客戶端 - Owner: Cursor - 完成
- [x] **[#343](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/343)**: 實作關鍵字提取核心邏輯 - Owner: Cursor - 完成
- [x] **[#344](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/344)**: 實作 LLM 回應解析器 - Owner: Cursor - 完成
- [ ] **[#345](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/345)**: 建立標準化字典和規則 - Owner: Cursor - 預估: 5h
- [x] **[#346](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/346)**: 建立請求/回應模型 - Owner: Cursor - 完成
- [x] **[#347](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/347)**: 建立 API 端點 - Owner: Cursor - 完成
- [x] **[#348](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/348)**: 撰寫單元測試 - Owner: Cursor - 完成
- [ ] **[#349](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/349)**: 撰寫整合測試 - Owner: Cursor - 預估: 4h
- [x] **[#341](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/341)**: 設定 Azure 環境變數 - Owner: WenHao - 完成
- [ ] **[#350](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/350)**: 配置 Azure Functions - Owner: WenHao - 預估: 2h

### 一致性測試任務
- [x] **[#394](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/394)**: Epic: 關鍵字提取一致性測試 - Owner: Claude - 完成
- [x] **[#395](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/395)**: Feature: 一致性 KPI 測試實作 - Owner: Claude - 完成
- [x] **[#396](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/396)**: Test Case: 短文本一致性測試 - Owner: Claude/Cursor - 完成
- [x] **[#397](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/397)**: Test Case: 長文本一致性測試 - Owner: Claude/Cursor - 完成
- [x] **[#398](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/398)**: Test Case: 兩次測試相同機率驗證 - Owner: Claude/Cursor - 完成

---

## 演算法更新概述（v2.0）

### 主要變更

1. **最大返回數限制**：新增 16 個關鍵字的硬性上限
2. **交集優先策略**：交集足夠時（≥12個）直接返回交集
3. **Prompt 版本管理**：支援 v1.0.0 和 v1.2.0，並有版本控制機制
4. **並行處理優化**：解決 Azure OpenAI 客戶端並行連接問題

### 版本對照

| 版本 | 發布日期 | 主要變更 | 一致性提升 |
|------|----------|----------|------------|
| v1.0 | 2025-06-30 | 初始2輪交集策略 | 基準值 |
| v2.0 | 2025-07-01 | 16個上限+交集優先 | +20-33% |

---

## 系統架構圖

### 整體架構


:::mermaid
graph TB
    subgraph "API Layer"
        A[POST /api/v1/extract-jd-keywords]
        A1[Query: prompt_version]
    end
    
    subgraph "Service Layer"
        B[KeywordExtractionService]
        C[AzureOpenAIClient]
        D[ResponseParser]
        E[KeywordStandardizer]
        F[PromptManager]
    end
    
    subgraph "Model Layer"
        G[ExtractKeywordsRequest]
        H[ExtractKeywordsResponse]
        I[KeywordExtractionData]
    end
    
    subgraph "External Services"
        J[Azure OpenAI API]
    end
    
    subgraph "Prompt Versions"
        K[v1.0.0.yaml]
        L[v1.2.0.yaml]
        M[latest.yaml]
    end
    
    A --> G
    A --> A1
    A1 --> F
    F --> K
    F --> L
    F --> M
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    C --> J
    B --> I
    I --> H
    A --> H
:::

### 核心演算法流程（v2.0）

:::mermaid
graph TD
    A[接收職位描述] --> B[載入 Prompt 版本]
    B --> C[執行第1輪提取]
    B --> D[執行第2輪提取]
    C --> E[計算交集]
    D --> E
    E --> F{交集 >= 12?}
    F -->|是| G[直接返回交集<br/>最多16個]
    F -->|否| H[啟動補充策略]
    H --> I[從兩輪結果補充<br/>至目標數量<br/>最多16個]
    G --> J[標準化處理<br/>可選]
    I --> J
    J --> K[返回結果]
:::

---

## 詳細設計

### 1. 資料模型設計

#### 1.1 請求模型
```python
# src/models/keyword_extraction.py
from pydantic import BaseModel, Field, validator
from typing import List

class ExtractKeywordsRequest(BaseModel):
    """關鍵字提取請求模型"""
    job_description: str = Field(
        ...,
        min_length=50,
        max_length=20000,
        description="職位描述文本"
    )
    max_keywords: int = Field(
        default=20,
        ge=5,
        le=30,
        description="最多返回的關鍵字數量"
    )
    include_standardization: bool = Field(
        default=True,
        description="是否啟用標準化處理"
    )
    use_multi_round_validation: bool = Field(
        default=True,
        description="是否使用2輪交集策略"
    )
```

#### 1.2 回應模型（Bubble.io 相容 - 固定 Schema）
```python
# src/models/response.py
class KeywordExtractionData(BaseModel):
    """永遠返回相同結構，確保 Bubble.io 相容性"""
    keywords: List[str] = []  # 失敗時為空陣列
    keyword_count: int = 0
    processing_time_ms: int = 0
    extraction_method: str = ""
    prompt_version: str = ""
    
    # 交集統計（總是存在）
    intersection_size: int = 0
    round1_size: int = 0
    round2_size: int = 0
    consistency_score: float = 0.0
    
    # 標準化資訊（總是存在）
    standardized_count: int = 0
    standardization_applied: bool = False

class ExtractKeywordsResponse(BaseModel):
    """固定結構回應"""
    success: bool = True
    data: KeywordExtractionData
    error: ErrorInfo  # 總是存在
    warning: WarningInfo  # 總是存在
```

### 2. 服務層設計

#### 2.1 關鍵字提取服務（v2.0 更新版）
```python
# src/services/keyword_extraction.py
class KeywordExtractionService:
    def __init__(self, prompt_version: str = "latest"):
        # 核心參數（v2.0 更新）
        self.min_response_keywords = 12    # 最小響應關鍵字數
        self.max_return_keywords = 16      # 最大返回關鍵字數（硬上限）
        self.default_max_keywords = 20     # 用戶請求的預設值
        
        # 載入 Prompt 配置
        self.config = self._load_prompt_config(prompt_version)
        
    async def extract_keywords(
        self, 
        job_description: str, 
        max_keywords: int = 20
    ) -> KeywordExtractionData:
        """v2.0 演算法實作"""
        # 1. 並行執行兩輪提取（使用獨立客戶端）
        round1_task = self._extract_keywords_round(job_description, 1)
        round2_task = self._extract_keywords_round(job_description, 2)
        round1_keywords, round2_keywords = await asyncio.gather(
            round1_task, round2_task
        )
        
        # 2. 計算交集（不區分大小寫）
        intersection = self._calculate_intersection(
            round1_keywords, round2_keywords
        )
        
        # 3. v2.0 決策邏輯
        if len(intersection) >= self.min_response_keywords:
            # 交集足夠，直接返回（限制16個）
            max_return = min(max_keywords, self.max_return_keywords)
            final_keywords = intersection[:max_return]
            strategy = "intersection_only"
        else:
            # 交集不足，啟動補充策略
            final_keywords = self._supplement_keywords(
                intersection, 
                round1_keywords, 
                round2_keywords, 
                target_count=min(max_keywords, self.max_return_keywords)
            )
            strategy = "intersection_plus_supplement"
        
        # 4. 構建結果
        return self._build_result(
            final_keywords, intersection, 
            round1_keywords, round2_keywords,
            strategy
        )
    
    async def _extract_keywords_round(
        self, job_description: str, round_number: int
    ) -> List[str]:
        """單輪提取（解決並行問題）"""
        # 為每個請求創建獨立的客戶端
        from src.services.openai_client import get_azure_openai_client
        client = get_azure_openai_client()
        
        try:
            response = await client.chat_completion(
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": self._format_user_prompt(
                        job_description
                    )}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                model="gpt-4o-2"
            )
            keywords = self._parse_keywords_response(response)
            return keywords
        finally:
            await client.close()
```

#### 2.2 補充策略詳解（v2.0）
```python
def _supplement_keywords(
    self, intersection, round1, round2, target_count
):
    """智能補充策略"""
    final_keywords = list(intersection)
    remaining_needed = target_count - len(final_keywords)
    
    if remaining_needed > 0:
        # 1. 統計兩輪中的出現頻率
        all_keywords = round1 + round2
        keyword_freq = Counter(kw.lower() for kw in all_keywords)
        
        # 2. 移除已在交集中的
        for kw in intersection:
            keyword_freq.pop(kw.lower(), None)
        
        # 3. 按頻率排序補充（優先選擇出現2次的）
        sorted_keywords = sorted(
            keyword_freq.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 4. 補充至目標數量
        for keyword, freq in sorted_keywords[:remaining_needed]:
            # 保持原始大小寫
            original = next(
                kw for kw in all_keywords 
                if kw.lower() == keyword
            )
            final_keywords.append(original)
    
    return final_keywords
```

#### 2.3 回應解析器（三層策略）
```python
# src/services/keyword_extraction/parser.py
class ResponseParser:
    def parse_keywords(self, llm_response: str) -> List[str]:
        """三層解析策略"""
        # 第一層：直接 JSON 解析
        keywords = self._try_json_parse(llm_response)
        if keywords:
            return keywords
        
        # 第二層：正則提取 JSON
        keywords = self._try_regex_json_parse(llm_response)
        if keywords:
            return keywords
        
        # 第三層：提取引號內容
        keywords = self._try_quote_extraction(llm_response)
        
        return keywords
```

#### 2.4 標準化服務
```python
# src/services/keyword_extraction/standardizer.py
class KeywordStandardizer:
    def __init__(self):
        self.dictionary = {
            # 技能標準化
            "python programming": "Python",
            "python development": "Python",
            "machine learning algorithms": "machine learning",
            "ml algorithms": "machine learning",
            "aws cloud services": "AWS",
            "amazon web services": "AWS",
            "react.js": "React",
            "node.js": "Node.js",
            # ... 更多映射
        }
        
        self.patterns = [
            # 移除無用後綴
            (r'\s+(programming|development|skills?)$', ''),
            (r'\s+(tools?|software|platform|services?)$', ''),
            # 標準化縮寫
            (r'\bml\b', 'machine learning'),
            (r'\bai\b', 'artificial intelligence'),
        ]
```

### 3. API 端點設計（支援 Prompt 版本選擇）

```python
# src/api/v1/keyword_extraction.py
@router.post("/extract-jd-keywords")
async def extract_keywords(
    request: ExtractKeywordsRequest,
    prompt_version: str = Query(
        default="latest", 
        description="Prompt版本 (v1.0.0, v1.2.0, latest)"
    )
) -> ExtractKeywordsResponse:
    """提取職位描述關鍵字"""
    # 初始化服務時傳入 prompt 版本
    service = KeywordExtractionService(prompt_version=prompt_version)
    
    try:
        data = await service.extract_keywords(
            job_description=request.job_description,
            max_keywords=request.max_keywords
        )
        
        # 處理警告情況
        if data.keyword_count < 12:
            response = ExtractKeywordsResponse(
                success=True,
                data=data
            )
            response.warning.has_warning = True
            response.warning.message = "關鍵字數量不足"
            return response
        
        return ExtractKeywordsResponse(
            success=True,
            data=data
        )
    except Exception as e:
        # 錯誤處理...
```

---

## Prompt 版本管理

### 版本結構
```
src/prompts/keyword_extraction/
├── v1.0.0.yaml    # 初始版本（每輪15-22個）
├── v1.2.0.yaml    # 優化版本（每輪固定25個）
└── latest.yaml    # 符號連結 -> v1.2.0.yaml
```

### 版本差異

#### v1.0.0 特徵
```yaml
version: "1.0.0"
system_prompt: |
  You are a professional keyword extractor...
user_prompt: |
  Extract 15-20 technical keywords...
llm_config:
  temperature: 0.3
  max_tokens: 500
```

#### v1.2.0 特徵
```yaml
version: "1.2.0"
changelog:
  - date: "2025-07-01"
    changes:
      - "增加提取數量到 25 個"
      - "優化指令清晰度"
    impact: "提高一致性 20%"
system_prompt: |
  You are a professional keyword extractor...
user_prompt: |
  Extract EXACTLY 25 technical keywords...
llm_config:
  temperature: 0.3
  max_tokens: 600
```

---

## 一致性 KPI 成果

### 測試結果對比

| 測試場景 | v1.0 | v2.0 | 提升幅度 |
|---------|------|------|----------|
| TSMC短文本（~1,200字符） | ~60% | 78.1% | +30% |
| BCG長文本（~5,898字符） | ~45% | 60.0% | +33% |
| 兩次相同機率 | ~25% | 39.84% | +59% |
| 核心關鍵字穩定性 | ~90% | 100% | +11% |

### 核心關鍵字穩定性

以下類型關鍵字達到 100% 穩定性：
- 程式語言：Python, Java, JavaScript, C++, Go
- 框架技術：React, Spring, Django, FastAPI
- 資料庫：MySQL, PostgreSQL, MongoDB, Redis
- 雲端平台：AWS, Azure, GCP
- AI/ML：machine learning, deep learning, TensorFlow

---

## 測試策略

### 1. 一致性 KPI 測試

```bash
# 測試腳本位置
src/tests/consistency_kpi/
├── test_consistency_kpi.sh      # 主測試腳本
├── test_tsmc_consistency.sh     # 短文本測試
├── test_bcg_consistency.sh      # 長文本測試
├── generate_report.sh           # 報告生成
└── README.md                    # 使用說明

# 執行測試
./test_consistency_kpi.sh
```

### 2. 單元測試

```python
# tests/unit/services/test_keyword_extraction.py
def test_intersection_priority():
    """測試交集優先策略"""
    service = KeywordExtractionService()
    round1 = ["Python", "Java", "AWS", "React", "Docker"] * 3  # 15個
    round2 = ["Python", "Java", "AWS", "React", "MySQL"] * 3   # 15個
    
    intersection = service._calculate_intersection(round1, round2)
    assert len(intersection) >= 12  # 應該有12個交集
    
    # 當交集足夠時，應直接返回交集
    final = service._process_results(intersection, round1, round2, 20)
    assert len(final) == 16  # 最多返回16個
```

### 3. 整合測試

```python
# tests/integration/test_api.py
@pytest.mark.asyncio
async def test_prompt_version_selection():
    """測試 Prompt 版本選擇"""
    # 測試 v1.0.0
    response = await client.post(
        "/api/v1/extract-jd-keywords?prompt_version=v1.0.0",
        json={"job_description": JOB_DESCRIPTION}
    )
    assert response.json()["data"]["prompt_version"] == "v1.0.0"
    
    # 測試 v1.2.0
    response = await client.post(
        "/api/v1/extract-jd-keywords?prompt_version=v1.2.0",
        json={"job_description": JOB_DESCRIPTION}
    )
    assert response.json()["data"]["prompt_version"] == "v1.2.0"
```

---

## 部署考量

### 1. 環境變數配置
```bash
# .env
LLM2_ENDPOINT=https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com
LLM2_API_KEY=your-api-key-here
EMBEDDING_ENDPOINT=https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15
OPENAI_API_KEY=your-openai-key-here

# Prompt 版本設定（可選）
DEFAULT_PROMPT_VERSION=v1.2.0
```

### 2. Azure Functions 配置
- 設定超時時間：5 分鐘
- 記憶體配置：512MB
- 並行實例：10
- Application Insights：啟用

### 3. 效能優化
- 回應快取：對相同輸入快取 1 小時
- 連接池：最大 50 個連接
- 重試策略：最多重試 3 次

### 4. 監控指標
- **P50 處理時間**: < 1.5秒
- **P95 處理時間**: < 3秒
- **一致性率**: > 70%（短文本）/ > 50%（長文本）
- **API 可用性**: > 99.9%

---

## 安全考量

1. **API Key 管理**：使用 Azure Key Vault
2. **輸入驗證**：防止注入攻擊
3. **速率限制**：每分鐘 60 次請求
4. **日誌處理**：不記錄完整職位描述

---

## 雙語擴展架構（v3.0 預計）

### 語言檢測整合

基於現有的關鍵字提取架構，v3.0 版本將整合自動語言檢測功能，實現語言一致性：



:::mermaid
graph TB
    subgraph API_Layer[Enhanced API Layer]
        A[POST /api/v1/extract-jd-keywords]
        A1[Query: prompt_version]
        A2["Body: language=auto|en|zh-TW"]
    end
    
    subgraph Language_Detection[Language Detection Layer]
        LD[LanguageDetectionService]
        LV[Language Validator]
    end
    
    subgraph Service_Layer[Enhanced Service Layer]
        B[BilingualKeywordExtractionService]
        BPM[BilingualPromptManager]
        MS[MultilingualStandardizer]
        C[AzureOpenAIClient]
        D[ResponseParser]
    end
    
    subgraph Language_Resources[Language-Specific Resources]
        EN[English Prompt v1.2.0]
        ZH[Chinese Prompt v1.2.0-zh-TW]
        ENDICT[English Dictionary]
        ZHDICT[Chinese Dictionary]
    end
    
    A --> A2
    A2 --> LD
    LD --> LV
    LV --> B
    B --> BPM
    BPM --> EN
    BPM --> ZH
    B --> MS
    MS --> ENDICT
    MS --> ZHDICT
    B --> C
    B --> D
:::

### 語言路由邏輯

現有的 `KeywordExtractionService` 將被擴展為 `BilingualKeywordExtractionService`：

```python
class BilingualKeywordExtractionService(KeywordExtractionService):
    def __init__(self, prompt_version: str = "latest"):
        super().__init__(prompt_version)
        self.language_detector = LanguageDetectionService()
        self.bilingual_prompt_manager = BilingualPromptManager()
        self.multilingual_standardizer = MultilingualStandardizer()
    
    async def extract_keywords(
        self, 
        job_description: str, 
        max_keywords: int = 20,
        language: str = "auto"
    ) -> BilingualKeywordExtractionData:
        # 1. 語言檢測或驗證
        if language == "auto":
            detected = await self.language_detector.detect_language(job_description)
        else:
            detected = self._validate_explicit_language(language)
        
        # 2. 載入語言特定配置
        config = self.bilingual_prompt_manager.load_language_prompt(detected.language)
        
        # 3. 執行語言感知的關鍵字提取
        return await self._extract_with_language_context(
            job_description, detected.language, config, max_keywords
        )
```

### 架構整合點

1. **API 層擴展**: 新增 `language` 參數支援
2. **服務層增強**: 整合語言檢測邏輯
3. **資源管理**: 支援多語言 Prompt 和字典
4. **回應模型**: 包含語言檢測資訊

### 相關設計文檔

完整的雙語系統架構設計請參見：
- [DESIGN_LANGUAGE_DETECTION_20250702](./DESIGN_LANGUAGE_DETECTION_20250702.md) - 語言檢測系統設計
- [REQ_BILINGUAL_KEYWORD_20250702](../requirements/REQ_BILINGUAL_KEYWORD_20250702.md) - 雙語需求規格
- [TEST_BILINGUAL_KEYWORD_20250702](../test_plans/TEST_BILINGUAL_KEYWORD_20250702.md) - 雙語測試計劃

### Work Items 規劃

雙語功能相關的 Work Items：
- **Feature [#399](https://dev.azure.com/airesumeadvisor/API/_workitems/edit/399)**: 雙語關鍵字提取功能（英文+繁體中文）
- **預估工時**: 60 小時
- **實作時程**: v2.0 穩定後開始

---

## 未來優化方向

1. **動態閾值調整**：根據文本長度動態調整 min_response_keywords
2. **快取機制**：實作 Redis 快取提升效能
3. **A/B 測試框架**：支援多版本 prompt 並行測試
4. **個性化調整**：根據不同產業調整關鍵字權重
5. **批次處理 API**：支援一次處理多個職位描述

---

## 相關文檔

- [需求文檔](../requirements/REQ_KEYWORD_EXTRACTION_20250630.md)
- [測試計畫](../test_plans/TEST_CONSISTENCY_KPI_20250701.md)
- [API 文檔](../api/API_KEYWORD_v1.md)
- [架構設計](./DESIGN_FHS_ARCHITECTURE_20250630.md)
- [Prompt 管理](./DESIGN_PROMPT_MANAGEMENT_20250630.md)
- [雙語語言檢測設計](./DESIGN_LANGUAGE_DETECTION_20250702.md)

---

**審核狀態**: ✅ 已發布  
**最後更新**: 2025-07-01  
**下次審查**: 2025-08-01  
**版本記錄**: 
- v1.0 (2025-06-30): 初始設計
- v2.0 (2025-07-01): 新增16個上限、交集優先策略、Prompt版本管理