#!/usr/bin/env python3
"""
多語言 Prompt 版本比較測試
自動偵測語言並比較該語言的不同 prompt 版本效果

功能:
- 自動偵測 JD 語言
- 比較該語言可用的 prompt 版本（如 v1.2.0 vs v1.3.0）
- 分析各版本的一致性和穩定性
- 找出最穩定的版本

用法:
    python test_prompt_version_comparison.py                    # 使用預設英文 JD
    python test_prompt_version_comparison.py --jd-file job.txt  # 使用檔案中的 JD
    python test_prompt_version_comparison.py --jd "職位描述"     # 直接提供 JD
    python test_prompt_version_comparison.py --runs 30          # 每個版本測試 30 次
"""
import asyncio
import httpx
import argparse
import math
import json
from datetime import datetime
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Set

# 預設英文測試 JD
DEFAULT_ENGLISH_JD = """
Sr. HR Data Analyst

Established in 1987 and headquartered in Taiwan, TSMC pioneered the pure-play foundry business model with an exclusive focus on manufacturing its customers’ products. In 2023, the company served 528 customers with 11,895 products for high performance computing, smartphones, IoT, automotive, and consumer electronics, and is the world’s largest provider of logic ICs with annual capacity of 16 million 12-inch equivalent wafers. TSMC operates fabs in Taiwan as well as manufacturing subsidiaries in Washington State, Japan and China, and its ESMC subsidiary plans to begin construction on a fab in Germany in 2024. In Arizona, TSMC is building three fabs, with the first starting 4nm production in 2025, the second by 2028, and the third by the end of the decade.

The Sr. HR Data Analyst will be responsible for analyzing large sets of HR data in order to provide insights and recommendations to the HR team and senior management independently or with other HR analysts across global HR team. The role will require a high level of technical expertise in data visualization and analysis, as well as a deep understanding of HR processes and policies.

**Job Responsibilities:**

1. Act as a Tableau data visualization expert and develop strategic HR dashboards with other domain experts in cross-team projects that enables data-informed decisions to stakeholders.
2. Provide guidance, training plans and technical support to other analysts in HR team for Tableau skills development.
3. Translate business needs into technical data requirements and work with IT data platform engineers for data preparation.
4. Create trust and maintain strong relationships with key stakeholders across the organization.
5. Stay up-to-date with industry trends and new analytics features as a technical advocate.

**Job Qualifications:**

1. Master's degree in HR, Business, Statistics, CS or related field.
2. Minimum 5 years of experience in data analysis, with a proven track record of delivering actionable business insights and recommendations.
3. Strong technical skills in data analysis tools such as Tableau, Power BI, Superset and SQL.
4. Excellent communication skills with the ability to effectively communicate complex data insights to non-technical stakeholders.
5. Strong problem-solving skills with the ability to think critically and creatively to solve complex business problems.
6. Ability to work independently and manage multiple projects simultaneously.
7. Strong attention to details and accuracy.
8. Experience in leading and mentoring junior analysts is a plus.
"""

# 預設中文測試 JD
DEFAULT_CHINESE_JD = """
資深軟體工程師

我們正在尋找一位經驗豐富的資深軟體工程師，加入我們的技術團隊。

主要職責：
- 設計和開發高品質的軟體解決方案
- 參與系統架構設計和技術決策
- 指導初級工程師並進行代碼審查
- 優化系統性能和可擴展性
- 撰寫技術文檔和最佳實踐

技能要求：
- 精通 Python 和相關框架（Django、FastAPI）
- 熟悉微服務架構和容器技術（Docker、Kubernetes）
- 具備資料庫設計和優化經驗（PostgreSQL、MongoDB）
- 了解 CI/CD 流程和 DevOps 實踐
- 良好的問題解決能力和團隊合作精神

資格要求：
- 計算機科學或相關領域學士學位以上
- 5年以上軟體開發經驗
- 具備大型系統開發經驗者優先
"""

