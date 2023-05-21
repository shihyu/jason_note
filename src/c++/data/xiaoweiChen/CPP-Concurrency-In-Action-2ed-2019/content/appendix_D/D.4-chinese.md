# D.4 &lt;future&gt;頭文件

`<future>`頭文件提供處理異步結果(在其他線程上執行額結果)的工具。

**頭文件內容**

```
namespace std
{
  enum class future_status {
      ready, timeout, deferred };

  enum class future_errc
  {
    broken_promise,
    future_already_retrieved,
    promise_already_satisfied,
    no_state
  };

  class future_error;

  const error_category& future_category();

  error_code make_error_code(future_errc e);
  error_condition make_error_condition(future_errc e);

  template<typename ResultType>
  class future;

  template<typename ResultType>
  class shared_future;

  template<typename ResultType>
  class promise;

  template<typename FunctionSignature>
  class packaged_task; // no definition provided

  template<typename ResultType,typename ... Args>
  class packaged_task<ResultType (Args...)>;

  enum class launch {
    async, deferred
  };

  template<typename FunctionType,typename ... Args>
  future<result_of<FunctionType(Args...)>::type>
  async(FunctionType&& func,Args&& ... args);

  template<typename FunctionType,typename ... Args>
  future<result_of<FunctionType(Args...)>::type>
  async(std::launch policy,FunctionType&& func,Args&& ... args);
}
```

## D.4.1 std::future類型模板

`std::future`類型模板是為了等待其他線程上的異步結果。其和`std::promise`，`std::packaged_task`類型模板，還有`std::async`函數模板，都是為異步結果準備的工具。只有`std::future`實例可以在任意時間引用異步結果。

`std::future`實例是MoveConstructible(移動構造)和MoveAssignable(移動賦值)，不過不能CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)。

**類型聲明**

```
template<typename ResultType>
class future
{
public:
  future() noexcept;
  future(future&&) noexcept;
  future& operator=(future&&) noexcept;
  ~future();
  
  future(future const&) = delete;
  future& operator=(future const&) = delete;

  shared_future<ResultType> share();

  bool valid() const noexcept;
  
  see description get();
 
  void wait();

  template<typename Rep,typename Period>
  future_status wait_for(
      std::chrono::duration<Rep,Period> const& relative_time);

  template<typename Clock,typename Duration>
  future_status wait_until(
      std::chrono::time_point<Clock,Duration> const& absolute_time);
};
```

### std::future 默認構造函數

不使用異步結果構造一個`std::future`對象。

**聲明**

```
future() noexcept;
```

**效果**
構造一個新的`std::future`實例。

**後置條件**
valid()返回false。

**拋出**
無

### std::future 移動構造函數

使用另外一個對象，構造一個`std::future`對象，將相關異步結果的所有權轉移給新`std::future`對象。

**聲明**

```
future(future&& other) noexcept;
```

**效果**
使用已有對象構造一個新的`std::future`對象。

**後置條件**
已有對象中的異步結果，將於新的對象相關聯。然後，解除已有對象和異步之間的關係。`this->valid()`返回的結果與之前已有對象`other.valid()`返回的結果相同。在調用該構造函數後，`other.valid()`將返回false。

**拋出**
無

### std::future 移動賦值操作

將已有`std::future`對象中異步結果的所有權，轉移到另一對象當中。

**聲明**

```
future(future&& other) noexcept;
```

**效果**
在兩個`std::future`實例中轉移異步結果的狀態。

**後置條件**
當執行完賦值操作後，`*this.other`就與異步結果沒有關係了。異步狀態(如果有的話)在釋放後與`*this`相關，並且在最後一次引用後，銷燬該狀態。`this->valid()`返回的結果與之前已有對象`other.valid()`返回的結果相同。在調用該構造函數後，`other.valid()`將返回false。

**拋出**
無

### std::future 析構函數

銷燬一個`std::future`對象。

**聲明**

```
~future();
```

**效果**
銷燬`*this`。如果這是最後一次引用與`*this`相關的異步結果，之後就會將該異步結果銷燬。

**拋出**
無

### std::future::share 成員函數

構造一個新`std::shared_future`實例，並且將`*this`異步結果的所有權轉移到新的`std::shared_future`實例中。

**聲明**

```
shared_future<ResultType> share();
```

**效果**
如同 shared_future<ResultType>(std::move(*this))。

**後置條件**
當調用share()成員函數，與`*this`相關的異步結果將與新構造的`std::shared_future`實例相關。`this->valid()`將返回false。

**拋出**
無

