# D.5 &lt;mutex&gt;頭文件

`<mutex>`頭文件提供互斥工具：互斥類型，鎖類型和函數，還有確保操作只執行一次的機制。

**頭文件內容**

```
namespace std
{
  class mutex;
  class recursive_mutex;
  class timed_mutex;
  class recursive_timed_mutex;

  struct adopt_lock_t;
  struct defer_lock_t;
  struct try_to_lock_t;

  constexpr adopt_lock_t adopt_lock{};
  constexpr defer_lock_t defer_lock{};
  constexpr try_to_lock_t try_to_lock{};

  template<typename LockableType>
  class lock_guard;

  template<typename LockableType>
  class unique_lock;

  template<typename LockableType1,typename... LockableType2>
  void lock(LockableType1& m1,LockableType2& m2...);

  template<typename LockableType1,typename... LockableType2>
  int try_lock(LockableType1& m1,LockableType2& m2...);

  struct once_flag;

  template<typename Callable,typename... Args>
  void call_once(once_flag& flag,Callable func,Args args...);
}
```

## D.5.1 std::mutex類

`std::mutex`類型為線程提供基本的互斥和同步工具，這些工具可以用來保護共享數據。互斥量可以用來保護數據，互斥量上鎖必須要調用lok()或try_lock()。當有一個線程獲取已經獲取了鎖，那麼其他線程想要在獲取鎖的時候，會在嘗試或取鎖的時候失敗(調用try_lock())或阻塞(調用lock())，具體酌情而定。當線程完成對共享數據的訪問，之後就必須調用unlock()對鎖進行釋放，並且允許其他線程來訪問這個共享數據。

`std::mutex`符合Lockable的需求。

**類型定義**

```
class mutex
{
public:
  mutex(mutex const&)=delete;
  mutex& operator=(mutex const&)=delete;

  constexpr mutex() noexcept;
  ~mutex();

  void lock();
  void unlock();
  bool try_lock();
};
```

### std::mutex 默認構造函數

構造一個`std::mutex`對象。

**聲明**

```
constexpr mutex() noexcept;
```

**效果**<br>
構造一個`std::mutex`實例。

**後置條件**<br>
新構造的`std::mutex`對象是未鎖的。

**拋出**<br>
無

### std::mutex 析構函數

銷燬一個`std::mutex`對象。

**聲明**

```
~mutex();
```

**先決條件**<br>
*this必須是未鎖的。

**效果**<br>
銷燬*this。

**拋出**<br>
無

### std::mutex::lock 成員函數

為當前線程獲取`std::mutex`上的鎖。

**聲明**

```
void lock();
```

**先決條件**<br>
*this上必須沒有持有一個鎖。

**效果**<br>
阻塞當前線程，知道*this獲取鎖。

**後置條件**<br>
*this被調用線程鎖住。

**拋出**<br>
當有錯誤產生，拋出`std::system_error`類型異常。

### std::mutex::try_lock 成員函數

嘗試為當前線程獲取`std::mutex`上的鎖。

**聲明**

```
bool try_lock();
```

**先決條件**<br>
*this上必須沒有持有一個鎖。

**效果**<br>
嘗試為當前線程*this獲取上的鎖，失敗時當前線程不會被阻塞。

**返回**<br>
當調用線程獲取鎖時，返回true。

**後置條件**<br>
當*this被調用線程鎖住，則返回true。

**拋出**
無

**NOTE** 該函數在獲取鎖時，可能失敗(並返回false)，即使沒有其他線程持有*this上的鎖。

### std::mutex::unlock 成員函數

釋放當前線程獲取的`std::mutex`鎖。

**聲明**

```
void unlock();
```

**先決條件**<br>
*this上必須持有一個鎖。

**效果**<be>
釋放當前線程獲取到`*this`上的鎖。任意等待獲取`*this`上的線程，會在該函數調用後解除阻塞。

**後置條件**<br>
調用線程不在擁有*this上的鎖。

**拋出**<br>
無

## D.5.2 std::recursive_mutex類

`std::recursive_mutex`類型為線程提供基本的互斥和同步工具，可以用來保護共享數據。互斥量可以用來保護數據，互斥量上鎖必須要調用lok()或try_lock()。當有一個線程獲取已經獲取了鎖，那麼其他線程想要在獲取鎖的時候，會在嘗試或取鎖的時候失敗(調用try_lock())或阻塞(調用lock())，具體酌情而定。當線程完成對共享數據的訪問，之後就必須調用unlock()對鎖進行釋放，並且允許其他線程來訪問這個共享數據。

這個互斥量是可遞歸的，所以一個線程獲取`std::recursive_mutex`後可以在之後繼續使用lock()或try_lock()來增加鎖的計數。只有當線程調用unlock釋放鎖，其他線程才可能用lock()或try_lock()獲取鎖。

`std::recursive_mutex`符合Lockable的需求。

**類型定義**

```
class recursive_mutex
{
public:
  recursive_mutex(recursive_mutex const&)=delete;
  recursive_mutex& operator=(recursive_mutex const&)=delete;

  recursive_mutex() noexcept;
 ~recursive_mutex();

  void lock();
  void unlock();
  bool try_lock() noexcept;
};
```

### std::recursive_mutex 默認構造函數

