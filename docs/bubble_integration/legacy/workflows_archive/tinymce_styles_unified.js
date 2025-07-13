// TinyMCE 樣式注入腳本 - 統一版本
// 支援 v1.0.0 (opt-strength) 和 v1.1.0 (opt-modified)
// 用於 Bubble.io "page is loaded" workflow
// 更新日期: 2025-01-12

function injectTinyMCEStyles() {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor && !tinymce.activeEditor.isHidden()) {
        var editor = tinymce.activeEditor;
        
        // 定義要注入的完整 CSS
        var fullCSS = `
            /* ===== 三層級標記系統 ===== */
            
            /* 1. Section Level - opt-new - 新增區塊（綠色左邊框） */
            .opt-new {
                border-left: 4px solid #10B981 !important;
                padding-left: 16px !important;
                background-color: rgba(209, 250, 229, 0.1) !important;
                margin-left: -20px !important;
                padding-right: 16px !important;
            }
            
            h2.opt-new, h3.opt-new, h4.opt-new {
                background-color: transparent !important;
            }
            
            /* 2. Content Level - opt-modified - 修改內容（淺黃色背景） */
            span.opt-modified {
                background-color: #FFF3CD !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                display: inline !important;
                line-height: inherit !important;
            }
            
            /* v1.0.0 相容性 - opt-strength (同樣使用黃色，但加底線) */
            span.opt-strength {
                background-color: #FFF3CD !important;
                border-bottom: 2px solid #FFC107 !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                display: inline !important;
                font-weight: 600 !important;
            }
            
            /* 防止錯誤使用在區塊元素上 */
            li.opt-modified, p.opt-modified,
            h1.opt-modified, h2.opt-modified, h3.opt-modified,
            h4.opt-modified, h5.opt-modified,
            li.opt-strength, p.opt-strength,
            h1.opt-strength, h2.opt-strength, h3.opt-strength,
            h4.opt-strength, h5.opt-strength {
                background-color: transparent !important;
                background: none !important;
                color: inherit !important;
                padding: 0 !important;
                border-radius: 0 !important;
                border-bottom: none !important;
            }
            
            /* 3. Data Level - opt-placeholder - 數據佔位符（紅色虛線框） */
            span.opt-placeholder {
                background-color: #FEE2E2 !important;
                color: #991B1B !important;
                border: 1px dashed #F87171 !important;
                padding: 2px 8px !important;
                border-radius: 4px !important;
                font-style: italic !important;
                font-weight: 500 !important;
                cursor: pointer !important;
                margin: 0 2px !important;
            }
            
            span.opt-placeholder:hover {
                background-color: #FECACA !important;
                border-color: #EF4444 !important;
            }
            
            /* ===== 關鍵字標記系統 ===== */
            
            /* 4. 新增關鍵字 - opt-keyword（紫色邊框，低調） */
            span.opt-keyword {
                background-color: transparent !important;
                color: #6366F1 !important;
                border: 1px solid #C7D2FE !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
                font-weight: 500 !important;
                margin: 0 2px !important;
            }
            
            /* 5. 原有關鍵字 - opt-keyword-existing（深藍色背景，醒目） */
            span.opt-keyword-existing {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                padding: 3px 8px !important;
                border-radius: 4px !important;
                font-weight: 600 !important;
                margin: 0 2px !important;
                box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3) !important;
            }
            
            /* ===== 額外標記（相容性） ===== */
            
            /* 6. 已編輯內容 - opt-improvement（綠色底線） */
            span.opt-improvement {
                border-bottom: 2px solid #10B981 !important;
                color: #065F46 !important;
                padding-bottom: 1px !important;
                font-weight: 500 !important;
            }
            
            /* ===== 防止錯誤應用 ===== */
            
            /* 防止關鍵字標記錯誤應用在區塊元素上 */
            li.opt-keyword, p.opt-keyword,
            h1.opt-keyword, h2.opt-keyword, h3.opt-keyword,
            h4.opt-keyword, h5.opt-keyword,
            li.opt-keyword-existing, p.opt-keyword-existing,
            h1.opt-keyword-existing, h2.opt-keyword-existing,
            h3.opt-keyword-existing, h4.opt-keyword-existing,
            h5.opt-keyword-existing,
            li.opt-placeholder, p.opt-placeholder,
            h1.opt-placeholder, h2.opt-placeholder, h3.opt-placeholder,
            h4.opt-placeholder, h5.opt-placeholder {
                background-color: transparent !important;
                background: none !important;
                color: inherit !important;
                padding: 0 !important;
                border: none !important;
                border-radius: 0 !important;
                box-shadow: none !important;
            }
            
            /* ===== 視覺改善 ===== */
            
            /* 確保標記不會破壞行高 */
            span.opt-modified,
            span.opt-strength,
            span.opt-keyword,
            span.opt-keyword-existing,
            span.opt-placeholder,
            span.opt-improvement {
                display: inline !important;
                line-height: inherit !important;
                vertical-align: baseline !important;
            }
            
            /* 列表項目中的標記調整 */
            li span.opt-modified,
            li span.opt-strength,
            li span.opt-keyword,
            li span.opt-keyword-existing,
            li span.opt-placeholder {
                margin: 0 1px !important;
            }
        `;
        
        // 注入樣式
        editor.dom.addStyle(fullCSS);
        console.log('✅ TinyMCE 統一樣式已成功注入');
        console.log('📋 支援標記: opt-new, opt-modified, opt-strength(v1.0.0相容), opt-placeholder, opt-keyword, opt-keyword-existing, opt-improvement');
        
        // 檢測內容版本
        var content = editor.getContent();
        if (content.includes('opt-strength')) {
            console.log('⚠️ 檢測到 v1.0.0 標記 (opt-strength)');
            
            // 詢問是否要轉換
            if (window.confirm('檢測到舊版標記 (opt-strength)，是否要轉換為新版 (opt-modified)？')) {
                var newContent = content.replace(/class="opt-strength"/g, 'class="opt-modified"');
                editor.setContent(newContent);
                console.log('✅ 已轉換 opt-strength → opt-modified');
            }
        }
        
        // 返回 true 表示成功
        return true;
    } else {
        // 如果 TinyMCE 還沒準備好，1秒後再試
        console.log('⏳ TinyMCE 尚未準備好，1秒後重試...');
        setTimeout(injectTinyMCEStyles, 1000);
        return false;
    }
}

