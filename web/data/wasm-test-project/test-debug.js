#!/usr/bin/env node

// WASM 調試測試腳本
// 專門用於 GDB 調試

import { readFile } from 'fs/promises';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

// 調試輔助函數
function debugLog(message) {
    console.log(`[DEBUG ${new Date().toISOString()}] ${message}`);
}

// 詳細的 WASM 調試測試
async function debugTestWasm() {
    debugLog('🐛 開始 WASM 調試測試...');
    
    try {
        // 載入調試版 WASM 文件
        debugLog('📦 載入調試版 WASM 文件...');
        const wasmBuffer = await readFile('./pkg/debug.wasm');
        debugLog(`✅ 調試版 WASM 文件載入成功，大小: ${wasmBuffer.length} bytes`);
        
        // 設置斷點友好的環境
        debugLog('🔧 設置調試環境...');
        
        // 創建詳細的導入對象
        const imports = {
            env: {
                // 提供詳細的 console API 模擬
                console_log: (ptr, len) => {
                    debugLog(`WASM console.log called with ptr=${ptr}, len=${len}`);
                },
                console_error: (ptr, len) => {
                    debugLog(`WASM console.error called with ptr=${ptr}, len=${len}`);
                },
                console_warn: (ptr, len) => {
                    debugLog(`WASM console.warn called with ptr=${ptr}, len=${len}`);
                },
                console_info: (ptr, len) => {
                    debugLog(`WASM console.info called with ptr=${ptr}, len=${len}`);
                },
                console_time: (ptr, len) => {
                    debugLog(`WASM console.time called with ptr=${ptr}, len=${len}`);
                },
                console_time_end: (ptr, len) => {
                    debugLog(`WASM console.timeEnd called with ptr=${ptr}, len=${len}`);
                }
            }
        };
        
        // 實例化 WASM 模組 (調試友好)
        debugLog('🚀 實例化 WASM 模組...');
        const wasmModule = await WebAssembly.instantiate(wasmBuffer, imports);
        debugLog('✅ WASM 模組實例化成功');
        
        // 設置 GDB 斷點位置
        debugger; // 在這裡可以設置 GDB 斷點
        
        // 獲取導出函數
        const exports = wasmModule.instance.exports;
        debugLog('📋 分析導出函數:');
        
        const functions = [];
        Object.keys(exports).forEach(key => {
            if (typeof exports[key] === 'function') {
                functions.push(key);
                debugLog(`  - ${key}: ${typeof exports[key]}`);
            }
        });
        
        // 逐步測試每個函數
        debugLog('\n🧪 開始逐步調試測試:');
        
        // 測試 1: 基本數學運算
        if (exports.test_basic_math) {
            debugLog('📊 測試 test_basic_math...');
            debugger; // GDB 斷點
            const mathResult = exports.test_basic_math(42, 58);
            debugLog(`✅ test_basic_math(42, 58) = ${mathResult}`);
        }
        
        // 測試 2: 內存信息
        if (exports.get_memory_info) {
            debugLog('💾 測試 get_memory_info...');
            debugger; // GDB 斷點
            try {
                exports.get_memory_info();
                debugLog('✅ get_memory_info() 執行成功');
            } catch (e) {
                debugLog(`❌ get_memory_info() 錯誤: ${e.message}`);
            }
        }
        
        // 測試 3: 重計算測試
        if (exports.test_heavy_computation) {
            debugLog('⚡ 測試 test_heavy_computation...');
            debugger; // GDB 斷點
            const heavyResult = exports.test_heavy_computation(1000);
            debugLog(`✅ test_heavy_computation(1000) = ${heavyResult}`);
        }
        
        // 測試 4: 錯誤處理
        if (exports.test_error_handling) {
            debugLog('🚨 測試錯誤處理...');
            debugger; // GDB 斷點
            try {
                // 測試正常情況
                const normalResult = exports.test_error_handling(0); // false
                debugLog(`✅ 正常情況: ${normalResult}`);
                
                // 測試錯誤情況
                const errorResult = exports.test_error_handling(1); // true
                debugLog(`⚠️ 錯誤情況: ${errorResult}`);
            } catch (e) {
                debugLog(`❌ 錯誤處理測試異常: ${e.message}`);
            }
        }
        
        // 最終調試點
        debugger; // 最終 GDB 斷點
        debugLog('\n🎉 調試測試完成!');
        
        // 輸出調試摘要
        debugLog('📊 調試摘要:');
        debugLog(`  - WASM 文件大小: ${wasmBuffer.length} bytes`);
        debugLog(`  - 導出函數數量: ${functions.length}`);
        debugLog(`  - 測試函數: ${functions.join(', ')}`);
        
    } catch (error) {
        debugLog(`❌ 調試測試失敗: ${error.message}`);
        debugLog(`Stack trace: ${error.stack}`);
        process.exit(1);
    }
}

// GDB 調試提示
console.log('🐛 GDB 調試提示:');
console.log('  1. 運行: gdb --args node test-debug.js');
console.log('  2. 設置斷點: break debugTestWasm');
console.log('  3. 運行程序: run');
console.log('  4. 繼續執行: continue');
console.log('  5. 檢查變量: print variable_name');
console.log('  6. 單步執行: next 或 step');
console.log('');

// 執行調試測試
debugTestWasm();