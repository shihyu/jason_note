# Rust 高頻交易開發技術指南

## 目錄
- [Rust vs C++ 在 HFT 中的對比](#rust-vs-c-在-hft-中的對比)
- [Rust 的語言優勢](#rust-的語言優勢)
- [零拷貝通信實現](#零拷貝通信實現)
- [SIMD 優化策略](#simd-優化策略)
- [記憶體管理與優化](#記憶體管理與優化)
- [並發模型](#並發模型)
- [實戰範例](#實戰範例)

## Rust vs C++ 在 HFT 中的對比

### 相同之處
| 特性 | 說明 |
|-----|------|
| **零成本抽象** | 兩者都提供編譯時優化，運行時無額外開銷 |
| **手動記憶體管理** | 精確控制記憶體分配和釋放 |
| **內聯優化** | 積極的函數內聯 |
| **LLVM 後端** | Rust 使用 LLVM，可獲得類似優化 |
| **系統調用** | 同樣可以直接使用 OS 級別的零拷貝 API |

### 關鍵差異
| 方面 | C++ | Rust |
|------|-----|------|
| **記憶體安全** | 需要手動管理，容易出錯 | 編譯時保證，無 data race |
| **生命週期** | 隱式管理 | 顯式生命週期標註 |
| **錯誤處理** | 異常或錯誤碼 | `Result<T, E>` 類型 |
| **並發模型** | 需要小心處理共享狀態 | `Send`/`Sync` trait 保證安全 |
| **編譯速度** | 較快 | 較慢（但程式更安全） |

## Rust 的語言優勢

### 1. 所有權系統帶來的優化

```rust
// Rust 的所有權系統允許編譯器進行更激進的優化
fn process_data(mut data: Vec<f64>) -> Vec<f64> {
    // 編譯器知道 data 是唯一擁有者，可以直接修改
    // 不需要擔心別名問題
    data.iter_mut().for_each(|x| *x *= 2.0);
    data  // 移動語義，零拷貝返回
}
```

### 2. 無畏並發（Fearless Concurrency）

```rust
use std::sync::Arc;
use crossbeam::channel;

// 編譯時保證線程安全
fn parallel_processing<T: Send + Sync + 'static>(data: Arc<T>) {
    // Send trait 保證可以安全地在線程間傳遞
    // Sync trait 保證可以安全地在線程間共享引用
    std::thread::spawn(move || {
        // 使用 data，編譯器保證安全
    });
}
```

## 零拷貝通信實現

### 1. 共享記憶體映射

```rust
use memmap2::{MmapMut, MmapOptions};
use std::fs::OpenOptions;
use std::os::unix::io::AsRawFd;

pub struct SharedMemoryBuffer {
    mmap: MmapMut,
    size: usize,
}

impl SharedMemoryBuffer {
    pub fn create(path: &str, size: usize) -> std::io::Result<Self> {
        // 創建共享記憶體文件
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(path)?;
        
        file.set_len(size as u64)?;
        
        // 內存映射 - 零拷貝的關鍵
        let mut mmap = unsafe { 
            MmapOptions::new()
                .len(size)
                .map_mut(&file)? 
        };
        
        // 鎖定內存，防止交換
        mmap.lock()?;
        
        Ok(Self { mmap, size })
    }
    
    // 零拷貝寫入
    pub fn write_at<T>(&mut self, offset: usize, data: &T) 
    where T: Copy {
        unsafe {
            let ptr = self.mmap.as_mut_ptr().add(offset) as *mut T;
            ptr.write_volatile(*data);
        }
    }
    
    // 零拷貝讀取
    pub fn read_at<T>(&self, offset: usize) -> T 
    where T: Copy {
        unsafe {
            let ptr = self.mmap.as_ptr().add(offset) as *const T;
            ptr.read_volatile()
        }
    }
}
```

### 2. Linux 特定零拷貝 API

```rust
use nix::sys::sendfile;
use nix::fcntl::{splice, SpliceFFlags};
use std::os::unix::io::RawFd;

pub struct ZeroCopyTransfer;

impl ZeroCopyTransfer {
    // 使用 sendfile 零拷貝傳輸
    pub fn sendfile_transfer(
        out_fd: RawFd,
        in_fd: RawFd,
        count: usize
    ) -> nix::Result<usize> {
        sendfile::sendfile(out_fd, in_fd, None, count)
    }
    
    // 使用 splice 在管道間移動數據
    pub fn splice_transfer(
        fd_in: RawFd,
        fd_out: RawFd,
        len: usize
    ) -> nix::Result<usize> {
        splice(
            fd_in,
            None,
            fd_out,
            None,
            len,
            SpliceFFlags::SPLICE_F_MOVE
        )
    }
}
```

### 3. 高性能環形緩衝區

```rust
use std::sync::atomic::{AtomicUsize, Ordering};
use std::alloc::{alloc, dealloc, Layout};

#[repr(C, align(64))]  // 快取行對齊
pub struct RingBuffer<T> {
    buffer: *mut T,
    capacity: usize,
    // 使用 padding 避免 false sharing
    _pad1: [u8; 64 - 16],
    
    write_pos: AtomicUsize,
    _pad2: [u8; 64 - 8],
    
    read_pos: AtomicUsize,
    _pad3: [u8; 64 - 8],
}

unsafe impl<T: Send> Send for RingBuffer<T> {}
unsafe impl<T: Send> Sync for RingBuffer<T> {}

impl<T> RingBuffer<T> {
    pub fn new(capacity: usize) -> Self {
        let layout = Layout::array::<T>(capacity).unwrap();
        let buffer = unsafe { alloc(layout) as *mut T };
        
        Self {
            buffer,
            capacity,
            _pad1: [0; 64 - 16],
            write_pos: AtomicUsize::new(0),
            _pad2: [0; 64 - 8],
            read_pos: AtomicUsize::new(0),
            _pad3: [0; 64 - 8],
        }
    }
    
    // 無鎖寫入
    pub fn push(&self, value: T) -> bool {
        let write = self.write_pos.load(Ordering::Acquire);
        let next_write = (write + 1) % self.capacity;
        
        if next_write == self.read_pos.load(Ordering::Acquire) {
            return false; // 緩衝區滿
        }
        
        unsafe {
            self.buffer.add(write).write(value);
        }
        
        self.write_pos.store(next_write, Ordering::Release);
        true
    }
}
```

## SIMD 優化策略

### 1. 使用 packed_simd 或 std::simd

```rust
#![feature(portable_simd)]
use std::simd::*;

pub fn calculate_returns_simd(prices: &[f32], returns: &mut [f32]) {
    // Rust 的 SIMD API（實驗性）
    let chunks = prices.chunks_exact(8);
    let remainder = chunks.remainder();
    
    for (price_chunk, return_chunk) in 
        chunks.zip(returns.chunks_exact_mut(8)) {
        
        let prices_vec = f32x8::from_slice(price_chunk);
        let prev_prices = f32x8::from_slice(&price_chunk[1..]);
        
        let returns_vec = (prices_vec - prev_prices) / prev_prices;
        returns_vec.copy_to_slice(return_chunk);
    }
    
    // 處理剩餘部分
    for i in 0..remainder.len()-1 {
        returns[prices.len() - remainder.len() + i] = 
            (remainder[i+1] - remainder[i]) / remainder[i];
    }
}
```

### 2. 自動向量化提示

```rust
// 使用迭代器讓編譯器自動向量化
#[inline(always)]
pub fn dot_product(a: &[f64], b: &[f64]) -> f64 {
    // Rust 編譯器會自動向量化這個
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| x * y)
        .sum()
}

// 使用 target-feature 啟用特定 SIMD 指令集
#[target_feature(enable = "avx2")]
unsafe fn process_avx2(data: &mut [f32]) {
    // 編譯器會使用 AVX2 指令
    for x in data {
        *x = x.mul_add(2.0, 1.0);
    }
}
```

### 3. 明確的 SIMD 控制

```rust
use packed_simd_2::*;

pub struct PriceProcessor;

impl PriceProcessor {
    // 批量處理價格更新
    pub fn update_prices_batch(
        bid_prices: &mut [f32],
        ask_prices: &mut [f32],
        adjustment: f32
    ) {
        const LANES: usize = 8;
        let adjustment_vec = f32x8::splat(adjustment);
        
        let chunks = bid_prices.chunks_exact_mut(LANES)
            .zip(ask_prices.chunks_exact_mut(LANES));
        
        for (bid_chunk, ask_chunk) in chunks {
            let bid_vec = f32x8::from_slice_unaligned(bid_chunk);
            let ask_vec = f32x8::from_slice_unaligned(ask_chunk);
            
            let new_bid = bid_vec * adjustment_vec;
            let new_ask = ask_vec * adjustment_vec;
            
            new_bid.write_to_slice_unaligned(bid_chunk);
            new_ask.write_to_slice_unaligned(ask_chunk);
        }
    }
}
```

## 記憶體管理與優化

### 1. 自定義分配器

```rust
use std::alloc::{GlobalAlloc, Layout};
use jemallocator::Jemalloc;

// 使用 jemalloc 提高性能
#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;

// 或者創建專用的內存池
pub struct PoolAllocator {
    pool: Vec<u8>,
    offset: AtomicUsize,
}

impl PoolAllocator {
    pub fn new(size: usize) -> Self {
        let mut pool = Vec::with_capacity(size);
        unsafe { pool.set_len(size); }
        
        Self {
            pool,
            offset: AtomicUsize::new(0),
        }
    }
    
    pub fn allocate(&self, size: usize) -> *mut u8 {
        let offset = self.offset.fetch_add(size, Ordering::SeqCst);
        if offset + size > self.pool.len() {
            panic!("Pool exhausted");
        }
        unsafe { self.pool.as_ptr().add(offset) as *mut u8 }
    }
}
```

### 2. 大頁面支持

```rust
use nix::sys::mman::{mmap, MapFlags, ProtFlags};

pub fn allocate_huge_pages(size: usize) -> *mut u8 {
    let addr = std::ptr::null_mut();
    let length = size;
    let prot = ProtFlags::PROT_READ | ProtFlags::PROT_WRITE;
    let flags = MapFlags::MAP_PRIVATE | 
                MapFlags::MAP_ANONYMOUS | 
                MapFlags::MAP_HUGETLB;
    
    unsafe {
        mmap(addr, length, prot, flags, -1, 0)
            .expect("Failed to allocate huge pages")
            as *mut u8
    }
}
```

## 並發模型

### 1. 無鎖數據結構

```rust
use crossbeam::queue::ArrayQueue;
use std::sync::Arc;

pub struct OrderProcessor {
    queue: Arc<ArrayQueue<Order>>,
}

impl OrderProcessor {
    pub fn new(capacity: usize) -> Self {
        Self {
            queue: Arc::new(ArrayQueue::new(capacity)),
        }
    }
    
    // 生產者
    pub fn submit_order(&self, order: Order) -> Result<(), Order> {
        self.queue.push(order)
    }
    
    // 消費者
    pub fn process_orders(&self) {
        while let Some(order) = self.queue.pop() {
            self.handle_order(order);
        }
    }
    
    fn handle_order(&self, order: Order) {
        // 處理訂單
    }
}
```

### 2. 高性能異步 IO

```rust
use tokio::net::UdpSocket;
use bytes::BytesMut;

pub struct MarketDataReceiver {
    socket: UdpSocket,
    buffer: BytesMut,
}

impl MarketDataReceiver {
    pub async fn new(addr: &str) -> std::io::Result<Self> {
        let socket = UdpSocket::bind(addr).await?;
        
        // 設置接收緩衝區大小
        socket.set_recv_buffer_size(8 * 1024 * 1024)?;
        
        Ok(Self {
            socket,
            buffer: BytesMut::with_capacity(65536),
        })
    }
    
    pub async fn receive_data(&mut self) -> std::io::Result<MarketData> {
        self.buffer.clear();
        let n = self.socket.recv_buf(&mut self.buffer).await?;
        
        // 零拷貝解析
        let data = self.parse_market_data(&self.buffer[..n]);
        Ok(data)
    }
    
    fn parse_market_data(&self, bytes: &[u8]) -> MarketData {
        // 直接從 bytes 解析，避免拷貝
        unsafe {
            std::ptr::read(bytes.as_ptr() as *const MarketData)
        }
    }
}
```

## 實戰範例

### 完整的 HFT 組件示例

```rust
use std::time::Instant;
use parking_lot::RwLock;
use ahash::AHashMap;

#[derive(Clone, Copy)]
#[repr(C, packed)]
pub struct MarketData {
    pub timestamp: u64,
    pub symbol_id: u32,
    pub bid_price: f64,
    pub ask_price: f64,
    pub bid_size: u32,
    pub ask_size: u32,
}

pub struct TradingEngine {
    // 使用 parking_lot 的 RwLock（比標準庫快）
    order_book: RwLock<AHashMap<u32, OrderBook>>,
    
    // 預分配的內存池
    memory_pool: PoolAllocator,
    
    // 性能統計
    latency_histogram: hdrhistogram::Histogram<u64>,
}

impl TradingEngine {
    pub fn new() -> Self {
        Self {
            order_book: RwLock::new(AHashMap::new()),
            memory_pool: PoolAllocator::new(1024 * 1024 * 1024), // 1GB
            latency_histogram: hdrhistogram::Histogram::new(5).unwrap(),
        }
    }
    
    #[inline(always)]
    pub fn process_market_data(&mut self, data: &MarketData) {
        let start = Instant::now();
        
        // 關鍵路徑：避免任何分配
        let book = self.order_book.read();
        if let Some(orders) = book.get(&data.symbol_id) {
            // 處理訂單匹配
            self.match_orders(orders, data);
        }
        
        // 記錄延遲（在非關鍵路徑）
        let latency = start.elapsed().as_nanos() as u64;
        self.latency_histogram.record(latency).ok();
    }
    
    #[inline(always)]
    fn match_orders(&self, orders: &OrderBook, data: &MarketData) {
        // 訂單匹配邏輯
        // 使用 likely/unlikely 提示分支預測
        if likely(data.bid_price > 0.0) {
            // 快速路徑
        }
    }
}

// 分支預測提示
#[inline(always)]
fn likely(b: bool) -> bool {
    // 使用 LLVM 內建函數
    unsafe { std::intrinsics::likely(b) }
}
```

### 編譯優化設置

```toml
# Cargo.toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true

# 針對特定 CPU 優化
[build]
rustflags = [
    "-C", "target-cpu=native",
    "-C", "target-feature=+avx2,+fma",
    "-C", "link-arg=-fuse-ld=lld",
]

# 使用高性能依賴
[dependencies]
parking_lot = "0.12"     # 更快的鎖
ahash = "0.8"            # 更快的哈希
crossbeam = "0.8"        # 無鎖數據結構
jemallocator = "0.5"     # 更好的分配器
packed_simd_2 = "0.3"    # SIMD 支持
tokio = { version = "1", features = ["net", "rt-multi-thread"] }
```

## Rust 特有優勢總結

### 相比 C++ 的優點

1. **記憶體安全保證**
   - 編譯時防止 data race
   - 無需擔心 use-after-free
   - 更容易寫出正確的並發代碼

2. **更好的工具鏈**
   - Cargo 統一的構建系統
   - 內建的測試框架
   - 優秀的錯誤訊息

3. **現代語言特性**
   - Pattern matching
   - Option/Result 類型
   - Trait system

### 性能考量

| 方面 | Rust 實現方式 |
|-----|--------------|
| **零成本抽象** | 內聯、單態化 |
| **記憶體佈局** | `#[repr(C)]` 精確控制 |
| **SIMD** | portable_simd、auto-vectorization |
| **並發** | Send/Sync traits、無鎖結構 |
| **系統調用** | 直接 FFI 調用 |

### 最佳實踐

1. **使用 `unsafe` 進行關鍵優化**
   - 在熱路徑上謹慎使用
   - 封裝在安全的 API 後面

2. **利用 Rust 的零成本抽象**
   - 迭代器通常比手寫循環快
   - 使用泛型實現編譯時優化

3. **選擇合適的數據結構**
   - `Vec` 用於連續數據
   - `SmallVec` 用於小數據避免堆分配
   - 無鎖結構用於高並發

## 結論

Rust 在 HFT 領域是 C++ 的有力競爭者，提供了：
- ✅ 相同的底層控制能力
- ✅ 更好的記憶體安全保證
- ✅ 現代的工具鏈和生態系統
- ✅ 零成本抽象

主要挑戰是：
- ⚠️ 生態系統相對年輕
- ⚠️ 學習曲線較陡
- ⚠️ 某些底層 API 需要 unsafe

總的來說，Rust 完全可以達到 C++ 的性能水平，同時提供更好的安全性和開發體驗。