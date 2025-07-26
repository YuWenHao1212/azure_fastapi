# 履歷格式化功能架構設計文件

**版本**: 1.1  
**日期**: 2025-01-09  
**狀態**: 草稿（已根據業務流程反饋更新）  
**作者**: Claude  

## 關鍵更新
1. 明確 OCR 服務由 Bubble.io 呼叫，本 API 負責格式化重建
2. 新增語言保持功能：LLM 自動偵測並使用原始語言輸出
3. 說明 OCR 輸出格式：非結構化文字，以句子為單位（item title + item text）

## 相關文件
- 需求文件：[REQ_RESUME_FORMAT_20250109.md](./REQ_RESUME_FORMAT_20250109.md)
- Work Items：
  - [PENDING_EPIC_ID] 履歷格式化功能開發
  - [PENDING_FEATURE_ID] 實作履歷格式化 API

## 1. 架構概述

### 1.1 業務流程說明
1. **Bubble.io** 先呼叫 OCR 服務處理上傳的履歷（PDF/圖片）
2. **OCR 輸出**格式為兩行：
   - 第一行：所有項目的類型，用逗號分隔（如：`Title, Title, NarrativeText, Title, NarrativeText...`）
   - 第二行：對應的文字內容，用逗號分隔（如：`John Smith, Senior Software Engineer, Experienced developer with...`）
   - 實際範例：
     ```
     Title, Title, NarrativeText, Title, NarrativeText, Title, ListItem, ListItem
     John Smith, Senior Software Engineer, Experienced developer with 10+ years, Work Experience, Led team of 5 engineers, Education, Bachelor of Computer Science, Master of Software Engineering
     ```
3. **Bubble.io** 將 OCR 結果傳給本 API 進行結構化重建
4. **LLM** 自動判斷原始語言並使用相同語言重建履歷

### 1.2 系統架構圖
```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│  Bubble.io  │────▶│ OCR Service │────▶│  OCR Output      │
│   (Client)  │     │ (External)  │     │ (Unstructured)   │
└─────────────┘     └─────────────┘     └────────┬─────────┘
                                                  │
                                                  ▼
                                         ┌──────────────────┐
                                         │ Resume Format    │
                                         │ API Endpoint     │
                                         │ /format-resume   │
                                         └────────┬─────────┘
                                                  │
                                    ┌─────────────┴──────────────┐
                                    │                            │
                              ┌─────▼─────┐              ┌──────▼──────┐
                              │    LLM    │              │   Unified   │
                              │  Service  │◀─────────────│   Prompt    │
                              │           │              │   Service   │
                              └─────┬─────┘              └─────────────┘
                                    │
                                    ▼
                              ┌─────────────┐
                              │ Formatted   │
                              │ HTML Resume │
                              └─────┬───────┘
                                    │
                              ┌─────▼─────┐
                              │   Text    │
                              │Processing │
                              └─────┬─────┘
                                    │
                              ┌─────▼─────┐
                              │   HTML    │
                              │ Validator │
                              └─────┬─────┘
                                    │
                              ┌─────▼─────┐
                              │  Final    │
                              │  Output   │
                              └───────────┘
```

### 1.3 模組職責
- **OCR Service (External)**: Bubble.io 呼叫的外部 OCR 服務
- **API Endpoint**: 接收 OCR 輸出，處理 HTTP 請求、驗證、回應格式化
- **LLM Service**: 使用 Azure OpenAI 將非結構化文字重建為結構化履歷
- **Unified Prompt Service**: 管理 Prompt 版本，包含語言保持指令
- **Text Processing Service**: 後處理，包括 OCR 錯誤修正、文字清理
- **HTML Validator**: 確保輸出符合 TinyMCE 要求，安全性驗證

## 2. 詳細設計

### 2.1 API 層設計

```python
# src/api/v1/resume_format.py
from fastapi import APIRouter, HTTPException, status
from src.models.resume_format import ResumeFormatRequest, ResumeFormatResponse
from src.services.resume_format import ResumeFormatService

router = APIRouter()

@router.post(
    "/format-resume",
    response_model=UnifiedResponse,
    status_code=status.HTTP_200_OK,
    summary="Format OCR text into structured HTML resume"
)
async def format_resume(request: ResumeFormatRequest) -> UnifiedResponse:
    """
    將 OCR 文字轉換為結構化的 HTML 履歷格式
    """
    try:
        service = ResumeFormatService()
        result = await service.format_resume(
            ocr_text=request.ocr_text,
            supplement_info=request.supplement_info
        )
        
        return UnifiedResponse(
            success=True,
            data=result,
            error=ErrorDetail(),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        # 錯誤處理邏輯
        pass
```

