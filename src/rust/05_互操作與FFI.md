# Rust 互操作與 FFI

> Rust 與 C/C++/Python 的互操作、FFI 調用、語言對比。

## 🔗 Rust 調用 C/C++

### C 語言互操作
- [Rust 調用 C](rust_call_c.md)
- [Rust 調用 C (Cargo)](rust_call_c_cargo.md)

### C++ 對比與互操作
- [Rust vs C++](rust_vs_cpp.md)
- [C++ vs Rust 對比](cpp_vs_rust_comparison.md)
- [Rust C++ 對比](rust_cpp_comparison_md.md)

### Wrapper 模式
- [Wrappers 指南](rust_wrappers_guide.md)

## 🐍 Rust 與 Python

### PyO3
- [PyO3 教學](pyo3.md) - Rust 與 Python 互操作

## 📊 語言特性對比

### 所有權與移動語義
- [C++ Move vs Rust Ownership](cpp-move-vs-rust-ownership.md)

### Self vs this
- [Rust Self vs C++ this](Rust-self-Self-與-C++-this-對比指南.md)

## 💡 使用建議

**何時使用 Rust 調用 C/C++**:
- 復用現有 C/C++ 庫
- 性能關鍵路徑
- 系統底層 API

**何時使用 PyO3**:
- Python 性能瓶頸優化
- 科學計算加速
- 機器學習推理

**注意事項**:
- FFI 調用需要 `unsafe`
- 注意記憶體安全
- 正確處理錯誤

**最後更新**: 2025-12-01
