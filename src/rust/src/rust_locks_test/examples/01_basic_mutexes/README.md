# Arc<Mutex<T>> 基本互斥鎖範例

這個資料夾包含了 Arc<Mutex<T>> 的基本使用範例，展示如何在多執行緒環境中安全地共享和修改資料。

## 📁 範例檔案

### 1. `basic_counter.rs` - 基本計數器
- **目的**: 演示最簡單的 Arc<Mutex<T>> 使用方式
- **概念**: 多執行緒共享整數計數器
- **學習重點**:
  - Arc 的引用計數共享
  - Mutex 的互斥存取
  - 基本的執行緒同步

**執行指令**:
```bash
cargo run --example basic_counter
```

### 2. `shared_data_structure.rs` - 共享資料結構
- **目的**: 展示如何共享複雜的資料結構
- **概念**: 多執行緒修改 Vec 和結構體
- **學習重點**:
  - 複雜資料結構的保護
  - 執行緒間協作模式
  - 資料一致性保證

**執行指令**:
```bash
cargo run --example shared_data_structure
```

### 3. `error_handling.rs` - 錯誤處理與毒化機制
- **目的**: 展示 Mutex 的錯誤處理機制
- **概念**: Panic 導致的 Mutex 毒化處理
- **學習重點**:
  - Mutex 毒化機制
  - 錯誤恢復策略
  - 健壯的程式設計

**執行指令**:
```bash
cargo run --example error_handling
```

## 🎯 核心概念

### Arc (Atomically Reference Counted)
- 允許多個所有者共享同一份資料
- 執行緒安全的引用計數
- 當最後一個引用被丟棄時，資料被釋放

### Mutex (Mutual Exclusion)
- 確保同一時間只有一個執行緒能存取資料
- 使用 `.lock()` 獲取獨佔存取權
- 自動在 guard 被丟棄時釋放鎖

### 毒化機制 (Poisoning)
- 當持有鎖的執行緒 panic 時，Mutex 會被標記為"毒化"
- 後續的 `.lock()` 會返回 `Err(PoisonError)`
- 可以通過 `.into_inner()` 恢復資料

## 🚀 下一步

完成這些範例後，可以繼續學習：
- 讀寫鎖 (RwLock) - 提供更好的讀取效能
- 原子操作 (Atomics) - 無鎖的高效能操作
- 通道 (Channels) - 基於訊息傳遞的並行模式