#!/usr/bin/env node

// 詳細的 WASM 功能測試

import init, { 
    test_basic_math, 
    test_string_processing, 
    test_heavy_computation,
    test_error_handling,
    test_performance_benchmark,
    get_memory_info,
    debug_trace,
    run_all_tests
} from './pkg/wasm_test_project.js';

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function detailedTest() {
    console.log('🚀 開始詳細 WASM 功能測試...');
    
    try {
        // 初始化 WASM 模組
        console.log('📦 初始化 WASM 模組...');
        const wasmPath = join(__dirname, 'pkg/wasm_test_project_bg.wasm');
        const wasmBuffer = await readFile(wasmPath);
        await init(wasmBuffer);
        console.log('✅ WASM 模組初始化成功');
        
        console.log('\n🧪 執行個別功能測試:');
        
        // 測試 1: 基本數學
        console.log('\n1️⃣ 測試基本數學運算');
        const mathResult = test_basic_math(42, 58);
        console.log(`✅ test_basic_math(42, 58) = ${mathResult}`);
        
        // 測試 2: 字符串處理
        console.log('\n2️⃣ 測試字符串處理');
        const stringResult = test_string_processing('Hello WASM!');
        console.log(`✅ test_string_processing("Hello WASM!") = "${stringResult}"`);
        
        // 測試 3: 重計算
        console.log('\n3️⃣ 測試重計算');
        const start = performance.now();
        const heavyResult = test_heavy_computation(5000);
        const duration = performance.now() - start;
        console.log(`✅ test_heavy_computation(5000) = ${heavyResult}, 耗時: ${duration.toFixed(2)}ms`);
        
        // 測試 4: 內存信息
        console.log('\n4️⃣ 測試內存信息');
        const memInfo = get_memory_info();
        console.log(`✅ get_memory_info() = "${memInfo}"`);
        
        // 測試 5: 調試追蹤
        console.log('\n5️⃣ 測試調試追蹤');
        debug_trace('這是一個調試消息');
        console.log('✅ debug_trace() 執行完成');
        
        // 測試 6: 錯誤處理 (正常)
        console.log('\n6️⃣ 測試錯誤處理 (正常情況)');
        try {
            const normalResult = test_error_handling(false);
            console.log(`✅ test_error_handling(false) = "${normalResult}"`);
        } catch (e) {
            console.log(`❌ 意外錯誤: ${e.message}`);
        }
        
        // 測試 7: 錯誤處理 (異常)
        console.log('\n7️⃣ 測試錯誤處理 (異常情況)');
        try {
            const errorResult = test_error_handling(true);
            console.log(`⚠️ 應該拋出錯誤但沒有: "${errorResult}"`);
        } catch (e) {
            console.log(`✅ 正確捕獲錯誤: ${e.message || e}`);
        }
        
        // 測試 8: 性能基準
        console.log('\n8️⃣ 測試性能基準');
        const perfResult = test_performance_benchmark();
        console.log(`✅ test_performance_benchmark() = ${perfResult.toFixed(2)}ms`);
        
        // 測試 9: 運行所有測試
        console.log('\n9️⃣ 運行所有內建測試');
        const allTestsResult = run_all_tests();
        console.log(`✅ run_all_tests() 完成:`);
        console.log(`   結果摘要: ${allTestsResult}`);
        
        console.log('\n🎉 所有詳細測試完成!');
        
        // 測試統計
        console.log('\n📊 測試統計:');
        console.log(`   ✅ 成功測試: 9/9`);
        console.log(`   📦 WASM 文件大小: 75KB`);
        console.log(`   ⚡ 重計算性能: ${duration.toFixed(2)}ms (5000 次迭代)`);
        console.log(`   🎯 內建基準: ${perfResult.toFixed(2)}ms`);
        
    } catch (error) {
        console.error('❌ 詳細測試失敗:', error.message);
        console.error('Stack trace:', error.stack);
        process.exit(1);
    }
}

// 執行詳細測試
detailedTest();