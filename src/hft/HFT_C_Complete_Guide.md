# 高頻交易 C 語言終極效能優化指南

完整涵蓋：位元運算、查表法、CPU 綁定、記憶體優化、Cache 優化、網路 I/O、FPGA 整合、系統調校

---

## 目錄

### 第一部分：基礎優化
1. [位元運算優化](#1-位元運算優化)
2. [查表法 (Lookup Table)](#2-查表法-lookup-table)
3. [分支預測優化](#3-分支預測優化)
4. [浮點數優化](#4-浮點數優化)
5. [SIMD 平行化](#5-simd-平行化)

### 第二部分：系統層級優化
6. [CPU 綁定與排程](#6-cpu-綁定與排程)
7. [記憶體與 Cache 優化](#7-記憶體與-cache-優化)
8. [Huge Pages 設定](#8-huge-pages-設定)
9. [資料結構對齊](#9-資料結構對齊)
10. [避免 Context Switch](#10-避免-context-switch)

### 第三部分：並行與無鎖
11. [Lock-Free 程式設計](#11-lock-free-程式設計)
12. [Atomic 操作](#12-atomic-操作)
13. [記憶體順序與屏障](#13-記憶體順序與屏障)

### 第四部分：編譯器優化
14. [編譯器優化選項](#14-編譯器優化選項)
15. [內聯與屬性](#15-內聯與屬性)
16. [PGO 優化](#16-pgo-優化)

### 第五部分：網路 I/O 優化
17. [傳統 Socket 優化](#17-傳統-socket-優化)
18. [零拷貝技術](#18-零拷貝技術)
19. [Kernel Bypass - DPDK](#19-kernel-bypass---dpdk)
20. [RDMA 程式設計](#20-rdma-程式設計)
21. [AF_XDP](#21-af_xdp)
22. [硬體時間戳](#22-硬體時間戳)

### 第六部分：FPGA 加速
23. [FPGA 基礎架構](#23-fpga-基礎架構)
24. [訂單處理加速](#24-訂單處理加速)
25. [市場資料解析](#25-市場資料解析)
26. [CPU-FPGA 通訊](#26-cpu-fpga-通訊)

### 第七部分：完整系統
27. [系統架構設計](#27-系統架構設計)
28. [完整範例專案](#28-完整範例專案)
29. [效能測試與監控](#29-效能測試與監控)
30. [故障排除](#30-故障排除)

---

# 第一部分：基礎優化

## 1. 位元運算優化

### 1.1 基本替換

```c
#include <stdint.h>
#include <stdio.h>

// ============ 乘法/除法替換 ============
// ❌ 慢 (~10-20 cycles)
static inline uint32_t multiply_slow(uint32_t x) {
    return x * 8;
}

static inline uint32_t divide_slow(uint32_t x) {
    return x / 16;
}

// ✅ 快 (~1-2 cycles)
static inline uint32_t multiply_fast(uint32_t x) {
    return x << 3;  // 乘以 2^3 = 8
}

static inline uint32_t divide_fast(uint32_t x) {
    return x >> 4;  // 除以 2^4 = 16
}

// ============ 模運算替換 ============
// ❌ 慢 (~20-40 cycles)
static inline uint32_t mod_slow(uint32_t x, uint32_t divisor) {
    return x % divisor;
}

// ✅ 快 - 僅適用於 2 的冪次 (~1 cycle)
static inline uint32_t mod_power_of_two(uint32_t x, uint32_t power) {
    return x & ((1 << power) - 1);
}

// 範例
static inline uint32_t mod_8(uint32_t x)   { return x & 7; }   // x % 8
static inline uint32_t mod_16(uint32_t x)  { return x & 15; }  // x % 16
static inline uint32_t mod_32(uint32_t x)  { return x & 31; }  // x % 32
static inline uint32_t mod_64(uint32_t x)  { return x & 63; }  // x % 64

// ============ 奇偶判斷 ============
static inline int is_even_slow(uint32_t x) {
    return (x % 2) == 0;
}

static inline int is_even_fast(uint32_t x) {
    return (x & 1) == 0;
}

static inline int is_odd_fast(uint32_t x) {
    return (x & 1) != 0;
}

// ============ 2 的冪次判斷 ============
static inline int is_power_of_two(uint32_t x) {
    return x != 0 && (x & (x - 1)) == 0;
}

// ============ 取絕對值 ============
static inline int32_t abs_i32(int32_t x) {
    int32_t mask = x >> 31;  // 負數: -1 (全1), 正數: 0 (全0)
    return (x ^ mask) - mask;
}

static inline int64_t abs_i64(int64_t x) {
    int64_t mask = x >> 63;
    return (x ^ mask) - mask;
}

// ============ 符號函數 ============
static inline int sign(int32_t x) {
    return (x > 0) - (x < 0);  // 返回 -1, 0, 或 1
}

// ============ 交換變數（XOR 技巧）============
static inline void swap_xor(int32_t *a, int32_t *b) {
    if (a != b) {  // 避免同一變數
        *a ^= *b;
        *b ^= *a;
        *a ^= *b;
    }
}

// ============ Min/Max（無分支）============
static inline int32_t min_branchless(int32_t a, int32_t b) {
    return b ^ ((a ^ b) & -(a < b));
}

static inline int32_t max_branchless(int32_t a, int32_t b) {
    return a ^ ((a ^ b) & -(a < b));
}

// ============ 條件選擇（無分支）============
static inline int32_t select(int condition, int32_t true_val, int32_t false_val) {
    int32_t mask = -condition;  // true: -1, false: 0
    return (true_val & mask) | (false_val & ~mask);
}

// ============ 位元操作進階 ============

// 找到最低位的 1
static inline uint64_t lowest_set_bit(uint64_t x) {
    return x & (~x + 1);
    // 或: return x & -x;
}

// 清除最低位的 1
static inline uint64_t clear_lowest_bit(uint64_t x) {
    return x & (x - 1);
}

// 計算 trailing zeros（GCC builtin）
static inline int trailing_zeros(uint64_t x) {
    return __builtin_ctzll(x);  // Count Trailing Zeros Long Long
}

// 計算 leading zeros
static inline int leading_zeros(uint64_t x) {
    return __builtin_clzll(x);  // Count Leading Zeros Long Long
}

// 計算 1 的數量（popcount）
static inline int count_ones(uint64_t x) {
    return __builtin_popcountll(x);
}

// 手動實作 popcount（如果沒有 builtin）
static inline int count_ones_manual(uint64_t x) {
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return (x * 0x0101010101010101ULL) >> 56;
}

// 位元反轉
static inline uint32_t reverse_bits(uint32_t x) {
    x = ((x & 0xAAAAAAAA) >> 1) | ((x & 0x55555555) << 1);
    x = ((x & 0xCCCCCCCC) >> 2) | ((x & 0x33333333) << 2);
    x = ((x & 0xF0F0F0F0) >> 4) | ((x & 0x0F0F0F0F) << 4);
    x = ((x & 0xFF00FF00) >> 8) | ((x & 0x00FF00FF) << 8);
    return (x >> 16) | (x << 16);
}

// 對齊到 2 的冪次
static inline uint64_t align_up(uint64_t x, uint64_t alignment) {
    return (x + alignment - 1) & ~(alignment - 1);
}

static inline uint64_t align_down(uint64_t x, uint64_t alignment) {
    return x & ~(alignment - 1);
}

// 下一個 2 的冪次
static inline uint32_t next_power_of_two(uint32_t x) {
    x--;
    x |= x >> 1;
    x |= x >> 2;
    x |= x >> 4;
    x |= x >> 8;
    x |= x >> 16;
    return x + 1;
}

// ============ 位元掃描 ============
// 找到第一個設置的位元（從 LSB）
static inline int find_first_set(uint64_t x) {
    return __builtin_ffsll(x);  // Returns 1-based index
}

// 找到最後一個設置的位元
static inline int find_last_set(uint64_t x) {
    return x ? 64 - __builtin_clzll(x) : 0;
}
```

### 1.2 交易應用範例

```c
// ============ 價格 Tick 計算 ============
#define TICK_SIZE_BITS 5  // 2^5 = 32

static inline uint32_t price_to_tick(uint32_t price) {
    return price >> TICK_SIZE_BITS;
}

static inline uint32_t tick_to_price(uint32_t tick) {
    return tick << TICK_SIZE_BITS;
}

// ============ 訂單 ID 編碼/解碼 ============
// 高 32 位：時間戳，低 32 位：序號
static inline uint64_t encode_order_id(uint32_t timestamp, uint32_t sequence) {
    return ((uint64_t)timestamp << 32) | sequence;
}

static inline uint32_t decode_timestamp(uint64_t order_id) {
    return (uint32_t)(order_id >> 32);
}

static inline uint32_t decode_sequence(uint64_t order_id) {
    return (uint32_t)(order_id & 0xFFFFFFFF);
}

// ============ 訂單標誌（Bit Flags）============
#define ORDER_BUY           (1 << 0)  // 0x01
#define ORDER_SELL          (1 << 1)  // 0x02
#define ORDER_MARKET        (1 << 2)  // 0x04
#define ORDER_LIMIT         (1 << 3)  // 0x08
#define ORDER_IOC           (1 << 4)  // 0x10 - Immediate or Cancel
#define ORDER_FOK           (1 << 5)  // 0x20 - Fill or Kill
#define ORDER_POST_ONLY     (1 << 6)  // 0x40
#define ORDER_REDUCE_ONLY   (1 << 7)  // 0x80

typedef struct {
    uint64_t order_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t flags;
    uint8_t _padding[7];
} __attribute__((packed)) Order;

// 檢查標誌
static inline int is_buy_order(const Order *order) {
    return (order->flags & ORDER_BUY) != 0;
}

static inline int is_market_order(const Order *order) {
    return (order->flags & ORDER_MARKET) != 0;
}

static inline int is_ioc_order(const Order *order) {
    return (order->flags & ORDER_IOC) != 0;
}

// 設定標誌
static inline void set_order_flag(Order *order, uint8_t flag) {
    order->flags |= flag;
}

// 清除標誌
static inline void clear_order_flag(Order *order, uint8_t flag) {
    order->flags &= ~flag;
}

// 創建標誌組合
static inline uint8_t create_order_flags(int is_buy, int is_market, int is_ioc) {
    return (is_buy ? ORDER_BUY : ORDER_SELL) |
           (is_market ? ORDER_MARKET : ORDER_LIMIT) |
           (is_ioc ? ORDER_IOC : 0);
}

// ============ 價格範圍檢查（無分支）============
static inline int price_in_range(uint32_t price, uint32_t min, uint32_t max) {
    // 利用 unsigned 溢位特性
    return (price - min) <= (max - min);
}

// ============ 循環緩衝區索引 ============
#define RING_BUFFER_SIZE 1024  // 必須是 2 的冪次
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1)

static inline uint32_t ring_buffer_index(uint32_t position) {
    return position & RING_BUFFER_MASK;
}

// ============ 快速餘數（僅 2 的冪次）============
static inline uint32_t fast_modulo_1024(uint32_t x) {
    return x & 1023;  // x % 1024
}

// ============ 位元欄位提取 ============
// 提取位元 [start, start+len)
static inline uint64_t extract_bits(uint64_t value, int start, int len) {
    return (value >> start) & ((1ULL << len) - 1);
}

// 設定位元欄位
static inline uint64_t set_bits(uint64_t value, int start, int len, uint64_t new_bits) {
    uint64_t mask = ((1ULL << len) - 1) << start;
    return (value & ~mask) | ((new_bits << start) & mask);
}
```

### 1.3 效能測試

```c
#include <time.h>

void benchmark_bit_operations(void) {
    const int ITERATIONS = 100000000;
    struct timespec start, end;
    uint64_t elapsed_ns;
    
    volatile uint32_t result;  // 防止編譯器優化掉
    uint32_t test_val = 12345;
    
    // 測試除法
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int i = 0; i < ITERATIONS; i++) {
        result = test_val / 8;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    elapsed_ns = (end.tv_sec - start.tv_sec) * 1000000000ULL + 
                 (end.tv_nsec - start.tv_nsec);
    printf("除法:     %lu ns (avg: %.2f ns)\n", 
           elapsed_ns, (double)elapsed_ns / ITERATIONS);
    
    // 測試位移
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int i = 0; i < ITERATIONS; i++) {
        result = test_val >> 3;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    elapsed_ns = (end.tv_sec - start.tv_sec) * 1000000000ULL + 
                 (end.tv_nsec - start.tv_nsec);
    printf("位移:     %lu ns (avg: %.2f ns)\n", 
           elapsed_ns, (double)elapsed_ns / ITERATIONS);
    
    // 測試模運算
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int i = 0; i < ITERATIONS; i++) {
        result = test_val % 16;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    elapsed_ns = (end.tv_sec - start.tv_sec) * 1000000000ULL + 
                 (end.tv_nsec - start.tv_nsec);
    printf("模運算:   %lu ns (avg: %.2f ns)\n", 
           elapsed_ns, (double)elapsed_ns / ITERATIONS);
    
    // 測試 AND
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int i = 0; i < ITERATIONS; i++) {
        result = test_val & 15;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);
    elapsed_ns = (end.tv_sec - start.tv_sec) * 1000000000ULL + 
                 (end.tv_nsec - start.tv_nsec);
    printf("AND運算:  %lu ns (avg: %.2f ns)\n", 
           elapsed_ns, (double)elapsed_ns / ITERATIONS);
}
```

---

## 2. 查表法 (Lookup Table)

### 2.1 基礎查表

```c
#include <stdint.h>
#include <math.h>
#include <string.h>

// ============ 位元計數表 ============
static uint8_t POPCOUNT_TABLE[256];

static void init_popcount_table(void) {
    for (int i = 0; i < 256; i++) {
        int count = 0;
        int val = i;
        while (val) {
            count += val & 1;
            val >>= 1;
        }
        POPCOUNT_TABLE[i] = count;
    }
}

static inline int popcount_lookup(uint32_t x) {
    return POPCOUNT_TABLE[x & 0xFF] +
           POPCOUNT_TABLE[(x >> 8) & 0xFF] +
           POPCOUNT_TABLE[(x >> 16) & 0xFF] +
           POPCOUNT_TABLE[(x >> 24) & 0xFF];
}

// ============ 對數表 ============
#define LOG2_TABLE_SIZE 256
static double LOG2_TABLE[LOG2_TABLE_SIZE];

static void init_log2_table(void) {
    for (int i = 1; i < LOG2_TABLE_SIZE; i++) {
        LOG2_TABLE[i] = log2((double)i);
    }
    LOG2_TABLE[0] = -INFINITY;  // log2(0) = -∞
}

static inline double fast_log2(uint32_t x) {
    if (x < LOG2_TABLE_SIZE) {
        return LOG2_TABLE[x];
    }
    return log2((double)x);  // Fallback
}

// ============ 平方根表 ============
#define SQRT_TABLE_SIZE 1024
static double SQRT_TABLE[SQRT_TABLE_SIZE];

static void init_sqrt_table(void) {
    for (int i = 0; i < SQRT_TABLE_SIZE; i++) {
        SQRT_TABLE[i] = sqrt((double)i);
    }
}

static inline double fast_sqrt_lookup(uint32_t x) {
    if (x < SQRT_TABLE_SIZE) {
        return SQRT_TABLE[x];
    }
    return sqrt((double)x);
}

// ============ 倒數表 ============
#define RECIPROCAL_TABLE_SIZE 256
static double RECIPROCAL_TABLE[RECIPROCAL_TABLE_SIZE];

static void init_reciprocal_table(void) {
    for (int i = 1; i < RECIPROCAL_TABLE_SIZE; i++) {
        RECIPROCAL_TABLE[i] = 1.0 / (double)i;
    }
    RECIPROCAL_TABLE[0] = INFINITY;
}

static inline double fast_divide(double x, uint32_t divisor) {
    if (divisor < RECIPROCAL_TABLE_SIZE) {
        return x * RECIPROCAL_TABLE[divisor];
    }
    return x / divisor;
}

// ============ 三角函數表 ============
#define TRIG_TABLE_SIZE 360
static double SIN_TABLE[TRIG_TABLE_SIZE];
static double COS_TABLE[TRIG_TABLE_SIZE];
static double TAN_TABLE[TRIG_TABLE_SIZE];

static void init_trig_tables(void) {
    for (int i = 0; i < TRIG_TABLE_SIZE; i++) {
        double rad = i * M_PI / 180.0;
        SIN_TABLE[i] = sin(rad);
        COS_TABLE[i] = cos(rad);
        TAN_TABLE[i] = tan(rad);
    }
}

static inline double fast_sin(int degrees) {
    degrees = degrees % 360;
    if (degrees < 0) degrees += 360;
    return SIN_TABLE[degrees];
}

static inline double fast_cos(int degrees) {
    degrees = degrees % 360;
    if (degrees < 0) degrees += 360;
    return COS_TABLE[degrees];
}

// ============ 指數表 ============
#define EXP_TABLE_SIZE 256
static double EXP_TABLE[EXP_TABLE_SIZE];

static void init_exp_table(void) {
    for (int i = 0; i < EXP_TABLE_SIZE; i++) {
        EXP_TABLE[i] = exp((double)i / 10.0);  // e^(i/10)
    }
}
```

### 2.2 交易應用查表

```c
// ============ 手續費計算表 ============
#define FEE_TABLE_SIZE 1000
static double FEE_TABLE[FEE_TABLE_SIZE];

static void init_fee_table(void) {
    for (int i = 0; i < FEE_TABLE_SIZE; i++) {
        if (i < 100) {
            FEE_TABLE[i] = i * 0.001;       // VIP1: 0.1%
        } else if (i < 500) {
            FEE_TABLE[i] = i * 0.0008;      // VIP2: 0.08%
        } else {
            FEE_TABLE[i] = i * 0.0005;      // VIP3: 0.05%
        }
    }
}

static inline double calculate_fee(uint32_t volume) {
    if (volume < FEE_TABLE_SIZE) {
        return FEE_TABLE[volume];
    }
    return volume * 0.0005;  // 最高等級
}

// ============ 價格等級表 ============
#define PRICE_MIN 1000000   // 10000.00 * 100
#define PRICE_MAX 2000000   // 20000.00 * 100
#define PRICE_RANGE (PRICE_MAX - PRICE_MIN + 1)

static uint16_t PRICE_LEVEL_TABLE[PRICE_RANGE];

static void init_price_level_table(void) {
    for (int i = 0; i < PRICE_RANGE; i++) {
        uint32_t price = PRICE_MIN + i;
        PRICE_LEVEL_TABLE[i] = (price - PRICE_MIN) / 100;
    }
}

static inline uint16_t get_price_level(uint32_t price) {
    if (price < PRICE_MIN || price > PRICE_MAX) {
        return 0;
    }
    return PRICE_LEVEL_TABLE[price - PRICE_MIN];
}

// ============ 波動率調整表 ============
#define VOLATILITY_BUCKETS 100
static double VOLATILITY_ADJUSTMENT[VOLATILITY_BUCKETS];

static void init_volatility_table(void) {
    for (int i = 0; i < VOLATILITY_BUCKETS; i++) {
        double vol = i * 0.01;  // 0.00 到 0.99
        if (vol < 0.2) {
            VOLATILITY_ADJUSTMENT[i] = 1.0;
        } else if (vol < 0.5) {
            VOLATILITY_ADJUSTMENT[i] = 0.95;
        } else {
            VOLATILITY_ADJUSTMENT[i] = 0.85;
        }
    }
}

static inline double get_volatility_adjustment(double volatility) {
    int bucket = (int)(volatility * 100);
    if (bucket >= VOLATILITY_BUCKETS) bucket = VOLATILITY_BUCKETS - 1;
    return VOLATILITY_ADJUSTMENT[bucket];
}

// ============ 時間衰減表（選擇權）============
#define TIME_DECAY_DAYS 365
static double TIME_DECAY[TIME_DECAY_DAYS];

static void init_time_decay_table(void) {
    for (int i = 0; i < TIME_DECAY_DAYS; i++) {
        TIME_DECAY[i] = exp(-(double)i / TIME_DECAY_DAYS);
    }
}

static inline double get_time_decay(int days_to_expiry) {
    if (days_to_expiry < 0) return 0.0;
    if (days_to_expiry >= TIME_DECAY_DAYS) days_to_expiry = TIME_DECAY_DAYS - 1;
    return TIME_DECAY[days_to_expiry];
}

// ============ CRC32 校驗表 ============
static uint32_t CRC32_TABLE[256];

static void init_crc32_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t crc = i;
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320 : 0);
        }
        CRC32_TABLE[i] = crc;
    }
}

static inline uint32_t crc32_fast(const void *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    const uint8_t *ptr = (const uint8_t*)data;
    
    for (size_t i = 0; i < len; i++) {
        crc = CRC32_TABLE[(crc ^ ptr[i]) & 0xFF] ^ (crc >> 8);
    }
    
    return ~crc;
}

// ============ 符號 ID 查找表 ============
#define MAX_SYMBOLS 10000

typedef struct {
    char symbol[16];
    uint32_t symbol_id;
    double tick_size;
    uint32_t lot_size;
} SymbolInfo;

static SymbolInfo SYMBOL_TABLE[MAX_SYMBOLS];
static int symbol_count = 0;

static void add_symbol(const char *symbol, uint32_t id, 
                      double tick_size, uint32_t lot_size) {
    if (symbol_count >= MAX_SYMBOLS) return;
    
    strncpy(SYMBOL_TABLE[symbol_count].symbol, symbol, 15);
    SYMBOL_TABLE[symbol_count].symbol[15] = '\0';
    SYMBOL_TABLE[symbol_count].symbol_id = id;
    SYMBOL_TABLE[symbol_count].tick_size = tick_size;
    SYMBOL_TABLE[symbol_count].lot_size = lot_size;
    
    symbol_count++;
}

static inline const SymbolInfo* lookup_symbol(uint32_t symbol_id) {
    // 線性搜尋（適合小表）
    for (int i = 0; i < symbol_count; i++) {
        if (SYMBOL_TABLE[i].symbol_id == symbol_id) {
            return &SYMBOL_TABLE[i];
        }
    }
    return NULL;
}

// ============ 統一初始化所有查表 ============
void init_all_lookup_tables(void) {
    init_popcount_table();
    init_log2_table();
    init_sqrt_table();
    init_reciprocal_table();
    init_trig_tables();
    init_exp_table();
    init_fee_table();
    init_price_level_table();
    init_volatility_table();
    init_time_decay_table();
    init_crc32_table();
    
    printf("All lookup tables initialized\n");
}
```

### 2.3 動態查表（Hash Table）

```c
#include <stdlib.h>

// ============ 簡單 Hash Table ============
#define HASH_TABLE_SIZE 4096
#define HASH_TABLE_MASK (HASH_TABLE_SIZE - 1)

typedef struct HashNode {
    uint64_t key;
    void *value;
    struct HashNode *next;
} HashNode;

typedef struct {
    HashNode *buckets[HASH_TABLE_SIZE];
} HashTable;

static inline uint32_t hash_function(uint64_t key) {
    // MurmurHash-inspired
    key ^= key >> 33;
    key *= 0xff51afd7ed558ccdULL;
    key ^= key >> 33;
    key *= 0xc4ceb9fe1a85ec53ULL;
    key ^= key >> 33;
    return key & HASH_TABLE_MASK;
}

HashTable* create_hash_table(void) {
    HashTable *ht = calloc(1, sizeof(HashTable));
    return ht;
}

void hash_table_insert(HashTable *ht, uint64_t key, void *value) {
    uint32_t index = hash_function(key);
    
    HashNode *node = malloc(sizeof(HashNode));
    node->key = key;
    node->value = value;
    node->next = ht->buckets[index];
    
    ht->buckets[index] = node;
}

void* hash_table_lookup(HashTable *ht, uint64_t key) {
    uint32_t index = hash_function(key);
    HashNode *node = ht->buckets[index];
    
    while (node) {
        if (node->key == key) {
            return node->value;
        }
        node = node->next;
    }
    
    return NULL;
}
```

---

## 3. 分支預測優化

### 3.1 Likely/Unlikely 提示

```c
// ============ 編譯器提示巨集 ============
#define likely(x)       __builtin_expect(!!(x), 1)
#define unlikely(x)     __builtin_expect(!!(x), 0)

// ============ 使用範例 ============
void process_order(const Order *order) {
    // 大部分訂單是買單
    if (likely(order->flags & ORDER_BUY)) {
        execute_buy_order(order);
    } else {
        execute_sell_order(order);
    }
    
    // 錯誤很少發生
    if (unlikely(order->quantity == 0)) {
        log_error("Invalid quantity");
        return;
    }
    
    // 正常處理
    validate_and_submit(order);
}

// ============ 錯誤處理 ============
int process_data(const uint8_t *data, size_t len) {
    // 快速路徑：資料有效
    if (likely(data != NULL && len > 0)) {
        return do_process(data, len);
    }
    
    // 慢速路徑：錯誤處理
    if (unlikely(data == NULL)) {
        return -1;
    }
    
    if (unlikely(len == 0)) {
        return -2;
    }
    
    return 0;
}
```

### 3.2 無分支程式設計

```c
// ============ 條件賦值（無分支）============
static inline double get_fee_rate(int is_vip) {
    // ❌ 有分支
    // return is_vip ? 0.0005 : 0.001;
    
    // ✅ 無分支
    return 0.001 - (is_vip * 0.0005);
}

// ============ 條件選擇 ============
static inline int32_t select_branchless(int condition, int32_t a, int32_t b) {
    int32_t values[2] = {b, a};
    return values[condition != 0];
}

// ============ Min/Max（無分支）============
static inline int32_t min_no_branch(int32_t a, int32_t b) {
    return b ^ ((a ^ b) & -(a < b));
}

static inline int32_t max_no_branch(int32_t a, int32_t b) {
    return a ^ ((a ^ b) & -(a < b));
}

static inline uint32_t min_u32(uint32_t a, uint32_t b) {
    return (a < b) ? a : b;  // 編譯器通常優化成 CMOV
}

// ============ Clamp（無分支）============
static inline int32_t clamp(int32_t value, int32_t min_val, int32_t max_val) {
    int32_t t = value < min_val ? min_val : value;
    return t > max_val ? max_val : t;
}

// ============ 絕對差值（無分支）============
static inline int32_t abs_diff(int32_t a, int32_t b) {
    int32_t diff = a - b;
    int32_t mask = diff >> 31;
    return (diff ^ mask) - mask;
}

// ============ 符號複製 ============
// 將 b 的符號複製到 |a|
static inline int32_t copysign_int(int32_t a, int32_t b) {
    int32_t abs_a = (a < 0) ? -a : a;
    int32_t sign = (b < 0) ? -1 : 1;
    return abs_a * sign;
}
```

### 3.3 陣列查表取代分支

```c
// ============ 用陣列取代 if-else ============

// ❌ 多重分支
const char* get_order_type_name_branched(uint8_t type) {
    if (type == 0) return "Limit";
    if (type == 1) return "Market";
    if (type == 2) return "Stop";
    if (type == 3) return "Stop-Limit";
    return "Unknown";
}

// ✅ 查表
static const char* ORDER_TYPE_NAMES[] = {
    "Limit", "Market", "Stop", "Stop-Limit", "Unknown"
};

static inline const char* get_order_type_name(uint8_t type) {
    if (type > 3) type = 4;
    return ORDER_TYPE_NAMES[type];
}

// ============ 狀態機用查表 ============
typedef void (*state_handler_t)(void*);

void handle_idle(void *ctx);
void handle_pending(void *ctx);
void handle_executing(void *ctx);
void handle_completed(void *ctx);

static const state_handler_t STATE_HANDLERS[] = {
    handle_idle,
    handle_pending,
    handle_executing,
    handle_completed
};

void process_state(uint8_t state, void *context) {
    if (state < sizeof(STATE_HANDLERS) / sizeof(STATE_HANDLERS[0])) {
        STATE_HANDLERS[state](context);
    }
}
```

### 3.4 預測友善的循環

```c
// ============ 分開處理（提升分支預測）============

// ❌ 分支預測困難
void process_orders_mixed(Order *orders, int count) {
    for (int i = 0; i < count; i++) {
        if (orders[i].flags & ORDER_BUY) {
            process_buy(&orders[i]);
        } else {
            process_sell(&orders[i]);
        }
    }
}

// ✅ 分開處理（分支預測友善）
void process_orders_separated(Order *orders, int count) {
    // 第一遍：處理所有買單
    for (int i = 0; i < count; i++) {
        if (orders[i].flags & ORDER_BUY) {
            process_buy(&orders[i]);
        }
    }
    
    // 第二遍：處理所有賣單
    for (int i = 0; i < count; i++) {
        if (!(orders[i].flags & ORDER_BUY)) {
            process_sell(&orders[i]);
        }
    }
}

// ============ 排序後處理（最佳）============
int compare_orders_by_type(const void *a, const void *b) {
    const Order *oa = (const Order*)a;
    const Order *ob = (const Order*)b;
    return (oa->flags & ORDER_BUY) - (ob->flags & ORDER_BUY);
}

void process_orders_sorted(Order *orders, int count) {
    // 先排序（買單在前，賣單在後）
    qsort(orders, count, sizeof(Order), compare_orders_by_type);
    
    // 然後處理（無分支預測失敗）
    int split_point = 0;
    for (int i = 0; i < count; i++) {
        if (!(orders[i].flags & ORDER_BUY)) {
            split_point = i;
            break;
        }
    }
    
    // 處理買單
    for (int i = 0; i < split_point; i++) {
        process_buy(&orders[i]);
    }
    
    // 處理賣單
    for (int i = split_point; i < count; i++) {
        process_sell(&orders[i]);
    }
}
```

---

## 4. 浮點數優化

### 4.1 乘法取代除法

```c
#include <math.h>

// ============ 基本替換 ============

// ❌ 慢（~10-20 cycles）
static inline double divide_slow(double x) {
    return x / 100.0;
}

// ✅ 快（~3-5 cycles）
static inline double divide_fast(double x) {
    return x * 0.01;  // 預先計算 1/100
}

// ============ 常用倒數 ============
#define INV_PI      0.318309886183790671537767526745  // 1/π
#define INV_E       0.367879441171442321595523770161  // 1/e
#define INV_SQRT2   0.707106781186547524400844362105  // 1/√2

// ============ 預計算倒數 ============
#define DIVISOR 123.456
static const double INV_DIVISOR = 1.0 / DIVISOR;

static inline double divide_by_constant(double x) {
    return x * INV_DIVISOR;
}
```

### 4.2 定點數運算

```c
// ============ 定點數價格 ============
// 使用整數表示，精度到 0.0001

typedef struct {
    int64_t value;  // 價格 * 10000
} FixedPrice;

static inline FixedPrice fixed_from_double(double price) {
    FixedPrice fp;
    fp.value = (int64_t)(price * 10000.0 + 0.5);  // 四捨五入
    return fp;
}

static inline double fixed_to_double(FixedPrice fp) {
    return fp.value * 0.0001;  // 乘法比除法快
}

static inline FixedPrice fixed_add(FixedPrice a, FixedPrice b) {
    FixedPrice result;
    result.value = a.value + b.value;
    return result;
}

static inline FixedPrice fixed_subtract(FixedPrice a, FixedPrice b) {
    FixedPrice result;
    result.value = a.value - b.value;
    return result;
}

static inline int64_t fixed_multiply(FixedPrice price, int64_t quantity) {
    return price.value * quantity;  // 結果也是 *10000
}

static inline FixedPrice fixed_divide(FixedPrice a, FixedPrice b) {
    FixedPrice result;
    result.value = (a.value * 10000) / b.value;
    return result;
}

static inline int fixed_compare(FixedPrice a, FixedPrice b) {
    if (a.value < b.value) return -1;
    if (a.value > b.value) return 1;
    return 0;
}
```

### 4.3 快速數學函數

```c
#include <immintrin.h>

// ============ 快速平方根倒數（Quake III）============
static inline float fast_inv_sqrt(float x) {
    float xhalf = 0.5f * x;
    union {
        float f;
        uint32_t i;
    } u;
    u.f = x;
    u.i = 0x5f3759df - (u.i >> 1);
    u.f = u.f * (1.5f - xhalf * u.f * u.f);  // 一次牛頓迭代
    return u.f;
}

// ============ 快速平方根 ============
static inline float fast_sqrt(float x) {
    return x * fast_inv_sqrt(x);
}

// 或使用 SSE 指令
static inline float sse_sqrt(float x) {
    __m128 v = _mm_set_ss(x);
    v = _mm_sqrt_ss(v);
    return _mm_cvtss_f32(v);
}

// ============ FMA (Fused Multiply-Add) ============
// a * b + c - 一條指令，更快更精確
static inline double fma_example(double a, double b, double c) {
    return fma(a, b, c);  // 需要 -mfma 編譯選項
}

// ============ 快速對數近似 ============
static inline float fast_log2_approx(float x) {
    union { float f; uint32_t i; } vx = { x };
    float y = vx.i;
    y *= 1.1920928955078125e-7f;  // 1 / 2^23
    return y - 126.94269504f;
}

// ============ 快速指數近似 ============
static inline float fast_exp2_approx(float x) {
    union { float f; uint32_t i; } v;
    v.i = (uint32_t)((1 << 23) * (x + 126.94269504f));
    return v.f;
}

static inline float fast_exp_approx(float x) {
    return fast_exp2_approx(1.442695040f * x);  // log2(e)
}

// ============ 快速 pow(2, x) ============
static inline float fast_pow2(float x) {
    if (x < -126.0f) return 0.0f;
    if (x > 128.0f) return INFINITY;
    
    union { float f; uint32_t i; } v;
    int i = (int)x;
    float frac = x - i;
    
    // 整數部分
    v.i = (uint32_t)((i + 127) << 23);
    
    // 小數部分近似
    v.f *= 1.0f + frac * (0.693147f + frac * (0.240153f + frac * 0.055104f));
    
    return v.f;
}
```

### 4.4 避免浮點比較

```c
#define EPSILON 1e-9
#define EPSILON_F 1e-6f

// ============ 浮點相等比較 ============
static inline int double_equals(double a, double b) {
    return fabs(a - b) < EPSILON;
}

static inline int float_equals(float a, float b) {
    return fabsf(a - b) < EPSILON_F;
}

// ============ 浮點比較（含容差）============
static inline int double_less_than(double a, double b) {
    return (b - a) > EPSILON;
}

static inline int double_greater_than(double a, double b) {
    return (a - b) > EPSILON;
}

static inline int double_less_equal(double a, double b) {
    return (a - b) <= EPSILON;
}

// ============ 整數價格比較（更好）============
typedef struct {
    int64_t value;  // 價格 * 10000
} IntPrice;

static inline int price_equals(IntPrice a, IntPrice b) {
    return a.value == b.value;
}

static inline int price_less_than(IntPrice a, IntPrice b) {
    return a.value < b.value;
}
```

### 4.5 浮點環境設定

```c
#include <fenv.h>

// ============ 設定 FPU ============
void setup_fpu(void) {
    // 禁用浮點例外（提升效能）
    fedisableexcept(FE_ALL_EXCEPT);
    
    // 設定捨入模式
    fesetround(FE_TONEAREST);  // 最近偶數捨入
    
    // 或其他模式：
    // FE_DOWNWARD    - 向下捨入
    // FE_UPWARD      - 向上捨入
    // FE_TOWARDZERO  - 向零捨入
}

// ============ 檢查浮點狀態 ============
int check_float_exceptions(void) {
    int exceptions = fetestexcept(FE_ALL_EXCEPT);
    
    if (exceptions & FE_DIVBYZERO) {
        printf("Division by zero\n");
    }
    if (exceptions & FE_INVALID) {
        printf("Invalid operation\n");
    }
    if (exceptions & FE_OVERFLOW) {
        printf("Overflow\n");
    }
    if (exceptions & FE_UNDERFLOW) {
        printf("Underflow\n");
    }
    
    // 清除例外
    feclearexcept(FE_ALL_EXCEPT);
    
    return exceptions;
}
```

---

## 5. SIMD 平行化

### 5.1 AVX2 基礎

```c
#include <immintrin.h>

// ============ 批次加法（8 個 float）============
void add_arrays_avx2(const float *a, const float *b, float *result, size_t len) {
    size_t i = 0;
    
    // 處理 8 個一組
    for (; i + 8 <= len; i += 8) {
        __m256 va = _mm256_loadu_ps(&a[i]);
        __m256 vb = _mm256_loadu_ps(&b[i]);
        __m256 vr = _mm256_add_ps(va, vb);
        _mm256_storeu_ps(&result[i], vr);
    }
    
    // 處理剩餘
    for (; i < len; i++) {
        result[i] = a[i] + b[i];
    }
}

// ============ 批次乘法（4 個 double）============
void multiply_arrays_avx2(const double *a, const double *b, double *result, size_t len) {
    size_t i = 0;
    
    for (; i + 4 <= len; i += 4) {
        __m256d va = _mm256_loadu_pd(&a[i]);
        __m256d vb = _mm256_loadu_pd(&b[i]);
        __m256d vr = _mm256_mul_pd(va, vb);
        _mm256_storeu_pd(&result[i], vr);
    }
    
    for (; i < len; i++) {
        result[i] = a[i] * b[i];
    }
}

// ============ 水平求和 ============
double sum_array_avx2(const double *data, size_t len) {
    __m256d sum_vec = _mm256_setzero_pd();
    size_t i = 0;
    
    // SIMD 累加
    for (; i + 4 <= len; i += 4) {
        __m256d v = _mm256_loadu_pd(&data[i]);
        sum_vec = _mm256_add_pd(sum_vec, v);
    }
    
    // 水平相加
    double temp[4];
    _mm256_storeu_pd(temp, sum_vec);
    double sum = temp[0] + temp[1] + temp[2] + temp[3];
    
    // 處理剩餘
    for (; i < len; i++) {
        sum += data[i];
    }
    
    return sum;
}

// ============ 找最大值 ============
double find_max_avx2(const double *data, size_t len) {
    if (len == 0) return -INFINITY;
    
    __m256d max_vec = _mm256_set1_pd(-INFINITY);
    size_t i = 0;
    
    for (; i + 4 <= len; i += 4) {
        __m256d v = _mm256_loadu_pd(&data[i]);
        max_vec = _mm256_max_pd(max_vec, v);
    }
    
    double temp[4];
    _mm256_storeu_pd(temp, max_vec);
    double max_val = fmax(fmax(temp[0], temp[1]), fmax(temp[2], temp[3]));
    
    for (; i < len; i++) {
        if (data[i] > max_val) max_val = data[i];
    }
    
    return max_val;
}

// ============ FMA (Fused Multiply-Add) ============
// result[i] = a[i] * b[i] + c[i]
void fma_arrays_avx2(const double *a, const double *b, const double *c,
                     double *result, size_t len) {
    size_t i = 0;
    
    for (; i + 4 <= len; i += 4) {
        __m256d va = _mm256_loadu_pd(&a[i]);
        __m256d vb = _mm256_loadu_pd(&b[i]);
        __m256d vc = _mm256_loadu_pd(&c[i]);
        __m256d vr = _mm256_fmadd_pd(va, vb, vc);  // a*b+c
        _mm256_storeu_pd(&result[i], vr);
    }
    
    for (; i < len; i++) {
        result[i] = a[i] * b[i] + c[i];
    }
}
```

### 5.2 交易應用範例

```c
// ============ 批次計算訂單價值 ============
// value = price * quantity
void calculate_order_values_simd(const double *prices,
                                 const double *quantities,
                                 double *values,
                                 size_t count) {
    multiply_arrays_avx2(prices, quantities, values, count);
}

// ============ 批次計算 P&L ============
// pnl = (exit_price - entry_price) * quantity
void calculate_pnl_batch(const double *entry_prices,
                         const double *exit_prices,
                         const double *quantities,
                         double *pnl,
                         size_t count) {
    double *price_diff = aligned_alloc(32, count * sizeof(double));
    
    // exit - entry
    size_t i = 0;
    for (; i + 4 <= count; i += 4) {
        __m256d exit = _mm256_loadu_pd(&exit_prices[i]);
        __m256d entry = _mm256_loadu_pd(&entry_prices[i]);
        __m256d diff = _mm256_sub_pd(exit, entry);
        _mm256_storeu_pd(&price_diff[i], diff);
    }
    for (; i < count; i++) {
        price_diff[i] = exit_prices[i] - entry_prices[i];
    }
    
    // diff * quantity
    multiply_arrays_avx2(price_diff, quantities, pnl, count);
    
    free(price_diff);
}

// ============ 批次價格範圍檢查 ============
// 返回有效價格的數量
size_t validate_prices_simd(const double *prices,
                            double min_price,
                            double max_price,
                            uint8_t *valid_flags,
                            size_t count) {
    __m256d min_vec = _mm256_set1_pd(min_price);
    __m256d max_vec = _mm256_set1_pd(max_price);
    size_t valid_count = 0;
    size_t i = 0;
    
    for (; i + 4 <= count; i += 4) {
        __m256d prices_vec = _mm256_loadu_pd(&prices[i]);
        
        // price >= min
        __m256d cmp_min = _mm256_cmp_pd(prices_vec, min_vec, _CMP_GE_OQ);
        // price <= max
        __m256d cmp_max = _mm256_cmp_pd(prices_vec, max_vec, _CMP_LE_OQ);
        // min <= price <= max
        __m256d valid = _mm256_and_pd(cmp_min, cmp_max);
        
        // 提取結果
        int mask = _mm256_movemask_pd(valid);
        for (int j = 0; j < 4; j++) {
            valid_flags[i + j] = (mask & (1 << j)) ? 1 : 0;
            valid_count += valid_flags[i + j];
        }
    }
    
    // 處理剩餘
    for (; i < count; i++) {
        valid_flags[i] = (prices[i] >= min_price && prices[i] <= max_price);
        valid_count += valid_flags[i];
    }
    
    return valid_count;
}
```

### 5.3 CPU 特性檢測

```c
#include <cpuid.h>

// ============ 檢測 CPU 支援的 SIMD 指令集 ============
typedef struct {
    int sse;
    int sse2;
    int sse3;
    int ssse3;
    int sse41;
    int sse42;
    int avx;
    int avx2;
    int fma;
    int avx512f;
} CPUFeatures;

CPUFeatures detect_cpu_features(void) {
    CPUFeatures features = {0};
    unsigned int eax, ebx, ecx, edx;
    
    // 檢查 CPUID 支援
    if (__get_cpuid_max(0, NULL) == 0) {
        return features;
    }
    
    // 功能位元 1
    __cpuid(1, eax, ebx, ecx, edx);
    
    features.sse    = (edx & bit_SSE) != 0;
    features.sse2   = (edx & bit_SSE2) != 0;
    features.sse3   = (ecx & bit_SSE3) != 0;
    features.ssse3  = (ecx & bit_SSSE3) != 0;
    features.sse41  = (ecx & bit_SSE4_1) != 0;
    features.sse42  = (ecx & bit_SSE4_2) != 0;
    features.avx    = (ecx & bit_AVX) != 0;
    features.fma    = (ecx & bit_FMA) != 0;
    
    // 功能位元 7
    if (__get_cpuid_max(0, NULL) >= 7) {
        __cpuid_count(7, 0, eax, ebx, ecx, edx);
        features.avx2     = (ebx & bit_AVX2) != 0;
        features.avx512f  = (ebx & bit_AVX512F) != 0;
    }
    
    return features;
}

void print_cpu_features(const CPUFeatures *features) {
    printf("CPU SIMD Features:\n");
    printf("  SSE:     %s\n", features->sse ? "Yes" : "No");
    printf("  SSE2:    %s\n", features->sse2 ? "Yes" : "No");
    printf("  SSE3:    %s\n", features->sse3 ? "Yes" : "No");
    printf("  SSSE3:   %s\n", features->ssse3 ? "Yes" : "No");
    printf("  SSE4.1:  %s\n", features->sse41 ? "Yes" : "No");
    printf("  SSE4.2:  %s\n", features->sse42 ? "Yes" : "No");
    printf("  AVX:     %s\n", features->avx ? "Yes" : "No");
    printf("  AVX2:    %s\n", features->avx2 ? "Yes" : "No");
    printf("  FMA:     %s\n", features->fma ? "Yes" : "No");
    printf("  AVX-512: %s\n", features->avx512f ? "Yes" : "No");
}

// ============ 動態選擇實作 ============
typedef void (*sum_func_t)(const double*, size_t, double*);

sum_func_t get_best_sum_function(void) {
    CPUFeatures features = detect_cpu_features();
    
    if (features.avx2) {
        return sum_array_avx2;
    } else if (features.sse2) {
        return sum_array_sse2;  // 需要實作
    } else {
        return sum_array_scalar;  // 標量版本
    }
}
```

---

# 第二部分：系統層級優化

## 6. CPU 綁定與排程

### 6.1 CPU Affinity

```c
#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

// ============ 綁定到單一 CPU ============
int pin_thread_to_cpu(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    
    pthread_t current_thread = pthread_self();
    int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
    
    if (result != 0) {
        perror("pthread_setaffinity_np");
        return -1;
    }
    
    printf("Thread %lu pinned to CPU %d\n", current_thread, cpu_id);
    return 0;
}

// ============ 綁定到多個 CPU ============
int pin_thread_to_cpus(const int *cpu_ids, int num_cpus) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    
    for (int i = 0; i < num_cpus; i++) {
        CPU_SET(cpu_ids[i], &cpuset);
    }
    
    pthread_t current_thread = pthread_self();
    return pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);
}

// ============ 查詢當前 CPU 綁定 ============
void print_current_affinity(void) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    
    pthread_t current_thread = pthread_self();
    if (pthread_getaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset) == 0) {
        printf("Thread %lu is bound to CPUs: ", current_thread);
        for (int i = 0; i < CPU_SETSIZE; i++) {
            if (CPU_ISSET(i, &cpuset)) {
                printf("%d ", i);
            }
        }
        printf("\n");
    }
}

// ============ 獲取可用 CPU 數量 ============
int get_num_cpus(void) {
    return sysconf(_SC_NPROCESSORS_ONLN);
}

// ============ 獲取當前執行的 CPU ============
int get_current_cpu(void) {
    return sched_getcpu();
}
```

### 6.2 Real-Time Priority

```c
#include <sys/mman.h>

// ============ 設定 Real-Time 優先權 ============
int set_realtime_priority(int priority) {
    // priority: 1-99，數字越大優先權越高
    // 建議：70-90 用於交易執行緒
    
    if (priority < 1 || priority > 99) {
        fprintf(stderr, "Priority must be 1-99\n");
        return -1;
    }
    
    struct sched_param param;
    param.sched_priority = priority;
    
    // SCHED_FIFO: 先進先出，執行到完成或主動讓出
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("sched_setscheduler");
        fprintf(stderr, "需要 CAP_SYS_NICE 權限或 sudo\n");
        return -1;
    }
    
    printf("Set real-time priority: %d (SCHED_FIFO)\n", priority);
    return 0;
}

// ============ 使用 SCHED_RR（時間片輪詢）============
int set_realtime_rr(int priority) {
    struct sched_param param;
    param.sched_priority = priority;
    
    // SCHED_RR: Round-Robin，有時間片限制
    if (sched_setscheduler(0, SCHED_RR, &param) != 0) {
        perror("sched_setscheduler (SCHED_RR)");
        return -1;
    }
    
    return 0;
}

// ============ 鎖定記憶體 ============
int lock_memory(void) {
    // 鎖定當前和未來的所有記憶體頁面
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall");
        fprintf(stderr, "需要 CAP_IPC_LOCK 權限\n");
        return -1;
    }
    
    printf("Memory locked\n");
    return 0;
}

// ============ 完整的執行緒設定 ============
int setup_realtime_thread(int cpu_id, int priority) {
    printf("Setting up real-time thread...\n");
    
    // 1. 綁定 CPU
    if (pin_thread_to_cpu(cpu_id) != 0) {
        return -1;
    }
    
    // 2. 設定 RT 優先權
    if (set_realtime_priority(priority) != 0) {
        return -1;
    }
    
    // 3. 鎖定記憶體
    if (lock_memory() != 0) {
        return -1;
    }
    
    printf("Real-time thread setup完成\n");
    return 0;
}
```

### 6.3 執行緒範例

```c
typedef struct {
    int cpu_id;
    int priority;
    void (*work_func)(void*);
    void *work_data;
} ThreadConfig;

void* realtime_thread_wrapper(void *arg) {
    ThreadConfig *config = (ThreadConfig*)arg;
    
    // 設定執行緒
    if (setup_realtime_thread(config->cpu_id, config->priority) != 0) {
        fprintf(stderr, "Failed to setup real-time thread\n");
        return NULL;
    }
    
    // 執行工作
    config->work_func(config->work_data);
    
    return NULL;
}

// ============ 使用範例 ============
void trading_work(void *data) {
    printf("Trading thread running on CPU %d\n", get_current_cpu());
    
    while (1) {
        // 交易邏輯
        process_orders();
        
        // CPU pause 指令
        __builtin_ia32_pause();
    }
}

void market_data_work(void *data) {
    printf("Market data thread running on CPU %d\n", get_current_cpu());
    
    while (1) {
        // 市場資料邏輯
        receive_market_data();
        
        __builtin_ia32_pause();
    }
}

int main(void) {
    pthread_t trading_tid, market_data_tid;
    
    // 交易執行緒配置
    ThreadConfig trading_config = {
        .cpu_id = 2,
        .priority = 85,
        .work_func = trading_work,
        .work_data = NULL
    };
    
    // 市場資料執行緒配置
    ThreadConfig market_data_config = {
        .cpu_id = 3,
        .priority = 80,
        .work_func = market_data_work,
        .work_data = NULL
    };
    
    // 創建執行緒
    if (pthread_create(&trading_tid, NULL, 
                       realtime_thread_wrapper, &trading_config) != 0) {
        perror("pthread_create (trading)");
        return 1;
    }
    
    if (pthread_create(&market_data_tid, NULL,
                       realtime_thread_wrapper, &market_data_config) != 0) {
        perror("pthread_create (market_data)");
        return 1;
    }
    
    // 等待執行緒
    pthread_join(trading_tid, NULL);
    pthread_join(market_data_tid, NULL);
    
    return 0;
}
```



### 6.4 設定資源限制

```c
#include <sys/resource.h>

void set_resource_limits(void) {
    struct rlimit rl;
    
    // 1. 最大檔案描述符
    rl.rlim_cur = 1048576;
    rl.rlim_max = 1048576;
    if (setrlimit(RLIMIT_NOFILE, &rl) != 0) {
        perror("setrlimit (NOFILE)");
    }
    
    // 2. 最大記憶體鎖定
    rl.rlim_cur = RLIM_INFINITY;
    rl.rlim_max = RLIM_INFINITY;
    if (setrlimit(RLIMIT_MEMLOCK, &rl) != 0) {
        perror("setrlimit (MEMLOCK)");
    }
    
    // 3. 核心轉儲大小
    rl.rlim_cur = 0;
    rl.rlim_max = 0;
    if (setrlimit(RLIMIT_CORE, &rl) != 0) {
        perror("setrlimit (CORE)");
    }
    
    printf("Resource limits set\n");
}

---

## 7. 記憶體與 Cache 優化

### 7.1 Cache Line 基礎

```c
#include <stdint.h>
#include <stdlib.h>

// ============ Cache Line 大小 ============
#define CACHE_LINE_SIZE 64  // 大部分 x86 CPU

// ============ Cache Line 對齊 ============
typedef struct {
    uint64_t counter;
    uint8_t _padding[CACHE_LINE_SIZE - sizeof(uint64_t)];
} __attribute__((aligned(CACHE_LINE_SIZE))) AlignedCounter;

// ============ False Sharing 範例 ============

// ❌ False Sharing - 效能差
typedef struct {
    uint64_t counter_a;  // 同一個 cache line
    uint64_t counter_b;  // 同一個 cache line
} BadCounters;

// ✅ 避免 False Sharing - 效能好
typedef struct {
    uint64_t counter_a;
    uint8_t _padding1[CACHE_LINE_SIZE - sizeof(uint64_t)];
    uint64_t counter_b;
    uint8_t _padding2[CACHE_LINE_SIZE - sizeof(uint64_t)];
} __attribute__((aligned(CACHE_LINE_SIZE))) GoodCounters;

// ============ Cache-Friendly 資料結構 ============

// ❌ 不友善 - 分散存取
typedef struct {
    char *name;        // 指標跳轉
    uint32_t price;
    uint32_t quantity;
    void *next;        // 指標跳轉
} BadOrder;

// ✅ 友善 - 連續記憶體
typedef struct {
    uint32_t price;
    uint32_t quantity;
    uint32_t symbol_id;
    uint32_t _padding;
} __attribute__((aligned(16))) GoodOrder;

// ============ 預取 (Prefetch) ============
static inline void prefetch_read(const void *addr) {
    __builtin_prefetch(addr, 0, 3);  // 0=read, 3=high temporal locality
}

static inline void prefetch_write(void *addr) {
    __builtin_prefetch(addr, 1, 3);  // 1=write
}

// 手動預取範例
void process_orders_with_prefetch(GoodOrder *orders, int count) {
    for (int i = 0; i < count; i++) {
        // 預取下一個元素
        if (i + 1 < count) {
            prefetch_read(&orders[i + 1]);
        }

        // 處理當前元素
        process_order(&orders[i]);
    }
}
```

### 7.2 記憶體池 (Memory Pool)

```c
#include <string.h>

// ============ 簡單記憶體池 ============
#define POOL_SIZE 1024
#define BLOCK_SIZE 256

typedef struct {
    uint8_t memory[POOL_SIZE * BLOCK_SIZE];
    uint8_t *free_list[POOL_SIZE];
    int free_count;
} MemoryPool;

MemoryPool* create_memory_pool(void) {
    MemoryPool *pool = aligned_alloc(CACHE_LINE_SIZE, sizeof(MemoryPool));
    if (!pool) return NULL;

    pool->free_count = POOL_SIZE;

    // 初始化 free list
    for (int i = 0; i < POOL_SIZE; i++) {
        pool->free_list[i] = &pool->memory[i * BLOCK_SIZE];
    }

    return pool;
}

void* pool_alloc(MemoryPool *pool) {
    if (pool->free_count == 0) {
        return NULL;  // 池已滿
    }

    return pool->free_list[--pool->free_count];
}

void pool_free(MemoryPool *pool, void *ptr) {
    if (pool->free_count >= POOL_SIZE) {
        return;  // 錯誤:重複釋放
    }

    pool->free_list[pool->free_count++] = (uint8_t*)ptr;
}

void destroy_memory_pool(MemoryPool *pool) {
    free(pool);
}

// ============ 訂單記憶體池 ============
typedef struct Order Order;
struct Order {
    uint64_t order_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t flags;
    uint8_t _padding[7];
};

typedef struct {
    Order orders[POOL_SIZE];
    int free_list[POOL_SIZE];
    int free_count;
} OrderPool;

OrderPool* create_order_pool(void) {
    OrderPool *pool = aligned_alloc(CACHE_LINE_SIZE, sizeof(OrderPool));
    if (!pool) return NULL;

    pool->free_count = POOL_SIZE;
    for (int i = 0; i < POOL_SIZE; i++) {
        pool->free_list[i] = i;
    }

    return pool;
}

Order* alloc_order(OrderPool *pool) {
    if (pool->free_count == 0) return NULL;

    int index = pool->free_list[--pool->free_count];
    return &pool->orders[index];
}

void free_order(OrderPool *pool, Order *order) {
    int index = order - pool->orders;
    if (index < 0 || index >= POOL_SIZE) return;

    pool->free_list[pool->free_count++] = index;
}
```

### 7.3 記憶體對齊分配

```c
#include <stdlib.h>

// ============ 對齊分配 ============
void* aligned_alloc_wrapper(size_t alignment, size_t size) {
    void *ptr = aligned_alloc(alignment, size);
    if (!ptr) {
        fprintf(stderr, "aligned_alloc failed\n");
        return NULL;
    }
    return ptr;
}

// ============ Cache Line 對齊分配 ============
void* cache_aligned_alloc(size_t size) {
    // 向上對齊到 cache line
    size_t aligned_size = (size + CACHE_LINE_SIZE - 1) & ~(CACHE_LINE_SIZE - 1);
    return aligned_alloc(CACHE_LINE_SIZE, aligned_size);
}

// ============ 分頁對齊分配 ============
#define PAGE_SIZE 4096

void* page_aligned_alloc(size_t size) {
    size_t aligned_size = (size + PAGE_SIZE - 1) & ~(PAGE_SIZE - 1);
    return aligned_alloc(PAGE_SIZE, aligned_size);
}

// ============ NUMA 感知分配 ============
#include <numaif.h>
#include <numa.h>

void* numa_alloc_on_node(size_t size, int node) {
    if (numa_available() == -1) {
        return malloc(size);
    }

    return numa_alloc_onnode(size, node);
}

void* numa_alloc_local(size_t size) {
    if (numa_available() == -1) {
        return malloc(size);
    }

    return numa_alloc_local(size);
}
```

### 7.4 Cache 優化技巧

```c
// ============ 資料打包 (Structure Packing) ============

// ❌ 未優化 - 24 bytes (有 padding)
typedef struct {
    char flag;      // 1 byte
    // 3 bytes padding
    int value;      // 4 bytes
    // 4 bytes padding (64-bit)
    void *ptr;      // 8 bytes
} UnoptimizedStruct;

// ✅ 優化 - 16 bytes (重新排序)
typedef struct {
    void *ptr;      // 8 bytes
    int value;      // 4 bytes
    char flag;      // 1 byte
    char _pad[3];   // 3 bytes explicit padding
} OptimizedStruct;

// ============ 陣列結構 vs 結構陣列 ============

// ❌ Array of Structures (AoS) - cache miss 多
typedef struct {
    double price;
    double quantity;
    double timestamp;
} Trade;

void process_prices_aos(Trade *trades, int count) {
    for (int i = 0; i < count; i++) {
        // 只需要 price,但載入整個 Trade (24 bytes)
        process_price(trades[i].price);
    }
}

// ✅ Structure of Arrays (SoA) - cache friendly
typedef struct {
    double *prices;
    double *quantities;
    double *timestamps;
    int count;
} TradesSoA;

void process_prices_soa(TradesSoA *trades) {
    // 連續存取,cache hit 率高
    for (int i = 0; i < trades->count; i++) {
        process_price(trades->prices[i]);
    }
}

// ============ 迴圈融合 (Loop Fusion) ============

// ❌ 分開迴圈 - 多次遍歷
void separate_loops(double *a, double *b, double *c, int n) {
    for (int i = 0; i < n; i++) {
        a[i] = a[i] * 2.0;
    }
    for (int i = 0; i < n; i++) {
        b[i] = b[i] + 1.0;
    }
}

// ✅ 融合迴圈 - 單次遍歷
void fused_loop(double *a, double *b, double *c, int n) {
    for (int i = 0; i < n; i++) {
        a[i] = a[i] * 2.0;
        b[i] = b[i] + 1.0;
    }
}

// ============ 迴圈展開 (Loop Unrolling) ============

// ✅ 手動展開 - 減少分支
void unrolled_sum(const double *data, int n, double *result) {
    double sum = 0.0;
    int i = 0;

    // 一次處理 4 個
    for (; i + 4 <= n; i += 4) {
        sum += data[i];
        sum += data[i + 1];
        sum += data[i + 2];
        sum += data[i + 3];
    }

    // 處理剩餘
    for (; i < n; i++) {
        sum += data[i];
    }

    *result = sum;
}

// ============ 迴圈分塊 (Loop Tiling/Blocking) ============
#define TILE_SIZE 64

void matrix_multiply_tiled(double *A, double *B, double *C, int N) {
    for (int ii = 0; ii < N; ii += TILE_SIZE) {
        for (int jj = 0; jj < N; jj += TILE_SIZE) {
            for (int kk = 0; kk < N; kk += TILE_SIZE) {
                // 處理 tile
                int i_max = (ii + TILE_SIZE < N) ? ii + TILE_SIZE : N;
                int j_max = (jj + TILE_SIZE < N) ? jj + TILE_SIZE : N;
                int k_max = (kk + TILE_SIZE < N) ? kk + TILE_SIZE : N;

                for (int i = ii; i < i_max; i++) {
                    for (int j = jj; j < j_max; j++) {
                        double sum = C[i * N + j];
                        for (int k = kk; k < k_max; k++) {
                            sum += A[i * N + k] * B[k * N + j];
                        }
                        C[i * N + j] = sum;
                    }
                }
            }
        }
    }
}
```

---

## 8. Huge Pages 設定

### 8.1 Huge Pages 基礎

```c
#include <sys/mman.h>
#include <fcntl.h>

// ============ Huge Page 大小 ============
#define HUGE_PAGE_2MB  (2UL * 1024 * 1024)
#define HUGE_PAGE_1GB  (1UL * 1024 * 1024 * 1024)

// ============ 透明 Huge Pages (THP) ============
void* alloc_with_thp(size_t size) {
    void *ptr = mmap(NULL, size,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS,
                     -1, 0);

    if (ptr == MAP_FAILED) {
        perror("mmap");
        return NULL;
    }

    // 建議使用 huge pages
    if (madvise(ptr, size, MADV_HUGEPAGE) != 0) {
        perror("madvise MADV_HUGEPAGE");
    }

    return ptr;
}

// ============ 明確使用 Huge Pages ============
void* alloc_huge_pages(size_t size) {
    // size 必須是 2MB 的倍數
    size_t aligned_size = (size + HUGE_PAGE_2MB - 1) & ~(HUGE_PAGE_2MB - 1);

    void *ptr = mmap(NULL, aligned_size,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                     -1, 0);

    if (ptr == MAP_FAILED) {
        perror("mmap MAP_HUGETLB");
        return NULL;
    }

    return ptr;
}

// ============ 使用 1GB Huge Pages ============
#ifndef MAP_HUGE_1GB
#define MAP_HUGE_1GB (30 << 26)
#endif

void* alloc_1gb_huge_pages(size_t size) {
    size_t aligned_size = (size + HUGE_PAGE_1GB - 1) & ~(HUGE_PAGE_1GB - 1);

    void *ptr = mmap(NULL, aligned_size,
                     PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB | MAP_HUGE_1GB,
                     -1, 0);

    if (ptr == MAP_FAILED) {
        perror("mmap 1GB huge pages");
        return NULL;
    }

    return ptr;
}

// ============ 釋放 Huge Pages ============
void free_huge_pages(void *ptr, size_t size) {
    if (munmap(ptr, size) != 0) {
        perror("munmap");
    }
}
```

### 8.2 Huge Pages 配置檢查

```c
#include <stdio.h>
#include <string.h>

// ============ 讀取 Huge Pages 狀態 ============
void print_hugepage_info(void) {
    FILE *fp = fopen("/proc/meminfo", "r");
    if (!fp) {
        perror("fopen /proc/meminfo");
        return;
    }

    char line[256];
    printf("\n=== Huge Pages Info ===\n");

    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "HugePages_", 10) == 0 ||
            strncmp(line, "Hugepagesize:", 13) == 0) {
            printf("%s", line);
        }
    }

    fclose(fp);
}

// ============ 檢查 THP 狀態 ============
void print_thp_status(void) {
    FILE *fp = fopen("/sys/kernel/mm/transparent_hugepage/enabled", "r");
    if (!fp) {
        printf("THP not available\n");
        return;
    }

    char line[256];
    if (fgets(line, sizeof(line), fp)) {
        printf("THP status: %s", line);
    }

    fclose(fp);
}
```

### 8.3 交易應用範例

```c
// ============ 訂單簿使用 Huge Pages ============
#define MAX_PRICE_LEVELS 100000
#define ORDERS_PER_LEVEL 100

typedef struct {
    uint64_t order_id;
    uint32_t quantity;
    uint32_t _padding;
} OrderEntry;

typedef struct {
    uint32_t price;
    uint32_t count;
    OrderEntry orders[ORDERS_PER_LEVEL];
} PriceLevel;

typedef struct {
    PriceLevel *levels;
    size_t size;
} OrderBook;

OrderBook* create_orderbook_with_hugepages(void) {
    OrderBook *book = malloc(sizeof(OrderBook));
    if (!book) return NULL;

    size_t size = MAX_PRICE_LEVELS * sizeof(PriceLevel);

    // 使用 huge pages 分配
    book->levels = alloc_with_thp(size);
    if (!book->levels) {
        free(book);
        return NULL;
    }

    book->size = size;

    // 初始化
    memset(book->levels, 0, size);

    printf("Order book allocated with huge pages (%zu MB)\n",
           size / (1024 * 1024));

    return book;
}

void destroy_orderbook(OrderBook *book) {
    if (book) {
        free_huge_pages(book->levels, book->size);
        free(book);
    }
}
```

### 8.4 系統配置腳本

```bash
#!/bin/bash
# hugepages_setup.sh

# 設定 2MB huge pages 數量
echo "Setting up 2MB huge pages..."
echo 1024 | sudo tee /proc/sys/vm/nr_hugepages

# 設定 1GB huge pages (需要在 kernel boot 時設定)
# 編輯 /etc/default/grub:
# GRUB_CMDLINE_LINUX="hugepagesz=1G hugepages=4"

# 啟用 THP
echo "Enabling THP..."
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# 檢查配置
echo ""
echo "=== Current Configuration ==="
cat /proc/meminfo | grep -i huge
```

---

## 9. 資料結構對齊

### 9.1 對齊基礎

```c
#include <stdalign.h>
#include <stddef.h>

// ============ 查詢對齊要求 ============
void print_alignment_info(void) {
    printf("Alignment requirements:\n");
    printf("  char:      %zu\n", alignof(char));
    printf("  short:     %zu\n", alignof(short));
    printf("  int:       %zu\n", alignof(int));
    printf("  long:      %zu\n", alignof(long));
    printf("  float:     %zu\n", alignof(float));
    printf("  double:    %zu\n", alignof(double));
    printf("  void*:     %zu\n", alignof(void*));
    printf("  max_align: %zu\n", alignof(max_align_t));
}

// ============ 結構體對齊 ============

// 未對齊 - 編譯器自動補齊
typedef struct {
    char a;      // 1 byte
    // 3 bytes padding
    int b;       // 4 bytes
    char c;      // 1 byte
    // 7 bytes padding
    double d;    // 8 bytes
} UnalignedStruct;  // Total: 24 bytes

// 手動優化 - 重新排序
typedef struct {
    double d;    // 8 bytes
    int b;       // 4 bytes
    char a;      // 1 byte
    char c;      // 1 byte
    char _pad[2];// 2 bytes
} AlignedStruct;  // Total: 16 bytes

// 緊密打包 (不建議用於高效能)
typedef struct {
    char a;
    int b;
    char c;
    double d;
} __attribute__((packed)) PackedStruct;  // Total: 14 bytes

// ============ 強制對齊 ============
typedef struct {
    uint64_t value;
} __attribute__((aligned(64))) CacheLineAligned;

typedef struct {
    uint64_t value;
} __attribute__((aligned(4096))) PageAligned;

// ============ 對齊檢查 ============
void check_alignment(void *ptr, size_t alignment) {
    uintptr_t addr = (uintptr_t)ptr;
    if ((addr & (alignment - 1)) == 0) {
        printf("Address %p is aligned to %zu bytes\n", ptr, alignment);
    } else {
        printf("Address %p is NOT aligned to %zu bytes\n", ptr, alignment);
    }
}
```

### 9.2 SIMD 對齊

```c
#include <immintrin.h>

// ============ AVX2 要求 32-byte 對齊 ============
typedef struct {
    double data[4];
} __attribute__((aligned(32))) AVX2Vector;

// ============ AVX-512 要求 64-byte 對齊 ============
typedef struct {
    double data[8];
} __attribute__((aligned(64))) AVX512Vector;

// ============ 對齊分配陣列 ============
double* alloc_aligned_array(size_t count, size_t alignment) {
    size_t size = count * sizeof(double);
    size_t aligned_size = (size + alignment - 1) & ~(alignment - 1);

    double *arr = aligned_alloc(alignment, aligned_size);
    if (!arr) {
        perror("aligned_alloc");
        return NULL;
    }

    return arr;
}

// ============ SIMD 運算範例 ============
void simd_add_aligned(const double *a, const double *b, double *result, size_t count) {
    // 假設 a, b, result 都是 32-byte 對齊

    size_t i = 0;
    for (; i + 4 <= count; i += 4) {
        // 使用 aligned load (更快)
        __m256d va = _mm256_load_pd(&a[i]);
        __m256d vb = _mm256_load_pd(&b[i]);
        __m256d vr = _mm256_add_pd(va, vb);
        _mm256_store_pd(&result[i], vr);
    }

    // 處理剩餘
    for (; i < count; i++) {
        result[i] = a[i] + b[i];
    }
}

// ============ 未對齊版本 ============
void simd_add_unaligned(const double *a, const double *b, double *result, size_t count) {
    size_t i = 0;
    for (; i + 4 <= count; i += 4) {
        // 使用 unaligned load (較慢)
        __m256d va = _mm256_loadu_pd(&a[i]);
        __m256d vb = _mm256_loadu_pd(&b[i]);
        __m256d vr = _mm256_add_pd(va, vb);
        _mm256_storeu_pd(&result[i], vr);
    }

    for (; i < count; i++) {
        result[i] = a[i] + b[i];
    }
}
```

### 9.3 交易資料結構對齊

```c
// ============ 市場資料 ============
typedef struct {
    uint64_t timestamp;    // 8 bytes
    uint32_t symbol_id;    // 4 bytes
    uint32_t price;        // 4 bytes
    uint32_t quantity;     // 4 bytes
    uint8_t side;          // 1 byte (buy/sell)
    uint8_t _pad[3];       // 3 bytes padding
} __attribute__((aligned(32))) MarketData;  // 24 bytes, aligned to 32

// ============ 訂單 ============
typedef struct {
    uint64_t order_id;     // 8 bytes
    uint64_t timestamp;    // 8 bytes
    uint32_t symbol_id;    // 4 bytes
    uint32_t price;        // 4 bytes
    uint32_t quantity;     // 4 bytes
    uint8_t side;          // 1 byte
    uint8_t type;          // 1 byte
    uint8_t flags;         // 1 byte
    uint8_t _pad;          // 1 byte
} __attribute__((aligned(32))) Order;  // 32 bytes, aligned to 32

// ============ 執行報告 ============
typedef struct {
    uint64_t order_id;     // 8 bytes
    uint64_t exec_id;      // 8 bytes
    uint64_t timestamp;    // 8 bytes
    uint32_t exec_price;   // 4 bytes
    uint32_t exec_qty;     // 4 bytes
    uint32_t leaves_qty;   // 4 bytes
    uint8_t exec_type;     // 1 byte
    uint8_t _pad[3];       // 3 bytes padding
} __attribute__((aligned(64))) ExecutionReport;  // 40 bytes, aligned to 64

// ============ 驗證對齊 ============
void verify_struct_alignment(void) {
    printf("Structure sizes and alignments:\n");
    printf("  MarketData: size=%zu, align=%zu\n",
           sizeof(MarketData), alignof(MarketData));
    printf("  Order: size=%zu, align=%zu\n",
           sizeof(Order), alignof(Order));
    printf("  ExecutionReport: size=%zu, align=%zu\n",
           sizeof(ExecutionReport), alignof(ExecutionReport));
}
```

---

## 10. 避免 Context Switch

### 10.1 忙等待 (Busy Waiting)

```c
#include <stdatomic.h>
#include <time.h>

// ============ CPU Pause ============
static inline void cpu_pause(void) {
    __builtin_ia32_pause();
}

// ============ Spin Lock ============
typedef struct {
    atomic_flag flag;
} SpinLock;

void spinlock_init(SpinLock *lock) {
    atomic_flag_clear(&lock->flag);
}

void spinlock_lock(SpinLock *lock) {
    while (atomic_flag_test_and_set_explicit(&lock->flag, memory_order_acquire)) {
        // 忙等待,但使用 pause 降低功耗
        cpu_pause();
    }
}

void spinlock_unlock(SpinLock *lock) {
    atomic_flag_clear_explicit(&lock->flag, memory_order_release);
}

// ============ 改良版 Spin Lock (帶退避) ============
typedef struct {
    atomic_int locked;
} AdaptiveSpinLock;

void adaptive_spinlock_init(AdaptiveSpinLock *lock) {
    atomic_store(&lock->locked, 0);
}

void adaptive_spinlock_lock(AdaptiveSpinLock *lock) {
    int spin_count = 0;
    const int max_spins = 1000;

    while (1) {
        // 嘗試獲取鎖
        int expected = 0;
        if (atomic_compare_exchange_weak(&lock->locked, &expected, 1)) {
            break;
        }

        // 指數退避
        for (int i = 0; i < (1 << (spin_count & 7)); i++) {
            cpu_pause();
        }

        spin_count++;

        // 超過最大次數後切換到 sched_yield
        if (spin_count > max_spins) {
            sched_yield();
            spin_count = 0;
        }
    }
}

void adaptive_spinlock_unlock(AdaptiveSpinLock *lock) {
    atomic_store(&lock->locked, 0);
}
```

### 10.2 無鎖環形緩衝區

```c
// ============ 單生產者單消費者環形緩衝區 ============
#define RING_BUFFER_SIZE 4096
#define RING_BUFFER_MASK (RING_BUFFER_SIZE - 1)

typedef struct {
    void *data[RING_BUFFER_SIZE];
    atomic_uint head;  // 寫位置
    atomic_uint tail;  // 讀位置
    uint8_t _pad1[CACHE_LINE_SIZE - sizeof(atomic_uint)];
    uint8_t _pad2[CACHE_LINE_SIZE - sizeof(atomic_uint)];
} SPSCRingBuffer;

void ring_buffer_init(SPSCRingBuffer *rb) {
    atomic_store_explicit(&rb->head, 0, memory_order_relaxed);
    atomic_store_explicit(&rb->tail, 0, memory_order_relaxed);
}

// 生產者寫入
int ring_buffer_push(SPSCRingBuffer *rb, void *data) {
    uint32_t head = atomic_load_explicit(&rb->head, memory_order_relaxed);
    uint32_t next_head = (head + 1) & RING_BUFFER_MASK;

    uint32_t tail = atomic_load_explicit(&rb->tail, memory_order_acquire);

    // 緩衝區已滿
    if (next_head == tail) {
        return 0;
    }

    rb->data[head] = data;

    atomic_store_explicit(&rb->head, next_head, memory_order_release);
    return 1;
}

// 消費者讀取
void* ring_buffer_pop(SPSCRingBuffer *rb) {
    uint32_t tail = atomic_load_explicit(&rb->tail, memory_order_relaxed);
    uint32_t head = atomic_load_explicit(&rb->head, memory_order_acquire);

    // 緩衝區為空
    if (tail == head) {
        return NULL;
    }

    void *data = rb->data[tail];

    uint32_t next_tail = (tail + 1) & RING_BUFFER_MASK;
    atomic_store_explicit(&rb->tail, next_tail, memory_order_release);

    return data;
}
```

### 10.3 忙輪詢 vs 阻塞

```c
// ============ 阻塞模式 (會 context switch) ============
void blocking_receiver(int sockfd) {
    char buffer[1024];

    while (1) {
        // 阻塞等待 - 會觸發 context switch
        ssize_t n = recv(sockfd, buffer, sizeof(buffer), 0);
        if (n > 0) {
            process_data(buffer, n);
        }
    }
}

// ============ 非阻塞忙輪詢 (無 context switch) ============
void busy_polling_receiver(int sockfd) {
    char buffer[1024];

    // 設為非阻塞
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

    while (1) {
        ssize_t n = recv(sockfd, buffer, sizeof(buffer), 0);

        if (n > 0) {
            process_data(buffer, n);
        } else if (n == -1 && errno == EAGAIN) {
            // 無資料,繼續輪詢
            cpu_pause();
        } else {
            // 錯誤處理
            break;
        }
    }
}

// ============ 混合模式 (輪詢 + 休眠) ============
void hybrid_receiver(int sockfd) {
    char buffer[1024];
    int consecutive_empty = 0;
    const int max_spins = 10000;

    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

    while (1) {
        ssize_t n = recv(sockfd, buffer, sizeof(buffer), 0);

        if (n > 0) {
            process_data(buffer, n);
            consecutive_empty = 0;
        } else if (n == -1 && errno == EAGAIN) {
            consecutive_empty++;

            if (consecutive_empty < max_spins) {
                // 忙輪詢
                cpu_pause();
            } else {
                // 切換到短暫休眠
                struct timespec ts = {0, 100};  // 100ns
                nanosleep(&ts, NULL);
            }
        } else {
            break;
        }
    }
}
```

### 10.4 避免系統呼叫

```c
#include <sys/eventfd.h>

// ============ 使用共享記憶體代替 pipe ============
typedef struct {
    atomic_int flag;
    uint8_t data[4096];
    uint8_t _pad[CACHE_LINE_SIZE];
} SharedBuffer;

// 寫入者
void writer_shm(SharedBuffer *buf, const void *data, size_t len) {
    memcpy(buf->data, data, len);
    atomic_store_explicit(&buf->flag, 1, memory_order_release);
}

// 讀取者 (忙輪詢)
int reader_shm(SharedBuffer *buf, void *data, size_t max_len) {
    while (atomic_load_explicit(&buf->flag, memory_order_acquire) == 0) {
        cpu_pause();
    }

    memcpy(data, buf->data, max_len);
    atomic_store_explicit(&buf->flag, 0, memory_order_release);
    return 1;
}

// ============ 批次處理減少系統呼叫 ============
#define BATCH_SIZE 100

void batch_write(int fd, const void **buffers, const size_t *sizes, int count) {
    struct iovec iov[BATCH_SIZE];

    for (int i = 0; i < count; i += BATCH_SIZE) {
        int batch = (count - i < BATCH_SIZE) ? (count - i) : BATCH_SIZE;

        for (int j = 0; j < batch; j++) {
            iov[j].iov_base = (void*)buffers[i + j];
            iov[j].iov_len = sizes[i + j];
        }

        // 一次系統呼叫寫入多個緩衝區
        writev(fd, iov, batch);
    }
}

// ============ 使用 vDSO 避免系統呼叫 ============
#include <sys/time.h>

uint64_t get_time_fast(void) {
    struct timespec ts;
    // clock_gettime 在新版 Linux 使用 vDSO,不會觸發系統呼叫
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}
```

### 10.5 執行緒親和性與隔離

```c
// ============ CPU 隔離 ============
// 在 kernel boot 參數中設定: isolcpus=2,3,4,5

int isolate_trading_thread(void) {
    // 綁定到隔離的 CPU
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);  // 使用隔離的 CPU 2

    if (pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset) != 0) {
        perror("pthread_setaffinity_np");
        return -1;
    }

    // 設定 real-time 優先權
    struct sched_param param;
    param.sched_priority = 99;

    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        perror("sched_setscheduler");
        return -1;
    }

    printf("Trading thread isolated on CPU 2 with RT priority 99\n");
    return 0;
}

// ============ 禁用中斷親和性 ============
// 腳本: disable_irq_affinity.sh
/*
#!/bin/bash
# 將網卡中斷綁定到非隔離的 CPU
for irq in $(grep eth0 /proc/interrupts | awk '{print $1}' | tr -d ':'); do
    echo 1 > /proc/irq/$irq/smp_affinity
done
*/
```

---

# 第三部分:並行與無鎖

## 11. Lock-Free 程式設計

### 11.1 Lock-Free Queue (SPSC)

```c
#include <stdatomic.h>
#include <stdlib.h>

// ============ 單生產者單消費者無鎖佇列 ============
#define QUEUE_SIZE 4096
#define QUEUE_MASK (QUEUE_SIZE - 1)

typedef struct {
    void *items[QUEUE_SIZE];
    char _pad1[CACHE_LINE_SIZE - sizeof(void*) * QUEUE_SIZE % CACHE_LINE_SIZE];
    atomic_size_t head;
    char _pad2[CACHE_LINE_SIZE - sizeof(atomic_size_t)];
    atomic_size_t tail;
    char _pad3[CACHE_LINE_SIZE - sizeof(atomic_size_t)];
} SPSCQueue;

void spsc_queue_init(SPSCQueue *q) {
    atomic_store_explicit(&q->head, 0, memory_order_relaxed);
    atomic_store_explicit(&q->tail, 0, memory_order_relaxed);
}

int spsc_queue_push(SPSCQueue *q, void *item) {
    size_t head = atomic_load_explicit(&q->head, memory_order_relaxed);
    size_t next_head = (head + 1) & QUEUE_MASK;

    // 檢查是否已滿
    if (next_head == atomic_load_explicit(&q->tail, memory_order_acquire)) {
        return 0;  // 佇列已滿
    }

    q->items[head] = item;
    atomic_store_explicit(&q->head, next_head, memory_order_release);
    return 1;
}

void* spsc_queue_pop(SPSCQueue *q) {
    size_t tail = atomic_load_explicit(&q->tail, memory_order_relaxed);

    // 檢查是否為空
    if (tail == atomic_load_explicit(&q->head, memory_order_acquire)) {
        return NULL;  // 佇列為空
    }

    void *item = q->items[tail];
    size_t next_tail = (tail + 1) & QUEUE_MASK;
    atomic_store_explicit(&q->tail, next_tail, memory_order_release);
    return item;
}
```

### 11.2 Lock-Free Stack

```c
// ============ 無鎖堆疊 (使用 CAS) ============
typedef struct StackNode {
    void *data;
    struct StackNode *next;
} StackNode;

typedef struct {
    atomic_uintptr_t head;
} LockFreeStack;

void stack_init(LockFreeStack *stack) {
    atomic_store(&stack->head, 0);
}

void stack_push(LockFreeStack *stack, StackNode *node) {
    uintptr_t old_head, new_head;

    do {
        old_head = atomic_load_explicit(&stack->head, memory_order_relaxed);
        node->next = (StackNode*)old_head;
        new_head = (uintptr_t)node;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack->head, &old_head, new_head,
        memory_order_release, memory_order_relaxed));
}

StackNode* stack_pop(LockFreeStack *stack) {
    uintptr_t old_head, new_head;
    StackNode *node;

    do {
        old_head = atomic_load_explicit(&stack->head, memory_order_acquire);
        if (old_head == 0) {
            return NULL;  // 堆疊為空
        }

        node = (StackNode*)old_head;
        new_head = (uintptr_t)node->next;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack->head, &old_head, new_head,
        memory_order_release, memory_order_acquire));

    return node;
}
```

### 11.3 Lock-Free Hash Table

```c
// ============ 簡化版無鎖 Hash Table ============
#define HASH_TABLE_SIZE 1024
#define HASH_TABLE_MASK (HASH_TABLE_SIZE - 1)

typedef struct HashEntry {
    atomic_uint64_t key;
    atomic_uintptr_t value;
} HashEntry;

typedef struct {
    HashEntry entries[HASH_TABLE_SIZE];
} LockFreeHashTable;

void hashtable_init(LockFreeHashTable *ht) {
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        atomic_store(&ht->entries[i].key, 0);
        atomic_store(&ht->entries[i].value, 0);
    }
}

static inline uint32_t hash_key(uint64_t key) {
    key ^= key >> 33;
    key *= 0xff51afd7ed558ccdULL;
    key ^= key >> 33;
    return (uint32_t)(key & HASH_TABLE_MASK);
}

int hashtable_insert(LockFreeHashTable *ht, uint64_t key, void *value) {
    if (key == 0) return 0;  // 0 是保留值

    uint32_t index = hash_key(key);
    uint32_t probe = 0;

    while (probe < HASH_TABLE_SIZE) {
        uint32_t pos = (index + probe) & HASH_TABLE_MASK;
        uint64_t expected = 0;

        // 嘗試在空位置插入
        if (atomic_compare_exchange_strong(&ht->entries[pos].key, &expected, key)) {
            atomic_store(&ht->entries[pos].value, (uintptr_t)value);
            return 1;
        }

        // 檢查是否已存在
        if (expected == key) {
            atomic_store(&ht->entries[pos].value, (uintptr_t)value);
            return 1;
        }

        probe++;
    }

    return 0;  // 表已滿
}

void* hashtable_lookup(LockFreeHashTable *ht, uint64_t key) {
    if (key == 0) return NULL;

    uint32_t index = hash_key(key);
    uint32_t probe = 0;

    while (probe < HASH_TABLE_SIZE) {
        uint32_t pos = (index + probe) & HASH_TABLE_MASK;
        uint64_t found_key = atomic_load(&ht->entries[pos].key);

        if (found_key == 0) {
            return NULL;  // 未找到
        }

        if (found_key == key) {
            return (void*)atomic_load(&ht->entries[pos].value);
        }

        probe++;
    }

    return NULL;
}
```

### 11.4 訂單簿無鎖設計

```c
// ============ 無鎖訂單簿 (簡化版) ============
#define MAX_PRICE_LEVELS 10000

typedef struct {
    uint64_t order_id;
    uint32_t quantity;
    uint32_t _padding;
} OrderEntry;

typedef struct {
    atomic_uint count;
    OrderEntry orders[100];
} PriceLevel;

typedef struct {
    PriceLevel levels[MAX_PRICE_LEVELS];
    uint32_t base_price;  // 基準價格
} LockFreeOrderBook;

void orderbook_init(LockFreeOrderBook *book, uint32_t base_price) {
    book->base_price = base_price;
    for (int i = 0; i < MAX_PRICE_LEVELS; i++) {
        atomic_store(&book->levels[i].count, 0);
    }
}

int orderbook_add_order(LockFreeOrderBook *book, uint32_t price,
                        uint64_t order_id, uint32_t quantity) {
    if (price < book->base_price) return 0;

    int level_idx = price - book->base_price;
    if (level_idx >= MAX_PRICE_LEVELS) return 0;

    PriceLevel *level = &book->levels[level_idx];

    // 嘗試加入訂單
    uint32_t count = atomic_load(&level->count);
    while (count < 100) {
        level->orders[count].order_id = order_id;
        level->orders[count].quantity = quantity;

        if (atomic_compare_exchange_weak(&level->count, &count, count + 1)) {
            return 1;
        }
        // CAS 失敗,重試
    }

    return 0;  // 該價格等級已滿
}
```

---

## 12. Atomic 操作

### 12.1 基本 Atomic 操作

```c
#include <stdatomic.h>

// ============ Atomic 類型 ============
atomic_int counter = 0;
atomic_uint64_t order_id = 0;
atomic_bool is_running = true;
atomic_uintptr_t pointer = 0;

// ============ Load/Store ============
void atomic_load_store_example(void) {
    // Load
    int value = atomic_load(&counter);
    int value_explicit = atomic_load_explicit(&counter, memory_order_acquire);

    // Store
    atomic_store(&counter, 42);
    atomic_store_explicit(&counter, 42, memory_order_release);
}

// ============ 算術操作 ============
void atomic_arithmetic_example(void) {
    // Fetch and add
    int old = atomic_fetch_add(&counter, 1);  // counter++, 返回舊值
    int old2 = atomic_fetch_add_explicit(&counter, 1, memory_order_relaxed);

    // Fetch and sub
    int old3 = atomic_fetch_sub(&counter, 1);  // counter--

    // Add and fetch (GCC extension)
    int new_val = __atomic_add_fetch(&counter, 1, __ATOMIC_SEQ_CST);
}

// ============ 位元操作 ============
void atomic_bitwise_example(void) {
    atomic_uint flags = 0;

    // OR
    atomic_fetch_or(&flags, 0x01);  // 設定 bit 0

    // AND
    atomic_fetch_and(&flags, ~0x02);  // 清除 bit 1

    // XOR
    atomic_fetch_xor(&flags, 0x04);  // 切換 bit 2
}

// ============ Compare-And-Swap ============
void atomic_cas_example(void) {
    atomic_int value = 10;

    // Weak CAS (可能偽失敗,用於循環)
    int expected = 10;
    int desired = 20;
    if (atomic_compare_exchange_weak(&value, &expected, desired)) {
        printf("CAS succeeded\n");
    } else {
        printf("CAS failed, current value: %d\n", expected);
    }

    // Strong CAS (不會偽失敗)
    expected = 20;
    desired = 30;
    if (atomic_compare_exchange_strong(&value, &expected, desired)) {
        printf("CAS succeeded\n");
    }
}

// ============ Exchange ============
void atomic_exchange_example(void) {
    atomic_int value = 10;

    // 交換值,返回舊值
    int old = atomic_exchange(&value, 20);
    printf("Old: %d, New: %d\n", old, atomic_load(&value));
}
```

### 12.2 實用 Atomic 模式

```c
// ============ Atomic Flag (簡單鎖) ============
atomic_flag lock = ATOMIC_FLAG_INIT;

void lock_acquire(void) {
    while (atomic_flag_test_and_set(&lock)) {
        // Spin
        __builtin_ia32_pause();
    }
}

void lock_release(void) {
    atomic_flag_clear(&lock);
}

// ============ 引用計數 ============
typedef struct {
    void *data;
    atomic_int ref_count;
} RefCounted;

RefCounted* refcount_create(void *data) {
    RefCounted *rc = malloc(sizeof(RefCounted));
    rc->data = data;
    atomic_store(&rc->ref_count, 1);
    return rc;
}

void refcount_retain(RefCounted *rc) {
    atomic_fetch_add(&rc->ref_count, 1);
}

void refcount_release(RefCounted *rc) {
    if (atomic_fetch_sub(&rc->ref_count, 1) == 1) {
        // 最後一個引用
        free(rc->data);
        free(rc);
    }
}

// ============ 序號生成器 ============
atomic_uint64_t global_sequence = 0;

uint64_t generate_sequence_number(void) {
    return atomic_fetch_add(&global_sequence, 1);
}

// ============ 狀態機 ============
enum State {
    STATE_IDLE = 0,
    STATE_CONNECTING,
    STATE_CONNECTED,
    STATE_DISCONNECTED
};

atomic_int connection_state = STATE_IDLE;

int try_transition_state(enum State from, enum State to) {
    int expected = from;
    return atomic_compare_exchange_strong(&connection_state, &expected, to);
}

// ============ Double-Checked Locking ============
atomic_bool initialized = false;
atomic_flag init_lock = ATOMIC_FLAG_INIT;
void *singleton = NULL;

void* get_singleton(void) {
    // 第一次檢查(無鎖)
    if (!atomic_load_explicit(&initialized, memory_order_acquire)) {
        // 獲取鎖
        while (atomic_flag_test_and_set(&init_lock)) {
            __builtin_ia32_pause();
        }

        // 第二次檢查(持鎖)
        if (!atomic_load(&initialized)) {
            singleton = create_singleton();
            atomic_store_explicit(&initialized, true, memory_order_release);
        }

        atomic_flag_clear(&init_lock);
    }

    return singleton;
}
```

### 12.3 Atomic 效能優化

```c
// ============ 避免 False Sharing ============
typedef struct {
    atomic_int counter;
    char _pad[CACHE_LINE_SIZE - sizeof(atomic_int)];
} PaddedCounter;

// ============ 批次累加 ============
typedef struct {
    atomic_int global_counter;
    char _pad1[CACHE_LINE_SIZE - sizeof(atomic_int)];
} GlobalCounter;

typedef struct {
    int local_counter;
    char _pad[CACHE_LINE_SIZE - sizeof(int)];
} ThreadLocalCounter;

#define NUM_THREADS 4
ThreadLocalCounter thread_counters[NUM_THREADS];
GlobalCounter global_counter;

void thread_increment(int thread_id) {
    thread_counters[thread_id].local_counter++;

    // 每 1000 次同步一次
    if (thread_counters[thread_id].local_counter >= 1000) {
        atomic_fetch_add(&global_counter.global_counter,
                        thread_counters[thread_id].local_counter);
        thread_counters[thread_id].local_counter = 0;
    }
}

int get_total_count(void) {
    int total = atomic_load(&global_counter.global_counter);

    for (int i = 0; i < NUM_THREADS; i++) {
        total += thread_counters[i].local_counter;
    }

    return total;
}
```

---

## 13. 記憶體順序與屏障

### 13.1 記憶體順序基礎

```c
// ============ 記憶體順序類型 ============

// 1. Relaxed - 無同步保證,只保證原子性
void relaxed_example(void) {
    atomic_int x = 0;
    atomic_int y = 0;

    // Thread 1
    atomic_store_explicit(&x, 1, memory_order_relaxed);
    atomic_store_explicit(&y, 2, memory_order_relaxed);

    // Thread 2 可能看到 y=2 但 x=0 (重排)
}

// 2. Acquire/Release - 同步點
void acquire_release_example(void) {
    atomic_int flag = 0;
    int data = 0;

    // Producer (Thread 1)
    data = 42;  // (1)
    atomic_store_explicit(&flag, 1, memory_order_release);  // (2)
    // (1) happens-before (2)

    // Consumer (Thread 2)
    while (atomic_load_explicit(&flag, memory_order_acquire) == 0);  // (3)
    int value = data;  // (4)
    // (3) synchronizes-with (2)
    // (1) happens-before (4)

    printf("data = %d\n", value);  // 保證是 42
}

// 3. Sequential Consistency - 全局順序
void seq_cst_example(void) {
    atomic_int x = 0;
    atomic_int y = 0;
    atomic_int r1, r2;

    // Thread 1
    atomic_store(&x, 1);  // 默認是 seq_cst
    r1 = atomic_load(&y);

    // Thread 2
    atomic_store(&y, 1);
    r2 = atomic_load(&x);

    // 不可能 r1 == 0 && r2 == 0
}
```

### 13.2 記憶體屏障

```c
// ============ 完整屏障 ============
void full_barrier_example(void) {
    atomic_thread_fence(memory_order_seq_cst);
}

// ============ Acquire 屏障 ============
void acquire_fence_example(void) {
    atomic_thread_fence(memory_order_acquire);
    // 阻止後面的讀取被重排到前面
}

// ============ Release 屏障 ============
void release_fence_example(void) {
    atomic_thread_fence(memory_order_release);
    // 阻止前面的寫入被重排到後面
}

// ============ 編譯器屏障 ============
void compiler_barrier(void) {
    asm volatile("" ::: "memory");
}
```

### 13.3 實際應用範例

```c
// ============ 生產者-消費者 (正確版本) ============
typedef struct {
    int data[1024];
    atomic_int write_pos;
    atomic_int read_pos;
} RingBuffer;

void producer_write(RingBuffer *rb, int value, int pos) {
    rb->data[pos] = value;  // (1) 寫入資料

    // Release: 確保 (1) 在 (2) 之前完成
    atomic_store_explicit(&rb->write_pos, pos + 1, memory_order_release);  // (2)
}

int consumer_read(RingBuffer *rb) {
    // Acquire: 確保 (3) 在 (4) 之前完成
    int pos = atomic_load_explicit(&rb->read_pos, memory_order_acquire);  // (3)
    int value = rb->data[pos];  // (4) 讀取資料

    atomic_store_explicit(&rb->read_pos, pos + 1, memory_order_release);
    return value;
}

// ============ 雙重檢查鎖定 (正確版本) ============
atomic_int initialized = 0;
void *data = NULL;

void* get_data(void) {
    // Acquire: 同步 initialization
    if (atomic_load_explicit(&initialized, memory_order_acquire) == 0) {
        // 初始化邏輯(加鎖)
        data = init_data();

        // Release: 確保 data 寫入完成
        atomic_store_explicit(&initialized, 1, memory_order_release);
    }

    return data;
}

// ============ 無鎖發布 ============
typedef struct {
    int value1;
    int value2;
    atomic_bool ready;
} Message;

void publish_message(Message *msg, int v1, int v2) {
    msg->value1 = v1;  // (1)
    msg->value2 = v2;  // (2)

    // Release: 確保 (1)(2) 在 (3) 之前
    atomic_store_explicit(&msg->ready, true, memory_order_release);  // (3)
}

void consume_message(Message *msg) {
    // Acquire: 同步 ready 標誌
    while (!atomic_load_explicit(&msg->ready, memory_order_acquire));  // (4)

    // 現在安全讀取
    printf("v1=%d, v2=%d\n", msg->value1, msg->value2);
}
```

### 13.4 記憶體順序選擇指南

```c
// ============ 使用建議 ============

/*
1. Relaxed (memory_order_relaxed)
   - 用於:計數器、統計資料
   - 特點:最快,但無同步保證
   - 範例:
*/
atomic_int stats_counter;
atomic_fetch_add_explicit(&stats_counter, 1, memory_order_relaxed);

/*
2. Acquire/Release (memory_order_acquire/release)
   - 用於:生產者-消費者、發布-訂閱
   - 特點:性能好,提供單向同步
   - 範例:見上方 producer_write/consumer_read
*/

/*
3. Sequential Consistency (memory_order_seq_cst)
   - 用於:複雜的多執行緒邏輯
   - 特點:最慢,但最安全
   - 範例:
*/
atomic_int x, y;
atomic_store(&x, 1);  // 默認 seq_cst
atomic_store(&y, 1);

/*
4. Consume (memory_order_consume)
   - 用於:依賴鏈優化
   - 特點:Linux kernel 常用,但 C11 不推薦
   - 建議:用 acquire 代替
*/
```

---

# 第四部分:編譯器優化

## 14. 編譯器優化選項

### 14.1 GCC 優化等級

```bash
# ============ 基本優化等級 ============

# -O0: 無優化 (默認,用於 debug)
gcc -O0 -g main.c -o main_debug

# -O1: 基本優化,不影響編譯速度
gcc -O1 main.c -o main_o1

# -O2: 推薦的優化等級 (平衡)
gcc -O2 main.c -o main_o2

# -O3: 激進優化 (可能增加程式大小)
gcc -O3 main.c -o main_o3

# -Os: 優化程式大小
gcc -Os main.c -o main_small

# -Ofast: 最激進優化 (可能違反標準)
gcc -Ofast main.c -o main_fast
```

### 14.2 HFT 推薦編譯選項

```makefile
# ============ Makefile 範例 ============
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -pedantic

# 基本優化
OPTFLAGS = -O3 -march=native -mtune=native

# SIMD
SIMDFLAGS = -mavx2 -mfma

# 安全優化
SAFEFLAGS = -fno-strict-aliasing -fwrapv

# Link-Time Optimization
LTOFLAGS = -flto

# 完整優化
CFLAGS_OPT = $(CFLAGS) $(OPTFLAGS) $(SIMDFLAGS) $(SAFEFLAGS) $(LTOFLAGS)

# 編譯
trading: main.c order.c market.c
	$(CC) $(CFLAGS_OPT) $^ -o $@ -lpthread -lm

# 帶 debug 資訊的優化版本
trading_debug: main.c order.c market.c
	$(CC) $(CFLAGS_OPT) -g $^ -o $@ -lpthread -lm
```

### 14.3 重要編譯選項詳解

```bash
# ============ CPU 特定優化 ============

# 針對當前 CPU 架構優化
gcc -march=native -mtune=native main.c

# 指定 CPU 架構
gcc -march=skylake -mtune=skylake main.c
gcc -march=haswell -mtune=haswell main.c

# ============ SIMD 指令集 ============

# SSE4.2
gcc -msse4.2 main.c

# AVX
gcc -mavx main.c

# AVX2 + FMA
gcc -mavx2 -mfma main.c

# AVX-512
gcc -mavx512f main.c

# ============ Link-Time Optimization ============

# 編譯時
gcc -O3 -flto -c file1.c -o file1.o
gcc -O3 -flto -c file2.c -o file2.o

# 連結時
gcc -O3 -flto file1.o file2.o -o program

# ============ 函數優化 ============

# 內聯限制
gcc -finline-limit=1000 main.c

# 不展開迴圈
gcc -fno-unroll-loops main.c

# 展開所有迴圈
gcc -funroll-all-loops main.c

# ============ 數學優化 ============

# 快速數學 (不遵守 IEEE 754)
gcc -ffast-math main.c

# 個別控制
gcc -fno-math-errno main.c          # 不設置 errno
gcc -fno-trapping-math main.c       # 假設無浮點例外
gcc -ffinite-math-only main.c       # 假設無 inf/nan
gcc -freciprocal-math main.c        # 用乘法代替除法

# ============ 分支優化 ============

# 使用 profile 資訊
gcc -fprofile-use main.c

# 預測分支
gcc -fpredict-loop-iterations main.c
```

### 14.4 效能測試腳本

```bash
#!/bin/bash
# benchmark_compiler_flags.sh

SOURCE="trading_engine.c"
ITERATIONS=1000000

echo "Compiler Flags Benchmark"
echo "========================"

# O2
gcc -O2 $SOURCE -o test_o2
time ./test_o2 $ITERATIONS
echo ""

# O3
gcc -O3 $SOURCE -o test_o3
time ./test_o3 $ITERATIONS
echo ""

# O3 + march=native
gcc -O3 -march=native $SOURCE -o test_native
time ./test_native $ITERATIONS
echo ""

# O3 + march=native + flto
gcc -O3 -march=native -flto $SOURCE -o test_lto
time ./test_lto $ITERATIONS
echo ""

# Ofast
gcc -Ofast -march=native -flto $SOURCE -o test_fast
time ./test_fast $ITERATIONS
echo ""
```

---

## 15. 內聯與屬性

### 15.1 函數內聯

```c
// ============ 基本 inline ============
static inline int add(int a, int b) {
    return a + b;
}

// ============ 強制內聯 ============
__attribute__((always_inline))
static inline uint32_t fast_modulo(uint32_t x, uint32_t divisor) {
    return x & (divisor - 1);
}

// ============ 禁止內聯 ============
__attribute__((noinline))
void debug_function(void) {
    printf("This function will never be inlined\n");
}

// ============ 內聯決策 ============
// 讓編譯器決定
static inline int maybe_inline(int x) {
    // 小函數,通常會內聯
    return x * 2;
}

// 大函數,可能不會內聯
static inline int complex_function(int x) {
    int result = 0;
    for (int i = 0; i < 100; i++) {
        result += x * i;
    }
    return result;
}
```

### 15.2 函數屬性

```c
// ============ Pure 函數 ============
// 不修改全局狀態,只依賴參數
__attribute__((pure))
int calculate_hash(int x) {
    return x * 31 + 17;
}

// ============ Const 函數 ============
// 不讀取記憶體,只依賴參數
__attribute__((const))
int square(int x) {
    return x * x;
}

// ============ Hot/Cold 函數 ============
// 經常呼叫的熱點函數
__attribute__((hot))
void process_order(Order *order) {
    // 交易核心邏輯
}

// 很少呼叫的冷門函數
__attribute__((cold))
void handle_error(const char *msg) {
    fprintf(stderr, "Error: %s\n", msg);
}

// ============ 預期條件 ============
int process_data(void *data) {
    if (__builtin_expect(data == NULL, 0)) {
        return -1;  // 不太可能
    }

    // 正常處理
    return 0;
}

// ============ 無返回函數 ============
__attribute__((noreturn))
void fatal_error(const char *msg) {
    fprintf(stderr, "Fatal: %s\n", msg);
    exit(1);
}

// ============ 格式檢查 ============
__attribute__((format(printf, 1, 2)))
void log_message(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
}

// ============ 警告未使用返回值 ============
__attribute__((warn_unused_result))
int important_function(void) {
    return 42;
}

// ============ 建議對齊 ============
__attribute__((aligned(64)))
typedef struct {
    int value;
} CacheAlignedInt;

// ============ 緊密打包 ============
__attribute__((packed))
typedef struct {
    char a;
    int b;
    char c;
} PackedStruct;
```

### 15.3 變數屬性

```c
// ============ 對齊 ============
__attribute__((aligned(64)))
int cache_line_var;

// ============ Section 指定 ============
__attribute__((section(".critical")))
void critical_function(void) {
    // 放在特定 section
}

// ============ 未使用警告抑制 ============
__attribute__((unused))
static int debug_var = 0;

// ============ TLS (Thread-Local Storage) ============
__thread int thread_local_counter = 0;

// ============ Weak Symbol ============
__attribute__((weak))
void optional_hook(void) {
    // 可以被覆蓋的弱符號
}

// ============ Visibility ============
__attribute__((visibility("hidden")))
void internal_function(void) {
    // 隱藏符號,不導出
}

__attribute__((visibility("default")))
void public_function(void) {
    // 公開符號
}
```

### 15.4 交易應用範例

```c
// ============ 訂單處理 (高度優化) ============

__attribute__((always_inline, hot))
static inline uint64_t encode_order_id(uint32_t timestamp, uint32_t seq) {
    return ((uint64_t)timestamp << 32) | seq;
}

__attribute__((always_inline, hot))
static inline uint32_t price_to_level(uint32_t price, uint32_t tick_size) {
    return price / tick_size;
}

__attribute__((hot))
void process_market_order(Order *order) {
    // 熱點路徑
    validate_order(order);
    match_order(order);
}

__attribute__((cold))
void reject_order(Order *order, const char *reason) {
    // 冷門路徑
    log_rejection(order, reason);
}

// ============ 純函數優化 ============

__attribute__((const))
static inline int is_power_of_two(uint32_t x) {
    return x != 0 && (x & (x - 1)) == 0;
}

__attribute__((pure))
uint32_t calculate_checksum(const void *data, size_t len) {
    uint32_t sum = 0;
    const uint8_t *ptr = data;
    for (size_t i = 0; i < len; i++) {
        sum += ptr[i];
    }
    return sum;
}
```

---

## 16. PGO 優化

### 16.1 Profile-Guided Optimization 基礎

```bash
# ============ 三步驟流程 ============

# Step 1: 編譯帶 instrumentation 的版本
gcc -O3 -fprofile-generate main.c -o main_profiling

# Step 2: 執行程式,收集 profile 資料
./main_profiling < typical_workload.dat
# 產生 *.gcda 檔案

# Step 3: 使用 profile 重新編譯
gcc -O3 -fprofile-use main.c -o main_optimized

# 清理 profile 資料
rm -f *.gcda
```

### 16.2 完整 Makefile 範例

```makefile
CC = gcc
CFLAGS = -std=c11 -O3 -march=native -Wall
LDFLAGS = -lpthread -lm

SOURCES = main.c order.c market.c
PROFILE_DIR = profile_data

.PHONY: all clean profile

# 正常編譯
all: trading

trading: $(SOURCES)
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

# PGO 優化編譯
pgo: trading_pgo

# Step 1: 編譯 instrumentation 版本
trading_instrumented: $(SOURCES)
	mkdir -p $(PROFILE_DIR)
	$(CC) $(CFLAGS) -fprofile-generate=$(PROFILE_DIR) $^ -o $@ $(LDFLAGS)

# Step 2: 執行並收集 profile (手動執行)
# ./trading_instrumented --benchmark

# Step 3: 使用 profile 編譯
trading_pgo: $(SOURCES) | profile_exists
	$(CC) $(CFLAGS) -fprofile-use=$(PROFILE_DIR) $^ -o $@ $(LDFLAGS)

profile_exists:
	@if [ ! -d $(PROFILE_DIR) ] || [ -z "$$(ls -A $(PROFILE_DIR))" ]; then \
		echo "Error: Run 'make profile' first to generate profile data"; \
		exit 1; \
	fi

# 自動化 profile 流程
profile: trading_instrumented
	@echo "Running profiling workload..."
	./trading_instrumented --benchmark --iterations 1000000
	@echo "Profile data collected in $(PROFILE_DIR)/"
	@echo "Now run 'make trading_pgo' to build optimized version"

clean:
	rm -f trading trading_instrumented trading_pgo
	rm -rf $(PROFILE_DIR)
```

### 16.3 Profile 工作負載

```c
// ============ benchmark.c - 代表性工作負載 ============
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct {
    uint64_t order_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t side;
} Order;

void process_order(Order *order);
void match_order(Order *order);
void cancel_order(uint64_t order_id);

void run_benchmark(int iterations) {
    srand(time(NULL));

    for (int i = 0; i < iterations; i++) {
        Order order;
        order.order_id = i;
        order.price = 10000 + rand() % 100;
        order.quantity = 100 + rand() % 900;
        order.side = rand() % 2;

        // 90% 處理訂單
        if (rand() % 100 < 90) {
            process_order(&order);

            // 70% 會成交
            if (rand() % 100 < 70) {
                match_order(&order);
            }
        }
        // 10% 取消訂單
        else {
            if (i > 0) {
                cancel_order(rand() % i);
            }
        }
    }
}

int main(int argc, char *argv[]) {
    int iterations = 100000;

    if (argc > 2 && strcmp(argv[1], "--iterations") == 0) {
        iterations = atoi(argv[2]);
    }

    printf("Running benchmark with %d iterations\n", iterations);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    run_benchmark(iterations);

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = (end.tv_sec - start.tv_sec) +
                     (end.tv_nsec - start.tv_nsec) / 1e9;

    printf("Elapsed: %.3f seconds\n", elapsed);
    printf("Throughput: %.0f ops/sec\n", iterations / elapsed);

    return 0;
}
```

### 16.4 PGO 效果驗證

```bash
#!/bin/bash
# compare_pgo.sh - 比較 PGO 前後效能

echo "Building versions..."

# 無優化
gcc -O3 main.c -o trading_o3

# PGO 優化
make profile
make trading_pgo

echo ""
echo "Benchmarking..."
echo "==============="

echo "O3 only:"
time ./trading_o3 --iterations 1000000

echo ""
echo "O3 + PGO:"
time ./trading_pgo --iterations 1000000
```

---

# 第五部分:網路 I/O 優化

## 17. 傳統 Socket 優化

### 17.1 基本 Socket 設定

```c
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <fcntl.h>
#include <unistd.h>

// ============ 創建優化的 Socket ============
int create_optimized_socket(void) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return -1;
    }

    // 1. 禁用 Nagle 算法 (減少延遲)
    int flag = 1;
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag)) < 0) {
        perror("TCP_NODELAY");
    }

    // 2. 啟用 SO_REUSEADDR
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag)) < 0) {
        perror("SO_REUSEADDR");
    }

    // 3. 啟用 SO_REUSEPORT (多執行緒綁定同一 port)
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &flag, sizeof(flag)) < 0) {
        perror("SO_REUSEPORT");
    }

    // 4. 設定接收緩衝區大小
    int rcvbuf = 2 * 1024 * 1024;  // 2MB
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf)) < 0) {
        perror("SO_RCVBUF");
    }

    // 5. 設定發送緩衝區大小
    int sndbuf = 2 * 1024 * 1024;  // 2MB
    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf)) < 0) {
        perror("SO_SNDBUF");
    }

    // 6. 設定 TCP Quickack (立即 ACK)
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK, &flag, sizeof(flag)) < 0) {
        perror("TCP_QUICKACK");
    }

    // 7. 設定非阻塞模式
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

    return sockfd;
}
```

### 17.2 TCP 調優參數

```c
// ============ 進階 TCP 選項 ============
void tune_tcp_socket(int sockfd) {
    int flag = 1;

    // TCP_CORK: 累積資料再送 (與 NODELAY 互斥)
    // setsockopt(sockfd, IPPROTO_TCP, TCP_CORK, &flag, sizeof(flag));

    // TCP_DEFER_ACCEPT: server 端延遲 accept 直到有資料
    int timeout = 5;  // 秒
    setsockopt(sockfd, IPPROTO_TCP, TCP_DEFER_ACCEPT, &timeout, sizeof(timeout));

    // TCP_KEEPALIVE
    setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &flag, sizeof(flag));

    int keepidle = 60;   // 60 秒後開始發送 keepalive
    int keepintvl = 10;  // 每 10 秒發送一次
    int keepcnt = 3;     // 失敗 3 次後斷開

    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle));
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPINTVL, &keepintvl, sizeof(keepintvl));
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPCNT, &keepcnt, sizeof(keepcnt));

    // SO_PRIORITY: 設定封包優先級
    int priority = 6;  // 0-7, 越高越優先
    setsockopt(sockfd, SOL_SOCKET, SO_PRIORITY, &priority, sizeof(priority));
}
```

### 17.3 epoll 高效能事件循環

```c
#include <sys/epoll.h>