構造一個`std::recursive_mutex`對象。

**聲明**

```
recursive_mutex() noexcept;
```

**效果**<br>
構造一個`std::recursive_mutex`實例。

**後置條件**<br>
新構造的`std::recursive_mutex`對象是未鎖的。

**拋出**<br>
當無法創建一個新的`std::recursive_mutex`時，拋出`std::system_error`異常。

### std::recursive_mutex 析構函數

銷燬一個`std::recursive_mutex`對象。

**聲明**

```
~recursive_mutex();
```

**先決條件**<br>
*this必須是未鎖的。

**效果**<br>
銷燬*this。

**拋出**<br>
無

### std::recursive_mutex::lock 成員函數

為當前線程獲取`std::recursive_mutex`上的鎖。

**聲明**

```
void lock();
```

**效果**<br>
阻塞線程，直到獲取*this上的鎖。

**先決條件**<br>
調用線程鎖住*this上的鎖。當調用已經持有一個*this的鎖時，鎖的計數會增加1。

**拋出**<br>
當有錯誤產生，將拋出`std::system_error`異常。

### std::recursive_mutex::try_lock 成員函數

嘗試為當前線程獲取`std::recursive_mutex`上的鎖。

**聲明**

```
bool try_lock() noexcept;
```

**效果**<br>
嘗試為當前線程*this獲取上的鎖，失敗時當前線程不會被阻塞。

**返回**<br>
當調用線程獲取鎖時，返回true；否則，返回false。

**後置條件**<br>
當*this被調用線程鎖住，則返回true。

**拋出**
無

**NOTE** 該函數在獲取鎖時，當函數返回true時，`*this`上對鎖的計數會加一。如果當前線程還未獲取`*this`上的鎖，那麼該函數在獲取鎖時，可能失敗(並返回false)，即使沒有其他線程持有`*this`上的鎖。

### std::recursive_mutex::unlock 成員函數

釋放當前線程獲取的`std::recursive_mutex`鎖。

**聲明**

```
void unlock();
```

**先決條件**<br>
*this上必須持有一個鎖。

**效果**<be>
釋放當前線程獲取到`*this`上的鎖。如果這是`*this`在當前線程上最後一個鎖，那麼任意等待獲取`*this`上的線程，會在該函數調用後解除其中一個線程的阻塞。

**後置條件**<br>
`*this`上鎖的計數會在該函數調用後減一。

**拋出**<br>
無

## D.5.3 std::timed_mutex類

`std::timed_mutex`類型在`std::mutex`基本互斥和同步工具的基礎上，讓鎖支持超時。互斥量可以用來保護數據，互斥量上鎖必須要調用lok(),try_lock_for(),或try_lock_until()。當有一個線程獲取已經獲取了鎖，那麼其他線程想要在獲取鎖的時候，會在嘗試或取鎖的時候失敗(調用try_lock())或阻塞(調用lock())，或直到想要獲取鎖可以獲取，亦或想要獲取的鎖超時(調用try_lock_for()或try_lock_until())。在線程調用unlock()對鎖進行釋放，其他線程才能獲取這個鎖被獲取(不管是調用的哪個函數)。

`std::timed_mutex`符合TimedLockable的需求。

**類型定義**

```
class timed_mutex
{
public:
  timed_mutex(timed_mutex const&)=delete;
  timed_mutex& operator=(timed_mutex const&)=delete;

  timed_mutex();
  ~timed_mutex();

  void lock();
  void unlock();
  bool try_lock();

  template<typename Rep,typename Period>
  bool try_lock_for(
      std::chrono::duration<Rep,Period> const& relative_time);

  template<typename Clock,typename Duration>
  bool try_lock_until(
      std::chrono::time_point<Clock,Duration> const& absolute_time);
};
```

### std::timed_mutex 默認構造函數

構造一個`std::timed_mutex`對象。

**聲明**

```
timed_mutex();
```

**效果**<br>
構造一個`std::timed_mutex`實例。

**後置條件**<br>
新構造一個未上鎖的`std::timed_mutex`對象。

**拋出**<br>
當無法創建出新的`std::timed_mutex`實例時，拋出`std::system_error`類型異常。

### std::timed_mutex 析構函數

銷燬一個`std::timed_mutex`對象。

**聲明**

```
~timed_mutex();
```

**先決條件**<br>
*this必須沒有上鎖。

**效果**<br>
銷燬*this。

**拋出**<br>
無

### std::timed_mutex::lock 成員函數

為當前線程獲取`std::timed_mutex`上的鎖。

**聲明**

```
void lock();
```

**先決條件**<br>
調用線程不能已經持有*this上的鎖。

**效果**<br>
阻塞當前線程，直到獲取到*this上的鎖。

**後置條件**<br>
*this被調用線程鎖住。

**拋出**<br>
當有錯誤產生，拋出`std::system_error`類型異常。

### std::timed_mutex::try_lock 成員函數

嘗試獲取為當前線程獲取`std::timed_mutex`上的鎖。

**聲明**

```
bool try_lock();
```

**先決條件**<br>
調用線程不能已經持有*this上的鎖。

**效果**<br>
嘗試獲取*this上的鎖，當獲取失敗時，不阻塞調用線程。

