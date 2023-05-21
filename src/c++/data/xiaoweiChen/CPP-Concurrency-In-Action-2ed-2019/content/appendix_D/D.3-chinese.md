# D.3 &lt;atomic&gt;頭文件

&lt;atomic&gt;頭文件提供一組基礎的原子類型，和提供對這些基本類型的操作，以及一個原子模板函數，用來接收用戶定義的類型，以適用於某些標準。

###頭文件內容

```
#define ATOMIC_BOOL_LOCK_FREE 參見詳述
#define ATOMIC_CHAR_LOCK_FREE 參見詳述
#define ATOMIC_SHORT_LOCK_FREE 參見詳述
#define ATOMIC_INT_LOCK_FREE 參見詳述
#define ATOMIC_LONG_LOCK_FREE 參見詳述
#define ATOMIC_LLONG_LOCK_FREE 參見詳述
#define ATOMIC_CHAR16_T_LOCK_FREE 參見詳述
#define ATOMIC_CHAR32_T_LOCK_FREE 參見詳述
#define ATOMIC_WCHAR_T_LOCK_FREE 參見詳述
#define ATOMIC_POINTER_LOCK_FREE 參見詳述

#define ATOMIC_VAR_INIT(value) 參見詳述

namespace std
{
  enum memory_order;

  struct atomic_flag;
  參見類型定義詳述 atomic_bool;
  參見類型定義詳述 atomic_char;
  參見類型定義詳述 atomic_char16_t;
  參見類型定義詳述 atomic_char32_t;
  參見類型定義詳述 atomic_schar;
  參見類型定義詳述 atomic_uchar;
  參見類型定義詳述 atomic_short;
  參見類型定義詳述 atomic_ushort;
  參見類型定義詳述 atomic_int;
  參見類型定義詳述 atomic_uint;
  參見類型定義詳述 atomic_long;
  參見類型定義詳述 atomic_ulong;
  參見類型定義詳述 atomic_llong;
  參見類型定義詳述 atomic_ullong;
  參見類型定義詳述 atomic_wchar_t;

  參見類型定義詳述 atomic_int_least8_t;
  參見類型定義詳述 atomic_uint_least8_t;
  參見類型定義詳述 atomic_int_least16_t;
  參見類型定義詳述 atomic_uint_least16_t;
  參見類型定義詳述 atomic_int_least32_t;
  參見類型定義詳述 atomic_uint_least32_t;
  參見類型定義詳述 atomic_int_least64_t;
  參見類型定義詳述 atomic_uint_least64_t;
  參見類型定義詳述 atomic_int_fast8_t;
  參見類型定義詳述 atomic_uint_fast8_t;
  參見類型定義詳述 atomic_int_fast16_t;
  參見類型定義詳述 atomic_uint_fast16_t;
  參見類型定義詳述 atomic_int_fast32_t;
  參見類型定義詳述 atomic_uint_fast32_t;
  參見類型定義詳述 atomic_int_fast64_t;
  參見類型定義詳述 atomic_uint_fast64_t;
  參見類型定義詳述 atomic_int8_t;
  參見類型定義詳述 atomic_uint8_t;
  參見類型定義詳述 atomic_int16_t;
  參見類型定義詳述 atomic_uint16_t;
  參見類型定義詳述 atomic_int32_t;
  參見類型定義詳述 atomic_uint32_t;
  參見類型定義詳述 atomic_int64_t;
  參見類型定義詳述 atomic_uint64_t;
  參見類型定義詳述 atomic_intptr_t;
  參見類型定義詳述 atomic_uintptr_t;
  參見類型定義詳述 atomic_size_t;
  參見類型定義詳述 atomic_ssize_t;
  參見類型定義詳述 atomic_ptrdiff_t;
  參見類型定義詳述 atomic_intmax_t;
  參見類型定義詳述 atomic_uintmax_t;

  template<typename T>
  struct atomic;

  extern "C" void atomic_thread_fence(memory_order order);
  extern "C" void atomic_signal_fence(memory_order order);

  template<typename T>
  T kill_dependency(T);
}
```

## std::atomic_xxx類型定義

為了兼容新的C標準(C11)，C++支持定義原子整型類型。這些類型都與`std::atimic<T>;`特化類相對應，或是用同一接口特化的一個基本類型。

**Table D.1 原子類型定義和與之相關的std::atmoic&lt;&gt;特化模板**

| std::atomic_itype 原子類型 | std::atomic&lt;&gt; 相關特化類 |
| ------------ | -------------- |
| atomic_char | std::atomic&lt;char&gt; |
| atomic_schar | std::atomic&lt;signed char&gt; |
| atomic_uchar | std::atomic&lt;unsigned char&gt; |
| atomic_int | std::atomic&lt;int&gt; |
| atomic_uint | std::atomic&lt;unsigned&gt; |
| atomic_short | std::atomic&lt;short&gt; |
| atomic_ushort | std::atomic&lt;unsigned short&gt; |
| atomic_long | std::atomic&lt;long&gt; |
| atomic_ulong | std::atomic&lt;unsigned long&gt; |
| atomic_llong | std::atomic&lt;long long&gt; |
| atomic_ullong | std::atomic&lt;unsigned long long&gt; |
| atomic_wchar_t | std::atomic&lt;wchar_t&gt; |
| atomic_char16_t | std::atomic&lt;char16_t&gt; |
| atomic_char32_t | std::atomic&lt;char32_t&gt; |

(譯者注：該表與第5章中的表5.1幾乎一致)

## D.3.2 ATOMIC_xxx_LOCK_FREE宏

這裡的宏指定了原子類型與其內置類型是否是無鎖的。

**宏定義**

```
#define ATOMIC_BOOL_LOCK_FREE 參見詳述
#define ATOMIC_CHAR_LOCK_FREE參見詳述
#define ATOMIC_SHORT_LOCK_FREE 參見詳述
#define ATOMIC_INT_LOCK_FREE 參見詳述
#define ATOMIC_LONG_LOCK_FREE 參見詳述
#define ATOMIC_LLONG_LOCK_FREE 參見詳述
#define ATOMIC_CHAR16_T_LOCK_FREE 參見詳述
#define ATOMIC_CHAR32_T_LOCK_FREE 參見詳述
#define ATOMIC_WCHAR_T_LOCK_FREE 參見詳述
#define ATOMIC_POINTER_LOCK_FREE 參見詳述
```

`ATOMIC_xxx_LOCK_FREE`的值無非就是0，1，2。0意味著，在對有無符號的相關原子類型操作是有鎖的；1意味著，操作只對一些特定的類型上鎖，而對沒有指定的類型不上鎖；2意味著，所有操作都是無鎖的。例如，當`ATOMIC_INT_LOCK_FREE`是2的時候，在`std::atomic&lt;int&gt;`和`std::atomic&lt;unsigned&gt;`上的操作始終無鎖。

宏`ATOMIC_POINTER_LOCK_FREE`描述了，對於特化的原子類型指針`std::atomic<T*>`操作的無鎖特性。

## D.3.3 ATOMIC_VAR_INIT宏

`ATOMIC_VAR_INIT`宏可以通過一個特定的值來初始化一個原子變量。

**聲明**
`#define ATOMIC_VAR_INIT(value)參見詳述`

宏可以擴展成一系列符號，這個宏可以通過一個給定值，初始化一個標準原子類型，表達式如下所示：

```
std::atomic<type> x = ATOMIC_VAR_INIT(val);
```

給定值可以兼容與原子變量相關的非原子變量，例如：

```
std::atomic&lt;int> i = ATOMIC_VAR_INIT(42);
std::string s;
std::atomic&lt;std::string*> p = ATOMIC_VAR_INIT(&s);
```

這樣初始化的變量是非原子的，並且在變量初始化之後，其他線程可以隨意的訪問該變量，這樣可以避免條件競爭和未定義行為的發生。

## D.3.4 std::memory_order枚舉類型

