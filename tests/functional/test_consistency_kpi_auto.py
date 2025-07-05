#!/usr/bin/env python3
"""
🎯 自動語言偵測版本的一致性 KPI 測試
會根據 JD 內容自動偵測語言，而非強制使用指定語言

使用方式：
    python test_consistency_kpi_auto.py              # 使用預設中文 JD (v1.4.0)
    python test_consistency_kpi_auto.py 1.3.0        # 指定版本
    python test_consistency_kpi_auto.py 1.3.0 jd.txt # 指定 JD 檔案
"""

import asyncio
import json
import os
import sys
from collections import Counter
from datetime import datetime

import httpx

# 預設的測試 JD（中文）
DEFAULT_JD = """
Project Manager
Responsible for wafer outsourcing and cost negotiation, including:
Competitive Price: RFQ, price negotiation, cost prediction, cost reduction initiatives, CA.Capacity: long-term reservation, short-term fulfillment, acting as a bridge for internal and external parties to reach goals. Contract: NDA and short-term agreements. Project management (e.g. procurement system)
**Requirement

**Proactive working attitude and good communication skills, with negotiation capability being a plus.Experience in handling wafer sourcing or procurement. Project management and business acumen.

"""

async def test_consistency_kpi(prompt_version: str = "1.4.0", job_description: str = None, num_tests: int = 20):
    """
    執行一致性 KPI 測試（使用自動語言偵測）
    """
    base_url = "http://localhost:8000/api/v1"
    
    # 使用提供的 JD 或預設值
    jd_to_test = job_description or DEFAULT_JD
    jd_preview = jd_to_test[:100] + "..." if len(jd_to_test) > 100 else jd_to_test
    
    print("🎯 一致性 KPI 測試（自動語言偵測版）")
    print("=" * 80)
    print(f"Prompt 版本: {prompt_version}")
    print("語言設定: auto (自動偵測)")
    print(f"測試次數: {num_tests}")
    print(f"JD 預覽: {jd_preview}")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 儲存所有結果
        all_results = []
        successful_runs = 0
        detected_languages = []
        
        print(f"\n📊 執行 {num_tests} 次測試...")
        
        for run in range(num_tests):
            request_data = {
                "job_description": jd_to_test,
                "max_keywords": 16,
                "prompt_version": prompt_version,
                "language": "auto"  # 使用自動偵測
            }
            
            try:
                response = await client.post(
                    f"{base_url}/extract-jd-keywords",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    keywords = result["data"]["keywords"]
                    detected_lang = result["data"].get("detected_language", "unknown")
                    
                    all_results.append(keywords)
                    detected_languages.append(detected_lang)
                    successful_runs += 1
                    
                    print(f"   Run {run+1:2d}: ✓ ({len(keywords)} keywords, lang={detected_lang})")
                else:
                    print(f"   Run {run+1:2d}: ✗ (Status {response.status_code})")
                    
            except Exception as e:
                print(f"   Run {run+1:2d}: ✗ (Error: {str(e)})")
            
            # 延遲避免 rate limiting
            await asyncio.sleep(1.5)
        
        # 分析結果
        if successful_runs < 2:
            print("\n❌ 測試失敗：成功次數不足")
            return
        
        print(f"\n✅ 成功執行: {successful_runs}/{num_tests} 次")
        
        # 語言偵測統計
        lang_counter = Counter(detected_languages)
        print("\n🌐 語言偵測統計:")
        for lang, count in lang_counter.most_common():
            print(f"   {lang}: {count} 次 ({count/successful_runs*100:.1f}%)")
        
        # 關鍵字分析
        if all_results:
            # 統計所有關鍵字出現頻率
            keyword_counter = Counter()
            for result in all_results:
                keyword_counter.update(result)
            
            print("\n📊 關鍵字頻率分析:")
            print(f"   總共出現 {len(keyword_counter)} 個不同關鍵字")
            
            # 顯示前 20 個最常出現的關鍵字
            print("\n🔝 前 20 個高頻關鍵字:")
            for i, (keyword, count) in enumerate(keyword_counter.most_common(20), 1):
                percentage = (count / successful_runs) * 100
                print(f"   {i:2d}. {keyword}: {count} 次 ({percentage:.1f}%)")
            
            # 計算唯一組合
            unique_combinations = {}
            for idx, result in enumerate(all_results):
                # 使用排序後的關鍵字作為組合的標識
                combo_key = tuple(sorted(result))
                if combo_key not in unique_combinations:
                    unique_combinations[combo_key] = []
                unique_combinations[combo_key].append(idx + 1)
            
            # 計算一致性和相似度
            total_pairs = successful_runs * (successful_runs - 1) // 2
            identical_pairs = 0
            jaccard_scores = []
            
            for i in range(len(all_results)):
                for j in range(i + 1, len(all_results)):
                    set1 = set(all_results[i])
                    set2 = set(all_results[j])
                    
                    # 檢查是否完全相同
                    if sorted(all_results[i]) == sorted(all_results[j]):
                        identical_pairs += 1
                    
                    # 計算 Jaccard 相似度
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    if union > 0:
                        jaccard = intersection / union
                        jaccard_scores.append(jaccard)
            
            consistency_rate = identical_pairs / total_pairs if total_pairs > 0 else 0
            
            print("\n📊 一致性 KPI 分析:")
            print(f"   總測試次數: {successful_runs}")
            print(f"   唯一結果組合: {len(unique_combinations)} 個")
            
            # 顯示組合分布
            sorted_combos = sorted(unique_combinations.items(), key=lambda x: len(x[1]), reverse=True)
            print("\n   組合分布:")
            for idx, (combo, occurrences) in enumerate(sorted_combos[:5], 1):
                percentage = (len(occurrences) / successful_runs) * 100
                print(f"   - 組合{idx}: {len(occurrences)}次 ({percentage:.1f}%)")
            if len(sorted_combos) > 5:
                print(f"   - 其他{len(sorted_combos)-5}個組合: 各出現較少次數")
            
            print("\n   配對統計:")
            print(f"   總配對數: {total_pairs}")
            print(f"   相同配對數: {identical_pairs}")
            print(f"   完全一致率: {consistency_rate:.1%}")
            
            # 計算 95% 信心區間
            # 使用二項分佈的正態近似
            import math
            
            if total_pairs > 0:
                p = consistency_rate
                n = total_pairs
                
                # 標準誤差
                se = math.sqrt(p * (1 - p) / n) if p > 0 and p < 1 else 0
                
                # 95% 信心區間 (z = 1.96)
                z = 1.96
                margin_of_error = z * se
                ci_lower = max(0, p - margin_of_error)
                ci_upper = min(1, p + margin_of_error)
                
                print("\n📈 統計分析:")
                print(f"   95% 信心區間: [{ci_lower:.1%}, {ci_upper:.1%}]")
                print(f"   標準誤差: {se:.3f}")
                print(f"   誤差範圍: ±{margin_of_error:.1%}")
                
                # 解釋信心區間
                print("\n💡 解釋:")
                print("   在 95% 的信心水準下，任兩次執行取得相同關鍵字列表的機率為:")
                print(f"   {ci_lower:.1%} 到 {ci_upper:.1%} 之間")
                
                # 計算達到目標所需的樣本數
                target_rate = 0.35
                if consistency_rate < target_rate:
                    # 使用當前的變異性估算需要多少次測試
                    required_identical = math.ceil(target_rate * total_pairs)
                    print("\n📊 達標分析:")
                    print(f"   目標一致性率: {target_rate:.0%}")
                    print(f"   需要相同配對數: {required_identical} (目前: {identical_pairs})")
                    print(f"   差距: {required_identical - identical_pairs} 對")
            
            # KPI 判定
            target_rate = 0.35  # 35% 目標值
            if consistency_rate >= target_rate:
                print(f"\n🎯 KPI 評估: ✅ 通過！({consistency_rate:.1%} ≥ 35%)")
            else:
                print(f"\n🎯 KPI 評估: ❌ 未達標！({consistency_rate:.1%} < 35%)")
            
            # Jaccard 相似度分析
            if jaccard_scores:
                avg_jaccard = sum(jaccard_scores) / len(jaccard_scores)
                min_jaccard = min(jaccard_scores)
                max_jaccard = max(jaccard_scores)
                
                # 計算 Jaccard 分數的標準差
                jaccard_variance = sum((x - avg_jaccard) ** 2 for x in jaccard_scores) / len(jaccard_scores)
                jaccard_std = math.sqrt(jaccard_variance)
                
                print("\n📊 Jaccard 相似度分析:")
                print(f"   平均相似度: {avg_jaccard:.1%}")
                print(f"     → 任意兩次測試平均有 {avg_jaccard:.1%} 的關鍵字重疊")
                print(f"     → 16個關鍵字中，平均約{int(16 * avg_jaccard)}個是相同的")
                
                print(f"\n   最低相似度: {min_jaccard:.1%}")
                print(f"     → 最不相似的兩次測試仍有 {min_jaccard:.1%} 重疊")
                print(f"     → 16個關鍵字中，至少有{int(16 * min_jaccard)}個相同")
                
                print(f"\n   最高相似度: {max_jaccard:.1%}")
                if max_jaccard == 1.0:
                    print("     → 有些測試對的關鍵字完全相同")
                else:
                    print(f"     → 最相似的兩次測試有 {max_jaccard:.1%} 重疊")
                
                print(f"\n   標準差: {jaccard_std:.3f}")
                if jaccard_std < 0.1:
                    print("     → 相似度的離散程度很小，表示穩定性高")
                elif jaccard_std < 0.2:
                    print("     → 相似度的離散程度中等，表示有一定變化")
                else:
                    print("     → 相似度的離散程度較大，表示變化較多")
                
                # 分組統計
                high_similarity = sum(1 for s in jaccard_scores if s >= 0.8)
                medium_similarity = sum(1 for s in jaccard_scores if 0.5 <= s < 0.8)
                low_similarity = sum(1 for s in jaccard_scores if s < 0.5)
                
                print("\n📊 相似度分布:")
                print(f"   高相似度 (≥80%): {high_similarity} 對 ({high_similarity/len(jaccard_scores)*100:.1f}%)")
                print(f"   中相似度 (50-79%): {medium_similarity} 對 ({medium_similarity/len(jaccard_scores)*100:.1f}%)")
                print(f"   低相似度 (<50%): {low_similarity} 對 ({low_similarity/len(jaccard_scores)*100:.1f}%)")
            
            # 儲存詳細結果到 JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"consistency_test_results_{timestamp}.json"
            
            results = {
                "test_info": {
                    "timestamp": datetime.now().isoformat(),
                    "prompt_version": prompt_version,
                    "language": "auto",
                    "num_tests": num_tests,
                    "successful_runs": successful_runs,
                    "jd_preview": jd_preview
                },
                "consistency_analysis": {
                    "total_pairs": total_pairs,
                    "identical_pairs": identical_pairs,
                    "consistency_rate": consistency_rate,
                    "confidence_interval_95": {
                        "lower": ci_lower if 'ci_lower' in locals() else None,
                        "upper": ci_upper if 'ci_upper' in locals() else None,
                        "margin_of_error": margin_of_error if 'margin_of_error' in locals() else None
                    }
                },
                "jaccard_analysis": {
                    "average": avg_jaccard if jaccard_scores else None,
                    "min": min_jaccard if jaccard_scores else None,
                    "max": max_jaccard if jaccard_scores else None,
                    "std_dev": jaccard_std if jaccard_scores else None,
                    "distribution": {
                        "high": high_similarity if jaccard_scores else 0,
                        "medium": medium_similarity if jaccard_scores else 0,
                        "low": low_similarity if jaccard_scores else 0
                    }
                },
                "keyword_frequency": dict(keyword_counter.most_common()),
                "language_detection": dict(lang_counter),
                "all_results": all_results,
                "kpi_status": "PASSED" if consistency_rate >= target_rate else "FAILED"
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 詳細結果已儲存至: {output_file}")

async def main():
    """主程式入口"""
    # 解析命令列參數
    prompt_version = "1.4.0"  # 預設版本
    job_description = None
    
    if len(sys.argv) > 1:
        prompt_version = sys.argv[1]
    
    if len(sys.argv) > 2:
        # 從檔案讀取 JD
        jd_file = sys.argv[2]
        if jd_file and os.path.exists(jd_file):
            with open(jd_file, encoding='utf-8') as f:
                job_description = f.read()
            print(f"📄 從檔案載入 JD: {jd_file}")
    
    # 檢查伺服器是否運行
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            if response.status_code != 200:
                print("❌ API 伺服器未回應")
                return
    except Exception as e:
        print(f"❌ 無法連接到 API 伺服器: {str(e)}")
        print("\n請先啟動 API 伺服器:")
        print("uvicorn src.main:app --reload --port 8000")
        return
    
    # 執行測試
    await test_consistency_kpi(prompt_version, job_description)

if __name__ == "__main__":
    asyncio.run(main())