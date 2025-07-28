#!/usr/bin/env python3
"""
Staging 環境效能追蹤測試腳本
測試新增的詳細效能追蹤功能
"""
import asyncio
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import httpx
import statistics
from collections import defaultdict
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 測試配置
# 注意：staging slot 的 URL 格式
STAGING_URL = "https://airesumeadvisor-fastapi-premium-staging.azurewebsites.net"
# 使用 Premium Staging Host Key
FUNCTION_KEY = (
    os.getenv("PREMIUM_STAGING_HOST_KEY") or  # 優先使用 staging key
    os.getenv("STAGING_FUNCTION_KEY") or 
    os.getenv("FUNCTION_KEY_STAGING")
)

# 測試案例
TEST_CASES = [
    {
        "name": "English Short JD",
        "language": "en",
        "job_description": """
        We are looking for a talented Full Stack Developer to join our growing team.
        The ideal candidate should have strong experience with React.js, Node.js, and 
        cloud services like AWS. Experience with Docker and Kubernetes is a plus.
        Strong problem-solving skills and ability to work in an agile environment.
        """.strip()
    },
    {
        "name": "English Long JD",
        "language": "en", 
        "job_description": """
        We are seeking an experienced Senior Software Engineer to lead our backend development initiatives.
        This is an exciting opportunity to work on cutting-edge technology and make a significant impact.
        
        Key Responsibilities:
        - Design and implement scalable microservices architecture using Python and Go
        - Lead technical discussions and mentor junior developers
        - Collaborate with product managers to define technical requirements
        - Optimize database performance with PostgreSQL and Redis
        - Implement CI/CD pipelines using Jenkins and GitLab CI
        - Ensure code quality through comprehensive testing and code reviews
        
        Required Qualifications:
        - Bachelor's degree in Computer Science or related field
        - 5+ years of experience in backend development
        - Strong proficiency in Python, with knowledge of Django or FastAPI
        - Experience with containerization using Docker and orchestration with Kubernetes
        - Solid understanding of RESTful API design principles
        - Experience with message queuing systems like RabbitMQ or Kafka
        - Strong knowledge of SQL and NoSQL databases
        - Experience with AWS services (EC2, S3, RDS, Lambda)
        
        Nice to Have:
        - Experience with Go programming language
        - Knowledge of GraphQL
        - Experience with monitoring tools like Prometheus and Grafana
        - Understanding of security best practices
        - Contributions to open source projects
        
        What We Offer:
        - Competitive salary and equity package
        - Flexible working hours and remote work options
        - Health insurance and wellness programs
        - Professional development budget
        - Collaborative and inclusive work environment
        """.strip()
    },
    {
        "name": "Chinese Short JD",
        "language": "zh-TW",
        "job_description": """
        我們正在尋找一位資深前端工程師，需要精通 React、Vue.js 和 TypeScript。
        具備響應式網頁設計經驗，熟悉 Git 版本控制和敏捷開發流程。
        有大型專案經驗者優先考慮。
        """.strip()
    },
    {
        "name": "Chinese Long JD",
        "language": "zh-TW",
        "job_description": """
        【職位名稱】資深全端工程師 Senior Full Stack Engineer

        【工作內容】
        1. 負責公司核心產品的前後端開發與維護
        2. 參與系統架構設計，確保系統的可擴展性和高可用性
        3. 與產品經理、設計師密切合作，將需求轉化為技術實現
        4. 優化現有程式碼，提升系統效能和使用者體驗
        5. 撰寫技術文檔，分享最佳實踐
        6. 指導初級工程師，協助團隊成長

        【職位要求】
        必備技能：
        - 5年以上全端開發經驗
        - 精通 JavaScript/TypeScript，熟練使用 React.js 或 Vue.js
        - 熟悉 Node.js 後端開發，有 Express.js 或 Nest.js 經驗
        - 掌握關聯式資料庫（MySQL/PostgreSQL）和 NoSQL（MongoDB/Redis）
        - 熟悉 RESTful API 設計原則，有 GraphQL 經驗更佳
        - 了解微服務架構和容器化技術（Docker/Kubernetes）
        - 熟悉 Git 版本控制和 CI/CD 流程

        加分項目：
        - 有雲端服務經驗（AWS/GCP/Azure）
        - 熟悉 Python 或 Go 語言
        - 有大流量網站優化經驗
        - 參與過開源專案
        - 具備 DevOps 相關經驗
        - 有金融科技或電商領域經驗

        【我們提供】
        - 具競爭力的薪資待遇
        - 彈性工作時間和遠端工作選項
        - 完善的員工培訓計畫
        - 定期技術分享會和讀書會
        - 現代化的辦公環境和設備
        """.strip()
    }
]

