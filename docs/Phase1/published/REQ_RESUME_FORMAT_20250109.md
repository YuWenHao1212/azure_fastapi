# 履歷格式化 API 功能需求文件

**版本**: 1.3  
**日期**: 2025-01-09  
**狀態**: 草稿（已加入完整 HTML 範例）  
**作者**: Claude  

## 相關 Work Items

- Epic: [PENDING_EPIC_ID] 履歷格式化功能開發
- Feature: [PENDING_FEATURE_ID] 實作履歷格式化 API
- User Stories:
  - [PENDING_US_ID_1] 作為 API 使用者，我需要將 OCR 文字轉換為結構化履歷
  - [PENDING_US_ID_2] 作為系統，我需要修正 OCR 錯誤並標準化內容
  - [PENDING_US_ID_3] 作為前端開發者，我需要接收符合 TinyMCE 的 HTML 格式

## 1. 功能概述

### 1.1 目標
履歷格式化 API 將 OCR 提取的非結構化文字轉換為標準化、結構化的 HTML 格式履歷，適用於 TinyMCE 編輯器顯示和編輯。

### 1.2 核心價值
- **自動化格式轉換**：減少手動編輯時間
- **錯誤修正**：自動修正常見 OCR 識別錯誤
- **標準化輸出**：確保履歷格式一致性
- **編輯器相容**：輸出符合 TinyMCE 要求的安全 HTML

### 1.3 使用場景
1. 使用者上傳 PDF/圖片履歷後，OCR 提取文字
2. 系統呼叫此 API 將文字轉換為結構化 HTML
3. 前端在 TinyMCE 編輯器中顯示格式化後的履歷
4. 使用者可進一步編輯和完善

## 2. API 規格

### 2.1 端點資訊
- **路徑**: `/api/v1/format-resume`
- **方法**: POST
- **認證**: Function Key (query parameter: `code`)

### 2.2 請求格式

```json
{
  "ocr_text": "string (required, min 100 chars)",
  "supplement_info": {
    "name": "string (optional)",
    "email": "string (optional)",
    "linkedin": "string (optional)",
    "phone": "string (optional)",
    "location": "string (optional)"
  }
}
```

### 2.3 回應格式

#### 成功回應 (200 OK)
```json
{
  "success": true,
  "data": {
    "formatted_resume": "<h1>John Doe</h1><h2>Software Engineer</h2>...",
    "sections_detected": {
      "contact": true,
      "summary": true,
      "skills": true,
      "experience": true,
      "education": true,
      "projects": false,
      "certifications": false
    },
    "corrections_made": {
      "ocr_errors": 12,
      "date_standardization": 5,
      "email_fixes": 1,
      "phone_fixes": 1
    },
    "supplement_info_used": ["name", "email"]
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  },
  "timestamp": "2025-01-09T10:00:00Z"
}
```

#### 錯誤回應
參考標準錯誤格式（400, 422, 500）

## 3. 功能詳細規格

### 3.1 OCR 錯誤修正

#### 3.1.1 電子郵件修正
- `＠` → `@`
- `.c0m` → `.com`
- 常見域名拼寫錯誤修正

#### 3.1.2 電話號碼修正
- `O` → `0`（字母 O 轉數字 0）
- `I`/`l` → `1`（字母轉數字 1）
- 標準化格式：`+1 (XXX) XXX-XXXX`

#### 3.1.3 公司/學校名稱標準化
- 修正常見機構名稱的 OCR 錯誤
- 統一大小寫（如 `MICROSOFT` → `Microsoft`）

### 3.2 內容結構化

