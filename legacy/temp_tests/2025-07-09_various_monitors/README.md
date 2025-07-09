# 2025-07-09 測試監控工具

此目錄包含 2025 年 7 月 9 日使用的各種監控和測試工具。

## 檔案清單

### 監控腳本
- `monitor_azure_test.sh` - Azure API 測試進度監控
- `monitor_local_test.py` - 本地測試進度監控
- `monitor_progress.py` - 一般進度監控
- `monitor_progress_live.py` - 即時進度監控
- `monitor_test_live.sh` - 即時測試監控
- `monitor_test_progress.py` - 測試進度監控
- `realtime_monitor.py` - 即時監控工具

### 檢查腳本
- `check_app_insights.sh` - Application Insights 檢查
- `check_test_output.sh` - 測試輸出檢查
- `check_test_status.sh` - 測試狀態檢查
- `check_content_variation.py` - 內容變化檢查

### 其他工具
- `estimate_completion.py` - 完成時間估算
- `force_check_progress.py` - 強制進度檢查

## 使用情境

這些工具主要用於監控 gap analysis API 的測試過程，特別是在調試空欄位問題時使用。

## 歸檔原因

- 這些是臨時性的監控工具
- 主要測試問題已解決
- 保留作為參考，但不屬於主要程式碼庫