# 項目清理摘要 - 2025-07-07

## 清理成果
- 根目錄項目數從 69 個減少到 26 個（減少 62%）
- 保留所有必要的開發和部署文件
- 歷史文件有序歸檔到 legacy 目錄

## 移動的內容

### Azure 監控配置
- `azure/monitoring/` → `legacy/azure_configs/monitoring/`
- 包含 workbook 配置、查詢文檔、測試數據生成腳本

### Shell 腳本歸檔
1. **監控腳本** → `legacy/scripts/monitoring/`
   - check_all_telemetry.sh
   - diagnose_monitoring.sh
   - generate_test_data.sh
   - check_azure_config.sh
   - restart_function_app.sh
   - test_debug_endpoint.sh

2. **測試腳本** → `legacy/scripts/testing/`
   - run_tests.sh
   - run_quick_tests.sh
   - run_kpi_tests.sh
   - run_predeploy_tests.sh
   - test_api.sh

3. **設置腳本** → `legacy/scripts/setup/`
   - install_aliases.sh

### 臨時文檔
- 移至 `legacy/docs/temp_docs/`
  - CLEANUP_PLAN.md
  - CREATE_WORKBOOK_NOW.md
  - monitoring_setup.md
  - language_detection_decision_tree.md
  - TEST_SCRIPTS_SUMMARY.md
  - TESTING_PLAN.md
  - DESIGN_LANGUAGE_DETECTION_20250107.md

### 其他
- `archive/` → `legacy/archive/`
- `test_request.json` → `legacy/test_configs/`

## 保留的核心 Shell 腳本
1. **setup_env.sh** - 環境設置（必要）
2. **run_precommit_tests.sh** - 預提交測試（必要）
3. **start_dev.sh** - 開發服務器（必要）
4. **quick_setup.sh** - 快速設置（有用）

## 清理後的結構
```
azure_fastapi/
├── src/                    # 核心源代碼
├── tests/                  # 測試套件
├── docs/                   # 項目文檔
├── tools/                  # 開發工具
├── legacy/                 # 歷史歸檔
│   ├── azure_configs/      # Azure 配置
│   ├── scripts/            # 舊腳本
│   ├── docs/               # 歷史文檔
│   └── ...
├── .github/                # CI/CD
├── *.sh                    # 核心腳本（4個）
├── requirements.txt        # 依賴
├── pyproject.toml         # 項目配置
└── README.md              # 項目說明
```

## 注意事項
- 所有移動的文件都在 legacy 目錄中保留
- 不影響任何代碼運行或部署
- 可以隨時從 legacy 目錄恢復需要的文件