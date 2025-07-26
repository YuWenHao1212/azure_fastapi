# Course Type 分類器實作規格書

**版本**: 1.0  
**日期**: 2025-07-16  
**狀態**: 已實作並部署

## 1. 概述

本文檔記錄了課程類型自動分類器的完整實作，用於將 Coursera 課程準確分類到適當的類型中。此分類器是 ETL 管線的重要組成部分，確保課程資料的準確性和一致性。

### 1.1 主要功能
- 基於多層次策略的自動課程分類
- 支援信心度評分 (0.0-1.0)
- 提供分類推理解釋
- 處理複雜的課程類型判斷

### 1.2 支援的課程類型
- `course` - 標準個人課程
- `specialization` - 多課程專項課程
- `specialization-course` - 專項課程中的個別課程
- `professional-certificate` - 專業認證課程
- `guided-project` - 短期實作項目
- `degree` - 完整學位課程
- `mastertrack-certificate` - MasterTrack 認證課程

## 2. 核心實作

### 2.1 分類器架構

```python
class CourseTypeClassifier:
    """
    多層次課程類型分類器
    
    分類策略：
    1. ID 前綴規則 (信心度 0.9+)
    2. 關鍵字模式匹配 (信心度 0.7-0.9)
    3. 內容上下文分析 (信心度 0.5-0.8)
    """
    
    @classmethod
    def classify(cls, 
                 course_id: str,
                 name: str,
                 description: str = "",
                 provider: str = "",
                 price: float = 0,
                 metadata: Optional[Dict[str, Any]] = None) -> Tuple[CourseType, float]:
        """
        分類課程類型並返回信心度
        
        Args:
            course_id: 課程 ID (如: coursera_spzn:xxx)
            name: 課程名稱
            description: 課程描述
            provider: 提供者名稱
            price: 課程價格
            metadata: 額外元資料
            
        Returns:
            (CourseType, confidence_score)
        """
```

### 2.2 三層分類策略

#### 第一層：ID 前綴規則 (信心度 0.9+)

**最高可信度的分類依據**：

```python
def _classify_by_id_prefix(cls, course_id: str) -> Optional[Tuple[CourseType, float]]:
    """基於 ID 前綴的高信心度分類"""
    
    # 提取 external_id
    external_id = course_id.split('_', 1)[1] if '_' in course_id else course_id
    
    # 專項課程中的子課程 (信心度: 0.95)
    if external_id.startswith('spzn:child'):
        return CourseType.SPECIALIZATION_COURSE, 0.95
    
    # 專項課程 (需進一步分析)
    elif external_id.startswith('spzn:'):
        return cls._analyze_specialization_type(...)
    
    # 一般課程 (需進一步分析)
    elif external_id.startswith('crse:'):
        return cls._analyze_course_type(...)
    
    return None
```

#### 第二層：關鍵字模式匹配 (信心度 0.7-0.9)

**基於名稱和描述的模式識別**：

```python
# 專業認證課程模式
PROFESSIONAL_CERTIFICATE_PATTERNS = [
    r'professional certificate',
    r'(ibm|google|meta|aws|microsoft|salesforce|adobe).*certificate',
    r'certified.*professional',
    r'certification program',
    r'career certificate'
]

# 引導項目模式
GUIDED_PROJECT_PATTERNS = [
    r'guided project',
    r'hands-on project',
    r'practical project',
    r'project-based.*course',
    r'learn.*by doing',
    r'(1|2) hour.*project'
]

# 學位課程模式
DEGREE_PATTERNS = [
    r'master of (science|arts|business|engineering|education|public)',
    r'bachelor of (science|arts|business|engineering)',
    r'ms in',
    r'mba program',
    r'degree program',
    r'graduate degree'
]

# MasterTrack 模式
MASTERTRACK_PATTERNS = [
    r'mastertrack certificate',
    r'mastertrack',
    r'master track'
]
```

#### 第三層：內容上下文分析 (信心度 0.5-0.8)

**基於價格、時長、提供者的推理**：

```python
def _analyze_contextual_clues(cls, name: str, description: str, 
                            provider: str, price: float) -> Optional[Tuple[CourseType, float]]:
    """內容上下文分析"""
    
    # 引導項目指標
    if price <= 10.0 and cls._has_duration_indicators(description, max_hours=2):
        return CourseType.GUIDED_PROJECT, 0.7
    
    # 大學提供者 + 學位關鍵字
    if cls._is_university_provider(provider) and cls._has_degree_keywords(name):
        return CourseType.DEGREE, 0.8
    
    # 科技公司 + 認證關鍵字
    if cls._is_tech_company(provider) and cls._has_certificate_keywords(name):
        return CourseType.PROFESSIONAL_CERTIFICATE, 0.75
    
    return None
```