#define MAX_EVENTS 1024

// ============ epoll 事件循環 ============
void run_epoll_loop(int listen_fd) {
    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1");
        return;
    }

    // 註冊 listening socket
    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev) < 0) {
        perror("epoll_ctl");
        close(epoll_fd);
        return;
    }

    struct epoll_event events[MAX_EVENTS];

    while (1) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);

        for (int i = 0; i < nfds; i++) {
            if (events[i].data.fd == listen_fd) {
                // 新連接
                int client_fd = accept(listen_fd, NULL, NULL);
                if (client_fd < 0) continue;

                // 設為非阻塞
                int flags = fcntl(client_fd, F_GETFL, 0);
                fcntl(client_fd, F_SETFL, flags | O_NONBLOCK);

                // 註冊到 epoll (Edge-Triggered)
                ev.events = EPOLLIN | EPOLLET;
                ev.data.fd = client_fd;
                epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev);
            }
            else {
                // 資料可讀
                handle_client_data(events[i].data.fd);
            }
        }
    }

    close(epoll_fd);
}

void handle_client_data(int fd) {
    char buffer[4096];

    while (1) {
        ssize_t n = recv(fd, buffer, sizeof(buffer), 0);

        if (n > 0) {
            process_data(buffer, n);
        }
        else if (n == 0) {
            // 連接關閉
            close(fd);
            break;
        }
        else {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // 無更多資料
                break;
            }
            else {
                // 錯誤
                close(fd);
                break;
            }
        }
    }
}
```

### 17.4 批次讀寫

```c
#include <sys/uio.h>

