// TinyMCE 除錯工具 - Bubble HTML Element 版本
// 將這段代碼放入 Bubble 的 HTML Element 中

// HTML 部分（放在 Bubble HTML Element 的內容中）
/*
<div id="tinymce-debugger" style="
    background: white;
    border: 2px solid #333;
    border-radius: 8px;
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 12px;
">
    <h3 style="margin: 0 0 10px 0; font-size: 14px;">🔍 TinyMCE 除錯工具</h3>
    
    <div style="margin-bottom: 10px;">
        <button onclick="debugTinyMCE.identify()" style="
            background: #2563EB;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            margin: 2px;
        ">識別編輯器</button>
        
        <button onclick="debugTinyMCE.checkStyles()" style="
            background: #2563EB;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            margin: 2px;
        ">檢查樣式</button>
        
        <button onclick="debugTinyMCE.inject()" style="
            background: #10B981;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            margin: 2px;
        ">注入樣式</button>
        
        <button onclick="debugTinyMCE.clear()" style="
            background: #EF4444;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            margin: 2px;
        ">清除</button>
    </div>
    
    <div id="debug-output" style="
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px;
        white-space: pre-wrap;
        word-wrap: break-word;
        min-height: 100px;
    ">等待操作...</div>
</div>

<script>
*/

// JavaScript 部分（也放在同一個 HTML Element 中）
window.debugTinyMCE = {
    output: null,
    
    init: function() {
        this.output = document.getElementById('debug-output');
        this.log('除錯工具已載入', 'info');
    },
    
    log: function(message, type = 'info') {
        if (!this.output) {
            this.output = document.getElementById('debug-output');
        }
        
        const time = new Date().toLocaleTimeString('zh-TW');
        const color = {
            'info': '#3B82F6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444'
        }[type] || '#000';
        
        const line = document.createElement('div');
        line.style.color = color;
        line.style.marginBottom = '4px';
        line.textContent = `[${time}] ${message}`;
        
        this.output.appendChild(line);
        this.output.scrollTop = this.output.scrollHeight;
        
        // 同時輸出到控制台
        console.log(`[TinyMCE Debug] ${message}`);
    },
    
    clear: function() {
        if (this.output) {
            this.output.innerHTML = '日誌已清除';
        }
    },
    
    identify: function() {
        this.log('===== 識別 TinyMCE 編輯器 =====', 'info');
        
        if (typeof tinymce === 'undefined') {
            this.log('錯誤: TinyMCE 未載入！', 'error');
            return;
        }
        
        this.log(`找到 ${tinymce.editors.length} 個編輯器`, 'success');
        
        tinymce.editors.forEach((editor, index) => {
            const isReadOnly = editor.mode.get() === 'readonly';
            this.log(`編輯器 ${index + 1}:`, 'info');
            this.log(`  ID: ${editor.id}`, 'info');
            this.log(`  狀態: ${editor.initialized ? '已初始化' : '未初始化'}`, 'info');
            this.log(`  模式: ${editor.mode.get()} ${isReadOnly ? '(唯讀)' : '(可編輯)'}`, 'info');
            
            // 特別標記
            if (editor.id === 'TinyMCE_Editor') {
                this.log('  → 這是原始編輯器', 'success');
            } else if (editor.id === 'TinyMCE_Editor_initial_resume') {
                this.log('  → 這是初始履歷編輯器', 'success');
            }
        });
        
        // 檢查特定編輯器
        this.log('\n檢查特定編輯器:', 'info');
        const editor1 = tinymce.get('TinyMCE_Editor');
        const editor2 = tinymce.get('TinyMCE_Editor_initial_resume');
        
        this.log(`TinyMCE_Editor: ${editor1 ? '✓ 存在' : '✗ 不存在'}`, 
                 editor1 ? 'success' : 'warning');
        this.log(`TinyMCE_Editor_initial_resume: ${editor2 ? '✓ 存在' : '✗ 不存在'}`, 
                 editor2 ? 'success' : 'warning');
    },
    
    checkStyles: function() {
        this.log('===== 檢查樣式狀態 =====', 'info');
        
        if (!tinymce || !tinymce.editors) {
            this.log('錯誤: TinyMCE 未載入', 'error');
            return;
        }
        
        const targetClasses = [
            'opt-keyword',
            'opt-keyword-existing',
            'opt-modified',
            'opt-new',
            'opt-placeholder'
        ];
        
        tinymce.editors.forEach((editor, index) => {
            this.log(`\n檢查編輯器: ${editor.id}`, 'info');
            
            if (!editor.getBody()) {
                this.log('  主體未載入', 'warning');
                return;
            }
            
            // 檢查注入標記
            const hasStyles = editor.dom.hasClass(editor.getBody(), 'styles-injected');
            this.log(`  樣式注入: ${hasStyles ? '✓ 已注入' : '✗ 未注入'}`, 
                     hasStyles ? 'success' : 'warning');
            
            // 檢查樣式類別
            targetClasses.forEach(className => {
                const count = editor.dom.select('.' + className).length;
                if (count > 0) {
                    this.log(`  ${className}: 找到 ${count} 個`, 'info');
                }
            });
            
            // 檢查 style 標籤
            const styleCount = editor.dom.select('style').length;
            this.log(`  <style> 標籤: ${styleCount} 個`, 'info');
        });
    },
    
    inject: function() {
        this.log('===== 注入樣式到所有編輯器 =====', 'info');
        
        if (!tinymce || !tinymce.editors) {
            this.log('錯誤: TinyMCE 未載入', 'error');
            return;
        }
        
        const css = `
            span.opt-keyword-existing {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                padding: 3px 8px !important;
                border-radius: 4px !important;
                font-weight: 600 !important;
            }
            
            span.opt-keyword {
                color: #6366F1 !important;
                border: 1px solid #C7D2FE !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
            }
            
            span.opt-modified {
                background-color: #FFF3CD !important;
                padding: 2px 6px !important;
                border-radius: 3px !important;
            }
            
            .opt-new {
                border-left: 4px solid #10B981 !important;
                padding-left: 16px !important;
                background-color: rgba(209, 250, 229, 0.1) !important;
            }
            
            span.opt-placeholder {
                background-color: #FEE2E2 !important;
                color: #991B1B !important;
                border: 1px dashed #F87171 !important;
                padding: 2px 8px !important;
                font-style: italic !important;
            }
        `;
        
        let count = 0;
        tinymce.editors.forEach(editor => {
            try {
                if (editor.initialized) {
                    editor.dom.addStyle(css);
                    editor.dom.addClass(editor.getBody(), 'styles-injected');
                    count++;
                    this.log(`✓ 成功注入到: ${editor.id}`, 'success');
                }
            } catch (e) {
                this.log(`✗ 注入失敗 (${editor.id}): ${e.message}`, 'error');
            }
        });
        
        this.log(`\n完成: ${count}/${tinymce.editors.length} 個成功`, 'info');
    }
};

// 初始化
setTimeout(function() {
    window.debugTinyMCE.init();
}, 1000);

/*
</script>
*/