# D.7 &lt;thread&gt;頭文件

`<thread>`頭文件提供了管理和辨別線程的工具，並且提供函數，可讓當前線程休眠。

**頭文件內容**

```
namespace std
{
  class thread;

  namespace this_thread
  {
    thread::id get_id() noexcept;

    void yield() noexcept;

    template<typename Rep,typename Period>
    void sleep_for(
        std::chrono::duration<Rep,Period> sleep_duration);

    template<typename Clock,typename Duration>
    void sleep_until(
        std::chrono::time_point<Clock,Duration> wake_time);
  }
}
```

## D.7.1 std::thread類

`std::thread`用來管理線程的執行。其提供讓新的線程執行或執行，也提供對線程的識別，以及提供其他函數用於管理線程的執行。

```
class thread
{
public:
  // Types
  class id;
  typedef implementation-defined native_handle_type; // optional

  // Construction and Destruction
  thread() noexcept;
  ~thread();

  template<typename Callable,typename Args...>
  explicit thread(Callable&& func,Args&&... args);

  // Copying and Moving
  thread(thread const& other) = delete;
  thread(thread&& other) noexcept;

  thread& operator=(thread const& other) = delete;
  thread& operator=(thread&& other) noexcept;

  void swap(thread& other) noexcept;

  void join();
  void detach();
  bool joinable() const noexcept;

  id get_id() const noexcept;
  native_handle_type native_handle();
  static unsigned hardware_concurrency() noexcept;
};

void swap(thread& lhs,thread& rhs);
```

### std::thread::id 類

可以通過`std::thread::id`實例對執行線程進行識別。

**類型定義**

```
class thread::id
{
public:
  id() noexcept;
};

bool operator==(thread::id x, thread::id y) noexcept;
bool operator!=(thread::id x, thread::id y) noexcept;
bool operator<(thread::id x, thread::id y) noexcept;
bool operator<=(thread::id x, thread::id y) noexcept;
bool operator>(thread::id x, thread::id y) noexcept;
bool operator>=(thread::id x, thread::id y) noexcept;

template<typename charT, typename traits>
basic_ostream<charT, traits>&
operator<< (basic_ostream<charT, traits>&& out, thread::id id);
```

**Notes**
`std::thread::id`的值可以識別不同的執行，每個`std::thread::id`默認構造出來的值都不一樣，不同值代表不同的執行線程。

`std::thread::id`的值是不可預測的，在同一程序中的不同線程的id也不同。

`std::thread::id`是可以CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)，所以對於`std::thread::id`的拷貝和賦值是沒有限制的。

#### std::thread::id 默認構造函數

構造一個`std::thread::id`對象，其不能表示任何執行線程。

**聲明**

```
id() noexcept;
```

**效果**
構造一個`std::thread::id`實例，不能表示任何一個線程值。

**拋出**
無

**NOTE** 所有默認構造的`std::thread::id`實例存儲的同一個值。

#### std::thread::id 相等比較操作

比較兩個`std::thread::id`的值，看是兩個執行線程是否相等。

**聲明**

```
bool operator==(std::thread::id lhs,std::thread::id rhs) noexcept;
```

**返回**
當lhs和rhs表示同一個執行線程或兩者不代表沒有任何線程，則返回true。當lsh和rhs表示不同執行線程或其中一個代表一個執行線程，另一個不代表任何線程，則返回false。

**拋出**
無

#### std::thread::id 不相等比較操作

比較兩個`std::thread::id`的值，看是兩個執行線程是否相等。

**聲明**

```
bool operator！=(std::thread::id lhs,std::thread::id rhs) noexcept;
```

**返回**
`!(lhs==rhs)`

**拋出**
無

#### std::thread::id 小於比較操作

比較兩個`std::thread::id`的值，看是兩個執行線程哪個先執行。

**聲明**

```
bool operator<(std::thread::id lhs,std::thread::id rhs) noexcept;
```

**返回**
當lhs比rhs的線程ID靠前，則返回true。當lhs!=rhs，且`lhs<rhs`或`rhs<lhs`返回true，其他情況則返回false。當lhs==rhs，在`lhs<rhs`和`rhs<lhs`時返回false。

**拋出**
無

