# Rust 鎖機制完整指南 🦀

## 📑 目錄結構

這份指南分為以下部分：

### 第一部分：概覽與基礎
- [視覺化概覽](#視覺化概覽)
- [Arc<Mutex<T>>](#arc-mutex-基本互斥鎖)
- [Arc<RwLock<T>>](#arc-rwlock-讀寫鎖)

### 第二部分：高效能原語
- [Atomic 類型](#atomic-類型)
- [Channel 通道](#channel-通道)

### 第三部分：高級同步
- [Condvar 條件變數](#condvar-條件變數)
- [Rc<RefCell<T>>](#rc-refcell-單執行緒共享)

### 第四部分：實戰與最佳實踐
- [高級並行模式](#高級並行模式)
- [選擇指南與最佳實踐](#選擇指南與最佳實踐)

---

## 📊 視覺化概覽

```
Rust 鎖的選擇流程圖：
┌─────────────────┐
│   需要共享嗎？   │
└─────┬───────────┘
      │ 是
      ▼
┌─────────────────┐    ┌──────────────────┐
│   簡單原子操作？ │───▶│  使用 Atomic     │
└─────┬───────────┘ 是 │  🔢 原子類型      │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐    ┌──────────────────┐
│   單一執行緒？   │───▶│  使用 Rc<RefCell>│
└─────┬───────────┘ 是 │  🏠 單執行緒共享  │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐    ┌──────────────────┐
│   多讀少寫？     │───▶│  使用 RwLock     │
└─────┬───────────┘ 是 │  📖 讀寫鎖        │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐    ┌──────────────────┐
│   需要等待？     │───▶│  使用 Condvar    │
└─────┬───────────┘ 是 │  🚌 條件變數      │
      │ 否           └──────────────────┘
      ▼
┌─────────────────┐
│  使用 Mutex     │
│  🔒 互斥鎖       │
└─────────────────┘
```

### 效能與使用場景快速參考

| 類型 | 效能 | 使用場景 | 特點 |
|------|------|----------|------|
| `Atomic` | 🥇 最快 | 簡單計數/標誌 | 無鎖，編譯時保證 |
| `Arc<RwLock>` (讀) | 🥈 很快 | 多讀少寫 | 並行讀取 |
| `Channel` | 🥉 快 | 執行緒通訊 | 零拷貝傳遞 |
| `Arc<Mutex>` | 🏅 中等 | 基本互斥 | 簡單可靠 |
| `Condvar` | 🏅 中等 | 條件等待 | 事件驅動 |
| `Rc<RefCell>` | 🏅 中等 | 單執行緒共享 | 運行時檢查 |

---

## Arc<Mutex<T>> 基本互斥鎖 🔒

**白話解釋**: 像有多把鑰匙的保險箱，每個執行緒都有鑰匙(Arc)，但一次只能一個人開箱子(Mutex)

```
Arc<Mutex<T>> 工作示意圖：
Thread A: 🔑 ──┐
Thread B: 🔑 ──┼──▶ 📦 Mutex<T>
Thread C: 🔑 ──┘
```

### 基本使用範例

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn basic_example() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                let mut num = counter.lock().unwrap();
                *num += 1;
            }
            println!("執行緒 {} 完成", i);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("最終計數: {}", *counter.lock().unwrap());
}
```

### 共享資料結構範例

```rust
#[derive(Debug)]
struct SharedData {
    value: i32,
    items: Vec<String>,
}

impl SharedData {
    fn new() -> Self {
        SharedData {
            value: 0,
            items: Vec::new(),
        }
    }
    
    fn add_item(&mut self, item: String) {
        self.value += 1;
        self.items.push(item);
    }
}

fn shared_data_example() {
    let data = Arc::new(Mutex::new(SharedData::new()));
    let mut handles = vec![];

    for i in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            for j in 0..3 {
                let item = format!("執行緒{}-項目{}", i, j);
                {
                    let mut shared = data.lock().unwrap();
                    shared.add_item(item.clone());
                    println!("新增: {}", item);
                }
                thread::sleep(std::time::Duration::from_millis(100));
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("最終資料: {:?}", *data.lock().unwrap());
}
```

### 錯誤處理與毒化機制

```rust
fn poison_handling_example() {
    let data = Arc::new(Mutex::new(vec![1, 2, 3]));
    let data_clone = Arc::clone(&data);
    
    // 建立會 panic 的執行緒
    let handle = thread::spawn(move || {
        let mut vec = data_clone.lock().unwrap();
        vec.push(4);
        panic!("故意的 panic!");
    });
    
    let _ = handle.join();
    
    // 處理毒化的 Mutex
    match data.lock() {
        Ok(vec) => println!("成功獲取: {:?}", *vec),
        Err(poisoned) => {
            println!("Mutex 被毒化了！");
            let vec = poisoned.into_inner();
            println!("強制獲取的資料: {:?}", *vec);
        }
    }
}

// 安全的 Mutex 存取包裝器
fn safe_mutex_access<T, F, R>(mutex: &Mutex<T>, f: F) -> Result<R, String>
where
    F: FnOnce(&mut T) -> R,
{
    match mutex.lock() {
        Ok(mut guard) => Ok(f(&mut guard)),
        Err(poisoned) => {
            eprintln!("警告: Mutex 被毒化，嘗試恢復...");
            let mut guard = poisoned.into_inner();
            Ok(f(&mut guard))
        }
    }
}
```

---

## Arc<RwLock<T>> 讀寫鎖 📖

**白話解釋**: 像圖書館規則，多人可以同時看書(讀)，但寫字時要清場

```
RwLock 狀態圖：
讀取模式: 👀👀👀👀 → [Data] ← ✍️💤 (寫者等待)
寫入模式: ✍️ → [Data] ← 👀💤👀💤 (讀者等待)
```

### 設定檔快取範例

```rust
use std::sync::{Arc, RwLock};
use std::thread;
use std::time::Duration;
use std::collections::HashMap;

#[derive(Debug, Clone)]
struct Config {
    settings: HashMap<String, String>,
    version: u32,
}

impl Config {
    fn new() -> Self {
        let mut settings = HashMap::new();
        settings.insert("theme".to_string(), "dark".to_string());
        settings.insert("language".to_string(), "zh-TW".to_string());
        
        Config { settings, version: 1 }
    }
    
    fn get_setting(&self, key: &str) -> Option<String> {
        self.settings.get(key).cloned()
    }
    
    fn update_setting(&mut self, key: String, value: String) {
        self.settings.insert(key, value);
        self.version += 1;
    }
}

fn config_cache_example() {
    let config = Arc::new(RwLock::new(Config::new()));
    let mut handles = vec![];
    
    // 多個讀者執行緒
    for i in 0..5 {
        let config = Arc::clone(&config);
        let handle = thread::spawn(move || {
            for j in 0..3 {
                let reader = config.read().unwrap();
                let theme = reader.get_setting("theme").unwrap_or_default();
                println!("讀者 {} 第 {} 次: theme={}", i, j, theme);
                drop(reader);
                thread::sleep(Duration::from_millis(100));
            }
        });
        handles.push(handle);
    }
    
    // 寫者執行緒
    for i in 0..2 {
        let config = Arc::clone(&config);
        let handle = thread::spawn(move || {
            thread::sleep(Duration::from_millis(200));
            let mut writer = config.write().unwrap();
            let new_theme = if i == 0 { "light" } else { "auto" };
            writer.update_setting("theme".to_string(), new_theme.to_string());
            println!("寫者 {} 更新主題為: {}", i, new_theme);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}
```

### 效能比較範例

```rust
fn performance_comparison() {
    use std::time::Instant;
    
    let iterations = 10000;
    let thread_count = 4;
    
    // Mutex 測試
    let mutex_data = Arc::new(Mutex::new(0));
    let start = Instant::now();
    
    let mut handles = vec![];
    for _ in 0..thread_count {
        let data = Arc::clone(&mutex_data);
        let handle = thread::spawn(move || {
            for _ in 0..iterations {
                let _guard = data.lock().unwrap();
                // 模擬讀取操作
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    let mutex_time = start.elapsed();
    
    // RwLock 測試
    let rwlock_data = Arc::new(RwLock::new(0));
    let start = Instant::now();
    
    let mut handles = vec![];
    for _ in 0..thread_count {
        let data = Arc::clone(&rwlock_data);
        let handle = thread::spawn(move || {
            for _ in 0..iterations {
                let _guard = data.read().unwrap();
                // 模擬讀取操作
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    let rwlock_time = start.elapsed();
    
    println!("Mutex 時間: {:?}", mutex_time);
    println!("RwLock 時間: {:?}", rwlock_time);
    println!("RwLock 比 Mutex 快 {:.2}x", 
        mutex_time.as_nanos() as f64 / rwlock_time.as_nanos() as f64);
}
```

# Rust 鎖機制指南 - 第二部分：高效能原語 ⚡

## Atomic 類型 ⚛️

**白話解釋**: 像原子彈一樣，操作不可分割，要嘛全做完，要嘛不做

```
Atomic vs Mutex 性能對比：
非原子操作問題 ❌:
Thread1: 讀取(5) → +1 → 寫入(6)
Thread2:   讀取(5) → +1 → 寫入(6) ← 丟失更新!

原子操作 ✅:
Thread1: fetch_add(1) → 6
Thread2: fetch_add(1) → 7 ← 正確!
```

### 基本原子操作範例

```rust
use std::sync::atomic::{AtomicI32, AtomicBool, AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

fn basic_atomic_example() {
    let counter = Arc::new(AtomicI32::new(0));
    let mut handles = vec![];
    
    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                counter.fetch_add(1, Ordering::SeqCst);
            }
            println!("執行緒 {} 完成", i);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("最終計數: {}", counter.load(Ordering::SeqCst));
}
```

### 原子布林值控制執行緒

```rust
fn atomic_flag_example() {
    let running = Arc::new(AtomicBool::new(true));
    let counter = Arc::new(AtomicUsize::new(0));
    
    // 工作執行緒
    let running_clone = Arc::clone(&running);
    let counter_clone = Arc::clone(&counter);
    let worker = thread::spawn(move || {
        while running_clone.load(Ordering::SeqCst) {
            counter_clone.fetch_add(1, Ordering::SeqCst);
            thread::sleep(Duration::from_millis(10));
        }
        println!("工作執行緒結束");
    });
    
    // 主執行緒等待3秒後停止
    thread::sleep(Duration::from_secs(3));
    running.store(false, Ordering::SeqCst);
    
    worker.join().unwrap();
    println!("總計數: {}", counter.load(Ordering::SeqCst));
}
```

### Compare-And-Swap (CAS) 進階操作

```rust
fn cas_example() {
    let value = Arc::new(AtomicI32::new(10));
    let mut handles = vec![];
    
    for i in 0..3 {
        let value = Arc::clone(&value);
        let handle = thread::spawn(move || {
            loop {
                let current = value.load(Ordering::SeqCst);
                let new_value = current * 2;
                
                match value.compare_exchange_weak(
                    current, 
                    new_value, 
                    Ordering::SeqCst, 
                    Ordering::SeqCst
                ) {
                    Ok(_) => {
                        println!("執行緒 {} 成功將 {} 更新為 {}", i, current, new_value);
                        break;
                    }
                    Err(actual) => {
                        println!("執行緒 {} CAS 失敗，期望 {} 但實際是 {}", i, current, actual);
                    }
                }
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("最終值: {}", value.load(Ordering::SeqCst));
}
```

### 記憶體順序 (Memory Ordering)

```rust
fn memory_ordering_example() {
    let data = Arc::new(AtomicI32::new(0));
    let flag = Arc::new(AtomicBool::new(false));
    
    // 生產者執行緒
    let data_producer = Arc::clone(&data);
    let flag_producer = Arc::clone(&flag);
    let producer = thread::spawn(move || {
        // 1. 寫入資料
        data_producer.store(42, Ordering::Relaxed);
        
        // 2. 設定旗標 (Release語義)
        flag_producer.store(true, Ordering::Release);
        
        println!("生產者：資料寫入完成");
    });
    
    // 消費者執行緒
    let data_consumer = Arc::clone(&data);
    let flag_consumer = Arc::clone(&flag);
    let consumer = thread::spawn(move || {
        // 等待旗標 (Acquire語義)
        while !flag_consumer.load(Ordering::Acquire) {
            thread::sleep(Duration::from_millis(1));
        }
        
        let value = data_consumer.load(Ordering::Relaxed);
        println!("消費者：讀取到資料 {}", value);
    });
    
    producer.join().unwrap();
    consumer.join().unwrap();
}
```

### 記憶體順序效能比較

```rust
fn ordering_performance_test() {
    let counter = Arc::new(AtomicI32::new(0));
    let iterations = 1_000_000;
    
    // 測試 SeqCst (最強順序)
    let start = Instant::now();
    let counter_seqcst = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        for _ in 0..iterations {
            counter_seqcst.fetch_add(1, Ordering::SeqCst);
        }
    });
    handle.join().unwrap();
    let seqcst_time = start.elapsed();
    
    counter.store(0, Ordering::SeqCst);
    
    // 測試 Relaxed (最弱順序)
    let start = Instant::now();
    let counter_relaxed = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        for _ in 0..iterations {
            counter_relaxed.fetch_add(1, Ordering::Relaxed);
        }
    });
    handle.join().unwrap();
    let relaxed_time = start.elapsed();
    
    println!("SeqCst 時間: {:?}", seqcst_time);
    println!("Relaxed 時間: {:?}", relaxed_time);
    println!("Relaxed 比 SeqCst 快 {:.2}x", 
        seqcst_time.as_nanos() as f64 / relaxed_time.as_nanos() as f64);
}
```

---

## Channel 通道 📡

**白話解釋**: 像郵筒，一邊投信一邊收信，是 Rust 的特色並行通訊方式

```
Channel 通訊示意圖：
Producer1: 📤 ──┐
Producer2: 📤 ──┼──▶ 📬 Channel ──▶ 📥 Consumer
Producer3: 📤 ──┘

同步 vs 異步:
Sync:   發送者等待接收者準備好
Async:  發送者立即返回，訊息進入佇列
```

### 標準庫 Channel 基本範例

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn basic_channel_example() {
    let (tx, rx) = mpsc::channel();
    
    // 發送者執行緒
    let tx_clone = tx.clone();
    thread::spawn(move || {
        for i in 0..5 {
            let message = format!("訊息 {}", i);
            tx_clone.send(message).unwrap();
            println!("發送: 訊息 {}", i);
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // 另一個發送者
    thread::spawn(move || {
        for i in 5..10 {
            let message = format!("訊息 {}", i);
            tx.send(message).unwrap();
            println!("發送: 訊息 {}", i);
            thread::sleep(Duration::from_millis(150));
        }
    });
    
    // 接收者
    for _ in 0..10 {
        let received = rx.recv().unwrap();
        println!("接收: {}", received);
    }
}
```

### 同步通道範例

```rust
fn sync_channel_example() {
    // 建立同步通道，緩衝區大小為2
    let (tx, rx) = mpsc::sync_channel(2);
    
    let sender = thread::spawn(move || {
        for i in 0..5 {
            println!("準備發送 {}", i);
            match tx.send(i) {
                Ok(_) => println!("成功發送 {}", i),
                Err(e) => println!("發送失敗: {}", e),
            }
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // 接收者故意延遲
    thread::sleep(Duration::from_millis(500));
    
    for received in rx {
        println!("接收: {}", received);
        thread::sleep(Duration::from_millis(200));
    }
    
    sender.join().unwrap();
}
```

### 工作分發系統範例

```rust
fn work_distribution_example() {
    let (job_tx, job_rx) = mpsc::channel();
    let (result_tx, result_rx) = mpsc::channel();
    
    // 工作者執行緒池
    let mut workers = vec![];
    for worker_id in 0..3 {
        let job_rx = job_rx.clone();
        let result_tx = result_tx.clone();
        
        let worker = thread::spawn(move || {
            loop {
                match job_rx.recv() {
                    Ok(job) => {
                        println!("工作者 {} 處理任務: {}", worker_id, job);
                        thread::sleep(Duration::from_millis(500));
                        let result = format!("任務 {} 的結果", job);
                        result_tx.send((worker_id, result)).unwrap();
                    }
                    Err(_) => {
                        println!("工作者 {} 結束", worker_id);
                        break;
                    }
                }
            }
        });
        workers.push(worker);
    }
    
    // 任務分發者
    let job_distributor = thread::spawn(move || {
        for i in 0..10 {
            job_tx.send(i).unwrap();
        }
        drop(job_tx); // 關閉通道
    });
    
    // 結果收集者
    let result_collector = thread::spawn(move || {
        let mut results = vec![];
        for (worker_id, result) in result_rx {
            println!("收到來自工作者 {} 的結果: {}", worker_id, result);
            results.push(result);
            if results.len() == 10 {
                break;
            }
        }
        results
    });
    
    job_distributor.join().unwrap();
    let results = result_collector.join().unwrap();
    
    for worker in workers {
        worker.join().unwrap();
    }
    
    println!("所有結果: {:?}", results);
}
```

### 跨平台高效能 Channel (crossbeam)

```rust
// Cargo.toml: crossbeam = "0.8"
use crossbeam::channel;
use std::thread;
use std::time::{Duration, Instant};

fn crossbeam_channel_example() {
    let (tx, rx) = channel::unbounded();
    let (bounded_tx, bounded_rx) = channel::bounded(10);
    
    // 多個生產者
    let mut producers = vec![];
    for i in 0..3 {
        let tx = tx.clone();
        let producer = thread::spawn(move || {
            for j in 0..5 {
                let message = format!("生產者 {} 的訊息 {}", i, j);
                tx.send(message).unwrap();
                thread::sleep(Duration::from_millis(50));
            }
        });
        producers.push(producer);
    }
    
    // 使用 select! 處理多個通道
    let selector = thread::spawn(move || {
        loop {
            crossbeam::select! {
                recv(rx) -> msg => {
                    match msg {
                        Ok(message) => println!("從無界通道收到: {}", message),
                        Err(_) => break,
                    }
                },
                recv(bounded_rx) -> msg => {
                    match msg {
                        Ok(message) => println!("從有界通道收到: {}", message),
                        Err(_) => {},
                    }
                },
                default(Duration::from_millis(100)) => {
                    println!("等待訊息超時...");
                },
            }
        }
    });
    
    // 向有界通道發送訊息
    thread::spawn(move || {
        for i in 0..3 {
            bounded_tx.send(format!("有界訊息 {}", i)).unwrap();
            thread::sleep(Duration::from_millis(200));
        }
    });
    
    for producer in producers {
        producer.join().unwrap();
    }
    
    drop(tx);
    selector.join().unwrap();
}
```

### Channel 效能測試

```rust
fn channel_performance_test() {
    let message_count = 1_000_000;
    
    // 標準庫 channel
    let start = Instant::now();
    let (tx, rx) = std::sync::mpsc::channel();
    
    let sender = thread::spawn(move || {
        for i in 0..message_count {
            tx.send(i).unwrap();
        }
    });
    
    let receiver = thread::spawn(move || {
        for _ in 0..message_count {
            rx.recv().unwrap();
        }
    });
    
    sender.join().unwrap();
    receiver.join().unwrap();
    let std_time = start.elapsed();
    
    // crossbeam channel
    let start = Instant::now();
    let (tx, rx) = channel::unbounded();
    
    let sender = thread::spawn(move || {
        for i in 0..message_count {
            tx.send(i).unwrap();
        }
    });
    
    let receiver = thread::spawn(move || {
        for _ in 0..message_count {
            rx.recv().unwrap();
        }
    });
    
    sender.join().unwrap();
    receiver.join().unwrap();
    let crossbeam_time = start.elapsed();
    
    println!("標準庫 channel: {:?}", std_time);
    println!("Crossbeam channel: {:?}", crossbeam_time);
    println!("效能比較: {:.2}x", 
        std_time.as_nanos() as f64 / crossbeam_time.as_nanos() as f64);
}
```

### Channel 選擇指南

| 場景 | 推薦類型 | 原因 |
|------|----------|------|
| 🔄 一對一通訊 | `mpsc::channel` | 簡單可靠 |
| 🚀 高效能需求 | `crossbeam::channel` | 更快的實現 |
| 📦 固定緩衝區 | `sync_channel` | 背壓控制 |
| 🎯 選擇性接收 | `crossbeam::select!` | 多通道處理 |
| 🔂 廣播模式 | `crossbeam::channel` + clone | 一對多通訊 |


# Rust 鎖機制指南 - 第三部分：高級同步機制 🚀

## Condvar 條件變數 🚌

**白話解釋**: 像等公車的站牌，只有當公車來了(條件滿足)才上車

```
Condvar 工作流程：
生產者: 🏭 ──▶ [緩衝區] ──▶ 📢 notify()
消費者: 👤💤 ──▶ 🔔收到通知 ──▶ 👤🏃‍♂️ 開始工作
```

### 生產者-消費者範例

```rust
use std::sync::{Arc, Mutex, Condvar};
use std::thread;
use std::time::Duration;
use std::collections::VecDeque;

struct ProducerConsumer<T> {
    buffer: Mutex<VecDeque<T>>,
    not_empty: Condvar,
    not_full: Condvar,
    capacity: usize,
}

impl<T> ProducerConsumer<T> {
    fn new(capacity: usize) -> Self {
        ProducerConsumer {
            buffer: Mutex::new(VecDeque::new()),
            not_empty: Condvar::new(),
            not_full: Condvar::new(),
            capacity,
        }
    }
    
    fn produce(&self, item: T) {
        let mut buffer = self.buffer.lock().unwrap();
        
        // 等待緩衝區有空間
        while buffer.len() >= self.capacity {
            println!("緩衝區滿了，生產者等待...");
            buffer = self.not_full.wait(buffer).unwrap();
        }
        
        buffer.push_back(item);
        println!("生產了一個項目，緩衝區大小: {}", buffer.len());
        
        // 通知消費者
        self.not_empty.notify_one();
    }
    
    fn consume(&self) -> T {
        let mut buffer = self.buffer.lock().unwrap();
        
        // 等待緩衝區有資料
        while buffer.is_empty() {
            println!("緩衝區空了，消費者等待...");
            buffer = self.not_empty.wait(buffer).unwrap();
        }
        
        let item = buffer.pop_front().unwrap();
        println!("消費了一個項目，緩衝區大小: {}", buffer.len());
        
        // 通知生產者
        self.not_full.notify_one();
        
        item
    }
}

fn producer_consumer_example() {
    let pc = Arc::new(ProducerConsumer::new(3)); // 緩衝區大小為3
    
    // 生產者執行緒
    let pc_producer = Arc::clone(&pc);
    let producer = thread::spawn(move || {
        for i in 0..10 {
            let item = format!("項目-{}", i);
            pc_producer.produce(item);
            thread::sleep(Duration::from_millis(100));
        }
        println!("生產者完成");
    });
    
    // 消費者執行緒
    let pc_consumer = Arc::clone(&pc);
    let consumer = thread::spawn(move || {
        for _ in 0..10 {
            let item = pc_consumer.consume();
            println!("收到: {}", item);
            thread::sleep(Duration::from_millis(200)); // 消費比生產慢
        }
        println!("消費者完成");
    });
    
    producer.join().unwrap();
    consumer.join().unwrap();
}
```

### 任務協調範例

```rust
struct TaskCoordinator {
    workers_ready: Mutex<usize>,
    all_ready: Condvar,
    target_count: usize,
}

impl TaskCoordinator {
    fn new(target_count: usize) -> Self {
        TaskCoordinator {
            workers_ready: Mutex::new(0),
            all_ready: Condvar::new(),
            target_count,
        }
    }
    
    fn worker_ready(&self, worker_id: usize) {
        let mut count = self.workers_ready.lock().unwrap();
        *count += 1;
        
        println!("工作者 {} 準備就緒 ({}/{})", worker_id, *count, self.target_count);
        
        if *count >= self.target_count {
            println!("所有工作者準備就緒，開始任務！");
            self.all_ready.notify_all();
        } else {
            // 等待其他工作者
            while *count < self.target_count {
                println!("工作者 {} 等待其他工作者...", worker_id);
                count = self.all_ready.wait(count).unwrap();
            }
        }
    }
}

fn task_coordination_example() {
    let coordinator = Arc::new(TaskCoordinator::new(3));
    let mut handles = vec![];
    
    for i in 0..3 {
        let coordinator = Arc::clone(&coordinator);
        let handle = thread::spawn(move || {
            // 模擬準備時間
            thread::sleep(Duration::from_millis((i + 1) * 500));
            
            // 報告準備就緒並等待開始信號
            coordinator.worker_ready(i);
            
            // 開始執行任務
            println!("工作者 {} 開始執行任務", i);
            thread::sleep(Duration::from_secs(2));
            println!("工作者 {} 完成任務", i);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}
```

### 超時等待範例

```rust
fn timeout_example() {
    let pair = Arc::new((Mutex::new(false), Condvar::new()));
    let pair_clone = Arc::clone(&pair);
    
    // 等待執行緒
    let waiter = thread::spawn(move || {
        let (lock, cvar) = &*pair_clone;
        let mut started = lock.lock().unwrap();
        
        // 等待條件滿足，最多等待2秒
        let result = cvar.wait_timeout_while(
            started,
            Duration::from_secs(2),
            |&mut pending| !pending,
        ).unwrap();
        
        if result.1.timed_out() {
            println!("等待超時！");
        } else {
            println!("條件滿足！");
        }
    });
    
    // 主執行緒等待3秒後設定條件
    thread::sleep(Duration::from_secs(3));
    
    let (lock, cvar) = &*pair;
    let mut started = lock.lock().unwrap();
    *started = true;
    cvar.notify_one();
    
    waiter.join().unwrap();
}
```

---

## Rc<RefCell<T>> 單執行緒共享 🏠

**白話解釋**: 像家裡的共用冰箱，只有一個家庭(執行緒)使用，但可以有多個使用者

```
Rc<RefCell<T>> 設計圖：
Reference Counting (Rc):
Owner1: 📎 ──┐
Owner2: 📎 ──┼──▶ 📦 RefCell<T>
Owner3: 📎 ──┘

Runtime Borrow Checking:
Immutable: 👀👀👀 (多個不可變借用)
Mutable:   ✍️     (一個可變借用)
Panic:     👀✍️   (同時存在會panic!)
```

### 樹狀結構範例

```rust
use std::rc::Rc;
use std::cell::RefCell;

#[derive(Debug)]
struct Node {
    value: i32,
    children: Vec<Rc<RefCell<Node>>>,
    parent: Option<Rc<RefCell<Node>>>,
}

impl Node {
    fn new(value: i32) -> Rc<RefCell<Self>> {
        Rc::new(RefCell::new(Node {
            value,
            children: Vec::new(),
            parent: None,
        }))
    }
    
    fn add_child(parent: &Rc<RefCell<Node>>, child: &Rc<RefCell<Node>>) {
        // 借用父節點並添加子節點
        parent.borrow_mut().children.push(Rc::clone(child));
        
        // 設定子節點的父節點引用
        child.borrow_mut().parent = Some(Rc::clone(parent));
    }
    
    fn print_tree(node: &Rc<RefCell<Node>>, depth: usize) {
        let indent = "  ".repeat(depth);
        let borrowed = node.borrow();
        println!("{}Node: {}", indent, borrowed.value);
        
        for child in &borrowed.children {
            Node::print_tree(child, depth + 1);
        }
    }
    
    fn update_value(node: &Rc<RefCell<Node>>, new_value: i32) {
        node.borrow_mut().value = new_value;
    }
}

fn tree_example() {
    // 建立樹狀結構
    let root = Node::new(1);
    let child1 = Node::new(2);
    let child2 = Node::new(3);
    let grandchild = Node::new(4);
    
    // 建立父子關係
    Node::add_child(&root, &child1);
    Node::add_child(&root, &child2);
    Node::add_child(&child1, &grandchild);
    
    println!("原始樹狀結構:");
    Node::print_tree(&root, 0);
    
    // 修改節點值
    Node::update_value(&grandchild, 42);
    
    println!("\n修改後的樹狀結構:");
    Node::print_tree(&root, 0);
}
```

### 遊戲狀態管理範例

```rust
#[derive(Debug)]
struct GameState {
    score: i32,
    level: i32,
    lives: i32,
}

impl GameState {
    fn new() -> Self {
        GameState {
            score: 0,
            level: 1,
            lives: 3,
        }
    }
    
    fn add_score(&mut self, points: i32) {
        self.score += points;
        if self.score >= self.level * 1000 {
            self.level_up();
        }
    }
    
    fn level_up(&mut self) {
        self.level += 1;
        self.lives += 1;
        println!("升級！等級: {}, 生命: {}", self.level, self.lives);
    }
    
    fn lose_life(&mut self) {
        self.lives -= 1;
        println!("失去生命！剩餘: {}", self.lives);
    }
}

struct Player {
    name: String,
    game_state: Rc<RefCell<GameState>>,
}

impl Player {
    fn new(name: String, game_state: Rc<RefCell<GameState>>) -> Self {
        Player { name, game_state }
    }
    
    fn score_points(&self, points: i32) {
        println!("{} 獲得 {} 分", self.name, points);
        self.game_state.borrow_mut().add_score(points);
    }
    
    fn take_damage(&self) {
        println!("{} 受到傷害", self.name);
        self.game_state.borrow_mut().lose_life();
    }
    
    fn show_status(&self) {
        let state = self.game_state.borrow();
        println!("{} - 分數: {}, 等級: {}, 生命: {}", 
            self.name, state.score, state.level, state.lives);
    }
}

fn game_state_example() {
    let game_state = Rc::new(RefCell::new(GameState::new()));
    
    // 多個玩家共享遊戲狀態
    let player1 = Player::new("玩家1".to_string(), Rc::clone(&game_state));
    let player2 = Player::new("玩家2".to_string(), Rc::clone(&game_state));
    
    // 遊戲過程
    player1.score_points(500);
    player1.show_status();
    
    player2.score_points(300);
    player2.show_status();
    
    player1.score_points(700); // 應該升級
    player1.show_status();
    
    player2.take_damage();
    player2.show_status();
}
```

### 借用檢查錯誤處理

```rust
fn borrowing_safety_example() {
    let data = Rc::new(RefCell::new(vec![1, 2, 3]));
    
    // ✅ 正確的使用方式
    {
        let borrowed = data.borrow();
        println!("不可變借用: {:?}", *borrowed);
    } // borrowed 在這裡被釋放
    
    {
        let mut borrowed = data.borrow_mut();
        borrowed.push(4);
        println!("可變借用後: {:?}", *borrowed);
    } // borrowed 在這裡被釋放
    
    // ✅ 安全的檢查方式
    if let Ok(borrowed) = data.try_borrow() {
        println!("安全借用: {:?}", *borrowed);
    } else {
        println!("無法借用，已被其他人使用");
    }
    
    // ❌ 這會在運行時 panic！
    // let borrowed1 = data.borrow();
    // let borrowed2 = data.borrow_mut(); // panic: already borrowed
}

// 安全的借用包裝器
fn safe_borrow_pattern() {
    let data = Rc::new(RefCell::new(0));
    
    // 使用函數包裝器避免長時間借用
    fn with_data<F, R>(data: &Rc<RefCell<i32>>, f: F) -> Option<R>
    where
        F: FnOnce(&mut i32) -> R,
    {
        if let Ok(mut guard) = data.try_borrow_mut() {
            Some(f(&mut guard))
        } else {
            None
        }
    }
    
    if let Some(result) = with_data(&data, |value| {
        *value += 1;
        *value
    }) {
        println!("操作成功，新值: {}", result);
    } else {
        println!("操作失敗，資源被借用中");
    }
}
```

### Weak 引用避免循環引用

```rust
use std::rc::Weak;

#[derive(Debug)]
struct Parent {
    children: RefCell<Vec<Rc<RefCell<Child>>>>,
}

#[derive(Debug)]
struct Child {
    parent: RefCell<Weak<RefCell<Parent>>>,
    value: i32,
}

impl Parent {
    fn new() -> Rc<RefCell<Self>> {
        Rc::new(RefCell::new(Parent {
            children: RefCell::new(Vec::new()),
        }))
    }
    
    fn add_child(parent: &Rc<RefCell<Parent>>, value: i32) -> Rc<RefCell<Child>> {
        let child = Rc::new(RefCell::new(Child {
            parent: RefCell::new(Rc::downgrade(parent)),
            value,
        }));
        
        parent.borrow().children.borrow_mut().push(Rc::clone(&child));
        child
    }
}

fn weak_reference_example() {
    let parent = Parent::new();
    let child1 = Parent::add_child(&parent, 1);
    let child2 = Parent::add_child(&parent, 2);
    
    println!("父節點有 {} 個子節點", 
        parent.borrow().children.borrow().len());
    
    // 通過 weak 引用訪問父節點
    if let Some(parent_ref) = child1.borrow().parent.borrow().upgrade() {
        println!("子節點可以訪問父節點");
    }
    
    // 當父節點被丟棄時，weak 引用會失效
    drop(parent);
    
    if child1.borrow().parent.borrow().upgrade().is_none() {
        println!("父節點已被丟棄，weak 引用失效");
    }
}
```

### 使用場景總結

| 場景 | 適用性 | 原因 |
|------|--------|------|
| 🌳 **樹狀結構** | ✅ 很適合 | 需要父子雙向引用 |
| 🎮 **單執行緒遊戲狀態** | ✅ 適合 | 多個系統共享狀態 |
| 🖼️ **GUI 元件** | ✅ 適合 | 元件間複雜引用關係 |
| 📊 **單執行緒圖結構** | ✅ 適合 | 節點間相互引用 |
| 🌐 **多執行緒場景** | ❌ 不適合 | 無法跨執行緒共享 |
| 🔄 **簡單資料** | ❌ 不推薦 | 過度複雜化 |



# Rust 鎖機制指南 - 第四部分：實戰應用與最佳實踐 🎯

## 高級並行模式 🚀

### Actor 模式實現

```rust
use std::sync::mpsc;
use std::thread;
use std::collections::HashMap;

// Actor 訊息定義
#[derive(Debug)]
enum Message {
    Set { key: String, value: String },
    Get { key: String, response: mpsc::Sender<Option<String>> },
    Delete { key: String },
    Stop,
}

// Key-Value Actor
struct KeyValueActor {
    receiver: mpsc::Receiver<Message>,
    data: HashMap<String, String>,
}

impl KeyValueActor {
    fn new() -> (mpsc::Sender<Message>, thread::JoinHandle<()>) {
        let (sender, receiver) = mpsc::channel();
        
        let handle = thread::spawn(move || {
            let mut actor = KeyValueActor {
                receiver,
                data: HashMap::new(),
            };
            actor.run();
        });
        
        (sender, handle)
    }
    
    fn run(&mut self) {
        loop {
            match self.receiver.recv() {
                Ok(Message::Set { key, value }) => {
                    println!("Actor: 設定 {} = {}", key, value);
                    self.data.insert(key, value);
                }
                Ok(Message::Get { key, response }) => {
                    let value = self.data.get(&key).cloned();
                    println!("Actor: 查詢 {} = {:?}", key, value);
                    let _ = response.send(value);
                }
                Ok(Message::Delete { key }) => {
                    let removed = self.data.remove(&key);
                    println!("Actor: 刪除 {} = {:?}", key, removed);
                }
                Ok(Message::Stop) => {
                    println!("Actor: 停止運行");
                    break;
                }
                Err(_) => {
                    println!("Actor: 發送端已關閉，退出");
                    break;
                }
            }
        }
    }
}

fn actor_pattern_example() {
    let (actor_sender, actor_handle) = KeyValueActor::new();
    
    // 多個客戶端執行緒
    let mut clients = vec![];
    
    for i in 0..3 {
        let sender = actor_sender.clone();
        let client = thread::spawn(move || {
            // 設定值
            sender.send(Message::Set {
                key: format!("key{}", i),
                value: format!("value{}", i),
            }).unwrap();
            
            // 查詢值
            let (response_tx, response_rx) = mpsc::channel();
            sender.send(Message::Get {
                key: format!("key{}", i),
                response: response_tx,
            }).unwrap();
            
            if let Ok(value) = response_rx.recv() {
                println!("客戶端 {} 收到回應: {:?}", i, value);
            }
            
            // 刪除值
            sender.send(Message::Delete {
                key: format!("key{}", i),
            }).unwrap();
        });
        clients.push(client);
    }
    
    // 等待所有客戶端完成
    for client in clients {
        client.join().unwrap();
    }
    
    // 停止 Actor
    actor_sender.send(Message::Stop).unwrap();
    actor_handle.join().unwrap();
}
```

### 執行緒池實現

```rust
use std::sync::{Arc, Mutex};
use std::sync::mpsc;
use std::thread;

type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: mpsc::Sender<Job>,
}

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);
        
        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));
        
        let mut workers = Vec::with_capacity(size);
        
        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }
        
        ThreadPool { workers, sender }
    }
    
    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);
        self.sender.send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        println!("關閉所有工作者...");
        
        for worker in &mut self.workers {
            println!("關閉工作者 {}", worker.id);
            
            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || loop {
            let job = receiver.lock().unwrap().recv();
            
            match job {
                Ok(job) => {
                    println!("工作者 {} 執行任務", id);
                    job();
                }
                Err(_) => {
                    println!("工作者 {} 斷開連接，關閉", id);
                    break;
                }
            }
        });
        
        Worker {
            id,
            thread: Some(thread),
        }
    }
}

fn thread_pool_example() {
    let pool = ThreadPool::new(4);
    
    for i in 0..8 {
        pool.execute(move || {
            println!("執行任務 {}", i);
            thread::sleep(std::time::Duration::from_secs(1));
            println!("任務 {} 完成", i);
        });
    }
    
    println!("所有任務已提交");
}
```

### 效能監控系統

```rust
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use std::thread;

#[derive(Debug)]
struct LockMetrics {
    acquisitions: AtomicU64,
    contentions: AtomicU64,
    total_wait_time: AtomicU64,
    max_wait_time: AtomicU64,
}

impl LockMetrics {
    fn new() -> Self {
        LockMetrics {
            acquisitions: AtomicU64::new(0),
            contentions: AtomicU64::new(0),
            total_wait_time: AtomicU64::new(0),
            max_wait_time: AtomicU64::new(0),
        }
    }
    
    fn record_acquisition(&self, wait_time: Duration, contended: bool) {
        self.acquisitions.fetch_add(1, Ordering::Relaxed);
        
        if contended {
            self.contentions.fetch_add(1, Ordering::Relaxed);
        }
        
        let wait_nanos = wait_time.as_nanos() as u64;
        self.total_wait_time.fetch_add(wait_nanos, Ordering::Relaxed);
        
        // 更新最大等待時間
        let mut current_max = self.max_wait_time.load(Ordering::Relaxed);
        while wait_nanos > current_max {
            match self.max_wait_time.compare_exchange_weak(
                current_max,
                wait_nanos,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(x) => current_max = x,
            }
        }
    }
    
    fn report(&self) {
        let acquisitions = self.acquisitions.load(Ordering::Relaxed);
        let contentions = self.contentions.load(Ordering::Relaxed);
        let total_wait = self.total_wait_time.load(Ordering::Relaxed);
        let max_wait = self.max_wait_time.load(Ordering::Relaxed);
        
        if acquisitions > 0 {
            let contention_rate = (contentions as f64 / acquisitions as f64) * 100.0;
            let avg_wait = total_wait as f64 / acquisitions as f64;
            
            println!("🔒 鎖統計報告:");
            println!("  總獲取次數: {}", acquisitions);
            println!("  競爭次數: {}", contentions);
            println!("  競爭率: {:.2}%", contention_rate);
            println!("  平均等待時間: {:.2}ns", avg_wait);
            println!("  最大等待時間: {}ns", max_wait);
        }
    }
}

// 監控包裝器
struct MonitoredMutex<T> {
    inner: Mutex<T>,
    metrics: LockMetrics,
}

impl<T> MonitoredMutex<T> {
    fn new(data: T) -> Self {
        MonitoredMutex {
            inner: Mutex::new(data),
            metrics: LockMetrics::new(),
        }
    }
    
    fn lock(&self) -> std::sync::MutexGuard<T> {
        let start = Instant::now();
        let guard = self.inner.lock().unwrap();
        let wait_time = start.elapsed();
        
        // 判斷是否有競爭 (簡單的啟發式方法)
        let contended = wait_time > Duration::from_nanos(1000);
        self.metrics.record_acquisition(wait_time, contended);
        
        guard
    }
    
    fn metrics(&self) -> &LockMetrics {
        &self.metrics
    }
}

fn performance_monitoring_example() {
    let counter = Arc::new(MonitoredMutex::new(0));
    let mut handles = vec![];
    
    // 建立多個競爭執行緒
    for i in 0..4 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for j in 0..1000 {
                {
                    let mut guard = counter.lock();
                    *guard += 1;
                    
                    // 模擬一些工作
                    if j % 100 == 0 {
                        thread::sleep(Duration::from_micros(10));
                    }
                }
                
                // 偶爾讓出CPU
                if j % 50 == 0 {
                    thread::yield_now();
                }
            }
            println!("執行緒 {} 完成", i);
        });
        handles.push(handle);
    }
    
    // 監控執行緒
    let counter_monitor = Arc::clone(&counter);
    let monitor = thread::spawn(move || {
        for _ in 0..5 {
            thread::sleep(Duration::from_secs(1));
            counter_monitor.metrics().report();
        }
    });
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    monitor.join().unwrap();
    
    println!("最終計數: {}", *counter.lock());
    println!("\n最終統計:");
    counter.metrics().report();
}
```

### 死鎖檢測系統

```rust
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread::{self, ThreadId};
use std::time::Duration;

struct DeadlockDetector {
    // 記錄哪個執行緒持有哪些鎖
    lock_owners: Arc<Mutex<HashMap<String, ThreadId>>>,
    // 記錄執行緒等待哪些鎖
    waiting_for: Arc<Mutex<HashMap<ThreadId, String>>>,
}

impl DeadlockDetector {
    fn new() -> Self {
        DeadlockDetector {
            lock_owners: Arc::new(Mutex::new(HashMap::new())),
            waiting_for: Arc::new(Mutex::new(HashMap::new())),
        }
    }
    
    fn try_acquire_lock(&self, lock_id: &str) -> bool {
        let current_thread = thread::current().id();
        
        // 檢查鎖是否被其他執行緒持有
        let mut owners = self.lock_owners.lock().unwrap();
        
        if let Some(&owner) = owners.get(lock_id) {
            if owner != current_thread {
                // 記錄等待關係
                drop(owners);
                let mut waiting = self.waiting_for.lock().unwrap();
                waiting.insert(current_thread, lock_id.to_string());
                drop(waiting);
                
                // 檢查死鎖
                if self.detect_deadlock(current_thread) {
                    println!("⚠️ 檢測到死鎖！執行緒 {:?} 等待鎖 {}", current_thread, lock_id);
                    return false;
                }
                
                println!("執行緒 {:?} 等待鎖 {}", current_thread, lock_id);
                return false;
            }
        }
        
        // 獲取鎖
        owners.insert(lock_id.to_string(), current_thread);
        println!("🔒 執行緒 {:?} 獲取鎖 {}", current_thread, lock_id);
        
        // 清除等待記錄
        drop(owners);
        let mut waiting = self.waiting_for.lock().unwrap();
        waiting.remove(&current_thread);
        
        true
    }
    
    fn release_lock(&self, lock_id: &str) {
        let current_thread = thread::current().id();
        let mut owners = self.lock_owners.lock().unwrap();
        
        if owners.get(lock_id) == Some(&current_thread) {
            owners.remove(lock_id);
            println!("🔓 執行緒 {:?} 釋放鎖 {}", current_thread, lock_id);
        }
    }
    
    fn detect_deadlock(&self, start_thread: ThreadId) -> bool {
        let waiting = self.waiting_for.lock().unwrap();
        let owners = self.lock_owners.lock().unwrap();
        
        let mut visited = std::collections::HashSet::new();
        let mut current_thread = start_thread;
        
        loop {
            if visited.contains(&current_thread) {
                return true; // 發現環，即死鎖
            }
            
            visited.insert(current_thread);
            
            // 找到當前執行緒等待的鎖
            if let Some(waiting_lock) = waiting.get(&current_thread) {
                // 找到持有該鎖的執行緒
                if let Some(&lock_owner) = owners.get(waiting_lock) {
                    if lock_owner == start_thread {
                        return true; // 回到起始執行緒，發現死鎖
                    }
                    current_thread = lock_owner;
                } else {
                    break; // 鎖沒有被持有
                }
            } else {
                break; // 執行緒沒有等待任何鎖
            }
        }
        
        false
    }
}

// 有序鎖包裝器
struct OrderedLock {
    id: String,
    inner: Mutex<i32>,
    detector: Arc<DeadlockDetector>,
}

impl OrderedLock {
    fn new(id: String, detector: Arc<DeadlockDetector>) -> Self {
        OrderedLock {
            id,
            inner: Mutex::new(0),
            detector,
        }
    }
    
    fn lock(&self) -> Option<std::sync::MutexGuard<i32>> {
        // 嘗試獲取鎖
        while !self.detector.try_acquire_lock(&self.id) {
            thread::sleep(Duration::from_millis(10));
        }
        
        Some(self.inner.lock().unwrap())
    }
    
    fn unlock(&self) {
        self.detector.release_lock(&self.id);
    }
}

fn deadlock_detection_example() {
    let detector = Arc::new(DeadlockDetector::new());
    
    let lock1 = Arc::new(OrderedLock::new("lock1".to_string(), Arc::clone(&detector)));
    let lock2 = Arc::new(OrderedLock::new("lock2".to_string(), Arc::clone(&detector)));
    
    let lock1_clone = Arc::clone(&lock1);
    let lock2_clone = Arc::clone(&lock2);
    
    // 執行緒1: 先鎖lock1，再鎖lock2
    let t1 = thread::spawn(move || {
        if let Some(_guard1) = lock1_clone.lock() {
            println!("執行緒1獲得lock1");
            thread::sleep(Duration::from_millis(100));
            
            if let Some(_guard2) = lock2_clone.lock() {
                println!("執行緒1獲得lock2");
                thread::sleep(Duration::from_millis(100));
                lock2_clone.unlock();
            }
            lock1_clone.unlock();
        }
    });
    
    let lock1_clone2 = Arc::clone(&lock1);
    let lock2_clone2 = Arc::clone(&lock2);
    
    // 執行緒2: 先鎖lock2，再鎖lock1 (可能造成死鎖)
    let t2 = thread::spawn(move || {
        thread::sleep(Duration::from_millis(50)); // 錯開啟動時間
        
        if let Some(_guard2) = lock2_clone2.lock() {
            println!("執行緒2獲得lock2");
            thread::sleep(Duration::from_millis(100));
            
            if let Some(_guard1) = lock1_clone2.lock() {
                println!("執行緒2獲得lock1");
                thread::sleep(Duration::from_millis(100));
                lock1_clone2.unlock();
            }
            lock2_clone2.unlock();
        }
    });
    
    t1.join().unwrap();
    t2.join().unwrap();
}
```

---

## 選擇指南與最佳實踐 🎯

### 完整選擇決策樹

```rust
// 決策輔助函數
fn choose_synchronization_primitive() -> &'static str {
    // 這是一個概念性的決策樹
    "
    選擇流程：
    
    1. 需要共享資料嗎？
       └─ 否 → 使用所有權轉移 (move)
       └─ 是 → 繼續
    
    2. 單執行緒還是多執行緒？
       └─ 單執行緒 → Rc<RefCell<T>>
       └─ 多執行緒 → 繼續
    
    3. 什麼類型的操作？
       ├─ 簡單計數/標誌 → Atomic 類型
       ├─ 複雜資料結構 → 繼續
       └─ 執行緒間通訊 → Channel
    
    4. 讀寫模式？
       ├─ 多讀少寫 → Arc<RwLock<T>>
       └─ 讀寫平衡 → Arc<Mutex<T>>
    
    5. 需要等待條件？
       └─ 是 → Condvar + Mutex
    "
}
```

### 效能對比表

| 同步原語 | 延遲 | 吞吐量 | 記憶體使用 | 複雜度 | 適用場景 |
|----------|------|--------|------------|--------|----------|
| `Atomic` | 🟢 極低 | 🟢 極高 | 🟢 極小 | 🟢 簡單 | 計數器、標誌 |
| `Arc<RwLock>` (讀) | 🟢 低 | 🟢 高 | 🟡 中等 | 🟡 中等 | 設定檔、快取 |
| `Channel` | 🟡 中等 | 🟡 中等 | 🟡 中等 | 🟢 簡單 | 執行緒通訊 |
| `Arc<Mutex>` | 🟡 中等 | 🟡 中等 | 🟡 中等 | 🟢 簡單 | 基本共享 |
| `Condvar` | 🔴 高 | 🔴 低 | 🟡 中等 | 🔴 複雜 | 條件等待 |
| `Rc<RefCell>` | 🟢 低 | 🟢 高 | 🟢 小 | 🟡 中等 | 單執行緒共享 |

### 最佳實踐指南

#### 1. 所有權驅動設計

```rust
// ✅ 好的設計：清晰的所有權
fn good_ownership_design() {
    let data = vec![1, 2, 3, 4, 5];
    
    // 移動所有權給工作執行緒
    let handle = thread::spawn(move || {
        let processed: Vec<_> = data.iter().map(|x| x * 2).collect();
        processed
    });
    
    let result = handle.join().unwrap();
    println!("處理結果: {:?}", result);
}

// ❌ 避免的模式：不必要的共享
fn avoid_unnecessary_sharing() {
    let data = Arc::new(Mutex::new(vec![1, 2, 3, 4, 5]));
    
    // 如果只是為了傳遞資料，不如直接移動所有權
    let data_clone = Arc::clone(&data);
    thread::spawn(move || {
        let guard = data_clone.lock().unwrap();
        println!("資料: {:?}", *guard);
    });
}
```

#### 2. 鎖的粒度控制

```rust
// ✅ 細粒度鎖：更好的並行性
struct FinegrainedCache {
    user_cache: Arc<RwLock<HashMap<u64, User>>>,
    session_cache: Arc<RwLock<HashMap<String, Session>>>,
    config: Arc<RwLock<Config>>,
}

// ❌ 粗粒度鎖：限制並行性
struct CoarseGrainedCache {
    data: Arc<Mutex<(HashMap<u64, User>, HashMap<String, Session>, Config)>>,
}

#[derive(Clone)]
struct User { name: String }
#[derive(Clone)]
struct Session { token: String }
#[derive(Clone)]
struct Config { setting: String }
```

#### 3. 錯誤處理最佳實踐

```rust
use std::sync::PoisonError;

// 強健的錯誤處理
fn robust_operation<T, R>(
    mutex: &Arc<Mutex<T>>,
    operation: impl FnOnce(&mut T) -> R,
) -> Result<R, String> {
    match mutex.lock() {
        Ok(mut guard) => Ok(operation(&mut guard)),
        Err(poisoned) => {
            // 記錄毒化事件
            eprintln!("警告: Mutex 被毒化，嘗試恢復操作");
            
            // 嘗試恢復
            let mut guard = poisoned.into_inner();
            Ok(operation(&mut guard))
        }
    }
}

// 使用範例
fn safe_counter_increment() {
    let counter = Arc::new(Mutex::new(0));
    
    match robust_operation(&counter, |count| {
        *count += 1;
        *count
    }) {
        Ok(new_value) => println!("計數器值: {}", new_value),
        Err(e) => eprintln!("操作失敗: {}", e),
    }
}
```

#### 4. Channel 使用模式

```rust
// 優雅關閉模式
fn graceful_shutdown_pattern() {
    let (tx, rx) = mpsc::channel();
    let (shutdown_tx, shutdown_rx) = mpsc::channel();
    
    // 工作執行緒
    let worker = thread::spawn(move || {
        loop {
            select! {
                recv(rx) -> msg => {
                    match msg {
                        Ok(work) => process_work(work),
                        Err(_) => break, // 通道關閉
                    }
                }
                recv(shutdown_rx) -> _ => {
                    println!("收到關閉信號");
                    break;
                }
                default(Duration::from_millis(100)) => {
                    // 定期維護工作
                    maintenance_work();
                }
            }
        }
        println!("工作執行緒優雅退出");
    });
    
    // 發送一些工作
    for i in 0..5 {
        tx.send(i).unwrap();
    }
    
    // 優雅關閉
    shutdown_tx.send(()).unwrap();
    worker.join().unwrap();
}

fn process_work(work: i32) {
    println!("處理工作: {}", work);
}

fn maintenance_work() {
    // 定期維護
}

// 需要引入 crossbeam 的 select! 巨集
use crossbeam::select;
```

#### 5. 記憶體順序指南

```rust
use std::sync::atomic::{AtomicBool, AtomicI32, Ordering};

// 生產者-消費者的最佳化記憶體順序
static DATA: AtomicI32 = AtomicI32::new(0);
static READY: AtomicBool = AtomicBool::new(false);

fn optimized_memory_ordering() {
    // 生產者
    thread::spawn(|| {
        // 1. 寫入資料 (可以是 Relaxed)
        DATA.store(42, Ordering::Relaxed);
        
        // 2. 發布準備標誌 (必須是 Release)
        READY.store(true, Ordering::Release);
        
        println!("生產者: 資料已準備");
    });
    
    // 消費者
    thread::spawn(|| {
        // 1. 等待準備標誌 (必須是 Acquire)
        while !READY.load(Ordering::Acquire) {
            std::hint::spin_loop();
        }
        
        // 2. 讀取資料 (可以是 Relaxed)
        let value = DATA.load(Ordering::Relaxed);
        println!("消費者: 讀取到 {}", value);
    });
}
```

### 除錯與診斷技巧

#### 1. 死鎖診斷

```rust
// 使用 parking_lot 的死鎖檢測
#[cfg(feature = "deadlock_detection")]
fn enable_deadlock_detection() {
    use parking_lot::deadlock;
    use std::time::Duration;
    
    thread::spawn(move || {
        loop {
            thread::sleep(Duration::from_secs(10));
            let deadlocks = deadlock::check_deadlock();
            
            if deadlocks.is_empty() {
                continue;
            }
            
            println!("🚨 檢測到 {} 個死鎖", deadlocks.len());
            for (i, threads) in deadlocks.iter().enumerate() {
                println!("死鎖 #{}", i);
                for t in threads {
                    println!("  執行緒 ID: {:?}", t.thread_id());
                    println!("  堆疊追蹤: {:#?}", t.backtrace());
                }
            }
        }
    });
}
```

#### 2. 效能分析工具

```rust
// 自訂效能分析器
struct PerformanceProfiler {
    start_time: Instant,
    operations: AtomicUsize,
}

impl PerformanceProfiler {
    fn new() -> Self {
        PerformanceProfiler {
            start_time: Instant::now(),
            operations: AtomicUsize::new(0),
        }
    }
    
    fn record_operation(&self) {
        self.operations.fetch_add(1, Ordering::Relaxed);
    }
    
    fn report(&self) {
        let elapsed = self.start_time.elapsed();
        let ops = self.operations.load(Ordering::Relaxed);
        let ops_per_sec = ops as f64 / elapsed.as_secs_f64();
        
        println!("📊 效能報告:");
        println!("  執行時間: {:?}", elapsed);
        println!("  總操作數: {}", ops);
        println!("  每秒操作數: {:.2}", ops_per_sec);
    }
}
```

---

## 學習路徑與總結 🎓

### 學習路徑建議

```
🌱 初學者 (0-3個月):
├── 理解所有權系統
├── 掌握 Arc<Mutex<T>>
├── 學習基本 Channel
└── 實作簡單併發程式

🚀 中級者 (3-6個月):
├── 深入 RwLock 和 Atomic
├── 掌握 Condvar 使用
├── 學習效能最佳化
└── 實作複雜併發系統

🎯 高級者 (6個月以上):
├── 無鎖程式設計
├── 自訂同步原語
├── 記憶體順序深度理解
└── 高效能系統設計
```

### 總結要點

**✨ Rust 並行編程的獨特優勢:**
- 🛡️ **編譯時安全** - 防止資料競爭
- ⚡ **零成本抽象** - 高效能不犧牲安全
- 🎯 **所有權清晰** - 明確的資源管理
- 🔧 **豐富工具** - 從基礎到高級的完整工具鏈

**🎯 核心設計原則:**
1. **優先訊息傳遞** - Channel 勝過共享記憶體
2. **最小化共享** - 只在必要時使用 Arc
3. **明確所有權** - 讓類型系統指導設計
4. **測試驅動** - 併發程式的正確性至關重要

**🚀 實踐建議:**
- 從簡單的 Arc<Mutex<T>> 開始學習
- 重視編譯器的錯誤訊息和建議
- 使用效能分析工具監控程式行為
- 積極使用 Rust 社群的最佳實踐

記住 Rust 的核心理念：**如果程式能夠編譯通過，它很可能就是正確的並行程式** 🦀✨

---

*完整指南到此結束。通過這四個部分，您已經掌握了 Rust 並行程式設計的完整知識體系！*