### std::future::valid 成員函數

檢查`std::future`實例是否與一個異步結果相關聯。

**聲明**

```
bool valid() const noexcept;
```

**返回**
當與異步結果相關時，返回true，否則返回false。

**拋出**
無

### std::future::wait 成員函數

如果與`*this`相關的狀態包含延遲函數，將調用該函數。否則，會等待`std::future`實例中的異步結果準備就緒。

**聲明**

```
void wait();
```

**先決條件**
`this->valid()`將會返回true。

**效果**
當相關狀態包含延遲函數，調用延遲函數，並保存返回的結果，或將拋出的異常保存成為異步結果。否則，會阻塞到`*this`準備就緒。

**拋出**
無

### std::future::wait_for 成員函數

等待`std::future`實例上相關異步結果準備就緒，或超過某個給定的時間。

**聲明**

```
template<typename Rep,typename Period>
future_status wait_for(
    std::chrono::duration<Rep,Period> const& relative_time);
```

**先決條件**
`this->valid()`將會返回true。

**效果**
如果與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，那麼就不阻塞立即返回。否則將阻塞實例，直到與`*this`相關異步結果準備就緒，或超過給定的relative_time時長。

**返回**
當與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，返回`std::future_status::deferred`；當與`*this`相關的異步結果準備就緒，返回`std::future_status::ready`；當給定時間超過relative_time時，返回`std::future_status::timeout`。

**NOTE**:線程阻塞的時間可能超多給定的時長。時長儘可能由一個穩定的時鐘決定。

**拋出**
無

### std::future::wait_until 成員函數

等待`std::future`實例上相關異步結果準備就緒，或超過某個給定的時間。

**聲明**

```
template<typename Clock,typename Duration>
future_status wait_until(
  std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**先決條件**
this->valid()將返回true。

**效果**
如果與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，那麼就不阻塞立即返回。否則將阻塞實例，直到與`*this`相關異步結果準備就緒，或`Clock::now()`返回的時間大於等於absolute_time。

**返回**
當與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，返回`std::future_status::deferred`；當與`*this`相關的異步結果準備就緒，返回`std::future_status::ready`；`Clock::now()`返回的時間大於等於absolute_time，返回`std::future_status::timeout`。

**NOTE**:這裡不保證調用線程會被阻塞多久，只有函數返回`std::future_status::timeout`，然後`Clock::now()`返回的時間大於等於absolute_time的時候，線程才會解除阻塞。

**拋出**
無

### std::future::get 成員函數

當相關狀態包含一個`std::async`調用的延遲函數，調用該延遲函數，並返回結果；否則，等待與`std::future`實例相關的異步結果準備就緒，之後返回存儲的值或異常。

**聲明**

```
void future<void>::get();
R& future<R&>::get();
R future<R>::get();
```

**先決條件**
this->valid()將返回true。

**效果**
如果*this相關狀態包含一個延期函數，那麼調用這個函數並返回結果，或將拋出的異常進行傳播。

否則，線程就要被阻塞，直到與*this相關的異步結果就緒。當結果存儲了一個異常，那麼就就會將存儲異常拋出。否則，將會返回存儲值。

**返回**
當相關狀態包含一個延期函數，那麼這個延期函數的結果將被返回。否則，當ResultType為void時，就會按照常規調用返回。如果ResultType是R&(R類型的引用)，存儲的引用值將會被返回。否則，存儲的值將會返回。

**拋出**
異常由延期函數，或存儲在異步結果中的異常(如果有的話)拋出。

**後置條件**

```
this->valid()==false
```

## D.4.2 std::shared_future類型模板

`std::shared_future`類型模板是為了等待其他線程上的異步結果。其和`std::promise`，`std::packaged_task`類型模板，還有`std::async`函數模板，都是為異步結果準備的工具。多個`std::shared_future`實例可以引用同一個異步結果。

`std::shared_future`實例是CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)。你也可以同ResultType的`std::future`類型對象，移動構造一個`std::shared_future`類型對象。

訪問給定`std::shared_future`實例是非同步的。因此，當有多個線程訪問同一個`std::shared_future`實例，且無任何外圍同步操作時，這樣的訪問是不安全的。不過訪問關聯狀態時是同步的，所以多個線程訪問多個獨立的`std::shared_future`實例，且沒有外圍同步操作的時候，是安全的。

**類型定義**

```
template<typename ResultType>
class shared_future
{
public:
  shared_future() noexcept;
  shared_future(future<ResultType>&&) noexcept;
  
