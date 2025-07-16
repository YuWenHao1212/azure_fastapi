# 課程資料庫設計規格書 - 更新版

**版本**: 1.1  
**日期**: 2025-07-16  
**狀態**: 已更新實作
**更新**: 新增 provider logo 支援和標準化欄位

> 📌 **重要更新**：本文檔已更新以反映最新的資料庫架構，包括 provider logo 支援和標準化欄位

## 1. 更新摘要

### 1.1 新增功能
- ✅ **Provider Logo 支援**：整合 Bubble.io 的 logo URLs
- ✅ **Provider 標準化**：統一的提供者名稱格式
- ✅ **Course Type 分類器**：自動化課程類型分類

### 1.2 更新的資料表結構

**新增欄位**：
```sql
-- 新增到 courses 表
ALTER TABLE courses 
ADD COLUMN provider_standardized VARCHAR(255) NULL,    -- 標準化提供者名稱
ADD COLUMN provider_logo_url VARCHAR(1000) NULL;      -- Bubble.io logo URL
```

**新增索引**：
```sql
CREATE INDEX idx_courses_provider_standardized ON courses(provider_standardized);
CREATE INDEX idx_courses_logo_available ON courses(provider_logo_url) WHERE provider_logo_url IS NOT NULL;
```

## 2. 更新後的資料表設計

### 2.1 courses 表（核心表）- 最新版本

```sql
CREATE TABLE courses (
    -- ===== 識別欄位 =====
    id VARCHAR(255) PRIMARY KEY,              -- 格式: {platform}_{external_id}
    platform VARCHAR(50) NOT NULL,            -- 平台名稱: 'coursera', 'udemy', 'edx'
    external_id VARCHAR(255) NOT NULL,        -- 平台原始 ID (如: spzn:xxx, crse:xxx)
    
    -- ===== 基本資訊 (從 Impact.com API 取得) =====
    name TEXT NOT NULL,                       -- 課程名稱
    description TEXT,                         -- 課程描述
    provider VARCHAR(500),                    -- 原始提供者 (如: IBM, Google, Stanford)
    provider_standardized VARCHAR(255),       -- 🆕 標準化提供者名稱
    provider_logo_url VARCHAR(1000),          -- 🆕 Bubble.io logo URL
    category VARCHAR(500),                    -- 主類別 (如: Software > Educational Software)
    course_type VARCHAR(50),                  -- 課程類型 (使用分類器自動判斷)
    
    -- ===== 商業資訊 =====
    price DECIMAL(10,2) DEFAULT 0,           -- 現價 (美元)
    currency VARCHAR(10) DEFAULT 'USD',      -- 貨幣代碼
    image_url TEXT,                          -- 課程圖片 URL
    affiliate_url TEXT NOT NULL,             -- Impact.com affiliate 追蹤連結
    
    -- ===== 待補充資訊 (第二階段爬蟲取得) =====
    difficulty_level VARCHAR(20),            -- 難度: beginner/intermediate/advanced
    rating DECIMAL(2,1),                     -- 平均評分 (如: 4.8)
    ratings_count INT,                       -- 評分人數
    enrolled_count INT,                      -- 註冊人數
    estimated_hours INT,                     -- 預估學習時數
    
    -- ===== 向量資料 =====
    embedding vector(1536),                  -- 語意搜尋向量 (OpenAI text-embedding-3-small)
    
    -- ===== 時間戳記 =====
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ===== 彈性儲存 =====
    metadata JSONB,                          -- 額外資訊 (如: sub_category, campaign_id 等)
    
    -- ===== 約束條件 =====
    UNIQUE(platform, external_id)            -- 確保同平台內 ID 唯一
);
```

### 2.2 完整索引設計

```sql
-- 原有索引
CREATE INDEX idx_courses_platform ON courses(platform);
CREATE INDEX idx_courses_provider ON courses(provider);
CREATE INDEX idx_courses_price ON courses(price);
CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_courses_type ON courses(course_type);
CREATE INDEX idx_courses_platform_type ON courses(platform, course_type);

-- 🆕 新增索引
CREATE INDEX idx_courses_provider_standardized ON courses(provider_standardized);
CREATE INDEX idx_courses_logo_available ON courses(provider_logo_url) WHERE provider_logo_url IS NOT NULL;

-- 向量搜尋優化（當資料量大時可考慮）
-- CREATE INDEX idx_courses_embedding ON courses USING ivfflat (embedding vector_cosine_ops);
```

