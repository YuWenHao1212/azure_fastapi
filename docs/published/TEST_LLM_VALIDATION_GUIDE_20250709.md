# LLM 驗證測試指南

**文檔版本**: 1.0.0  
**建立日期**: 2025-07-09  
**作者**: Claude Code + WenHao  
**目的**: 記錄 LLM API 驗證測試的標準程序和工具

## 概述

本文檔記錄了驗證 LLM API 回應品質的測試方法，特別是檢查 API 是否正確回傳 LLM 生成的內容，而非預設或空白訊息。這是確保 LLM 整合穩定性的重要步驟。

## 測試工具

### 主要測試腳本
- **檔案**: `test_gap_analysis_with_detailed_logging.py`
- **位置**: 專案根目錄
- **功能**: 
  - 驗證 Gap Analysis API 的回應品質
  - 檢測空白或預設訊息
  - 記錄詳細的請求和回應
  - 生成統計報告

### 測試特點
1. **雙模式支援**: 本地測試和 Azure Function App 測試
2. **詳細日誌**: 同時輸出到控制台和檔案
3. **自動檢測**: 識別預設訊息和空白欄位
4. **批次測試**: 支援大量測試執行
5. **結構化輸出**: JSON 格式保存每個測試結果

## 使用方法

### 1. 基本測試執行

```bash
# 執行 3 次測試（預設）
python test_gap_analysis_with_detailed_logging.py

# 執行指定次數測試
python test_gap_analysis_with_detailed_logging.py 10
```

### 2. 背景執行大量測試

#### 使用 nohup（推薦）
```bash
# 在背景執行 100 次測試
nohup python test_gap_analysis_with_detailed_logging.py 100 > test_100_output.log 2>&1 &

# 記錄 process ID
echo $! > test_pid.txt

# 監控執行狀態
tail -f test_100_output.log
```

#### 使用 screen
```bash
# 建立 screen session
screen -S gap_test

# 執行測試
python test_gap_analysis_with_detailed_logging.py 100

# Detach: Ctrl+A, D
# 重新連接
screen -r gap_test
```

### 3. 測試模式設定

```bash
# 本地測試
TEST_MODE=local python test_gap_analysis_with_detailed_logging.py

# Azure 測試（需要 host key）
TEST_MODE=azure python test_gap_analysis_with_detailed_logging.py
```

### 4. 監控測試進度

```bash
# 即時查看測試進度
tail -f gap_analysis_test_results_*/gap_analysis_test_*.log | grep -E "Test #|Summary"

# 計算已完成測試數
watch -n 5 'ls gap_analysis_test_results_*/test_*.json 2>/dev/null | wc -l'

# 檢查錯誤
tail -f gap_analysis_test_results_*/gap_analysis_test_*.log | grep -E "ERROR|empty"
```

### 5. 停止測試

```bash
# 使用記錄的 PID
kill $(cat test_pid.txt)

# 或手動查找
ps aux | grep test_gap_analysis_with_detailed_logging
kill <PID>
```

## 輸出結構

測試會產生以下檔案結構：

```
gap_analysis_test_results_YYYYMMDD_HHMMSS/
├── gap_analysis_test_YYYYMMDD_HHMMSS.log  # 詳細執行日誌
├── test_001_ok.json                        # 成功的測試結果
├── test_002_error.json                     # 失敗的測試結果
└── test_summary.json                       # 測試總結報告
```

### 日誌內容範例

```
2025-07-09 14:04:07 - root - INFO - Starting Test #1
2025-07-09 14:04:07 - root - INFO - Request Details:
2025-07-09 14:04:07 - root - INFO -   URL: https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/index-cal-and-gap-analysis
2025-07-09 14:04:07 - root - INFO -   Language: en
2025-07-09 14:04:07 - root - INFO -   Keywords: 14 items
2025-07-09 14:04:26 - root - INFO - Response received in 19.64 seconds
2025-07-09 14:04:26 - root - INFO - Field 'CoreStrengths': 101 words, 5 items
2025-07-09 14:04:26 - root - INFO - Test Summary:
2025-07-09 14:04:26 - root - INFO -   ✓ API Response: Success
2025-07-09 14:04:26 - root - INFO -   ✓ All Fields Valid: True
```

### JSON 結果範例

```json
{
  "test_number": 1,
  "timestamp": "2025-07-09T14:04:26.123456",
  "duration_seconds": 19.64,
  "all_fields_valid": true,
  "analysis": {
    "CoreStrengths": {
      "content_length": 523,
      "word_count": 101,
      "item_count": 5,
      "has_substantial_content": true
    },
    "OverallAssessment": {
      "content_length": 856,
      "word_count": 165,
      "has_substantial_content": true
    }
  },
  "errors": []
}
```

## 檢查的預設訊息

腳本會檢查以下預設/錯誤訊息：

### 列表欄位 (CoreStrengths, KeyGaps, QuickImprovements)
- `<ol></ol>` - 空列表
- `<ol><li>Unable to analyze ... Please try again.</li></ol>` - 錯誤訊息

### 段落欄位 (OverallAssessment)
- `<p></p>` - 空段落
- `<p>Unable to generate a comprehensive assessment...</p>`
- `<p>Unable to generate overall assessment...</p>`
- `<p>Overall assessment not available...</p>`

### 陣列欄位 (SkillSearchQueries)
- `[]` - 空陣列

## 成功標準

測試被視為成功當：
1. API 回應狀態碼為 200
2. 所有欄位都包含實質內容（非空白、非預設訊息）
3. SkillSearchQueries 包含至少一個技能項目
4. 回應時間在合理範圍內（通常 15-30 秒）

## 實際測試結果

### 2025-07-09 測試總結
- **測試次數**: 76 次
- **成功率**: 100%
- **空白欄位**: 0
- **平均回應時間**: 19.64 秒
- **結論**: API 穩定可靠，LLM 整合正常運作

## 故障排除

### 連線超時
- 增加 timeout 設定（目前為 120 秒）
- 檢查網路連線
- 確認 Azure Function App 運行狀態

### 認證失敗
- 檢查 host key 是否正確
- 確認 .env 檔案設定
- 驗證 Azure Function App 的認證設定

### 空白欄位
- 檢查 LLM API key 有效性
- 查看詳細日誌中的錯誤訊息
- 確認 prompt 設定正確
- 檢查 LLM 服務狀態

## 最佳實踐

1. **定期執行**: 建議每週執行一次完整測試
2. **監控趨勢**: 追蹤成功率和回應時間的變化
3. **保存結果**: 歸檔測試結果以供未來比較
4. **異常處理**: 發現問題立即調查原因

## 相關文件

- [Gap Analysis Service 實作](../../../src/services/gap_analysis.py)
- [LLM 呼叫最佳實踐](../../../CLAUDE.md#llm-呼叫最佳實踐-重要教訓---20250709)
- [測試策略與管理](../../../CLAUDE.md#測試策略與管理)

---

**維護說明**: 此測試方法已被證明有效，應作為所有 LLM API 驗證的標準程序。