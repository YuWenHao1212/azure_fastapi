# 預提交測試超時解決方案

## 問題描述

`./run_precommit_tests.sh` 在 Claude Code 環境中執行時可能會遇到 2 分鐘超時限制，特別是在以下情況：
- 運行完整測試套件
- 生成覆蓋率報告
- 執行安全測試和文檔測試
- 使用單線程執行

## 解決方案

### 方案 1：使用並行執行（推薦）

```bash
# 使用並行執行顯著減少測試時間
./run_precommit_tests.sh --parallel
```

**優點**：
- 利用多核心 CPU
- 測試時間減少 50-70%
- 通常可在 2 分鐘內完成

### 方案 2：快速測試腳本

使用輕量級測試腳本進行快速驗證：

```bash
# 執行快速測試（< 30 秒）
./run_precommit_tests_quick.sh
```

**包含內容**：
- 代碼風格檢查
- 核心單元測試
- 基本健康檢查

### 方案 3：分階段測試

將測試分成多個階段執行：

```bash
# 階段 1：代碼品質
ruff check src/ tests/ --exclude=legacy,archive,temp

# 階段 2：單元測試
pytest tests/unit/ -v --tb=short

# 階段 3：整合測試（如果需要）
pytest tests/integration/ -v --tb=short

# 階段 4：覆蓋率報告（可選）
pytest --cov=src --cov-report=html tests/unit/ -q
```

### 方案 4：跳過 API 測試

如果只修改了文檔或配置：

```bash
# 跳過需要 API 的測試
./run_precommit_tests.sh --no-api
```

### 方案 5：直接在終端執行

在 Claude Code 外部直接執行：

```bash
# 在終端中執行完整測試
./run_precommit_tests.sh

# 或使用 nohup 背景執行
nohup ./run_precommit_tests.sh > test_results.log 2>&1 &
tail -f test_results.log
```

## 測試時間優化建議

### 1. 預設使用並行

修改 `.bashrc` 或 `.zshrc`：

```bash
alias precommit='./run_precommit_tests.sh --parallel'
```

### 2. 根據修改選擇測試

| 修改類型 | 建議命令 |
|---------|---------|
| 只改文檔 | `./run_precommit_tests.sh --no-api` |
| 改代碼 | `./run_precommit_tests.sh --parallel` |
| 緊急修復 | `./run_precommit_tests_quick.sh` |
| 完整驗證 | 終端執行 `./run_precommit_tests.sh` |

### 3. CI/CD 依賴

由於已設置 CI/CD：
1. 本地可執行快速測試
2. 推送後 CI/CD 會執行完整測試
3. 部署前會自動驗證

## 實際使用流程

### 日常開發

```bash
# 1. 開發完成後，快速驗證
./run_precommit_tests_quick.sh

# 2. 如果通過，執行並行測試
./run_precommit_tests.sh --parallel

# 3. 提交代碼
git add -A && git commit -m "feat: your feature"

# 4. 推送（CI/CD 會執行完整測試）
git push origin main
```

### 重要發布

```bash
# 1. 在終端執行完整測試
./run_precommit_tests.sh

# 2. 檢查覆蓋率報告
open htmlcov/index.html

# 3. 確認所有測試通過後提交
git add -A && git commit -m "release: v1.0.0"
```

## 測試執行時間參考

| 測試類型 | 單線程 | 並行 | 快速版 |
|---------|--------|------|--------|
| 單元測試 | ~60s | ~20s | ~10s |
| 整合測試 | ~90s | ~30s | 跳過 |
| 安全測試 | ~60s | ~20s | 跳過 |
| 文檔測試 | ~30s | ~15s | 跳過 |
| 覆蓋率 | ~30s | ~20s | 跳過 |
| **總計** | ~4.5分 | ~1.5分 | <30秒 |

## 總結

1. **日常使用**：`./run_precommit_tests.sh --parallel`
2. **快速檢查**：`./run_precommit_tests_quick.sh`
3. **完整驗證**：在終端執行完整測試
4. **依賴 CI/CD**：本地快速測試 + 雲端完整驗證

選擇適合當前情況的測試策略，平衡速度與完整性！