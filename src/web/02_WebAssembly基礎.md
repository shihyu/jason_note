# WebAssembly 基礎

> WASM 核心概念、架構與基礎應用。

## 🎯 WebAssembly 概念

### 基礎介紹
- [WebAssembly](webassembly.md)

核心內容：
- WASM 是什麼
- 為什麼需要 WASM
- WASM 架構概覽
- 基本使用方式

### 完整指南
- [WebAssembly (WASM) 完整開發指南](webassembly_complete_guide.md)

核心內容：
- WASM 模組結構
- 記憶體模型
- JavaScript 互操作
- 工具鏈介紹
- 實戰開發流程

## 💡 核心概念

### WASM 四大組件
1. **Module**
   - 編譯後的 WASM 二進制
   - 可重用的程式碼單元

2. **Memory**
   - 線性記憶體空間
   - JavaScript 可訪問
   - ArrayBuffer 實現

3. **Table**
   - 類型化的引用數組
   - 函數指針表

4. **Instance**
   - Module 的實例化
   - 可執行狀態

## 🔧 基本使用

### 載入 WASM 模組
```javascript
async function loadWasm() {
  const response = await fetch('module.wasm');
  const bytes = await response.arrayBuffer();
  const { instance } = await WebAssembly.instantiate(bytes);

  return instance.exports;
}
```

### JavaScript 互操作
```javascript
const exports = await loadWasm();

// 調用 WASM 函數
const result = exports.add(5, 3);
console.log(result); // 8

// 訪問 WASM 記憶體
const memory = exports.memory;
const buffer = new Uint8Array(memory.buffer);
```

## 🎯 WASM 優勢

### 性能
- 接近原生執行速度
- 比 JavaScript 快 10-100 倍（計算密集型任務）
- 高效的二進制格式

### 可移植性
- 跨平台執行
- 所有主流瀏覽器支援
- 沙盒安全環境

### 多語言支援
- C/C++ 編譯至 WASM
- Rust 編譯至 WASM
- Go、AssemblyScript 等

**最後更新**: 2025-12-01