async def test_single_request(
    client: httpx.AsyncClient,
    test_case: Dict[str, Any],
    iteration: int
) -> Dict[str, Any]:
    """執行單次測試請求"""
    
    url = f"{STAGING_URL}/api/v1/extract-jd-keywords?code={FUNCTION_KEY}"
    
    payload = {
        "job_description": test_case["job_description"],
        "language": test_case["language"],
        "max_keywords": 15,
        "prompt_version": "latest"
    }
    
    start_time = time.time()
    
    try:
        response = await client.post(url, json=payload, timeout=30.0)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                result = data["data"]
                
                # 提取詳細的時間指標
                timing_breakdown = result.get("timing_breakdown", {})
                
                return {
                    "iteration": iteration,
                    "test_case": test_case["name"],
                    "language": test_case["language"],
                    "jd_length": len(test_case["job_description"]),
                    "status": "success",
                    "total_time_ms": total_time_ms,
                    "api_processing_ms": result.get("processing_time_ms", 0),
                    "service_init_ms": timing_breakdown.get("service_init_ms", 0),
                    "validation_ms": timing_breakdown.get("validation_ms", 0),
                    "extraction_ms": timing_breakdown.get("keyword_extraction_ms", 0),
                    "language_detection_ms": result.get("language_detection_time_ms", 0),
                    "cache_hit": result.get("cache_hit", False),
                    "keyword_count": result.get("keyword_count", 0),
                    "detected_language": result.get("detected_language", ""),
                    "extraction_method": result.get("extraction_method", ""),
                    "confidence_score": result.get("confidence_score", 0)
                }
            else:
                return {
                    "iteration": iteration,
                    "test_case": test_case["name"],
                    "status": "api_error",
                    "error": data.get("error", {}).get("message", "Unknown error"),
                    "total_time_ms": total_time_ms
                }
        else:
            # 嘗試獲取錯誤訊息
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", response.text[:200])
            except:
                error_detail = response.text[:200]
            
            return {
                "iteration": iteration,
                "test_case": test_case["name"],
                "status": "http_error",
                "status_code": response.status_code,
                "error_detail": error_detail,
                "total_time_ms": total_time_ms
            }
            
    except Exception as e:
        return {
            "iteration": iteration,
            "test_case": test_case["name"],
            "status": "exception",
            "error": str(e),
            "total_time_ms": (time.time() - start_time) * 1000
        }