**返回**<br>
當鎖被調用線程獲取，返回true；反之，返回false。

**後置條件**<br>
當函數返回為true，*this則被當前線程鎖住。

**拋出**<br>
無

**NOTE** 即使沒有線程已獲取*this上的鎖，函數還是有可能獲取不到鎖(並返回false)。

### std::timed_mutex::try_lock_for 成員函數

嘗試獲取為當前線程獲取`std::timed_mutex`上的鎖。

**聲明**

```
template<typename Rep,typename Period>
bool try_lock_for(
    std::chrono::duration<Rep,Period> const& relative_time);
```

**先決條件**<br>
調用線程不能已經持有*this上的鎖。

**效果**<br>
在指定的relative_time時間內，嘗試獲取*this上的鎖。當relative_time.count()為0或負數，將會立即返回，就像調用try_lock()一樣。否則，將會阻塞，直到獲取鎖或超過給定的relative_time的時間。

**返回**<br>
當鎖被調用線程獲取，返回true；反之，返回false。

**後置條件**<br>
當函數返回為true，*this則被當前線程鎖住。

**拋出**<br>
無

**NOTE** 即使沒有線程已獲取*this上的鎖，函數還是有可能獲取不到鎖(並返回false)。線程阻塞的時長可能會長於給定的時間。逝去的時間可能是由一個穩定時鐘所決定。

### std::timed_mutex::try_lock_until 成員函數

嘗試獲取為當前線程獲取`std::timed_mutex`上的鎖。

**聲明**

```
template<typename Clock,typename Duration>
bool try_lock_until(
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**先決條件**<br>
調用線程不能已經持有*this上的鎖。

**效果**<br>
在指定的absolute_time時間內，嘗試獲取*this上的鎖。當`absolute_time<=Clock::now()`時，將會立即返回，就像調用try_lock()一樣。否則，將會阻塞，直到獲取鎖或Clock::now()返回的時間等於或超過給定的absolute_time的時間。

**返回**<br>
當鎖被調用線程獲取，返回true；反之，返回false。

**後置條件**<br>
當函數返回為true，*this則被當前線程鎖住。

**拋出**<br>
無

**NOTE** 即使沒有線程已獲取*this上的鎖，函數還是有可能獲取不到鎖(並返回false)。這裡不保證調用函數要阻塞多久，只有在函數返回false後，在Clock::now()返回的時間大於或等於absolute_time時，線程才會接觸阻塞。

### std::timed_mutex::unlock 成員函數

將當前線程持有`std::timed_mutex`對象上的鎖進行釋放。

**聲明**

```
void unlock();
```

**先決條件**<br>
調用線程已經持有*this上的鎖。

**效果**<br>
當前線程釋放`*this`上的鎖。任一阻塞等待獲取`*this`上的線程，將被解除阻塞。

**後置條件**<br>
*this未被調用線程上鎖。

**拋出**<br>
無

## D.5.4 std::recursive_timed_mutex類

`std::recursive_timed_mutex`類型在`std::recursive_mutex`提供的互斥和同步工具的基礎上，讓鎖支持超時。互斥量可以用來保護數據，互斥量上鎖必須要調用lok(),try_lock_for(),或try_lock_until()。當有一個線程獲取已經獲取了鎖，那麼其他線程想要在獲取鎖的時候，會在嘗試或取鎖的時候失敗(調用try_lock())或阻塞(調用lock())，或直到想要獲取鎖可以獲取，亦或想要獲取的鎖超時(調用try_lock_for()或try_lock_until())。在線程調用unlock()對鎖進行釋放，其他線程才能獲取這個鎖被獲取(不管是調用的哪個函數)。

該互斥量是可遞歸的，所以獲取`std::recursive_timed_mutex`鎖的線程，可以多次的對該實例上的鎖獲取。所有的鎖將會在調用相關unlock()操作後，可由其他線程獲取該實例上的鎖。

`std::recursive_timed_mutex`符合TimedLockable的需求。

**類型定義**

```
class recursive_timed_mutex
{
public:
  recursive_timed_mutex(recursive_timed_mutex const&)=delete;
  recursive_timed_mutex& operator=(recursive_timed_mutex const&)=delete;

  recursive_timed_mutex();
  ~recursive_timed_mutex();

  void lock();
  void unlock();
  bool try_lock() noexcept;

  template<typename Rep,typename Period>
  bool try_lock_for(
      std::chrono::duration<Rep,Period> const& relative_time);

