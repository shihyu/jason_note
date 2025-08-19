# WebAssembly 相容性與載入器完整指南

## 目錄
- [WASM 編譯產物](#wasm-編譯產物)
- [調試方法](#調試方法)
- [WASM 載入器](#wasm-載入器)
- [載入失敗原因](#載入失敗原因)
- [WASM 相容性策略](#wasm-相容性策略)
- [載入器生態系統](#載入器生態系統)

## WASM 編譯產物

WASM 編譯會產生：
- **.wasm** 文件：二進制格式的 WebAssembly 模塊
- **.wat** 文件：文本格式（WebAssembly Text Format），可讀的 S-表達式格式

## 調試方法

### 1. Log 調試
```javascript
// 在 WASM 模塊中導出調試函數
Module.exports.debug_log = (value) => {
    console.log('WASM debug:', value);
};

// 在 C/C++ 源碼中
extern void debug_log(int value);
void my_function() {
    debug_log(42); // 輸出調試信息
}
```

### 2. 瀏覽器開發者工具
現代瀏覽器支持 WASM 調試：
- Chrome/Edge DevTools 可以直接調試 WASM
- 設置斷點、查看變量
- 支持源碼映射（source maps）

### 3. GDB 調試（有限支持）
```bash
# 使用 wasmer 等運行時
wasmer run --debug module.wasm

# 或使用 wasmtime
wasmtime --debug module.wasm
```

### 4. 專門的 WASM 調試工具
- **wasmtime** 運行時支持調試
- **wasm-pack** 提供調試輔助
- **wasm-bindgen** 生成的綁定代碼便於調試

## WASM 載入器

WASM 載入器負責載入和實例化 WebAssembly 模塊：

### 1. 瀏覽器環境
```javascript
// 使用 WebAssembly API
async function loadWasm() {
    const response = await fetch('module.wasm');
    const bytes = await response.arrayBuffer();
    const module = await WebAssembly.compile(bytes);
    const instance = await WebAssembly.instantiate(module);
    return instance.exports;
}

// 或者直接
WebAssembly.instantiateStreaming(fetch('module.wasm'))
    .then(result => {
        // 使用 result.instance.exports
    });
```

### 2. Node.js 環境
```javascript
const fs = require('fs');
const wasmBuffer = fs.readFileSync('module.wasm');
WebAssembly.instantiate(wasmBuffer).then(result => {
    const exports = result.instance.exports;
});
```

### 3. 載入過程
1. **獲取** .wasm 文件
2. **編譯** 字節碼為機器碼
3. **實例化** 創建模塊實例
4. **綁定** 導入/導出函數
5. **執行** 調用 WASM 函數

## 載入失敗原因

> **重要：** 能編譯出 WASM 不代表就能成功載入！

### 1. 導入依賴問題
```javascript
// WASM 模塊期望的導入
const importObject = {
    env: {
        memory: new WebAssembly.Memory({ initial: 256 }),
        table: new WebAssembly.Table({ initial: 0, element: 'anyfunc' }),
        __memory_base: 0,
        __table_base: 0,
        abort: () => { throw new Error('abort called'); }
    }
};

// 如果缺少必要的導入，載入會失敗
WebAssembly.instantiate(wasmBytes, importObject);
```

### 2. 記憶體限制
```javascript
// WASM 模塊要求的記憶體超過限制
const importObject = {
    env: {
        memory: new WebAssembly.Memory({ 
            initial: 1000,  // 如果太大會失敗
            maximum: 2000 
        })
    }
};
```

### 3. 平台兼容性
```bash
# 編譯時指定了特定的 CPU 特性
emcc -msse4.1 source.c -o output.wasm  # 老舊瀏覽器不支持

# 或使用了實驗性功能
emcc -matomics -mbulk-memory source.c -o output.wasm
```

### 4. 驗證失敗
```wast
;; 無效的 WASM 字節碼
(module
  (func $invalid
    i32.const 42
    i64.add  ;; 型別不匹配！i32 + i64
  )
)
```

### 5. 安全策略限制
```javascript
// CSP (Content Security Policy) 可能阻止 WASM
// HTTP header: Content-Security-Policy: script-src 'self'

// 某些環境禁用 WebAssembly
if (typeof WebAssembly === 'undefined') {
    console.error('WebAssembly not supported');
}
```

## 除錯載入問題的方法

### 1. 檢查導入需求
```bash
# 查看 WASM 模塊需要的導入
wasm-objdump -x module.wasm

# 或使用 wabt 工具
wasm2wat module.wasm | grep import
```

### 2. 驗證 WASM 檔案
```bash
# 檢查 WASM 格式是否正確
wasm-validate module.wasm

# 反組譯查看內容
wasm2wat module.wasm -o module.wat
```

### 3. 逐步載入測試
```javascript
async function debugWasmLoad(wasmPath) {
    try {
        // 1. 檢查檔案是否存在
        const response = await fetch(wasmPath);
        if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.status}`);
        }
        
        // 2. 檢查編譯
        const bytes = await response.arrayBuffer();
        console.log('WASM size:', bytes.byteLength);
        
        const module = await WebAssembly.compile(bytes);
        console.log('Compilation successful');
        
        // 3. 檢查導入需求
        const imports = WebAssembly.Module.imports(module);
        console.log('Required imports:', imports);
        
        // 4. 提供基本導入
        const importObject = {
            env: {
                memory: new WebAssembly.Memory({ initial: 256 }),
                // ... 其他必要的導入
            }
        };
        
        // 5. 實例化
        const instance = await WebAssembly.instantiate(module, importObject);
        console.log('Instantiation successful');
        
        return instance;
        
    } catch (error) {
        console.error('WASM load failed:', error);
        throw error;
    }
}
```

### 4. 常見錯誤模式
```javascript
// TypeError: import object field 'xxx' is not a Function
// → 缺少必要的函數導入

// RangeError: Maximum memory size exceeded
// → 記憶體需求超過限制

// CompileError: WebAssembly.compile(): invalid magic word
// → WASM 檔案損壞或格式錯誤

// LinkError: import object field 'memory' is not a Memory
// → 記憶體物件類型錯誤
```

## WASM 相容性策略

### 1. 使用保守的編譯選項
```bash
# 高相容性編譯（避免新功能）
emcc source.c -o output.wasm \
  -s WASM=1 \
  -s STANDALONE_WASM=1 \
  -s EXPORTED_FUNCTIONS='["_main"]' \
  --no-entry

# 避免這些可能有相容性問題的選項
# -matomics（多執行緒）
# -msimd128（SIMD）
# -mbulk-memory（批量記憶體操作）
# -mmutable-globals（可變全域變數）
```

### 2. 最小化外部依賴
```c
// 避免複雜的 libc 功能
#include <stdint.h>  // ✓ 基本型別
// #include <stdio.h>   // ✗ 可能需要額外導入

// 自己實現簡單功能而不依賴標準庫
int my_strlen(const char* str) {
    int len = 0;
    while (str[len]) len++;
    return len;
}
```

### 3. 檢查功能支援
```javascript
// 檢查瀏覽器支援
function checkWasmSupport() {
    return typeof WebAssembly === 'object' &&
           typeof WebAssembly.instantiate === 'function';
}

// 檢查特定功能
async function checkWasmFeatures() {
    const features = {
        basic: typeof WebAssembly !== 'undefined',
        streaming: typeof WebAssembly.instantiateStreaming !== 'undefined',
        threads: typeof SharedArrayBuffer !== 'undefined',
        simd: false // 需要更複雜的檢測
    };
    
    // 檢測 SIMD 支援
    try {
        await WebAssembly.compile(new Uint8Array([
            0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
            // SIMD 測試字節碼...
        ]));
        features.simd = true;
    } catch (e) {
        features.simd = false;
    }
    
    return features;
}
```

## 載入器生態系統

### 1. 瀏覽器原生載入器
```javascript
// 最基本、相容性最好
async function loadWasmNative(url) {
    const response = await fetch(url);
    const bytes = await response.arrayBuffer();
    const result = await WebAssembly.instantiate(bytes);
    return result.instance;
}
```

### 2. 框架整合載入器

#### Emscripten 生成的載入器
```javascript
// Emscripten 自動生成
Module = {
    onRuntimeInitialized: function() {
        // WASM 載入完成
        console.log('Emscripten module ready');
    }
};
```

#### wasm-pack (Rust)
```javascript
// wasm-pack 生成的 JavaScript 綁定
import init, { greet } from './pkg/my_wasm.js';

async function run() {
    await init();  // 載入 WASM
    greet('World');
}
```

#### AssemblyScript
```javascript
// AssemblyScript 載入器
import { instantiate } from "@assemblyscript/loader";

instantiate(fetch("module.wasm")).then(module => {
    module.exports.add(1, 2);
});
```

### 3. 運行時載入器

#### Node.js 環境
```javascript
const fs = require('fs');

// 同步載入
const wasmBuffer = fs.readFileSync('module.wasm');
const wasmModule = new WebAssembly.Module(wasmBuffer);
const wasmInstance = new WebAssembly.Instance(wasmModule);

// 異步載入
async function loadWasmNode(path) {
    const wasmBuffer = await fs.promises.readFile(path);
    return await WebAssembly.instantiate(wasmBuffer);
}
```

#### Deno
```javascript
const wasmCode = await Deno.readFile("./module.wasm");
const wasmModule = new WebAssembly.Module(wasmCode);
const wasmInstance = new WebAssembly.Instance(wasmModule);
```

### 4. 獨立運行時

#### Wasmtime
```bash
# 命令行執行
wasmtime module.wasm

# 或嵌入到應用程式
wasmtime = Wasmtime::Engine.new
module = wasmtime.module_from_file('module.wasm')
```

#### Wasmer
```bash
# 直接執行
wasmer run module.wasm

# 或編譯為原生執行檔
wasmer compile module.wasm -o native_binary
```

## 通用載入器模式

```javascript
// 統一的載入器介面
class UniversalWasmLoader {
    async load(wasmPath, importObject = {}) {
        // 環境檢測
        if (typeof WebAssembly === 'undefined') {
            throw new Error('WebAssembly not supported');
        }
        
        // 預設導入物件
        const defaultImports = {
            env: {
                memory: new WebAssembly.Memory({ initial: 256 }),
                table: new WebAssembly.Table({ initial: 0, element: 'anyfunc' }),
                __memory_base: 0,
                __table_base: 0,
                abort: () => { throw new Error('abort'); }
            }
        };
        
        const mergedImports = this.mergeImports(defaultImports, importObject);
        
        try {
            // 嘗試串流載入（較新瀏覽器）
            if (typeof WebAssembly.instantiateStreaming !== 'undefined') {
                const result = await WebAssembly.instantiateStreaming(
                    fetch(wasmPath), 
                    mergedImports
                );
                return result.instance;
            }
        } catch (e) {
            console.warn('Streaming failed, falling back to fetch');
        }
        
        // 降級到傳統載入
        const response = await fetch(wasmPath);
        const bytes = await response.arrayBuffer();
        const result = await WebAssembly.instantiate(bytes, mergedImports);
        return result.instance;
    }
    
    mergeImports(defaults, custom) {
        // 深度合併導入物件
        return { ...defaults, ...custom };
    }
}
```

## 常見載入器類型總結

| 載入器類型 | 適用場景 | 相容性 | 複雜度 |
|-----------|---------|--------|--------|
| 瀏覽器原生 API | 基本使用 | 最高 | 低 |
| Emscripten | C/C++ 項目 | 高 | 中 |
| wasm-pack | Rust 項目 | 高 | 中 |
| AssemblyScript | TypeScript 項目 | 高 | 低 |
| Node.js 原生 | 伺服器端 | 高 | 低 |
| Wasmtime/Wasmer | 獨立應用 | 中 | 高 |

## 最佳實踐總結

### 相容性方面：
- 使用保守編譯選項
- 最小化依賴
- 避免實驗性功能
- 提供降級方案

### 載入器選擇：
- **新項目**：建議先用瀏覽器原生 WebAssembly API
- **特殊需求**：再考慮特定框架的載入器
- **生產環境**：使用經過驗證的載入器組合

載入器本質上是連接 WASM 模塊與宿主環境（瀏覽器、Node.js 等）的橋樑，處理記憶體管理、函數調用和數據轉換。