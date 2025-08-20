#!/usr/bin/env node

// 簡化的 WASM 測試腳本 - 使用 wasm-pack 生成的綁定

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 檢查 WASM 文件
async function testWasmFiles() {
    console.log('🚀 開始 WASM 文件測試...');
    
    try {
        // 檢查生成的文件
        const files = [
            'pkg/wasm_test_project_bg.wasm',
            'pkg/wasm_test_project.js',
            'pkg/optimized.wasm'
        ];
        
        for (const file of files) {
            try {
                const filePath = join(__dirname, file);
                const stats = await readFile(filePath);
                console.log(`✅ ${file}: ${stats.length} bytes`);
            } catch (error) {
                console.log(`❌ ${file}: 文件不存在`);
            }
        }
        
        // 測試原始 WASM 文件
        console.log('\n📦 測試原始 WASM 文件...');
        const wasmBuffer = await readFile(join(__dirname, 'pkg/wasm_test_project_bg.wasm'));
        console.log(`✅ WASM 文件載入成功，大小: ${wasmBuffer.length} bytes`);
        
        // 分析 WASM 文件
        console.log('\n🔍 分析 WASM 模組...');
        const wasmModule = await WebAssembly.compile(wasmBuffer);
        
        // 獲取模組導入和導出
        const imports = WebAssembly.Module.imports(wasmModule);
        const exports = WebAssembly.Module.exports(wasmModule);
        
        console.log(`📥 導入數量: ${imports.length}`);
        imports.slice(0, 10).forEach(imp => {
            console.log(`  - ${imp.module}.${imp.name} (${imp.kind})`);
        });
        
        console.log(`📤 導出數量: ${exports.length}`);
        exports.slice(0, 10).forEach(exp => {
            console.log(`  - ${exp.name} (${exp.kind})`);
        });
        
        console.log('\n🎉 WASM 文件測試完成!');
        
    } catch (error) {
        console.error('❌ 測試失敗:', error.message);
        process.exit(1);
    }
}

// 執行測試
testWasmFiles();