  template<typename Clock,typename Duration>
  bool try_lock_until(
      std::chrono::time_point<Clock,Duration> const& absolute_time);
};
```

### std::recursive_timed_mutex 默認構造函數

構造一個`std::recursive_timed_mutex`對象。

**聲明**

```
recursive_timed_mutex();
```

**效果**<br>
構造一個`std::recursive_timed_mutex`實例。

**後置條件**<br>
新構造的`std::recursive_timed_mutex`實例是沒有上鎖的。

**拋出**<br>
當無法創建一個`std::recursive_timed_mutex`實例時，拋出`std::system_error`類異常。

### std::recursive_timed_mutex 析構函數

析構一個`std::recursive_timed_mutex`對象。

**聲明**

```
~recursive_timed_mutex();
```

**先決條件**<br>
*this不能上鎖。

**效果**<br>
銷燬*this。

**拋出**<br>
無

### std::recursive_timed_mutex::lock 成員函數

為當前線程獲取`std::recursive_timed_mutex`對象上的鎖。

**聲明**

```
void lock();
```

**先決條件**<br>
*this上的鎖不能被線程調用。

**效果**<br>
阻塞當前線程，直到獲取*this上的鎖。

**後置條件**<br>
`*this`被調用線程鎖住。當調用線程已經獲取`*this`上的鎖，那麼鎖的計數會再增加1。

**拋出**<br>
當錯誤出現時，拋出`std::system_error`類型異常。

### std::recursive_timed_mutex::try_lock 成員函數

嘗試為當前線程獲取`std::recursive_timed_mutex`對象上的鎖。

**聲明**

```
bool try_lock() noexcept;
```

**效果**<br>
嘗試獲取*this上的鎖，當獲取失敗時，直接不阻塞線程。

**返回**<br>
當調用線程獲取了鎖，返回true，否則返回false。

**後置條件**<br>
當函數返回true，`*this`會被調用線程鎖住。

**拋出**<br>
無

**NOTE** 該函數在獲取鎖時，當函數返回true時，`*this`上對鎖的計數會加一。如果當前線程還未獲取`*this`上的鎖，那麼該函數在獲取鎖時，可能失敗(並返回false)，即使沒有其他線程持有`*this`上的鎖。

### std::recursive_timed_mutex::try_lock_for 成員函數

嘗試為當前線程獲取`std::recursive_timed_mutex`對象上的鎖。

**聲明**

```
template<typename Rep,typename Period>
bool try_lock_for(
    std::chrono::duration<Rep,Period> const& relative_time);
```

**效果**<br>
在指定時間relative_time內，嘗試為調用線程獲取*this上的鎖。當relative_time.count()為0或負數時，將會立即返回，就像調用try_lock()一樣。否則，調用會阻塞，直到獲取相應的鎖，或超出了relative_time時限時，調用線程解除阻塞。

**返回**<br>
當調用線程獲取了鎖，返回true，否則返回false。

**後置條件**<br>
當函數返回true，`*this`會被調用線程鎖住。

**拋出**<br>
無

**NOTE** 該函數在獲取鎖時，當函數返回true時，`*this`上對鎖的計數會加一。如果當前線程還未獲取`*this`上的鎖，那麼該函數在獲取鎖時，可能失敗(並返回false)，即使沒有其他線程持有`*this`上的鎖。等待時間可能要比指定的時間長很多。逝去的時間可能由一個穩定時鐘來計算。

### std::recursive_timed_mutex::try_lock_until 成員函數

嘗試為當前線程獲取`std::recursive_timed_mutex`對象上的鎖。

**聲明**

```
template<typename Clock,typename Duration>
bool try_lock_until(
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**效果**<br>
在指定時間absolute_time內，嘗試為調用線程獲取*this上的鎖。當absolute_time<=Clock::now()時，將會立即返回，就像調用try_lock()一樣。否則，調用會阻塞，直到獲取相應的鎖，或Clock::now()返回的時間大於或等於absolute_time時，調用線程解除阻塞。

**返回**<br>
當調用線程獲取了鎖，返回true，否則返回false。

**後置條件**<br>
當函數返回true，`*this`會被調用線程鎖住。

**拋出**<br>
無

**NOTE** 該函數在獲取鎖時，當函數返回true時，`*this`上對鎖的計數會加一。如果當前線程還未獲取`*this`上的鎖，那麼該函數在獲取鎖時，可能失敗(並返回false)，即使沒有其他線程持有`*this`上的鎖。這裡阻塞的時間並不確定，只有當函數返回false，然後Clock::now()返回的時間大於或等於absolute_time時，調用線程將會解除阻塞。

### std::recursive_timed_mutex::unlock 成員函數

釋放當前線程獲取到的`std::recursive_timed_mutex`上的鎖。

**聲明**

```
void unlock();
```

**效果**<br>
當前線程釋放`*this`上的鎖。當`*this`上最後一個鎖被釋放後，任何等待獲取`*this`上的鎖將會解除阻塞，不過只能解除其中一個線程的阻塞。

**後置條件**<br>
調用線程*this上鎖的計數減一。

**拋出**<br>
無

## D.5.5 std::lock_guard類型模板

`std::lock_guard`類型模板為基礎鎖包裝所有權。所要上鎖的互斥量類型，由模板參數Mutex來決定，並且必須符合Lockable的需求。指定的互斥量在構造函數中上鎖，在析構函數中解鎖。這就為互斥量鎖部分代碼提供了一個簡單的方式；當程序運行完成時，阻塞解除，互斥量解鎖(無論是執行到最後，還是通過控制流語句break或return，亦或是拋出異常)。

`std::lock_guard`是不可MoveConstructible(移動構造), CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)。

**類型定義**

```
template <class Mutex>
class lock_guard
{
public:
  typedef Mutex mutex_type;

  explicit lock_guard(mutex_type& m);
  lock_guard(mutex_type& m, adopt_lock_t);
  ~lock_guard();

  lock_guard(lock_guard const& ) = delete;
  lock_guard& operator=(lock_guard const& ) = delete;
};
```