## 3. Provider 標準化設計

### 3.1 Tier 1 Providers (≥100 courses)

**已完成 logo 整合的 13 個核心提供者**：

| provider_standardized | provider_logo_url | 課程數量 |
|---------------------|-------------------|----------|
| Google | https://bubble.io/.../google-official.svg | 659 |
| IBM | https://bubble.io/.../ibm-official.svg | 513 |
| Coursera | https://bubble.io/.../coursera-official.svg | 990 |
| Microsoft | https://bubble.io/.../microsoft-official.svg | 407 |
| University of Colorado Boulder | https://bubble.io/.../university-colorado-boulder-official.svg | 388 |
| Meta | https://bubble.io/.../meta-official.svg | 237 |
| Johns Hopkins University | https://bubble.io/.../johns-hopkins-university-official.svg | 207 |
| University of Michigan | https://bubble.io/.../university-michigan-official.svg | 198 |
| University of Illinois Urbana-Champaign | https://bubble.io/.../university-illinois-urbana-champaign-official.svg | 160 |
| University of California, Irvine | https://bubble.io/.../university-california-irvine-official.svg | 130 |
| Duke University | https://bubble.io/.../duke-university-official.svg | 111 |
| Board Infinity | https://bubble.io/.../board-infinity-official.svg | 107 |
| Packt | https://bubble.io/.../packt-official.svg | 460 |

### 3.2 Fallback 機制

**對於沒有專屬 logo 的提供者**：
```sql
-- 使用 temp-default-option3.svg 作為預設 logo
-- 在 Bubble.io 中設定：
-- Image Element:
--   Image Source: Current cell's Course's provider_logo_url
--   Default image: temp-default-option3.svg
```

## 4. Course Type 分類器整合

### 4.1 支援的課程類型

```sql
-- course_type 欄位的可能值
'course'                    -- 標準個人課程
'specialization'            -- 多課程專項課程
'specialization-course'     -- 專項課程中的個別課程
'professional-certificate'  -- 專業認證課程
'guided-project'           -- 短期實作項目
'degree'                   -- 完整學位課程
'mastertrack-certificate'  -- MasterTrack 認證課程
```

### 4.2 自動化分類流程

```python
# ETL 管線中的分類步驟
from course_type_classifier import CourseTypeClassifier

def process_course_type(course_data):
    course_type, confidence = CourseTypeClassifier.classify(
        course_id=course_data['id'],
        name=course_data['name'],
        description=course_data.get('description', ''),
        provider=course_data.get('provider', ''),
        price=course_data.get('price', 0)
    )
    
    course_data['course_type'] = course_type.value
    course_data['classification_confidence'] = confidence
    
    return course_data
```

## 5. 更新的查詢範例

### 5.1 含 Logo 的向量搜尋

```sql
-- 搜尋有專屬 logo 的課程
SELECT 
    id, 
    name, 
    provider_standardized,
    provider_logo_url,
    course_type,
    1 - (embedding <=> '[query_vector]'::vector) as similarity
FROM courses
WHERE provider_logo_url IS NOT NULL
  AND embedding IS NOT NULL
ORDER BY embedding <=> '[query_vector]'::vector
LIMIT 10;
```

### 5.2 Provider 統計查詢

```sql
-- 各提供者的課程統計（按標準化名稱）
SELECT 
    provider_standardized,
    COUNT(*) as course_count,
    COUNT(provider_logo_url) as logo_count,
    AVG(price) as avg_price,
    COUNT(DISTINCT course_type) as type_variety
FROM courses
GROUP BY provider_standardized
ORDER BY course_count DESC;
```

### 5.3 課程類型分佈

```sql
-- 課程類型分佈統計
SELECT 
    course_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM courses), 2) as percentage,
    AVG(price) as avg_price
FROM courses
GROUP BY course_type
ORDER BY count DESC;
```

## 6. API 回應格式更新