### 2.2 模型設計

```python
# src/models/resume_format.py
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional

class SupplementInfo(BaseModel):
    """補充資訊模型"""
    name: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class ResumeFormatRequest(BaseModel):
    """履歷格式化請求模型"""
    ocr_text: str = Field(..., min_length=100, description="OCR 提取的文字")
    supplement_info: Optional[SupplementInfo] = None
    
    @validator('ocr_text')
    def validate_ocr_text(cls, v):
        if len(v.strip()) < 100:
            raise ValueError("OCR text too short, minimum 100 characters required")
        return v

class SectionsDetected(BaseModel):
    """檢測到的履歷區段"""
    contact: bool = False
    summary: bool = False
    skills: bool = False
    experience: bool = False
    education: bool = False
    projects: bool = False
    certifications: bool = False

class CorrectionsMade(BaseModel):
    """修正統計"""
    ocr_errors: int = 0
    date_standardization: int = 0
    email_fixes: int = 0
    phone_fixes: int = 0

class ResumeFormatData(BaseModel):
    """履歷格式化回應資料"""
    formatted_resume: str
    sections_detected: SectionsDetected
    corrections_made: CorrectionsMade
    supplement_info_used: list[str] = []
```

### 2.3 服務層設計

```python
# src/services/resume_format.py
import logging
from typing import Optional, Dict, Any
from src.services.llm_service import LLMService
from src.services.text_processing import TextProcessingService
from src.services.html_validator import HTMLValidator
from src.models.resume_format import (
    ResumeFormatData, SectionsDetected, CorrectionsMade
)

logger = logging.getLogger(__name__)

class ResumeFormatService:
    """履歷格式化服務"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.text_processor = TextProcessingService()
        self.html_validator = HTMLValidator()
    
    async def format_resume(
        self, 
        ocr_text: str, 
        supplement_info: Optional[Dict[str, Any]] = None
    ) -> ResumeFormatData:
        """
        格式化履歷主流程
        """
        try:
            # 1. 預處理 OCR 文字
            cleaned_text = self.text_processor.preprocess_ocr_text(ocr_text)
            
            # 2. 準備 LLM 輸入
            # OCR 輸出格式：第一行是逗號分隔的 types，第二行是逗號分隔的內容
            llm_input = self._prepare_llm_input(cleaned_text, supplement_info)
            
            # 3. 呼叫 LLM 進行格式化
            formatted_html = await self.llm_service.format_resume(llm_input)
            
            # 4. 文字後處理（OCR 錯誤修正等）
            processed_html = self.text_processor.postprocess_html(formatted_html)
            
            # 5. HTML 驗證和清理
            validated_html = self.html_validator.validate_and_clean(processed_html)
            
            # 6. 檢測區段
            sections_detected = self._detect_sections(validated_html)
            
            # 7. 計算修正統計
            corrections_made = self._calculate_corrections(
                ocr_text, cleaned_text, validated_html
            )
            
            # 8. 記錄使用的補充資訊
            supplement_used = self._track_supplement_usage(
                validated_html, supplement_info
            )
            
            return ResumeFormatData(
                formatted_resume=validated_html,
                sections_detected=sections_detected,
                corrections_made=corrections_made,
                supplement_info_used=supplement_used
            )
            
        except Exception as e:
            logger.error(f"Resume formatting failed: {str(e)}")
            raise
```

### 2.4 文字處理服務