## 3. 關鍵實作細節

### 3.1 專項課程分析

**區分專項課程和專業認證**：

```python
def _analyze_specialization_type(cls, name: str, description: str, 
                               provider: str) -> Tuple[CourseType, float]:
    """分析 spzn: 前綴的課程類型"""
    
    # 檢查是否為專業認證
    if cls._matches_professional_certificate_patterns(name, description):
        return CourseType.PROFESSIONAL_CERTIFICATE, 0.9
    
    # 檢查提供者是否為科技公司
    if cls._is_tech_company(provider):
        cert_keywords = ['certificate', 'certification', 'certified']
        if any(keyword in name.lower() for keyword in cert_keywords):
            return CourseType.PROFESSIONAL_CERTIFICATE, 0.85
    
    # 預設為專項課程
    return CourseType.SPECIALIZATION, 0.8
```

### 3.2 課程細分分析

**區分引導項目、學位課程和一般課程**：

```python
def _analyze_course_type(cls, name: str, description: str, 
                        provider: str, price: float) -> Tuple[CourseType, float]:
    """分析 crse: 前綴的課程類型"""
    
    # 引導項目檢查
    if cls._matches_guided_project_patterns(name, description):
        return CourseType.GUIDED_PROJECT, 0.9
    
    # 學位課程檢查
    if cls._matches_degree_patterns(name, description):
        return CourseType.DEGREE, 0.9
    
    # MasterTrack 檢查
    if cls._matches_mastertrack_patterns(name, description):
        return CourseType.MASTERTRACK_CERTIFICATE, 0.9
    
    # 內容上下文分析
    contextual_result = cls._analyze_contextual_clues(name, description, provider, price)
    if contextual_result:
        return contextual_result
    
    # 預設為一般課程
    return CourseType.COURSE, 0.6
```

### 3.3 模式匹配輔助函數

```python
def _matches_professional_certificate_patterns(cls, name: str, description: str) -> bool:
    """檢查是否符合專業認證模式"""
    text = f"{name} {description}".lower()
    return any(re.search(pattern, text, re.IGNORECASE) 
              for pattern in cls.PROFESSIONAL_CERTIFICATE_PATTERNS)

def _matches_guided_project_patterns(cls, name: str, description: str) -> bool:
    """檢查是否符合引導項目模式"""
    text = f"{name} {description}".lower()
    return any(re.search(pattern, text, re.IGNORECASE) 
              for pattern in cls.GUIDED_PROJECT_PATTERNS)

def _has_duration_indicators(cls, text: str, max_hours: int = 2) -> bool:
    """檢查是否有時長指標"""
    duration_patterns = [
        r'(\d+)\s*(hour|hr)s?',
        r'(\d+)\s*minutes?',
        r'(\d+)\s*mins?'
    ]
    # 實作時長檢查邏輯
    # ...
```

## 4. 資料庫整合

### 4.1 更新腳本

**測試模式**：
```python
# 預覽變更但不更新資料庫
python update_course_types.py --test-mode
```

**生產模式**：
```python
# 實際更新資料庫
python update_course_types.py --production
```

### 4.2 批次處理

```python
def update_course_types_batch(courses: List[Dict], batch_size: int = 100) -> Dict[str, Any]:
    """批次更新課程類型"""
    
    results = {
        'total_processed': 0,
        'updated_count': 0,
        'confidence_distribution': defaultdict(int),
        'type_distribution': defaultdict(int)
    }
    
    for i in range(0, len(courses), batch_size):
        batch = courses[i:i+batch_size]
        
        for course in batch:
            course_type, confidence = CourseTypeClassifier.classify(
                course_id=course['id'],
                name=course['name'],
                description=course.get('description', ''),
                provider=course.get('provider', ''),
                price=course.get('price', 0)
            )
            
            # 更新資料庫
            update_course_type_in_db(course['id'], course_type.value)
            
            # 統計
            results['total_processed'] += 1
            results['type_distribution'][course_type.value] += 1
            results['confidence_distribution'][f"{confidence:.1f}"] += 1
    
    return results
```

## 5. 測試與驗證

### 5.1 測試案例

