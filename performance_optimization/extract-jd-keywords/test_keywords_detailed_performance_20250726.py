#!/usr/bin/env python3
"""
關鍵字提取 API 詳細效能分析腳本
測試日期: 2025-07-26
目標: 分析 extract-jd-keywords API 各個步驟的時間開銷
"""

import asyncio
import time
import statistics
import json
from typing import Dict
import httpx
from datetime import datetime
import os
from dotenv import load_dotenv
import random
import csv

# 載入環境變數
load_dotenv()

# API 配置
API_URL = "https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/extract-jd-keywords"
# 嘗試多個可能的環境變數名稱
API_KEY = os.getenv("AZURE_FUNCTION_KEY") or os.getenv("AZURE_FUNCTION_DEFAULT_KEY") or os.getenv("AZURE_FUNCTION_MASTER_KEY") or ""

# 測試資料集 - 每種語言6個不同的JD，避免快取
TEST_CASES = {
    "en": [
        # JD 1: Software Engineer (約 600 字)
        """
We are seeking a talented Software Engineer to join our innovative team at TechCorp. 
The ideal candidate will have 5+ years of experience in full-stack development with 
expertise in Python, Django, React, and cloud technologies. You will be responsible 
for designing and implementing scalable web applications, working with microservices 
architecture, and optimizing database performance using PostgreSQL and MongoDB.

Key responsibilities include developing RESTful APIs, implementing CI/CD pipelines 
with Jenkins and GitLab, containerizing applications using Docker and Kubernetes, 
and ensuring code quality through comprehensive testing. Experience with AWS services 
including EC2, S3, Lambda, and RDS is essential. You should be proficient in agile 
methodologies, code review processes, and technical documentation.

We value candidates who demonstrate strong problem-solving abilities, excellent 
communication skills, and a passion for learning new technologies. Experience with 
machine learning frameworks like TensorFlow or PyTorch is a plus. You will collaborate 
with cross-functional teams, mentor junior developers, and contribute to architectural 
decisions. Join us in building cutting-edge solutions that impact millions of users 
globally while working in a flexible, remote-friendly environment with competitive 
compensation and growth opportunities.
        """.strip(),
        
        # JD 2: Data Engineer (約 650 字)
        """
Join our Data Engineering team as a Senior Data Engineer where you'll build and 
maintain large-scale data pipelines processing billions of events daily. We need 
someone with 4+ years of experience in data engineering, proficient in Apache Spark, 
Kafka, and Airflow. You'll work with both batch and real-time data processing systems, 
designing ETL pipelines and data warehousing solutions using technologies like 
Snowflake, BigQuery, or Redshift.

Your responsibilities will include developing data ingestion frameworks, implementing 
data quality monitoring, optimizing query performance, and building data APIs for 
downstream consumers. Strong programming skills in Python and Scala are required, 
along with expertise in SQL and NoSQL databases. Experience with data modeling, 
dimensional design, and data governance best practices is essential.

You should be comfortable with cloud platforms (AWS, GCP, or Azure), infrastructure 
as code using Terraform, and monitoring tools like Datadog or Prometheus. Knowledge 
of data streaming architectures, event-driven systems, and distributed computing 
principles is crucial. We're looking for someone who can collaborate with data 
scientists, analysts, and business stakeholders to deliver reliable, scalable data 
solutions.

This role offers the opportunity to work with cutting-edge big data technologies, 
solve complex scalability challenges, and directly impact data-driven decision making 
across the organization. We provide excellent benefits, learning opportunities, and 
a collaborative work environment.
        """.strip(),
        
        # JD 3: DevOps Engineer (約 700 字)
        """
We are looking for an experienced DevOps Engineer to join our infrastructure team 
and help us scale our platform to support millions of users. The ideal candidate 
will have 5+ years of experience in DevOps/SRE roles with deep expertise in cloud 
infrastructure, automation, and system reliability. You'll be responsible for 
designing, implementing, and maintaining our cloud infrastructure on AWS and GCP.

Key technical requirements include proficiency in Infrastructure as Code using 
Terraform and CloudFormation, container orchestration with Kubernetes and Helm, 
CI/CD pipeline design using Jenkins, GitLab CI, or GitHub Actions, and monitoring 
solutions with Prometheus, Grafana, and ELK stack. Experience with service mesh 
technologies like Istio, API gateway management, and microservices architecture 
is essential.

You should have strong scripting skills in Python, Bash, and Go, with the ability 
to automate repetitive tasks and build internal tools. Knowledge of security best 
practices, including secrets management with Vault, network security, and compliance 
frameworks is required. Experience with database administration (PostgreSQL, MySQL, 
Redis) and message queuing systems (RabbitMQ, Kafka) is highly valued.

The role involves on-call responsibilities, incident response, and continuous 
improvement of system reliability. You'll work closely with development teams to 
ensure smooth deployments, optimize application performance, and maintain SLAs. 
We offer competitive compensation, flexible working hours, professional development 
budget, and the chance to work with modern technologies in a fast-paced environment.
        """.strip(),
        
        # JD 4: Frontend Developer (約 550 字)
        """
We're seeking a passionate Frontend Developer to create exceptional user experiences 
for our web applications. The ideal candidate has 4+ years of experience building 
modern, responsive web applications using React, TypeScript, and Next.js. You'll 
work closely with our design team to implement pixel-perfect interfaces while 
ensuring optimal performance and accessibility.

Technical requirements include expert-level knowledge of JavaScript ES6+, React 
hooks and context API, state management with Redux or MobX, and CSS-in-JS solutions 
like styled-components or Emotion. Experience with modern build tools (Webpack, 
Rollup, Vite), testing frameworks (Jest, React Testing Library, Cypress), and 
performance optimization techniques is essential. You should be proficient in 
responsive design, cross-browser compatibility, and PWA development.

The role involves collaborating with backend engineers to integrate RESTful and 
GraphQL APIs, implementing real-time features using WebSockets, and optimizing 
bundle sizes and load times. Knowledge of design systems, component libraries, 
and micro-frontend architecture is highly valued. Experience with React Native 
for mobile development is a plus.

You'll contribute to our design system, conduct code reviews, and mentor junior 
developers. We value clean code, attention to detail, and a user-centric mindset. 
Join our team to work on products used by millions while enjoying remote work 
flexibility, continuous learning opportunities, and a supportive team environment.
        """.strip(),
        
        # JD 5: Machine Learning Engineer (約 750 字)
        """
Join our AI team as a Machine Learning Engineer to develop and deploy cutting-edge 
ML models at scale. We're looking for someone with 5+ years of experience in machine 
learning and deep learning, with a strong background in Python, TensorFlow, PyTorch, 
and scikit-learn. You'll work on diverse projects including natural language processing, 
computer vision, recommendation systems, and predictive analytics.

Core responsibilities include designing and implementing ML pipelines, conducting 
experiments and A/B tests, optimizing model performance and inference speed, and 
deploying models to production using MLflow, Kubeflow, or SageMaker. You should 
have experience with distributed training frameworks, GPU optimization, and model 
serving infrastructure. Proficiency in data preprocessing, feature engineering, 
and model evaluation metrics is essential.

Technical requirements include strong programming skills in Python and familiarity 
with C++ for performance-critical components, experience with big data tools like 
Spark and Hadoop, knowledge of SQL and NoSQL databases, and expertise in cloud 
platforms (AWS, GCP, or Azure). Understanding of MLOps practices, including model 
versioning, monitoring, and continuous integration/deployment for ML systems is crucial.

You should be comfortable with various ML algorithms including deep neural networks, 
gradient boosting, clustering, and reinforcement learning. Experience with specialized 
frameworks like Hugging Face Transformers, OpenCV, or JAX is highly valued. Strong 
mathematical foundation in linear algebra, probability, and statistics is required.

This role offers the opportunity to work on challenging problems, publish research 
papers, attend conferences, and shape the future of AI products. We provide competitive 
compensation, stock options, state-of-the-art hardware, and a collaborative research 
environment. Join us to push the boundaries of what's possible with machine learning.
        """.strip(),
        
        # JD 6: Backend Developer (約 600 字)
        """
We are hiring a Senior Backend Developer to architect and build scalable server-side 
applications. The ideal candidate has 6+ years of experience in backend development 
with expertise in Java, Spring Boot, and microservices architecture. You'll design 
and implement high-performance APIs, work with distributed systems, and ensure our 
services can handle millions of requests per day.

Key technical skills include proficiency in Java 11+, Spring ecosystem (Boot, Cloud, 
Security), RESTful API design and GraphQL, message queuing with RabbitMQ or Kafka, 
and database technologies including PostgreSQL, MongoDB, and Redis. Experience with 
event-driven architecture, CQRS pattern, and domain-driven design is highly valued. 
You should be comfortable with containerization using Docker and orchestration with 
Kubernetes.

Responsibilities include developing scalable microservices, implementing authentication 
and authorization systems, optimizing database queries and caching strategies, and 
ensuring high availability and fault tolerance. Knowledge of distributed tracing, 
service mesh, and API gateway patterns is important. Experience with performance 
profiling, load testing, and optimization techniques is essential.

You'll collaborate with frontend teams, DevOps engineers, and product managers to 
deliver features that delight our users. We value clean code, comprehensive testing, 
and documentation. Experience with agile methodologies, code review best practices, 
and mentoring is expected. Join our team to work on challenging technical problems 
while enjoying flexible work arrangements, professional growth opportunities, and 
excellent benefits.
        """.strip()
    ],
    
    "zh-TW": [
        # JD 1: 資深後端工程師 (約 600 字)
        """
我們正在尋找一位資深後端工程師加入我們的技術團隊。理想的候選人需具備 5 年以上的
後端開發經驗，精通 Python、Django、FastAPI 等框架，並熟悉微服務架構設計。您將
負責設計和實現高性能的 API 服務，處理每日數百萬次的請求，並確保系統的穩定性和
可擴展性。

技術要求包括：精通 Python 3.8+ 和異步編程，熟悉 RESTful API 和 GraphQL 設計，
具備 PostgreSQL、MongoDB、Redis 等資料庫使用經驗，了解訊息佇列系統如 RabbitMQ 
或 Kafka，掌握容器化技術 Docker 和 Kubernetes。您需要有分散式系統設計經驗，
理解 CAP 定理和一致性協議，並能實現高可用性和容錯機制。

工作職責包括開發和維護微服務，實施 API 安全性和認證機制，優化資料庫查詢和快取
策略，進行代碼審查和技術文檔撰寫。我們重視測試驅動開發，您需要編寫單元測試和
整合測試，確保代碼品質。具備 CI/CD 流程經驗，熟悉 GitLab CI 或 Jenkins 是必要的。

加入我們，您將有機會參與大規模系統的設計和優化，使用最新的技術棧解決複雜的技術
挑戰。我們提供具競爭力的薪酬、彈性工作時間、持續學習的機會，以及開放創新的工作
環境。如果您熱愛技術、追求卓越，歡迎加入我們的團隊。
        """.strip(),
        
        # JD 2: 資料科學家 (約 650 字)
        """
我們正在招募一位經驗豐富的資料科學家，協助我們運用數據驅動業務決策。理想人選
需具備 4 年以上資料分析和機器學習經驗，精通 Python 數據分析生態系統，包括 
Pandas、NumPy、Scikit-learn、TensorFlow 和 PyTorch。您將負責開發預測模型、
進行 A/B 測試、建立推薦系統，並將研究成果轉化為實際的產品功能。

核心技能要求：深入理解統計學和機器學習算法，包括迴歸分析、分類、聚類、深度學習
等；熟練使用 SQL 進行資料查詢和處理；具備大數據工具如 Spark、Hadoop 使用經驗；
掌握資料視覺化工具如 Tableau、Power BI 或 Python 視覺化庫。您應該熟悉特徵工程、
模型評估指標、交叉驗證等概念，並能處理不平衡資料集和時間序列分析。

工作內容包括：與業務團隊合作定義問題和成功指標，收集、清理和探索大規模資料集，
建立和部署機器學習模型，設計和執行 A/B 測試評估模型效果，創建儀表板和報告呈現
洞察結果。您需要具備良好的溝通能力，能向非技術人員解釋複雜的分析結果。

我們特別重視自然語言處理（NLP）和深度學習經驗，熟悉 BERT、GPT 等預訓練模型
的應用。雲端平台經驗（AWS SageMaker、Google Cloud AI Platform）將是加分項。
加入我們，您將有機會處理 TB 級資料，運用最新的 AI 技術解決實際業務問題，並在
快速成長的環境中發揮影響力。
        """.strip(),
        
        # JD 3: 前端工程師 (約 700 字)
        """
我們正在尋找一位充滿熱情的前端工程師，負責打造卓越的使用者體驗。理想候選人需有
4 年以上前端開發經驗，精通 React、Vue.js 或 Angular 等現代前端框架，並對 UI/UX 
設計有深入理解。您將與設計團隊密切合作，將設計稿轉化為流暢、響應式的網頁應用，
確保在各種設備和瀏覽器上都能提供一致的體驗。

技術要求包括：精通 JavaScript ES6+、TypeScript，深入理解 React Hooks、Context API
和狀態管理（Redux、MobX），熟悉現代 CSS 預處理器（Sass、Less）和 CSS-in-JS 解決
方案，掌握前端建構工具（Webpack、Rollup、Vite）和版本控制（Git）。您需要了解
網頁性能優化技巧，包括程式碼分割、延遲載入、圖片優化等，並能使用 Chrome DevTools
進行性能分析。

工作職責涵蓋：開發和維護複雜的單頁應用（SPA），實現響應式設計和跨瀏覽器相容性，
整合 RESTful API 和 GraphQL，實施前端安全最佳實踐，編寫可維護、可測試的程式碼。
您需要熟悉前端測試框架（Jest、Mocha、Cypress），並能建立自動化測試。對無障礙
設計（Accessibility）和 SEO 優化的理解也很重要。

加分技能包括：React Native 或 Flutter 行動應用開發經驗，PWA（漸進式網頁應用）
開發經驗，WebGL、Canvas 或 SVG 動畫經驗，微前端架構知識。我們重視持續學習和
知識分享，您將有機會參與技術決策、指導初級工程師，並在技術社群分享經驗。

我們提供具競爭力的薪酬福利、彈性遠距工作、最新的開發設備、技術會議補助，以及
充滿挑戰和成長機會的工作環境。如果您對創造優質的使用者體驗充滿熱情，歡迎加入
我們的團隊。
        """.strip(),
        
        # JD 4: DevOps 工程師 (約 550 字)
        """
我們正在招聘一位經驗豐富的 DevOps 工程師，協助我們建立和維護可靠、可擴展的
基礎設施。理想人選需具備 5 年以上 DevOps 或 SRE 經驗，精通雲端平台（AWS、GCP
或 Azure），並對自動化和系統可靠性有深入理解。您將負責設計和實施 CI/CD 流程，
管理容器化應用，並確保系統的高可用性。

核心技術要求：精通基礎設施即代碼（Terraform、CloudFormation），熟練使用容器
技術（Docker、Kubernetes、Helm），掌握 CI/CD 工具（Jenkins、GitLab CI、GitHub 
Actions），具備監控和日誌系統經驗（Prometheus、Grafana、ELK Stack）。您需要
有 Linux 系統管理經驗，熟悉網路協議和安全最佳實踐。

工作內容包括：設計和維護雲端基礎設施，實施自動化部署和配置管理，建立監控告警
系統，進行容量規劃和成本優化，處理事件響應和故障排除。您需要與開發團隊合作，
確保應用程式的順利部署和運行。對服務網格（Istio）、API 閘道、負載均衡等技術
的了解將是優勢。

我們重視 DevOps 文化，您將推動持續改進，實施 SRE 最佳實踐，並參與 on-call 
輪值。加入我們，您將有機會使用最新的雲端技術，解決大規模系統的挑戰，並直接
影響產品的穩定性和用戶體驗。我們提供優厚的薪資待遇、靈活的工作安排、專業
認證補助，以及與優秀團隊共同成長的機會。
        """.strip(),
        
        # JD 5: 產品經理 (約 750 字)
        """
我們正在尋找一位資深產品經理來領導我們的核心產品線。理想的候選人需要有 6 年以上
產品管理經驗，最好在 B2B SaaS 或平台型產品領域。您將負責制定產品策略、規劃路線圖，
並與工程、設計、業務團隊緊密合作，打造用戶喜愛的產品。您需要具備數據驅動的思維，
能夠通過用戶研究和數據分析來做出明智的產品決策。

核心能力要求：深入理解產品開發生命週期，精通敏捷開發方法（Scrum、Kanban），
具備出色的數據分析能力，熟練使用 Google Analytics、Amplitude、Mixpanel 等分析
工具，掌握 A/B 測試方法論，能夠撰寫清晰的產品需求文檔（PRD）和用戶故事。您需要
有 SQL 基礎，能夠自行查詢數據並生成洞察報告。

工作職責包括：進行市場調研和競品分析，定義產品願景和策略，管理產品待辦事項並
確定優先級，與利益相關者溝通並獲得支持，追蹤產品指標並持續優化。您將領導跨職能
團隊，確保產品按時交付並達到質量標準。具備技術背景將有助於與工程團隊的溝通，
了解 API、系統架構、技術債務等概念。

我們特別重視以下經驗：國際化產品經驗，了解不同市場的需求差異；平台型產品經驗，
理解網絡效應和生態系統建設；B2B 銷售流程知識，能夠支持銷售團隊；定價策略制定，
理解不同商業模式的優劣。您需要具備優秀的溝通和簡報技巧，能夠向高層管理者和
外部客戶展示產品價值。

加入我們的團隊，您將有機會定義產品方向，直接影響公司的成長軌跡。我們提供有
競爭力的薪酬、股票期權、靈活的工作環境、定期的用戶訪談機會，以及與優秀團隊
共同打造世界級產品的機會。如果您對創造價值充滿熱情，歡迎加入我們。
        """.strip(),
        
        # JD 6: 全端工程師 (約 600 字)
        """
我們正在招募一位全端工程師，負責開發端到端的網路應用解決方案。理想人選需具備
5 年以上全端開發經驗，同時精通前端和後端技術。您將參與產品的完整開發週期，從
需求分析、系統設計到部署維護，打造高品質的用戶體驗。我們需要一位能夠獨立解決
問題、具備產品思維的工程師。

技術要求涵蓋：前端技術包括 React、Vue.js、TypeScript、Tailwind CSS，後端技術
包括 Node.js、Python、Go 其中至少一種，資料庫經驗涵蓋 PostgreSQL、MongoDB、
Redis，熟悉 RESTful API 和 GraphQL 設計，掌握雲端服務（AWS、GCP）和容器技術。
您需要了解網路安全基礎，包括 OWASP Top 10、JWT、OAuth 2.0 等。

工作內容包括：設計和開發響應式網頁應用，建立可擴展的後端服務和 API，實施資料庫
設計和優化，整合第三方服務和 API，進行代碼審查和技術文檔撰寫。您將與產品經理和
設計師合作，將業務需求轉化為技術解決方案。對 DevOps 實踐的了解，如 CI/CD、
監控、日誌管理，將使您更好地維護產品。

我們重視的特質：主動積極的學習態度，良好的問題解決能力，優秀的團隊合作精神，
對代碼品質的追求。加分項包括開源專案貢獻經驗、技術部落格撰寫、新技術的快速
學習能力。您將有機會接觸多元的技術棧，參與架構決策，並在快速成長的環境中
提升技能。我們提供優渥的薪資福利、彈性工作時間、教育訓練補助，以及充滿挑戰
與成就感的工作機會。
        """.strip()
    ]
}

