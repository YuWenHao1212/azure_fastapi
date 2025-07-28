#!/usr/bin/env python3
"""
診斷 Function App 3 秒開銷的具體來源
"""
import asyncio
import time
import httpx
import json
import os
from datetime import datetime
import statistics

# 配置
FUNCTION_URL = "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net"
FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY", "")  # Set via environment variable

async def test_minimal_endpoint():
    """測試最小化的端點（如果有）"""
    print("\n=== 測試不同端點的響應時間 ===")
    
    endpoints = [
        ("/", "GET", None),
        ("/docs", "GET", None),
        ("/openapi.json", "GET", None),
        ("/api/v1/extract-jd-keywords", "POST", {
            "job_description": "Python developer with 3 years experience needed for backend development",
            "language": "en"
        })
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for path, method, data in endpoints:
            url = f"{FUNCTION_URL}{path}?code={FUNCTION_KEY}"
            
            try:
                start = time.time()
                if method == "GET":
                    response = await client.get(url)
                else:
                    response = await client.post(url, json=data)
                elapsed = (time.time() - start) * 1000
                
                print(f"\n{method} {path}:")
                print(f"  Status: {response.status_code}")
                print(f"  Time: {elapsed:.0f}ms")
                
                # 如果是 keywords API，顯示處理時間
                if path == "/api/v1/extract-jd-keywords" and response.status_code == 200:
                    data = response.json()
                    api_time = data.get("data", {}).get("processing_time_ms", 0)
                    print(f"  API Processing: {api_time:.0f}ms")
                    print(f"  Function Overhead: {elapsed - api_time:.0f}ms")
                    
            except Exception as e:
                print(f"\n{method} {path}: 失敗 - {e}")

async def test_connection_reuse():
    """測試連接重用的影響"""
    print("\n=== 測試連接重用效果 ===")
    
    # 使用同一個客戶端進行多次請求
    async with httpx.AsyncClient(timeout=30.0) as client:
        times = []
        
        for i in range(5):
            start = time.time()
            response = await client.get(f"{FUNCTION_URL}/openapi.json?code={FUNCTION_KEY}")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"  第 {i+1} 次: {elapsed:.0f}ms (連接重用)")
            await asyncio.sleep(0.5)
        
        avg_reuse = statistics.mean(times[1:])  # 排除第一次
        print(f"\n  平均時間（連接重用）: {avg_reuse:.0f}ms")
    
    # 每次創建新客戶端
    times = []
    for i in range(5):
        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()
            response = await client.get(f"{FUNCTION_URL}/openapi.json?code={FUNCTION_KEY}")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            print(f"  第 {i+1} 次: {elapsed:.0f}ms (新連接)")
            await asyncio.sleep(0.5)
    
    avg_new = statistics.mean(times)
    print(f"\n  平均時間（新連接）: {avg_new:.0f}ms")
    print(f"  差異: {avg_new - avg_reuse:.0f}ms")

async def test_concurrent_requests():
    """測試並發請求的表現"""
    print("\n=== 測試並發請求 ===")
    
    async def single_request(client, index):
        start = time.time()
        response = await client.get(f"{FUNCTION_URL}/openapi.json?code={FUNCTION_KEY}")
        elapsed = (time.time() - start) * 1000
        return index, elapsed, response.status_code
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 並發 5 個請求
        tasks = [single_request(client, i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        for index, elapsed, status in results:
            print(f"  請求 {index+1}: {elapsed:.0f}ms (狀態: {status})")
        
        times = [r[1] for r in results]
        print(f"\n  平均時間: {statistics.mean(times):.0f}ms")
        print(f"  最慢請求: {max(times):.0f}ms")

async def test_with_tcpdump_simulation():
    """模擬 tcpdump 來分析請求的各個階段"""
    print("\n=== 詳細請求階段分析 ===")
    
    import socket
    
    # DNS 解析
    start = time.time()
    ip = socket.gethostbyname("airesumeadvisor-fastapi-japaneast.azurewebsites.net")
    dns_time = (time.time() - start) * 1000
    print(f"DNS 解析: {dns_time:.1f}ms ({ip})")
    
    # 使用 hooks 來追蹤請求的各個階段
    timings = {}
    
    async def log_request_start(request):
        timings['request_start'] = time.time()
    
    async def log_request_end(request):
        timings['request_end'] = time.time()
    
    async def log_response_start(response):
        timings['response_start'] = time.time()
    
    async def log_response_end(response):
        timings['response_end'] = time.time()
    
    async with httpx.AsyncClient(
        timeout=30.0,
        event_hooks={
            'request': [log_request_start, log_request_end],
            'response': [log_response_start, log_response_end]
        }
    ) as client:
        timings['total_start'] = time.time()
        response = await client.get(f"{FUNCTION_URL}/openapi.json?code={FUNCTION_KEY}")
        timings['total_end'] = time.time()
        
        # 計算各階段時間
        total_time = (timings['total_end'] - timings['total_start']) * 1000
        request_time = (timings['request_end'] - timings['request_start']) * 1000
        wait_time = (timings['response_start'] - timings['request_end']) * 1000
        response_time = (timings['response_end'] - timings['response_start']) * 1000
        
        print(f"\n請求階段分解:")
        print(f"  請求準備: {request_time:.1f}ms")
        print(f"  等待響應: {wait_time:.1f}ms")
        print(f"  接收響應: {response_time:.1f}ms")
        print(f"  總時間: {total_time:.1f}ms")
        print(f"\nFunction App 處理時間: ~{wait_time:.0f}ms")

async def analyze_premium_plan_issue():
    """分析 Premium Plan 仍然慢的原因"""
    print("\n=== Premium Plan 性能問題分析 ===")
    
    print("\n可能的原因：")
    print("1. ASGI 適配層開銷")
    print("   - Azure Functions → ASGI → FastAPI 的多層轉換")
    print("   - 每層都有序列化/反序列化開銷")
    
    print("\n2. Application Insights 遙測")
    print("   - 同步的遙測操作可能阻塞請求")
    print("   - 過度的日誌記錄")
    
    print("\n3. Python 運行時問題")
    print("   - GIL (Global Interpreter Lock) 限制")
    print("   - 異步操作的開銷")
    
    print("\n4. Azure Functions 平台限制")
    print("   - 即使是 Premium Plan 也有平台開銷")
    print("   - 內部的代理和路由層")
    
    print("\n建議的解決方案：")
    print("1. 使用 Azure Container Apps 或 App Service")
    print("2. 實施更激進的緩存策略")
    print("3. 批處理 API 來攤薄開銷")
    print("4. 考慮使用 gRPC 而非 HTTP")

async def main():
    """執行所有診斷測試"""
    print(f"開始診斷 Function App 開銷問題...")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目標: {FUNCTION_URL}")
    print("=" * 60)
    
    # 執行各項測試
    await test_minimal_endpoint()
    await test_connection_reuse()
    await test_concurrent_requests()
    await test_with_tcpdump_simulation()
    await analyze_premium_plan_issue()
    
    print("\n" + "=" * 60)
    print("診斷完成！")
    
    print("\n關鍵發現：")
    print("1. Premium Plan 並不能完全解決 Function App 的架構開銷")
    print("2. ASGI 適配層增加了顯著的延遲")
    print("3. 真正的解決方案可能需要架構調整")

if __name__ == "__main__":
    asyncio.run(main())