  shared_future(shared_future&&) noexcept;
  shared_future(shared_future const&);
  shared_future& operator=(shared_future const&);
  shared_future& operator=(shared_future&&) noexcept;
  ~shared_future();

  bool valid() const noexcept;

  see description get() const;

  void wait() const;

  template<typename Rep,typename Period>
  future_status wait_for(
     std::chrono::duration<Rep,Period> const& relative_time) const;

  template<typename Clock,typename Duration>
  future_status wait_until(
     std::chrono::time_point<Clock,Duration> const& absolute_time)
    const;
};
```

### std::shared_future 默認構造函數

不使用關聯異步結果，構造一個`std::shared_future`對象。

**聲明**

```
shared_future() noexcept;
```

**效果**
構造一個新的`std::shared_future`實例。

**後置條件**
當新實例構建完成後，調用valid()將返回false。

**拋出**
無

### std::shared_future 移動構造函數

以一個已創建`std::shared_future`對象為準，構造`std::shared_future`實例，並將使用`std::shared_future`對象關聯的異步結果的所有權轉移到新的實例中。

**聲明**

```
shared_future(shared_future&& other) noexcept;
```

**效果**
構造一個新`std::shared_future`實例。

**後置條件**
將other對象中關聯異步結果的所有權轉移到新對象中，這樣other對象就沒有與之相關聯的異步結果了。

**拋出**
無

### std::shared_future 移動對應std::future對象的構造函數

以一個已創建`std::future`對象為準，構造`std::shared_future`實例，並將使用`std::shared_future`對象關聯的異步結果的所有權轉移到新的實例中。

**聲明**

```
shared_future(std::future<ResultType>&& other) noexcept;
```

**效果**
構造一個`std::shared_future`對象。

**後置條件**
將other對象中關聯異步結果的所有權轉移到新對象中，這樣other對象就沒有與之相關聯的異步結果了。

**拋出**
無

### std::shared_future 拷貝構造函數

以一個已創建`std::future`對象為準，構造`std::shared_future`實例，並將使用`std::shared_future`對象關聯的異步結果(如果有的話)拷貝到新創建對象當中，兩個對象共享該異步結果。

**聲明**

```
shared_future(shared_future const& other);
```

**效果**
構造一個`std::shared_future`對象。

**後置條件**
將other對象中關聯異步結果拷貝到新對象中，與other共享關聯的異步結果。

**拋出**
無

### std::shared_future 析構函數

銷燬一個`std::shared_future`對象。

**聲明**

```
~shared_future();
```

**效果**
將`*this`銷燬。如果`*this`關聯的異步結果與`std::promise`或`std::packaged_task`不再有關聯，那麼該函數將會切斷`std::shared_future`實例與異步結果的聯繫，並銷燬異步結果。

**拋出**
無

### std::shared_future::valid 成員函數

檢查`std::shared_future`實例是否與一個異步結果相關聯。

**聲明**

```
bool valid() const noexcept;
```

**返回**
當與異步結果相關時，返回true，否則返回false。

**拋出**
無

### std::shared_future::wait 成員函數

當*this關聯狀態包含一個延期函數，那麼調用這個函數。否則，等待直到與`std::shared_future`實例相關的異步結果就緒為止。

**聲明**

```
void wait() const;
```

**先決條件**
this->valid()將返回true。

**效果**
當有多個線程調用`std::shared_future`實例上的get()和wait()時，實例會序列化的共享同一關聯狀態。如果關聯狀態包括一個延期函數，那麼第一個調用get()或wait()時就會調用延期函數，並且存儲返回值，或將拋出異常以異步結果的方式保存下來。

**拋出**
無

### std::shared_future::wait_for 成員函數

等待`std::shared_future`實例上相關異步結果準備就緒，或超過某個給定的時間。

**聲明**

```
template<typename Rep,typename Period>
future_status wait_for(
    std::chrono::duration<Rep,Period> const& relative_time) const;
```

**先決條件**
`this->valid()`將會返回true。

**效果**
如果與`*this`相關的異步結果包含一個`std::async`調用的延期函數(還未執行)，那麼就不阻塞立即返回。否則將阻塞實例，直到與`*this`相關異步結果準備就緒，或超過給定的relative_time時長。

**返回**
當與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，返回`std::future_status::deferred`；當與`*this`相關的異步結果準備就緒，返回`std::future_status::ready`；當給定時間超過relative_time時，返回`std::future_status::timeout`。

**NOTE**:線程阻塞的時間可能超多給定的時長。時長儘可能由一個穩定的時鐘決定。

**拋出**
無

### std::shared_future::wait_until 成員函數

等待`std::future`實例上相關異步結果準備就緒，或超過某個給定的時間。

**聲明**

```
template<typename Clock,typename Duration>
future_status wait_until(
  std::chrono::time_point<Clock,Duration> const& absolute_time) const;