`std::memory_order`枚舉類型用來表明原子操作的約束順序。

**聲明**

```
typedef enum memory_order
{
  memory_order_relaxed,memory_order_consume,
  memory_order_acquire,memory_order_release,
  memory_order_acq_rel,memory_order_seq_cst
} memory_order;
```

通過標記各種內存序變量來標記操作的順序(詳見第5章，在該章節中有對書序約束更加詳盡的介紹)

### std::memory_order_relaxed

操作不受任何額外的限制。

### std::memory_order_release

對於指定位置上的內存可進行釋放操作。因此，與獲取操作讀取同一內存位置所存儲的值。

### std::memory_order_acquire

操作可以獲取指定內存位置上的值。當需要存儲的值通過釋放操作寫入時，是與存儲操同步的。

### std::memory_order_acq_rel

操作必須是“讀-改-寫”操作，並且其行為需要在`std::memory_order_acquire`和`std::memory_order_release`序指定的內存位置上進行操作。

### std::memory_order_seq_cst

操作在全局序上都會受到約束。還有，當為存儲操作時，其行為好比`std::memory_order_release`操作；當為加載操作時，其行為好比`std::memory_order_acquire`操作；並且，當其是一個“讀-改-寫”操作時，其行為和`std::memory_order_acquire`和`std::memory_order_release`類似。對於所有順序來說，該順序為默認序。

### std::memory_order_consume

對於指定位置的內存進行消耗操作(consume operation)。

(譯者注：與memory_order_acquire類似)

##D.3.5 std::atomic_thread_fence函數

`std::atomic_thread_fence()`會在代碼中插入“內存柵欄”，強制兩個操作保持內存約束順序。

**聲明**

```
extern "C" void atomic_thread_fence(std::memory_order order);
```

**效果**
插入柵欄的目的是為了保證內存序的約束性。

柵欄使用`std::memory_order_release`, `std::memory_order_acq_rel`, 或 `std::memory_order_seq_cst`內存序，會同步與一些內存位置上的獲取操作進行同步，如果這些獲取操作要獲取一個已存儲的值(通過原子操作進行的存儲)，就會通過柵欄進行同步。

釋放操作可對`std::memory_order_acquire`, `std::memory_order_acq_rel`, 或 `std::memory_order_seq_cst`進行柵欄同步，；當釋放操作存儲的值，在一個原子操作之前讀取，那麼就會通過柵欄進行同步。

**拋出**
無

## D.3.6 std::atomic_signal_fence函數

`std::atomic_signal_fence()`會在代碼中插入“內存柵欄”，強制兩個操作保持內存約束順序，並且在對應線程上執行信號處理操作。

**聲明**

```
extern "C" void atomic_signal_fence(std::memory_order order);
```

**效果**
根據需要的內存約束序插入一個柵欄。除非約束序應用於“操作和信號處理函數在同一線程”的情況下，否則，這個操作等價於`std::atomic_thread_fence(order)`操作。

**拋出**
無

## D.3.7 std::atomic_flag類

`std::atomic_flag`類算是原子標識的骨架。在C++11標準下，只有這個數據類型可以保證是無鎖的(當然，更多的原子類型在未來的實現中將採取無鎖實現)。

對於一個`std::atomic_flag`來說，其狀態不是set，就是clear。

**類型定義**

```
struct atomic_flag
{
  atomic_flag() noexcept = default;
  atomic_flag(const atomic_flag&) = delete;
  atomic_flag& operator=(const atomic_flag&) = delete;
  atomic_flag& operator=(const atomic_flag&) volatile = delete;

  bool test_and_set(memory_order = memory_order_seq_cst) volatile
    noexcept;
  bool test_and_set(memory_order = memory_order_seq_cst) noexcept;
  void clear(memory_order = memory_order_seq_cst) volatile noexcept;
  void clear(memory_order = memory_order_seq_cst) noexcept;
};

bool atomic_flag_test_and_set(volatile atomic_flag*) noexcept;
bool atomic_flag_test_and_set(atomic_flag*) noexcept;
bool atomic_flag_test_and_set_explicit(
  volatile atomic_flag*, memory_order) noexcept;
bool atomic_flag_test_and_set_explicit(
  atomic_flag*, memory_order) noexcept;
void atomic_flag_clear(volatile atomic_flag*) noexcept;
void atomic_flag_clear(atomic_flag*) noexcept;
void atomic_flag_clear_explicit(
  volatile atomic_flag*, memory_order) noexcept;
void atomic_flag_clear_explicit(
  atomic_flag*, memory_order) noexcept;

#define ATOMIC_FLAG_INIT unspecified
```

### std::atomic_flag 默認構造函數

這裡未指定默認構造出來的`std::atomic_flag`實例是clear狀態，還是set狀態。因為對象存儲過程是靜態的，所以初始化必須是靜態的。

**聲明**

```
std::atomic_flag() noexcept = default;
```

**效果**
構造一個新`std::atomic_flag`對象，不過未指明狀態。(薛定諤的貓？)

**拋出**
無

### std::atomic_flag 使用ATOMIC_FLAG_INIT進行初始化

`std::atomic_flag`實例可以使用`ATOMIC_FLAG_INIT`宏進行創建，這樣構造出來的實例狀態為clear。因為對象存儲過程是靜態的，所以初始化必須是靜態的。

**聲明**

```
#define ATOMIC_FLAG_INIT unspecified
```

**用法**

```
std::atomic_flag flag=ATOMIC_FLAG_INIT;
```

**效果**
構造一個新`std::atomic_flag`對象，狀態為clear。

**拋出**
無

**NOTE**：
對於內存位置上的*this，這個操作屬於“讀-改-寫”操作。

### std::atomic_flag::test_and_set 成員函數

自動設置實例狀態標識，並且檢查實例的狀態標識是否已經設置。

**聲明**

```
bool atomic_flag_test_and_set(volatile atomic_flag* flag) noexcept;
bool atomic_flag_test_and_set(atomic_flag* flag) noexcept;
```

**效果**

```
return flag->test_and_set();
```

### std::atomic_flag_test_and_set 非成員函數

自動設置原子變量的狀態標識，並且檢查原子變量的狀態標識是否已經設置。

**聲明**

```
bool atomic_flag_test_and_set_explicit(
    volatile atomic_flag* flag, memory_order order) noexcept;
bool atomic_flag_test_and_set_explicit(
    atomic_flag* flag, memory_order order) noexcept;
```

**效果**

```
return flag->test_and_set(order);
```

### std::atomic_flag_test_and_set_explicit 非成員函數

自動設置原子變量的狀態標識，並且檢查原子變量的狀態標識是否已經設置。

**聲明**

```
bool atomic_flag_test_and_set_explicit(
    volatile atomic_flag* flag, memory_order order) noexcept;
bool atomic_flag_test_and_set_explicit(
    atomic_flag* flag, memory_order order) noexcept;
```

**效果**

```
return flag->test_and_set(order);
```

### std::atomic_flag::clear 成員函數

自動清除原子變量的狀態標識。

**聲明**

```
void clear(memory_order order = memory_order_seq_cst) volatile noexcept;
void clear(memory_order order = memory_order_seq_cst) noexcept;
```

**先決條件**
支持`std::memory_order_relaxed`,`std::memory_order_release`和`std::memory_order_seq_cst`中任意一個。


**效果**
自動清除變量狀態標識。

**拋出**
無

**NOTE**:對於內存位置上的*this，這個操作屬於“寫”操作(存儲操作)。


### std::atomic_flag_clear 非成員函數

自動清除原子變量的狀態標識。

**聲明**

```
void atomic_flag_clear(volatile atomic_flag* flag) noexcept;
void atomic_flag_clear(atomic_flag* flag) noexcept;
```

**效果**

```
flag->clear();
```

### std::atomic_flag_clear_explicit 非成員函數

自動清除原子變量的狀態標識。

**聲明**

