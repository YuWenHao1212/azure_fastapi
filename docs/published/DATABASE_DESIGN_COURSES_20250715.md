# 課程資料庫設計規格書

**版本**: 1.0  
**日期**: 2025-07-15  
**狀態**: 已實作

> 📌 **注意**：本文檔專注於資料庫設計。完整的 ETL 實作細節請參考 [COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md](./COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md)

## 1. 概述

本文檔定義了課程推薦系統的資料庫架構，主要用於儲存多平台線上課程資料並支援向量語意搜尋。

### 1.1 主要需求
- 支援多個課程平台（初期以 Coursera 為主）
- 儲存課程基本資訊和行銷素材
- 支援向量搜尋（使用 pgvector）
- 預留欄位供未來資料擴充
- 追蹤搜尋行為和同步狀態

### 1.2 技術架構
- 資料庫：PostgreSQL 15 with pgvector extension
- 向量維度：1536（OpenAI text-embedding-3-small）
- 主機：Azure Database for PostgreSQL Flexible Server

## 2. 資料表設計

### 2.1 courses 表（核心表）

儲存所有課程的詳細資訊，包含向量資料。

```sql
CREATE TABLE courses (
    -- ===== 識別欄位 =====
    id VARCHAR(255) PRIMARY KEY,              -- 格式: {platform}_{external_id}
    platform VARCHAR(50) NOT NULL,            -- 平台名稱: 'coursera', 'udemy', 'edx'
    external_id VARCHAR(255) NOT NULL,        -- 平台原始 ID (如: spzn:xxx, crse:xxx)
    
    -- ===== 基本資訊 (從 Impact.com API 取得) =====
    name TEXT NOT NULL,                       -- 課程名稱
    description TEXT,                         -- 課程描述
    provider VARCHAR(500),                    -- 提供者 (如: IBM, Google, Stanford)
    category VARCHAR(500),                    -- 主類別 (如: Software > Educational Software)
    course_type VARCHAR(50),                  -- 課程類型 (course/specialization/certificate)
    
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

### 2.2 search_logs 表（搜尋記錄）

記錄使用者搜尋行為，用於分析和優化。

```sql
CREATE TABLE search_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,                     -- 搜尋關鍵字或描述
    results_count INT DEFAULT 0,             -- 回傳結果數量
    response_time_ms INT,                    -- 回應時間（毫秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 sync_logs 表（同步記錄）

追蹤資料同步狀態，便於維護和除錯。

```sql
CREATE TABLE sync_logs (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,          -- 同步類型: 'full' 或 'incremental'
    platform VARCHAR(50),                    -- 同步的平台
    total_processed INT DEFAULT 0,           -- 處理的課程數量
    new_courses INT DEFAULT 0,               -- 新增的課程數
    updated_courses INT DEFAULT 0,           -- 更新的課程數
    status VARCHAR(50) NOT NULL,             -- 狀態: 'running', 'completed', 'failed'
    error_message TEXT,                      -- 錯誤訊息（如果失敗）
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

## 3. 索引設計

為了優化查詢效能，建立以下索引：

```sql
-- 平台篩選（找特定平台的課程）
CREATE INDEX idx_courses_platform ON courses(platform);

-- 提供者查詢（找 Google 或 IBM 的課程）
CREATE INDEX idx_courses_provider ON courses(provider);

-- 價格篩選（找免費課程或特定價格範圍）
CREATE INDEX idx_courses_price ON courses(price);

-- 類別瀏覽（找特定類別的課程）
CREATE INDEX idx_courses_category ON courses(category);

-- 課程類型（區分 course/specialization）
CREATE INDEX idx_courses_type ON courses(course_type);

-- 複合索引：平台+類型（常用組合查詢）
CREATE INDEX idx_courses_platform_type ON courses(platform, course_type);

