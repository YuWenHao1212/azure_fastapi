// === Placeholder 點擊處理器 ===
// 恢復 placeholder 的點擊編輯功能

window.initializePlaceholderClickHandlers = function() {
    console.log('🔧 初始化 Placeholder 點擊處理器...');
    
    try {
        if (typeof tinymce === 'undefined' || !tinymce.activeEditor) {
            console.log('⏳ TinyMCE 尚未準備好');
            return false;
        }
        
        const editor = tinymce.activeEditor;
        const iframeDoc = editor.getDoc();
        
        // 為 placeholder 添加點擊事件處理
        function attachPlaceholderHandlers() {
            const placeholders = iframeDoc.querySelectorAll('.opt-placeholder');
            console.log(`找到 ${placeholders.length} 個 placeholder`);
            
            placeholders.forEach((placeholder, index) => {
                // 移除舊的事件監聽器（如果有）
                placeholder.removeEventListener('click', placeholder._clickHandler);
                
                // 創建新的點擊處理器
                placeholder._clickHandler = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log(`Placeholder ${index + 1} 被點擊`);
                    
                    // 獲取當前文本
                    const currentText = placeholder.textContent || placeholder.innerText;
                    console.log('當前文本:', currentText);
                    
                    // 創建輸入框
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.value = currentText;
                    input.style.cssText = `
                        background: #fff;
                        border: 2px solid #f87171;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: inherit;
                        font-family: inherit;
                        color: #991b1b;
                        width: ${Math.max(150, currentText.length * 8)}px;
                    `;
                    
                    // 替換 placeholder 為輸入框
                    const parent = placeholder.parentNode;
                    parent.insertBefore(input, placeholder);
                    placeholder.style.display = 'none';
                    
                    // 聚焦並選中文本
                    input.focus();
                    input.select();
                    
                    // 處理輸入完成
                    function finishEdit() {
                        const newValue = input.value.trim();
                        if (newValue) {
                            placeholder.textContent = newValue;
                        }
                        placeholder.style.display = '';
                        input.remove();
                        
                        // 觸發 TinyMCE 的內容更新事件
                        editor.fire('change');
                        editor.save();
                    }
                    
                    // Enter 鍵確認
                    input.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            finishEdit();
                        } else if (e.key === 'Escape') {
                            e.preventDefault();
                            placeholder.style.display = '';
                            input.remove();
                        }
                    });
                    
                    // 失去焦點時確認
                    input.addEventListener('blur', finishEdit);
                };
                
                // 添加事件監聽器
                placeholder.addEventListener('click', placeholder._clickHandler);
                
                // 確保 placeholder 可點擊
                placeholder.style.cursor = 'pointer';
                placeholder.setAttribute('contenteditable', 'false');
                placeholder.setAttribute('data-clickable', 'true');
            });
            
            console.log('✅ Placeholder 點擊處理器已附加');
        }
        
        // 立即附加處理器
        attachPlaceholderHandlers();
        
        // 監聽內容變化，重新附加處理器
        editor.on('NodeChange', function() {
            setTimeout(attachPlaceholderHandlers, 100);
        });
        
        // 監聽內容設置，重新附加處理器
        editor.on('SetContent', function() {
            setTimeout(attachPlaceholderHandlers, 100);
        });
        
        return true;
        
    } catch (error) {
        console.error('❌ 初始化 Placeholder 處理器時發生錯誤:', error);
        return false;
    }
};

// 自動初始化
setTimeout(function() {
    const checkInterval = setInterval(function() {
        if (window.initializePlaceholderClickHandlers()) {
            clearInterval(checkInterval);
        }
    }, 1000);
    
    // 30秒後停止嘗試
    setTimeout(() => clearInterval(checkInterval), 30000);
}, 2000);