```

**先決條件**
this->valid()將返回true。

**效果**
如果與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，那麼就不阻塞立即返回。否則將阻塞實例，直到與`*this`相關異步結果準備就緒，或`Clock::now()`返回的時間大於等於absolute_time。

**返回**
當與`*this`相關的異步結果包含一個`std::async`調用的延遲函數(還未執行)，返回`std::future_status::deferred`；當與`*this`相關的異步結果準備就緒，返回`std::future_status::ready`；`Clock::now()`返回的時間大於等於absolute_time，返回`std::future_status::timeout`。

**NOTE**:這裡不保證調用線程會被阻塞多久，只有函數返回`std::future_status::timeout`，然後`Clock::now()`返回的時間大於等於absolute_time的時候，線程才會解除阻塞。

**拋出**
無

### std::shared_future::get 成員函數

當相關狀態包含一個`std::async`調用的延遲函數，調用該延遲函數，並返回結果；否則，等待與`std::shared_future`實例相關的異步結果準備就緒，之後返回存儲的值或異常。

**聲明**

```
void shared_future<void>::get() const;
R& shared_future<R&>::get() const;
R const& shared_future<R>::get() const;
```

**先決條件**
this->valid()將返回true。

**效果**
當有多個線程調用`std::shared_future`實例上的get()和wait()時，實例會序列化的共享同一關聯狀態。如果關聯狀態包括一個延期函數，那麼第一個調用get()或wait()時就會調用延期函數，並且存儲返回值，或將拋出異常以異步結果的方式保存下來。

阻塞會知道*this關聯的異步結果就緒後解除。當異步結果存儲了一個一行，那麼就會拋出這個異常。否則，返回存儲的值。

**返回**
當ResultType為void時，就會按照常規調用返回。如果ResultType是R&(R類型的引用)，存儲的引用值將會被返回。否則，返回存儲值的const引用。

**拋出**
拋出存儲的異常(如果有的話)。

## D.4.3 std::packaged_task類型模板

`std::packaged_task`類型模板可打包一個函數或其他可調用對象，所以當函數通過`std::packaged_task`實例被調用時，結果將會作為異步結果。這個結果可以通過檢索`std::future`實例來查找。

`std::packaged_task`實例是可以MoveConstructible(移動構造)和MoveAssignable(移動賦值)，不過不能CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)。

**類型定義**

```
template<typename FunctionType>
class packaged_task; // undefined

template<typename ResultType,typename... ArgTypes>
class packaged_task<ResultType(ArgTypes...)>
{
public:
  packaged_task() noexcept;
  packaged_task(packaged_task&&) noexcept;
  ~packaged_task();

  packaged_task& operator=(packaged_task&&) noexcept;

  packaged_task(packaged_task const&) = delete;
  packaged_task& operator=(packaged_task const&) = delete;

  void swap(packaged_task&) noexcept;

  template<typename Callable>
  explicit packaged_task(Callable&& func);

  template<typename Callable,typename Allocator>
  packaged_task(std::allocator_arg_t, const Allocator&,Callable&&);

  bool valid() const noexcept;
  std::future<ResultType> get_future();
  void operator()(ArgTypes...);
  void make_ready_at_thread_exit(ArgTypes...);
  void reset();
};
```

### std::packaged_task 默認構造函數

構造一個`std::packaged_task`對象。

**聲明**

```
packaged_task() noexcept;
```

**效果**
不使用關聯任務或異步結果來構造一個`std::packaged_task`對象。

**拋出**
無

### std::packaged_task 通過可調用對象構造

使用關聯任務和異步結果，構造一個`std::packaged_task`對象。

**聲明**

```
template<typename Callable>
packaged_task(Callable&& func);
```

**先決條件**
表達式`func(args...)`必須是合法的，並且在`args...`中的args-i參數，必須是`ArgTypes...`中ArgTypes-i類型的一個值。且返回值必須可轉換為ResultType。

**效果**
使用ResultType類型的關聯異步結果，構造一個`std::packaged_task`對象，異步結果是未就緒的，並且Callable類型相關的任務是對func的一個拷貝。

**拋出**
當構造函數無法為異步結果分配出內存時，會拋出`std::bad_alloc`類型的異常。其他異常會在使用Callable類型的拷貝或移動構造過程中拋出。

### std::packaged_task 通過有分配器的可調用對象構造

使用關聯任務和異步結果，構造一個`std::packaged_task`對象。使用以提供的分配器為關聯任務和異步結果分配內存。

**聲明**

```
template<typename Allocator,typename Callable>
packaged_task(
    std::allocator_arg_t, Allocator const& alloc,Callable&& func);