### std::lock_guard 自動上鎖的構造函數

使用互斥量構造一個`std::lock_guard`實例。

**聲明**

```
explicit lock_guard(mutex_type& m);
```

**效果**<br>
通過引用提供的互斥量，構造一個新的`std::lock_guard`實例，並調用m.lock()。

**拋出**<br>
m.lock()拋出的任何異常。

**後置條件**<br>
*this擁有m上的鎖。

### std::lock_guard 獲取鎖的構造函數

使用已提供互斥量上的鎖，構造一個`std::lock_guard`實例。

**聲明**

```
lock_guard(mutex_type& m,std::adopt_lock_t);
```

**先決條件**<br>
調用線程必須擁有m上的鎖。

**效果**<br>
調用線程通過引用提供的互斥量，以及獲取m上鎖的所有權，來構造一個新的`std::lock_guard`實例。

**拋出**<br>
無

**後置條件**<br>
*this擁有m上的鎖。

### std::lock_guard 析構函數

銷燬一個`std::lock_guard`實例，並且解鎖相關互斥量。

**聲明**

```
~lock_guard();
```

**效果**<br>
當*this被創建後，調用m.unlock()。

**拋出**<br>
無

## D.5.6 std::unique_lock類型模板

`std::unique_lock`類型模板相較`std::loc_guard`提供了更通用的所有權包裝器。上鎖的互斥量可由模板參數Mutex提供，這個類型必須滿足BasicLockable的需求。雖然，通常情況下，制定的互斥量會在構造的時候上鎖，析構的時候解鎖，但是附加的構造函數和成員函數提供靈活的功能。互斥量上鎖，意味著對操作同一段代碼的線程進行阻塞；當互斥量解鎖，就意味著阻塞解除(不論是裕興到最後，還是使用控制語句break和return，亦或是拋出異常)。`std::condition_variable`的鄧丹函數是需要`std::unique_lock<std::mutex>`實例的，並且所有`std::unique_lock`實例都適用於`std::conditin_variable_any`等待函數的Lockable參數。

當提供的Mutex類型符合Lockable的需求，那麼`std::unique_lock<Mutex>`也是符合Lockable的需求。此外，如果提供的Mutex類型符合TimedLockable的需求，那麼`std::unique_lock<Mutex>`也符合TimedLockable的需求。

`std::unique_lock`實例是MoveConstructible(移動構造)和MoveAssignable(移動賦值)，但是不能CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)。

**類型定義**

```
template <class Mutex>
class unique_lock
{
public:
  typedef Mutex mutex_type;

  unique_lock() noexcept;
  explicit unique_lock(mutex_type& m);
  unique_lock(mutex_type& m, adopt_lock_t);
  unique_lock(mutex_type& m, defer_lock_t) noexcept;
  unique_lock(mutex_type& m, try_to_lock_t);

  template<typename Clock,typename Duration>
  unique_lock(
      mutex_type& m,
      std::chrono::time_point<Clock,Duration> const& absolute_time);

  template<typename Rep,typename Period>
      unique_lock(
      mutex_type& m,
      std::chrono::duration<Rep,Period> const& relative_time);

  ~unique_lock();

  unique_lock(unique_lock const& ) = delete;
  unique_lock& operator=(unique_lock const& ) = delete;

  unique_lock(unique_lock&& );
  unique_lock& operator=(unique_lock&& );

  void swap(unique_lock& other) noexcept;

  void lock();
  bool try_lock();
  template<typename Rep, typename Period>
  bool try_lock_for(
      std::chrono::duration<Rep,Period> const& relative_time);
  template<typename Clock, typename Duration>
  bool try_lock_until(
      std::chrono::time_point<Clock,Duration> const& absolute_time);
  void unlock();

  explicit operator bool() const noexcept;
  bool owns_lock() const noexcept;
  Mutex* mutex() const noexcept;
  Mutex* release() noexcept;
};
```

### std::unique_lock 默認構造函數

不使用相關互斥量，構造一個`std::unique_lock`實例。

**聲明**

```
unique_lock() noexcept;
```

**效果**<br>
構造一個`std::unique_lock`實例，這個新構造的實例沒有相關互斥量。

**後置條件**<br>
this->mutex()==NULL, this->owns_lock()==false.

### std::unique_lock 自動上鎖的構造函數

使用相關互斥量，構造一個`std::unique_lock`實例。

**聲明**

```
explicit unique_lock(mutex_type& m);
```

**效果**<br>
通過提供的互斥量，構造一個`std::unique_lock`實例，且調用m.lock()。

**拋出**<br>
m.lock()拋出的任何異常。

**後置條件**<br>
this->owns_lock()==true, this->mutex()==&m.

### std::unique_lock 獲取鎖的構造函數

使用相關互斥量和持有的鎖，構造一個`std::unique_lock`實例。

**聲明**

```
unique_lock(mutex_type& m,std::adopt_lock_t);
```

**先決條件**<br>
調用線程必須持有m上的鎖。

**效果**<br>
通過提供的互斥量和已經擁有m上的鎖，構造一個`std::unique_lock`實例。

**拋出**<br>
無

**後置條件**<br>
this->owns_lock()==true, this->mutex()==&m.

### std::unique_lock 遞延鎖的構造函數

