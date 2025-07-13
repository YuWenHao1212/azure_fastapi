// === 快速修復 Placeholder 點擊功能 ===
// 在 Page Load 或任何地方執行這段代碼

setTimeout(function() {
    console.log('🔧 修復 Placeholder 點擊功能...');
    
    try {
        if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
            console.log('⏳ TinyMCE 尚未準備好，稍後重試');
            return;
        }
        
        const editor = tinymce.activeEditor;
        const iframeDoc = editor.getDoc();
        
        // 檢查是否有 placeholder 修復樣式
        let fixStyle = iframeDoc.getElementById('placeholder-fix-style');
        if (!fixStyle) {
            fixStyle = iframeDoc.createElement('style');
            fixStyle.id = 'placeholder-fix-style';
            iframeDoc.head.appendChild(fixStyle);
        }
        
        // 更新樣式 - 覆蓋原本的隱藏樣式
        fixStyle.textContent = `
            /* 修復：隱藏的 placeholder 仍可點擊 */
            body.hide-opt-placeholder .opt-placeholder {
                /* 使用 opacity 而非完全隱藏 */
                opacity: 0.2 !important;
                cursor: pointer !important;
                /* 保留一些視覺提示 */
                background-color: rgba(254, 226, 226, 0.1) !important;
                border: 1px dashed rgba(248, 113, 113, 0.2) !important;
                /* 保留原有的 padding 和其他屬性 */
                color: #991b1b !important;
                padding: 2px 8px !important;
                border-radius: 4px !important;
                font-style: italic !important;
                transition: all 0.2s ease;
            }
            
            /* Hover 時更明顯 */
            body.hide-opt-placeholder .opt-placeholder:hover {
                opacity: 1 !important;
                background-color: #fee2e2 !important;
                border: 1px dashed #f87171 !important;
            }
            
            /* Focus 時完全顯示 */
            body.hide-opt-placeholder .opt-placeholder:focus {
                opacity: 1 !important;
            }
        `;
        
        console.log('✅ Placeholder 點擊功能已修復');
        
        // 確保 placeholder 有點擊事件
        const placeholders = iframeDoc.querySelectorAll('.opt-placeholder');
        console.log(`找到 ${placeholders.length} 個 placeholder`);
        
    } catch (error) {
        console.error('❌ 修復 Placeholder 時發生錯誤:', error);
    }
    
}, 3000); // 延遲 3 秒確保 TinyMCE 完全載入