#!/usr/bin/env python3
"""
TC-416: 關鍵字提取一致性測試（多語言支援）
核心 KPI 測試 - 評估 AI 關鍵字提取的穩定性和一致性

用法: 
    python test_tc416_consistency.py                    # 使用預設 JD
    python test_tc416_consistency.py --jd-file job.txt  # 使用自訂 JD 檔案
    python test_tc416_consistency.py --jd "職位描述內容" # 直接提供 JD 內容
    python test_tc416_consistency.py --iterations 20    # 自訂測試次數

功能:
- 支援任何語言的 JD（自動偵測語言）
- 根據偵測到的語言自動選擇對應的最新 prompt 版本
- 分析關鍵字重複率和 Jaccard 相似度
- 驗證語言檢測一致性
- 生成詳細的一致性報告
- 計算 KPI 指標

⚠️  注意:
- 需要真實 OpenAI API 金鑰
- 執行時間: 5-10 分鐘（50次測試）
- 會產生 API 使用費用
- 需要穩定網路連線

Author: Claude Code
Date: 2025-07-04
"""
import asyncio
import json
import time
import sys
import os
import argparse
from typing import Tuple
from datetime import datetime
from pathlib import Path
from collections import Counter

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
os.environ['PYTHONPATH'] = str(project_root) + ":" + os.environ.get('PYTHONPATH', '')

# Import services
from src.services.keyword_extraction_v2 import KeywordExtractionServiceV2

# 預設測試 JD（中文）
DEFAULT_JD = """
Project Manager
Responsible for wafer outsourcing and cost negotiation, including:
Competitive Price: RFQ, price negotiation, cost prediction, cost reduction initiatives, CA.Capacity: long-term reservation, short-term fulfillment, acting as a bridge for internal and external parties to reach goals. Contract: NDA and short-term agreements. Project management (e.g. procurement system)

**Requirement

**Proactive working attitude and good communication skills, with negotiation capability being a plus.Experience in handling wafer sourcing or procurement. Project management and business acumen.
"""

