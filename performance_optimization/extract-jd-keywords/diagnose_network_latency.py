#\!/usr/bin/env python3
"""
診斷 Azure Function App 網路延遲問題
分析為什麼同區域（Japan East）部署沒有減少延遲
"""
import asyncio
import json
import time
import socket
import ssl
import httpx
from urllib.parse import urlparse
from datetime import datetime
import statistics

# 測試配置
# 測試配置 - Function Keys 需透過環境變數設定
import os

ENDPOINTS = {
    "east_asia": {
        "url": "https://airesumeadvisor-fastapi.azurewebsites.net",
        "key": os.getenv("AZURE_FUNCTION_KEY_EAST_ASIA", ""),  # Set via environment variable
        "region": "East Asia"
    },
    "japan_east": {
        "url": "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net", 
        "key": os.getenv("AZURE_FUNCTION_KEY_JAPAN_EAST", ""),  # Set via environment variable
        "region": "Japan East"
    }
}

# 簡單的測試 JD
TEST_JD = "Software engineer with Python experience needed for backend development."

async def measure_dns_lookup(hostname):
    """測量 DNS 查詢時間"""
    start = time.time()
    try:
        socket.gethostbyname(hostname)
        dns_time = (time.time() - start) * 1000
        return dns_time
    except:
        return -1

async def measure_tcp_handshake(hostname, port=443):
    """測量 TCP 連接時間"""
    start = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        ip = socket.gethostbyname(hostname)
        sock.connect((ip, port))
        tcp_time = (time.time() - start) * 1000
        sock.close()
        return tcp_time
    except:
        return -1