**NOTE** 當默認構造的`std::thread::id`實例，在不代表任何線程的時候，其值小於任何一個代表執行線程的實例。當兩個實例相等，那麼兩個對象代表兩個執行線程。任何一組不同的`std::thread::id`的值，是由同一序列構造，這與程序執行的順序相同。同一個可執行程序可能有不同的執行順序。

#### std::thread::id 小於等於比較操作

比較兩個`std::thread::id`的值，看是兩個執行線程的ID值是否相等，或其中一個先行。

**聲明**

```
bool operator<(std::thread::id lhs,std::thread::id rhs) noexcept;
```

**返回**
`!(rhs<lhs)`

**拋出**
無

#### std::thread::id 大於比較操作

比較兩個`std::thread::id`的值，看是兩個執行線程的是後行的。

**聲明**

```
bool operator>(std::thread::id lhs,std::thread::id rhs) noexcept;
```

**返回**
`rhs<lhs`

**拋出**
無

#### std::thread::id 大於等於比較操作

比較兩個`std::thread::id`的值，看是兩個執行線程的ID值是否相等，或其中一個後行。

**聲明**

```
bool operator>=(std::thread::id lhs,std::thread::id rhs) noexcept;
```

**返回**
`!(lhs<rhs)`

**拋出**
無

#### std::thread::id 插入流操作

將`std::thread::id`的值通過給指定流寫入字符串。

**聲明**

```
template<typename charT, typename traits>
basic_ostream<charT, traits>&
operator<< (basic_ostream<charT, traits>&& out, thread::id id);
```

**效果**
將`std::thread::id`的值通過給指定流插入字符串。

**返回**
無

**NOTE** 字符串的格式並未給定。`std::thread::id`實例具有相同的表達式時，是相同的；當實例表達式不同，則代表不同的線程。

### std::thread::native_handler 成員函數

`native_handle_type`是由另一類型定義而來，這個類型會隨著指定平臺的API而變化。

**聲明**

```
typedef implementation-defined native_handle_type;
```

**NOTE** 這個類型定義是可選的。如果提供，實現將使用原生平臺指定的API，並提供合適的類型作為實現。

### std::thread 默認構造函數

返回一個`native_handle_type`類型的值，這個值可以可以表示*this相關的執行線程。

**聲明**

```
native_handle_type native_handle();
```

**NOTE** 這個函數是可選的。如果提供，會使用原生平臺指定的API，並返回合適的值。

### std::thread 構造函數

構造一個無相關線程的`std::thread`對象。

**聲明**

```
thread() noexcept;
```

**效果**
構造一個無相關線程的`std::thread`實例。

**後置條件**
對於一個新構造的`std::thread`對象x，x.get_id() == id()。

**拋出**
無

### std::thread 移動構造函數

將已存在`std::thread`對象的所有權，轉移到新創建的對象中。

**聲明**

```
thread(thread&& other) noexcept;
```

**效果**
構造一個`std::thread`實例。與other相關的執行線程的所有權，將轉移到新創建的`std::thread`對象上。否則，新創建的`std::thread`對象將無任何相關執行線程。

**後置條件**
對於一個新構建的`std::thread`對象x來說，x.get_id()等價於未轉移所有權時的other.get_id()。get_id()==id()。

**拋出**
無

**NOTE** `std::thread`對象是不可CopyConstructible(拷貝構造)，所以該類沒有拷貝構造函數，只有移動構造函數。

### std::thread 析構函數

銷燬`std::thread`對象。

**聲明**

```
~thread();
```

**效果**
銷燬`*this`。當`*this`與執行線程相關(this->joinable()將返回true)，調用`std::terminate()`來終止程序。

**拋出**
無

### std::thread 移動賦值操作

將一個`std::thread`的所有權，轉移到另一個`std::thread`對象上。

**聲明**

```
thread& operator=(thread&& other) noexcept;
```

**效果**
在調用該函數前，this->joinable返回true，則調用`std::terminate()`來終止程序。當other在執行賦值前，具有相關的執行線程，那麼執行線程現在就與`*this`相關聯。否則，`*this`無相關執行線程。

**後置條件**
this->get_id()的值等於調用該函數前的other.get_id()。oter.get_id()==id()。

**拋出**
無

**NOTE** `std::thread`對象是不可CopyAssignable(拷貝賦值)，所以該類沒有拷貝賦值函數，只有移動賦值函數。

