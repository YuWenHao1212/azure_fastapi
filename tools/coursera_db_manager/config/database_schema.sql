-- =====================================================
-- Coursera 課程資料庫 - 最終設計 (2025-01-27 版本)
-- =====================================================

-- 1. 主要表格：課程資料（含 embedding）
CREATE TABLE courses (
    -- 識別欄位
    id VARCHAR(255) PRIMARY KEY,                     -- 格式: {platform}_{external_id}
    platform VARCHAR(50) NOT NULL DEFAULT 'coursera', -- 平台名稱
    external_id VARCHAR(255) NOT NULL,               -- 原始平台的課程 ID
    
    -- 基本資訊
    name TEXT NOT NULL,                              -- 課程名稱
    description TEXT,                                -- 課程描述
    provider VARCHAR(500),                           -- 原始提供者名稱
    provider_standardized VARCHAR(255),              -- 標準化提供者名稱
    provider_logo_url VARCHAR(1000),                 -- 提供者 Logo URL
    category VARCHAR(500),                           -- 類別
    course_type VARCHAR(50),                         -- 原始課程類型
    course_type_standard VARCHAR(50),                -- 標準化課程類型
    
    -- 商業資訊
    price NUMERIC DEFAULT 0,                         -- 現價
    currency VARCHAR(10) DEFAULT 'USD',              -- 貨幣
    image_url TEXT,                                  -- 課程圖片
    affiliate_url TEXT NOT NULL,                     -- Impact.com affiliate 連結
    
    -- 課程詳細資訊
    difficulty_level VARCHAR(20),                    -- 難度等級
    rating NUMERIC,                                  -- 評分
    ratings_count INTEGER,                           -- 評分數量
    enrolled_count INTEGER,                          -- 註冊人數
    estimated_hours INTEGER,                         -- 預估學習時數
    
    -- 向量資料
    embedding vector(3072),                          -- 語意搜尋用
    
    -- 元資料
    metadata JSONB,                                  -- 額外的結構化資料
    
    -- 時間戳記
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 複合唯一索引
    UNIQUE(platform, external_id)
);

-- 2. 搜尋記錄（分析用戶行為）
CREATE TABLE search_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,                     -- 搜尋關鍵字
    results_count INT DEFAULT 0,             -- 結果數量
    response_time_ms INT,                    -- 回應時間（毫秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 同步記錄（維護用）
CREATE TABLE sync_logs (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,          -- 同步類型 (full, incremental)
    platform VARCHAR(50),                    -- 平台名稱
    total_processed INT DEFAULT 0,           -- 處理總數
    new_courses INT DEFAULT 0,               -- 新增課程數
    updated_courses INT DEFAULT 0,           -- 更新課程數
    status VARCHAR(50) NOT NULL,             -- 狀態 (running, completed, failed)
    error_message TEXT,                      -- 錯誤訊息
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 4. 建立索引（加速常用查詢）
-- 平台索引
CREATE INDEX idx_courses_platform ON courses(platform);

-- 依提供者查詢：找 Google 的課程
CREATE INDEX idx_courses_provider ON courses(provider);

-- 標準化提供者索引
CREATE INDEX idx_courses_provider_standardized ON courses(provider_standardized);

-- 依價格查詢：找免費或特定價格範圍
CREATE INDEX idx_courses_price ON courses(price);

-- 依類別查詢：找 "Data Science" 相關
CREATE INDEX idx_courses_category ON courses(category);

-- 課程類型索引
CREATE INDEX idx_courses_type ON courses(course_type);

-- 標準化課程類型索引
CREATE INDEX idx_course_type_standard ON courses(course_type_standard);

-- 向量搜尋（如果使用 ivfflat，但 3072 維度可能太大）
-- CREATE INDEX idx_courses_embedding ON courses USING ivfflat (embedding vector_cosine_ops);

-- 5. 建立更新時間的觸發器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_courses_updated_at 
    BEFORE UPDATE ON courses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 使用範例
-- =====================================================

-- 1. 插入課程
INSERT INTO courses (
    id, platform, external_id, name, description, 
    provider, provider_standardized, provider_logo_url,
    category, course_type, course_type_standard,
    price, affiliate_url, embedding
) VALUES (
    'coursera_spzn:xxx',
    'coursera',
    'spzn:xxx',
    'Machine Learning',
    'Learn ML basics...',
    'Stanford University',
    'Stanford University',
    'https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/[logo_url]',
    'Computer Science > AI',
    'specialization',
    'specialization',
    49.00,
    'https://imp.i384100.net/...',
    '[0.1, 0.2, ...]'::vector
);

-- 2. 搜尋範例
-- 找 Google 的免費課程（使用標準化名稱）
SELECT name, price, affiliate_url, provider_logo_url
FROM courses 
WHERE provider_standardized = 'Google' AND price = 0;

-- 找特定類型的課程
SELECT name, provider_standardized, course_type_standard
FROM courses
WHERE course_type_standard IN ('certification', 'specialization');

-- 向量相似度搜尋
SELECT name, provider_standardized, price,
       1 - (embedding <=> '[query_vector]'::vector) as similarity
FROM courses
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '[query_vector]'::vector
LIMIT 10;

-- 3. 記錄搜尋
INSERT INTO search_logs (query, results_count, response_time_ms)
VALUES ('python data science', 25, 156);

-- 4. 記錄同步
INSERT INTO sync_logs (sync_type, platform, total_processed, new_courses, updated_courses, status)
VALUES ('incremental', 'coursera', 150, 10, 140, 'completed');