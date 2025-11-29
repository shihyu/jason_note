# 高頻交易 Rust 終極效能優化指南

完整涵蓋：位元運算、查表法、CPU 綁定、記憶體優化、Cache 優化、系統調校

---

## 目錄
1. [位元運算優化](#1-位元運算優化)
2. [查表法 (Lookup Table)](#2-查表法-lookup-table)
3. [分支預測優化](#3-分支預測優化)
4. [CPU 綁定與排程優化](#4-cpu-綁定與排程優化)
5. [記憶體與 Cache 優化](#5-記憶體與-cache-優化)
6. [Huge Pages 設定](#6-huge-pages-設定)
7. [資料結構對齊](#7-資料結構對齊)
8. [浮點數優化](#8-浮點數優化)
9. [SIMD 平行化](#9-simd-平行化)
10. [避免 Context Switch](#10-避免-context-switch)
11. [Lock-Free 程式設計](#11-lock-free-程式設計)
12. [編譯器優化](#12-編譯器優化)
13. [系統層級調校](#13-系統層級調校)
14. [完整範例專案](#14-完整範例專案)
15. [效能測試與監控](#15-效能測試與監控)

---

## 1. 位元運算優化

### 基本運算替換

```rust
// ============ 乘法/除法 ============
// ❌ 慢
let a = x * 2;
let b = x * 4;
let c = x * 8;
let d = x / 2;
let e = x / 16;

// ✅ 快（快 3-10 倍）
let a = x << 1;      // 乘以 2
let b = x << 2;      // 乘以 4
let c = x << 3;      // 乘以 8
let d = x >> 1;      // 除以 2
let e = x >> 4;      // 除以 16

// ============ 模運算 ============
// ❌ 慢
let remainder = x % 8;
let r2 = x % 16;
let r3 = x % 32;

// ✅ 快
let remainder = x & 7;    // % 8  (7 = 2^3 - 1)
let r2 = x & 15;          // % 16 (15 = 2^4 - 1)
let r3 = x & 31;          // % 32 (31 = 2^5 - 1)

// ============ 奇偶判斷 ============
// ❌ 慢
if x % 2 == 0 { /* 偶數 */ }

// ✅ 快
if (x & 1) == 0 { /* 偶數 */ }

// ============ 判斷 2 的冪次 ============
fn is_power_of_two(x: u32) -> bool {
    x != 0 && (x & (x - 1)) == 0
}

// ============ 取絕對值（整數）============
fn abs_i32(x: i32) -> i32 {
    let mask = x >> 31;  // 負數全為 1，正數全為 0
    (x ^ mask) - mask
}

fn abs_i64(x: i64) -> i64 {
    let mask = x >> 63;
    (x ^ mask) - mask
}

// ============ 交換變數 ============
// ❌ 需要臨時變數
let temp = a;
a = b;
b = temp;

// ✅ XOR 交換（無需額外記憶體）
a ^= b;
b ^= a;
a ^= b;

// ============ 最小/最大值（無分支）============
fn min_branchless(a: i32, b: i32) -> i32 {
    b ^ ((a ^ b) & -((a < b) as i32))
}

fn max_branchless(a: i32, b: i32) -> i32 {
    a ^ ((a ^ b) & -((a < b) as i32))
}

// ============ 位元操作進階 ============
// 找到最低位的 1
fn lowest_set_bit(x: u64) -> u64 {
    x & x.wrapping_neg()
}

// 清除最低位的 1
fn clear_lowest_bit(x: u64) -> u64 {
    x & (x - 1)
}

// 計算 trailing zeros（使用 CPU 指令）
fn trailing_zeros(x: u64) -> u32 {
    x.trailing_zeros()  // 編譯成 BSF/TZCNT 指令
}

// 計算 leading zeros
fn leading_zeros(x: u64) -> u32 {
    x.leading_zeros()   // 編譯成 BSR/LZCNT 指令
}

// 計算 1 的數量（popcount）
fn count_ones(x: u64) -> u32 {
    x.count_ones()      // 編譯成 POPCNT 指令
}

// 位元反轉
fn reverse_bits(x: u32) -> u32 {
    x.reverse_bits()    // 硬體加速
}

// ============ 條件選擇（無分支）============
// 選擇 a 或 b，根據 condition
fn select(condition: bool, a: i32, b: i32) -> i32 {
    let mask = -(condition as i32);  // true: -1, false: 0
    (a & mask) | (b & !mask)
}

// ============ 符號擴展 ============
// 將 8-bit 符號數擴展到 32-bit
fn sign_extend_8to32(x: u8) -> i32 {
    ((x as i8) as i32)
}

// ============ 快速整數平方根（近似）============
fn isqrt_approx(x: u32) -> u32 {
    if x == 0 { return 0; }
    let mut z = x;
    let mut result = 0u32;
    let mut bit = 1u32 << 30;
    
    while bit > x {
        bit >>= 2;
    }
    
    while bit != 0 {
        if x >= result + bit {
            z = x - (result + bit);
            result = (result >> 1) + bit;
        } else {
            result >>= 1;
        }
        bit >>= 2;
    }
    result
}
```

### 實際交易應用

```rust
// 價格 tick 計算
const TICK_SIZE: u32 = 25;  // 2^5 = 32 的倍數，可用位移

fn price_to_tick(price: u32) -> u32 {
    price >> 5  // 除以 32，等同於 price / TICK_SIZE
}

fn tick_to_price(tick: u32) -> u32 {
    tick << 5   // 乘以 32
}

// 訂單 ID 編碼/解碼
// 高 32 位：時間戳，低 32 位：序號
fn encode_order_id(timestamp: u32, sequence: u32) -> u64 {
    ((timestamp as u64) << 32) | (sequence as u64)
}

fn decode_timestamp(order_id: u64) -> u32 {
    (order_id >> 32) as u32
}

fn decode_sequence(order_id: u64) -> u32 {
    (order_id & 0xFFFFFFFF) as u32
}

// 快速判斷買賣方向（bit flag）
const BUY_FLAG: u8 = 0b0000_0001;
const MARKET_ORDER: u8 = 0b0000_0010;
const IOC_FLAG: u8 = 0b0000_0100;

fn is_buy_order(flags: u8) -> bool {
    (flags & BUY_FLAG) != 0
}

fn is_market_order(flags: u8) -> bool {
    (flags & MARKET_ORDER) != 0
}

// 組合多個標誌
fn create_flags(is_buy: bool, is_market: bool, is_ioc: bool) -> u8 {
    ((is_buy as u8) * BUY_FLAG) |
    ((is_market as u8) * MARKET_ORDER) |
    ((is_ioc as u8) * IOC_FLAG)
}
```

---

## 2. 查表法 (Lookup Table)

### 基礎查表

```rust
// ============ 預計算常用值 ============
// 位元計數表（8-bit）
static POPCOUNT_TABLE: [u8; 256] = {
    let mut table = [0u8; 256];
    let mut i = 0;
    while i < 256 {
        table[i] = (i as u8).count_ones() as u8;
        i += 1;
    }
    table
};

fn popcount_lookup(mut x: u32) -> u32 {
    let mut count = 0u32;
    while x != 0 {
        count += POPCOUNT_TABLE[(x & 0xFF) as usize] as u32;
        x >>= 8;
    }
    count
}

// ============ 對數表 ============
static LOG2_TABLE: [f64; 256] = {
    let mut table = [0.0; 256];
    let mut i = 1;
    while i < 256 {
        table[i] = (i as f64).log2();
        i += 1;
    }
    table
};

// ============ 平方根表 ============
static SQRT_TABLE: [f64; 1024] = {
    let mut table = [0.0; 1024];
    let mut i = 0;
    while i < 1024 {
        table[i] = (i as f64).sqrt();
        i += 1;
    }
    table
};

// ============ 手續費計算表 ============
static FEE_TABLE: [f64; 1000] = {
    let mut table = [0.0; 1000];
    let mut i = 0;
    while i < 1000 {
        table[i] = if i < 100 {
            i as f64 * 0.001
        } else if i < 500 {
            i as f64 * 0.0008
        } else {
            i as f64 * 0.0005
        };
        i += 1;
    }
    table
};

#[inline(always)]
fn calculate_fee(volume: u32) -> f64 {
    if volume < 1000 {
        FEE_TABLE[volume as usize]
    } else {
        volume as f64 * 0.0005
    }
}
```

### 交易應用查表

```rust
// ============ 價格等級查表 ============
// 假設價格範圍 10000-20000，精度 0.01
const PRICE_MIN: u32 = 1000000;  // 10000.00 * 100
const PRICE_MAX: u32 = 2000000;  // 20000.00 * 100
const PRICE_RANGE: usize = (PRICE_MAX - PRICE_MIN) as usize + 1;

static PRICE_LEVEL_TABLE: [u16; PRICE_RANGE] = {
    let mut table = [0u16; PRICE_RANGE];
    let mut i = 0;
    while i < PRICE_RANGE {
        let price = PRICE_MIN + i as u32;
        table[i] = ((price - PRICE_MIN) / 100) as u16;  // 每 1.00 一個等級
        i += 1;
    }
    table
};

#[inline(always)]
fn get_price_level(price: u32) -> u16 {
    if price < PRICE_MIN || price > PRICE_MAX {
        return 0;
    }
    PRICE_LEVEL_TABLE[(price - PRICE_MIN) as usize]
}

// ============ 波動率區間查表 ============
const VOLATILITY_BUCKETS: usize = 100;
static VOLATILITY_ADJUSTMENT: [f64; VOLATILITY_BUCKETS] = {
    let mut table = [0.0; VOLATILITY_BUCKETS];
    let mut i = 0;
    while i < VOLATILITY_BUCKETS {
        let vol = i as f64 * 0.01;  // 0.00 到 1.00
        table[i] = if vol < 0.2 {
            1.0
        } else if vol < 0.5 {
            0.95
        } else {
            0.85
        };
        i += 1;
    }
    table
};

// ============ 時間衰減表（選擇權）============
static TIME_DECAY: [f64; 365] = {
    let mut table = [0.0; 365];
    let mut i = 0;
    while i < 365 {
        let days = i as f64;
        table[i] = (-days / 365.0).exp();
        i += 1;
    }
    table
};
```

### 動態查表（執行時建立）

```rust
use std::collections::HashMap;
use std::sync::Arc;

// 使用 FxHashMap（更快的 hash）
use rustc_hash::FxHashMap;

struct OrderBook {
    // 價格 -> 訂單列表索引
    price_index: FxHashMap<u32, Vec<usize>>,
    orders: Vec<Order>,
}

impl OrderBook {
    fn new() -> Self {
        Self {
            price_index: FxHashMap::default(),
            orders: Vec::with_capacity(10000),
        }
    }
    
    fn add_order(&mut self, price: u32, order: Order) {
        let idx = self.orders.len();
        self.orders.push(order);
        self.price_index.entry(price).or_insert_with(Vec::new).push(idx);
    }
    
    #[inline(always)]
    fn get_orders_at_price(&self, price: u32) -> Option<&Vec<usize>> {
        self.price_index.get(&price)
    }
}
```

---

## 3. 分支預測優化

```rust
// ============ Likely/Unlikely 提示 ============
#![feature(core_intrinsics)]
use std::intrinsics::{likely, unlikely};

fn process_order(order: &Order) {
    // 大部分訂單是買單
    if unsafe { likely(order.is_buy) } {
        execute_buy(order);
    } else {
        execute_sell(order);
    }
    
    // 極少數情況會出錯
    if unsafe { unlikely(order.quantity == 0) } {
        handle_error();
        return;
    }
    
    normal_processing(order);
}

// ============ 無分支版本 ============
// 條件賦值
fn get_fee_rate(is_vip: bool) -> f64 {
    // ❌ 有分支
    // if is_vip { 0.0005 } else { 0.001 }
    
    // ✅ 無分支
    0.001 - (is_vip as u32 as f64 * 0.0005)
}

// 條件選擇
fn select_value(condition: bool, true_val: i32, false_val: i32) -> i32 {
    let index = condition as usize;
    [false_val, true_val][index]
}

// ============ 用陣列取代 if-else ============
// ❌ 多重分支
fn get_tier_name(tier: u8) -> &'static str {
    if tier == 0 { "Bronze" }
    else if tier == 1 { "Silver" }
    else if tier == 2 { "Gold" }
    else if tier == 3 { "Platinum" }
    else { "Unknown" }
}

// ✅ 查表
const TIER_NAMES: [&str; 5] = ["Bronze", "Silver", "Gold", "Platinum", "Unknown"];

fn get_tier_name_fast(tier: u8) -> &'static str {
    TIER_NAMES[tier.min(4) as usize]
}

// ============ 位元操作取代分支 ============
// 計算絕對差值
fn abs_diff_branched(a: i32, b: i32) -> i32 {
    if a > b { a - b } else { b - a }
}

fn abs_diff_branchless(a: i32, b: i32) -> i32 {
    let diff = a - b;
    let mask = diff >> 31;
    (diff ^ mask) - mask
}

// Min/Max
fn min_i32(a: i32, b: i32) -> i32 {
    b ^ ((a ^ b) & -((a < b) as i32))
}

fn max_i32(a: i32, b: i32) -> i32 {
    a ^ ((a ^ b) & -((a < b) as i32))
}

// ============ 提前返回（短路）============
fn validate_and_execute(order: &Order) -> Result<(), Error> {
    // 快速失敗路徑
    if order.quantity == 0 { return Err(Error::InvalidQuantity); }
    if order.price == 0 { return Err(Error::InvalidPrice); }
    
    // 主要邏輯
    execute_order(order)
}
```

---

## 4. CPU 綁定與排程優化

### CPU Affinity

```rust
// Cargo.toml
// [dependencies]
// core_affinity = "0.8"
// libc = "0.2"

use core_affinity::{self, CoreId};
use std::thread;

// ============ 基本 CPU 綁定 ============
fn pin_thread_to_core(core_id: usize) {
    let core_ids = core_affinity::get_core_ids().unwrap();
    if core_id < core_ids.len() {
        core_affinity::set_for_current(core_ids[core_id]);
        println!("執行緒綁定到核心 {}", core_id);
    }
}

fn main() {
    // 主執行緒綁到核心 0
    pin_thread_to_core(0);
    
    // 交易執行緒綁到核心 2
    let trading_thread = thread::spawn(|| {
        pin_thread_to_core(2);
        trading_loop();
    });
    
    // 市場資料執行緒綁到核心 3
    let market_data_thread = thread::spawn(|| {
        pin_thread_to_core(3);
        market_data_loop();
    });
    
    trading_thread.join().unwrap();
    market_data_thread.join().unwrap();
}

// ============ 使用 libc 直接設定 ============
use libc::{cpu_set_t, sched_setaffinity, CPU_SET, CPU_ZERO};

fn pin_to_cpu_libc(cpu: usize) -> Result<(), String> {
    unsafe {
        let mut cpuset: cpu_set_t = std::mem::zeroed();
        CPU_ZERO(&mut cpuset);
        CPU_SET(cpu, &mut cpuset);
        
        let result = sched_setaffinity(
            0,  // 0 = 當前執行緒
            std::mem::size_of::<cpu_set_t>(),
            &cpuset
        );
        
        if result != 0 {
            return Err(format!("無法綁定 CPU {}", cpu));
        }
    }
    Ok(())
}

// ============ 綁定多個 CPU ============
fn pin_to_multiple_cpus(cpus: &[usize]) -> Result<(), String> {
    unsafe {
        let mut cpuset: cpu_set_t = std::mem::zeroed();
        CPU_ZERO(&mut cpuset);
        
        for &cpu in cpus {
            CPU_SET(cpu, &mut cpuset);
        }
        
        let result = sched_setaffinity(
            0,
            std::mem::size_of::<cpu_set_t>(),
            &cpuset
        );
        
        if result != 0 {
            return Err("無法設定 CPU affinity".to_string());
        }
    }
    Ok(())
}

// ============ 查詢當前綁定 ============
use libc::{sched_getaffinity, CPU_ISSET};

fn get_current_affinity() -> Vec<usize> {
    unsafe {
        let mut cpuset: cpu_set_t = std::mem::zeroed();
        sched_getaffinity(0, std::mem::size_of::<cpu_set_t>(), &mut cpuset);
        
        let mut cores = Vec::new();
        for cpu in 0..256 {
            if CPU_ISSET(cpu, &cpuset) {
                cores.push(cpu);
            }
        }
        cores
    }
}
```

### Real-Time Priority

```rust
use libc::{sched_param, sched_setscheduler, SCHED_FIFO, SCHED_RR};

// ============ 設定 Real-Time 優先權 ============
fn set_realtime_priority(priority: i32) -> Result<(), String> {
    // priority: 1-99，數字越大優先權越高
    // 一般建議：70-90
    
    if priority < 1 || priority > 99 {
        return Err("優先權必須在 1-99 之間".to_string());
    }
    
    unsafe {
        let param = sched_param {
            sched_priority: priority,
        };
        
        // SCHED_FIFO: 先進先出，執行到完成或主動讓出
        let result = sched_setscheduler(0, SCHED_FIFO, &param);
        
        if result != 0 {
            return Err("需要 CAP_SYS_NICE 權限或 sudo".to_string());
        }
    }
    
    Ok(())
}

// ============ 使用 SCHED_RR（時間片輪詢）============
fn set_realtime_rr(priority: i32, timeslice_ms: u32) -> Result<(), String> {
    unsafe {
        let param = sched_param {
            sched_priority: priority,
        };
        
        // SCHED_RR: Round-Robin，有時間片限制
        let result = sched_setscheduler(0, SCHED_RR, &param);
        
        if result != 0 {
            return Err("無法設定 SCHED_RR".to_string());
        }
    }
    
    Ok(())
}

// ============ 完整的執行緒設定 ============
fn setup_realtime_thread(cpu_id: usize, priority: i32) -> Result<(), String> {
    // 1. 綁定 CPU
    pin_to_cpu_libc(cpu_id)?;
    
    // 2. 設定 RT 優先權
    set_realtime_priority(priority)?;
    
    // 3. 鎖定記憶體（避免 page fault）
    unsafe {
        if libc::mlockall(libc::MCL_CURRENT | libc::MCL_FUTURE) != 0 {
            return Err("無法鎖定記憶體".to_string());
        }
    }
    
    Ok(())
}
```

---

## 5. 記憶體與 Cache 優化

### Cache-Friendly 資料結構

```rust
// ============ Structure of Arrays (SoA) ============
// ❌ Array of Structures (AoS) - Cache miss 多
struct Order {
    id: u64,
    price: f64,
    quantity: u32,
    timestamp: u64,
}

struct OrderBookAoS {
    orders: Vec<Order>,  // 每次存取跳來跳去
}

// ✅ Structure of Arrays - Cache 友善
struct OrderBookSoA {
    ids: Vec<u64>,
    prices: Vec<f64>,
    quantities: Vec<u32>,
    timestamps: Vec<u64>,
}

impl OrderBookSoA {
    // 只需要價格時，只載入 prices 到 cache
    fn get_best_price(&self) -> Option<f64> {
        self.prices.first().copied()
    }
    
    // SIMD 可以一次處理多個價格
    fn calculate_vwap(&self) -> f64 {
        let total_value: f64 = self.prices.iter()
            .zip(self.quantities.iter())
            .map(|(&p, &q)| p * q as f64)
            .sum();
        let total_qty: u32 = self.quantities.iter().sum();
        total_value / total_qty as f64
    }
}

// ============ Cache Line 大小對齊 ============
const CACHE_LINE_SIZE: usize = 64;

#[repr(align(64))]
struct AlignedData {
    value: u64,
    _padding: [u8; 56],  // 填充到 64 bytes
}

// ============ 避免 False Sharing ============
use crossbeam::utils::CachePadded;

struct SharedCounters {
    // ❌ False sharing - 兩個執行緒寫入同一 cache line
    // counter1: AtomicU64,
    // counter2: AtomicU64,
    
    // ✅ 各自在不同 cache line
    counter1: CachePadded<AtomicU64>,
    counter2: CachePadded<AtomicU64>,
}

// ============ 記憶體池（避免頻繁分配）============
struct OrderPool {
    pool: Vec<Order>,
    free_indices: Vec<usize>,
    capacity: usize,
}

impl OrderPool {
    fn new(capacity: usize) -> Self {
        let mut pool = Vec::with_capacity(capacity);
        for i in 0..capacity {
            pool.push(Order::default());
        }
        
        Self {
            pool,
            free_indices: (0..capacity).collect(),
            capacity,
        }
    }
    
    fn allocate(&mut self) -> Option<&mut Order> {
        if let Some(idx) = self.free_indices.pop() {
            Some(&mut self.pool[idx])
        } else {
            None
        }
    }
    
    fn deallocate(&mut self, order: &Order) {
        // 找到索引並回收
        let idx = order as *const Order as usize - 
                  self.pool.as_ptr() as usize;
        let idx = idx / std::mem::size_of::<Order>();
        self.free_indices.push(idx);
    }
}

// ============ 預分配與重用 ============
struct MessageBuffer {
    buffer: Vec<u8>,
}

impl MessageBuffer {
    fn new() -> Self {
        Self {
            buffer: Vec::with_capacity(4096),
        }
    }
    
    fn prepare(&mut self, size: usize) {
        self.buffer.clear();
        self.buffer.reserve(size);
    }
    
    fn get_buffer(&mut self) -> &mut Vec<u8> {
        &mut self.buffer
    }
}

// ============ Arena Allocator ============
use bumpalo::Bump;

fn use_arena() {
    let arena = Bump::new();
    
    // 所有分配都在 arena 中，一次性釋放
    let orders: Vec<_> = (0..1000)
        .map(|i| arena.alloc(Order { id: i, ..Default::default() }))
        .collect();
    
    // 離開 scope 時一次釋放所有記憶體
}
```

### 記憶體預熱

```rust
// ============ Cache 預熱 ============
fn warmup_cache<T>(data: &[T]) {
    // 觸發所有 cache line 載入
    for item in data {
        std::hint::black_box(item);
    }
}

fn warmup_order_book(book: &OrderBookSoA) {
    // 預熱所有價格資料
    for price in &book.prices {
        std::hint::black_box(price);
    }
}

// ============ Prefetch（手動）============
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

unsafe fn prefetch_data<T>(ptr: *const T) {
    #[cfg(target_arch = "x86_64")]
    {
        _mm_prefetch(ptr as *const i8, _MM_HINT_T0);  // 載入到 L1 cache
    }
}

// 使用範例
fn process_orders_with_prefetch(orders: &[Order]) {
    for i in 0..orders.len() {
        // 預取下一個訂單
        if i + 1 < orders.len() {
            unsafe {
                prefetch_data(&orders[i + 1]);
            }
        }
        
        process_order(&orders[i]);
    }
}
```

---

## 6. Huge Pages 設定

### 系統設定（不需重編 kernel）

```bash
#!/bin/bash
# setup_hugepages.sh

# ============ 查看目前狀態 ============
cat /proc/meminfo | grep -i huge

# ============ 方法 1: Transparent Huge Pages (THP) ============
# 自動啟用，最簡單
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# 查看狀態
cat /sys/kernel/mm/transparent_hugepage/enabled
# 應該顯示: [always] madvise never

# ============ 方法 2: 預分配 Huge Pages ============
# 分配 1024 個 2MB 頁面 = 2GB
echo 1024 | sudo tee /proc/sys/vm/nr_hugepages

# 分配 1GB 頁面（需要 CPU 支援）
echo 2 | sudo tee /proc/sys/vm/nr_hugepages_1GB

# 查看分配結果
cat /proc/meminfo | grep HugePages_Total
cat /proc/meminfo | grep HugePages_Free

# ============ 永久設定 ============
# 編輯 /etc/sysctl.conf
sudo tee -a /etc/sysctl.conf <<EOF
# Huge Pages 設定
vm.nr_hugepages = 1024
vm.hugetlb_shm_group = 1000  # 你的 group ID
EOF

# 套用設定
sudo sysctl -p

# ============ 掛載 hugetlbfs ============
sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge

# 永久掛載（加到 /etc/fstab）
echo "nodev /mnt/huge hugetlbfs defaults 0 0" | sudo tee -a /etc/fstab
```

### Rust 中使用 Huge Pages

```rust
use libc::{mmap, munmap, MAP_ANONYMOUS, MAP_PRIVATE, MAP_HUGETLB, PROT_READ, PROT_WRITE};
use std::ptr;

// ============ 手動分配 Huge Pages ============
struct HugePageBuffer {
    ptr: *mut u8,
    size: usize,
}

impl HugePageBuffer {
    fn new(size: usize) -> Result<Self, String> {
        // size 應該是 2MB 的倍數
        let size = (size + 2 * 1024 * 1024 - 1) & !(2 * 1024 * 1024 - 1);
        
        unsafe {
            let ptr = mmap(
                ptr::null_mut(),
                size,
                PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                -1,
                0
            );
            
            if ptr == libc::MAP_FAILED {
                return Err("無法分配 huge pages，檢查系統設定".to_string());
            }
            
            Ok(Self {
                ptr: ptr as *mut u8,
                size,
            })
        }
    }
    
    fn as_slice_mut(&mut self) -> &mut [u8] {
        unsafe {
            std::slice::from_raw_parts_mut(self.ptr, self.size)
        }
    }
}

impl Drop for HugePageBuffer {
    fn drop(&mut self) {
        unsafe {
            munmap(self.ptr as *mut libc::c_void, self.size);
        }
    }
}

// 使用範例
fn use_huge_pages() -> Result<(), String> {
    let mut buffer = HugePageBuffer::new(4 * 1024 * 1024)?;  // 4MB
    let slice = buffer.as_slice_mut();
    
    // 使用 buffer
    slice[0] = 42;
    
    Ok(())
}

// ============ 使用 madvise 提示 ============
use libc::{madvise, MADV_HUGEPAGE};

fn suggest_huge_pages(ptr: *mut u8, size: usize) {
    unsafe {
        madvise(ptr as *mut libc::c_void, size, MADV_HUGEPAGE);
    }
}

// ============ Global Allocator 使用 Huge Pages ============
// Cargo.toml: huge_pages = "0.2"
// 注意：這個會影響所有記憶體分配

// 方法 1: 完全替換 allocator
#[global_allocator]
static ALLOC: huge_pages::HugePageAllocator = huge_pages::HugePageAllocator;

// 方法 2: 只針對特定資料結構
use huge_pages::HugePageVec;

fn use_huge_page_vec() {
    let mut vec = HugePageVec::<u64>::new();
    vec.extend(0..1_000_000);
}
```

---

## 7. 資料結構對齊

```rust
// ============ Rust 自動優化 ============
struct Auto {
    a: u8,      // 1 byte
    b: u64,     // 8 bytes  
    c: u16,     // 2 bytes
}
// Rust 會重排成：b, c, a, padding
// 實際大小：16 bytes（已優化）

// ============ C 語言佈局（FFI 用）============
#[repr(C)]
struct CLayout {
    a: u8,      // 位置固定
    // padding: 7 bytes
    b: u64,
    c: u16,
    // padding: 6 bytes
}
// 大小：24 bytes（未優化）

// ============ 緊密打包（無 padding）============
#[repr(packed)]
struct Packed {
    a: u8,
    b: u64,
    c: u16,
}
// 大小：11 bytes
// ⚠️ 警告：存取 b 可能很慢（未對齊）

// ⚠️ 取引用會有問題
fn use_packed() {
    let p = Packed { a: 1, b: 2, c: 3 };
    
    // ❌ 編譯錯誤或警告
    // let r = &p.b;
    
    // ✅ 複製值
    let val = p.b;  // OK
}

// ============ 指定對齊 ============
#[repr(align(16))]
struct Aligned16 {
    data: u64,
}
// 大小：16 bytes（對齊到 16）

#[repr(align(64))]  // Cache line 大小
struct CacheLineAligned {
    data: u64,
}
// 大小：64 bytes

// ============ 組合使用 ============
#[repr(C, align(32))]
struct Combined {
    a: u32,
    b: u32,
}
// C 佈局 + 32-byte 對齊

// ============ 檢查大小和對齊 ============
use std::mem::{size_of, align_of};

fn check_layout() {
    println!("Auto: size={}, align={}", 
        size_of::<Auto>(), align_of::<Auto>());
    
    println!("CLayout: size={}, align={}", 
        size_of::<CLayout>(), align_of::<CLayout>());
    
    println!("Packed: size={}, align={}", 
        size_of::<Packed>(), align_of::<Packed>());
    
    println!("Aligned16: size={}, align={}", 
        size_of::<Aligned16>(), align_of::<Aligned16>());
}

// ============ 實用的對齊巨集 ============
macro_rules! cache_aligned {
    ($name:ident, $field:ty) => {
        #[repr(align(64))]
        struct $name {
            value: $field,
            _padding: [u8; 64 - std::mem::size_of::<$field>()],
        }
    };
}

cache_aligned!(AlignedCounter, std::sync::atomic::AtomicU64);

// ============ SIMD 對齊 ============
#[repr(align(32))]  // AVX 需要 32-byte 對齊
struct SimdBuffer {
    data: [f32; 8],
}

#[repr(align(64))]  // AVX-512 需要 64-byte 對齊
struct Simd512Buffer {
    data: [f32; 16],
}
```

---

## 8. 浮點數優化

```rust
// ============ 乘法取代除法 ============
// ❌ 慢
let result = price / 100.0;           // ~10 cycles
let r2 = value / 3.14159;

// ✅ 快
let result = price * 0.01;            // ~3 cycles
let r2 = value * 0.318309886;         // 1/π 預計算

// ============ 整數運算取代浮點 ============
// 價格用整數（單位：分或 tick）
struct Price {
    value: i64,  // 價格 * 10000，精度到 0.0001
}

impl Price {
    fn from_float(price: f64) -> Self {
        Self { value: (price * 10000.0) as i64 }
    }
    
    fn to_float(&self) -> f64 {
        self.value as f64 * 0.0001  // 乘法比除法快
    }
    
    fn add(&self, other: &Self) -> Self {
        Self { value: self.value + other.value }
    }
    
    fn multiply(&self, qty: i64) -> i64 {
        self.value * qty
    }
}

// ============ 避免浮點比較 ============
// ❌ 不精確
if price == 123.45 { }

// ✅ 用整數
let price_int = (price * 10000.0) as i64;
if price_int == 1234500 { }

// ✅ 容差比較
const EPSILON: f64 = 1e-9;
if (price - 123.45).abs() < EPSILON { }

// ============ 快速數學函數 ============
// ❌ 精確但慢
let sqrt_val = x.sqrt();
let ln_val = x.ln();

// ✅ 快速近似（需要 libm 或自己實作）
fn fast_sqrt(x: f32) -> f32 {
    // 使用 CPU 指令
    unsafe { std::arch::x86_64::_mm_cvtss_f32(
        std::arch::x86_64::_mm_sqrt_ss(
            std::arch::x86_64::_mm_set_ss(x)
        )
    )}
}

// 或用位元技巧（Quake III 演算法）
fn fast_inv_sqrt(x: f32) -> f32 {
    let i = x.to_bits();
    let i = 0x5f3759df - (i >> 1);
    let y = f32::from_bits(i);
    y * (1.5 - 0.5 * x * y * y)  // 一次牛頓迭代
}

// ============ FMA (Fused Multiply-Add) ============
// a * b + c 一次完成，更快更精確
fn use_fma(a: f64, b: f64, c: f64) -> f64 {
    a.mul_add(b, c)  // 編譯成 FMA 指令
}

// ============ 避免不必要的型別轉換 ============
// ❌ 慢
let result = (x as f64 * y as f64) as i32;

// ✅ 快
let result = (x * y) as i32;

// ============ 使用 SIMD 版本 ============
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

unsafe fn sqrt_4(values: [f32; 4]) -> [f32; 4] {
    let v = _mm_loadu_ps(values.as_ptr());
    let result = _mm_sqrt_ps(v);
    let mut out = [0.0f32; 4];
    _mm_storeu_ps(out.as_mut_ptr(), result);
    out
}
```

---

## 9. SIMD 平行化

```rust
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

// ============ AVX2 範例：處理 4 個 f64 ============
unsafe fn sum_f64_simd(data: &[f64]) -> f64 {
    let mut sum = _mm256_setzero_pd();  // 4 個 f64
    
    let chunks = data.chunks_exact(4);
    let remainder = chunks.remainder();
    
    for chunk in chunks {
        let v = _mm256_loadu_pd(chunk.as_ptr());
        sum = _mm256_add_pd(sum, v);
    }
    
    // 水平相加
    let mut result = [0.0; 4];
    _mm256_storeu_pd(result.as_mut_ptr(), sum);
    let mut total = result.iter().sum::<f64>();
    
    // 處理剩餘
    total += remainder.iter().sum::<f64>();
    total
}

// ============ AVX2：價格 * 數量（批次）============
unsafe fn calculate_values_simd(prices: &[f64], quantities: &[f64], output: &mut [f64]) {
    assert_eq!(prices.len(), quantities.len());
    assert_eq!(prices.len(), output.len());
    
    let len = prices.len();
    let mut i = 0;
    
    while i + 4 <= len {
        let p = _mm256_loadu_pd(prices[i..].as_ptr());
        let q = _mm256_loadu_pd(quantities[i..].as_ptr());
        let result = _mm256_mul_pd(p, q);
        _mm256_storeu_pd(output[i..].as_mut_ptr(), result);
        i += 4;
    }
    
    // 處理剩餘
    while i < len {
        output[i] = prices[i] * quantities[i];
        i += 1;
    }
}

// ============ AVX2：比較（找最大價格）============
unsafe fn find_max_price_simd(prices: &[f64]) -> f64 {
    if prices.is_empty() { return 0.0; }
    
    let mut max_vec = _mm256_set1_pd(f64::MIN);
    
    let chunks = prices.chunks_exact(4);
    for chunk in chunks {
        let v = _mm256_loadu_pd(chunk.as_ptr());
        max_vec = _mm256_max_pd(max_vec, v);
    }
    
    // 提取 4 個值
    let mut result = [0.0; 4];
    _mm256_storeu_pd(result.as_mut_ptr(), max_vec);
    
    let mut max = result.iter().copied().fold(f64::MIN, f64::max);
    
    // 處理剩餘
    for &price in chunks.remainder() {
        max = max.max(price);
    }
    
    max
}

// ============ 使用 packed_simd（更簡單）============
// Cargo.toml: packed_simd = "0.3"
use packed_simd::*;

fn sum_f64_packed_simd(data: &[f64]) -> f64 {
    let mut sum = f64x4::splat(0.0);
    
    for chunk in data.chunks_exact(4) {
        let v = f64x4::from_slice_unaligned(chunk);
        sum += v;
    }
    
    sum.sum()
}

// ============ 自動向量化提示 ============
fn process_prices_auto_vec(prices: &mut [f64]) {
    // 編譯器可能自動向量化
    for price in prices {
        *price *= 1.01;  // 簡單運算容易向量化
    }
}

// 檢查是否向量化：
// RUSTFLAGS="-C opt-level=3 -C target-cpu=native" cargo build --release
// cargo asm your_crate::process_prices_auto_vec
// 看是否有 vmulpd 等 SIMD 指令
```

---

## 10. 避免 Context Switch

```rust
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Duration;

// ============ Busy-Wait（CPU 空轉）============
fn spin_wait_nanos(nanos: u64) {
    let start = std::time::Instant::now();
    while start.elapsed().as_nanos() < nanos as u128 {
        std::hint::spin_loop();  // CPU pause 指令
    }
}

// ============ 混合策略：先 spin 後 sleep ============
fn hybrid_wait(duration: Duration) {
    const SPIN_THRESHOLD: Duration = Duration::from_micros(50);
    
    if duration < SPIN_THRESHOLD {
        // 短時間：busy wait
        spin_wait_nanos(duration.as_nanos() as u64);
    } else {
        // 長時間：先 spin 一小段，再 sleep
        spin_wait_nanos(SPIN_THRESHOLD.as_nanos() as u64);
        std::thread::sleep(duration - SPIN_THRESHOLD);
    }
}

// ============ Lock-Free 輪詢 ============
use crossbeam::queue::ArrayQueue;

static QUEUE: ArrayQueue<Message> = ArrayQueue::new(1024);

fn consumer_loop() {
    loop {
        // 無鎖輪詢，不會被阻塞
        match QUEUE.pop() {
            Some(msg) => process_message(msg),
            None => std::hint::spin_loop(),  // CPU pause
        }
    }
}

// ============ 減少系統呼叫 ============
use std::io::Write;

fn batch_logging() {
    let mut buffer = Vec::with_capacity(4096);
    
    for i in 0..100 {
        // 先寫到 buffer
        writeln!(&mut buffer, "Log {}", i).unwrap();
    }
    
    // 一次性寫入（只有一次系統呼叫）
    std::io::stdout().write_all(&buffer).unwrap();
}

// ============ 禁用搶占（需要 RT priority）============
use libc::{sched_param, sched_setscheduler, SCHED_FIFO};

fn prevent_preemption() {
    unsafe {
        let param = sched_param {
            sched_priority: 99,  // 最高優先權
        };
        sched_setscheduler(0, SCHED_FIFO, &param);
    }
    
    // 現在這個執行緒只會在以下情況被中斷：
    // 1. 主動 yield
    // 2. 更高優先權的執行緒
    // 3. 硬體中斷
}
```

---

## 11. Lock-Free 程式設計

```rust
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use crossbeam::queue::{ArrayQueue, SegQueue};
use crossbeam::channel::{bounded, unbounded};

// ============ Atomic 操作 ============
struct LockFreeCounter {
    count: AtomicU64,
}

impl LockFreeCounter {
    fn new() -> Self {
        Self { count: AtomicU64::new(0) }
    }
    
    fn increment(&self) -> u64 {
        self.count.fetch_add(1, Ordering::Relaxed)
    }
    
    fn get(&self) -> u64 {
        self.count.load(Ordering::Relaxed)
    }
}

// ============ Lock-Free Queue ============
struct LockFreeQueue<T> {
    queue: ArrayQueue<T>,
}

impl<T> LockFreeQueue<T> {
    fn new(capacity: usize) -> Self {
        Self {
            queue: ArrayQueue::new(capacity),
        }
    }
    
    fn push(&self, item: T) -> Result<(), T> {
        self.queue.push(item)
    }
    
    fn pop(&self) -> Option<T> {
        self.queue.pop()
    }
}

// ============ MPSC Channel (多生產者單消費者) ============
fn use_mpsc() {
    let (tx, rx) = bounded(1000);
    
    // 多個生產者
    for i in 0..4 {
        let tx = tx.clone();
        std::thread::spawn(move || {
            for msg in 0..100 {
                tx.send((i, msg)).unwrap();
            }
        });
    }
    
    // 單一消費者
    std::thread::spawn(move || {
        while let Ok(msg) = rx.recv() {
            process_message(msg);
        }
    });
}

// ============ SPSC Channel (單生產者單消費者，最快) ============
use crossbeam::channel::unbounded;

fn use_spsc() {
    let (tx, rx) = unbounded();
    
    std::thread::spawn(move || {
        for i in 0..1000000 {
            tx.send(i).unwrap();
        }
    });
    
    std::thread::spawn(move || {
        while let Ok(msg) = rx.recv() {
            // 處理訊息
        }
    });
}

// ============ RwLock 替代方案：SeqLock ============
use seqlock::SeqLock;

struct PriceData {
    price: f64,
    volume: u64,
}

static PRICE: SeqLock<PriceData> = SeqLock::new(PriceData { 
    price: 0.0, 
    volume: 0 
});

// 寫入（單一寫入者）
fn update_price(new_price: f64, new_volume: u64) {
    *PRICE.lock_write() = PriceData {
        price: new_price,
        volume: new_volume,
    };
}

// 讀取（多個讀取者，無鎖）
fn read_price() -> PriceData {
    PRICE.read()
}

// ============ Compare-And-Swap (CAS) ============
use std::sync::atomic::AtomicPtr;

struct Node<T> {
    data: T,
    next: AtomicPtr<Node<T>>,
}

struct LockFreeStack<T> {
    head: AtomicPtr<Node<T>>,
}

impl<T> LockFreeStack<T> {
    fn push(&self, data: T) {
        let new_node = Box::into_raw(Box::new(Node {
            data,
            next: AtomicPtr::new(std::ptr::null_mut()),
        }));
        
        loop {
            let old_head = self.head.load(Ordering::Acquire);
            unsafe {
                (*new_node).next.store(old_head, Ordering::Relaxed);
            }
            
            // CAS: 如果 head 還是 old_head，就換成 new_node
            if self.head
                .compare_exchange(old_head, new_node, Ordering::Release, Ordering::Acquire)
                .is_ok()
            {
                break;
            }
        }
    }
}
```

---

## 12. 編譯器優化

### Cargo.toml 設定

```toml
[profile.release]
opt-level = 3              # 最高優化等級
lto = "fat"               # Link-Time Optimization (跨檔案優化)
codegen-units = 1         # 單一編譯單元（更好的優化，但編譯較慢）
panic = "abort"           # 移除 panic unwinding 程式碼
strip = true              # 移除除錯符號
overflow-checks = false   # 移除整數溢位檢查（小心使用）
debug = false             # 不產生除錯資訊
rpath = false             # 不使用 rpath

# 針對所有相依套件也做最佳化
[profile.release.package."*"]
opt-level = 3

# 針對特定套件
[profile.release.package.serde]
opt-level = 3

# 開發時的 release 版本（較快編譯）
[profile.dev]
opt-level = 1

# 自訂 profile
[profile.production]
inherits = "release"
lto = "fat"
codegen-units = 1
```

### 編譯時的 RUSTFLAGS

```bash
# ============ 啟用 CPU 特定指令 ============
# 方法 1: 環境變數
RUSTFLAGS="-C target-cpu=native" cargo build --release

# 方法 2: .cargo/config.toml
# [build]
# rustflags = ["-C", "target-cpu=native"]

# ============ 更多優化標記 ============
RUSTFLAGS="-C target-cpu=native \
           -C opt-level=3 \
           -C lto=fat \
           -C embed-bitcode=yes \
           -C codegen-units=1" \
cargo build --release

# ============ PGO (Profile-Guided Optimization) ============
# 步驟 1: 產生 instrumented 版本
RUSTFLAGS="-Cprofile-generate=/tmp/pgo-data" \
cargo build --release

# 步驟 2: 執行程式收集 profile 資料
./target/release/your_app

# 步驟 3: 用 profile 資料重新編譯
RUSTFLAGS="-Cprofile-use=/tmp/pgo-data/merged.profdata" \
cargo build --release

# 步驟 4: 合併 profile 資料（如果有多個）
llvm-profdata merge -o /tmp/pgo-data/merged.profdata /tmp/pgo-data/*.profraw
```

### 內聯優化

```rust
// ============ 強制內聯 ============
#[inline(always)]
fn hot_function(x: u64) -> u64 {
    x.wrapping_mul(2).wrapping_add(1)
}

// ============ 禁止內聯（冷路徑）============
#[inline(never)]
fn cold_error_path(msg: &str) {
    eprintln!("Error: {}", msg);
}

// ============ 建議內聯（讓編譯器決定）============
#[inline]
fn might_inline(x: u32) -> u32 {
    x * 2
}

// ============ const fn（編譯期計算）============
const fn calculate_table_size(n: usize) -> usize {
    n * 2 + 1
}

const TABLE_SIZE: usize = calculate_table_size(100);
static TABLE: [u8; TABLE_SIZE] = [0; TABLE_SIZE];

// ============ 編譯期常數 ============
const TICK_SIZE: f64 = 0.01;
const MAX_PRICE: u32 = 1000000;

#[inline(always)]
fn price_to_tick(price: f64) -> u32 {
    (price / TICK_SIZE) as u32
}
```

### 屬性優化

```rust
// ============ 冷/熱路徑標記 ============
#[cold]
fn handle_error() {
    // 告訴編譯器這個函數很少執行
    panic!("Error occurred");
}

#[inline(always)]
fn fast_path() {
    // 熱路徑
}

// ============ 分支預測提示 ============
fn process(x: i32) {
    if x > 0 {
        // 熱路徑
        fast_path();
    } else {
        // 冷路徑
        handle_error();
    }
}

// ============ 避免 bounds checking ============
fn sum_array(arr: &[i32]) -> i32 {
    let mut sum = 0;
    
    // ❌ 每次都檢查邊界
    for i in 0..arr.len() {
        sum += arr[i];
    }
    
    // ✅ 迭代器，編譯器可能省略檢查
    for &val in arr {
        sum += val;
    }
    
    sum
}

// ✅ 明確告訴編譯器不用檢查
unsafe fn sum_unchecked(arr: &[i32]) -> i32 {
    let mut sum = 0;
    for i in 0..arr.len() {
        sum += arr.get_unchecked(i);  // 無邊界檢查
    }
    sum
}
```

---

## 13. 系統層級調校

### 完整系統設定腳本

```bash
#!/bin/bash
# hft_system_setup.sh - 高頻交易系統調校

set -e

echo "========== 高頻交易系統調校開始 =========="

# ============ 1. Huge Pages ============
echo "[1/10] 設定 Huge Pages..."
echo 1024 | sudo tee /proc/sys/vm/nr_hugepages
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# ============ 2. CPU 性能模式 ============
echo "[2/10] 設定 CPU 為性能模式..."
for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $gov
done

# 關閉 CPU idle states (減少喚醒延遲)
for state in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
    echo 1 | sudo tee $state 2>/dev/null || true
done

# ============ 3. 關閉超執行緒（可選）============
echo "[3/10] 關閉超執行緒..."
echo off | sudo tee /sys/devices/system/cpu/smt/control

# ============ 4. 隔離 CPU 核心 ============
echo "[4/10] 設定 CPU 隔離（需要重啟）..."
GRUB_FILE="/etc/default/grub"
if grep -q "isolcpus" $GRUB_FILE; then
    echo "CPU 隔離已設定"
else
    sudo sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="isolcpus=2,3,4,5 nohz_full=2,3,4,5 rcu_nocbs=2,3,4,5"/' $GRUB_FILE
    sudo update-grub
    echo "已更新 GRUB，請重啟生效"
fi

# ============ 5. IRQ Affinity（中斷親和性）============
echo "[5/10] 設定網卡中斷親和性..."
# 把所有網卡中斷綁到 CPU 0,1
for irq in $(grep eth0 /proc/interrupts | cut -d: -f1); do
    echo 3 | sudo tee /proc/irq/$irq/smp_affinity 2>/dev/null || true
done

# ============ 6. 網路優化 ============
echo "[6/10] 網路參數優化..."
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"
sudo sysctl -w net.core.netdev_max_backlog=5000
sudo sysctl -w net.ipv4.tcp_no_metrics_save=1
sudo sysctl -w net.ipv4.tcp_timestamps=0

# ============ 7. 記憶體優化 ============
echo "[7/10] 記憶體參數優化..."
sudo sysctl -w vm.swappiness=0              # 不要 swap
sudo sysctl -w vm.dirty_ratio=80            # dirty page 比例
sudo sysctl -w vm.dirty_background_ratio=5
sudo sysctl -w vm.dirty_expire_centisecs=12000

# ============ 8. 檔案系統優化 ============
echo "[8/10] 檔案系統參數..."
sudo sysctl -w fs.file-max=2097152
ulimit -n 1048576  # 最大檔案描述符

# ============ 9. Kernel 參數持久化 ============
echo "[9/10] 寫入 /etc/sysctl.conf..."
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF

# HFT Optimizations
vm.nr_hugepages = 1024
vm.swappiness = 0
vm.dirty_ratio = 80
vm.dirty_background_ratio = 5

net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_no_metrics_save = 1

fs.file-max = 2097152
EOF

sudo sysctl -p

# ============ 10. 設定程式權限 ============
echo "[10/10] 設定程式權限..."
# 替換成你的程式路徑
APP_PATH="./target/release/trading_app"

if [ -f "$APP_PATH" ]; then
    sudo setcap cap_sys_nice,cap_ipc_lock,cap_net_raw+ep $APP_PATH
    echo "已設定 $APP_PATH 權限"
else
    echo "警告：找不到 $APP_PATH"
fi

echo "========== 系統調校完成 =========="
echo ""
echo "建議："
echo "1. 重啟系統讓 CPU 隔離生效"
echo "2. 檢查 Huge Pages: cat /proc/meminfo | grep Huge"
echo "3. 檢查 CPU 模式: cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
echo "4. 執行你的程式: $APP_PATH"
```

### 檢查與監控腳本

```bash
#!/bin/bash
# check_system.sh - 檢查系統狀態

echo "========== 系統狀態檢查 =========="

# Huge Pages
echo "[Huge Pages]"
cat /proc/meminfo | grep -i huge

# CPU 模式
echo -e "\n[CPU Governor]"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# CPU 隔離
echo -e "\n[CPU Isolation]"
cat /proc/cmdline | grep isolcpus

# 網路緩衝區
echo -e "\n[Network Buffers]"
sysctl net.core.rmem_max
sysctl net.core.wmem_max

# Swap
echo -e "\n[Swappiness]"
sysctl vm.swappiness

# 檔案限制
echo -e "\n[File Limits]"
ulimit -n
```

---

## 14. 完整範例專案

### 專案結構

```
hft-trading/
├── Cargo.toml
├── .cargo/
│   └── config.toml
├── src/
│   ├── main.rs
│   ├── trading.rs
│   ├── market_data.rs
│   └── order_book.rs
└── scripts/
    ├── setup_system.sh
    └── run.sh
```

### Cargo.toml

```toml
[package]
name = "hft-trading"
version = "0.1.0"
edition = "2021"

[dependencies]
core_affinity = "0.8"
libc = "0.2"
crossbeam = "0.8"
parking_lot = "0.12"
rustc-hash = "1.1"

[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true
overflow-checks = false

[profile.release.package."*"]
opt-level = 3
```

### .cargo/config.toml

```toml
[build]
rustflags = ["-C", "target-cpu=native", "-C", "opt-level=3"]

[target.x86_64-unknown-linux-gnu]
rustflags = [
    "-C", "target-cpu=native",
    "-C", "link-arg=-fuse-ld=lld",  # 使用更快的連結器
]
```

### src/main.rs

```rust
use core_affinity::{self, CoreId};
use std::thread;
use libc::{sched_param, sched_setscheduler, SCHED_FIFO, mlockall, MCL_CURRENT, MCL_FUTURE};

mod trading;
mod market_data;
mod order_book;

fn setup_realtime_thread(cpu: usize, priority: i32) -> Result<(), String> {
    // 1. CPU 綁定
    let core_ids = core_affinity::get_core_ids()
        .ok_or("無法獲取 CPU 核心")?;
    
    if cpu >= core_ids.len() {
        return Err(format!("CPU {} 不存在", cpu));
    }
    
    core_affinity::set_for_current(core_ids[cpu]);
    println!("執行緒綁定到 CPU {}", cpu);
    
    // 2. 設定 Real-Time 優先權
    unsafe {
        let param = sched_param {
            sched_priority: priority,
        };
        
        if sched_setscheduler(0, SCHED_FIFO, &param) != 0 {
            return Err("無法設定 RT 優先權（需要 CAP_SYS_NICE）".to_string());
        }
        println!("設定 RT 優先權: {}", priority);
        
        // 3. 鎖定記憶體
        if mlockall(MCL_CURRENT | MCL_FUTURE) != 0 {
            return Err("無法鎖定記憶體".to_string());
        }
        println!("記憶體已鎖定");
    }
    
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("========== 高頻交易系統啟動 ==========");
    
    // 交易執行緒（CPU 2，高優先權）
    let trading_handle = thread::Builder::new()
        .name("trading".to_string())
        .spawn(|| {
            if let Err(e) = setup_realtime_thread(2, 85) {
                eprintln!("交易執行緒設定失敗: {}", e);
                return;
            }
            
            trading::run();
        })?;
    
    // 市場資料執行緒（CPU 3，次高優先權）
    let market_data_handle = thread::Builder::new()
        .name("market_data".to_string())
        .spawn(|| {
            if let Err(e) = setup_realtime_thread(3, 80) {
                eprintln!("市場資料執行緒設定失敗: {}", e);
                return;
            }
            
            market_data::run();
        })?;
    
    // 等待執行緒
    trading_handle.join().unwrap();
    market_data_handle.join().unwrap();
    
    Ok(())
}
```

### src/order_book.rs

```rust
use rustc_hash::FxHashMap;
use std::sync::atomic::{AtomicU64, Ordering};

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Order {
    pub id: u64,
    pub price: u32,      // 價格 * 10000
    pub quantity: u32,
    pub is_buy: bool,
}

// SoA 結構
pub struct OrderBook {
    // 買單
    buy_prices: Vec<u32>,
    buy_quantities: Vec<u32>,
    buy_ids: Vec<u64>,
    
    // 賣單
    sell_prices: Vec<u32>,
    sell_quantities: Vec<u32>,
    sell_ids: Vec<u64>,
    
    // 統計
    total_volume: AtomicU64,
}

impl OrderBook {
    pub fn new() -> Self {
        Self {
            buy_prices: Vec::with_capacity(10000),
            buy_quantities: Vec::with_capacity(10000),
            buy_ids: Vec::with_capacity(10000),
            
            sell_prices: Vec::with_capacity(10000),
            sell_quantities: Vec::with_capacity(10000),
            sell_ids: Vec::with_capacity(10000),
            
            total_volume: AtomicU64::new(0),
        }
    }
    
    #[inline(always)]
    pub fn add_buy_order(&mut self, order: Order) {
        self.buy_prices.push(order.price);
        self.buy_quantities.push(order.quantity);
        self.buy_ids.push(order.id);
        
        self.total_volume.fetch_add(order.quantity as u64, Ordering::Relaxed);
    }
    
    #[inline(always)]
    pub fn get_best_bid(&self) -> Option<u32> {
        self.buy_prices.first().copied()
    }
    
    #[inline(always)]
    pub fn get_best_ask(&self) -> Option<u32> {
        self.sell_prices.first().copied()
    }
}
```

### scripts/run.sh

```bash
#!/bin/bash
# 編譯並執行

set -e

echo "編譯中..."
RUSTFLAGS="-C target-cpu=native" cargo build --release

echo "執行..."
sudo ./target/release/hft-trading

# 或使用 setcap
# sudo setcap cap_sys_nice,cap_ipc_lock+ep ./target/release/hft-trading
# ./target/release/hft-trading
```

---

## 15. 效能測試與監控

### Benchmark 程式碼

```rust
use std::time::Instant;

fn benchmark<F: Fn()>(name: &str, iterations: usize, f: F) {
    // 預熱
    for _ in 0..100 {
        f();
    }
    
    let start = Instant::now();
    for _ in 0..iterations {
        f();
    }
    let elapsed = start.elapsed();
    
    let avg_ns = elapsed.as_nanos() / iterations as u128;
    println!("{}: 平均 {} ns/op ({} ops)", name, avg_ns, iterations);
}

fn main() {
    const ITERATIONS: usize = 10_000_000;
    
    // 比較除法 vs 位移
    benchmark("除法", ITERATIONS, || {
        let _ = 12345 / 8;
    });
    
    benchmark("位移", ITERATIONS, || {
        let _ = 12345 >> 3;
    });
    
    // 比較浮點除法 vs 乘法
    benchmark("浮點除法", ITERATIONS, || {
        let _ = 123.45 / 100.0;
    });
    
    benchmark("浮點乘法", ITERATIONS, || {
        let _ = 123.45 * 0.01;
    });
}
```

### 監控工具

```bash
#!/bin/bash
# monitor.sh - 即時監控

APP_PID=$(pgrep trading_app)

if [ -z "$APP_PID" ]; then
    echo "找不到程式"
    exit 1
fi

echo "監控 PID: $APP_PID"

# Context Switch
watch -n 1 "cat /proc/$APP_PID/status | grep -E 'ctxt|State'"

# CPU 使用率
htop -p $APP_PID

# 效能分析
# sudo perf record -p $APP_PID -g sleep 30
# sudo perf report

# Flamegraph
# cargo install flamegraph
# sudo flamegraph -p $APP_PID
```

### 延遲測試

```rust
use std::time::Instant;

fn measure_latency() {
    let mut latencies = Vec::with_capacity(1000000);
    
    for _ in 0..1000000 {
        let start = Instant::now();
        
        // 你的關鍵路徑
        process_order();
        
        latencies.push(start.elapsed().as_nanos());
    }
    
    latencies.sort();
    
    println!("Min: {} ns", latencies[0]);
    println!("P50: {} ns", latencies[latencies.len() / 2]);
    println!("P99: {} ns", latencies[latencies.len() * 99 / 100]);
    println!("P99.9: {} ns", latencies[latencies.len() * 999 / 1000]);
    println!("Max: {} ns", latencies[latencies.len() - 1]);
}
```

---

## 總結檢查清單

### ✅ 必做優化（影響最大）

1. **CPU 綁定** - 避免 cache 失效
2. **Real-Time Priority** - 減少搶占
3. **Lock-Free 資料結構** - 避免鎖競爭
4. **Huge Pages** - 減少 TLB miss
5. **編譯優化** - `target-cpu=native`, `lto=fat`

### ⚡ 重要優化

6. **位元運算** - 替換除法/模運算
7. **查表法** - 預計算常用值
8. **Cache Line 對齊** - 避免 False Sharing
9. **SoA 資料結構** - 提升 cache 效率
10. **SIMD** - 批次處理

### 🔧 進階優化

11. **PGO** - Profile-Guided Optimization
12. **無分支程式設計** - 提升分支預測
13. **預熱 Cache** - 啟動時預載資料
14. **IRQ Affinity** - 中斷不打擾關鍵 CPU

### 📊 監控指標

- **Latency**: P50, P99, P99.9
- **Context Switch**: 應接近 0
- **Cache Miss**: 用 `perf stat` 監控
- **CPU 使用率**: 關鍵核心應 100%