### std::thread::swap 成員函數

將兩個`std::thread`對象的所有權進行交換。

**聲明**

```
void swap(thread& other) noexcept;
```

**效果**
當other在執行賦值前，具有相關的執行線程，那麼執行線程現在就與`*this`相關聯。否則，`*this`無相關執行線程。對於`*this`也是一樣。

**後置條件**
this->get_id()的值等於調用該函數前的other.get_id()。other.get_id()的值等於沒有調用函數前this->get_id()的值。

**拋出**
無

### std::thread的非成員函數swap

將兩個`std::thread`對象的所有權進行交換。

**聲明**

```
void swap(thread& lhs,thread& rhs) noexcept;
```

**效果**
lhs.swap(rhs)

**拋出**
無

### std::thread::joinable 成員函數

查詢*this是否具有相關執行線程。

**聲明**

```
bool joinable() const noexcept;
```

**返回**
如果*this具有相關執行線程，則返回true；否則，返回false。

**拋出**
無

### std::thread::join 成員函數

等待*this相關的執行線程結束。

**聲明**

```
void join();
```

**先決條件**
this->joinable()返回true。

**效果**
阻塞當前線程，直到與*this相關的執行線程執行結束。

**後置條件**
this->get_id()==id()。與*this先關的執行線程將在該函數調用後結束。

**同步**
想要在*this上成功的調用該函數，則需要依賴有joinable()的返回。

**拋出**
當效果沒有達到或this->joinable()返回false，則拋出`std::system_error`異常。

### std::thread::detach 成員函數

將*this上的相關線程進行分離。

**聲明**

```
void detach();
```

**先決條件**
this->joinable()返回true。

**效果**
將*this上的相關線程進行分離。

**後置條件**
this->get_id()==id(), this->joinable()==false

與*this相關的執行線程在調用該函數後就會分離，並且不在會與當前`std::thread`對象再相關。

**拋出**
當效果沒有達到或this->joinable()返回false，則拋出`std::system_error`異常。

### std::thread::get_id 成員函數

返回`std::thread::id`的值來表示*this上相關執行線程。

**聲明**

```
thread::id get_id() const noexcept;
```

**返回**
當*this具有相關執行線程，將返回`std::thread::id`作為識別當前函數的依據。否則，返回默認構造的`std::thread::id`。

**拋出**
無

### std::thread::hardware_concurrency 靜態成員函數

返回硬件上可以併發線程的數量。

**聲明**

```
unsigned hardware_concurrency() noexcept;
```

**返回**
硬件上可以併發線程的數量。這個值可能是系統處理器的數量。當信息不用或只有定義，則該函數返回0。

**拋出**
無

## D.7.2 this_thread命名空間

這裡介紹一下`std::this_thread`命名空間內提供的函數操作。

### this_thread::get_id 非成員函數

返回`std::thread::id`用來識別當前執行線程。

**聲明**

```
thread::id get_id() noexcept;
```

**返回**
可通過`std:thread::id`來識別當前線程。

**拋出**
無

### this_thread::yield 非成員函數

該函數用於通知庫，調用線程不需要立即運行。一般使用小循環來避免消耗過多CPU時間。

**聲明**

```
void yield() noexcept;
```

**效果**
使用標準庫的實現來安排線程的一些事情。

**拋出**
無

### this_thread::sleep_for 非成員函數

在指定的指定時長內，暫停執行當前線程。

**聲明**

```
template<typename Rep,typename Period>
void sleep_for(std::chrono::duration<Rep,Period> const& relative_time);
```

**效果**
在超出relative_time的時長內，阻塞當前線程。

**NOTE** 線程可能阻塞的時間要長於指定時長。如果可能，逝去的時間由將會由一個穩定時鐘決定。

**拋出**
無

### this_thread::sleep_until 非成員函數

暫停指定當前線程，直到到了指定的時間點。

**聲明**

```
template<typename Clock,typename Duration>
void sleep_until(
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**效果**
在到達absolute_time的時間點前，阻塞當前線程，這個時間點由指定的Clock決定。

**NOTE** 這裡不保證會阻塞多長時間，只有Clock::now()返回的時間等於或大於absolute_time時，阻塞的線程才能被解除阻塞。

**拋出**
無