```python
# src/services/text_processing.py
import re
from typing import Dict, Tuple

class TextProcessingService:
    """文字處理服務"""
    
    # OCR 錯誤修正對照表
    EMAIL_CORRECTIONS = {
        '＠': '@',
        '.c0m': '.com',
        '.c0n': '.com',
        'gmai1': 'gmail',
        'out1ook': 'outlook'
    }
    
    PHONE_CORRECTIONS = {
        'O': '0',
        'I': '1',
        'l': '1',
        'S': '5',
        'Z': '2'
    }
    
    def preprocess_ocr_text(self, text: str) -> str:
        """預處理 OCR 文字"""
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text)
        
        # 修正常見 OCR 錯誤
        text = self._fix_email_errors(text)
        text = self._fix_phone_errors(text)
        text = self._fix_encoding_issues(text)
        
        return text.strip()
    
    def _fix_email_errors(self, text: str) -> str:
        """修正 email 相關的 OCR 錯誤"""
        for wrong, correct in self.EMAIL_CORRECTIONS.items():
            text = text.replace(wrong, correct)
        
        # 使用正則表達式修正 email 格式
        email_pattern = r'([a-zA-Z0-9._%+-]+)[@＠]([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        text = re.sub(email_pattern, r'\1@\2', text)
        
        return text
```

### 2.5 HTML 驗證服務

```python
# src/services/html_validator.py
from bs4 import BeautifulSoup
import re
from typing import Dict

class HTMLValidator:
    """HTML 驗證和清理服務"""
    
    # 允許的 HTML 標籤白名單
    ALLOWED_TAGS = {
        'h1', 'h2', 'h3', 'h4', 'p', 'ul', 'li', 
        'strong', 'em', 'br', 'a'
    }
    
    # 允許的屬性
    ALLOWED_ATTRS = {
        'a': ['href']
    }
    
    def validate_and_clean(self, html: str) -> str:
        """驗證並清理 HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. 移除不允許的標籤
        self._remove_disallowed_tags(soup)
        
        # 2. 清理屬性
        self._clean_attributes(soup)
        
        # 3. 移除危險內容
        self._remove_dangerous_content(soup)
        
        # 4. 確保正確的編碼
        cleaned_html = str(soup)
        
        return cleaned_html
    
    def detect_sections(self, html: str) -> Dict[str, bool]:
        """檢測履歷中的各個區段"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            "contact": self._has_contact_info(soup),
            "summary": self._has_summary(soup),
            "skills": self._has_section_h2(soup, "Skills"),
            "experience": self._has_section_h2(soup, "Work Experience"),
            "education": self._has_section_h2(soup, "Education"),
            "projects": self._has_section_h2(soup, "Projects"),
            "certifications": self._has_section_h2(soup, "Certifications")
        }
    
    def _has_section_h2(self, soup: BeautifulSoup, title: str) -> bool:
        """檢查是否有特定的 h2 標題"""
        h2_tags = soup.find_all('h2')
        return any(h2.get_text().strip() == title for h2 in h2_tags)
```

### 2.6 LLM 服務整合

```python
# src/services/llm_service.py
from src.core.config import get_settings
from src.prompts.unified_prompt_service import UnifiedPromptService
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """LLM 服務封裝"""
    
    def __init__(self):
        self.settings = get_settings()
        self.prompt_service = UnifiedPromptService()
        self.client = self._initialize_client()
    
    async def format_resume(self, input_data: Dict[str, Any]) -> str:
        """使用 LLM 格式化履歷"""
        try:
            # 1. 獲取 prompt
            system_prompt, user_prompt = self.prompt_service.get_prompt(
                task="resume_format",
                version="v1.0",
                data=input_data
            )
            
            # 2. 呼叫 LLM
            response = await self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # 較低的溫度以確保一致性
                max_tokens=4000
            )
            
            # 3. 提取並返回 HTML 內容
            html_content = response.choices[0].message.content
            return self._extract_html_content(html_content)
            
        except Exception as e:
            logger.error(f"LLM formatting failed: {str(e)}")
            raise
```

## 3. Prompt 管理

### 3.1 Prompt 檔案結構
```
src/prompts/
├── resume_format/
│   └── v1.0.0.yaml
└── unified_prompt_service.py
```