// ============ Scatter/Gather I/O ============

// 批次讀取
ssize_t readv_example(int fd) {
    struct iovec iov[3];
    char buf1[100], buf2[200], buf3[300];

    iov[0].iov_base = buf1;
    iov[0].iov_len = sizeof(buf1);
    iov[1].iov_base = buf2;
    iov[1].iov_len = sizeof(buf2);
    iov[2].iov_base = buf3;
    iov[2].iov_len = sizeof(buf3);

    ssize_t n = readv(fd, iov, 3);
    return n;
}

// 批次寫入
ssize_t writev_example(int fd, const char *msg1, const char *msg2) {
    struct iovec iov[2];

    iov[0].iov_base = (void*)msg1;
    iov[0].iov_len = strlen(msg1);
    iov[1].iov_base = (void*)msg2;
    iov[1].iov_len = strlen(msg2);

    ssize_t n = writev(fd, iov, 2);
    return n;
}
```

---

## 18. 零拷貝技術

### 18.1 sendfile

```c
#include <sys/sendfile.h>

// ============ sendfile - 檔案到 socket ============
ssize_t send_file_zero_copy(int out_fd, int in_fd, off_t offset, size_t count) {
    return sendfile(out_fd, in_fd, &offset, count);
}

// 範例:發送檔案
void send_market_data_file(int client_fd, const char *filename) {
    int file_fd = open(filename, O_RDONLY);
    if (file_fd < 0) {
        perror("open");
        return;
    }

    struct stat st;
    fstat(file_fd, &st);

    off_t offset = 0;
    ssize_t sent = sendfile(client_fd, file_fd, &offset, st.st_size);

    printf("Sent %zd bytes using zero-copy\n", sent);

    close(file_fd);
}
```

### 18.2 splice

```c
#include <fcntl.h>