```
void atomic_flag_clear_explicit(
    volatile atomic_flag* flag, memory_order order) noexcept;
void atomic_flag_clear_explicit(
    atomic_flag* flag, memory_order order) noexcept;
```

**效果**

```
return flag->clear(order);
```

##D.3.8 std::atomic類型模板

`std::atomic`提供了對任意類型的原子操作的包裝，以滿足下面的需求。

模板參數BaseType必須滿足下面的條件。

- 具有簡單的默認構造函數
- 具有簡單的拷貝賦值操作
- 具有簡單的析構函數
- 可以進行位比較

這就意味著`std::atomic&lt;some-simple-struct&gt;`會和使用`std::atomic<some-built-in-type>`一樣簡單；不過對於`std::atomic<std::string>`就不同了。

除了主模板，對於內置整型和指針的特化，模板也支持類似x++這樣的操作。

`std::atomic`實例是不支持`CopyConstructible`(拷貝構造)和`CopyAssignable`(拷貝賦值)，原因你懂得，因為這樣原子操作就無法執行。

**類型定義**

```
template<typename BaseType>
struct atomic
{
  atomic() noexcept = default;
  constexpr atomic(BaseType) noexcept;
  BaseType operator=(BaseType) volatile noexcept;
  BaseType operator=(BaseType) noexcept;

  atomic(const atomic&) = delete;
  atomic& operator=(const atomic&) = delete;
  atomic& operator=(const atomic&) volatile = delete;

  bool is_lock_free() const volatile noexcept;
  bool is_lock_free() const noexcept;

  void store(BaseType,memory_order = memory_order_seq_cst)
      volatile noexcept;
  void store(BaseType,memory_order = memory_order_seq_cst) noexcept;
  BaseType load(memory_order = memory_order_seq_cst)
      const volatile noexcept;
  BaseType load(memory_order = memory_order_seq_cst) const noexcept;
  BaseType exchange(BaseType,memory_order = memory_order_seq_cst)
      volatile noexcept;
  BaseType exchange(BaseType,memory_order = memory_order_seq_cst)
      noexcept;

  bool compare_exchange_strong(
      BaseType & old_value, BaseType new_value,
      memory_order order = memory_order_seq_cst) volatile noexcept;
  bool compare_exchange_strong(
      BaseType & old_value, BaseType new_value,
      memory_order order = memory_order_seq_cst) noexcept;
  bool compare_exchange_strong(
      BaseType & old_value, BaseType new_value,
      memory_order success_order,
      memory_order failure_order) volatile noexcept;
  bool compare_exchange_strong(
      BaseType & old_value, BaseType new_value,
      memory_order success_order,
      memory_order failure_order) noexcept;
  bool compare_exchange_weak(
      BaseType & old_value, BaseType new_value,
      memory_order order = memory_order_seq_cst)
      volatile noexcept;
  bool compare_exchange_weak(
      BaseType & old_value, BaseType new_value,
      memory_order order = memory_order_seq_cst) noexcept;
  bool compare_exchange_weak(
      BaseType & old_value, BaseType new_value,
      memory_order success_order,
      memory_order failure_order) volatile noexcept;
  bool compare_exchange_weak(
      BaseType & old_value, BaseType new_value,
      memory_order success_order,
      memory_order failure_order) noexcept;
      operator BaseType () const volatile noexcept;
      operator BaseType () const noexcept;
};

template<typename BaseType>
bool atomic_is_lock_free(volatile const atomic<BaseType>*) noexcept;
template<typename BaseType>
bool atomic_is_lock_free(const atomic<BaseType>*) noexcept;
template<typename BaseType>
void atomic_init(volatile atomic<BaseType>*, void*) noexcept;
template<typename BaseType>
void atomic_init(atomic<BaseType>*, void*) noexcept;
template<typename BaseType>
BaseType atomic_exchange(volatile atomic<BaseType>*, memory_order)
  noexcept;
template<typename BaseType>
BaseType atomic_exchange(atomic<BaseType>*, memory_order) noexcept;
template<typename BaseType>
BaseType atomic_exchange_explicit(
  volatile atomic<BaseType>*, memory_order) noexcept;
template<typename BaseType>
BaseType atomic_exchange_explicit(
  atomic<BaseType>*, memory_order) noexcept;
template<typename BaseType>
void atomic_store(volatile atomic<BaseType>*, BaseType) noexcept;
template<typename BaseType>
void atomic_store(atomic<BaseType>*, BaseType) noexcept;
template<typename BaseType>
void atomic_store_explicit(
  volatile atomic<BaseType>*, BaseType, memory_order) noexcept;
template<typename BaseType>
void atomic_store_explicit(
  atomic<BaseType>*, BaseType, memory_order) noexcept;
template<typename BaseType>
BaseType atomic_load(volatile const atomic<BaseType>*) noexcept;
template<typename BaseType>
BaseType atomic_load(const atomic<BaseType>*) noexcept;
template<typename BaseType>
BaseType atomic_load_explicit(
  volatile const atomic<BaseType>*, memory_order) noexcept;
template<typename BaseType>
BaseType atomic_load_explicit(
  const atomic<BaseType>*, memory_order) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_strong(
  volatile atomic<BaseType>*,BaseType * old_value,
  BaseType new_value) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_strong(
  atomic<BaseType>*,BaseType * old_value,
  BaseType new_value) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_strong_explicit(
  volatile atomic<BaseType>*,BaseType * old_value,
  BaseType new_value, memory_order success_order,
  memory_order failure_order) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_strong_explicit(
  atomic<BaseType>*,BaseType * old_value,
  BaseType new_value, memory_order success_order,
  memory_order failure_order) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_weak(
  volatile atomic<BaseType>*,BaseType * old_value,BaseType new_value)
  noexcept;
template<typename BaseType>
bool atomic_compare_exchange_weak(
  atomic<BaseType>*,BaseType * old_value,BaseType new_value) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_weak_explicit(
  volatile atomic<BaseType>*,BaseType * old_value,
  BaseType new_value, memory_order success_order,
  memory_order failure_order) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_weak_explicit(
  atomic<BaseType>*,BaseType * old_value,
  BaseType new_value, memory_order success_order,
  memory_order failure_order) noexcept;
```

**NOTE**:雖然非成員函數通過模板的方式指定，不過他們只作為從在函數提供，並且對於這些函數，不能顯示的指定模板的參數。

### std::atomic 構造函數

使用默認初始值，構造一個`std::atomic`實例。

**聲明**

```
atomic() noexcept;
```

**效果**
使用默認初始值，構造一個新`std::atomic`實例。因對象是靜態存儲的，所以初始化過程也是靜態的。

**NOTE**:當`std::atomic`實例以非靜態方式初始化的，那麼其值就是不可估計的。

**拋出**
無

### std::atomic_init 非成員函數

`std::atomic<BaseType>`實例提供的值，可非原子的進行存儲。

**聲明**

```
template<typename BaseType>
void atomic_init(atomic<BaseType> volatile* p, BaseType v) noexcept;
template<typename BaseType>
void atomic_init(atomic<BaseType>* p, BaseType v) noexcept;
```

**效果**
將值v以非原子存儲的方式，存儲在*p中。調用`atomic<BaseType>`實例中的atomic_init()，這裡需要實例不是默認構造出來的，或者在構造出來的時候被執行了某些操作，否則將會引發未定義行為。

**NOTE**:因為存儲是非原子的，對對象指針p任意的併發訪問(即使是原子操作)都會引發數據競爭。

**拋出**
無

### std::atomic 轉換構造函數

使用提供的BaseType值去構造一個`std::atomic`實例。

**聲明**

```
constexpr atomic(BaseType b) noexcept;
```

**效果**
通過b值構造一個新的`std::atomic`對象。因對象是靜態存儲的，所以初始化過程也是靜態的。

**拋出**
無

### std::atomic 轉換賦值操作

在*this存儲一個新值。

**聲明**

