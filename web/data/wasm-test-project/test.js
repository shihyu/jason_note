#!/usr/bin/env node

// WASM 測試腳本
// 需要 Node.js 環境運行

import { readFile } from 'fs/promises';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

// 簡單的 WASM 載入和測試
async function testWasm() {
    console.log('🚀 開始 WASM 測試...');
    
    try {
        // 載入 WASM 文件
        console.log('📦 載入 WASM 文件...');
        const wasmBuffer = await readFile('./pkg/optimized.wasm');
        console.log(`✅ WASM 文件載入成功，大小: ${wasmBuffer.length} bytes`);
        
        // 使用 Node.js 的 WebAssembly API
        const wasmModule = await WebAssembly.instantiate(wasmBuffer, {
            env: {
                // 提供 console API 的模擬
                console_log: (ptr, len) => {
                    console.log('[WASM]', 'Log called');
                },
                console_error: (ptr, len) => {
                    console.error('[WASM]', 'Error called');
                },
                console_warn: (ptr, len) => {
                    console.warn('[WASM]', 'Warn called');
                },
                console_info: (ptr, len) => {
                    console.info('[WASM]', 'Info called');
                }
            }
        });
        
        console.log('✅ WASM 模組實例化成功');
        
        // 列出可用的導出函數
        const exports = wasmModule.instance.exports;
        console.log('📋 可用的導出函數:');
        Object.keys(exports).forEach(key => {
            if (typeof exports[key] === 'function') {
                console.log(`  - ${key}`);
            }
        });
        
        // 測試基本功能
        console.log('\n🧪 執行功能測試:');
        
        // 如果有 test_basic_math 函數
        if (exports.test_basic_math) {
            const result = exports.test_basic_math(10, 20);
            console.log(`✅ test_basic_math(10, 20) = ${result}`);
        }
        
        // 如果有 get_memory_info 函數
        if (exports.get_memory_info) {
            try {
                exports.get_memory_info();
                console.log('✅ get_memory_info() 執行成功');
            } catch (e) {
                console.log('⚠️ get_memory_info() 執行時發生錯誤:', e.message);
            }
        }
        
        console.log('\n🎉 WASM 測試完成!');
        
    } catch (error) {
        console.error('❌ 測試失敗:', error.message);
        process.exit(1);
    }
}

// 執行測試
testWasm();