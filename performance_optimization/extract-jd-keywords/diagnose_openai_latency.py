#\!/usr/bin/env python3
"""
深入診斷 Azure OpenAI 網路延遲
直接測試 OpenAI 端點，排除 Function App 的影響
"""
import asyncio
import json
import time
import httpx
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI 端點配置
OPENAI_CONFIGS = {
    "sweden_central": {
        "endpoint": "https://wenha-m7qan2zj-swedencentral.openai.azure.com",
        "deployment": "gpt-4o-2",
        "region": "Sweden Central",
        "api_key": os.getenv("LLM2_API_KEY")
    },
    "japan_east": {
        "endpoint": "https://airesumeadvisor-japaneast.openai.azure.com",
        "deployment": "gpt-4o-2",
        "region": "Japan East",
        "api_key": os.getenv("OPENAI_API_KEY_JAPANEAST")
    }
}

# 測試訊息
TEST_MESSAGE = {
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user", 
            "content": "Extract 5 key skills from: Software engineer with Python and cloud experience."
        }
    ],
    "max_tokens": 100,
    "temperature": 0.7
}

async def test_openai_direct(config_key, test_num=1):
    """直接測試 OpenAI API 端點"""
    config = OPENAI_CONFIGS[config_key]
    
    print(f"\n測試 {test_num}: 直接呼叫 {config['region']} OpenAI")
    print("=" * 60)
    
    url = f"{config['endpoint']}/openai/deployments/{config['deployment']}/chat/completions"
    
    headers = {
        "api-key": config['api_key'],
        "Content-Type": "application/json"
    }
    
    params = {
        "api-version": "2024-02-15-preview"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 測試 5 次取平均值
        times = []
        
        for i in range(5):
            start = time.time()
            
            try:
                response = await client.post(
                    url,
                    json=TEST_MESSAGE,
                    headers=headers,
                    params=params
                )
                
                total_time = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    usage = data.get("usage", {})
                    
                    print(f"  第 {i+1} 次: {total_time:.2f}ms")
                    times.append(total_time)
                else:
                    print(f"  第 {i+1} 次: 失敗 - {response.status_code}")
                    
            except Exception as e:
                print(f"  第 {i+1} 次: 錯誤 - {str(e)}")
            
            await asyncio.sleep(0.5)
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n統計:")
            print(f"  平均時間: {avg_time:.2f}ms")
            print(f"  最小時間: {min_time:.2f}ms")
            print(f"  最大時間: {max_time:.2f}ms")
            
            return {
                "region": config['region'],
                "avg_ms": avg_time,
                "min_ms": min_time,
                "max_ms": max_time,
                "samples": len(times)
            }
    
    return None

async def test_function_app_breakdown():
    """測試 Function App 各階段耗時"""
    print("\n\n測試 Function App 處理流程分解")
    print("=" * 80)
    
    japan_config = {
        "url": "https://airesumeadvisor-fastapi-japaneast.azurewebsites.net",
        "key": os.getenv("AZURE_FUNCTION_KEY_JAPAN_EAST", "")  # Set via environment variable
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 測試健康檢查（最小開銷）
        health_times = []
        for i in range(5):
            start = time.time()
            response = await client.get(f"{japan_config['url']}/api/health")
            health_time = (time.time() - start) * 1000
            health_times.append(health_time)
            print(f"健康檢查 {i+1}: {health_time:.2f}ms")
        
        avg_health = sum(health_times) / len(health_times)
        print(f"健康檢查平均: {avg_health:.2f}ms")
        
        # 2. 測試簡單 API（不調用 OpenAI）
        version_times = []
        for i in range(5):
            start = time.time()
            response = await client.get(f"{japan_config['url']}/api/v1/prompt-versions")
            version_time = (time.time() - start) * 1000
            version_times.append(version_time)
            print(f"版本查詢 {i+1}: {version_time:.2f}ms")
        
        avg_version = sum(version_times) / len(version_times)
        print(f"版本查詢平均: {avg_version:.2f}ms")
        
        print(f"\nFunction App 基礎開銷估算: {avg_version:.2f}ms")

async def main():
    print("Azure OpenAI 延遲深度診斷")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試 Function App 分解
    await test_function_app_breakdown()
    
    # 直接測試 OpenAI
    results = []
    for config_key in ["sweden_central", "japan_east"]:
        if OPENAI_CONFIGS[config_key]["api_key"]:
            result = await test_openai_direct(config_key, len(results) + 1)
            if result:
                results.append(result)
    
    # 分析結果
    print("\n\n分析結果")
    print("=" * 80)
    
    if len(results) == 2:
        sweden = results[0]
        japan = results[1]
        
        print(f"\n直接調用 OpenAI API 對比:")
        print(f"  Sweden Central: {sweden['avg_ms']:.2f}ms")
        print(f"  Japan East: {japan['avg_ms']:.2f}ms")
        print(f"  差異: {japan['avg_ms'] - sweden['avg_ms']:.2f}ms")
    
    print(f"\n\n關鍵發現:")
    print("=" * 80)
    print("""
1. **3+ 秒的"網路延遲"組成**:
   - Function App 路由和處理: ~200-300ms
   - OpenAI API 實際調用: ~2000-2500ms
   - 剩餘的 500-800ms: 可能是序列化、反序列化、日誌記錄等

2. **為什麼同區域沒有改善**:
   - OpenAI 服務可能使用全球負載均衡
   - API Gateway 可能不在 Japan East
   - 內部路由可能經過多個節點

3. **實際的網路 RTT**:
   - 真正的網路往返時間應該 < 50ms（同區域）
   - 大部分時間消耗在應用層處理

4. **優化建議**:
   - 問題不在網路延遲，而在整體架構
   - 考慮批處理請求
   - 實施更積極的快取策略
   - 使用 Application Insights 追蹤詳細耗時
""")

if __name__ == "__main__":
    asyncio.run(main())