```

**先決條件**
表達式`func(args...)`必須是合法的，並且在`args...`中的args-i參數，必須是`ArgTypes...`中ArgTypes-i類型的一個值。且返回值必須可轉換為ResultType。

**效果**
使用ResultType類型的關聯異步結果，構造一個`std::packaged_task`對象，異步結果是未就緒的，並且Callable類型相關的任務是對func的一個拷貝。異步結果和任務的內存通過內存分配器alloc進行分配，或進行拷貝。

**拋出**
當構造函數無法為異步結果分配出內存時，會拋出`std::bad_alloc`類型的異常。其他異常會在使用Callable類型的拷貝或移動構造過程中拋出。

### std::packaged_task 移動構造函數

通過一個`std::packaged_task`對象構建另一個，將與已存在的`std::packaged_task`相關的異步結果和任務的所有權轉移到新構建的對象當中。

**聲明**

```
packaged_task(packaged_task&& other) noexcept;
```

**效果**
構建一個新的`std::packaged_task`實例。

**後置條件**
通過other構建新的`std::packaged_task`對象。在新對象構建完成後，other與其之前相關聯的異步結果就沒有任何關係了。

**拋出**
無

### std::packaged_task 移動賦值操作

將一個`std::packaged_task`對象相關的異步結果的所有權轉移到另外一個。

**聲明**

```
packaged_task& operator=(packaged_task&& other) noexcept;
```

**效果**
將other相關異步結果和任務的所有權轉移到`*this`中，並且切斷異步結果和任務與other對象的關聯，如同`std::packaged_task(other).swap(*this)`。

**後置條件**
與other相關的異步結果與任務移動轉移，使*this.other無關聯的異步結果。

**返回**

```
*this
```

**拋出**
無

### std::packaged_task::swap 成員函數

將兩個`std::packaged_task`對象所關聯的異步結果的所有權進行交換。

**聲明**

```
void swap(packaged_task& other) noexcept;
```

**效果**
將other和*this關聯的異步結果與任務進行交換。

**後置條件**
將與other關聯的異步結果和任務，通過調用swap的方式，與*this相交換。

**拋出**
無

### std::packaged_task 析構函數

銷燬一個`std::packaged_task`對象。

**聲明**

```
~packaged_task();
```

**效果**
將`*this`銷燬。如果`*this`有關聯的異步結果，並且結果不是一個已存儲的任務或異常，那麼異步結果狀態將會變為就緒，伴隨就緒的是一個`std::future_error`異常和錯誤碼`std::future_errc::broken_promise`。

**拋出**
無

### std::packaged_task::get_future 成員函數

在*this相關異步結果中，檢索一個`std::future`實例。

**聲明**

```
std::future<ResultType> get_future();
```

**先決條件**
*this具有關聯異步結果。

**返回**
一個與*this關聯異構結果相關的一個`std::future`實例。

**拋出**
如果一個`std::future`已經通過get_future()獲取了異步結果，在拋出`std::future_error`異常時，錯誤碼是`std::future_errc::future_already_retrieved`

### std::packaged_task::reset 成員函數

將一個`std::packaged_task`對實例與一個新的異步結果相關聯。

**聲明**

```
void reset();
```

**先決條件**
*this具有關聯的異步任務。

**效果**
如同`*this=packaged_task(std::move(f))`，f是*this中已存儲的關聯任務。

**拋出**
如果內存不足以分配給新的異構結果，那麼將會拋出`std::bad_alloc`類異常。

### std::packaged_task::valid 成員函數

檢查*this中是都具有關聯任務和異步結果。

**聲明**

```
bool valid() const noexcept;
```

**返回**
當*this具有相關任務和異步結構，返回true；否則，返回false。

**拋出**
無

### std::packaged_task::operator() 函數調用操作

調用一個`std::packaged_task`實例中的相關任務，並且存儲返回值，或將異常存儲到異常結果當中。

**聲明**

```
void operator()(ArgTypes... args);
```

**先決條件**
*this具有相關任務。

**效果**
像`INVOKE(func,args...)`那要調用相關的函數func。如果返回征程，那麼將會存儲到*this相關的異步結果中。當返回結果是一個異常，將這個異常存儲到*this相關的異步結果中。

**後置條件**
*this相關聯的異步結果狀態為就緒，並且存儲了一個值或異常。所有阻塞線程，在等待到異步結果的時候被解除阻塞。

**拋出**
當異步結果已經存儲了一個值或異常，那麼將拋出一個`std::future_error`異常，錯誤碼為`std::future_errc::promise_already_satisfied`。

**同步**
`std::future<ResultType>::get()`或`std::shared_future<ResultType>::get()`的成功調用，代表同步操作的成功，函數將會檢索異步結果中的值或異常。

### std::packaged_task::make_ready_at_thread_exit 成員函數

調用一個`std::packaged_task`實例中的相關任務，並且存儲返回值，或將異常存儲到異常結果當中，直到線程退出時，將相關異步結果的狀態置為就緒。

**聲明**

```
void make_ready_at_thread_exit(ArgTypes... args);
```

**先決條件**
*this具有相關任務。

**效果**
像`INVOKE(func,args...)`那要調用相關的函數func。如果返回征程，那麼將會存儲到`*this`相關的異步結果中。當返回結果是一個異常，將這個異常存儲到`*this`相關的異步結果中。噹噹前線程退出的時候，可調配相關異步狀態為就緒。

**後置條件**
*this的異步結果中已經存儲了一個值或一個異常，不過在當前線程退出的時候，這個結果都是非就緒的。噹噹前線程退出時，阻塞等待異步結果的線程將會被解除阻塞。

**拋出**
當異步結果已經存儲了一個值或異常，那麼將拋出一個`std::future_error`異常，錯誤碼為`std::future_errc::promise_already_satisfied`。當無關聯異步狀態時，拋出`std::future_error`異常，錯誤碼為`std::future_errc::no_state`。

**同步**
`std::future<ResultType>::get()`或`std::shared_future<ResultType>::get()`在線程上的成功調用，代表同步操作的成功，函數將會檢索異步結果中的值或異常。

## D.4.4 std::promise類型模板

`std::promise`類型模板提供設置異步結果的方法，這樣其他線程就可以通過`std::future`實例來索引該結果。

ResultType模板參數，該類型可以存儲異步結果。

`std::promise`實例中的異步結果與某個`srd::future`實例相關聯，並且可以通過調用get_future()成員函數來獲取這個`srd::future`實例。ResultType類型的異步結果，可以通過set_value()成員函數對存儲值進行設置，或者使用set_exception()將對應異常設置進異步結果中。

`std::promise`實例是可以MoveConstructible(移動構造)和MoveAssignable(移動賦值)，但是不能CopyConstructible(拷貝構造)和CopyAssignable(拷貝賦值)。

**類型定義**

```
template<typename ResultType>
class promise
{
public:
  promise();
  promise(promise&&) noexcept;
  ~promise();
  promise& operator=(promise&&) noexcept;

