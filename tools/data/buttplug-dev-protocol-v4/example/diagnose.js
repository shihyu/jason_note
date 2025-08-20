// 診斷腳本 - 檢查原始頁面的問題
console.log("=== 診斷開始 ===");

// 檢查 DOM 元素
setTimeout(() => {
    console.log("檢查 DOM 元素:");
    const scanBtn = document.getElementById('b');
    console.log("掃描按鈕:", scanBtn);
    
    const deviceList = document.getElementById('deviceList');
    console.log("設備列表:", deviceList);
    
    const logs = document.getElementById('logs');
    console.log("日誌區域:", logs);
    
    // 檢查函數
    console.log("檢查函數:");
    console.log("test_wasm 函數:", typeof test_wasm);
    console.log("addLog 函數:", typeof addLog);
    
    // 檢查全域變數
    console.log("檢查全域變數:");
    console.log("ButtplugWasmClientConnector:", typeof ButtplugWasmClientConnector);
    console.log("ButtplugClient:", typeof ButtplugClient);
    console.log("navigator.bluetooth:", !!navigator.bluetooth);
    
    // 手動測試按鈕點擊
    if (scanBtn) {
        console.log("測試按鈕點擊事件...");
        scanBtn.click();
    }
    
}, 2000);

// 添加錯誤監聽
window.addEventListener('error', (e) => {
    console.error("JavaScript 錯誤:", e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error("未處理的 Promise 拒絕:", e.reason);
});

console.log("=== 診斷腳本載入完成 ===");