// ============ splice - pipe 零拷貝 ============
ssize_t splice_data(int fd_in, int fd_out, size_t len) {
    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("pipe");
        return -1;
    }

    // fd_in -> pipe
    ssize_t bytes = splice(fd_in, NULL, pipefd[1], NULL, len,
                           SPLICE_F_MOVE | SPLICE_F_MORE);
    if (bytes < 0) {
        perror("splice in");
        close(pipefd[0]);
        close(pipefd[1]);
        return -1;
    }

    // pipe -> fd_out
    ssize_t written = splice(pipefd[0], NULL, fd_out, NULL, bytes,
                             SPLICE_F_MOVE | SPLICE_F_MORE);

    close(pipefd[0]);
    close(pipefd[1]);

    return written;
}
```

### 18.3 mmap + write

```c
#include <sys/mman.h>

// ============ mmap 零拷貝 ============
void send_file_mmap(int sockfd, const char *filename) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("open");
        return;
    }

    struct stat st;
    fstat(fd, &st);

    // mmap 檔案
    void *ptr = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return;
    }

    // 建議連續讀取
    madvise(ptr, st.st_size, MADV_SEQUENTIAL);

    // 直接從 mmap 區域寫入 socket
    ssize_t sent = write(sockfd, ptr, st.st_size);

    printf("Sent %zd bytes using mmap\n", sent);

    munmap(ptr, st.st_size);
    close(fd);
}
```

### 18.4 UDP 零拷貝

```c
// ============ UDP sendmmsg - 批次發送 ============
#include <sys/socket.h>