class DetailedPerformanceTester:
    def __init__(self):
        self.results = []
        self.headers = {
            "Content-Type": "application/json"
        }
        self.url = f"{API_URL}?code={API_KEY}" if API_KEY else API_URL
        
    async def test_single_request(self, job_description: str, language: str, test_name: str, test_number: int) -> Dict:
        """測試單一請求的詳細效能"""
        total_start = time.time()
        
        # 準備請求
        payload = {
            "job_description": job_description,
            "language": language,
            "max_keywords": 16,
            "prompt_version": "1.4.0"
        }
        
        timing_details = {
            "preparation_ms": 0,
            "network_request_ms": 0,
            "server_processing_ms": 0,
            "response_parsing_ms": 0,
            "total_ms": 0
        }
        
        try:
            # 1. 準備階段
            prep_start = time.time()
            _ = json.dumps(payload)  # 確保 payload 可序列化
            timing_details["preparation_ms"] = (time.time() - prep_start) * 1000
            
            # 2. 網路請求階段
            network_start = time.time()
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.url, json=payload, headers=self.headers)
            timing_details["network_request_ms"] = (time.time() - network_start) * 1000
            
            # 3. 解析回應階段
            parse_start = time.time()
            response_data = response.json()
            timing_details["response_parsing_ms"] = (time.time() - parse_start) * 1000
            
            # 計算總時間
            timing_details["total_ms"] = (time.time() - total_start) * 1000
            
            # 從回應中提取伺服器端的時間資訊
            if response.status_code == 200 and "data" in response_data:
                data = response_data["data"]
                server_timing = data.get("timing_breakdown", {})
                processing_time = data.get("processing_time_ms", 0)
                
                # 伺服器端詳細時間
                timing_details["server_breakdown"] = {
                    "validation_ms": server_timing.get("validation_ms", 0),
                    "language_detection_ms": server_timing.get("language_detection_ms", 0),
                    "keyword_extraction_ms": server_timing.get("keyword_extraction_ms", 0),
                    "total_server_ms": server_timing.get("total_ms", processing_time)
                }
                
                # 計算網路延遲
                timing_details["network_latency_ms"] = timing_details["network_request_ms"] - timing_details["server_breakdown"]["total_server_ms"]
            
            result = {
                "test_name": test_name,
                "test_number": test_number,
                "language": language,
                "jd_length": len(job_description),
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "timing": timing_details,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                result["keywords_count"] = data.get("keyword_count", 0)
                result["extraction_method"] = data.get("extraction_method", "")
                result["confidence_score"] = data.get("confidence_score", 0)
                result["cache_hit"] = data.get("cache_hit", False)
            else:
                result["error"] = response_data
                
        except Exception as e:
            timing_details["total_ms"] = (time.time() - total_start) * 1000
            result = {
                "test_name": test_name,
                "test_number": test_number,
                "language": language,
                "jd_length": len(job_description),
                "success": False,
                "error": str(e),
                "timing": timing_details,
                "timestamp": datetime.now().isoformat()
            }
            
        return result
    
    async def run_comprehensive_tests(self):
        """執行全面的效能測試"""
        print("=== 關鍵字提取 API 詳細效能分析 ===")
        print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API URL: {self.url}")
        print("-" * 80)
        
        # 測試計劃：每種語言 3 個不同的 JD，每個執行 2 次
        test_plan = {
            "en": random.sample(range(6), 3),  # 隨機選擇 3 個英文 JD
            "zh-TW": random.sample(range(6), 3)  # 隨機選擇 3 個中文 JD
        }
        
        total_tests = 0
        for lang, indices in test_plan.items():
            print(f"\n{'='*60}")
            print(f"測試語言: {lang}")
            print(f"{'='*60}")
            
            for idx in indices:
                jd = TEST_CASES[lang][idx]
                test_name = f"{lang}_jd_{idx+1}"
                print(f"\n測試案例: {test_name} (長度: {len(jd)} 字元)")
                
                # 每個 JD 執行 2 次
                for run in range(2):
                    total_tests += 1
                    result = await self.test_single_request(jd, lang, test_name, run + 1)
                    self.results.append(result)
                    
                    if result["success"]:
                        timing = result["timing"]
                        server_timing = timing.get("server_breakdown", {})
                        print(f"\n  執行 #{run+1}:")
                        print(f"    總時間: {timing['total_ms']:.1f}ms")
                        print(f"    - 準備請求: {timing['preparation_ms']:.1f}ms")
                        print(f"    - 網路請求: {timing['network_request_ms']:.1f}ms")
                        print(f"      - 網路延遲: {timing.get('network_latency_ms', 0):.1f}ms")
                        print(f"      - 伺服器處理: {server_timing.get('total_server_ms', 0):.1f}ms")
                        print(f"        - 驗證: {server_timing.get('validation_ms', 0):.1f}ms")
                        print(f"        - 語言檢測: {server_timing.get('language_detection_ms', 0):.1f}ms")
                        print(f"        - 關鍵字提取: {server_timing.get('keyword_extraction_ms', 0):.1f}ms")
                        print(f"    - 解析回應: {timing['response_parsing_ms']:.1f}ms")
                        print(f"    提取關鍵字數: {result.get('keywords_count', 0)}")
                        print(f"    快取命中: {'是' if result.get('cache_hit', False) else '否'}")
                    else:
                        print(f"\n  執行 #{run+1}: 失敗 - {result.get('error', 'Unknown error')}")
                    
                    # 避免過於頻繁的請求
                    if total_tests < 12:  # 還有更多測試要執行
                        await asyncio.sleep(2)
        
        # 生成分析報告
        self.generate_detailed_analysis()
        
    def generate_detailed_analysis(self):
        """生成詳細的效能分析報告"""
        print("\n" + "=" * 80)
        print("=== 詳細效能分析報告 ===")
        print("=" * 80)
        
        # 分離成功和失敗的結果
        successful_results = [r for r in self.results if r["success"]]
        failed_results = [r for r in self.results if not r["success"]]
        
        print(f"\n總測試次數: {len(self.results)}")
        print(f"成功: {len(successful_results)}")
        print(f"失敗: {len(failed_results)}")
        
        if not successful_results:
            print("\n沒有成功的測試結果可供分析")
            return
        
        # 按語言分組分析
        for lang in ["en", "zh-TW"]:
            lang_results = [r for r in successful_results if r["language"] == lang]
            if not lang_results:
                continue
                
            print(f"\n\n{'='*60}")
            print(f"{lang} 語言分析 ({len(lang_results)} 個成功測試)")
            print(f"{'='*60}")
            
            # 收集各階段的時間數據
            total_times = []
            network_latencies = []
            server_times = []
            validation_times = []
            detection_times = []
            extraction_times = []
            
            for r in lang_results:
                timing = r["timing"]
                server_breakdown = timing.get("server_breakdown", {})
                
                total_times.append(timing["total_ms"])
                network_latencies.append(timing.get("network_latency_ms", 0))
                server_times.append(server_breakdown.get("total_server_ms", 0))
                validation_times.append(server_breakdown.get("validation_ms", 0))
                detection_times.append(server_breakdown.get("language_detection_ms", 0))
                extraction_times.append(server_breakdown.get("keyword_extraction_ms", 0))
            
            # 計算統計數據
            print(f"\n總回應時間:")
            print(f"  平均: {statistics.mean(total_times):.1f}ms")
            print(f"  中位數: {statistics.median(total_times):.1f}ms")
            print(f"  最小/最大: {min(total_times):.1f}ms / {max(total_times):.1f}ms")
            if len(total_times) >= 5:
                print(f"  P95: {statistics.quantiles(total_times, n=20)[18]:.1f}ms")
            
            print(f"\n時間分解（平均值）:")
            print(f"  網路延遲: {statistics.mean(network_latencies):.1f}ms ({statistics.mean(network_latencies)/statistics.mean(total_times)*100:.1f}%)")
            print(f"  伺服器處理: {statistics.mean(server_times):.1f}ms ({statistics.mean(server_times)/statistics.mean(total_times)*100:.1f}%)")
            print(f"    - 請求驗證: {statistics.mean(validation_times):.1f}ms")
            print(f"    - 語言檢測: {statistics.mean(detection_times):.1f}ms")
            print(f"    - 關鍵字提取: {statistics.mean(extraction_times):.1f}ms")
            
            # 關鍵字數量統計
            keyword_counts = [r["keywords_count"] for r in lang_results]
            print(f"\n關鍵字數量:")
            print(f"  平均: {statistics.mean(keyword_counts):.1f}")
            print(f"  範圍: {min(keyword_counts)} - {max(keyword_counts)}")
            
            # 快取命中統計
            cache_hits = sum(1 for r in lang_results if r.get("cache_hit", False))
            print(f"\n快取命中率: {cache_hits}/{len(lang_results)} ({cache_hits/len(lang_results)*100:.1f}%)")
        
        # 總體分析
        all_total_times = [r["timing"]["total_ms"] for r in successful_results]
        all_extraction_times = [r["timing"]["server_breakdown"]["keyword_extraction_ms"] 
                               for r in successful_results 
                               if "server_breakdown" in r["timing"]]
        
        print(f"\n\n{'='*60}")
        print("總體效能分析")
        print(f"{'='*60}")
        
        print(f"\n整體 P95 回應時間: {statistics.quantiles(all_total_times, n=20)[18]:.1f}ms")
        print(f"目標 P95: 2500ms")
        
        p95_time = statistics.quantiles(all_total_times, n=20)[18]
        if p95_time > 2500:
            gap = p95_time - 2500
            print(f"⚠️  需要優化: 超出目標 {gap:.1f}ms ({gap/2500*100:.1f}%)")
        else:
            print("✅ 已達到效能目標!")
        
        # 瓶頸分析
        print(f"\n效能瓶頸分析:")
        avg_network = statistics.mean([r["timing"].get("network_latency_ms", 0) 
                                      for r in successful_results])
        avg_extraction = statistics.mean(all_extraction_times) if all_extraction_times else 0
        
        print(f"  網路延遲佔比: {avg_network/statistics.mean(all_total_times)*100:.1f}%")
        print(f"  LLM 處理佔比: {avg_extraction/statistics.mean(all_total_times)*100:.1f}%")
        
        # 儲存詳細結果
        self.save_detailed_results()
        
    def save_detailed_results(self):
        """儲存詳細的測試結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 格式結果
        output_file = f"temp/tests/results/keywords_detailed_perf_{timestamp}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        analysis_summary = self.calculate_summary_statistics()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_info": {
                    "test_date": datetime.now().isoformat(),
                    "api_url": self.url,
                    "total_tests": len(self.results),
                    "successful_tests": len([r for r in self.results if r["success"]])
                },
                "summary": analysis_summary,
                "detailed_results": self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n詳細結果已儲存至: {output_file}")
        
        # CSV 格式結果（便於分析）
        csv_file = f"temp/tests/results/keywords_detailed_perf_{timestamp}.csv"
        self.save_csv_results(csv_file)
        print(f"CSV 結果已儲存至: {csv_file}")
        
    def save_csv_results(self, filename):
        """儲存 CSV 格式的結果"""
        rows = []
        for r in self.results:
            if r["success"]:
                timing = r["timing"]
                server = timing.get("server_breakdown", {})
                row = {
                    "test_name": r["test_name"],
                    "test_number": r["test_number"],
                    "language": r["language"],
                    "jd_length": r["jd_length"],
                    "keywords_count": r.get("keywords_count", 0),
                    "total_ms": round(timing["total_ms"], 2),
                    "network_latency_ms": round(timing.get("network_latency_ms", 0), 2),
                    "server_total_ms": round(server.get("total_server_ms", 0), 2),
                    "validation_ms": round(server.get("validation_ms", 0), 2),
                    "detection_ms": round(server.get("language_detection_ms", 0), 2),
                    "extraction_ms": round(server.get("keyword_extraction_ms", 0), 2),
                    "cache_hit": r.get("cache_hit", False),
                    "timestamp": r["timestamp"]
                }
                rows.append(row)
        
        if rows:
            # 使用標準 csv 模組寫入
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
    
    def calculate_summary_statistics(self):
        """計算摘要統計數據"""
        successful = [r for r in self.results if r["success"]]
        if not successful:
            return {}
            
        all_total_times = [r["timing"]["total_ms"] for r in successful]
        
        summary = {
            "performance_metrics": {
                "avg_response_time_ms": statistics.mean(all_total_times),
                "median_response_time_ms": statistics.median(all_total_times),
                "p95_response_time_ms": statistics.quantiles(all_total_times, n=20)[18] if len(all_total_times) >= 5 else max(all_total_times),
                "p99_response_time_ms": statistics.quantiles(all_total_times, n=100)[98] if len(all_total_times) >= 10 else max(all_total_times),
                "min_response_time_ms": min(all_total_times),
                "max_response_time_ms": max(all_total_times)
            },
            "bottleneck_analysis": {},
            "by_language": {}
        }
        
        # 瓶頸分析
        network_times = [r["timing"].get("network_latency_ms", 0) for r in successful]
        extraction_times = [r["timing"]["server_breakdown"]["keyword_extraction_ms"] 
                           for r in successful if "server_breakdown" in r["timing"]]
        
        if network_times:
            summary["bottleneck_analysis"]["avg_network_latency_ms"] = statistics.mean(network_times)
            summary["bottleneck_analysis"]["network_latency_percentage"] = (statistics.mean(network_times) / statistics.mean(all_total_times)) * 100
            
        if extraction_times:
            summary["bottleneck_analysis"]["avg_llm_extraction_ms"] = statistics.mean(extraction_times)
            summary["bottleneck_analysis"]["llm_extraction_percentage"] = (statistics.mean(extraction_times) / statistics.mean(all_total_times)) * 100
        
        # 按語言分組統計
        for lang in ["en", "zh-TW"]:
            lang_results = [r for r in successful if r["language"] == lang]
            if lang_results:
                lang_times = [r["timing"]["total_ms"] for r in lang_results]
                summary["by_language"][lang] = {
                    "test_count": len(lang_results),
                    "avg_response_time_ms": statistics.mean(lang_times),
                    "p95_response_time_ms": statistics.quantiles(lang_times, n=20)[18] if len(lang_times) >= 5 else max(lang_times),
                    "avg_keywords_count": statistics.mean([r["keywords_count"] for r in lang_results])
                }
        
        return summary

async def main():
    """主函數"""
    if not API_KEY:
        print("警告: 未設置 AZURE_FUNCTION_KEY 環境變數")
        print("請在 .env 檔案中設置或通過環境變數提供")
        return
    
    tester = DetailedPerformanceTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())