// 輔助函數：手動轉換標記版本
function convertToV2Markers() {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
        var editor = tinymce.activeEditor;
        var content = editor.getContent();
        
        // 統計轉換
        var strengthCount = (content.match(/opt-strength/g) || []).length;
        
        if (strengthCount > 0) {
            // 執行轉換
            var newContent = content.replace(/class="opt-strength"/g, 'class="opt-modified"');
            editor.setContent(newContent);
            
            console.log(`✅ 成功轉換 ${strengthCount} 個 opt-strength 標記為 opt-modified`);
            alert(`已轉換 ${strengthCount} 個標記為新版格式`);
        } else {
            console.log('ℹ️ 沒有找到需要轉換的 opt-strength 標記');
            alert('沒有找到需要轉換的舊版標記');
        }
    }
}

// 輔助函數：統計標記使用情況
function getMarkerStatistics() {
    if (typeof tinymce !== 'undefined' && tinymce.activeEditor) {
        var editor = tinymce.activeEditor;
        var content = editor.getContent();
        
        var stats = {
            'opt-new': (content.match(/opt-new/g) || []).length,
            'opt-modified': (content.match(/opt-modified/g) || []).length,
            'opt-strength': (content.match(/opt-strength/g) || []).length,
            'opt-placeholder': (content.match(/opt-placeholder/g) || []).length,
            'opt-keyword': (content.match(/class="opt-keyword"/g) || []).length,
            'opt-keyword-existing': (content.match(/opt-keyword-existing/g) || []).length,
            'opt-improvement': (content.match(/opt-improvement/g) || []).length
        };
        
        console.log('📊 標記統計:', stats);
        
        // 顯示版本資訊
        if (stats['opt-strength'] > 0 && stats['opt-modified'] === 0) {
            console.log('📌 版本: v1.0.0 (使用 opt-strength)');
        } else if (stats['opt-modified'] > 0 && stats['opt-strength'] === 0) {
            console.log('📌 版本: v1.1.0 (使用 opt-modified)');
        } else if (stats['opt-strength'] > 0 && stats['opt-modified'] > 0) {
            console.log('⚠️ 版本: 混合 (同時包含 opt-strength 和 opt-modified)');
        }
        
        return stats;
    }
}

// 開始注入流程
injectTinyMCEStyles();

// 將輔助函數暴露到全域
window.convertToV2Markers = convertToV2Markers;
window.getMarkerStatistics = getMarkerStatistics;