### 3.2 Prompt YAML 格式
```yaml
# src/prompts/resume_format/v1.0.0.yaml
task: resume_format
version: v1.0.0
system: |
  You are an expert resume formatter specializing in processing OCR-extracted text...
  
  ## Language Preservation Rule
  CRITICAL: You MUST detect the original language of the OCR text and generate the resume in THE SAME LANGUAGE.
  - If OCR text is in English → Output in English
  - If OCR text is in Traditional Chinese → Output in Traditional Chinese (繁體中文)
  - If OCR text is in Simplified Chinese → Output in Simplified Chinese (简体中文)
  - If OCR text is mixed languages → Use the dominant language
  
  ## OCR Input Format
  The OCR output consists of two lines:
  1. First line: All item types separated by commas (e.g., Title, Title, NarrativeText, Title, ListItem...)
  2. Second line: Corresponding text content separated by commas
  
  Example:
  ```
  Title, Title, NarrativeText, Title, NarrativeText
  John Smith, Senior Software Engineer, Experienced developer with 10+ years, Work Experience, Led team of 5 engineers
  ```
  
  Your task is to parse these two lines, match types with their content, and reconstruct a properly structured HTML resume.
  
  [其餘 system prompt 內容...]
  
user: |
  ## Input Data
  OCR_TEXT: {ocr_text}
  
  SUPPLEMENT_INFO: {supplement_info}
  
  Please format this OCR output into a structured HTML resume, maintaining the original language.
```

## 4. 錯誤處理策略

### 4.1 錯誤類型
1. **輸入驗證錯誤** (422)
   - OCR 文字太短
   - 無效的補充資訊格式

2. **LLM 處理錯誤** (500)
   - API 呼叫失敗
   - 超時
   - 回應格式異常

3. **HTML 驗證錯誤** (500)
   - 無法解析的 HTML
   - 危險內容檢測

### 4.2 錯誤回應格式
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_OCR_TEXT",
    "message": "OCR text is too short or unreadable",
    "details": "Minimum 100 characters required, received 50"
  },
  "timestamp": "2025-01-09T12:00:00Z"
}
```

## 5. 效能優化

### 5.1 快取策略
- 使用 Redis 快取相同 OCR 文字的處理結果
- TTL: 60 分鐘
- 快取鍵：`resume_format:{ocr_text_hash}`

### 5.2 並行處理
- 文字預處理和 prompt 準備可並行執行
- 區段檢測和修正統計可並行計算

### 5.3 資源限制
- 最大輸入長度：50,000 字符
- LLM 超時：30 秒
- 最大併發請求：10

## 6. 監控與日誌

### 6.1 監控指標
```python
# Application Insights 自定義事件
monitoring_service.track_event("ResumeFormatRequested", {
    "ocr_text_length": len(ocr_text),
    "has_supplement_info": bool(supplement_info),
    "processing_time_ms": duration * 1000,
    "sections_detected_count": sum(sections_detected.values()),
    "total_corrections": sum(corrections_made.values())
})
```

### 6.2 日誌記錄
- 請求開始/結束
- LLM 呼叫時間
- 錯誤詳情
- 區段檢測結果

## 7. 測試策略

### 7.1 單元測試
```python
# tests/unit/test_text_processing.py
def test_fix_email_errors():
    """測試 email OCR 錯誤修正"""
    input_text = "Contact: john＠gmai1.c0m"
    expected = "Contact: john@gmail.com"
    assert text_processor.fix_email_errors(input_text) == expected
```

### 7.2 整合測試
```python
# tests/integration/test_resume_format_api.py
async def test_format_resume_complete_flow():
    """測試完整的履歷格式化流程"""
    # 準備測試資料
    # 呼叫 API
    # 驗證回應格式
    # 檢查 HTML 有效性
```

## 8. 安全考量

### 8.1 輸入驗證
- 長度限制
- 字符編碼驗證
- SQL 注入防護

### 8.2 輸出安全
- HTML 標籤白名單
- XSS 防護
- 屬性清理

### 8.3 資料隱私
- 不記錄個人資訊
- 快取使用雜湊鍵
- 日誌脫敏處理

## 9. 部署考量

### 9.1 環境變數
```yaml
# Azure Function App 設定
AZURE_OPENAI_ENDPOINT: "https://..."
AZURE_OPENAI_API_KEY: "從 Key Vault 讀取"
REDIS_CONNECTION_STRING: "從 Key Vault 讀取"
```

### 9.2 相依性
```txt
# requirements.txt 新增
beautifulsoup4==4.12.2
lxml==4.9.3
```

### 9.3 Function App 設定
- 超時時間：60 秒
- 記憶體：512 MB
- Python 版本：3.11

---

**下一步**：
1. 審核架構設計
2. 建立相關 Work Items
3. 開始實作開發