void sendmmsg_example(int sockfd, struct sockaddr_in *dest_addr) {
    #define NUM_MESSAGES 10

    struct mmsghdr messages[NUM_MESSAGES];
    struct iovec iovecs[NUM_MESSAGES];
    char buffers[NUM_MESSAGES][100];

    memset(messages, 0, sizeof(messages));

    for (int i = 0; i < NUM_MESSAGES; i++) {
        snprintf(buffers[i], sizeof(buffers[i]), "Message %d", i);

        iovecs[i].iov_base = buffers[i];
        iovecs[i].iov_len = strlen(buffers[i]);

        messages[i].msg_hdr.msg_iov = &iovecs[i];
        messages[i].msg_hdr.msg_iovlen = 1;
        messages[i].msg_hdr.msg_name = dest_addr;
        messages[i].msg_hdr.msg_namelen = sizeof(*dest_addr);
    }

    int sent = sendmmsg(sockfd, messages, NUM_MESSAGES, 0);
    printf("Sent %d messages in one syscall\n", sent);
}
```

---

## 19. Kernel Bypass - DPDK

### 19.1 DPDK 基礎概念

DPDK (Data Plane Development Kit) 是用於快速封包處理的函式庫,繞過 kernel 直接從使用者空間存取網卡。

**主要優勢:**
- 零拷貝 I/O
- 批次處理
- 無系統呼叫開銷
- 降低延遲到微秒級

### 19.2 DPDK 安裝與設定

```bash
# 安裝 DPDK
sudo apt-get install dpdk dpdk-dev