-- 向量搜尋優化（當資料量大時可考慮）
-- CREATE INDEX idx_courses_embedding ON courses USING ivfflat (embedding vector_cosine_ops);
-- 注意：ivfflat 對 1536 維度支援良好，3072 維度可能需要其他策略
```

## 4. 資料範例

### 4.1 Coursera 單一課程
```json
{
    "id": "coursera_crse:v1:xxx",
    "platform": "coursera",
    "external_id": "crse:v1:xxx",
    "name": "Machine Learning",
    "provider": "Stanford University",
    "course_type": "course",
    "price": 79.00,
    "difficulty_level": "intermediate",
    "rating": 4.9,
    "enrolled_count": 4500000
}
```

### 4.2 Coursera 專項課程
```json
{
    "id": "coursera_spzn:xxx",
    "platform": "coursera",
    "external_id": "spzn:xxx",
    "name": "Google Data Analytics Professional Certificate",
    "provider": "Google",
    "course_type": "professional-certificate",
    "price": 49.00,
    "difficulty_level": "beginner",
    "metadata": {
        "courses_count": 8,
        "months_to_complete": 6
    }
}
```

## 5. 欄位詳細說明

### 5.1 course_type 值域
- `course` - 單一課程
- `specialization` - 專項課程（多個相關課程組合）
- `professional-certificate` - 專業證書課程
- `specialization-course` - 專項課程中的子課程
- `degree` - 學位課程（未來擴充）

### 5.2 difficulty_level 值域
- `beginner` - 初學者
- `intermediate` - 中級
- `advanced` - 進階
- `mixed` - 混合等級（專項課程可能包含不同難度）

### 5.3 metadata 欄位範例
```json
{
    "sub_category": "Machine Learning",
    "skills": ["Python", "TensorFlow", "Deep Learning"],
    "prerequisites": ["Basic Python", "Linear Algebra"],
    "instructors": ["Andrew Ng"],
    "university_partner": true,
    "completion_rate": 0.73,
    "campaign_id": "14726",
    "catalog_item_id": "spzn:xxx"
}
```

## 6. ETL 流程

### 6.1 第一階段：Impact.com API
1. 從 API 取得基本資料
2. 推斷 course_type（基於 external_id prefix）
3. 儲存到資料庫
4. 生成 embedding（詳見 6.3）

### 6.2 第二階段：資料補充（未來實作）
1. 使用爬蟲或其他 API
2. 補充 rating、enrolled_count、difficulty_level 等
3. 重新生成 embedding（納入新資訊）

### 6.3 Embedding 生成策略

#### 6.3.1 文本組成
Embedding 使用以下欄位組合生成，依重要性排序：

```python
# 生成 embedding 的文本格式
text_parts = [
    f"Course: {name}",                    # 課程名稱（最重要）
    f"Provider: {provider}",              # 提供者（如 Google, IBM）
    f"Category: {category}",              # 類別（如 Data Science）
    f"Description: {description[:1500]}", # 描述（涵蓋 80% 課程的完整描述）
]

# 未來當有更多資料時可加入
if difficulty_level:
    text_parts.append(f"Level: {difficulty_level}")
if rating:
    text_parts.append(f"Rating: {rating} stars")

embedding_text = " | ".join(text_parts)
```

#### 6.3.2 實際範例
```text
輸入文本：
"Course: Machine Learning | Provider: Stanford University | Category: Computer Science > AI | Description: This course provides a broad introduction to machine learning..."

輸出：
1536 維向量 [0.0123, -0.0456, 0.0789, ...]
```

#### 6.3.3 生成考量
- **權重分配**：課程名稱最重要，其次是提供者和類別
- **描述截斷**：限制在 1,500 字元（涵蓋 80% 課程的完整描述）
- **語言處理**：保持原始語言（英文），確保語意準確
- **更新策略**：當重要欄位變更時需重新生成

## 7. 查詢範例

### 7.1 向量相似度搜尋
```sql
-- 搜尋與使用者技能差距相關的課程
SELECT 
    id, name, provider, price, affiliate_url,
    1 - (embedding <=> '[query_vector]'::vector) as similarity
FROM courses
WHERE platform = 'coursera'
  AND embedding IS NOT NULL
ORDER BY embedding <=> '[query_vector]'::vector
LIMIT 10;
```

### 7.2 篩選查詢
```sql
-- 找 Google 提供的免費初學者課程
SELECT name, course_type, rating, enrolled_count
FROM courses
WHERE platform = 'coursera'
  AND provider = 'Google'
  AND price = 0
  AND difficulty_level = 'beginner'