#### 3.2.1 必要區段（按順序）
1. **姓名** (`<h1>`)
2. **職位標題** (`<h2>`)
3. **聯絡資訊** (`<p>`)
4. **個人摘要** (`<p>`)（可選）
5. **技能** (`<ul>`)（可選）
6. **工作經驗** (`<h2>` 標題 + `<h3>` 職位）（可選）
7. **教育背景** (`<h2>` 標題 + `<h4>` 學位）（可選）
8. **專案** (`<h2>` 標題）（可選）
9. **證書** (`<h2>` 標題）（可選）



#### 3.2.2 日期標準化
- 格式：統一使用 `mmm YYYY` 格式（如 `Jan 2025`）
- 範圍：`Jan 2023 - Dec 2024` 或 `Jan 2023 - Present`
- 教育日期推算：
  - 學士：畢業日期 - 4 年
  - 碩士：畢業日期 - 2 年
  - 博士：畢業日期 - 5 年
  - 副學士：畢業日期 - 2 年
  - 證書課程：畢業日期 - 1 年

### 3.3 內容分類規則

#### 3.3.1 專案分類
- **個人專案識別詞**：
  - "personal project"
  - "side project"
  - "github.com"
  - "hackathon"
  - "portfolio"
- **工作專案**：預設放在相關工作經驗中

#### 3.3.2 技能分類
- **技術技能**：程式語言、框架、工具
- **軟技能**：溝通、領導、團隊合作
- **認證技能**：有證書支持的技能

### 3.4 HTML 安全處理

#### 3.4.1 禁止的標籤
- `<script>`, `<style>`, `<iframe>`
- `<object>`, `<embed>`, `<applet>`
- 所有表單相關標籤

#### 3.4.2 清理規則
- 移除所有 JavaScript 事件屬性（onclick, onload 等）
- 移除 `javascript:` 協議
- 清理危險的 CSS（expression, url()）
- 確保 UTF-8 編碼正確性

### 3.5 智慧推斷功能

#### 3.5.1 缺失資訊處理
- 無姓名：使用 "[Your Name]" 佔位符
- 無職位：基於工作經驗推斷或使用 "[Desired Position]"
- 無聯絡資訊：使用 supplement_info 或佔位符

#### 3.5.2 內容增強
- 自動產生動作動詞開頭的職責描述
- 量化成就（如有數字）
- 技能關鍵詞標準化

### 3.6 HTML 格式模板（基於 Prompt 定義）

#### 3.6.1 完整履歷結構範例
```html
<h1>Jane Smith</h1>
<h2>Full Stack Developer</h2>
<p>
Location: Seattle, WA<br>
Email: <a href="mailto:jane.smith@email.com">jane.smith@email.com</a><br>
LinkedIn: <a href="https://linkedin.com/in/janesmith">https://linkedin.com/in/janesmith</a>
</p>
<p>Experienced Full Stack Developer with 5+ years building scalable web applications. Expertise in modern JavaScript frameworks and cloud technologies. Passionate about creating efficient, user-friendly solutions.</p>

<h2>Skills</h2>
<ul>
<li>Programming Languages: JavaScript, Python, Java, TypeScript</li>
<li>Frontend: React, Vue.js, Angular, HTML5, CSS3, Sass</li>
<li>Backend: Node.js, Express, Django, Spring Boot</li>
<li>Databases: PostgreSQL, MongoDB, Redis, MySQL</li>
<li>DevOps & Cloud: AWS, Docker, Kubernetes, Jenkins, GitHub Actions</li>
</ul>

<h2>Work Experience</h2>
<h3><strong>Senior Full Stack Developer</strong></h3>
<p><em>Innovation Tech Solutions</em>•<em>Seattle, WA</em>•<em>Jan 2021 - Present</em></p>
<ul>
<li>Architected and developed a microservices-based e-commerce platform handling 500K daily transactions</li>
<li>Reduced page load time by 60% through implementation of lazy loading and code splitting</li>
<li>Mentored team of 4 junior developers and conducted code reviews</li>
<li>Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes</li>
</ul>

<h3><strong>Full Stack Developer</strong></h3>
<p><em>Digital Innovations Inc.</em>•<em>Portland, OR</em>•<em>Mar 2019 - Dec 2020</em></p>
<ul>
<li>Developed RESTful APIs serving mobile and web applications for 100K+ users</li>
<li>Migrated legacy monolithic application to microservices architecture</li>
<li>Improved database query performance by 40% through optimization</li>
</ul>

<h3><strong>Junior Web Developer</strong></h3>
<p><em>StartUp Hub</em>•<em>San Francisco, CA</em>•<em>Jun 2018 - Feb 2019</em></p>
<ul>
<li>Built responsive web interfaces using React and modern CSS frameworks</li>
<li>Participated in agile development process and daily stand-ups</li>
</ul>

<h2>Education</h2>
<h4>Master of Science in Computer Science</h4>
<p><em>University of Washington</em>•<em>Seattle, WA</em>•<em>Sep 2016 - Jun 2018</em></p>
<ul>
<li>GPA: 3.9/4.0, Specialization in Software Engineering</li>
<li>Thesis: "Optimizing Microservices Communication in Distributed Systems"</li>
</ul>

<h4>Bachelor of Science in Information Technology</h4>
<p><em>Oregon State University</em>•<em>Corvallis, OR</em>•<em>Sep 2012 - May 2016</em></p>
<ul>
<li>Graduated Summa Cum Laude, Computer Science Honor Society</li>
</ul>

<h2>Projects</h2>
<h3><strong>Task Management SaaS Platform</strong> | 2023</h3>
<p>Personal project building a full-featured task management application</p>
<ul>
<li>Developed using React, Node.js, and PostgreSQL with real-time updates via WebSockets</li>
<li>Implemented user authentication, team collaboration features, and payment integration</li>
<li>Deployed on AWS with auto-scaling and 99.9% uptime</li>
</ul>

<h2>Certifications</h2>
<ul>
<li>AWS Certified Developer - Associate</li>
<li>MongoDB Certified Developer</li>
<li>Google Cloud Professional Cloud Developer</li>
</ul>
```

#### 3.6.2 關鍵格式規則
- **區段標題**：使用 `<h2>` 標籤（Skills, Work Experience, Education, Projects, Certifications）
- **工作職位**：使用 `<h3><strong>` 標籤組合
- **學位名稱**：使用 `<h4>` 標籤
- **公司/學校資訊**：統一使用 `<em>` 標籤，並用 • 符號分隔
- **技能列表**：每個技能類別為一個 `<li>`，格式為 "類別名稱: 技能1, 技能2, 技能3"
- **專案標題**：使用 `<h3><strong>` 標籤，可包含日期資訊

## 4. 實作考量

### 4.1 技術架構
- 使用 Azure OpenAI GPT-4 進行智慧格式化
- BeautifulSoup 進行 HTML 解析和清理
- 正則表達式進行模式匹配和修正
- 快取機制避免重複處理相同內容

### 4.2 LLM Prompt 管理
- 使用 `UnifiedPromptService` 管理 Resume Format prompts
- Prompt 版本：v1.0（參考 legacy/Legacy_Code/prompts.py 第 197-364 行）
- 主要功能：
  - OCR 錯誤修正
  - 日期標準化和推算
  - 內容分類（個人專案 vs 工作專案）
  - HTML 結構生成
  - 佔位符處理

### 4.3 效能要求
- 平均處理時間：< 3 秒
- 最大輸入長度：50,000 字符
- 併發處理：支援每分鐘 60 個請求

### 4.4 錯誤處理策略
1. **完全無法解析**：返回基本模板並標註需要人工審核
2. **部分缺失**：使用佔位符並在 metadata 中標註
3. **格式異常**：盡力修正，記錄修正次數

## 5. 整合需求

### 5.1 與現有功能整合
- 可與關鍵詞提取功能結合，識別技能關鍵詞
- 可與差距分析功能結合，評估履歷品質
- 輸出格式與 Bubble.io 前端完全相容

### 5.2 監控指標
- OCR 錯誤修正率
- 各區段檢測成功率
- 處理時間分佈
- 語言分佈統計

## 6. 測試需求

### 6.1 單元測試
- OCR 錯誤修正功能
- 日期標準化邏輯
- HTML 安全處理
- 內容分類規則

### 6.2 整合測試
- 完整 API 流程
- 各種履歷格式處理
- 錯誤情況處理
- TinyMCE 相容性驗證

### 6.3 測試案例
1. 標準英文履歷
2. 繁體中文履歷
3. 雙語履歷
4. 缺失部分資訊的履歷
5. OCR 品質差的履歷

## 7. 安全考量

### 7.1 輸入驗證
- 最大長度限制：50,000 字符
- 禁止執行程式碼
- SQL 注入防護

### 7.2 輸出安全
- XSS 防護
- HTML 注入防護
- 安全的 HTML 白名單

## 8. 未來擴展

### 8.1 計劃功能
- 支援更多履歷格式（如 LinkedIn 匯出）
- AI 驅動的內容改進建議
- 多種輸出格式（PDF、Word）
- 履歷評分功能

### 8.2 版本規劃
- v1.0：基本格式化功能（當前）
- v1.1：增加內容優化建議
- v2.0：支援多種輸出格式

---

**下一步**：
1. 審核並確認需求
2. 建立相關 Work Items
3. 設計詳細技術架構
4. 開始實作開發