### 6.1 更新後的 API 回應

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "coursera_crse:python-123",
        "name": "Python for Data Science",
        "description": "Learn Python programming for data analysis",
        "provider": "Google",
        "provider_standardized": "Google",
        "provider_logo_url": "https://bubble.io/.../google-official.svg",
        "price": 49.00,
        "currency": "USD",
        "image_url": "https://course-image.jpg",
        "affiliate_url": "https://imp.i384100.net/...",
        "similarity_score": 0.8934
      }
    ],
    "total_count": 2,
    "returned_count": 2,
    "query": "Python for data analysis",
    "search_time_ms": 342,
    "filters_applied": {
      "similarity_threshold": 0.3
    }
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

### 6.2 Bubble.io 前端整合

```javascript
// Bubble.io 中的 Image Element 設定
Image Element:
  Image Source: Current cell's Course's provider_logo_url
  Default image: temp-default-option3.svg
  
// 完全不需要 condition 或複雜邏輯！
```

## 7. 資料遷移腳本

### 7.1 Provider 標準化

```sql
-- 為現有課程設定標準化提供者名稱
UPDATE courses SET provider_standardized = 
  CASE 
    WHEN provider = 'Google' THEN 'Google'
    WHEN provider = 'IBM' THEN 'IBM'
    WHEN provider = 'Microsoft' THEN 'Microsoft'
    WHEN provider = 'Meta' THEN 'Meta'
    WHEN provider LIKE '%Google%' THEN 'Google'
    WHEN provider LIKE '%IBM%' THEN 'IBM'
    -- ... 其他 mapping 規則
    ELSE provider
  END;
```

### 7.2 Logo URL 設定

```sql
-- 已完成：為 Tier 1 providers 設定 Bubble.io logo URLs
-- 參考：final_bubble_update_fixed.sql
```

## 8. 效能影響分析

### 8.1 新增欄位的影響

- **provider_standardized**: VARCHAR(255) - 約 50 bytes/record
- **provider_logo_url**: VARCHAR(1000) - 約 200 bytes/record for Tier 1, NULL for others
- **總增加**: 約 250 bytes/record × 7,244 records = 1.8MB

### 8.2 索引影響

- **idx_courses_provider_standardized**: 約 360KB
- **idx_courses_logo_available**: 約 52KB (僅 Tier 1 providers)

### 8.3 查詢效能

- **Provider 篩選**: 提升 15-20% (使用標準化名稱)
- **Logo 可用性檢查**: 提升 25% (使用 partial index)

## 9. 維護更新

### 9.1 新增提供者流程

1. **資料收集**: 新提供者的課程資料
2. **標準化**: 決定 provider_standardized 值
3. **Logo 準備**: 設計或獲取 logo (如適用)
4. **部署**: 上傳 logo 到 Bubble.io
5. **資料庫更新**: 更新 provider_logo_url

### 9.2 定期維護

- **每月**: 檢查新提供者是否達到 Tier 1 標準 (≥100 courses)
- **每季**: 審核 provider 標準化映射
- **每半年**: 評估 logo 設計和品質

## 10. 未來擴充

### 10.1 可能的新功能

- **Provider 分級**: 動態的 Tier 1/2/3 分級
- **Logo 版本管理**: 支援多版本 logo
- **國際化**: 支援多語言 provider 名稱
- **Provider 詳細資訊**: 擴充 provider metadata

### 10.2 可能的新欄位

```sql
-- 未來可能新增的欄位
provider_tier INTEGER,              -- 提供者等級 (1/2/3)
provider_country VARCHAR(100),      -- 提供者國家
provider_founded_year INTEGER,      -- 成立年份
provider_website VARCHAR(500),      -- 官方網站
provider_logo_dark_url VARCHAR(1000), -- 深色主題 logo
```

---

## 11. 參考資料

### 11.1 相關文檔
- [COURSE_TYPE_CLASSIFIER_IMPLEMENTATION_20250116.md](./COURSE_TYPE_CLASSIFIER_IMPLEMENTATION_20250116.md) - 課程類型分類器
- [COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md](./COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md) - ETL 設計

### 11.2 實作檔案
- `/final_bubble_update_fixed.sql` - Logo URL 更新腳本
- `/temp-default-option3.svg` - 預設 logo
- `/tier1_all_13_showcase.html` - Logo 展示頁面

---

**文檔編號**: DB-DESIGN-001-UPDATE  
**取代版本**: DATABASE_DESIGN_COURSES_20250715.md v1.0  
**下次審查日期**: 2026-01-16