```python
def test_professional_certificate_classification():
    """測試專業認證分類"""
    test_cases = [
        {
            'course_id': 'coursera_spzn:google-data-analytics',
            'name': 'Google Data Analytics Professional Certificate',
            'provider': 'Google',
            'expected_type': CourseType.PROFESSIONAL_CERTIFICATE,
            'min_confidence': 0.85
        },
        {
            'course_id': 'coursera_spzn:ibm-ai-engineering',
            'name': 'IBM AI Engineering Professional Certificate',
            'provider': 'IBM',
            'expected_type': CourseType.PROFESSIONAL_CERTIFICATE,
            'min_confidence': 0.85
        }
    ]
    
    for case in test_cases:
        course_type, confidence = CourseTypeClassifier.classify(
            course_id=case['course_id'],
            name=case['name'],
            provider=case['provider']
        )
        
        assert course_type == case['expected_type']
        assert confidence >= case['min_confidence']
```

### 5.2 驗證統計

**分類準確度統計**：
```python
def validate_classification_accuracy(sample_size: int = 1000) -> Dict[str, float]:
    """驗證分類準確度"""
    
    # 隨機抽樣
    sample_courses = get_random_sample(sample_size)
    
    # 手動驗證結果
    manual_labels = load_manual_labels()
    
    # 計算準確度
    correct = 0
    total = len(sample_courses)
    
    for course in sample_courses:
        predicted_type, confidence = CourseTypeClassifier.classify(**course)
        actual_type = manual_labels[course['id']]
        
        if predicted_type.value == actual_type:
            correct += 1
    
    return {
        'accuracy': correct / total,
        'total_samples': total,
        'correct_predictions': correct
    }
```

## 6. 效能考量

### 6.1 最佳化策略

- **Regex 編譯快取**：預編譯正規表達式
- **優先級規則**：最具體的規則優先評估
- **批次處理**：大規模資料集的批次更新
- **信心度閾值**：低信心度結果的人工審核

### 6.2 記憶體使用

```python
class CourseTypeClassifier:
    # 預編譯正規表達式以提升效能
    _compiled_patterns = {
        'professional_certificate': [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in PROFESSIONAL_CERTIFICATE_PATTERNS
        ],
        'guided_project': [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in GUIDED_PROJECT_PATTERNS
        ]
        # ... 其他模式
    }
```

## 7. 錯誤處理與除錯

### 7.1 分類解釋功能

```python
def classify_with_explanation(cls, **kwargs) -> Dict[str, Any]:
    """提供分類結果與詳細解釋"""
    
    course_type, confidence = cls.classify(**kwargs)
    
    return {
        'classification': course_type.value,
        'confidence': confidence,
        'reasoning': cls._generate_reasoning(**kwargs),
        'matched_patterns': cls._get_matched_patterns(**kwargs),
        'contextual_clues': cls._analyze_contextual_clues(**kwargs)
    }
```

### 7.2 常見問題處理

**低信心度結果**：
- 信心度 < 0.7 的結果需要人工審核
- 建立審核隊列和反饋機制
- 持續改進分類規則

**邊界案例**：
- 混合類型課程的處理
- 新課程類型的識別
- 特殊格式課程的分類

## 8. 維護與更新

### 8.1 定期審核

- 每月審核低信心度分類結果
- 分析新課程類型趨勢
- 更新分類規則和模式

### 8.2 規則更新流程

1. **識別新模式**：從失敗案例中學習
2. **測試新規則**：在測試環境中驗證
3. **部署更新**：謹慎部署到生產環境
4. **監控效果**：追蹤分類準確度變化

## 9. 整合狀態

### 9.1 已完成
- ✅ 核心分類器實作
- ✅ 多層次分類策略
- ✅ 資料庫整合腳本
- ✅ 測試案例覆蓋
- ✅ 批次處理能力

### 9.2 待完成
- ⏳ 自動化分類準確度監控
- ⏳ 新課程類型的自動識別
- ⏳ 分類規則的機器學習優化

---

## 10. 參考資料

### 10.1 相關文檔
- [DATABASE_DESIGN_COURSES_20250715.md](./DATABASE_DESIGN_COURSES_20250715.md) - 資料庫設計
- [COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md](./COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md) - ETL 設計

### 10.2 實作檔案
- `/temp/dev/scripts/course_type_classifier.py` - 核心分類器
- `/temp/dev/scripts/update_course_types.py` - 更新腳本
- `/temp/dev/scripts/update_course_types_final.py` - 生產腳本

---

**文檔編號**: COURSE-TYPE-CLASSIFIER-001  
**作者**: Claude Code  
**下次審查日期**: 2026-01-16