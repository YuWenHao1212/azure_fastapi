#!/bin/bash

# 本地測試 format-resume API

echo "測試本地 format-resume API"
echo "=========================="

# 測試 1: 基本測試
echo -e "\n測試 1: 基本格式化測試"
curl -X POST "http://localhost:8000/api/v1/format-resume" \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_text": "【Title】:John Doe\n【Title】:Software Engineer\n【NarrativeText】:Experienced developer with 5 years building web applications\n\n【Title】:Education\n【NarrativeText】:Stanford University • MS Computer Science • 2018\n\n【Title】:Experience\n【Title】:Google Inc.\n【NarrativeText】:Senior Software Engineer • 2020 - Present\n【ListItem】:Led development team\n【ListItem】:Improved performance by 40%"
  }' | jq .

# 測試 2: 更詳細的履歷
echo -e "\n\n測試 2: 詳細履歷測試"
curl -X POST "http://localhost:8000/api/v1/format-resume" \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_text": "【Title】:Jane Smith\n【Title】:Senior Product Manager\n【NarrativeText】:Product leader with 8+ years experience driving innovation\n\n【Title】:Contact Information\n【NarrativeText】:Email: jane.smith@example.com\n【NarrativeText】:Phone: (415) 555-0123\n【NarrativeText】:Location: San Francisco, CA\n\n【Title】:Professional Summary\n【NarrativeText】:Accomplished product manager with proven track record of launching successful products that have generated over $50M in revenue. Expert in agile methodologies, user research, and data-driven decision making.\n\n【Title】:Work Experience\n【Title】:Uber Technologies Inc.\n【NarrativeText】:Senior Product Manager • San Francisco, CA • Jan 2020 - Present\n【ListItem】:Led cross-functional team of 15 engineers and designers to launch new rider features\n【ListItem】:Increased user engagement by 35% through data-driven product improvements\n【ListItem】:Managed product roadmap for $100M business unit\n\n【Title】:Facebook Inc.\n【NarrativeText】:Product Manager • Menlo Park, CA • Jun 2017 - Dec 2019\n【ListItem】:Launched 3 major features for Facebook Marketplace\n【ListItem】:Conducted 50+ user interviews to identify pain points\n【ListItem】:Improved seller onboarding conversion by 40%\n\n【Title】:Education\n【Title】:Harvard Business School\n【NarrativeText】:MBA • 2015 - 2017\n【ListItem】:Baker Scholar (top 5% of class)\n【ListItem】:Product Management Club President\n\n【Title】:Massachusetts Institute of Technology\n【NarrativeText】:BS Computer Science • 2008 - 2012\n【ListItem】:Summa Cum Laude, GPA: 3.9/4.0\n\n【Title】:Skills\n【ListItem】:Product Strategy: Roadmap Planning, Market Analysis, Competitive Intelligence\n【ListItem】:Technical: SQL, Python, Tableau, JIRA, Figma\n【ListItem】:Leadership: Team Building, Stakeholder Management, Executive Presentations"
  }' | jq .

echo -e "\n\n測試完成！"