# Azure DevOps Wiki 文檔導出指南

## 方法 1：使用 Azure CLI (推薦)

```bash
# 1. 確保已登錄
az login --tenant wenhaoairesumeadvisor.onmicrosoft.com

# 2. 設置默認值
az devops configure --defaults organization=https://dev.azure.com/airesumeadvisor project=API

# 3. 列出所有 Wiki
az repos list --output table

# 4. 克隆 Wiki 倉庫（Wiki 在 Azure DevOps 中是 Git 倉庫）
git clone https://airesumeadvisor@dev.azure.com/airesumeadvisor/API/_git/API.wiki

# 5. 或使用 REST API 獲取頁面
az rest --method get --uri "https://dev.azure.com/airesumeadvisor/API/_apis/wiki/wikis/API.wiki/pages?path=/&recursionLevel=full&api-version=7.0"
```

## 方法 2：手動導出

1. 訪問 https://dev.azure.com/airesumeadvisor/API/_wiki/wikis/API.wiki
2. 瀏覽到各個文檔頁面
3. 使用瀏覽器的"另存為"功能或複製內容

## 方法 3：使用 Git（如果 Wiki 是代碼倉庫）

```bash
# 克隆 Wiki 倉庫
git clone https://dev.azure.com/airesumeadvisor/_git/API.wiki wiki-export

# 查看內容
cd wiki-export
ls -la
```

## 預期的文檔結構

根據 CLAUDE.md，應該包含：
```
Wiki/
├── Published/
│   ├── API/
│   │   ├── API_KEYWORD_EXTRACTION_V3.md
│   │   ├── API_BILINGUAL_KEYWORD_EXTRACTION.md
│   │   └── API_QUICK_REFERENCE.md
│   ├── Design/
│   │   ├── DESIGN_FHS_ARCHITECTURE.md
│   │   ├── DESIGN_KEYWORD_EXTRACTION.md
│   │   └── DESIGN_LANGUAGE_DETECTION.md
│   ├── Requirements/
│   │   ├── REQ_KEYWORD_EXTRACTION.md
│   │   └── REQ_BILINGUAL_KEYWORD.md
│   └── Implementation/
│       └── IMPLEMENTATION_BILINGUAL_SYSTEM.md
└── Work_Items/
    └── [各種 Work Item 記錄]
```

## 導出後的對比步驟

1. **結構對比**：檢查文檔組織是否一致
2. **內容對比**：使用 diff 工具比較內容差異
3. **版本確認**：確認哪個版本更新、更準確
4. **整合更新**：將 Wiki 中的獨特內容合併到本地文檔

## 注意事項
- Wiki 可能需要特定權限才能訪問
- 某些內容可能包含敏感信息（如 API Keys）
- 導出時注意保持文檔格式（Markdown）