```
BaseType operator=(BaseType b) volatile noexcept;
BaseType operator=(BaseType b) noexcept;
```

**效果**

```
return this->store(b);
```

### std::atomic::is_lock_free 成員函數

確定對於*this是否是無鎖操作。

**聲明**

```
bool is_lock_free() const volatile noexcept;
bool is_lock_free() const noexcept;
```

**返回**
當操作是無鎖操作，那麼就返回true，否則返回false。

**拋出**
無

### std::atomic_is_lock_free 非成員函數

確定對於*this是否是無鎖操作。

**聲明**

```
template<typename BaseType>
bool atomic_is_lock_free(volatile const atomic<BaseType>* p) noexcept;
template<typename BaseType>
bool atomic_is_lock_free(const atomic<BaseType>* p) noexcept;
```

**效果**

```
return p->is_lock_free();
```

### std::atomic::load 成員函數

原子的加載`std::atomic`實例當前的值

**聲明**

```
BaseType load(memory_order order = memory_order_seq_cst)
    const volatile noexcept;
BaseType load(memory_order order = memory_order_seq_cst) const noexcept;
```

**先決條件**
支持`std::memory_order_relaxed`、`std::memory_order_acquire`、`std::memory_order_consume`或`std::memory_order_seq_cst`內存序。

**效果**
原子的加載已存儲到*this上的值。

**返回**
返回存儲在*this上的值。

**拋出**
無

**NOTE**:是對於*this內存地址原子加載的操作。

### std::atomic_load 非成員函數

原子的加載`std::atomic`實例當前的值。

**聲明**

```
template<typename BaseType>
BaseType atomic_load(volatile const atomic<BaseType>* p) noexcept;
template<typename BaseType>
BaseType atomic_load(const atomic<BaseType>* p) noexcept;
```

**效果**

```
return p->load();
```

### std::atomic_load_explicit 非成員函數

原子的加載`std::atomic`實例當前的值。

**聲明**

```
template<typename BaseType>
BaseType atomic_load_explicit(
    volatile const atomic<BaseType>* p, memory_order order) noexcept;
template<typename BaseType>
BaseType atomic_load_explicit(
    const atomic<BaseType>* p, memory_order order) noexcept;
```

**效果**

```
return p->load(order);
```

### std::atomic::operator BastType轉換操作

加載存儲在*this中的值。

**聲明**

```
operator BaseType() const volatile noexcept;
operator BaseType() const noexcept;
```

**效果**

```
return this->load();
```

### std::atomic::store 成員函數

以原子操作的方式存儲一個新值到`atomic<BaseType>`實例中。

**聲明**

```
void store(BaseType new_value,memory_order order = memory_order_seq_cst)
    volatile noexcept;
void store(BaseType new_value,memory_order order = memory_order_seq_cst)
    noexcept;
```

**先決條件**
支持`std::memory_order_relaxed`、`std::memory_order_release`或`std::memory_order_seq_cst`內存序。

**效果**
將new_value原子的存儲到*this中。

**拋出**
無

**NOTE**:是對於*this內存地址原子加載的操作。

### std::atomic_store 非成員函數

以原子操作的方式存儲一個新值到`atomic&lt;BaseType&gt;`實例中。

**聲明**

```
template<typename BaseType>
void atomic_store(volatile atomic<BaseType>* p, BaseType new_value)
    noexcept;
template<typename BaseType>
void atomic_store(atomic<BaseType>* p, BaseType new_value) noexcept;
```

**效果**

```
p->store(new_value);
```

### std::atomic_explicit 非成員函數

以原子操作的方式存儲一個新值到`atomic&lt;BaseType&gt;`實例中。

**聲明**

```
template<typename BaseType>
void atomic_store_explicit(
    volatile atomic<BaseType>* p, BaseType new_value, memory_order order)
    noexcept;
template<typename BaseType>
void atomic_store_explicit(
    atomic<BaseType>* p, BaseType new_value, memory_order order) noexcept;
```

**效果**

```
p->store(new_value,order);
```

### std::atomic::exchange 成員函數

原子的存儲一個新值，並讀取舊值。

**聲明**

```
BaseType exchange(
    BaseType new_value,
    memory_order order = memory_order_seq_cst)
    volatile noexcept;
```

**效果**
原子的將new_value存儲在*this中，並且取出*this中已經存儲的值。

**返回**
返回*this之前的值。

**拋出**
無

**NOTE**:這是對*this內存地址的原子“讀-改-寫”操作。

### std::atomic_exchange 非成員函數

原子的存儲一個新值到`atomic<BaseType>`實例中，並且讀取舊值。

**聲明**

```
template<typename BaseType>
BaseType atomic_exchange(volatile atomic<BaseType>* p, BaseType new_value)
    noexcept;
template<typename BaseType>
BaseType atomic_exchange(atomic<BaseType>* p, BaseType new_value) noexcept;
```

**效果**

```
return p->exchange(new_value);
```

### std::atomic_exchange_explicit 非成員函數

原子的存儲一個新值到`atomic<BaseType>`實例中，並且讀取舊值。

**聲明**

```
template<typename BaseType>
BaseType atomic_exchange_explicit(
    volatile atomic<BaseType>* p, BaseType new_value, memory_order order)
    noexcept;
template<typename BaseType>
BaseType atomic_exchange_explicit(
    atomic<BaseType>* p, BaseType new_value, memory_order order) noexcept;
```

**效果**

```
return p->exchange(new_value,order);
```

### std::atomic::compare_exchange_strong 成員函數

當期望值和新值一樣時，將新值存儲到實例中。如果不相等，那麼就實用新值更新期望值。

**聲明**

```
bool compare_exchange_strong(
    BaseType& expected,BaseType new_value,
    memory_order order = std::memory_order_seq_cst) volatile noexcept;
bool compare_exchange_strong(
    BaseType& expected,BaseType new_value,
    memory_order order = std::memory_order_seq_cst) noexcept;
bool compare_exchange_strong(
    BaseType& expected,BaseType new_value,
    memory_order success_order,memory_order failure_order)
    volatile noexcept;
bool compare_exchange_strong(
    BaseType& expected,BaseType new_value,
    memory_order success_order,memory_order failure_order) noexcept;
```

**先決條件**
failure_order不能是`std::memory_order_release`或`std::memory_order_acq_rel`內存序。

**效果**
將存儲在*this中的expected值與new_value值進行逐位對比，當相等時間new_value存儲在*this中；否則，更新expected的值。

**返回**
當new_value的值與*this中已經存在的值相同，就返回true；否則，返回false。

**拋出**
無

**NOTE**:在success_order==order和failure_order==order的情況下，三個參數的重載函數與四個參數的重載函數等價。除非，order是`std::memory_order_acq_rel`時，failure_order是`std::memory_order_acquire`，且當order是`std::memory_order_release`時，failure_order是`std::memory_order_relaxed`。

**NOTE**:當返回true和success_order內存序時，是對*this內存地址的原子“讀-改-寫”操作；反之，這是對*this內存地址的原子加載操作(failure_order)。

### std::atomic_compare_exchange_strong 非成員函數

當期望值和新值一樣時，將新值存儲到實例中。如果不相等，那麼就實用新值更新期望值。

**聲明**

```
template<typename BaseType>
bool atomic_compare_exchange_strong(
    volatile atomic<BaseType>* p,BaseType * old_value,BaseType new_value)
    noexcept;
template<typename BaseType>
bool atomic_compare_exchange_strong(  
    atomic<BaseType>* p,BaseType * old_value,BaseType new_value) noexcept;
```

**效果**

```
return p->compare_exchange_strong(*old_value,new_value);
```

### std::atomic_compare_exchange_strong_explicit 非成員函數

當期望值和新值一樣時，將新值存儲到實例中。如果不相等，那麼就實用新值更新期望值。

**聲明**