使用相關互斥量和非持有的鎖，構造一個`std::unique_lock`實例。

**聲明**

```
unique_lock(mutex_type& m,std::defer_lock_t) noexcept;
```

**效果**<br>
構造的`std::unique_lock`實例引用了提供的互斥量。

**拋出**<br>
無

**後置條件**<br>
this->owns_lock()==false, this->mutex()==&m.

### std::unique_lock 嘗試獲取鎖的構造函數

使用提供的互斥量，並嘗試從互斥量上獲取鎖，從而構造一個`std::unique_lock`實例。

**聲明**

```
unique_lock(mutex_type& m,std::try_to_lock_t);
```

**先決條件**<br>
使`std::unique_lock`實例化的Mutex類型，必須符合Loackable的需求。

**效果**<br>
構造的`std::unique_lock`實例引用了提供的互斥量，且調用m.try_lock()。

**拋出**<br>
無

**後置條件**<br>
this->owns_lock()將返回m.try_lock()的結果，且this->mutex()==&m。

### std::unique_lock 在給定時長內嘗試獲取鎖的構造函數

使用提供的互斥量，並嘗試從互斥量上獲取鎖，從而構造一個`std::unique_lock`實例。

**聲明**

```
template<typename Rep,typename Period>
unique_lock(
    mutex_type& m,
    std::chrono::duration<Rep,Period> const& relative_time);
```

**先決條件**<br>
使`std::unique_lock`實例化的Mutex類型，必須符合TimedLockable的需求。

**效果**<br>
構造的`std::unique_lock`實例引用了提供的互斥量，且調用m.try_lock_for(relative_time)。

**拋出**<br>
無

**後置條件**<br>
this->owns_lock()將返回m.try_lock_for()的結果，且this->mutex()==&m。

### std::unique_lock 在給定時間點內嘗試獲取鎖的構造函數

使用提供的互斥量，並嘗試從互斥量上獲取鎖，從而構造一個`std::unique_lock`實例。

**聲明**

```
template<typename Clock,typename Duration>
unique_lock(
    mutex_type& m,
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**先決條件**<br>
使`std::unique_lock`實例化的Mutex類型，必須符合TimedLockable的需求。

**效果**<br>
構造的`std::unique_lock`實例引用了提供的互斥量，且調用m.try_lock_until(absolute_time)。

**拋出**<br>
無

**後置條件**<br>
this->owns_lock()將返回m.try_lock_until()的結果，且this->mutex()==&m。

### std::unique_lock 移動構造函數

將一個已經構造`std::unique_lock`實例的所有權，轉移到新的`std::unique_lock`實例上去。

**聲明**

```
unique_lock(unique_lock&& other) noexcept;
```

**先決條件**<br>
使`std::unique_lock`實例化的Mutex類型，必須符合TimedLockable的需求。

**效果**<br>
構造的`std::unique_lock`實例。當other在函數調用的時候擁有互斥量上的鎖，那麼該鎖的所有權將被轉移到新構建的`std::unique_lock`對象當中去。

**後置條件**<br>
對於新構建的`std::unique_lock`對象x，x.mutex等價與在構造函數調用前的other.mutex()，並且x.owns_lock()等價於函數調用前的other.owns_lock()。在調用函數後，other.mutex()==NULL，other.owns_lock()=false。

**拋出**<br>
無

**NOTE** `std::unique_lock`對象是不可CopyConstructible(拷貝構造)，所以這裡沒有拷貝構造函數，只有移動構造函數。

### std::unique_lock 移動賦值操作

將一個已經構造`std::unique_lock`實例的所有權，轉移到新的`std::unique_lock`實例上去。

**聲明**

```
unique_lock& operator=(unique_lock&& other) noexcept;
```

**效果**<br>
當this->owns_lock()返回true時，調用this->unlock()。如果other擁有mutex上的鎖，那麼這個所將歸*this所有。

**後置條件**<br>
this->mutex()等於在為進行賦值前的other.mutex()，並且this->owns_lock()的值與進行賦值操作前的other.owns_lock()相等。other.mutex()==NULL, other.owns_lock()==false。

**拋出**<br>
無

**NOTE** `std::unique_lock`對象是不可CopyAssignable(拷貝賦值)，所以這裡沒有拷貝賦值函數，只有移動賦值函數。

### std::unique_lock 析構函數

銷燬一個`std::unique_lock`實例，如果該實例擁有鎖，那麼會將相關互斥量進行解鎖。

**聲明**

```
~unique_lock();
```

**效果**<br>
當this->owns_lock()返回true時，調用this->mutex()->unlock()。

**拋出**<br>
無

### std::unique_lock::swap 成員函數

交換`std::unique_lock`實例中相關的所有權。

**聲明**

```
void swap(unique_lock& other) noexcept;
```

**效果**<br>
如果other在調用該函數前擁有互斥量上的鎖，那麼這個鎖將歸`*this`所有。如果`*this`在調用哎函數前擁有互斥量上的鎖，那麼這個鎖將歸other所有。

**拋出**<br>
無

### std::unique_lock 上非成員函數swap

交換`std::unique_lock`實例中相關的所有權。

**聲明**

```
void swap(unique_lock& lhs,unique_lock& rhs) noexcept;
```

**效果**<br>
lhs.swap(rhs)

**拋出**<br>
無

### std::unique_lock::lock 成員函數

獲取與*this相關互斥量上的鎖。

**聲明**

```
void lock();
```

**先決條件**<br>
this->mutex()!=NULL, this->owns_lock()==false.

**效果**<br>
調用this->mutex()->lock()。

**拋出**<br>
拋出任何this->mutex()->lock()所拋出的異常。當this->mutex()==NULL，拋出`std::sytem_error`類型異常，錯誤碼為`std::errc::operation_not_permitted`。當this->owns_lock()==true時，拋出`std::system_error`，錯誤碼為`std::errc::resource_deadlock_would_occur`。

**後置條件**<br>
this->owns_lock()==true。

### std::unique_lock::try_lock 成員函數

嘗試獲取與*this相關互斥量上的鎖。

**聲明**

```
bool try_lock();
```

**先決條件**<br>
`std::unique_lock`實例化說是用的Mutex類型，必須滿足Lockable需求。this->mutex()!=NULL, this->owns_lock()==false。

**效果**<br>
調用this->mutex()->try_lock()。

**拋出**<br>
拋出任何this->mutex()->try_lock()所拋出的異常。當this->mutex()==NULL，拋出`std::sytem_error`類型異常，錯誤碼為`std::errc::operation_not_permitted`。當this->owns_lock()==true時，拋出`std::system_error`，錯誤碼為`std::errc::resource_deadlock_would_occur`。

**後置條件**<br>
當函數返回true時，this->ows_lock()==true，否則this->owns_lock()==false。

### std::unique_lock::unlock 成員函數

釋放與*this相關互斥量上的鎖。

**聲明**

```
void unlock();
```

**先決條件**<br>
this->mutex()!=NULL, this->owns_lock()==true。

**拋出**<br>
拋出任何this->mutex()->unlock()所拋出的異常。當this->owns_lock()==false時，拋出`std::system_error`，錯誤碼為`std::errc::operation_not_permitted`。

**後置條件**<br>
this->owns_lock()==false。

### std::unique_lock::try_lock_for 成員函數

在指定時間內嘗試獲取與*this相關互斥量上的鎖。

**聲明**

```
template<typename Rep, typename Period>
bool try_lock_for(
    std::chrono::duration<Rep,Period> const& relative_time);
