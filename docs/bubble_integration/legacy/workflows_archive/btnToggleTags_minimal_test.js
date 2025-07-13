// === 極簡測試版本 - 只輸出訊息 ===
console.log('✅ Workflow JavaScript is running!');
console.log('Current time:', new Date().toISOString());

// 不執行任何函數調用，只是測試 JavaScript 是否能執行
try {
    console.log('Testing basic JavaScript...');
    var testVar = 'Hello from Bubble workflow';
    console.log('Test variable:', testVar);
    console.log('✅ Basic JavaScript works!');
} catch (e) {
    console.error('❌ Basic JavaScript error:', e);
}