# 設定 huge pages
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 綁定網卡到 DPDK
sudo dpdk-devbind.py --bind=uio_pci_generic eth1

# 檢查綁定狀態
dpdk-devbind.py --status
```

### 19.3 DPDK 基本程式

```c
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

static const struct rte_eth_conf port_conf_default = {
    .rxmode = {
        .max_rx_pkt_len = RTE_ETHER_MAX_LEN,
    },
};

// 初始化端口
int port_init(uint16_t port) {
    struct rte_eth_conf port_conf = port_conf_default;
    const uint16_t rx_rings = 1, tx_rings = 1;
    struct rte_mempool *mbuf_pool;
    int retval;

    // 創建 mbuf pool
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());

    if (mbuf_pool == NULL)
        return -1;

    // 配置端口
    retval = rte_eth_dev_configure(port, rx_rings, tx_rings, &port_conf);
    if (retval != 0)
        return retval;

    // 設定 RX queue
    retval = rte_eth_rx_queue_setup(port, 0, RX_RING_SIZE,
            rte_eth_dev_socket_id(port), NULL, mbuf_pool);
    if (retval < 0)
        return retval;

    // 設定 TX queue
    retval = rte_eth_tx_queue_setup(port, 0, TX_RING_SIZE,
            rte_eth_dev_socket_id(port), NULL);
    if (retval < 0)
        return retval;

    // 啟動端口
    retval = rte_eth_dev_start(port);
    if (retval < 0)
        return retval;

    // 啟用混雜模式
    rte_eth_promiscuous_enable(port);

    return 0;
}

