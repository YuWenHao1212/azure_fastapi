# 項目清理計劃

## 目錄分析與處理建議

### 需要保留的目錄 ✅
- **src/** - 核心源代碼
- **tests/** - 測試文件
- **.github/** - GitHub Actions 配置
- **docs/** - 項目文檔
- **.venv/** - Python 虛擬環境
- **.vscode/** - VS Code 配置

### 可以移至 legacy 的目錄 🔄
1. **azure/monitoring/** - Azure 監控配置文件
   - 原因：這些是配置文件，不是代碼依賴
   - 操作：移至 `legacy/azure_configs/monitoring/`

2. **keyword_extraction/** - 空目錄
   - 原因：目錄為空
   - 操作：刪除

3. **archive/** - 臨時測試輸出
   - 原因：已經是歸檔內容
   - 操作：移至 `legacy/archive/`

### Shell 腳本分類

#### 必要保留的 .sh 文件 ✅
1. **setup_env.sh** - 環境設置
2. **run_precommit_tests.sh** - 預提交測試
3. **start_dev.sh** - 開發服務器啟動
4. **quick_setup.sh** - 快速設置

#### 可以歸檔的 .sh 文件 📦
1. **監控相關** (7月6日創建的臨時腳本)：
   - check_all_telemetry.sh
   - check_azure_config.sh
   - diagnose_monitoring.sh
   - generate_test_data.sh
   - restart_function_app.sh
   - test_debug_endpoint.sh

2. **測試相關** (可用 run_precommit_tests.sh 替代)：
   - run_tests.sh
   - run_quick_tests.sh
   - run_kpi_tests.sh
   - run_predeploy_tests.sh
   - test_api.sh

3. **其他**：
   - install_aliases.sh (一次性設置)

## 執行計劃

```bash
# 1. 創建 legacy 子目錄
mkdir -p legacy/azure_configs/monitoring
mkdir -p legacy/scripts/monitoring
mkdir -p legacy/scripts/testing
mkdir -p legacy/scripts/setup

# 2. 移動 azure/monitoring
mv azure/monitoring/* legacy/azure_configs/monitoring/

# 3. 移動監控相關腳本
mv check_all_telemetry.sh diagnose_monitoring.sh generate_test_data.sh \
   check_azure_config.sh restart_function_app.sh test_debug_endpoint.sh \
   legacy/scripts/monitoring/

# 4. 移動測試相關腳本
mv run_tests.sh run_quick_tests.sh run_kpi_tests.sh \
   run_predeploy_tests.sh test_api.sh \
   legacy/scripts/testing/

# 5. 移動設置腳本
mv install_aliases.sh legacy/scripts/setup/

# 6. 移動 archive
mv archive/* legacy/archive/

# 7. 刪除空目錄
rmdir keyword_extraction archive azure/monitoring azure
```

## 清理後的根目錄結構

```
azure_fastapi/
├── src/                    # 源代碼
├── tests/                  # 測試
├── docs/                   # 文檔
├── tools/                  # 工具腳本
├── legacy/                 # 歷史文件
├── .github/                # CI/CD
├── setup_env.sh           # 環境設置
├── run_precommit_tests.sh # 測試腳本
├── start_dev.sh           # 開發啟動
├── quick_setup.sh         # 快速設置
├── pyproject.toml         # Python 項目配置
├── requirements.txt       # 依賴
├── README.md              # 項目說明
└── .gitignore             # Git 忽略規則
```

## 預期效果
- 根目錄從 69 個項目減少到約 20 個
- 保留所有必要的開發工具
- 歷史文件有序歸檔
- 不影響任何代碼運行