  template<typename Allocator>
  promise(std::allocator_arg_t, Allocator const&);

  promise(promise const&) = delete;
  promise& operator=(promise const&) = delete;

  void swap(promise& ) noexcept;
  
  std::future<ResultType> get_future();

  void set_value(see description);
  void set_exception(std::exception_ptr p);
};
```

### std::promise 默認構造函數

構造一個`std::promise`對象。

**聲明**

```
promise();
```

**效果**
使用ResultType類型的相關異步結果來構造`std::promise`實例，不過異步結果並未就緒。

**拋出**
當沒有足夠內存為異步結果進行分配，那麼將拋出`std::bad_alloc`型異常。

### std::promise 帶分配器的構造函數

構造一個`std::promise`對象，使用提供的分配器來為相關異步結果分配內存。

**聲明**

```
template<typename Allocator>
promise(std::allocator_arg_t, Allocator const& alloc);
```

**效果**
使用ResultType類型的相關異步結果來構造`std::promise`實例，不過異步結果並未就緒。異步結果的內存由alloc分配器來分配。

**拋出**
當分配器為異步結果分配內存時，如有拋出異常，就為該函數拋出的異常。

### std::promise 移動構造函數

通過另一個已存在對象，構造一個`std::promise`對象。將已存在對象中的相關異步結果的所有權轉移到新創建的`std::promise`對象當中。

**聲明**

```
promise(promise&& other) noexcept;
```

**效果**
構造一個`std::promise`實例。

**後置條件**
當使用other來構造一個新的實例，那麼other中相關異構結果的所有權將轉移到新創建的對象上。之後，other將無關聯異步結果。

**拋出**
無

### std::promise 移動賦值操作符

在兩個`std::promise`實例中轉移異步結果的所有權。

**聲明**

```
promise& operator=(promise&& other) noexcept;
```

**效果**
在other和`*this`之間進行異步結果所有權的轉移。當`*this`已經有關聯的異步結果，那麼該異步結果的狀態將會為就緒態，且伴隨一個`std::future_error`類型異常，錯誤碼為`std::future_errc::broken_promise`。

**後置條件**
將other中關聯的異步結果轉移到*this當中。other中將無關聯異步結果。

**返回**

```
*this
```

**拋出**
無

### std::promise::swap 成員函數

將兩個`std::promise`實例中的關聯異步結果進行交換。

**聲明**

```
void swap(promise& other);
```

**效果**
交換other和*this當中的關聯異步結果。

**後置條件**
當swap使用other時，other中的異步結果就會與*this中關聯異步結果相交換。二者返回來亦然。

**拋出**
無

### std::promise 析構函數

銷燬`std::promise`對象。

**聲明**

```
~promise();
```

**效果**
銷燬`*this`。當`*this`具有關聯的異步結果，並且結果中沒有存儲值或異常，那麼結果將會置為就緒，伴隨一個`std::future_error`異常，錯誤碼為`std::future_errc::broken_promise`。

**拋出**
無

### std::promise::get_future 成員函數

通過*this關聯的異步結果，檢索出所要的`std::future`實例。

**聲明**

```
std::future<ResultType> get_future();
```

**先決條件**
*this具有關聯異步結果。

**返回**
與*this關聯異步結果關聯的`std::future`實例。

**拋出**
當`std::future`已經通過get_future()獲取過了，將會拋出一個`std::future_error`類型異常，伴隨的錯誤碼為`std::future_errc::future_already_retrieved`。

### std::promise::set_value 成員函數

存儲一個值到與*this關聯的異步結果中。

**聲明**

```
void promise<void>::set_value();
void promise<R&>::set_value(R& r);
void promise<R>::set_value(R const& r);
void promise<R>::set_value(R&& r);
```

**先決條件**
*this具有關聯異步結果。

**效果**
當ResultType不是void型，就存儲r到*this相關的異步結果當中。

**後置條件**
*this相關的異步結果的狀態為就緒，且將值存入。任意等待異步結果的阻塞線程將解除阻塞。

**拋出**
當異步結果已經存有一個值或一個異常，那麼將拋出`std::future_error`型異常，伴隨錯誤碼為`std::future_errc::promise_already_satisfied`。r的拷貝構造或移動構造拋出的異常，即為本函數拋出的異常。

**同步**
併發調用set_value()和set_exception()的線程將被序列化。要想成功的調用set_exception()，需要在之前調用`std::future<Result-Type>::get()`或`std::shared_future<ResultType>::get()`，這兩個函數將會查找已存儲的異常。

### std::promise::set_value_at_thread_exit 成員函數

存儲一個值到與*this關聯的異步結果中，到線程退出時，異步結果的狀態會被設置為就緒。

**聲明**

```
void promise<void>::set_value_at_thread_exit();
void promise<R&>::set_value_at_thread_exit(R& r);
void promise<R>::set_value_at_thread_exit(R const& r);
void promise<R>::set_value_at_thread_exit(R&& r);
```

**先決條件**
*this具有關聯異步結果。

**效果**
當ResultType不是void型，就存儲r到*this相關的異步結果當中。標記異步結果為“已存儲值”。當前線程退出時，會安排相關異步結果的狀態為就緒。

**後置條件**
將值存入*this相關的異步結果，且直到當前線程退出時，異步結果狀態被置為就緒。任何等待異步結果的阻塞線程將解除阻塞。

**拋出**
當異步結果已經存有一個值或一個異常，那麼將拋出`std::future_error`型異常，伴隨錯誤碼為`std::future_errc::promise_already_satisfied`。r的拷貝構造或移動構造拋出的異常，即為本函數拋出的異常。

**同步**
併發調用set_value(), set_value_at_thread_exit(), set_exception()和set_exception_at_thread_exit()的線程將被序列化。要想成功的調用set_exception()，需要在之前調用`std::future<Result-Type>::get()`或`std::shared_future<ResultType>::get()`，這兩個函數將會查找已存儲的異常。

### std::promise::set_exception 成員函數

存儲一個異常到與*this關聯的異步結果中。

**聲明**

```
void set_exception(std::exception_ptr e);
```

**先決條件**
*this具有關聯異步結果。(bool)e為true。

**效果**
將e存儲到*this相關的異步結果中。

**後置條件**
在存儲異常後，*this相關的異步結果的狀態將置為繼續。任何等待異步結果的阻塞線程將解除阻塞。

**拋出**
當異步結果已經存有一個值或一個異常，那麼將拋出`std::future_error`型異常，伴隨錯誤碼為`std::future_errc::promise_already_satisfied`。

**同步**
併發調用set_value()和set_exception()的線程將被序列化。要想成功的調用set_exception()，需要在之前調用`std::future<Result-Type>::get()`或`std::shared_future<ResultType>::get()`，這兩個函數將會查找已存儲的異常。

### std::promise::set_exception_at_thread_exit 成員函數

存儲一個異常到與*this關聯的異步結果中，知道當前線程退出，異步結果被置為就緒。

**聲明**

```
void set_exception_at_thread_exit(std::exception_ptr e);
```

**先決條件**
*this具有關聯異步結果。(bool)e為true。

**效果**
將e存儲到*this相關的異步結果中。標記異步結果為“已存儲值”。當前線程退出時，會安排相關異步結果的狀態為就緒。

**後置條件**
將值存入*this相關的異步結果，且直到當前線程退出時，異步結果狀態被置為就緒。任何等待異步結果的阻塞線程將解除阻塞。

**拋出**
當異步結果已經存有一個值或一個異常，那麼將拋出`std::future_error`型異常，伴隨錯誤碼為`std::future_errc::promise_already_satisfied`。

**同步**
併發調用set_value(), set_value_at_thread_exit(), set_exception()和set_exception_at_thread_exit()的線程將被序列化。要想成功的調用set_exception()，需要在之前調用`std::future<Result-Type>::get()`或`std::shared_future<ResultType>::get()`，這兩個函數將會查找已存儲的異常。

## D.4.5 std::async函數模板

`std::async`能夠簡單的使用可用的硬件並行來運行自身包含的異步任務。當調用`std::async`返回一個包含任務結果的`std::future`對象。根據投放策略，任務在其所在線程上是異步運行的，當有線程調用了這個future對象的wait()和get()成員函數，則該任務會同步運行。

**聲明**

```
enum class launch
{
  async,deferred
};