ORDER BY rating DESC NULLS LAST;
```

### 7.3 統計查詢
```sql
-- 各平台課程統計
SELECT 
    platform,
    course_type,
    COUNT(*) as course_count,
    AVG(price) as avg_price,
    AVG(rating) as avg_rating
FROM courses
GROUP BY platform, course_type
ORDER BY platform, course_count DESC;
```

## 8. 維護指引

### 8.1 資料更新頻率
- 完整同步：每月一次
- 增量更新：每週一次
- 價格更新：每日一次（如需要）

### 8.2 Embedding 更新
- 當課程基本資訊變更時
- 當新增重要欄位（如 rating）後
- 更換 embedding 模型時

### 8.3 備份策略
- 每日備份：僅 courses 表（不含 embedding）
- 每週備份：完整資料庫
- Embedding 可重建，非關鍵備份項目

## 9. 效能考量

### 9.1 預期資料量
- Coursera：約 10,000 門課程
- 每個 embedding：6KB (1536 * 4 bytes)
- 總 embedding 儲存：約 60MB
- 預估總資料庫大小：< 300MB

**Embedding 模型選擇**：
- 使用 OpenAI `text-embedding-3-small` (1536 維度)
- 成本效益較佳，對大多數搜尋場景已足夠
- 未來可升級至 `text-embedding-3-large` (3072 維度)

### 9.2 查詢效能目標
- 向量搜尋：< 100ms（前 10 筆）
- 篩選查詢：< 50ms
- 統計查詢：< 200ms

## 10. 安全考量

### 10.1 Affiliate URL 處理策略

您說得對！前端確實需要 affiliate URL 才能讓使用者點擊並追蹤傭金。我的原始建議有誤。正確的做法：

**方案 A：直接返回 Affiliate URL（簡單直接）**
```json
{
  "courses": [{
    "id": "coursera_xxx",
    "name": "Machine Learning",
    "affiliate_url": "https://imp.i384100.net/c/5901857/..."
  }]
}
```
- 優點：實作簡單，沒有額外步驟
- 缺點：URL 較長，可能暴露 campaign 結構

**方案 B：內部追蹤系統（進階）**
```json
{
  "courses": [{
    "id": "coursera_xxx",
    "name": "Machine Learning",
    "click_url": "https://api.yourdomain.com/click/abc123"
  }]
}
```
- API 產生短碼 → 使用者點擊 → 後端記錄 → 302 轉址到 affiliate URL
- 優點：可追蹤點擊數據、URL 更短、可做 A/B 測試
- 缺點：需要額外開發轉址服務

**建議**：初期使用方案 A，直接返回 affiliate URL。

### 10.2 其他安全措施
- 敏感資料（如 campaign_id、auth_token）僅存在後端
- API 需要認證，避免濫用
- 定期清理過期的 search_logs（GDPR 合規）

## 11. 未來擴充

### 11.1 可能新增的欄位
- `last_updated_date` - 課程最後更新日期
- `completion_certificate` - 是否提供證書
- `language` - 授課語言
- `subtitles` - 字幕語言清單

### 11.2 可能新增的表
- `user_favorites` - 使用者收藏
- `course_reviews` - 課程評論快照
- `price_history` - 價格變動歷史
- `course_prerequisites` - 先修課程關係

---

## 12. 參考資料

### 12.1 API 文檔
- Impact.com Publisher API: https://integrations.impact.com/impact-publisher/
- 用於獲取課程資料、價格、Affiliate URLs 等資訊

### 12.2 相關技術文檔
- PostgreSQL pgvector: https://github.com/pgvector/pgvector
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings

### 12.3 相關專案文檔
- **ETL 實作細節**：[COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md](./COURSERA_DATABASE_AND_ETL_DESIGN_20250715.md)
- **文檔組織說明**：[README_COURSERA_DB_DOCS.md](./README_COURSERA_DB_DOCS.md)

---

**文檔編號**: DB-DESIGN-001  
**下次審查日期**: 2025-02-15