```

**先決條件**<br>
`std::unique_lock`實例化說是用的Mutex類型，必須滿足TimedLockable需求。this->mutex()!=NULL, this->owns_lock()==false。

**效果**<br>
調用this->mutex()->try_lock_for(relative_time)。

**返回**<br>
當this->mutex()->try_lock_for()返回true，返回true，否則返回false。

**拋出**<br>
拋出任何this->mutex()->try_lock_for()所拋出的異常。當this->mutex()==NULL，拋出`std::sytem_error`類型異常，錯誤碼為`std::errc::operation_not_permitted`。當this->owns_lock()==true時，拋出`std::system_error`，錯誤碼為`std::errc::resource_deadlock_would_occur`。

**後置條件**<br>
當函數返回true時，this->ows_lock()==true，否則this->owns_lock()==false。

### std::unique_lock::try_lock_until 成員函數

在指定時間點嘗試獲取與*this相關互斥量上的鎖。

**聲明**

```
template<typename Clock, typename Duration>
bool try_lock_until(
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**先決條件**<br>
`std::unique_lock`實例化說是用的Mutex類型，必須滿足TimedLockable需求。this->mutex()!=NULL, this->owns_lock()==false。

**效果**<br>
調用this->mutex()->try_lock_until(absolute_time)。

**返回**<br>
當this->mutex()->try_lock_for()返回true，返回true，否則返回false。

**拋出**<br>
拋出任何this->mutex()->try_lock_for()所拋出的異常。當this->mutex()==NULL，拋出`std::sytem_error`類型異常，錯誤碼為`std::errc::operation_not_permitted`。當this->owns_lock()==true時，拋出`std::system_error`，錯誤碼為`std::errc::resource_deadlock_would_occur`。

**後置條件**<br>
當函數返回true時，this->ows_lock()==true，否則this->owns_lock()==false。

### std::unique_lock::operator bool成員函數

檢查*this是否擁有一個互斥量上的鎖。

**聲明**

```
explicit operator bool() const noexcept;
```

**返回**<br>
this->owns_lock()

**拋出**<br>
無

**NOTE** 這是一個explicit轉換操作，所以當這樣的操作在上下文中只能被隱式的調用，所返回的結果需要被當做一個布爾量進行使用，而非僅僅作為整型數0或1。

### std::unique_lock::owns_lock 成員函數

檢查*this是否擁有一個互斥量上的鎖。

**聲明**

```
bool owns_lock() const noexcept;
```

**返回**<br>
當*this持有一個互斥量的鎖，返回true；否則，返回false。

**拋出**<br>
無

### std::unique_lock::mutex 成員函數

當*this具有相關互斥量時，返回這個互斥量

**聲明**

```
mutex_type* mutex() const noexcept;
```

**返回**<br>
當*this有相關互斥量，則返回該互斥量；否則，返回NULL。

**拋出**<br>
無

### std::unique_lock::release 成員函數

當*this具有相關互斥量時，返回這個互斥量，並將這個互斥量進行釋放。

**聲明**

```
mutex_type* release() noexcept;
```

**效果**<br>
將*this與相關的互斥量之間的關係解除，同時解除所有持有鎖的所有權。

**返回**<br>
返回與*this相關的互斥量指針，如果沒有相關的互斥量，則返回NULL。

**後置條件**<br>
this->mutex()==NULL, this->owns_lock()==false。

**拋出**<br>
無

**NOTE** 如果this->owns_lock()在調用該函數前返回true，那麼調用者則有責任裡解除互斥量上的鎖。

## D.5.7 std::lock函數模板

`std::lock`函數模板提供同時鎖住多個互斥量的功能，且不會有因改變鎖的一致性而導致的死鎖。

**聲明**

```
template<typename LockableType1,typename... LockableType2>
void lock(LockableType1& m1,LockableType2& m2...);
```

**先決條件**<br>
提供的可鎖對象LockableType1, LockableType2...，需要滿足Lockable的需求。

**效果**<br>
使用未指定順序調用lock(),try_lock()獲取每個可鎖對象(m1, m2...)上的鎖，還有unlock()成員來避免這個類型陷入死鎖。

**後置條件**<br>
當前線程擁有提供的所有可鎖對象上的鎖。

**拋出**<br>
任何lock(), try_lock()和unlock()拋出的異常。

**NOTE** 如果一個異常由`std::lock`所傳播開來，當可鎖對象上有鎖被lock()或try_lock()獲取，那麼unlock()會使用在這些可鎖對象上。

## D.5.8 std::try_lock函數模板

`std::try_lock`函數模板允許嘗試獲取一組可鎖對象上的鎖，所以要不全部獲取，要不一個都不獲取。

**聲明**

```
template<typename LockableType1,typename... LockableType2>
int try_lock(LockableType1& m1,LockableType2& m2...);
```

**先決條件**<br>
提供的可鎖對象LockableType1, LockableType2...，需要滿足Lockable的需求。

**效果**<br>
使用try_lock()嘗試從提供的可鎖對象m1,m2...上逐個獲取鎖。當鎖在之前獲取過，但被當前線程使用unlock()對相關可鎖對象進行了釋放後，try_lock()會返回false或拋出一個異常。

**返回**<br>
當所有鎖都已獲取(每個互斥量調用try_lock()返回true)，則返回-1，否則返回以0為基數的數字，其值為調用try_lock()返回false的個數。

**後置條件**<br>
當函數返回-1，當前線程獲取從每個可鎖對象上都獲取一個鎖。否則，通過該調用獲取的任何鎖都將被釋放。

**拋出**<br>
try_lock()拋出的任何異常。

**NOTE** 如果一個異常由`std::try_lock`所傳播開來，則通過try_lock()獲取鎖對象，將會調用unlock()解除對鎖的持有。

## D.5.9 std::once_flag類

`std::once_flag`和`std::call_once`一起使用，為了保證某特定函數只執行一次(即使有多個線程在併發的調用該函數)。

`std::once_flag`實例是不能CopyConstructible(拷貝構造)，CopyAssignable(拷貝賦值)，MoveConstructible(移動構造)，以及MoveAssignable(移動賦值)。

**類型定義**

```
struct once_flag
{
  constexpr once_flag() noexcept;

  once_flag(once_flag const& ) = delete;
  once_flag& operator=(once_flag const& ) = delete;
};
```

### std::once_flag 默認構造函數

`std::once_flag`默認構造函數創建了一個新的`std::once_flag`實例(幷包含一個狀態，這個狀態表示相關函數沒有被調用)。

**聲明**

```
constexpr once_flag() noexcept;
```

**效果**<br>
`std::once_flag`默認構造函數創建了一個新的`std::once_flag`實例(幷包含一個狀態，這個狀態表示相關函數沒有被調用)。因為這是一個constexpr構造函數，在構造的靜態初始部分，實例是靜態存儲的，這樣就避免了條件競爭和初始化順序的問題。

## D.5.10 std::call_once函數模板

`std::call_once`和`std::once_flag`一起使用，為了保證某特定函數只執行一次(即使有多個線程在併發的調用該函數)。

**聲明**

```
template<typename Callable,typename... Args>
void call_once(std::once_flag& flag,Callable func,Args args...);
```

**先決條件**<br>
表達式`INVOKE(func,args)`提供的func和args必須是合法的。Callable和每個Args的成員都是可MoveConstructible(移動構造)。

**效果**<br>
在同一個`std::once_flag`對象上調用`std::call_once`是串行的。如果之前沒有在同一個`std::once_flag`對象上調用過`std::call_once`，參數func(或副本)被調用，就像INVOKE(func, args),並且只有可調用的func不拋出任何異常時，調用`std::call_once`才是有效的。當有異常拋出，異常會被調用函數進行傳播。如果之前在`std::once_flag`上的`std::call_once`是有效的，那麼再次調用`std::call_once`將不會在調用func。

**同步**<br>
在`std::once_flag`上完成對`std::call_once`的調用的先決條件是，後續所有對`std::call_once`調用都在同一`std::once_flag`對象。

**拋出**<br>
當效果沒有達到，或任何異常由調用func而傳播，則拋出`std::system_error`。