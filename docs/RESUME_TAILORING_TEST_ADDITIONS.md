# Resume Tailoring 預提交測試整合說明

## 概述
本文檔說明為 Resume Tailoring 功能在 `run_precommit_tests.sh` 中添加的測試項目。

## 添加的測試項目

### 1. 單元測試 (Unit Tests)
**位置**: 第 210-211 行
```bash
run_test_category "Resume Tailoring Test" \
    "pytest tests/unit/test_resume_tailoring.py -v --tb=short"
```

**測試內容**:
- 服務初始化測試
- 英文履歷優化測試
- 繁體中文履歷優化測試
- 視覺標記開關測試
- 輸入驗證錯誤處理
- LLM 重試機制測試
- LLM 響應解析測試
- 優化統計計算測試
- STAR/PAR 格式標記移除測試

### 2. 整合測試 (Integration Tests)
**位置**: 第 227-228 行
```bash
run_test_category "Resume Tailoring API Test" \
    "pytest tests/integration/test_resume_tailoring_api.py -v --tb=short"
```

**測試內容**:
- API 端點成功響應測試
- 多語言支持測試（英文/繁體中文）
- 視覺標記控制測試
- 錯誤處理測試（驗證錯誤、服務器錯誤）
- 健康檢查端點測試
- 支持語言查詢端點測試
- Bubble.io 響應格式相容性測試

### 3. Prompt 文件檢查
**位置**: 第 300-320 行
```bash
# Check for required prompt files
echo -e "\n${YELLOW}Checking for required prompt files...${NC}"
missing_prompts=0
prompt_files=(
    "src/prompts/resume_tailoring/v1.0.0.yaml"
    # ... 其他 prompt 文件
)
```

**檢查項目**:
- 確保 `resume_tailoring/v1.0.0.yaml` 存在
- 與其他服務的 prompt 文件一起檢查

## 測試執行順序

1. **單元測試階段**:
   - Resume Tailoring Test 在 Resume Format Test 之後執行
   - 確保核心功能正常運作

2. **整合測試階段**:
   - Resume Tailoring API Test 在 Resume Format Integration Test 之後執行
   - 需要 API 服務器運行

## 測試考量

### 性能考量
- Resume Tailoring 涉及 LLM 調用，執行時間較長（約 10-30 秒）
- 在 CI/CD 環境中可能需要調整超時設置

### 依賴檢查
- 確保所有必要的 Python 套件已安裝
- 檢查環境變數配置（LLM2_API_KEY, EMBEDDING_API_KEY 等）

### 錯誤處理
- 測試會繼續執行即使單個測試失敗
- 最終摘要會顯示失敗的測試數量

## 使用建議

### 快速測試（跳過 API 測試）
```bash
./run_precommit_tests.sh --no-api
```
這會跳過需要 API 服務器的整合測試，適合快速檢查。

### 完整測試
```bash
./run_precommit_tests.sh
```
執行所有測試，包括需要 API 服務器的整合測試。

### 單獨測試 Resume Tailoring
```bash
# 只運行單元測試
pytest tests/unit/test_resume_tailoring.py -v

# 只運行整合測試
pytest tests/integration/test_resume_tailoring_api.py -v
```

## 預期結果

成功執行時應看到：
```
📋 Running Resume Tailoring Test...
✅ Resume Tailoring Test passed

📋 Running Resume Tailoring API Test...
✅ Resume Tailoring API Test passed
```

## 故障排除

1. **LLM API 錯誤**:
   - 檢查 `LLM2_API_KEY` 環境變數
   - 確認 Azure OpenAI 服務正常

2. **Prompt 文件缺失**:
   - 確保 `src/prompts/resume_tailoring/v1.0.0.yaml` 存在
   - 檢查文件權限

3. **整合測試失敗**:
   - 確認 API 服務器正在運行
   - 檢查端口 8000 是否可用