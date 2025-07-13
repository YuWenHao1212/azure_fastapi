/**
 * Bubble.io Page Loaded JavaScript
 * 用於初始化 TinyMCE 樣式和處理 Resume Tailoring API 回應
 */

(function() {
    'use strict';
    
    console.log('🚀 AIResumeAdvisor: Initializing page loaded script');
    
    // === 1. TinyMCE 增強標記樣式 ===
    function initializeEnhancedStyles() {
        console.log('📝 Initializing TinyMCE enhanced styles');
        
        // 檢查是否已經添加過樣式
        if (document.getElementById('resume-enhanced-styles')) {
            console.log('⚠️ Enhanced styles already loaded');
            return;
        }
        
        const styleSheet = document.createElement('style');
        styleSheet.id = 'resume-enhanced-styles';
        styleSheet.innerHTML = `
            /* === 增強標記樣式 === */
            
            /* 新增內容 - 綠色邊框 */
            .opt-new {
                background-color: #e8f5e8 !important;
                border-left: 4px solid #4CAF50 !important;
                padding: 8px !important;
                margin: 4px 0 !important;
                border-radius: 4px;
                position: relative;
            }
            
            .opt-new::before {
                content: "NEW";
                position: absolute;
                top: -8px;
                right: 8px;
                background: #4CAF50;
                color: white;
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 3px;
                font-weight: bold;
            }
            
            /* 修改內容 - 黃色邊框 */
            .opt-modified {
                background-color: #fff3cd !important;
                border-left: 4px solid #ffc107 !important;
                padding: 8px !important;
                margin: 4px 0 !important;
                border-radius: 4px;
                position: relative;
            }
            
            .opt-modified::before {
                content: "ENHANCED";
                position: absolute;
                top: -8px;
                right: 8px;
                background: #ffc107;
                color: #333;
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 3px;
                font-weight: bold;
            }
            
            /* 數據佔位符 - 紅色背景 */
            .opt-placeholder {
                background-color: #f8d7da !important;
                color: #721c24 !important;
                border: 1px solid #dc3545 !important;
                padding: 2px 6px !important;
                font-weight: bold !important;
                border-radius: 4px !important;
                font-family: monospace !important;
                font-size: 0.9em !important;
                cursor: help;
            }
            
            .opt-placeholder:hover {
                background-color: #dc3545 !important;
                color: white !important;
                transform: scale(1.05);
                transition: all 0.2s ease;
            }
            
            /* 新關鍵字 - 藍色背景 */
            .opt-keyword {
                background-color: #d1ecf1 !important;
                color: #0c5460 !important;
                font-weight: bold !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
                border: 1px solid #bee5eb !important;
                font-size: 0.95em !important;
                cursor: pointer;
            }
            
            .opt-keyword:hover {
                background-color: #0c5460 !important;
                color: white !important;
                transform: scale(1.05);
                transition: all 0.2s ease;
            }
            
            /* 原有關鍵字 - 綠色背景 */
            .opt-keyword-existing {
                background-color: #d4edda !important;
                color: #155724 !important;
                font-weight: bold !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
                border: 1px solid #c3e6cb !important;
                font-size: 0.95em !important;
                cursor: pointer;
            }
            
            .opt-keyword-existing:hover {
                background-color: #155724 !important;
                color: white !important;
                transform: scale(1.05);
                transition: all 0.2s ease;
            }
            
            /* 強化項目 - 橙色邊框 (v1.0.0 相容性) */
            .opt-strength {
                background-color: #fff3cd !important;
                border-bottom: 2px solid #fd7e14 !important;
                font-weight: 600 !important;
                padding: 1px 3px !important;
            }
            
            /* 注意：opt-strength 已在 v1.1.0 中被 opt-modified 取代 */
            
            /* === 響應式設計 === */
            @media (max-width: 768px) {
                .opt-new, .opt-modified {
                    padding: 6px !important;
                    margin: 2px 0 !important;
                }
                
                .opt-new::before, .opt-modified::before {
                    font-size: 8px !important;
                    padding: 1px 4px !important;
                }
                
                .opt-placeholder, .opt-keyword, .opt-keyword-existing {
                    padding: 1px 4px !important;
                    font-size: 0.85em !important;
                }
            }
            
            /* === 印刷友好樣式 === */
            @media print {
                .opt-new, .opt-modified {
                    border: 2px solid #333 !important;
                    background: transparent !important;
                }
                
                .opt-new::before, .opt-modified::before {
                    display: none !important;
                }
                
                .opt-placeholder {
                    background: #f0f0f0 !important;
                    color: #333 !important;
                    border: 1px solid #333 !important;
                }
                
                .opt-keyword, .opt-keyword-existing {
                    background: transparent !important;
                    color: #333 !important;
                    border: 1px solid #333 !important;
                }
            }
            
            /* === 動畫效果 === */
            .opt-new, .opt-modified, .opt-placeholder, .opt-keyword, .opt-keyword-existing {
                transition: all 0.3s ease !important;
            }
            
            /* === 工具提示樣式 === */
            .tooltip {
                position: relative;
                cursor: help;
            }
            
            .tooltip::after {
                content: attr(data-tooltip);
                position: absolute;
                bottom: 125%;
                left: 50%;
                transform: translateX(-50%);
                background: #333;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.3s;
                z-index: 1000;
            }
            
            .tooltip:hover::after {
                opacity: 1;
                visibility: visible;
            }
        `;
        
        document.head.appendChild(styleSheet);
        console.log('✅ Enhanced styles loaded successfully');
    }
    
    // === 2. API 回應處理函數 ===
    function initializeAPIResponseHandlers() {
        console.log('🔧 Initializing API response handlers');
        
        // 全域函數：處理 Resume Tailoring API 回應
        window.handleResumeTailoringResponse = function(apiResponse) {
            console.log('📊 Processing resume tailoring response', apiResponse);
            
            try {
                if (!apiResponse || !apiResponse.success) {
                    console.error('❌ Invalid API response:', apiResponse);
                    return false;
                }
                
                const data = apiResponse.data;
                
                // 處理優化後的履歷 HTML (v2.1: optimized_resume → resume)
                if (data.resume || data.optimized_resume) {
                    const resumeHTML = data.resume || data.optimized_resume;  // Support both v2.0 and v2.1
                    const resumeContainer = document.querySelector('#optimized-resume-container');
                    if (resumeContainer) {
                        resumeContainer.innerHTML = resumeHTML;
                        console.log('✅ Optimized resume HTML updated');
                        
                        // 添加工具提示
                        addTooltips(resumeContainer);
                    }
                }
                
                // 處理統計數據 (v2.1: split into similarity and coverage)
                if (data.similarity) {
                    updateSimilarityDisplay(data.similarity);
                } else if (data.index_calculation) {
                    // v2.0 compatibility
                    updateIndexCalculationDisplay(data.index_calculation);
                }
                
                if (data.coverage) {
                    updateCoverageDisplay(data.coverage);
                }
                
                if (data.markers || data.visual_markers) {
                    updateVisualMarkersDisplay(data.markers || data.visual_markers);
                }
                
                // 觸發自定義事件
                const event = new CustomEvent('resumeTailoringComplete', {
                    detail: {
                        response: apiResponse,
                        stats: data.index_calculation,
                        markers: data.visual_markers
                    }
                });
                document.dispatchEvent(event);
                
                console.log('🎉 Resume tailoring response processed successfully');
                return true;
                
            } catch (error) {
                console.error('❌ Error processing API response:', error);
                return false;
            }
        };
        
        // 全域函數：添加工具提示
        window.addTooltips = function(container) {
            // 為佔位符添加工具提示
            const placeholders = container.querySelectorAll('.opt-placeholder');
            placeholders.forEach(el => {
                el.setAttribute('data-tooltip', '請填入具體數據');
                el.classList.add('tooltip');
            });
            
            // 為新關鍵字添加工具提示
            const newKeywords = container.querySelectorAll('.opt-keyword');
            newKeywords.forEach(el => {
                el.setAttribute('data-tooltip', '新增的關鍵字');
                el.classList.add('tooltip');
            });
            
            // 為原有關鍵字添加工具提示
            const existingKeywords = container.querySelectorAll('.opt-keyword-existing');
            existingKeywords.forEach(el => {
                el.setAttribute('data-tooltip', '原有的關鍵字');
                el.classList.add('tooltip');
            });
        };
        
        // 更新 Index Calculation 顯示
        window.updateIndexCalculationDisplay = function(indexCalc) {
            const elements = {
                'original-similarity': indexCalc.original_similarity,
                'optimized-similarity': indexCalc.optimized_similarity,
                'similarity-improvement': indexCalc.similarity_improvement,
                'original-keyword-coverage': indexCalc.original_keyword_coverage,
                'optimized-keyword-coverage': indexCalc.optimized_keyword_coverage,
                'keyword-coverage-improvement': indexCalc.keyword_coverage_improvement
            };
            
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = `${value}%`;
                    element.style.fontWeight = 'bold';
                    element.style.color = value > 0 ? '#28a745' : '#6c757d';
                }
            });
            
            // 新增關鍵字列表
            const newKeywordsList = document.getElementById('new-keywords-list');
            if (newKeywordsList && indexCalc.new_keywords_added) {
                newKeywordsList.innerHTML = indexCalc.new_keywords_added
                    .map(keyword => `<span class="badge badge-primary mr-1">${keyword}</span>`)
                    .join('');
            }
        };
        
        // 更新 Visual Markers 顯示 (supports both v2.0 and v2.1)
        window.updateVisualMarkersDisplay = function(markers) {
            // v2.1 field names
            const v21Stats = {
                'keyword-count': markers.keyword_new,
                'keyword-existing-count': markers.keyword_existing,
                'placeholder-count': markers.placeholder,
                'new-content-count': markers.new_section,
                'modified-content-count': markers.modified
            };
            
            // v2.0 field names (fallback)
            const v20Stats = {
                'keyword-count': markers.keyword_count,
                'keyword-existing-count': markers.keyword_existing_count,
                'placeholder-count': markers.placeholder_count,
                'new-content-count': markers.new_content_count,
                'modified-content-count': markers.modified_content_count
            };
            
            // Use v2.1 if available, otherwise v2.0
            const stats = markers.keyword_new !== undefined ? v21Stats : v20Stats;
            
            Object.entries(stats).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value || 0;
                    element.style.fontWeight = 'bold';
                }
            });
        };
        
        // 更新 Keywords Analysis 顯示
        window.updateKeywordsAnalysisDisplay = function(analysis) {
            // 原有關鍵字
            const originalKeywords = document.getElementById('original-keywords-list');
            if (originalKeywords && analysis.original_keywords) {
                originalKeywords.innerHTML = analysis.original_keywords
                    .map(keyword => `<span class="badge badge-success mr-1">${keyword}</span>`)
                    .join('');
            }
            
            // 新增關鍵字
            const newKeywords = document.getElementById('added-keywords-list');
            if (newKeywords && analysis.new_keywords) {
                newKeywords.innerHTML = analysis.new_keywords
                    .map(keyword => `<span class="badge badge-info mr-1">${keyword}</span>`)
                    .join('');
            }
            
            // 總關鍵字數
            const totalKeywords = document.getElementById('total-keywords-count');
            if (totalKeywords) {
                totalKeywords.textContent = analysis.total_keywords;
            }
        };
        
        // 更新 Similarity 顯示 (v2.1)
        window.updateSimilarityDisplay = function(similarity) {
            const elements = {
                'original-similarity': similarity.before,
                'optimized-similarity': similarity.after,
                'similarity-improvement': similarity.improvement
            };
            
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = `${value}%`;
                    element.style.fontWeight = 'bold';
                    element.style.color = value > 0 ? '#28a745' : '#6c757d';
                }
            });
        };
        
        // 更新 Coverage 顯示 (v2.1)
        window.updateCoverageDisplay = function(coverage) {
            // Before coverage
            const beforeElement = document.getElementById('original-keyword-coverage');
            if (beforeElement) {
                beforeElement.textContent = `${coverage.before.percentage}%`;
                beforeElement.style.fontWeight = 'bold';
            }
            
            // After coverage
            const afterElement = document.getElementById('optimized-keyword-coverage');
            if (afterElement) {
                afterElement.textContent = `${coverage.after.percentage}%`;
                afterElement.style.fontWeight = 'bold';
            }
            
            // Improvement
            const improvementElement = document.getElementById('keyword-coverage-improvement');
            if (improvementElement) {
                improvementElement.textContent = `${coverage.improvement}%`;
                improvementElement.style.fontWeight = 'bold';
                improvementElement.style.color = coverage.improvement > 0 ? '#28a745' : '#6c757d';
            }
            
            // Newly added keywords
            const newKeywordsList = document.getElementById('new-keywords-list');
            if (newKeywordsList && coverage.newly_added) {
                newKeywordsList.innerHTML = coverage.newly_added
                    .map(keyword => `<span class="badge badge-primary mr-1">${keyword}</span>`)
                    .join('');
            }
            
            // Missed keywords (v2.1 new feature)
            const missedKeywordsList = document.getElementById('missed-keywords-list');
            if (missedKeywordsList && coverage.after.missed) {
                missedKeywordsList.innerHTML = coverage.after.missed
                    .map(keyword => `<span class="badge badge-warning mr-1">${keyword}</span>`)
                    .join('');
            }
        };
        
        console.log('✅ API response handlers initialized (v2.0 and v2.1 compatible)');
    }
    
    // === 3. TinyMCE 整合 ===
    function initializeTinyMCEIntegration() {
        console.log('📝 Initializing TinyMCE integration');
        
        // 檢查 TinyMCE 是否可用
        if (typeof tinymce !== 'undefined') {
            // 添加自定義 CSS 到 TinyMCE
            tinymce.on('AddEditor', function(e) {
                const editor = e.editor;
                editor.on('init', function() {
                    // 將增強樣式添加到 TinyMCE iframe
                    const doc = editor.getDoc();
                    const styleSheet = doc.createElement('style');
                    styleSheet.innerHTML = document.getElementById('resume-enhanced-styles').innerHTML;
                    doc.head.appendChild(styleSheet);
                    
                    console.log('✅ Enhanced styles added to TinyMCE editor');
                });
            });
        }
    }
    
    // === 4. 錯誤處理 ===
    function initializeErrorHandling() {
        console.log('⚠️ Initializing error handling');
        
        // 全域錯誤處理函數
        window.handleAPIError = function(error, context = 'API Call') {
            console.error(`❌ ${context} Error:`, error);
            
            // 顯示用戶友好的錯誤訊息
            const errorContainer = document.getElementById('error-message-container');
            if (errorContainer) {
                let errorMessage = 'An unexpected error occurred. Please try again.';
                
                if (error.status === 401) {
                    errorMessage = 'Authentication failed. Please check your API key.';
                } else if (error.status === 422) {
                    errorMessage = 'Invalid input data. Please check your job description and resume.';
                } else if (error.status === 500) {
                    errorMessage = 'Server error. Please try again later.';
                } else if (error.name === 'TimeoutError') {
                    errorMessage = 'Request timeout. The API is processing, please try again.';
                }
                
                errorContainer.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <strong>Error:</strong> ${errorMessage}
                    </div>
                `;
                
                // 自動隱藏錯誤訊息
                setTimeout(() => {
                    errorContainer.innerHTML = '';
                }, 10000);
            }
        };
        
        console.log('✅ Error handling initialized');
    }
    
    // === 5. 實用工具函數 ===
    function initializeUtilityFunctions() {
        console.log('🛠️ Initializing utility functions');
        
        // 計算標記統計
        window.calculateMarkerStats = function(htmlContent) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlContent;
            
            return {
                newContent: tempDiv.querySelectorAll('.opt-new').length,
                modifiedContent: tempDiv.querySelectorAll('.opt-modified').length,
                placeholders: tempDiv.querySelectorAll('.opt-placeholder').length,
                newKeywords: tempDiv.querySelectorAll('.opt-keyword').length,
                existingKeywords: tempDiv.querySelectorAll('.opt-keyword-existing').length,
                // v1.0.0 相容性
                strengthMarkers: tempDiv.querySelectorAll('.opt-strength').length
            };
        };
        
        // 標記版本轉換函數 (v1.0.0 → v1.1.0)
        window.convertMarkersToV2 = function(htmlContent) {
            console.log('🔄 Converting markers from v1.0.0 to v1.1.0 format...');
            
            // 將 opt-strength 轉換為 opt-modified
            let convertedHTML = htmlContent.replace(/class="opt-strength"/g, 'class="opt-modified"');
            
            // 統計轉換數量
            const strengthCount = (htmlContent.match(/opt-strength/g) || []).length;
            if (strengthCount > 0) {
                console.log(`✅ Converted ${strengthCount} opt-strength markers to opt-modified`);
            }
            
            return convertedHTML;
        };
        
        // 檢查標記版本
        window.detectMarkerVersion = function(htmlContent) {
            const hasOptStrength = htmlContent.includes('opt-strength');
            const hasOptModified = htmlContent.includes('opt-modified');
            
            if (hasOptStrength && !hasOptModified) {
                return 'v1.0.0';
            } else if (hasOptModified && !hasOptStrength) {
                return 'v1.1.0';
            } else if (hasOptStrength && hasOptModified) {
                return 'mixed';
            } else {
                return 'unknown';
            }
        };
        
        // 清理 HTML（移除所有標記）
        window.cleanResumeHTML = function(htmlContent) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlContent;
            
            // 移除所有標記類別
            const markers = tempDiv.querySelectorAll('.opt-new, .opt-modified, .opt-placeholder, .opt-keyword, .opt-keyword-existing, .opt-strength');
            markers.forEach(el => {
                el.className = '';
            });
            
            return tempDiv.innerHTML;
        };
        
        // 匯出為 PDF 友好格式
        window.getPrintFriendlyHTML = function(htmlContent) {
            return `
                <style>
                    @media print {
                        .opt-new, .opt-modified { border: 2px solid #333 !important; background: transparent !important; }
                        .opt-placeholder { background: #f0f0f0 !important; color: #333 !important; }
                        .opt-keyword, .opt-keyword-existing { background: transparent !important; color: #333 !important; border: 1px solid #333 !important; }
                    }
                </style>
                ${htmlContent}
            `;
        };
        
        console.log('✅ Utility functions initialized');
    }
    
    // === 主要初始化 ===
    function initialize() {
        try {
            initializeEnhancedStyles();
            initializeAPIResponseHandlers();
            initializeTinyMCEIntegration();
            initializeErrorHandling();
            initializeUtilityFunctions();
            
            console.log('🎉 AIResumeAdvisor page loaded script initialized successfully');
            
            // 觸發初始化完成事件
            const event = new CustomEvent('aiResumeAdvisorReady', {
                detail: { timestamp: new Date().toISOString() }
            });
            document.dispatchEvent(event);
            
        } catch (error) {
            console.error('❌ Failed to initialize AIResumeAdvisor:', error);
        }
    }
    
    // 確保 DOM 已載入
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
})();