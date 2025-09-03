#!/usr/bin/env node

// WASM 性能基準測試腳本

import { readFile } from 'fs/promises';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

// 性能測試工具
class PerformanceTester {
    constructor() {
        this.results = [];
    }
    
    async runTest(name, testFunction, iterations = 100) {
        console.log(`⏱️ 執行測試: ${name} (${iterations} 次迭代)`);
        
        const times = [];
        
        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await testFunction();
            const end = performance.now();
            times.push(end - start);
        }
        
        // 計算統計數據
        times.sort((a, b) => a - b);
        const min = times[0];
        const max = times[times.length - 1];
        const mean = times.reduce((a, b) => a + b, 0) / times.length;
        const p95 = times[Math.floor(times.length * 0.95)];
        const p99 = times[Math.floor(times.length * 0.99)];
        
        const result = {
            name,
            iterations,
            min: min.toFixed(3),
            max: max.toFixed(3),
            mean: mean.toFixed(3),
            p95: p95.toFixed(3),
            p99: p99.toFixed(3)
        };
        
        this.results.push(result);
        
        console.log(`  最小: ${min.toFixed(3)}ms`);
        console.log(`  最大: ${max.toFixed(3)}ms`);
        console.log(`  平均: ${mean.toFixed(3)}ms`);
        console.log(`  95%: ${p95.toFixed(3)}ms`);
        console.log(`  99%: ${p99.toFixed(3)}ms`);
        console.log('');
        
        return result;
    }
    
    printSummary() {
        console.log('📊 性能基準測試總結:');
        console.log('=' .repeat(80));
        console.log('| 測試名稱                | 迭代 | 最小(ms) | 平均(ms) | 95%(ms) | 99%(ms) |');
        console.log('|' + '-'.repeat(78) + '|');
        
        this.results.forEach(result => {
            const name = result.name.padEnd(22);
            const iterations = result.iterations.toString().padStart(4);
            const min = result.min.padStart(8);
            const mean = result.mean.padStart(8);
            const p95 = result.p95.padStart(7);
            const p99 = result.p99.padStart(7);
            
            console.log(`| ${name} | ${iterations} | ${min} | ${mean} | ${p95} | ${p99} |`);
        });
        
        console.log('=' .repeat(80));
    }
}

// 主要基準測試函數
async function runBenchmarks() {
    console.log('🚀 開始 WASM 性能基準測試...');
    
    try {
        // 載入優化的 WASM 文件
        console.log('📦 載入優化的 WASM 文件...');
        const wasmBuffer = await readFile('./pkg/optimized.wasm');
        console.log(`✅ WASM 文件載入成功，大小: ${wasmBuffer.length} bytes\n`);
        
        // 創建 WASM 實例
        const wasmModule = await WebAssembly.instantiate(wasmBuffer, {
            env: {
                console_log: () => {},
                console_error: () => {},
                console_warn: () => {},
                console_info: () => {},
                console_time: () => {},
                console_time_end: () => {}
            }
        });
        
        const exports = wasmModule.instance.exports;
        const tester = new PerformanceTester();
        
        // 基準測試 1: 基本數學運算
        if (exports.test_basic_math) {
            await tester.runTest('基本數學運算', () => {
                exports.test_basic_math(Math.floor(Math.random() * 100), Math.floor(Math.random() * 100));
            }, 1000);
        }
        
        // 基準測試 2: 重計算
        if (exports.test_heavy_computation) {
            await tester.runTest('重計算 (n=1000)', () => {
                exports.test_heavy_computation(1000);
            }, 50);
            
            await tester.runTest('重計算 (n=5000)', () => {
                exports.test_heavy_computation(5000);
            }, 10);
        }
        
        // 基準測試 3: 內存訊息
        if (exports.get_memory_info) {
            await tester.runTest('內存信息獲取', () => {
                exports.get_memory_info();
            }, 500);
        }
        
        // 基準測試 4: 性能基準測試函數本身
        if (exports.test_performance_benchmark) {
            await tester.runTest('內建性能測試', () => {
                exports.test_performance_benchmark();
            }, 20);
        }
        
        // 基準測試 5: 錯誤處理
        if (exports.test_error_handling) {
            await tester.runTest('錯誤處理 (正常)', () => {
                exports.test_error_handling(0);
            }, 200);
            
            await tester.runTest('錯誤處理 (異常)', () => {
                try {
                    exports.test_error_handling(1);
                } catch (e) {
                    // 預期的錯誤
                }
            }, 200);
        }
        
        // 打印總結
        tester.printSummary();
        
        console.log('\n🎉 基準測試完成!');
        
    } catch (error) {
        console.error('❌ 基準測試失敗:', error.message);
        process.exit(1);
    }
}

// 執行基準測試
runBenchmarks();