async def run_performance_tests(iterations: int = 5):
    """執行效能測試"""
    
    print(f"\n🚀 開始 Staging 環境效能追蹤測試")
    print(f"📍 目標: {STAGING_URL}")
    print(f"🔄 每個測試案例執行 {iterations} 次\n")
    
    if not FUNCTION_KEY:
        print("⚠️  警告: 找不到 Function Key!")
        print("   請確認 .env 檔案中有設定以下任一環境變數:")
        print("   - PREMIUM_STAGING_HOST_KEY (推薦)")
        print("   - STAGING_FUNCTION_KEY")
        print("   - FUNCTION_KEY_STAGING")
        return
    
    print(f"✅ 使用 Function Key: {FUNCTION_KEY[:10]}...")
    
    async with httpx.AsyncClient() as client:
        # 預熱請求
        print("🔥 執行預熱請求...")
        warmup_case = TEST_CASES[0]
        await test_single_request(client, warmup_case, 0)
        await asyncio.sleep(2)
        
        # 執行測試
        all_results = []
        
        for test_case in TEST_CASES:
            print(f"\n📝 測試案例: {test_case['name']}")
            print(f"   語言: {test_case['language']}")
            print(f"   JD長度: {len(test_case['job_description'])} 字元")
            
            case_results = []
            
            for i in range(iterations):
                result = await test_single_request(client, test_case, i + 1)
                case_results.append(result)
                
                if result["status"] == "success":
                    print(f"   ✅ 迭代 {i+1}: {result['total_time_ms']:.0f}ms "
                          f"(API: {result['api_processing_ms']:.0f}ms, "
                          f"Cache: {'Hit' if result['cache_hit'] else 'Miss'})")
                else:
                    print(f"   ❌ 迭代 {i+1}: {result['status']} - {result.get('error', 'N/A')}")
                
                # 避免太快的請求
                if i < iterations - 1:
                    await asyncio.sleep(1)
            
            all_results.extend(case_results)
            
            # 計算統計數據
            success_results = [r for r in case_results if r["status"] == "success"]
            if success_results:
                api_times = [r["api_processing_ms"] for r in success_results]
                total_times = [r["total_time_ms"] for r in success_results]
                
                print(f"\n   📊 統計摘要:")
                print(f"   成功率: {len(success_results)}/{len(case_results)} "
                      f"({len(success_results)/len(case_results)*100:.0f}%)")
                print(f"   API 處理時間: 平均 {statistics.mean(api_times):.0f}ms, "
                      f"中位數 {statistics.median(api_times):.0f}ms")
                print(f"   總回應時間: 平均 {statistics.mean(total_times):.0f}ms, "
                      f"中位數 {statistics.median(total_times):.0f}ms")
    
    # 保存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"staging_performance_test_{timestamp}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 測試結果已保存到: {output_file}")
    
    # 生成詳細報告
    generate_detailed_report(all_results)

def generate_detailed_report(results: List[Dict[str, Any]]):
    """生成詳細的效能報告"""
    
    print("\n" + "="*60)
    print("📊 詳細效能分析報告")
    print("="*60)
    
    # 按測試案例分組
    case_groups = defaultdict(list)
    for result in results:
        if result["status"] == "success":
            case_groups[result["test_case"]].append(result)
    
    for case_name, case_results in case_groups.items():
        print(f"\n### {case_name}")
        
        # 時間分解分析
        print("\n⏱️  時間分解 (平均值 ms):")
        
        metrics = {
            "服務初始化": [r["service_init_ms"] for r in case_results],
            "請求驗證": [r["validation_ms"] for r in case_results],
            "語言檢測": [r["language_detection_ms"] for r in case_results],
            "關鍵字提取": [r["extraction_ms"] for r in case_results],
            "API 總處理": [r["api_processing_ms"] for r in case_results],
            "端到端總時間": [r["total_time_ms"] for r in case_results]
        }
        
        for metric_name, values in metrics.items():
            if values and all(v is not None for v in values):
                avg = statistics.mean(values)
                print(f"   {metric_name}: {avg:.1f}ms")
        
        # 快取分析
        cache_hits = sum(1 for r in case_results if r["cache_hit"])
        print(f"\n💾 快取命中率: {cache_hits}/{len(case_results)} "
              f"({cache_hits/len(case_results)*100:.0f}%)")
        
        # 效能瓶頸分析
        if case_results:
            avg_extraction = statistics.mean([r["extraction_ms"] for r in case_results])
            avg_total = statistics.mean([r["api_processing_ms"] for r in case_results])
            extraction_percentage = (avg_extraction / avg_total) * 100
            
            print(f"\n🎯 效能瓶頸:")
            print(f"   關鍵字提取佔總時間: {extraction_percentage:.1f}%")
            
            if extraction_percentage > 80:
                print("   ⚠️  LLM 調用是主要瓶頸")
            elif extraction_percentage > 60:
                print("   ⚡ LLM 調用佔用大部分時間")
            else:
                print("   ✅ 時間分配相對均衡")

if __name__ == "__main__":
    asyncio.run(run_performance_tests(iterations=2))