```
template<typename BaseType>
bool atomic_compare_exchange_strong_explicit(
    volatile atomic<BaseType>* p,BaseType * old_value,
    BaseType new_value, memory_order success_order,
    memory_order failure_order) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_strong_explicit(
    atomic<BaseType>* p,BaseType * old_value,
    BaseType new_value, memory_order success_order,
    memory_order failure_order) noexcept;
```

**效果**

```
return p->compare_exchange_strong(
    *old_value,new_value,success_order,failure_order) noexcept;
```

### std::atomic::compare_exchange_weak 成員函數

原子的比較新值和期望值，如果相等，那麼存儲新值並且進行原子化更新。當兩值不相等，或更新未進行，那期望值會更新為新值。

**聲明**

```
bool compare_exchange_weak(
    BaseType& expected,BaseType new_value,
    memory_order order = std::memory_order_seq_cst) volatile noexcept;
bool compare_exchange_weak(
    BaseType& expected,BaseType new_value,
    memory_order order = std::memory_order_seq_cst) noexcept;
bool compare_exchange_weak(
    BaseType& expected,BaseType new_value,
    memory_order success_order,memory_order failure_order)
    volatile noexcept;
bool compare_exchange_weak(
    BaseType& expected,BaseType new_value,
    memory_order success_order,memory_order failure_order) noexcept;
```

**先決條件**
failure_order不能是`std::memory_order_release`或`std::memory_order_acq_rel`內存序。

**效果**
將存儲在*this中的expected值與new_value值進行逐位對比，當相等時間new_value存儲在*this中；否則，更新expected的值。

**返回**
當new_value的值與*this中已經存在的值相同，就返回true；否則，返回false。

**拋出**
無

**NOTE**:在success_order==order和failure_order==order的情況下，三個參數的重載函數與四個參數的重載函數等價。除非，order是`std::memory_order_acq_rel`時，failure_order是`std::memory_order_acquire`，且當order是`std::memory_order_release`時，failure_order是`std::memory_order_relaxed`。

**NOTE**:當返回true和success_order內存序時，是對*this內存地址的原子“讀-改-寫”操作；反之，這是對*this內存地址的原子加載操作(failure_order)。

### std::atomic_compare_exchange_weak 非成員函數

原子的比較新值和期望值，如果相等，那麼存儲新值並且進行原子化更新。當兩值不相等，或更新未進行，那期望值會更新為新值。

**聲明**

```
template<typename BaseType>
bool atomic_compare_exchange_weak(
    volatile atomic<BaseType>* p,BaseType * old_value,BaseType new_value)
    noexcept;
template<typename BaseType>
bool atomic_compare_exchange_weak(
    atomic<BaseType>* p,BaseType * old_value,BaseType new_value) noexcept;
```

**效果**

```
return p->compare_exchange_weak(*old_value,new_value);
```

### std::atomic_compare_exchange_weak_explicit 非成員函數

原子的比較新值和期望值，如果相等，那麼存儲新值並且進行原子化更新。當兩值不相等，或更新未進行，那期望值會更新為新值。

**聲明**

```
template<typename BaseType>
bool atomic_compare_exchange_weak_explicit(
    volatile atomic<BaseType>* p,BaseType * old_value,
    BaseType new_value, memory_order success_order,
    memory_order failure_order) noexcept;
template<typename BaseType>
bool atomic_compare_exchange_weak_explicit(
    atomic<BaseType>* p,BaseType * old_value,
    BaseType new_value, memory_order success_order,
    memory_order failure_order) noexcept;
```

**效果**

```
return p->compare_exchange_weak(
   *old_value,new_value,success_order,failure_order);
```

## D.3.9 std::atomic模板類型的特化

`std::atomic`類模板的特化類型有整型和指針類型。對於整型來說，特化模板提供原子加減，以及位域操作(主模板未提供)。對於指針類型來說，特化模板提供原子指針的運算(主模板未提供)。

特化模板提供如下整型：

```
std::atomic<bool>
std::atomic<char>
std::atomic<signed char>
std::atomic<unsigned char>
std::atomic<short>
std::atomic<unsigned short>
std::atomic<int>
std::atomic<unsigned>
std::atomic<long>
std::atomic<unsigned long>
std::atomic<long long>
std::atomic<unsigned long long>
std::atomic<wchar_t>
std::atomic<char16_t>
std::atomic<char32_t&gt;
```

`std::atomic<T*>`原子指針，可以使用以上的類型作為T。

## D.3.10 特化std::atomic&lt;integral-type&gt;

`std::atomic&lt;integral-type&gt;`是為每一個基礎整型提供的`std::atomic`類模板，其中提供了一套完整的整型操作。

下面的特化模板也適用於`std::atomic<>`類模板：

```
std::atomic<char>
std::atomic<signed char>
std::atomic<unsigned char>
std::atomic<short>
std::atomic<unsigned short>
std::atomic<int>
std::atomic<unsigned>
std::atomic<long>
std::atomic<unsigned long>
std::atomic<long long>
std::atomic<unsigned long long>
std::atomic<wchar_t>
std::atomic<char16_t>
std::atomic<char32_t>
```

因為原子操作只能執行其中一個，所以特化模板的實例不可`CopyConstructible`(拷貝構造)和`CopyAssignable`(拷貝賦值)。

**類型定義**