class TC416ConsistencyTest:
    """TC-416: 多語言關鍵字提取一致性測試"""
    
    def __init__(self, iterations: int = 50, delay_seconds: float = 1.0):
        # 關閉快取以測試真實的 AI 一致性（而非快取一致性）
        self.keyword_service = KeywordExtractionServiceV2(enable_cache=False)
        self.iterations = iterations
        self.delay_seconds = delay_seconds
        
        # 確認快取是否真的關閉
        cache_info = self.keyword_service.get_cache_info()
        print(f"⚙️  快取設定: {'關閉' if not cache_info['enabled'] else '開啟'}")
        print(f"   快取大小: {cache_info['total_entries']}")
        
        # 清空任何現有快取
        if cache_info['total_entries'] > 0:
            self.keyword_service.clear_cache()
            print(f"   已清空 {cache_info['total_entries']} 個快取項目")
        
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.test_jd = None
        self.detected_language = None
        self.prompt_version_used = None
        
    def set_test_jd(self, jd: str):
        """設定測試用的 JD"""
        self.test_jd = jd.strip()
        
    def print_header(self):
        """打印測試標題"""
        print("=" * 70)
        print(f"🧪 TC-416: 關鍵字提取一致性測試 ({self.iterations}次)")
        print("📊 核心 KPI 測試 - AI 穩定性和一致性評估")
        print("=" * 70)
        print(f"專案目錄: {project_root}")
        print(f"Python 版本: {sys.version.split()[0]}")
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"JD 長度: {len(self.test_jd)} 字符")
        print("=" * 70)
        print(f"⚠️  注意: 此測試將進行 {self.iterations} 次真實 AI 呼叫")
        # 預估時間包含 API 調用時間（約 2 秒）和延遲時間
        estimated_seconds = self.iterations * (2 + self.delay_seconds)
        estimated_minutes = estimated_seconds / 60
        print(f"⏱️  預估執行時間: {estimated_minutes:.1f} 分鐘 (包含 {self.delay_seconds} 秒延遲)")
        print("💰 會產生 OpenAI API 使用費用")
        print("=" * 70)
        
    def log_progress(self, iteration, total, result=None):
        """記錄進度"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        progress = f"[{timestamp}] 進度: {iteration:2d}/{total}"
        
        if result:
            keywords_count = len(result.get("keywords", []))
            lang = result.get("detected_language", "未知")
            confidence = result.get("confidence_score", 0)
            cache_hit = result.get("cache_hit", False)
            prompt_version = result.get("prompt_version", "N/A")
            progress += f" | 關鍵字: {keywords_count:2d} | 語言: {lang} | 版本: {prompt_version} | 快取: {'是' if cache_hit else '否'}"
        
        print(progress)
    
    async def detect_language_and_version(self):
        """偵測語言並決定使用的 prompt 版本"""
        print("\n🌐 偵測 JD 語言...")
        
        # 使用第一次測試來偵測語言
        result = await self.keyword_service.process({
            "job_description": self.test_jd,
            "max_keywords": 16,
            "include_standardization": True,
            "use_multi_round_validation": True,
            "language": "auto"  # 自動偵測語言
        })
        
        self.detected_language = result.get("detected_language", "unknown")
        self.prompt_version_used = result.get("prompt_version", "latest")
        
        print(f"   偵測到語言: {self.detected_language}")
        print(f"   使用 Prompt 版本: {self.prompt_version_used}")
        
        # 獲取可用的 prompt 版本資訊
        print(f"   支援的 prompt 版本: v1.0.0, v1.2.0, v1.3.0, v1.4.0")
        
        return result
    
    async def run_consistency_test(self):
        """執行一致性測試"""
        self.print_header()
        
        # 首先偵測語言
        first_result = await self.detect_language_and_version()
        
        print(f"\n🚀 開始執行 {self.iterations} 次一致性測試...")
        print("-" * 50)
        
        self.start_time = time.time()
        all_keywords = []
        
        # 將第一次結果加入
        self.test_results.append({
            "iteration": 1,
            "keywords": first_result.get("keywords", []),
            "keyword_count": len(first_result.get("keywords", [])),
            "detected_language": first_result.get("detected_language", ""),
            "confidence_score": first_result.get("confidence_score", 0),
            "extraction_method": first_result.get("extraction_method", ""),
            "processing_time_ms": 0,  # 第一次沒有計時
            "cache_hit": first_result.get("cache_hit", False),
            "intersection_stats": first_result.get("intersection_stats", {}),
            "llm_config_used": first_result.get("llm_config_used", {}),
            "prompt_version": first_result.get("prompt_version", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        # 顯示 LLM 配置
        llm_config = first_result.get("llm_config_used", {})
        if llm_config:
            print(f"\n📋 LLM 配置:")
            print(f"   Temperature: {llm_config.get('temperature', 'N/A')}")
            print(f"   Seed: {llm_config.get('seed', 'N/A')}")
            print(f"   Top-p: {llm_config.get('top_p', 'N/A')}")
            print(f"   Max tokens: {llm_config.get('max_tokens', 'N/A')}")
            print()
        
        self.log_progress(1, self.iterations, first_result)
        
        # 執行剩餘的測試
        for i in range(2, self.iterations + 1):
            try:
                iteration_start = time.time()
                
                # 調用關鍵字提取服務，使用偵測到的語言對應的 prompt
                result = await self.keyword_service.process({
                    "job_description": self.test_jd,
                    "max_keywords": 16,
                    "include_standardization": True,
                    "use_multi_round_validation": True,
                    "prompt_version": self.prompt_version_used,  # 使用偵測到的版本
                    "language": self.detected_language  # 使用偵測到的語言
                })
                
                processing_time = int((time.time() - iteration_start) * 1000)
                keywords = result.get("keywords", [])
                
                # 記錄此次測試結果
                iteration_result = {
                    "iteration": i,
                    "keywords": keywords,
                    "keyword_count": len(keywords),
                    "detected_language": result.get("detected_language", ""),
                    "confidence_score": result.get("confidence_score", 0),
                    "extraction_method": result.get("extraction_method", ""),
                    "processing_time_ms": processing_time,
                    "cache_hit": result.get("cache_hit", False),
                    "intersection_stats": result.get("intersection_stats", {}),
                    "llm_config_used": result.get("llm_config_used", {}),
                    "prompt_version": result.get("prompt_version", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.test_results.append(iteration_result)
                all_keywords.extend(keywords)
                
                # 每 10 次或前 5 次顯示進度
                if i % 10 == 0 or i <= 5:
                    self.log_progress(i, self.iterations, result)
                
                # 加入延遲以避免 rate limit (除了最後一次)
                if i < self.iterations:
                    await asyncio.sleep(self.delay_seconds)
                
            except Exception as e:
                error_result = {
                    "iteration": i,
                    "error": str(e),
                    "failed": True,
                    "timestamp": datetime.now().isoformat()
                }
                self.test_results.append(error_result)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 第 {i} 次測試失敗: {str(e)}")
        
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        print(f"\n✅ {self.iterations} 次測試完成，總耗時: {total_time:.1f} 秒")
        print("-" * 50)
        
        # 分析結果
        await self.analyze_results()
    
    async def analyze_results(self):
        """分析一致性結果"""
        print("🔍 分析一致性結果...")
        print("-" * 40)
        
        # 過濾成功的測試
        successful_results = [r for r in self.test_results if not r.get("failed", False)]
        failed_count = len(self.test_results) - len(successful_results)
        
        # 檢查快取命中情況
        cache_hits = sum(1 for r in successful_results if r.get("cache_hit", False))
        
        print(f"成功測試: {len(successful_results)}/{self.iterations}")
        print(f"失敗測試: {failed_count}/{self.iterations}")
        print(f"快取命中: {cache_hits}/{len(successful_results)} {'⚠️  快取被啟用！' if cache_hits > 0 else ''}")
        
        if len(successful_results) < self.iterations * 0.6:
            print(f"❌ 成功測試數量不足（< {int(self.iterations * 0.6)}），無法進行可靠的一致性分析")
            return
        
        # 檢查是否所有結果都相同（可能是固定 seed 的問題）
        if len(successful_results) > 1:
            first_keywords = set(successful_results[0]["keywords"])
            all_same = all(set(r["keywords"]) == first_keywords for r in successful_results[1:])
            if all_same:
                print("\n⚠️  警告：所有測試結果完全相同！")
                print("   可能原因：")
                print("   1. Azure OpenAI 可能不支援 seed 參數")
                print("   2. Temperature=0 + top_p=0.1 導致完全確定性輸出")
                print(f"   3. 當前配置：{self.prompt_version_used}")
                print("   → 這不是真實的 AI 一致性測試！")
                print("\n   建議：")
                print("   1. 提高 temperature 到 0.1-0.3")
                print("   2. 提高 top_p 到 0.8-0.95")
                print("   3. 使用不同的 prompt 版本進行測試")
        
        # 1. 語言檢測一致性
        languages = [r["detected_language"] for r in successful_results]
        language_counter = Counter(languages)
        most_common_lang = language_counter.most_common(1)[0][0]
        language_consistency = language_counter[most_common_lang] / len(languages)
        
        # 2. 關鍵字數量分析
        keyword_counts = [r["keyword_count"] for r in successful_results]
        avg_keyword_count = sum(keyword_counts) / len(keyword_counts)
        min_keywords = min(keyword_counts)
        max_keywords = max(keyword_counts)
        
        # 3. 計算完整的一致性指標
        # 3.1 計算所有配對的 Jaccard 相似度
        jaccard_similarities = []
        keyword_combinations = []
        identical_pairs = 0
        
        for result in successful_results:
            combo = tuple(sorted(result["keywords"]))
            keyword_combinations.append(combo)
        
        # 比較所有配對（不只是相鄰的）
        total_pairs = len(successful_results) * (len(successful_results) - 1) // 2
        
        for i in range(len(successful_results)):
            for j in range(i + 1, len(successful_results)):
                set1 = set(successful_results[i]["keywords"])
                set2 = set(successful_results[j]["keywords"])
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                jaccard = intersection / union if union > 0 else 0
                jaccard_similarities.append(jaccard)
                
                # 檢查是否完全相同
                if keyword_combinations[i] == keyword_combinations[j]:
                    identical_pairs += 1
        
        avg_jaccard = sum(jaccard_similarities) / len(jaccard_similarities) if jaccard_similarities else 0
        exact_match_rate = identical_pairs / total_pairs if total_pairs > 0 else 0
        
        # 3.2 計算 95% 信心區間
        import math
        p = exact_match_rate
        n = total_pairs
        
        if p > 0 and p < 1 and n > 0:
            se = math.sqrt(p * (1 - p) / n)
            z = 1.96  # 95% 信心水準
            ci_lower = max(0, p - z * se)
            ci_upper = min(1, p + z * se)
        else:
            se = 0
            ci_lower = p
            ci_upper = p
        
        # 4. 關鍵字重複率分析
        all_keywords = []
        for result in successful_results:
            all_keywords.extend(result["keywords"])
        
        unique_keywords = list(set(all_keywords))
        total_keywords = len(all_keywords)
        unique_count = len(unique_keywords)
        repetition_rate = (total_keywords - unique_count) / total_keywords if total_keywords > 0 else 0
        
        # 5. 最高頻關鍵字
        keyword_frequency = {}
        for keyword in all_keywords:
            keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 6. 執行時間分析
        processing_times = [r["processing_time_ms"] for r in successful_results if r["processing_time_ms"] > 0]
        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
        else:
            avg_processing_time = min_time = max_time = 0
        
        # 7. 信心度分析
        confidence_scores = [r["confidence_score"] for r in successful_results]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        min_confidence = min(confidence_scores)
        max_confidence = max(confidence_scores)
        
        # 打印分析結果
        self.print_analysis_results(
            successful_results, language_consistency, avg_keyword_count,
            min_keywords, max_keywords, avg_jaccard, repetition_rate,
            top_keywords, avg_processing_time, min_time, max_time,
            avg_confidence, min_confidence, max_confidence,
            exact_match_rate, total_pairs, identical_pairs,
            ci_lower, ci_upper, len(set(keyword_combinations)),
            language_counter
        )
        
        # 生成報告
        await self.generate_report(
            successful_results, language_consistency, avg_jaccard,
            repetition_rate, top_keywords, exact_match_rate,
            total_pairs, identical_pairs, ci_lower, ci_upper,
            language_counter
        )
    
    def print_analysis_results(self, successful_results, language_consistency, 
                             avg_keyword_count, min_keywords, max_keywords,
                             avg_jaccard, repetition_rate, top_keywords,
                             avg_processing_time, min_time, max_time,
                             avg_confidence, min_confidence, max_confidence,
                             exact_match_rate, total_pairs, identical_pairs,
                             ci_lower, ci_upper, unique_combinations,
                             language_counter):
        """打印分析結果"""
        print("\n" + "=" * 60)
        print("📊 TC-416 一致性分析結果")
        print("=" * 60)
        
        # 語言統計
        print("🌐 語言偵測統計:")
        for lang, count in language_counter.most_common():
            percentage = (count / len(successful_results)) * 100
            print(f"   {lang}: {count} 次 ({percentage:.1f}%)")
        
        # KPI 指標
        print("\n🎯 核心 KPI 指標:")
        print(f"   語言檢測一致性: {language_consistency*100:.1f}% {'✅' if language_consistency >= 0.95 else '❌'}")
        print(f"   完全相同率: {exact_match_rate*100:.1f}% {'✅' if exact_match_rate >= 0.35 else '❌'} (目標: ≥35%)")
        print(f"   平均 Jaccard 相似度: {avg_jaccard:.3f}")
        
        print(f"\n📈 關鍵字一致性統計:")
        print(f"   總配對數: {total_pairs}")
        print(f"   完全相同配對數: {identical_pairs}")
        print(f"   唯一關鍵字組合數: {unique_combinations}")
        print(f"   95% 信心區間: [{ci_lower*100:.1f}%, {ci_upper*100:.1f}%]")
        print(f"   → 在 95% 信心水準下，任兩次取得相同關鍵字列表的機率為 {ci_lower*100:.1f}% 到 {ci_upper*100:.1f}% 之間")
        
        # 關鍵字統計
        print(f"\n📝 關鍵字統計:")
        print(f"   平均關鍵字數量: {avg_keyword_count:.1f}")
        print(f"   關鍵字數量範圍: {min_keywords} - {max_keywords}")
        print(f"   成功測試數量: {len(successful_results)}/{self.iterations}")
        
        # 效能指標
        print(f"\n⏱️  效能指標:")
        print(f"   平均處理時間: {avg_processing_time:.0f}ms")
        print(f"   處理時間範圍: {min_time}ms - {max_time}ms")
        print(f"   平均信心度: {avg_confidence:.3f}")
        print(f"   信心度範圍: {min_confidence:.3f} - {max_confidence:.3f}")
        
        # 高頻關鍵字
        print(f"\n🔥 最高頻關鍵字 (Top 10):")
        for i, (keyword, freq) in enumerate(top_keywords, 1):
            percentage = (freq / len(successful_results)) * 100
            print(f"   {i:2d}. {keyword} ({freq}次, {percentage:.1f}%)")
        
        # 整體評估
        kpi_pass_count = sum([
            language_consistency >= 0.95,
            exact_match_rate >= 0.35
        ])
        
        print(f"\n🏆 整體評估:")
        print(f"   KPI 通過: {kpi_pass_count}/2")
        if kpi_pass_count == 2:
            print("   ✅ TC-416 測試通過 - AI 一致性表現良好")
        else:
            print("   ❌ TC-416 測試未通過 - AI 一致性需要改善")
    
    async def generate_report(self, successful_results, language_consistency,
                            avg_jaccard, repetition_rate, top_keywords,
                            exact_match_rate, total_pairs, identical_pairs,
                            ci_lower, ci_upper, language_counter):
        """生成詳細報告"""
        timestamp = int(time.time())
        report_file = f"TC416_consistency_report_{self.detected_language}_{timestamp}.json"
        
        report_data = {
            "test_info": {
                "test_case": "TC-416",
                "test_name": "多語言關鍵字提取一致性測試",
                "detected_language": self.detected_language,
                "prompt_version": self.prompt_version_used,
                "execution_date": datetime.now().isoformat(),
                "total_iterations": self.iterations,
                "successful_iterations": len(successful_results),
                "total_execution_time_seconds": self.end_time - self.start_time,
                "jd_content": self.test_jd.strip(),
                "jd_length": len(self.test_jd)
            },
            "language_detection": {
                "statistics": dict(language_counter),
                "consistency_rate": language_consistency
            },
            "kpi_metrics": {
                "language_consistency_rate": language_consistency,
                "exact_match_rate": exact_match_rate,
                "total_pairs": total_pairs,
                "identical_pairs": identical_pairs,
                "confidence_interval_95": {
                    "lower": ci_lower,
                    "upper": ci_upper
                },
                "average_jaccard_similarity": avg_jaccard,
                "keyword_repetition_rate": repetition_rate,
                "kpi_pass_threshold": {
                    "language_consistency": 0.95,
                    "exact_match_rate": 0.35
                }
            },
            "keyword_analysis": {
                "top_keywords": top_keywords,
                "unique_keywords_count": len(set([k for r in successful_results for k in r["keywords"]])),
                "total_keywords_extracted": sum([len(r["keywords"]) for r in successful_results])
            },
            "detailed_results": self.test_results,
            "performance_metrics": {
                "average_processing_time_ms": sum([r["processing_time_ms"] for r in successful_results if r["processing_time_ms"] > 0]) / len([r for r in successful_results if r["processing_time_ms"] > 0]) if any(r["processing_time_ms"] > 0 for r in successful_results) else 0,
                "average_confidence_score": sum([r["confidence_score"] for r in successful_results]) / len(successful_results)
            }
        }
        
        # 保存報告
        report_path = project_root / report_file
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細測試報告已保存:")
        print(f"   檔案: {report_path}")
        print(f"   大小: {os.path.getsize(report_path)} bytes")

def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="TC-416: 多語言關鍵字提取一致性測試",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s                           # 使用預設英文 JD，50次測試
  %(prog)s --jd-file chinese.txt    # 使用檔案中的 JD
  %(prog)s --jd "職位描述內容"        # 直接提供 JD 內容
  %(prog)s --iterations 20          # 只執行 20 次測試
  %(prog)s --jd-file job.txt -n 100 # 使用檔案，執行 100 次測試
        """
    )
    
    # JD 來源（互斥群組）
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
    
    # 測試次數
    parser.add_argument(
        '-n', '--iterations',
        type=int,
        default=50,
        help='測試次數（預設: 50）'
    )
    
    # 延遲時間
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=2.0,
        help='每次測試之間的延遲秒數，用於避免 rate limit（預設: 2.0）'
    )
    
    return parser.parse_args()