async def measure_ssl_handshake(hostname, port=443):
    """測量 SSL/TLS 握手時間"""
    context = ssl.create_default_context()
    start = time.time()
    try:
        ip = socket.gethostbyname(hostname)
        with socket.create_connection((ip, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ssl_time = (time.time() - start) * 1000
                return ssl_time
    except:
        return -1

async def test_api_call(endpoint_key, test_num=1):
    """測試單次 API 調用的詳細時間分解"""
    config = ENDPOINTS[endpoint_key]
    url = config["url"]
    hostname = urlparse(url).hostname
    
    print(f"\n測試 {test_num}: {config['region']} ({hostname})")
    print("=" * 60)
    
    # 1. DNS 查詢
    dns_time = await measure_dns_lookup(hostname)
    print(f"DNS 查詢時間: {dns_time:.2f}ms")
    
    # 2. TCP 連接
    tcp_time = await measure_tcp_handshake(hostname)
    print(f"TCP 握手時間: {tcp_time:.2f}ms")
    
    # 3. SSL 握手
    ssl_time = await measure_ssl_handshake(hostname)
    print(f"SSL 握手時間: {ssl_time:.2f}ms")
    
    # 4. 完整 API 調用
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 預熱連接
        warmup_start = time.time()
        await client.get(f"{url}/api/health")
        warmup_time = (time.time() - warmup_start) * 1000
        print(f"預熱連接時間: {warmup_time:.2f}ms")
        
        # 實際 API 調用
        api_start = time.time()
        response = await client.post(
            f"{url}/api/v1/extract-jd-keywords?code={config['key']}",
            json={
                "job_description": TEST_JD,
                "language": "en",
                "max_keywords": 10
            }
        )
        total_time = (time.time() - api_start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            api_processing_time = data.get("data", {}).get("processing_time_ms", 0)
            
            # 計算各部分時間
            network_overhead = total_time - api_processing_time
            
            print(f"\nAPI 調用結果:")
            print(f"  總時間: {total_time:.2f}ms")
            print(f"  API 處理時間: {api_processing_time:.2f}ms")
            print(f"  網路開銷: {network_overhead:.2f}ms")
            print(f"  網路開銷佔比: {(network_overhead/total_time*100):.1f}%")
            
            # 詳細分解
            print(f"\n時間分解估算:")
            print(f"  請求序列化: ~50ms")
            print(f"  Function App 冷啟動: 0ms (已預熱)")
            print(f"  API Gateway 路由: ~100ms")
            print(f"  響應反序列化: ~50ms")
            print(f"  未知延遲: {network_overhead - 200:.2f}ms")
            
            return {
                "region": config["region"],
                "total_ms": total_time,
                "api_ms": api_processing_time,
                "network_ms": network_overhead,
                "dns_ms": dns_time,
                "tcp_ms": tcp_time,
                "ssl_ms": ssl_time
            }
        else:
            print(f"API 調用失敗: {response.status_code}")
            return None

async def trace_route(hostname):
    """使用 curl 追蹤路由（macOS 沒有 traceroute 的 Python 庫）"""
    print(f"\n追蹤到 {hostname} 的路由...")
    import subprocess
    result = subprocess.run(
        f"curl -w '@-' -o /dev/null -s https://{hostname} << 'EOF'\ntime_namelookup:  %{{time_namelookup}}s\ntime_connect:  %{{time_connect}}s\ntime_appconnect:  %{{time_appconnect}}s\ntime_pretransfer:  %{{time_pretransfer}}s\ntime_redirect:  %{{time_redirect}}s\ntime_starttransfer:  %{{time_starttransfer}}s\ntime_total:  %{{time_total}}s\nEOF",
        shell=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)

async def main():
    print("Azure Function App 網路延遲診斷")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 測試兩個區域
    for endpoint_key in ["east_asia", "japan_east"]:
        result = await test_api_call(endpoint_key, len(results) + 1)
        if result:
            results.append(result)
        await asyncio.sleep(1)  # 避免過快請求
    
    # 總結比較
    if len(results) == 2:
        print("\n\n總結比較")
        print("=" * 80)
        print(f"{'指標':<20} {'East Asia':>15} {'Japan East':>15} {'差異':>15}")
        print("-" * 65)
        
        metrics = ["total_ms", "api_ms", "network_ms", "dns_ms", "tcp_ms", "ssl_ms"]
        for metric in metrics:
            ea_val = results[0][metric]
            je_val = results[1][metric]
            diff = je_val - ea_val
            diff_pct = (diff / ea_val * 100) if ea_val > 0 else 0
            
            metric_name = {
                "total_ms": "總時間",
                "api_ms": "API 處理",
                "network_ms": "網路開銷",
                "dns_ms": "DNS 查詢",
                "tcp_ms": "TCP 握手",
                "ssl_ms": "SSL 握手"
            }.get(metric, metric)
            
            print(f"{metric_name:<20} {ea_val:>13.2f}ms {je_val:>13.2f}ms {diff:>+13.2f}ms ({diff_pct:+.1f}%)")
    
    # 追蹤路由（選擇性）
    print("\n是否要追蹤詳細路由？這可能需要較長時間。(y/n): ", end="")
    # 自動跳過，避免交互
    print("n")
    
    print("\n\n可能的原因分析:")
    print("=" * 80)
    print("""
1. **"網路延遲"的誤導性命名**
   - 實際包含: Function App 處理開銷、API Gateway、序列化/反序列化
   - 真正的網路 RTT 可能只有 <100ms

2. **Function App 內部架構**
   - 即使在同區域，仍需經過多層路由
   - Azure 內部網路可能不是直連

3. **OpenAI 服務架構**
   - API 端點可能是全球負載均衡
   - 實際處理可能不在 Japan East

4. **測量方法問題**
   - total_time - api_processing_time 包含太多非網路因素
   - 需要更細粒度的測量

建議的優化方向:
- 使用 Application Insights 追蹤詳細的依賴調用
- 考慮使用 Premium Plan 減少冷啟動
- 實施請求批處理減少往返次數
- 優化 API 處理邏輯本身
""")

if __name__ == "__main__":
    asyncio.run(main())
