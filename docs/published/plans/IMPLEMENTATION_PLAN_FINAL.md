# 履歷標記策略實施計畫 - 最終版

**日期**: 2025-01-12  
**目標**: 一次性實施新的標記策略，整合 Index Calculation

## 實施概要

基於分析，我們將：
1. 更新 LLM Prompt 以符合新的標記規則
2. 創建 EnhancedMarker 類別負責關鍵字標記
3. 整合現有的 IndexCalculationService
4. 更新 API 回應格式

## 詳細實施步驟

### Step 1: 更新 LLM Prompt (30分鐘)

**檔案**: `/src/prompts/resume_tailoring/v1.0.0.yaml`

**修改內容**:
1. **移除 opt-strength 標記**
   - 刪除所有 opt-strength 相關說明
   - 簡化標記策略說明

2. **更新 opt-modified 使用規則**
   ```yaml
   # 新增到 line 188 後
   - `opt-modified`: 改寫或優化的內容 (必須使用 <span> 包裹)
   ```

3. **加強三層級架構說明**
   ```yaml
   ## 三層級標記架構
   1. 段落層級 (opt-new): 完全新增的 section 或段落
      - 可用於 <h2>, <h3>, <p>, <ul> 等區塊元素
      - 例: <h2 class="opt-new">Professional Summary</h2>
   
   2. 內容層級 (opt-modified): 改寫的內容或在現有 section 內新增
      - 必須使用 <span> 包裹
      - 例: <li><span class="opt-modified">改寫的內容...</span></li>
   
   3. 數據層級 (opt-placeholder): 需要填寫的具體數據
      - 必須使用 <span> 包裹
      - 例: <span class="opt-placeholder">[TEAM SIZE]</span>
   ```

4. **移除關鍵字標記指示**
   - 刪除 opt-keyword 相關說明
   - 加入說明：關鍵字標記將由 Python 自動處理

### Step 2: 創建 EnhancedMarker 類別 (1小時)

**新檔案**: `/src/core/enhanced_marker.py`

```python
import re
from typing import List, Tuple
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class EnhancedMarker:
    """Enhanced marker for precise keyword marking"""
    
    def __init__(self):
        self.protected_terms = {
            'JavaScript': ['javascript', 'Javascript'],
            'TypeScript': ['typescript', 'Typescript'],
            # ... 更多
        }
    
    def mark_keywords(
        self,
        html: str,
        original_keywords: List[str],
        new_keywords: List[str]
    ) -> str:
        """
        Mark keywords in HTML content
        
        Args:
            html: HTML content to process
            original_keywords: Keywords from original resume
            new_keywords: New keywords added during optimization
            
        Returns:
            HTML with marked keywords
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Process text nodes only
        for text_node in soup.find_all(text=True):
            if text_node.parent.name in ['script', 'style']:
                continue
                
            # Skip if already marked
            if text_node.parent.name == 'span' and any(
                cls in text_node.parent.get('class', []) 
                for cls in ['opt-keyword', 'opt-keyword-existing', 'opt-placeholder']
            ):
                continue
            
            # Mark keywords
            new_text = self._mark_keywords_in_text(
                str(text_node),
                original_keywords,
                new_keywords
            )
            
            if new_text != str(text_node):
                new_soup = BeautifulSoup(new_text, 'html.parser')
                text_node.replace_with(new_soup)
        
        return str(soup)
    
    def _mark_keywords_in_text(
        self,
        text: str,
        original_keywords: List[str],
        new_keywords: List[str]
    ) -> str:
        """Mark keywords in plain text"""
        # Sort by length (longest first) to handle overlaps
        all_keywords = [
            (kw, 'opt-keyword-existing') for kw in original_keywords
        ] + [
            (kw, 'opt-keyword') for kw in new_keywords
        ]
        
        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)
        
        # Track marked positions
        marked_positions = []
        result_parts = []
        last_end = 0
        
        for keyword, css_class in all_keywords:
            pattern = self._create_keyword_pattern(keyword)
            
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                
                # Check overlap
                if any(start < me and end > ms for ms, me in marked_positions):
                    continue
                
                # Add unmarked text before match
                if last_end < start:
                    result_parts.append(text[last_end:start])
                
                # Add marked keyword
                matched_text = match.group()
                result_parts.append(
                    f'<span class="{css_class}">{matched_text}</span>'
                )
                
                marked_positions.append((start, end))
                last_end = end
        
        # Add remaining text
        if last_end < len(text):
            result_parts.append(text[last_end:])
        
        return ''.join(result_parts)
    
    def _create_keyword_pattern(self, keyword: str) -> str:
        """Create regex pattern for keyword matching"""
        # Handle special characters
        if any(char in keyword for char in ['+', '#', '.', '-']):
            return re.escape(keyword)
        else:
            return r'\b' + re.escape(keyword) + r'\b'
```

### Step 3: 更新 MarkerFixer 整合 EnhancedMarker (30分鐘)

**修改檔案**: `/src/core/marker_fixer.py`

