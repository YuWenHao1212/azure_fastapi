# 關鍵字標準化系統維護指南

**版本**: 1.0.0  
**最後更新**: 2025-07-02  
**維護者**: AI Resume Advisor 開發團隊

---

## 📋 目錄

1. [系統概述](#系統概述)
2. [快速開始（給一般使用者的白話說明）](#快速開始給一般使用者的白話說明)
3. [進階使用（給技術人員）](#進階使用給技術人員)
4. [維護工作流程](#維護工作流程)
5. [字典結構說明](#字典結構說明)
6. [新增映射指南](#新增映射指南)
7. [模式規則說明](#模式規則說明)
8. [測試與驗證](#測試與驗證)
9. [常見問題處理](#常見問題處理)
10. [最佳實踐](#最佳實踐)
11. [工具使用說明](#工具使用說明)

---

## 系統概述

關鍵字標準化系統將各種變體形式的技術術語統一為標準形式，提高關鍵字提取的一致性和準確性。

### 系統架構

```
src/
├── services/
│   └── keyword_standardizer.py    # 標準化服務主程式
└── data/
    └── standardization/           # 標準化資料目錄
        ├── skills.yaml           # 技能映射（250條）
        ├── positions.yaml        # 職位映射（95條）
        ├── tools.yaml            # 工具映射（170條）
        ├── patterns.yaml         # 模式規則（66條）
        ├── README.md             # 快速參考
        └── validate_dictionaries.py  # 驗證工具
```

### 核心功能

1. **字典映射**: 精確匹配並轉換為標準形式
2. **模式匹配**: 使用正則表達式處理變體
3. **組合策略**: 先模式後字典的智能匹配
4. **熱更新**: 支援不重啟服務更新映射

---

## 快速開始（給一般使用者的白話說明）

### 🎯 什麼是關鍵字標準化？

想像你在找「Python 工程師」的工作，但不同公司可能寫成：
- "python developer"
- "Python 開發者"
- "python programming"
- "py developer"

我們的系統會自動把這些都統一成「Python」，讓搜尋更準確！

### 📝 最簡單的使用方式：用 Excel 編輯

如果你不懂程式，沒關係！我們提供了 Excel 編輯的方式：

#### 步驟 1：匯出成 Excel 檔案
```bash
# 在終端機執行這個指令
cd src/data/standardization
python export_to_csv.py

# 會看到類似這樣的訊息：
# ✓ Exported 250 entries to csv_export/20250702_093000/skills.csv
# ✓ 匯出完成！請到 csv_export/20250702_093000 資料夾找檔案
```

#### 步驟 2：用 Excel 開啟編輯
1. 到 `csv_export/日期時間/` 資料夾
2. 用 Excel 開啟 CSV 檔案
3. 你會看到這樣的表格：

| Category | Original | Standardized | Notes |
|----------|----------|--------------|--------|
| programming_languages | python programming | Python | |
| programming_languages | java development | Java | |

4. 在 `Standardized` 欄位修改成你要的標準形式
5. 在最下方新增新的對應關係
6. 儲存檔案

#### 步驟 3：匯入修改後的檔案
```bash
# 先測試看看（不會真的修改）
python import_from_csv.py --input csv_export/20250702_093000 --dry-run

# 確認沒問題後，正式匯入（會自動備份）
python import_from_csv.py --input csv_export/20250702_093000 --backup
```

### 🔍 查詢現有的標準化規則

想知道某個關鍵字會被轉換成什麼？

```bash
# 查詢特定關鍵字
cd src/data/standardization
python analyze_usage.py --find "python"

# 會顯示：
# Found 5 matches:
# skills.yaml    python programming → Python
# skills.yaml    python development → Python
# positions.yaml python developer   → Python Developer
```

### 📊 查看統計資料

想了解目前有多少標準化規則？

```bash
python analyze_usage.py --detailed

# 會顯示完整統計報告，包括：
# - 總共有幾個對應規則
# - 哪些標準形式最常用
# - 有沒有衝突的規則
```

### ⚠️ 注意事項（重要！）

1. **不要改動 Original 欄位**：這是原始的關鍵字，改了系統就找不到了
2. **不要改欄位標題**：Category、Original、Standardized 這些標題不能改
3. **大小寫要注意**：Python 和 python 是不同的
4. **測試後再正式匯入**：用 --dry-run 先測試

### 🆘 遇到問題怎麼辦？

1. **驗證失敗**：檢查是否有重複的 Original 關鍵字
2. **匯入失敗**：確認 CSV 格式正確，欄位沒有被改動
3. **找不到檔案**：確認在正確的目錄執行指令

### 💡 實用技巧

1. **批次新增同類詞**：
   ```
   如果要加入 Kubernetes 的各種寫法：
   - kubernetes → Kubernetes
   - k8s → Kubernetes  
   - kube → Kubernetes
   ```

2. **保持一致性**：
   ```
   所有程式語言都用首字母大寫：
   - Python、Java、JavaScript（不是 python、JAVA、JS）
   ```

3. **定期備份**：
   系統會自動備份，但建議定期手動備份重要修改

---

## 進階使用（給技術人員）

### 1. 查看現有映射

```bash
# 查看技能映射
cat src/data/standardization/skills.yaml

# 搜尋特定關鍵字
grep -i "python" src/data/standardization/*.yaml
```

### 2. 新增簡單映射

在適當的 YAML 檔案中新增：
```yaml
category_name:
  原始關鍵字: 標準化關鍵字
  another keyword: Another Standard Form
```

### 3. 驗證變更

```bash
cd src/data/standardization
python validate_dictionaries.py
```

### 4. 測試標準化效果

```python
from src.services.keyword_standardizer import KeywordStandardizer

standardizer = KeywordStandardizer()
result, details = standardizer.standardize_keywords(
    ["python programming", "ml", "vscode"],
    include_details=True
)
print(result)  # ['Python', 'Machine Learning', 'VS Code']
```

---

## 維護工作流程

### 標準維護流程


::: mermaid
graph TD
    A[識別需要標準化的術語] --> B{術語類型?}
    B -->|技能| C[編輯 skills.yaml]
    B -->|職位| D[編輯 positions.yaml]
    B -->|工具| E[編輯 tools.yaml]
    B -->|通用模式| F[編輯 patterns.yaml]
    
    C --> G[執行驗證腳本]
    D --> G
    E --> G
    F --> G
    
    G --> H{驗證通過?}
    H -->|是| I[測試標準化效果]
    H -->|否| J[修正問題]
    J --> G
    
    I --> K[提交變更]
    K --> L[更新文檔];
:::


### 詳細步驟

#### 1. 識別需求
- 從使用者回饋收集非標準術語
- 分析系統日誌中的新關鍵字
- 定期審查業界新技術術語

#### 2. 分類術語
- **技能類**: 程式語言、框架、技術能力
- **職位類**: 職稱、角色名稱
- **工具類**: 軟體、平台、服務
- **通用模式**: 可用規則處理的變體

#### 3. 新增映射
```yaml
# 範例：新增 Rust 相關映射
programming_languages:
  rust programming: Rust
  rust development: Rust
  rust lang: Rust
  rustlang: Rust
```

#### 4. 驗證完整性
```bash
python validate_dictionaries.py
```

#### 5. 測試效果
```bash
# 使用測試腳本
python test_standardization.py

# 或使用 API 測試
curl -X POST http://localhost:8000/api/v1/extract-jd-keywords \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Looking for Rust programming expert"}'
```

---

## 字典結構說明

### skills.yaml 結構

```yaml
# 類別名稱（用於組織，不影響功能）
programming_languages:
  # 原始形式: 標準形式
  python programming: Python
  python development: Python
  py: Python

ai_ml:
  machine learning algorithms: Machine Learning
  ml algorithms: Machine Learning
  ml: Machine Learning
```

### 映射原則

1. **鍵（Key）規範**
   - 全部小寫
   - 保留空格
   - 不使用特殊字符

2. **值（Value）規範**
   - 保持正確的大小寫
   - 縮寫詞全大寫（AWS, API, SQL）
   - 專有名詞首字母大寫

3. **分類建議**
   - 相關技術放在同一類別
   - 每個類別控制在 50 條以內
   - 使用清晰的類別名稱

---

## 新增映射指南

### 決策流程圖

::: mermaid
graph TD
    A[新術語] --> B{是否已存在?}
    B -->|是| C[檢查映射是否正確]
    B -->|否| D{是否有明確標準形式?}
    
    D -->|是| E[新增字典映射]
    D -->|否| F{是否有通用模式?}
    
    F -->|是| G[新增模式規則]
    F -->|否| H[諮詢團隊決定標準]
    
    C -->|正確| I[無需修改]
    C -->|錯誤| J[更新映射]
:::



### 範例場景

#### 場景 1: 新程式語言
```yaml
# 在 skills.yaml 的 programming_languages 下新增
zig programming: Zig
zig language: Zig
zig dev: Zig
```

#### 場景 2: 新框架版本
```yaml
# 在 tools.yaml 的 web_frameworks 下新增
next.js 14: Next.js
nextjs 14: Next.js
# 注意：版本號通常會被模式規則移除
```

#### 場景 3: 新職位變體
```yaml
# 在 positions.yaml 的 ai_ml_roles 下新增
prompt engineer: Prompt Engineer
prompt engineering: Prompt Engineer
ai prompt engineer: Prompt Engineer
```

---

## 模式規則說明

### patterns.yaml 結構

```yaml
category_name:
  - pattern: '正則表達式'
    replacement: '替換文字'
    type: 'pattern類型'
    description: '規則說明'
```

### 常用模式類型

#### 1. 後綴移除 (suffix_removal)
```yaml
- pattern: '\s+programming$'
  replacement: ''
  type: suffix_removal
  description: 移除 "programming" 後綴
```

#### 2. 縮寫展開 (abbreviation)
```yaml
- pattern: '\bml\b'
  replacement: 'machine learning'
  type: abbreviation
  description: 展開 ML 為 machine learning
```

#### 3. 版本移除 (version_removal)
```yaml
- pattern: '\s+v?\d+(\.\d+)*$'
  replacement: ''
  type: version_removal
  description: 移除版本號（如 v2.0.1）
```

#### 4. 特殊字符 (special_char)
```yaml
- pattern: '[/\\&]'
  replacement: ' and '
  type: special_char
  description: 替換斜線和 & 為 "and"
```

### 新增模式規則

1. **測試正則表達式**
   ```python
   import re
   pattern = re.compile(r'\s+programming$', re.IGNORECASE)
   test = pattern.sub('', 'python programming')
   print(test)  # 應輸出: python
   ```

2. **考慮邊界情況**
   - 使用 `\b` 標記詞邊界
   - 考慮大小寫（使用 IGNORECASE）
   - 避免過度匹配

3. **記錄清楚**
   - 提供明確的 description
   - 選擇正確的 type
   - 給出匹配範例

---

## 測試與驗證

### 1. 單元測試

```python
# test_new_mappings.py
def test_rust_standardization():
    standardizer = KeywordStandardizer()
    
    test_cases = [
        ("rust programming", "Rust"),
        ("rust development", "Rust"),
        ("rustlang", "Rust"),
    ]
    
    for original, expected in test_cases:
        result, _ = standardizer.standardize_keywords([original])
        assert result[0] == expected, f"{original} should map to {expected}"
```

### 2. 整合測試

```bash
# 測試 API 端點
python test_standardization.py

# 檢查具體案例
curl -X POST http://localhost:8000/api/v1/extract-jd-keywords \
  -H "Content-Type: application/json" \
  -d @test_job_description.json
```

### 3. 驗證檢查清單

- [ ] 無重複鍵值（除非故意設計）
- [ ] 無自引用（key = value）
- [ ] 無循環引用（A→B→A）
- [ ] 正則表達式語法正確
- [ ] 標準形式拼寫正確
- [ ] 大小寫符合規範

---

## 常見問題處理

### Q1: 一個術語應該映射到技能還是工具？

**判斷原則**：
- 如果強調能力/知識 → skills.yaml
- 如果強調軟體/產品 → tools.yaml
- 如果兩者皆可，優先放在更常見的使用情境

**範例**：
- "docker" → 工具 (Docker)
- "containerization" → 技能 (Containerization)

### Q2: 發現映射錯誤如何修正？

1. 找到錯誤映射位置
   ```bash
   grep -n "錯誤術語" src/data/standardization/*.yaml
   ```

2. 修正映射
   ```yaml
   # 原本
   ptyhon: Pyhton  # 拼寫錯誤
   
   # 修正為
   python: Python
   ```

3. 驗證並測試
   ```bash
   python validate_dictionaries.py
   python test_standardization.py
   ```

### Q3: 如何處理一詞多義？

**策略**：
1. 保留最常見的含義
2. 使用上下文線索（未來功能）
3. 記錄在文檔中供參考

**範例**：
- "java" → Java (程式語言，不是咖啡或島嶼)
- "python" → Python (程式語言，不是蛇)

### Q4: 效能考量

- 字典載入時間：< 100ms
- 標準化處理：< 1ms per keyword
- 記憶體使用：< 10MB

如果字典過大影響效能：
1. 考慮分割字典
2. 實作延遲載入
3. 使用快取機制

---

## 最佳實踐

### ✅ 應該做

1. **保持一致性**
   - 相似術語使用相同的標準化策略
   - 遵循既定的命名規範

2. **定期審查**
   - 每月檢查新增術語
   - 每季度清理過時映射

3. **文檔同步**
   - 重大變更記錄在 CHANGE_LOG
   - 更新相關 API 文檔

4. **版本控制**
   - 使用有意義的提交訊息
   - 標記重要版本

### ❌ 避免做

1. **過度標準化**
   - 不要合併意義不同的術語
   - 保留必要的細節區分

2. **破壞性變更**
   - 避免修改已廣泛使用的映射
   - 考慮向後相容性

3. **複雜規則**
   - 模式規則保持簡單
   - 優先使用字典映射

4. **重複定義**
   - 檢查是否已存在類似映射
   - 使用驗證工具

---

## 工具使用說明

### validate_dictionaries.py

**功能**：檢查字典完整性和潛在問題

**使用方法**：
```bash
cd src/data/standardization
python validate_dictionaries.py
```

**輸出說明**：
- ✅ 綠色勾號：檢查通過
- ❌ 紅色叉號：發現問題需修正
- ⚠️ 黃色警告：潛在問題但可能是設計意圖

### 計劃中的工具

1. **export_to_csv.py**
   - 匯出字典為 Excel 格式
   - 方便非技術人員檢視和編輯

2. **import_from_csv.py**
   - 從 Excel 匯入更新
   - 支援批量更新

3. **diff_tool.py**
   - 比較不同版本的差異
   - 生成變更報告

4. **stats_generator.py**
   - 生成使用統計
   - 識別熱門和冷門映射

---

## 附錄

### A. 快速參考卡

| 檔案 | 用途 | 條目數 |
|------|------|--------|
| skills.yaml | 技能映射 | 250 |
| positions.yaml | 職位映射 | 95 |
| tools.yaml | 工具映射 | 170 |
| patterns.yaml | 模式規則 | 66 |

### B. 常用命令

```bash
# 搜尋關鍵字
grep -i "keyword" *.yaml

# 統計條目數
grep -c ":" skills.yaml

# 查看最近變更
git log -p -- *.yaml

# 比較版本差異
git diff HEAD~1 skills.yaml
```

### C. 聯絡資訊

- 技術問題：開發團隊 Slack #keyword-standardization
- 內容建議：提交 GitHub Issue
- 緊急修復：聯絡值班工程師

---

**文檔版本記錄**：
- v1.0.0 (2025-07-02): 初始版本