#!/usr/bin/env python3
"""檢查測試結果內容的變化性"""

import json
from pathlib import Path
from collections import Counter
import hashlib

def check_content_variation(results_dir):
    results_path = Path(results_dir)
    
    # 存儲各欄位的內容哈希值
    field_hashes = {
        'CoreStrengths': [],
        'KeyGaps': [],
        'QuickImprovements': [],
        'OverallAssessment': []
    }
    
    # 存儲前幾個字的模式
    first_words_patterns = {
        'CoreStrengths': [],
        'KeyGaps': [],
        'QuickImprovements': [],
        'OverallAssessment': []
    }
    
    test_files = sorted(results_path.glob("test_*.json"))
    
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            gap_analysis = data['response']['data'].get('gap_analysis', {})
            
            for field in field_hashes.keys():
                content = gap_analysis.get(field, '')
                if content:
                    # 計算內容哈希
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    field_hashes[field].append(content_hash)
                    
                    # 提取前幾個字（去除HTML標籤）
                    clean_content = content.replace('<ol>', '').replace('<li>', '').replace('<p>', '')
                    clean_content = clean_content.replace('</ol>', '').replace('</li>', '').replace('</p>', '')
                    clean_content = clean_content.replace('<strong>', '').replace('</strong>', '')
                    first_words = ' '.join(clean_content.split()[:10])
                    first_words_patterns[field].append(first_words)
                    
        except Exception as e:
            print(f"處理檔案 {test_file} 時發生錯誤: {e}")
    
    print("\n內容變化性分析")
    print("="*80)
    
    # 分析每個欄位的唯一性
    for field, hashes in field_hashes.items():
        unique_count = len(set(hashes))
        total_count = len(hashes)
        
        print(f"\n{field}:")
        print(f"  總數: {total_count}")
        print(f"  唯一內容數: {unique_count}")
        print(f"  重複率: {(total_count - unique_count) / total_count * 100:.1f}%")
        
        # 找出最常見的內容模式
        hash_counter = Counter(hashes)
        most_common = hash_counter.most_common(3)
        
        if most_common[0][1] > 1:
            print(f"  最常重複的內容出現 {most_common[0][1]} 次")
            
        # 分析開頭模式
        pattern_counter = Counter(first_words_patterns[field])
        most_common_patterns = pattern_counter.most_common(3)
        
        print(f"\n  最常見的開頭模式:")
        for pattern, count in most_common_patterns:
            if count > 1:
                print(f"    '{pattern[:50]}...' (出現 {count} 次)")
    
    # 檢查是否所有測試都使用相同的輸入
    print("\n\n輸入資料檢查:")
    print("="*80)
    
    jd_hashes = []
    resume_hashes = []
    
    for test_file in test_files[:10]:  # 只檢查前10個
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            jd = data['request']['job_description']
            resume = data['request']['resume']
            
            jd_hashes.append(hashlib.md5(jd.encode()).hexdigest())
            resume_hashes.append(hashlib.md5(resume.encode()).hexdigest())
            
        except Exception:
            pass
    
    if len(set(jd_hashes)) == 1:
        print("⚠️  所有測試使用相同的 Job Description")
    else:
        print("✓ 測試使用不同的 Job Description")
        
    if len(set(resume_hashes)) == 1:
        print("⚠️  所有測試使用相同的 Resume")
    else:
        print("✓ 測試使用不同的 Resume")

if __name__ == "__main__":
    results_dir = "/Users/yuwenhao/Documents/GitHub/azure_fastapi/gap_analysis_test_results_20250709_140407"
    check_content_variation(results_dir)