// 主循環
int lcore_main(void *arg) {
    uint16_t port = 0;
    struct rte_mbuf *bufs[BURST_SIZE];

    printf("Core %u receiving packets\n", rte_lcore_id());

    while (1) {
        // 接收封包
        const uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);

        if (unlikely(nb_rx == 0))
            continue;

        // 處理封包
        for (int i = 0; i < nb_rx; i++) {
            process_packet(bufs[i]);
        }

        // 發送封包
        const uint16_t nb_tx = rte_eth_tx_burst(port, 0, bufs, nb_rx);

        // 釋放未發送的封包
        if (unlikely(nb_tx < nb_rx)) {
            for (int i = nb_tx; i < nb_rx; i++)
                rte_pktmbuf_free(bufs[i]);
        }
    }

    return 0;
}

int main(int argc, char *argv[]) {
    // 初始化 EAL
    int ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");

    // 初始化端口
    if (port_init(0) != 0)
        rte_exit(EXIT_FAILURE, "Cannot init port 0\n");

    // 啟動工作執行緒
    rte_eal_mp_remote_launch(lcore_main, NULL, CALL_MAIN);

    return 0;
}
```

---

## 20. RDMA 程式設計

### 20.1 RDMA 基礎

RDMA (Remote Direct Memory Access) 允許直接從遠端記憶體讀寫資料,無需 CPU 介入。

**適用場景:**
- 超低延遲通訊 (< 1μs)
- 高頻交易
- 分散式系統

### 20.2 RDMA Verbs 基本操作

```c
#include <infiniband/verbs.h>

// RDMA 連接設定
struct rdma_context {
    struct ibv_context *context;
    struct ibv_pd *pd;
    struct ibv_cq *cq;
    struct ibv_qp *qp;
    struct ibv_mr *mr;
    void *buf;
    size_t size;
};

// 初始化 RDMA 裝置
struct rdma_context* init_rdma(size_t buf_size) {
    struct rdma_context *ctx = calloc(1, sizeof(*ctx));
    
    // 獲取裝置列表
    int num_devices;
    struct ibv_device **dev_list = ibv_get_device_list(&num_devices);
    if (!dev_list)
        return NULL;
    
    // 打開第一個裝置
    ctx->context = ibv_open_device(dev_list[0]);
    
    // 分配保護域
    ctx->pd = ibv_alloc_pd(ctx->context);
    
    // 創建完成佇列
    ctx->cq = ibv_create_cq(ctx->context, 10, NULL, NULL, 0);
    
    // 創建佇列對
    struct ibv_qp_init_attr qp_init_attr = {
        .send_cq = ctx->cq,
        .recv_cq = ctx->cq,
        .qp_type = IBV_QPT_RC,
        .cap = {
            .max_send_wr = 10,
            .max_recv_wr = 10,
            .max_send_sge = 1,
            .max_recv_sge = 1,
        }
    };
    ctx->qp = ibv_create_qp(ctx->pd, &qp_init_attr);
    
    // 分配並註冊記憶體
    ctx->size = buf_size;
    ctx->buf = malloc(buf_size);
    ctx->mr = ibv_reg_mr(ctx->pd, ctx->buf, buf_size,
                         IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ);
    
    return ctx;
}

// RDMA SEND
int rdma_send(struct rdma_context *ctx, void *data, size_t len) {
    memcpy(ctx->buf, data, len);
    
    struct ibv_sge sge = {
        .addr = (uint64_t)ctx->buf,
        .length = len,
        .lkey = ctx->mr->lkey
    };
    
    struct ibv_send_wr wr = {
        .wr_id = 0,
        .sg_list = &sge,
        .num_sge = 1,
        .opcode = IBV_WR_SEND,
        .send_flags = IBV_SEND_SIGNALED,
    };
    
    struct ibv_send_wr *bad_wr;
    return ibv_post_send(ctx->qp, &wr, &bad_wr);
}

// RDMA WRITE (單向)
int rdma_write(struct rdma_context *ctx, void *local_data, size_t len,
               uint64_t remote_addr, uint32_t rkey) {
    memcpy(ctx->buf, local_data, len);
    
    struct ibv_sge sge = {
        .addr = (uint64_t)ctx->buf,
        .length = len,
        .lkey = ctx->mr->lkey
    };
    
    struct ibv_send_wr wr = {
        .wr_id = 0,
        .sg_list = &sge,
        .num_sge = 1,
        .opcode = IBV_WR_RDMA_WRITE,
        .send_flags = IBV_SEND_SIGNALED,
        .wr.rdma = {
            .remote_addr = remote_addr,
            .rkey = rkey
        }
    };
    
    struct ibv_send_wr *bad_wr;
    return ibv_post_send(ctx->qp, &wr, &bad_wr);
}
```

---

## 21. AF_XDP

AF_XDP 是 Linux kernel 提供的高效能 socket,允許使用者空間直接存取網卡接收佇列。

### 21.1 AF_XDP 基礎

```c
#include <linux/if_xdp.h>
#include <bpf/xsk.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE 2048

struct xsk_socket_info {
    struct xsk_ring_cons rx;
    struct xsk_ring_prod tx;
    struct xsk_umem *umem;
    struct xsk_socket *xsk;
    void *umem_area;
};

// 初始化 XDP socket
struct xsk_socket_info* create_xsk_socket(const char *ifname, int queue_id) {
    struct xsk_socket_info *xsk_info = calloc(1, sizeof(*xsk_info));
    
    // 分配 UMEM
    size_t umem_size = NUM_FRAMES * FRAME_SIZE;
    xsk_info->umem_area = mmap(NULL, umem_size,
                               PROT_READ | PROT_WRITE,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    
    // 設定 UMEM
    struct xsk_umem_config umem_config = {
        .fill_size = NUM_FRAMES / 2,
        .comp_size = NUM_FRAMES / 2,
        .frame_size = FRAME_SIZE,
        .frame_headroom = 0,
    };
    
    xsk_umem__create(&xsk_info->umem, xsk_info->umem_area, umem_size,
                     NULL, NULL, &umem_config);
    
    // 創建 socket
    struct xsk_socket_config xsk_config = {
        .rx_size = NUM_FRAMES / 2,
        .tx_size = NUM_FRAMES / 2,
    };
    
    xsk_socket__create(&xsk_info->xsk, ifname, queue_id, xsk_info->umem,
                       &xsk_info->rx, &xsk_info->tx, &xsk_config);
    
    return xsk_info;
}

// 接收封包
void rx_packets(struct xsk_socket_info *xsk_info) {
    uint32_t idx_rx = 0, idx_fq = 0;
    unsigned int rcvd;
    
    rcvd = xsk_ring_cons__peek(&xsk_info->rx, 64, &idx_rx);
    
    if (rcvd > 0) {
        // 處理接收到的封包
        for (int i = 0; i < rcvd; i++) {
            uint64_t addr = xsk_ring_cons__rx_desc(&xsk_info->rx, idx_rx++)->addr;
            uint32_t len = xsk_ring_cons__rx_desc(&xsk_info->rx, idx_rx - 1)->len;
            
            uint8_t *pkt = xsk_umem__get_data(xsk_info->umem_area, addr);
            
            // 處理封包
            process_packet(pkt, len);
        }
        
        xsk_ring_cons__release(&xsk_info->rx, rcvd);
    }
}
```

---

## 22. 硬體時間戳

### 22.1 SO_TIMESTAMPING

```c
#include <linux/net_tstamp.h>

// 啟用硬體時間戳
int enable_hw_timestamp(int sockfd) {
    int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                SOF_TIMESTAMPING_RX_HARDWARE |
                SOF_TIMESTAMPING_RAW_HARDWARE;
    
    return setsockopt(sockfd, SOL_SOCKET, SO_TIMESTAMPING,
                      &flags, sizeof(flags));
}

// 讀取硬體時間戳
void recv_with_timestamp(int sockfd) {
    char buf[2048];
    char control[1024];
    
    struct iovec iov = {
        .iov_base = buf,
        .iov_len = sizeof(buf)
    };
    
    struct msghdr msg = {
        .msg_iov = &iov,
        .msg_iovlen = 1,
        .msg_control = control,
        .msg_controllen = sizeof(control)
    };
    
    ssize_t len = recvmsg(sockfd, &msg, 0);
    
    // 解析時間戳
    for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
         cmsg != NULL;
         cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        
        if (cmsg->cmsg_level == SOL_SOCKET &&
            cmsg->cmsg_type == SO_TIMESTAMPING) {
            
            struct timespec *ts = (struct timespec *)CMSG_DATA(cmsg);
            
            printf("HW timestamp: %ld.%09ld\n", ts[2].tv_sec, ts[2].tv_nsec);
        }
    }
}
```

### 22.2 PTP (Precision Time Protocol)

```c
// PTP 時鐘同步
#include <linux/ptp_clock.h>