template<typename Callable,typename ... Args>
future<result_of<Callable(Args...)>::type>
async(Callable&& func,Args&& ... args);

template<typename Callable,typename ... Args>
future<result_of<Callable(Args...)>::type>
async(launch policy,Callable&& func,Args&& ... args);
```

**先決條件**
表達式`INVOKE(func,args)`能都為func提供合法的值和args。Callable和Args的所有成員都可MoveConstructible(可移動構造)。

**效果**
在內部存儲中拷貝構造`func`和`arg...`(分別使用fff和xyz...進行表示)。

當policy是`std::launch::async`,運行`INVOKE(fff,xyz...)`在所在線程上。當這個線程完成時，返回的`std::future`狀態將會為就緒態，並且之後會返回對應的值或異常(由調用函數拋出)。析構函數會等待返回的`std::future`相關異步狀態為就緒時，才解除阻塞。

當policy是`std::launch::deferred`，fff和xyx...都會作為延期函數調用，存儲在返回的`std::future`。首次調用future的wait()或get()成員函數，將會共享相關狀態，之後執行的`INVOKE(fff,xyz...)`與調用wait()或get()函數的線程同步執行。

執行`INVOKE(fff,xyz...)`後，在調用`std::future`的成員函數get()時，就會有值返回或有異常拋出。

當policy是`std::launch::async | std::launch::deferred`或是policy參數被省略，其行為如同已指定的`std::launch::async`或`std::launch::deferred`。具體實現將會通過逐漸遞增的方式(call-by-call basis)最大化利用可用的硬件並行，並避免超限分配的問題。

在所有的情況下，`std::async`調用都會直接返回。

**同步**
完成函數調用的先行條件是，需要通過調用`std::future`和`std::shared_future`實例的wait(),get(),wait_for()或wait_until()，返回的對象與`std::async`返回的`std::future`對象關聯的狀態相同才算成功。就`std::launch::async`這個policy來說，在完成線程上的函數前，也需要先行對上面的函數調用後，成功的返回才行。

**拋出**
當內部存儲無法分配所需的空間，將拋出`std::bad_alloc`類型異常；否則，當效果沒有達到，或任何異常在構造fff和xyz...發生時，拋出`std::future_error`異常。