```
template<>
struct atomic<integral-type>
{
  atomic() noexcept = default;
  constexpr atomic(integral-type) noexcept;
  bool operator=(integral-type) volatile noexcept;

  atomic(const atomic&) = delete;
  atomic& operator=(const atomic&) = delete;
  atomic& operator=(const atomic&) volatile = delete;

  bool is_lock_free() const volatile noexcept;
  bool is_lock_free() const noexcept;

  void store(integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
  void store(integral-type,memory_order = memory_order_seq_cst) noexcept;
  integral-type load(memory_order = memory_order_seq_cst)
      const volatile noexcept;
  integral-type load(memory_order = memory_order_seq_cst) const noexcept;
  integral-type exchange(
      integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
 integral-type exchange(
      integral-type,memory_order = memory_order_seq_cst) noexcept;

  bool compare_exchange_strong(
      integral-type & old_value,integral-type new_value,
      memory_order order = memory_order_seq_cst) volatile noexcept;
  bool compare_exchange_strong(
      integral-type & old_value,integral-type new_value,
      memory_order order = memory_order_seq_cst) noexcept;
  bool compare_exchange_strong(
      integral-type & old_value,integral-type new_value,
      memory_order success_order,memory_order failure_order)
      volatile noexcept;
  bool compare_exchange_strong(
      integral-type & old_value,integral-type new_value,
      memory_order success_order,memory_order failure_order) noexcept;
  bool compare_exchange_weak(
      integral-type & old_value,integral-type new_value,
      memory_order order = memory_order_seq_cst) volatile noexcept;
  bool compare_exchange_weak(
      integral-type & old_value,integral-type new_value,
      memory_order order = memory_order_seq_cst) noexcept;
  bool compare_exchange_weak(
      integral-type & old_value,integral-type new_value,
      memory_order success_order,memory_order failure_order)
      volatile noexcept;
  bool compare_exchange_weak(
      integral-type & old_value,integral-type new_value,
      memory_order success_order,memory_order failure_order) noexcept;

  operator integral-type() const volatile noexcept;
  operator integral-type() const noexcept;

  integral-type fetch_add(
      integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
  integral-type fetch_add(
      integral-type,memory_order = memory_order_seq_cst) noexcept;
  integral-type fetch_sub(
      integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
  integral-type fetch_sub(
      integral-type,memory_order = memory_order_seq_cst) noexcept;
  integral-type fetch_and(
      integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
  integral-type fetch_and(
      integral-type,memory_order = memory_order_seq_cst) noexcept;
  integral-type fetch_or(
      integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
  integral-type fetch_or(
      integral-type,memory_order = memory_order_seq_cst) noexcept;
  integral-type fetch_xor(
      integral-type,memory_order = memory_order_seq_cst)
      volatile noexcept;
  integral-type fetch_xor(
      integral-type,memory_order = memory_order_seq_cst) noexcept;

  integral-type operator++() volatile noexcept;
  integral-type operator++() noexcept;
  integral-type operator++(int) volatile noexcept;
  integral-type operator++(int) noexcept;
  integral-type operator--() volatile noexcept;
  integral-type operator--() noexcept;
  integral-type operator--(int) volatile noexcept;
  integral-type operator--(int) noexcept;
  integral-type operator+=(integral-type) volatile noexcept;
  integral-type operator+=(integral-type) noexcept;
  integral-type operator-=(integral-type) volatile noexcept;
  integral-type operator-=(integral-type) noexcept;
  integral-type operator&=(integral-type) volatile noexcept;
  integral-type operator&=(integral-type) noexcept;
  integral-type operator|=(integral-type) volatile noexcept;
  integral-type operator|=(integral-type) noexcept;
  integral-type operator^=(integral-type) volatile noexcept;
  integral-type operator^=(integral-type) noexcept;
};

bool atomic_is_lock_free(volatile const atomic<integral-type>*) noexcept;
bool atomic_is_lock_free(const atomic<integral-type>*) noexcept;
void atomic_init(volatile atomic<integral-type>*,integral-type) noexcept;
void atomic_init(atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_exchange(
    volatile atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_exchange(
    atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_exchange_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_exchange_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
void atomic_store(volatile atomic<integral-type>*,integral-type) noexcept;
void atomic_store(atomic<integral-type>*,integral-type) noexcept;
void atomic_store_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
void atomic_store_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_load(volatile const atomic<integral-type>*) noexcept;
integral-type atomic_load(const atomic<integral-type>*) noexcept;
integral-type atomic_load_explicit(
    volatile const atomic<integral-type>*,memory_order) noexcept;
integral-type atomic_load_explicit(
    const atomic<integral-type>*,memory_order) noexcept;
bool atomic_compare_exchange_strong(
    volatile atomic<integral-type>*,
    integral-type * old_value,integral-type new_value) noexcept;
bool atomic_compare_exchange_strong(
    atomic<integral-type>*,
    integral-type * old_value,integral-type new_value) noexcept;
bool atomic_compare_exchange_strong_explicit(
    volatile atomic<integral-type>*,
    integral-type * old_value,integral-type new_value,
    memory_order success_order,memory_order failure_order) noexcept;
bool atomic_compare_exchange_strong_explicit(
    atomic<integral-type>*,
    integral-type * old_value,integral-type new_value,
    memory_order success_order,memory_order failure_order) noexcept;
bool atomic_compare_exchange_weak(
    volatile atomic<integral-type>*,
    integral-type * old_value,integral-type new_value) noexcept;
bool atomic_compare_exchange_weak(
    atomic<integral-type>*,
    integral-type * old_value,integral-type new_value) noexcept;
bool atomic_compare_exchange_weak_explicit(
    volatile atomic<integral-type>*,
    integral-type * old_value,integral-type new_value,
    memory_order success_order,memory_order failure_order) noexcept;
bool atomic_compare_exchange_weak_explicit(
    atomic<integral-type>*,
    integral-type * old_value,integral-type new_value,
    memory_order success_order,memory_order failure_order) noexcept;

integral-type atomic_fetch_add(
    volatile atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_add(
    atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_add_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_add_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_sub(
    volatile atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_sub(
    atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_sub_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_sub_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_and(
    volatile atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_and(
    atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_and_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_and_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_or(
    volatile atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_or(
    atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_or_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_or_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_xor(
    volatile atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_xor(
    atomic<integral-type>*,integral-type) noexcept;
integral-type atomic_fetch_xor_explicit(
    volatile atomic<integral-type>*,integral-type, memory_order) noexcept;
integral-type atomic_fetch_xor_explicit(
    atomic<integral-type>*,integral-type, memory_order) noexcept;
```

這些操作在主模板中也有提供(見D.3.8)。

### std::atomic&lt;integral-type&gt;::fetch_add 成員函數

原子的加載一個值，然後使用與提供i相加的結果，替換掉原值。

**聲明**

```
integral-type fetch_add(
    integral-type i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
integral-type fetch_add(
    integral-type i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value+i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_add 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值相加，替換原值。

**聲明**

```
integral-type atomic_fetch_add(
    volatile atomic<integral-type>* p, integral-type i) noexcept;
integral-type atomic_fetch_add(
    atomic<integral-type>* p, integral-type i) noexcept;
```

**效果**

```
return p->fetch_add(i);
```

### std::atomic_fetch_add_explicit 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值相加，替換原值。

**聲明**

```
integral-type atomic_fetch_add_explicit(
    volatile atomic<integral-type>* p, integral-type i,
    memory_order order) noexcept;
integral-type atomic_fetch_add_explicit(
    atomic<integral-type>* p, integral-type i, memory_order order)
    noexcept;
