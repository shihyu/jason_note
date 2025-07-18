# Rust 模組系統範例專案

這個專案展示了 Rust 模組系統的各種功能和最佳實踐。

## 專案結構

```
rust_module_example/
├── Cargo.toml
├── README.md
├── src/
│   ├── main.rs          # 主程式入口
│   ├── lib.rs           # 函式庫入口
│   ├── swimming.rs      # 游泳相關 trait
│   └── animals/         # 動物模組目錄
│       ├── mod.rs       # 模組入口
│       ├── fish.rs      # 魚類實作
│       └── bird.rs      # 鳥類實作
└── examples/
    └── advanced_features.rs  # 進階功能展示
```

## 執行方式

### 執行主程式
```bash
cargo run
```

### 執行進階範例
```bash
cargo run --example advanced_features
```

### 啟用進階功能
```bash
cargo run --features advanced
```

## 模組系統特色

1. **模組組織** - 使用 `mod` 關鍵字組織程式碼
2. **路徑引用** - 使用 `crate::` 進行絕對路徑引用
3. **可見性控制** - 使用 `pub` 控制外部可見性
4. **重新導出** - 使用 `pub use` 簡化外部使用
5. **條件編譯** - 使用 `#[cfg]` 進行功能開關
6. **trait 系統** - 展示 Rust 的 trait 實作

## 學習重點

- 模組宣告和引用方式
- `crate::` vs `super::` vs `self::` 的使用時機
- 公開和私有項目的設計
- 子模組的組織方式
- 外部 crate 的整合方式