class PromptVersionComparison:
    """Prompt 版本比較測試類"""
    
    def __init__(self, runs_per_version: int = 20):
        self.runs_per_version = runs_per_version
        self.base_url = "http://localhost:8000/api/v1"
        self.test_jd = None
        self.detected_language = None
        self.available_versions = []
        
    def set_test_jd(self, jd: str):
        """設定測試用的 JD"""
        self.test_jd = jd.strip()
    
    async def detect_language_and_versions(self):
        """偵測語言並獲取可用的 prompt 版本"""
        print("\n🌐 偵測 JD 語言並獲取可用版本...")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 第一次請求，使用 auto 語言偵測
            response = await client.post(
                f"{self.base_url}/extract-jd-keywords",
                json={
                    "job_description": self.test_jd,
                    "max_keywords": 16,
                    "language": "auto"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                self.detected_language = result["data"].get("detected_language", "unknown")
                current_version = result["data"].get("prompt_version", "latest")
                
                print(f"   偵測到語言: {self.detected_language}")
                print(f"   當前使用版本: {current_version}")
                
                # 根據語言決定可用版本
                if self.detected_language == "en":
                    self.available_versions = ["1.2.0", "1.3.0", "1.4.0"]  # 英文有三個版本
                elif self.detected_language == "zh-TW":
                    self.available_versions = ["1.2.0", "1.3.0", "1.4.0"]  # 中文也有三個版本
                else:
                    self.available_versions = ["1.3.0"]  # 其他語言只有最新版
                
                print(f"   可測試版本: {', '.join(self.available_versions)}")
                
                return True
            else:
                print(f"❌ 語言偵測失敗: HTTP {response.status_code}")
                return False
    
    async def test_version_consistency(self, version: str) -> Dict:
        """測試特定版本的一致性"""
        print(f"\n📋 測試版本 {version} ({self.runs_per_version} 次)...")
        
        results = []
        failed_runs = 0
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for run in range(1, self.runs_per_version + 1):
                try:
                    response = await client.post(
                        f"{self.base_url}/extract-jd-keywords",
                        json={
                            "job_description": self.test_jd,
                            "max_keywords": 16,
                            "prompt_version": version,
                            "language": self.detected_language
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        keywords = result["data"]["keywords"]
                        results.append(keywords)
                        
                        if run <= 5 or run % 5 == 0:
                            print(f"   Run {run:2d}: ✓ ({len(keywords)} keywords)")
                    else:
                        failed_runs += 1
                        print(f"   Run {run:2d}: ✗ (HTTP {response.status_code})")
                        
                except Exception as e:
                    failed_runs += 1
                    print(f"   Run {run:2d}: ✗ (Error: {str(e)})")
                
                # 延遲避免 rate limiting
                await asyncio.sleep(1.0)
        
        return {
            "version": version,
            "results": results,
            "failed_runs": failed_runs,
            "success_rate": len(results) / self.runs_per_version
        }
    
    def analyze_consistency(self, version_data: Dict) -> Dict:
        """分析一個版本的一致性"""
        results = version_data["results"]
        
        if len(results) < 2:
            return {
                "version": version_data["version"],
                "insufficient_data": True
            }
        
        # 計算唯一組合
        unique_combinations = {}
        for result in results:
            result_tuple = tuple(sorted(result))
            if result_tuple not in unique_combinations:
                unique_combinations[result_tuple] = 0
            unique_combinations[result_tuple] += 1
        
        # 計算配對一致性
        total_pairs = len(results) * (len(results) - 1) // 2
        identical_pairs = 0
        
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                if sorted(results[i]) == sorted(results[j]):
                    identical_pairs += 1
        
        consistency_rate = identical_pairs / total_pairs if total_pairs > 0 else 0
        
        # 計算 95% 信心區間
        p = consistency_rate
        n = total_pairs
        
        if n > 0 and p > 0 and p < 1:
            se = math.sqrt(p * (1 - p) / n)
            z = 1.96  # 95% 信心水準
            ci_lower = max(0, p - z * se)
            ci_upper = min(1, p + z * se)
        else:
            ci_lower = ci_upper = p
        
        # 找出最穩定的關鍵字（出現在所有結果中）
        if results:
            stable_keywords = set(results[0])
            for result in results[1:]:
                stable_keywords &= set(result)
        else:
            stable_keywords = set()
        
        # 關鍵字頻率統計
        all_keywords = []
        for result in results:
            all_keywords.extend(result)
        keyword_counter = Counter(all_keywords)
        
        return {
            "version": version_data["version"],
            "success_rate": version_data["success_rate"],
            "unique_combinations": len(unique_combinations),
            "consistency_rate": consistency_rate,
            "confidence_interval": {"lower": ci_lower, "upper": ci_upper},
            "total_pairs": total_pairs,
            "identical_pairs": identical_pairs,
            "stable_keywords": sorted(stable_keywords),
            "stable_keywords_count": len(stable_keywords),
            "top_keywords": keyword_counter.most_common(10),
            "combination_frequencies": sorted(unique_combinations.items(), 
                                            key=lambda x: x[1], reverse=True)[:5]
        }
    
    def compare_versions(self, analyses: List[Dict]) -> Dict:
        """比較不同版本的結果"""
        if len(analyses) < 2:
            return {"insufficient_versions": True}
        
        # 找出最穩定的版本
        best_version = max(analyses, key=lambda x: x["consistency_rate"])
        
        # 計算版本間的共同關鍵字
        version_keywords = {}
        for analysis in analyses:
            if analysis["combination_frequencies"]:
                # 使用最常見的組合
                most_common = analysis["combination_frequencies"][0][0]
                version_keywords[analysis["version"]] = set(most_common)
        
        # 計算交集
        if len(version_keywords) >= 2:
            versions = list(version_keywords.keys())
            common_keywords = version_keywords[versions[0]]
            for v in versions[1:]:
                common_keywords &= version_keywords[v]
        else:
            common_keywords = set()
        
        return {
            "best_version": best_version["version"],
            "best_consistency": best_version["consistency_rate"],
            "common_keywords_across_versions": sorted(common_keywords),
            "version_comparisons": analyses
        }
    
    async def run_comparison(self):
        """執行完整的版本比較測試"""
        print(f"\n🚀 開始 Prompt 版本比較測試")
        print(f"   JD 長度: {len(self.test_jd)} 字符")
        print(f"   每版本測試次數: {self.runs_per_version}")
        print("=" * 80)
        
        # 偵測語言和版本
        if not await self.detect_language_and_versions():
            return
        
        if len(self.available_versions) < 2:
            print(f"\n⚠️  {self.detected_language} 語言只有一個版本可用，無法進行比較")
            return
        
        # 測試每個版本
        version_results = []
        for version in self.available_versions:
            result = await self.test_version_consistency(version)
            version_results.append(result)
        
        # 分析結果
        print("\n\n📊 一致性分析結果")
        print("=" * 80)
        
        analyses = []
        for version_data in version_results:
            analysis = self.analyze_consistency(version_data)
            analyses.append(analysis)
            
            print(f"\n🔍 版本 {analysis['version']}")
            print(f"   成功率: {analysis['success_rate']:.1%}")
            print(f"   唯一組合數: {analysis['unique_combinations']}")
            print(f"   一致性率: {analysis['consistency_rate']:.1%}")
            print(f"   95% 信心區間: [{analysis['confidence_interval']['lower']:.1%}, "
                  f"{analysis['confidence_interval']['upper']:.1%}]")
            print(f"   100% 穩定關鍵字數: {analysis['stable_keywords_count']}")
            
            # 顯示組合頻率
            print("\n   組合頻率 (前5):")
            for i, (combo, count) in enumerate(analysis['combination_frequencies'][:5]):
                percentage = (count / len(version_data['results'])) * 100
                print(f"     組合 {i+1}: {count} 次 ({percentage:.1f}%)")
                if i == 0:  # 顯示最常見組合的前10個關鍵字
                    print(f"       關鍵字: {', '.join(sorted(combo)[:10])}...")
        
        # 版本比較
        comparison = self.compare_versions(analyses)
        
        print("\n\n🔄 版本比較總結")
        print("=" * 80)
        print(f"   最穩定版本: {comparison['best_version']} "
              f"(一致性 {comparison['best_consistency']:.1%})")
        print(f"   跨版本共同關鍵字數: {len(comparison['common_keywords_across_versions'])}")
        
        if comparison['common_keywords_across_versions']:
            print(f"   共同關鍵字: {', '.join(comparison['common_keywords_across_versions'][:10])}...")
        
        # 生成報告
        self.generate_report(analyses, comparison)
    
    def generate_report(self, analyses: List[Dict], comparison: Dict):
        """生成詳細報告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"prompt_version_comparison_{self.detected_language}_{timestamp}.json"
        
        report_data = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "detected_language": self.detected_language,
                "available_versions": self.available_versions,
                "runs_per_version": self.runs_per_version,
                "jd_length": len(self.test_jd),
                "jd_preview": self.test_jd[:200] + "..." if len(self.test_jd) > 200 else self.test_jd
            },
            "version_analyses": analyses,
            "comparison_summary": comparison,
            "recommendations": {
                "best_version": comparison['best_version'],
                "reason": f"最高一致性 {comparison['best_consistency']:.1%}"
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n📄 詳細報告已保存: {report_file}")


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="多語言 Prompt 版本比較測試",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s                           # 使用預設英文 JD
  %(prog)s --jd-file chinese.txt    # 使用檔案中的 JD
  %(prog)s --jd "職位描述內容"        # 直接提供 JD 內容
  %(prog)s --runs 30                # 每個版本測試 30 次
  %(prog)s --chinese                # 使用預設中文 JD
        """
    )
    
    # JD 來源
    jd_group = parser.add_mutually_exclusive_group()
    jd_group.add_argument(
        '--jd-file', 
        type=str,
        help='從檔案讀取 JD 內容'
    )
    jd_group.add_argument(
        '--jd',
        type=str,
        help='直接提供 JD 內容'
    )
    jd_group.add_argument(
        '--chinese',
        action='store_true',
        help='使用預設中文 JD'
    )
    
    # 測試次數
    parser.add_argument(
        '-r', '--runs',
        type=int,
        default=20,
        help='每個版本的測試次數（預設: 20）'
    )
    
    return parser.parse_args()


async def main():
    """主函數"""
    args = parse_arguments()
    
    # 檢查伺服器是否運行
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            if response.status_code != 200:
                print("❌ API 伺服器未回應")
                return
    except Exception:
        print("❌ 無法連接到 API 伺服器")
        print("請先啟動伺服器: uvicorn src.main:app --reload")
        return
    
    # 決定使用的 JD
    if args.jd_file:
        try:
            with open(args.jd_file, 'r', encoding='utf-8') as f:
                test_jd = f.read()
            print(f"📄 從檔案載入 JD: {args.jd_file}")
        except Exception as e:
            print(f"❌ 無法讀取檔案: {e}")
            return
    elif args.jd:
        test_jd = args.jd
        print("📝 使用命令列提供的 JD")
    elif args.chinese:
        test_jd = DEFAULT_CHINESE_JD
        print("📝 使用預設中文 JD")
    else:
        test_jd = DEFAULT_ENGLISH_JD
        print("📝 使用預設英文 JD")
    
    # 執行測試
    tester = PromptVersionComparison(runs_per_version=args.runs)
    tester.set_test_jd(test_jd)
    await tester.run_comparison()
    
    print("\n✅ 測試完成！")


if __name__ == "__main__":
    asyncio.run(main())