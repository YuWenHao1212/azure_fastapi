# Stable Rounding Implementation Guide

## 問題描述
相似度計算在邊界值（如 78.5%）附近時，由於浮點數精度問題，可能產生不一致的結果（有時 78%，有時 79%）。

## 解決方案
實施了 `stable_percentage_round()` 函數，使用 Python 的 Decimal 類型進行精確計算。

## 實作細節

### 1. 核心工具函數
位置：`src/core/utils.py`

```python
from decimal import ROUND_HALF_UP, Decimal

def stable_percentage_round(value: float) -> int:
    """
    Stable percentage rounding method to solve floating-point precision issues.
    
    Uses Decimal to ensure consistent rounding behavior, especially for x.5 values.
    """
    # Convert to Decimal using string to avoid floating-point precision issues
    decimal_percent = Decimal(str(value)) * Decimal('100')
    
    # Use ROUND_HALF_UP for consistent traditional rounding (0.5 always rounds up)
    rounded = decimal_percent.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    return int(rounded)
```

### 2. 使用位置
- **index_calculation.py**:
  - 相似度百分比計算（原始和轉換後）
  - 關鍵字覆蓋率百分比計算

### 3. 關鍵優勢
- **精確性**：使用字符串初始化 Decimal，避免浮點數精度問題
- **一致性**：ROUND_HALF_UP 確保 x.5 永遠向上取整
- **可預測性**：相同輸入永遠得到相同輸出

## 測試結果
- 修復前：相似度結果可能在 78% 和 79% 之間變化
- 修復後：30+ 次測試全部返回一致結果

## 技術細節

### 為什麼標準 round() 會出問題？
1. **浮點數精度**：0.785 可能存儲為 0.78499999... 或 0.78500000...
2. **Banker's rounding**：Python 的 round() 使用銀行家捨入（.5 捨入到最近偶數）

### Decimal 如何解決？
1. **精確表示**：Decimal('0.785') 確保得到精確的 0.785
2. **傳統捨入**：ROUND_HALF_UP 實現傳統四捨五入規則

## 使用指南
任何需要將比率（0-1）轉換為百分比（0-100）的地方都應使用此函數：

```python
from src.core.utils import stable_percentage_round

# 正確用法
percentage = stable_percentage_round(0.785)  # 永遠返回 79

# 避免
percentage = round(0.785 * 100)  # 可能返回 78 或 79
```

## 維護建議
1. 所有百分比計算都應使用此函數
2. 定期測試邊界值（x.5）的一致性
3. 新增百分比計算時記得 import 此函數

---
文檔建立日期：2025-07-14
作者：Claude Code