```

**效果**

```
return p->fetch_add(i,order);
```

### std::atomic&lt;integral-type&gt;::fetch_sub 成員函數

原子的加載一個值，然後使用與提供i相減的結果，替換掉原值。

**聲明**

```
integral-type fetch_sub(
    integral-type i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
integral-type fetch_sub(
    integral-type i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value-i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_sub 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值相減，替換原值。

**聲明**

```
integral-type atomic_fetch_sub(
    volatile atomic<integral-type>* p, integral-type i) noexcept;
integral-type atomic_fetch_sub(
    atomic<integral-type>* p, integral-type i) noexcept;
```

**效果**

```
return p->fetch_sub(i);
```

### std::atomic_fetch_sub_explicit 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值相減，替換原值。

**聲明**

```
integral-type atomic_fetch_sub_explicit(
    volatile atomic<integral-type>* p, integral-type i,
    memory_order order) noexcept;
integral-type atomic_fetch_sub_explicit(
    atomic<integral-type>* p, integral-type i, memory_order order)
    noexcept;
```

**效果**

```
return p->fetch_sub(i,order);
```

### std::atomic&lt;integral-type&gt;::fetch_and 成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位與操作後，替換原值。

**聲明**

```
integral-type fetch_and(
    integral-type i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
integral-type fetch_and(
    integral-type i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value&i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_and 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位與操作後，替換原值。

**聲明**

```
integral-type atomic_fetch_and(
    volatile atomic<integral-type>* p, integral-type i) noexcept;
integral-type atomic_fetch_and(
    atomic<integral-type>* p, integral-type i) noexcept;
```

**效果**

```
return p->fetch_and(i);
```

### std::atomic_fetch_and_explicit 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位與操作後，替換原值。

**聲明**

```
integral-type atomic_fetch_and_explicit(
    volatile atomic<integral-type>* p, integral-type i,
    memory_order order) noexcept;
integral-type atomic_fetch_and_explicit(
    atomic<integral-type>* p, integral-type i, memory_order order)
    noexcept;
```

**效果**

```
return p->fetch_and(i,order);
```

### std::atomic&lt;integral-type&gt;::fetch_or 成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位或操作後，替換原值。

**聲明**

```
integral-type fetch_or(
    integral-type i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
integral-type fetch_or(
    integral-type i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value|i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_or 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位或操作後，替換原值。

**聲明**

```
integral-type atomic_fetch_or(
    volatile atomic<integral-type>* p, integral-type i) noexcept;
integral-type atomic_fetch_or(
    atomic<integral-type>* p, integral-type i) noexcept;
```

**效果**

```
return p->fetch_or(i);
```

### std::atomic_fetch_or_explicit 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位或操作後，替換原值。

**聲明**

```
integral-type atomic_fetch_or_explicit(
    volatile atomic<integral-type>* p, integral-type i,
    memory_order order) noexcept;
integral-type atomic_fetch_or_explicit(
    atomic<integral-type>* p, integral-type i, memory_order order)
    noexcept;
```

**效果**

```
return p->fetch_or(i,order);
```

### std::atomic&lt;integral-type&gt;::fetch_xor 成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位亦或操作後，替換原值。

**聲明**

```
integral-type fetch_xor(
    integral-type i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
integral-type fetch_xor(
    integral-type i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value^i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_xor 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位異或操作後，替換原值。

**聲明**

```
integral-type atomic_fetch_xor_explicit(
    volatile atomic<integral-type>* p, integral-type i,
    memory_order order) noexcept;
integral-type atomic_fetch_xor_explicit(
    atomic<integral-type>* p, integral-type i, memory_order order)
    noexcept;
```

**效果**

```
return p->fetch_xor(i,order);
```

### std::atomic_fetch_xor_explicit 非成員函數

從`atomic<integral-type>`實例中原子的讀取一個值，並且將其與給定i值進行位異或操作後，替換原值。

**聲明**

```
integral-type atomic_fetch_xor_explicit(
    volatile atomic<integral-type>* p, integral-type i,
    memory_order order) noexcept;
integral-type atomic_fetch_xor_explicit(
    atomic<integral-type>* p, integral-type i, memory_order order)
    noexcept;
```

**效果**

```
return p->fetch_xor(i,order);
```

### std::atomic&lt;integral-type&gt;::operator++ 前置遞增操作

原子的將*this中存儲的值加1，並返回新值。

**聲明**

```
integral-type operator++() volatile noexcept;
integral-type operator++() noexcept;
```

**效果**

```
return this->fetch_add(1) + 1;
```

### std::atomic&lt;integral-type&gt;::operator++ 後置遞增操作

原子的將*this中存儲的值加1，並返回舊值。

**聲明**

```
integral-type operator++() volatile noexcept;
integral-type operator++() noexcept;
```

**效果**

```
return this->fetch_add(1);
```

### std::atomic&lt;integral-type&gt;::operator-- 前置遞減操作

原子的將*this中存儲的值減1，並返回新值。

**聲明**

```
integral-type operator--() volatile noexcept;
integral-type operator--() noexcept;
```

**效果**

```
return this->fetch_add(1) - 1;
```

### std::atomic&lt;integral-type&gt;::operator-- 後置遞減操作

原子的將*this中存儲的值減1，並返回舊值。

**聲明**

```
integral-type operator--() volatile noexcept;
integral-type operator--() noexcept;
```

**效果**

```
return this->fetch_add(1);
```

### std::atomic&lt;integral-type&gt;::operator+= 複合賦值操作

原子的將給定值與*this中的值相加，並返回新值。

**聲明**

```
integral-type operator+=(integral-type i) volatile noexcept;
integral-type operator+=(integral-type i) noexcept;
```

**效果**

```
return this->fetch_add(i) + i;
```

### std::atomic&lt;integral-type&gt;::operator-= 複合賦值操作

原子的將給定值與*this中的值相減，並返回新值。

**聲明**

```
integral-type operator-=(integral-type i) volatile noexcept;
integral-type operator-=(integral-type i) noexcept;
```

**效果**

```
return this->fetch_sub(i,std::memory_order_seq_cst) – i;
```

### std::atomic&lt;integral-type&gt;::operator&= 複合賦值操作

原子的將給定值與*this中的值相與，並返回新值。

**聲明**

```
integral-type operator&=(integral-type i) volatile noexcept;
integral-type operator&=(integral-type i) noexcept;
```

**效果**

```
return this->fetch_and(i) & i;
```

### std::atomic&lt;integral-type&gt;::operator|= 複合賦值操作

原子的將給定值與*this中的值相或，並返回新值。

**聲明**

```
integral-type operator|=(integral-type i) volatile noexcept;
integral-type operator|=(integral-type i) noexcept;
```

**效果**

```
return this->fetch_or(i,std::memory_order_seq_cst) | i;
```

### std::atomic&lt;integral-type&gt;::operator^= 複合賦值操作

原子的將給定值與*this中的值相亦或，並返回新值。

**聲明**

```
integral-type operator^=(integral-type i) volatile noexcept;
integral-type operator^=(integral-type i) noexcept;
```

**效果**

```
return this->fetch_xor(i,std::memory_order_seq_cst) ^ i;
```

### std::atomic&lt;T*&gt; 局部特化

`std::atomic<T*>`為`std::atomic`特化了指針類型原子變量，並提供了一系列相關操作。

`std::atomic<T*>`是CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)的，因為操作是原子的，在同一時間只能執行一個操作。

**類型定義**

```
template<typename T>
struct atomic<T*>
{
  atomic() noexcept = default;
  constexpr atomic(T*) noexcept;
  bool operator=(T*) volatile;
  bool operator=(T*);

  atomic(const atomic&) = delete;
  atomic& operator=(const atomic&) = delete;
  atomic& operator=(const atomic&) volatile = delete;

  bool is_lock_free() const volatile noexcept;
  bool is_lock_free() const noexcept;
  void store(T*,memory_order = memory_order_seq_cst) volatile noexcept;
  void store(T*,memory_order = memory_order_seq_cst) noexcept;
  T* load(memory_order = memory_order_seq_cst) const volatile noexcept;
  T* load(memory_order = memory_order_seq_cst) const noexcept;
  T* exchange(T*,memory_order = memory_order_seq_cst) volatile noexcept;
  T* exchange(T*,memory_order = memory_order_seq_cst) noexcept;

  bool compare_exchange_strong(
      T* & old_value, T* new_value,
      memory_order order = memory_order_seq_cst) volatile noexcept;
  bool compare_exchange_strong(
      T* & old_value, T* new_value,
      memory_order order = memory_order_seq_cst) noexcept;
  bool compare_exchange_strong(
      T* & old_value, T* new_value,
      memory_order success_order,memory_order failure_order)  
      volatile noexcept;
  bool compare_exchange_strong(
      T* & old_value, T* new_value,
      memory_order success_order,memory_order failure_order) noexcept;
  bool compare_exchange_weak(
      T* & old_value, T* new_value,
      memory_order order = memory_order_seq_cst) volatile noexcept;
  bool compare_exchange_weak(
      T* & old_value, T* new_value,
      memory_order order = memory_order_seq_cst) noexcept;
  bool compare_exchange_weak(
      T* & old_value, T* new_value,
      memory_order success_order,memory_order failure_order)
      volatile noexcept;
  bool compare_exchange_weak(
      T* & old_value, T* new_value,
      memory_order success_order,memory_order failure_order) noexcept;

  operator T*() const volatile noexcept;
  operator T*() const noexcept;

  T* fetch_add(
      ptrdiff_t,memory_order = memory_order_seq_cst) volatile noexcept;
  T* fetch_add(
      ptrdiff_t,memory_order = memory_order_seq_cst) noexcept;
  T* fetch_sub(
      ptrdiff_t,memory_order = memory_order_seq_cst) volatile noexcept;
  T* fetch_sub(
      ptrdiff_t,memory_order = memory_order_seq_cst) noexcept;

  T* operator++() volatile noexcept;
  T* operator++() noexcept;
  T* operator++(int) volatile noexcept;
  T* operator++(int) noexcept;
  T* operator--() volatile noexcept;
  T* operator--() noexcept;
  T* operator--(int) volatile noexcept;
  T* operator--(int) noexcept;

  T* operator+=(ptrdiff_t) volatile noexcept;
  T* operator+=(ptrdiff_t) noexcept;
  T* operator-=(ptrdiff_t) volatile noexcept;
  T* operator-=(ptrdiff_t) noexcept;
};

bool atomic_is_lock_free(volatile const atomic<T*>*) noexcept;
bool atomic_is_lock_free(const atomic<T*>*) noexcept;
void atomic_init(volatile atomic<T*>*, T*) noexcept;
void atomic_init(atomic<T*>*, T*) noexcept;
T* atomic_exchange(volatile atomic<T*>*, T*) noexcept;
T* atomic_exchange(atomic<T*>*, T*) noexcept;
T* atomic_exchange_explicit(volatile atomic<T*>*, T*, memory_order)
  noexcept;
T* atomic_exchange_explicit(atomic<T*>*, T*, memory_order) noexcept;
void atomic_store(volatile atomic<T*>*, T*) noexcept;
void atomic_store(atomic<T*>*, T*) noexcept;
void atomic_store_explicit(volatile atomic<T*>*, T*, memory_order)
  noexcept;
void atomic_store_explicit(atomic<T*>*, T*, memory_order) noexcept;
T* atomic_load(volatile const atomic<T*>*) noexcept;
T* atomic_load(const atomic<T*>*) noexcept;
T* atomic_load_explicit(volatile const atomic<T*>*, memory_order) noexcept;
T* atomic_load_explicit(const atomic<T*>*, memory_order) noexcept;
bool atomic_compare_exchange_strong(
  volatile atomic<T*>*,T* * old_value,T* new_value) noexcept;
bool atomic_compare_exchange_strong(
  volatile atomic<T*>*,T* * old_value,T* new_value) noexcept;
bool atomic_compare_exchange_strong_explicit(
  atomic<T*>*,T* * old_value,T* new_value,
  memory_order success_order,memory_order failure_order) noexcept;
bool atomic_compare_exchange_strong_explicit(
  atomic<T*>*,T* * old_value,T* new_value,
  memory_order success_order,memory_order failure_order) noexcept;
bool atomic_compare_exchange_weak(
  volatile atomic<T*>*,T* * old_value,T* new_value) noexcept;
bool atomic_compare_exchange_weak(
  atomic<T*>*,T* * old_value,T* new_value) noexcept;
bool atomic_compare_exchange_weak_explicit(
  volatile atomic<T*>*,T* * old_value, T* new_value,
  memory_order success_order,memory_order failure_order) noexcept;
bool atomic_compare_exchange_weak_explicit(
  atomic<T*>*,T* * old_value, T* new_value,
  memory_order success_order,memory_order failure_order) noexcept;

T* atomic_fetch_add(volatile atomic<T*>*, ptrdiff_t) noexcept;
T* atomic_fetch_add(atomic<T*>*, ptrdiff_t) noexcept;
T* atomic_fetch_add_explicit(
  volatile atomic<T*>*, ptrdiff_t, memory_order) noexcept;
T* atomic_fetch_add_explicit(
  atomic<T*>*, ptrdiff_t, memory_order) noexcept;
T* atomic_fetch_sub(volatile atomic<T*>*, ptrdiff_t) noexcept;
T* atomic_fetch_sub(atomic<T*>*, ptrdiff_t) noexcept;
T* atomic_fetch_sub_explicit(
  volatile atomic<T*>*, ptrdiff_t, memory_order) noexcept;
T* atomic_fetch_sub_explicit(
  atomic<T*>*, ptrdiff_t, memory_order) noexcept;
```

在主模板中也提供了一些相同的操作(可見11.3.8節)。

### std::atomic&lt;T*&gt;::fetch_add 成員函數

原子的加載一個值，然後使用與提供i相加(使用標準指針運算規則)的結果，替換掉原值。

**聲明**

```
T* fetch_add(
    ptrdiff_t i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
T* fetch_add(
    ptrdiff_t i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value+i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_add 非成員函數

從`atomic<T*>`實例中原子的讀取一個值，並且將其與給定i值進行位相加操作(使用標準指針運算規則)後，替換原值。

**聲明**

```
T* atomic_fetch_add(volatile atomic<T*>* p, ptrdiff_t i) noexcept;
T* atomic_fetch_add(atomic<T*>* p, ptrdiff_t i) noexcept;
```

**效果**

```
return p->fetch_add(i);
```

### std::atomic_fetch_add_explicit 非成員函數

從`atomic<T*>`實例中原子的讀取一個值，並且將其與給定i值進行位相加操作(使用標準指針運算規則)後，替換原值。

**聲明**

```
T* atomic_fetch_add_explicit(
     volatile atomic<T*>* p, ptrdiff_t i,memory_order order) noexcept;
T* atomic_fetch_add_explicit(
     atomic<T*>* p, ptrdiff_t i, memory_order order) noexcept;
```

**效果**

```
return p->fetch_add(i,order);
```

### std::atomic&lt;T*&gt;::fetch_sub 成員函數

原子的加載一個值，然後使用與提供i相減(使用標準指針運算規則)的結果，替換掉原值。

**聲明**

```
T* fetch_sub(
    ptrdiff_t i,memory_order order = memory_order_seq_cst)
    volatile noexcept;
T* fetch_sub(
    ptrdiff_t i,memory_order order = memory_order_seq_cst) noexcept;
```

**效果**
原子的查詢*this中的值，將old-value-i的和存回*this。

**返回**
返回*this之前存儲的值。

**拋出**
無

**NOTE**:對於*this的內存地址來說，這是一個“讀-改-寫”操作。

### std::atomic_fetch_sub 非成員函數

從`atomic<T*>`實例中原子的讀取一個值，並且將其與給定i值進行位相減操作(使用標準指針運算規則)後，替換原值。

**聲明**

```
T* atomic_fetch_sub(volatile atomic<T*>* p, ptrdiff_t i) noexcept;
T* atomic_fetch_sub(atomic<T*>* p, ptrdiff_t i) noexcept;
```

**效果**

```
return p->fetch_sub(i);
```

### std::atomic_fetch_sub_explicit 非成員函數

從`atomic<T*>`實例中原子的讀取一個值，並且將其與給定i值進行位相減操作(使用標準指針運算規則)後，替換原值。

**聲明**

```
T* atomic_fetch_sub_explicit(
     volatile atomic<T*>* p, ptrdiff_t i,memory_order order) noexcept;
T* atomic_fetch_sub_explicit(
     atomic<T*>* p, ptrdiff_t i, memory_order order) noexcept;
```

**效果**

```
return p->fetch_sub(i,order);
```

### std::atomic&lt;T*&gt;::operator++ 前置遞增操作

原子的將*this中存儲的值加1(使用標準指針運算規則)，並返回新值。

**聲明**

```
T* operator++() volatile noexcept;
T* operator++() noexcept;
```

**效果**

```
return this->fetch_add(1) + 1;
```

### std::atomic&lt;T*&gt;::operator++ 後置遞增操作

原子的將*this中存儲的值加1(使用標準指針運算規則)，並返回舊值。

**聲明**

```
T* operator++() volatile noexcept;
T* operator++() noexcept;
```

**效果**

```
return this->fetch_add(1);
```

### std::atomic&lt;T*&gt;::operator-- 前置遞減操作

原子的將*this中存儲的值減1(使用標準指針運算規則)，並返回新值。

**聲明**

```
T* operator--() volatile noexcept;
T* operator--() noexcept;
```

**效果**

```
return this->fetch_sub(1) - 1;
```

### std::atomic&lt;T*&gt;::operator-- 後置遞減操作

原子的將*this中存儲的值減1(使用標準指針運算規則)，並返回舊值。

**聲明**

```
T* operator--() volatile noexcept;
T* operator--() noexcept;
```

**效果**

```
return this->fetch_sub(1);
```

### std::atomic&lt;T*&gt;::operator+= 複合賦值操作

原子的將*this中存儲的值與給定值相加(使用標準指針運算規則)，並返回新值。

**聲明**

```
T* operator+=(ptrdiff_t i) volatile noexcept;
T* operator+=(ptrdiff_t i) noexcept;
```

**效果**

```
return this->fetch_add(i) + i;
```

### std::atomic&lt;T*&gt;::operator-= 複合賦值操作


原子的將*this中存儲的值與給定值相減(使用標準指針運算規則)，並返回新值。

**聲明**

```
T* operator+=(ptrdiff_t i) volatile noexcept;
T* operator+=(ptrdiff_t i) noexcept;
```

**效果**

```
return this->fetch_add(i) - i;
```