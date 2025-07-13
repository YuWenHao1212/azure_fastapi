// 簡單的 TinyMCE 測試腳本
// 在 Bubble 的 "Run javascript" action 中使用

// 測試 1: 檢查 TinyMCE 是否存在
console.log('=== TinyMCE 測試開始 ===');
console.log('1. TinyMCE 是否存在:', typeof tinymce !== 'undefined');

if (typeof tinymce === 'undefined') {
    console.error('TinyMCE 未載入！');
    alert('錯誤: TinyMCE 未載入');
    return;
}

// 測試 2: 列出所有編輯器
console.log('2. 編輯器數量:', tinymce.editors.length);
console.log('3. 編輯器列表:');

tinymce.editors.forEach(function(editor, index) {
    console.log('  編輯器 ' + (index + 1) + ':');
    console.log('    - ID:', editor.id);
    console.log('    - 已初始化:', editor.initialized);
    console.log('    - 模式:', editor.mode.get());
    console.log('    - 可見:', !editor.isHidden());
});

// 測試 3: 檢查特定編輯器
console.log('\n4. 檢查特定編輯器:');
var editor1 = tinymce.get('TinyMCE_Editor');
var editor2 = tinymce.get('TinyMCE_Editor_initial_resume');

console.log('  TinyMCE_Editor 存在:', editor1 !== null);
console.log('  TinyMCE_Editor_initial_resume 存在:', editor2 !== null);

// 測試 4: 注入簡單樣式測試
console.log('\n5. 嘗試注入測試樣式...');

var testCSS = 'body { border: 2px solid red !important; }';
var injectedCount = 0;

tinymce.editors.forEach(function(editor) {
    if (editor.initialized) {
        try {
            editor.dom.addStyle(testCSS);
            console.log('  ✓ 成功注入到:', editor.id);
            injectedCount++;
        } catch (e) {
            console.error('  ✗ 注入失敗:', editor.id, e.message);
        }
    }
});

console.log('\n測試完成！');
console.log('成功注入樣式到 ' + injectedCount + ' 個編輯器');

// 顯示結果
var resultMessage = 'TinyMCE 測試結果:\n' +
    '- TinyMCE 已載入: ' + (typeof tinymce !== 'undefined' ? '是' : '否') + '\n' +
    '- 編輯器數量: ' + tinymce.editors.length + '\n' +
    '- 成功注入測試樣式: ' + injectedCount + ' 個\n\n' +
    '請檢查瀏覽器控制台查看詳細資訊';

alert(resultMessage);