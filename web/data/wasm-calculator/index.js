// WASM 計算機 JavaScript 入口

import init, { main, handle_button } from './wasm_calculator.js';

// 將 handle_button 暴露到全局作用域
window.handle_button = handle_button;

// 初始化 WASM 模組
async function run() {
    await init();
    main();
}

run().catch(console.error);