```python
# 在 fix_and_enhance_markers 方法中整合
def fix_and_enhance_markers(
    self, 
    html: str, 
    keywords: list[str] = None,
    original_keywords: list[str] = None
) -> str:
    """Fix incorrectly placed markers and enhance with keyword marking"""
    # 先執行原有的修復邏輯
    html = self._move_markers_to_spans(html)
    html = self._clean_empty_markers(html)
    
    # 如果提供了關鍵字，使用 EnhancedMarker 標記
    if keywords is not None:
        from .enhanced_marker import EnhancedMarker
        enhanced_marker = EnhancedMarker()
        
        # original_keywords 預設為空列表
        if original_keywords is None:
            original_keywords = []
        
        html = enhanced_marker.mark_keywords(
            html,
            original_keywords=original_keywords,
            new_keywords=keywords
        )
    
    return html
```

### Step 4: 整合 Index Calculation (1小時)

**修改檔案**: `/src/services/resume_tailoring.py`

1. **導入 IndexCalculationService**
   ```python
   from .index_calculation import IndexCalculationService, analyze_keyword_coverage
   ```

2. **修改 _process_optimization_result 方法**
   ```python
   async def _process_optimization_result(
       self,
       optimized_data: dict,
       original_resume: str,
       include_markers: bool,
       gap_analysis: GapAnalysisInput,
       job_description: str,  # 新增參數
       language: str  # 新增參數
   ) -> TailoringResult:
       # ... 原有邏輯 ...
       
       # 計算原始關鍵字覆蓋
       original_coverage = analyze_keyword_coverage(
           original_resume,
           gap_analysis.covered_keywords + gap_analysis.missing_keywords
       )
       
       # 修正標記時傳入原始關鍵字
       if include_markers:
           optimized_resume = self.marker_fixer.fix_and_enhance_markers(
               optimized_resume,
               keywords=gap_analysis.missing_keywords,
               original_keywords=gap_analysis.covered_keywords
           )
       
       # 計算優化後的 index
       index_calc_service = IndexCalculationService()
       index_result = await index_calc_service.calculate_index(
           optimized_resume,
           job_description,
           gap_analysis.covered_keywords + gap_analysis.missing_keywords
       )
       
       # 計算改善幅度
       improvement_data = {
           "original_similarity": 0,  # 需要計算原始相似度
           "optimized_similarity": index_result["similarity_percentage"],
           "similarity_improvement": 0,  # 計算提升
           "original_keyword_coverage": original_coverage["coverage_percentage"],
           "optimized_keyword_coverage": index_result["keyword_coverage"]["coverage_percentage"],
           "keyword_coverage_improvement": (
               index_result["keyword_coverage"]["coverage_percentage"] - 
               original_coverage["coverage_percentage"]
           ),
           "new_keywords_added": list(
               set(index_result["keyword_coverage"]["covered_keywords"]) - 
               set(original_coverage["covered_keywords"])
           )
       }
       
       # ... 建立回傳結果 ...
   ```

### Step 5: 更新 API 回應模型 (30分鐘)

**修改檔案**: `/src/models/api/resume_tailoring.py`

```python
# 新增 Index Calculation 結果模型
class IndexCalculationResult(BaseModel):
    """Index calculation results"""
    original_similarity: int
    optimized_similarity: int
    similarity_improvement: int
    original_keyword_coverage: int
    optimized_keyword_coverage: int
    keyword_coverage_improvement: int
    new_keywords_added: List[str]

class KeywordsAnalysis(BaseModel):
    """Keywords analysis results"""
    original_keywords: List[str]
    new_keywords: List[str]
    total_keywords: int
    coverage_details: Dict[str, Any]

# 更新 TailoringResult
class TailoringResult(BaseModel):
    """Resume tailoring result"""
    optimized_resume: str
    applied_improvements: List[str]
    applied_improvements_html: str
    optimization_stats: OptimizationStats
    visual_markers: VisualMarkerStats
    
    # 新增欄位
    index_calculation: IndexCalculationResult
    keywords_analysis: KeywordsAnalysis
```

### Step 6: 測試計畫 (1小時)

1. **單元測試**
   - EnhancedMarker 關鍵字標記測試
   - 重疊關鍵字處理
   - 大小寫處理
   - 特殊字符處理

2. **整合測試**
   - 完整 resume tailoring 流程
   - Index calculation 準確性
   - API 回應格式驗證

3. **驗收測試**
   - 使用真實履歷測試
   - 驗證三層級標記正確性
   - 確認關鍵字 100% 標記率

## 時間估計

- **總時間**: 4-5 小時
- **核心功能**: 3-4 小時
- **測試與調整**: 1 小時

## 風險與緩解

1. **LLM 不遵循新規則**
   - 緩解：提供清晰範例，多次測試調整 prompt

2. **性能影響**
   - 緩解：優化關鍵字匹配演算法，設置關鍵字數量上限

3. **向前相容性**
   - 緩解：新欄位使用 Optional，確保不會破壞現有功能

## 實施順序

1. 更新 LLM Prompt ✅
2. 創建 EnhancedMarker ✅
3. 更新 MarkerFixer ✅
4. 整合 Index Calculation ✅
5. 更新 API 模型 ✅
6. 測試與驗證 ✅

準備開始實施嗎？