async def main():
    """主函數"""
    args = parse_arguments()
    
    print("🚀 啟動 TC-416 多語言關鍵字一致性測試")
    print("📋 這是核心 KPI 測試，將評估 AI 的穩定性和一致性")
    print("")
    
    # 檢查環境
    try:
        from src.services.keyword_extraction_v2 import KeywordExtractionServiceV2
    except ImportError as e:
        print(f"❌ 環境檢查失敗: {e}")
        print("請確保已正確設置 Python 環境和依賴套件")
        return False
    
    # 設置環境變數
    os.environ['PYTHONPATH'] = str(project_root) + ":" + os.environ.get('PYTHONPATH', '')
    
    # 決定使用的 JD
    if args.jd_file:
        try:
            with open(args.jd_file, 'r', encoding='utf-8') as f:
                test_jd = f.read()
            print(f"📄 從檔案載入 JD: {args.jd_file}")
        except Exception as e:
            print(f"❌ 無法讀取檔案 {args.jd_file}: {e}")
            return False
    elif args.jd:
        test_jd = args.jd
        print("📝 使用命令列提供的 JD")
    else:
        test_jd = DEFAULT_JD
        print("📝 使用預設英文 JD")
    
    # 執行測試
    test = TC416ConsistencyTest(iterations=args.iterations, delay_seconds=args.delay)
    test.set_test_jd(test_jd)
    await test.run_consistency_test()
    
    print("\n✨ TC-416 一致性測試執行完成！")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)