int sync_ptp_clock(const char *device) {
    int fd = open(device, O_RDWR);
    if (fd < 0)
        return -1;
    
    struct ptp_clock_time ptp_time;
    
    if (ioctl(fd, PTP_CLOCK_GETTIME, &ptp_time) < 0) {
        close(fd);
        return -1;
    }
    
    printf("PTP time: %lld.%u\n", ptp_time.sec, ptp_time.nsec);
    
    close(fd);
    return 0;
}
```

---

# 第六部分:FPGA 加速

## 23. FPGA 基礎架構

### 23.1 FPGA 概念

FPGA (Field-Programmable Gate Array) 是可程式化硬體,用於加速特定計算任務。

**在 HFT 的應用:**
- 訂單解析與驗證
- 市場資料處理
- 風險檢查
- 延遲 < 100ns

### 23.2 CPU-FPGA 通訊架構

```
┌─────────────┐        PCIe        ┌─────────────┐
│             │ ◄───────────────► │             │
│   CPU       │   DMA Transfer    │   FPGA      │
│   (C code)  │                   │   (Verilog) │
│             │                   │             │
└─────────────┘                   └─────────────┘
```

### 23.3 基本 FPGA 介面 (偽代碼)

```c
// FPGA 記憶體映射 I/O
#define FPGA_BASE_ADDR 0xC0000000
#define FPGA_REG_STATUS   (FPGA_BASE_ADDR + 0x00)
#define FPGA_REG_CONTROL  (FPGA_BASE_ADDR + 0x04)
#define FPGA_REG_DATA_IN  (FPGA_BASE_ADDR + 0x08)
#define FPGA_REG_DATA_OUT (FPGA_BASE_ADDR + 0x0C)

// 寫入 FPGA
static inline void fpga_write_reg(uint32_t offset, uint32_t value) {
    volatile uint32_t *reg = (volatile uint32_t *)(FPGA_BASE_ADDR + offset);
    *reg = value;
}

// 從 FPGA 讀取
static inline uint32_t fpga_read_reg(uint32_t offset) {
    volatile uint32_t *reg = (volatile uint32_t *)(FPGA_BASE_ADDR + offset);
    return *reg;
}

// 發送訂單到 FPGA
void send_order_to_fpga(Order *order) {
    // 等待 FPGA ready
    while (!(fpga_read_reg(0x00) & 0x01));
    
    // 寫入訂單資料
    fpga_write_reg(0x08, order->order_id);
    fpga_write_reg(0x0C, order->price);
    fpga_write_reg(0x10, order->quantity);
    
    // 觸發處理
    fpga_write_reg(0x04, 0x01);
}
```

---

## 24. 訂單處理加速

### 24.1 FPGA 訂單驗證

```c
// CPU 端程式碼
typedef struct {
    uint64_t order_id;
    uint32_t symbol_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t side;
    uint8_t type;
} FPGAOrder;

// FPGA 驗證結果
typedef struct {
    uint8_t valid;
    uint8_t reject_reason;
    uint16_t _padding;
} FPGAValidationResult;

// 使用 FPGA 驗證訂單
int validate_order_fpga(FPGAOrder *order, FPGAValidationResult *result) {
    // 將訂單送入 FPGA
    fpga_write_reg(0x100, order->order_id >> 32);
    fpga_write_reg(0x104, order->order_id & 0xFFFFFFFF);
    fpga_write_reg(0x108, order->price);
    fpga_write_reg(0x10C, order->quantity);
    
    // 觸發驗證
    fpga_write_reg(0x00, 0x01);
    
    // 等待結果 (busy wait)
    while (!(fpga_read_reg(0x04) & 0x01));
    
    // 讀取結果
    uint32_t result_reg = fpga_read_reg(0x200);
    result->valid = result_reg & 0xFF;
    result->reject_reason = (result_reg >> 8) & 0xFF;
    
    return result->valid;
}
```

---

## 25. 市場資料解析

FPGA 可以並行解析市場資料協議,延遲遠低於 CPU。

### 25.1 FIX 協議解析

```c
// FPGA FIX 解析器介面
typedef struct {
    uint64_t timestamp_ns;
    uint32_t symbol_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t msg_type;
} FPGAParsedMessage;

// 批次解析
int fpga_parse_fix_batch(const char *raw_data, size_t len,
                         FPGAParsedMessage *parsed, int max_msgs) {
    // 寫入原始資料到 FPGA
    for (size_t i = 0; i < len; i += 4) {
        uint32_t word = *(uint32_t *)(raw_data + i);
        fpga_write_reg(0x1000 + i, word);
    }
    
    // 設定長度並觸發解析
    fpga_write_reg(0x2000, len);
    fpga_write_reg(0x2004, 0x01);  // Start
    
    // 等待完成
    while (!(fpga_read_reg(0x2008) & 0x01));
    
    // 讀取解析後的訊息數量
    int num_parsed = fpga_read_reg(0x200C);
    
    // 讀取解析結果
    for (int i = 0; i < num_parsed && i < max_msgs; i++) {
        uint32_t base = 0x3000 + i * 32;
        parsed[i].timestamp_ns = ((uint64_t)fpga_read_reg(base) << 32) |
                                 fpga_read_reg(base + 4);
        parsed[i].symbol_id = fpga_read_reg(base + 8);
        parsed[i].price = fpga_read_reg(base + 12);
        parsed[i].quantity = fpga_read_reg(base + 16);
        parsed[i].msg_type = fpga_read_reg(base + 20) & 0xFF;
    }
    
    return num_parsed;
}
```

---

## 26. CPU-FPGA 通訊

### 26.1 DMA 傳輸

```c
#include <linux/dma-mapping.h>

// DMA 緩衝區
typedef struct {
    void *cpu_addr;
    dma_addr_t dma_addr;
    size_t size;
} DMABuffer;

// 分配 DMA 緩衝區
DMABuffer* alloc_dma_buffer(size_t size) {
    DMABuffer *buf = malloc(sizeof(DMABuffer));
    
    buf->size = size;
    buf->cpu_addr = dma_alloc_coherent(NULL, size, &buf->dma_addr, GFP_KERNEL);
    
    if (!buf->cpu_addr) {
        free(buf);
        return NULL;
    }
    
    return buf;
}

// 啟動 DMA 傳輸到 FPGA
void dma_to_fpga(DMABuffer *buf, size_t len) {
    // 設定 DMA 來源地址
    fpga_write_reg(DMA_SRC_ADDR_LOW, buf->dma_addr & 0xFFFFFFFF);
    fpga_write_reg(DMA_SRC_ADDR_HIGH, buf->dma_addr >> 32);
    
    // 設定傳輸長度
    fpga_write_reg(DMA_LENGTH, len);
    
    // 啟動 DMA
    fpga_write_reg(DMA_CONTROL, 0x01);
    
    // 等待完成
    while (!(fpga_read_reg(DMA_STATUS) & 0x01));
}
```

### 26.2 共享記憶體

```c
// 使用 mmap 與 FPGA 共享記憶體
void* fpga_shared_memory_init(const char *device, size_t size) {
    int fd = open(device, O_RDWR | O_SYNC);
    if (fd < 0)
        return NULL;
    
    void *mem = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    
    if (mem == MAP_FAILED) {
        close(fd);
        return NULL;
    }
    
    return mem;
}
```

---

# 第七部分:完整系統

## 27. 系統架構設計

### 27.1 整體架構

```
┌────────────────────────────────────────────────────┐
│                  Trading System                    │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌─────────────┐     ┌──────────────┐            │
│  │ Market Data │────▶│ Order Engine │            │
│  │  Receiver   │     │   (Core 2)   │            │
│  │  (Core 1)   │     └──────┬───────┘            │
│  └─────────────┘            │                     │
│         │                   │                     │
│         │                   ▼                     │
│         │          ┌────────────────┐            │
│         └─────────▶│  Risk Manager  │            │
│                    │    (Core 3)    │            │
│                    └────────┬───────┘            │
│                             │                     │
│                             ▼                     │
│                    ┌────────────────┐            │
│                    │ Order Gateway  │            │
│                    │    (Core 4)    │            │
│                    └────────────────┘            │
│                                                    │
└────────────────────────────────────────────────────┘
```

### 27.2 核心模組設計

```c
// trading_system.h
#ifndef TRADING_SYSTEM_H
#define TRADING_SYSTEM_H

#include <stdint.h>
#include <pthread.h>

// 市場資料
typedef struct {
    uint64_t timestamp;
    uint32_t symbol_id;
    uint32_t bid_price;
    uint32_t ask_price;
    uint32_t bid_qty;
    uint32_t ask_qty;
} MarketData;

// 訂單
typedef struct {
    uint64_t order_id;
    uint64_t timestamp;
    uint32_t symbol_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t side;  // 0=buy, 1=sell
    uint8_t type;  // 0=limit, 1=market
    uint8_t status;
} Order;

// 系統配置
typedef struct {
    int market_data_cpu;
    int order_engine_cpu;
    int risk_manager_cpu;
    int order_gateway_cpu;
    
    const char *market_data_addr;
    int market_data_port;
    
    const char *exchange_addr;
    int exchange_port;
} SystemConfig;

// 系統狀態
typedef struct {
    atomic_bool running;
    
    // 執行緒
    pthread_t market_data_thread;
    pthread_t order_engine_thread;
    pthread_t risk_manager_thread;
    pthread_t order_gateway_thread;
    
    // 無鎖佇列
    SPSCQueue *md_to_engine;
    SPSCQueue *engine_to_risk;
    SPSCQueue *risk_to_gateway;
    
    // 統計
    atomic_uint64_t orders_processed;
    atomic_uint64_t orders_sent;
    atomic_uint64_t md_packets_recv;
} TradingSystem;

// API
TradingSystem* create_trading_system(SystemConfig *config);
int start_trading_system(TradingSystem *sys);
void stop_trading_system(TradingSystem *sys);
void destroy_trading_system(TradingSystem *sys);

#endif
```

---

## 28. 完整範例專案

### 28.1 主程式

```c
// main.c
#include "trading_system.h"
#include <signal.h>

static TradingSystem *g_system = NULL;

void signal_handler(int sig) {
    if (g_system) {
        stop_trading_system(g_system);
    }
}

int main(int argc, char *argv[]) {
    // 設定信號處理
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // 配置
    SystemConfig config = {
        .market_data_cpu = 1,
        .order_engine_cpu = 2,
        .risk_manager_cpu = 3,
        .order_gateway_cpu = 4,
        .market_data_addr = "239.1.1.1",
        .market_data_port = 9000,
        .exchange_addr = "192.168.1.100",
        .exchange_port = 8000,
    };
    
    // 創建系統
    g_system = create_trading_system(&config);
    if (!g_system) {
        fprintf(stderr, "Failed to create trading system\n");
        return 1;
    }
    
    // 啟動系統
    printf("Starting trading system...\n");
    if (start_trading_system(g_system) != 0) {
        fprintf(stderr, "Failed to start trading system\n");
        destroy_trading_system(g_system);
        return 1;
    }
    
    printf("Trading system running. Press Ctrl+C to stop.\n");
    
    // 主循環
    while (atomic_load(&g_system->running)) {
        sleep(1);
        
        // 打印統計
        printf("Stats - MD: %lu, Orders: %lu, Sent: %lu\n",
               atomic_load(&g_system->md_packets_recv),
               atomic_load(&g_system->orders_processed),
               atomic_load(&g_system->orders_sent));
    }
    
    // 清理
    destroy_trading_system(g_system);
    
    return 0;
}
```

---

## 29. 效能測試與監控

### 29.1 延遲測量

```c
// latency.h
#include <time.h>

typedef struct {
    uint64_t min_ns;
    uint64_t max_ns;
    uint64_t avg_ns;
    uint64_t p50_ns;
    uint64_t p99_ns;
    uint64_t p999_ns;
    uint64_t count;
} LatencyStats;

// 延遲直方圖
typedef struct {
    uint64_t buckets[100];
    uint64_t *samples;
    size_t count;
    size_t capacity;
} LatencyHistogram;

LatencyHistogram* create_latency_histogram(size_t capacity);
void record_latency(LatencyHistogram *hist, uint64_t latency_ns);
void calculate_latency_stats(LatencyHistogram *hist, LatencyStats *stats);

// 使用範例
void measure_order_latency(void) {
    LatencyHistogram *hist = create_latency_histogram(1000000);
    
    for (int i = 0; i < 1000000; i++) {
        struct timespec start, end;
        
        clock_gettime(CLOCK_MONOTONIC, &start);
        
        // 處理訂單
        process_order(&orders[i]);
        
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        uint64_t latency_ns = (end.tv_sec - start.tv_sec) * 1000000000ULL +
                              (end.tv_nsec - start.tv_nsec);
        
        record_latency(hist, latency_ns);
    }
    
    LatencyStats stats;
    calculate_latency_stats(hist, &stats);
    
    printf("Latency Stats:\n");
    printf("  Min:    %lu ns\n", stats.min_ns);
    printf("  Max:    %lu ns\n", stats.max_ns);
    printf("  Avg:    %lu ns\n", stats.avg_ns);
    printf("  P50:    %lu ns\n", stats.p50_ns);
    printf("  P99:    %lu ns\n", stats.p99_ns);
    printf("  P99.9:  %lu ns\n", stats.p999_ns);
}
```

### 29.2 效能監控

```c
// monitor.h
typedef struct {
    atomic_uint64_t rx_packets;
    atomic_uint64_t rx_bytes;
    atomic_uint64_t tx_packets;
    atomic_uint64_t tx_bytes;
    atomic_uint64_t orders_total;
    atomic_uint64_t orders_filled;
    atomic_uint64_t orders_rejected;
} SystemMetrics;

// 監控執行緒
void* monitoring_thread(void *arg) {
    SystemMetrics *metrics = (SystemMetrics *)arg;
    
    uint64_t last_rx_packets = 0;
    uint64_t last_tx_packets = 0;
    
    while (1) {
        sleep(1);
        
        uint64_t rx = atomic_load(&metrics->rx_packets);
        uint64_t tx = atomic_load(&metrics->tx_packets);
        
        printf("Rate - RX: %lu pps, TX: %lu pps\n",
               rx - last_rx_packets,
               tx - last_tx_packets);
        
        last_rx_packets = rx;
        last_tx_packets = tx;
    }
    
    return NULL;
}
```

---

## 30. 故障排除

### 30.1 常見問題

#### 問題 1: 延遲過高

**診斷:**
```bash
# 檢查 CPU 頻率
cat /proc/cpuinfo | grep MHz

# 檢查 context switch
vmstat 1

# 檢查中斷分佈
cat /proc/interrupts
```

**解決方案:**
- 綁定 CPU 親和性
- 禁用 CPU 頻率調節
- 隔離 CPU core
- 關閉不必要的服務

#### 問題 2: 封包遺失

**診斷:**
```bash
# 檢查網卡統計
ethtool -S eth0 | grep drop

# 檢查接收緩衝區
netstat -s | grep overflow
```

**解決方案:**
- 增加接收緩衝區
- 啟用多佇列
- 使用 DPDK/AF_XDP

#### 問題 3: 記憶體延遲

**診斷:**
```bash
# 檢查 huge pages
cat /proc/meminfo | grep Huge

# 檢查 NUMA
numactl --hardware
```

**解決方案:**
- 啟用 huge pages
- NUMA aware 分配
- 減少 TLB miss

### 30.2 除錯工具

```bash
# perf - 效能分析
perf record -F 99 -a -g -- sleep 10
perf report

# perf top - 即時效能監控
perf top -F 99

# strace - 系統呼叫追蹤
strace -c ./trading_system

# gdb - 除錯
gdb ./trading_system
(gdb) break main
(gdb) run
(gdb) bt

# valgrind - 記憶體檢查
valgrind --leak-check=full ./trading_system
```

### 30.3 最佳實踐清單

**開發階段:**
- [ ] 使用版本控制 (Git)
- [ ] 撰寫單元測試
- [ ] 程式碼審查
- [ ] 效能基準測試
- [ ] 文件完整

**部署階段:**
- [ ] CPU 隔離與綁定
- [ ] 網路調優
- [ ] 記憶體優化 (Huge Pages)
- [ ] 實時優先權設定
- [ ] 監控系統部署

**維運階段:**
- [ ] 日誌記錄
- [ ] 效能監控
- [ ] 告警設定
- [ ] 備援機制
- [ ] 定期檢查

---

## 結語

本指南涵蓋了高頻交易系統中 C 語言的完整優化技術,從基礎的位元運算到 FPGA 加速,從記憶體管理到網路 I/O,從編譯器優化到系統調校。

**關鍵要點:**
1. **微秒級優化**:每個 cycle 都很重要
2. **系統性思考**:硬體+軟體+網路整體優化
3. **測量驅動**:先測量再優化
4. **權衡取捨**:延遲 vs 吞吐量 vs 穩定性

**持續學習:**
- Linux kernel 原始碼
- 硬體架構手冊
- 最新優化技術
- 業界最佳實踐

祝您在高頻交易領域取得成功!

---

**附錄:參考資源**

- Linux Kernel Documentation
- Intel Optimization Manual
- DPDK Programming Guide
- Mellanox RDMA Guide
- GCC Optimization Options
- Xilinx FPGA Documentation

**版本資訊**
- 版本: 1.0
- 更新日期: 2024
- 作者: Claude Code Assistant
