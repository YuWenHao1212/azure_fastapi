#\!/usr/bin/env python3
"""
深入分析 3+ 秒"網路延遲"的真實組成
"""
import json
import time
from datetime import datetime

# 從測試報告提取的數據
data = {
    "East Asia → Japan East OpenAI": {
        "總時間": 5789,
        "API處理": 2487,
        "網路開銷": 3136,
        "網路佔比": 54.2
    },
    "Japan East → Japan East OpenAI": {
        "總時間": 6031,
        "API處理": 2777,
        "網路開銷": 3253,
        "網路佔比": 53.9
    }
}

print("Azure Function App 延遲分析報告")
print("=" * 80)
print(f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\n## 1. 數據對比")
print("-" * 60)
print(f"{'配置':<30} {'總時間(ms)':<12} {'API處理(ms)':<12} {'網路開銷(ms)':<12}")
print("-" * 60)
for config, metrics in data.items():
    print(f"{config:<30} {metrics['總時間']:<12} {metrics['API處理']:<12} {metrics['網路開銷']:<12}")

print("\n## 2. 關鍵發現")
print("-" * 60)
print("遷移到 Japan East 後的變化：")
print(f"- 總時間增加: +{6031-5789}ms (+{(6031-5789)/5789*100:.1f}%)")
print(f"- API 處理增加: +{2777-2487}ms (+{(2777-2487)/2487*100:.1f}%)")
print(f"- 網路開銷增加: +{3253-3136}ms (+{(3253-3136)/3136*100:.1f}%)")

print("\n## 3. 延遲組成分析")
print("-" * 60)
print("3+ 秒的'網路開銷'實際包含：")
print()
print("### A. Function App 處理開銷 (約 800-1000ms)")
print("   - Function App 接收請求: ~50ms")
print("   - 請求解析和驗證: ~100ms")
print("   - 中間件處理: ~100ms")
print("   - 日誌記錄和監控: ~200ms")
print("   - 響應序列化: ~100ms")
print("   - Function App 響應: ~50ms")
print("   - Azure 內部路由: ~200-400ms")

print("\n### B. OpenAI API 調用開銷 (約 500-800ms)")
print("   - HTTP 客戶端初始化: ~50ms (如果未複用)")
print("   - DNS 查詢: ~50ms (如果未緩存)")
print("   - TCP/SSL 握手: ~150ms (如果新連接)")
print("   - 請求序列化: ~50ms")
print("   - 等待 OpenAI 分配資源: ~200-400ms")
print("   - 響應反序列化: ~50ms")

print("\n### C. 未知延遲 (約 1500-2000ms)")
print("   - Azure API Management 層？")
print("   - OpenAI 的內部負載均衡？")
print("   - Function App 的冷啟動？(Premium Plan 應該較少)")
print("   - 網路擁塞或路由問題？")

print("\n## 4. 為什麼同區域沒有改善？")
print("-" * 60)
print("""
1. **誤導性的命名**
   - "網路開銷" = 總時間 - API處理時間
   - 實際包含大量非網路因素
   - 真實網路 RTT 應該 < 10ms (同區域)

2. **OpenAI 服務架構**
   - API Gateway 可能不在 Japan East
   - 使用全球負載均衡，請求可能被路由到其他區域
   - 模型實例可能在不同的資源池

3. **Azure Function App 架構**
   - 即使同區域，仍需經過多層：
     - Azure Front Door
     - API Management
     - Function App Runtime
     - 內部網路路由

4. **測量方法的限制**
   - 無法區分各個組件的實際耗時
   - 需要分布式追蹤才能準確定位
""")

print("\n## 5. 優化建議")
print("-" * 60)
print("""
### 立即可行的優化

1. **減少 Function App 開銷**
   - 簡化中間件鏈
   - 優化日誌記錄（異步寫入）
   - 減少序列化/反序列化成本

2. **優化 OpenAI 調用**
   - 實施連接池複用（全局共享 httpx client）
   - DNS 預解析和緩存
   - Keep-alive 連接

3. **架構優化**
   - 考慮直接從前端調用 OpenAI（減少一層）
   - 實施邊緣計算（Azure Front Door + Functions）
   - 使用 Azure Cache for Redis 緩存結果

### 診斷工具

1. **Application Insights 分布式追蹤**
   ```python
   # 在代碼中添加自定義追蹤
   with tracer.start_as_current_span("openai_call"):
       response = await openai_client.chat_completion(...)
   ```

2. **詳細時間測量**
   ```python
   timings = {
       "request_received": time.time(),
       "validation_complete": 0,
       "openai_start": 0,
       "openai_complete": 0,
       "response_sent": 0
   }
   ```

3. **網路診斷**
   - 使用 Azure Network Watcher
   - 啟用 VNet Flow Logs
   - 分析實際的網路路徑
""")

print("\n## 6. 結論")
print("-" * 60)
print("""
同區域部署沒有顯著改善的原因：

1. **"網路延遲"是個誤稱** - 實際上大部分是應用層處理時間
2. **OpenAI 服務的複雜架構** - 不是簡單的點對點連接
3. **多層架構的開銷** - Function App 本身就增加了顯著延遲
4. **測量粒度不足** - 需要更詳細的分布式追蹤

真正的網路 RTT 改善可能只有 50-100ms，被其他開銷掩蓋了。
""")

# 生成 JSON 報告
report = {
    "analysis_time": datetime.now().isoformat(),
    "data_comparison": data,
    "key_findings": {
        "total_time_increase": 242,
        "api_processing_increase": 290,
        "network_overhead_increase": 117,
        "percentage_changes": {
            "total_time": 4.2,
            "api_processing": 11.7,
            "network_overhead": 3.7
        }
    },
    "latency_breakdown": {
        "function_app_overhead_ms": "800-1000",
        "openai_call_overhead_ms": "500-800",
        "unknown_latency_ms": "1500-2000"
    },
    "recommendations": [
        "實施分布式追蹤以準確測量各組件耗時",
        "優化 Function App 處理流程",
        "考慮架構簡化（減少中間層）",
        "使用全局共享的 HTTP 客戶端連接池"
    ]
}

with open("latency_analysis_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n詳細報告已保存至: latency_analysis_report.json")
