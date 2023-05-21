# D.2 &lt;condition_variable&gt;頭文件

&lt;condition_variable&gt;頭文件提供了條件變量的定義。其作為基本同步機制，允許被阻塞的線程在某些條件達成或超時時，解除阻塞繼續執行。

### 頭文件內容

```
namespace std
{
  enum class cv_status { timeout, no_timeout };
  
  class condition_variable;
  class condition_variable_any;
}
```

## D.2.1 std::condition_variable類

`std::condition_variable`允許阻塞一個線程，直到條件達成。

`std::condition_variable`實例不支持CopyAssignable(拷貝賦值), CopyConstructible(拷貝構造), MoveAssignable(移動賦值)和 MoveConstructible(移動構造)。

### 類型定義

```
class condition_variable
{
public:
  condition_variable();
  ~condition_variable();

  condition_variable(condition_variable const& ) = delete;
  condition_variable& operator=(condition_variable const& ) = delete;

  void notify_one() noexcept;
  void notify_all() noexcept;

  void wait(std::unique_lock<std::mutex>& lock);

  template <typename Predicate>
  void wait(std::unique_lock<std::mutex>& lock,Predicate pred);

  template <typename Clock, typename Duration>
  cv_status wait_until(
       std::unique_lock<std::mutex>& lock,
       const std::chrono::time_point<Clock, Duration>& absolute_time);

  template <typename Clock, typename Duration, typename Predicate>
  bool wait_until(
       std::unique_lock<std::mutex>& lock,
       const std::chrono::time_point<Clock, Duration>& absolute_time,
       Predicate pred);

  template <typename Rep, typename Period>
  cv_status wait_for(
       std::unique_lock<std::mutex>& lock,
       const std::chrono::duration<Rep, Period>& relative_time);

  template <typename Rep, typename Period, typename Predicate>
  bool wait_for(
       std::unique_lock<std::mutex>& lock,
       const std::chrono::duration<Rep, Period>& relative_time,
       Predicate pred);
};

void notify_all_at_thread_exit(condition_variable&,unique_lock<mutex>);
```

### std::condition_variable 默認構造函數

構造一個`std::condition_variable`對象。

**聲明**

```
condition_variable();
```

**效果**
構造一個新的`std::condition_variable`實例。

**拋出**
當條件變量無法夠早的時候，將會拋出一個`std::system_error`異常。

### std::condition_variable 析構函數

銷燬一個`std::condition_variable`對象。

**聲明**

```
~condition_variable();
```

**先決條件**
之前沒有使用*this總的wait(),wait_for()或wait_until()阻塞過線程。

**效果**
銷燬*this。

**拋出**
無

### std::condition_variable::notify_one 成員函數

喚醒一個等待當前`std::condition_variable`實例的線程。

**聲明**

```
void notify_one() noexcept;
```

**效果**
喚醒一個等待*this的線程。如果沒有線程在等待，那麼調用沒有任何效果。

**拋出**
當效果沒有達成，就會拋出`std::system_error`異常。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::notify_all 成員函數

喚醒所有等待當前`std::condition_variable`實例的線程。

**聲明**

```
void notify_all() noexcept;
```

**效果**
喚醒所有等待*this的線程。如果沒有線程在等待，那麼調用沒有任何效果。

**拋出**
當效果沒有達成，就會拋出`std::system_error`異常

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::wait 成員函數

通過`std::condition_variable`的notify_one()、notify_all()或偽喚醒結束等待。

**等待**

```
void wait(std::unique_lock<std::mutex>& lock);
```

**先決條件**
當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
自動解鎖lock對象，對於線程等待線程，當其他線程調用notify_one()或notify_all()時被喚醒，亦或該線程處於偽喚醒狀態。在wait()返回前，lock對象將會再次上鎖。

**拋出**
當效果沒有達成的時候，將會拋出`std::system_error`異常。當lock對象在調用wait()階段被解鎖，那麼當wait()退出的時候lock會再次上鎖，即使函數是通過異常的方式退出。

**NOTE**:偽喚醒意味著一個線程調用wait()後，在沒有其他線程調用notify_one()或notify_all()時，還處以甦醒狀態。因此，建議對wait()進行重載，在可能的情況下使用一個謂詞。否則，建議wait()使用循環檢查與條件變量相關的謂詞。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::wait 需要一個謂詞的成員函數重載

等待`std::condition_variable`上的notify_one()或notify_all()被調用，或謂詞為true的情況，來喚醒線程。

**聲明**

```
template<typename Predicate>
void wait(std::unique_lock<std::mutex>& lock,Predicate pred);
```

**先決條件**
pred()謂詞必須是合法的，並且需要返回一個值，這個值可以和bool互相轉化。當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
正如

```
while(!pred())
{
  wait(lock);
}
```

**拋出**
pred中可以拋出任意異常，或者當效果沒有達到的時候，拋出`std::system_error`異常。

**NOTE**:潛在的偽喚醒意味著不會指定pred調用的次數。通過lock進行上鎖，pred經常會被互斥量引用所調用，並且函數必須返回(只能返回)一個值，在`(bool)pred()`評估後，返回true。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::wait_for 成員函數

`std::condition_variable`在調用notify_one()、調用notify_all()、超時或線程偽喚醒時，結束等待。

**聲明**

```
template<typename Rep,typename Period>
cv_status wait_for(
    std::unique_lock<std::mutex>& lock,
    std::chrono::duration<Rep,Period> const& relative_time);
```

**先決條件**
當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
當其他線程調用notify_one()或notify_all()函數時，或超出了relative_time的時間，亦或是線程被偽喚醒，則將lock對象自動解鎖，並將阻塞線程喚醒。當wait_for()調用返回前，lock對象會再次上鎖。

**返回**
線程被notify_one()、notify_all()或偽喚醒喚醒時，會返回`std::cv_status::no_timeout`；反之，則返回`std::cv_status::timeout`。

**拋出**
當效果沒有達成的時候，會拋出`std::system_error`異常。當lock對象在調用wait_for()函數前解鎖，那麼lock對象會在wait_for()退出前再次上鎖，即使函數是以異常的方式退出。

**NOTE**:偽喚醒意味著，一個線程在調用wait_for()的時候，即使沒有其他線程調用notify_one()和notify_all()函數，也處於甦醒狀態。因此，這裡建議重載wait_for()函數，重載函數可以使用謂詞。要不，則建議wait_for()使用循環的方式對與謂詞相關的條件變量進行檢查。在這樣做的時候還需要小心，以確保超時部分依舊有效；wait_until()可能適合更多的情況。這樣的話，線程阻塞的時間就要比指定的時間長了。在有這樣可能性的地方，流逝的時間是由穩定時鐘決定。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::wait_for 需要一個謂詞的成員函數重載

`std::condition_variable`在調用notify_one()、調用notify_all()、超時或線程偽喚醒時，結束等待。

**聲明**

```
template<typename Rep,typename Period,typename Predicate>
bool wait_for(
    std::unique_lock<std::mutex>& lock,
    std::chrono::duration<Rep,Period> const& relative_time,
    Predicate pred);
```

**先決條件**
pred()謂詞必須是合法的，並且需要返回一個值，這個值可以和bool互相轉化。當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
等價於

```
internal_clock::time_point end=internal_clock::now()+relative_time;
while(!pred())
{
  std::chrono::duration<Rep,Period> remaining_time=
      end-internal_clock::now();
  if(wait_for(lock,remaining_time)==std::cv_status::timeout)
      return pred();
}
return true;
```

**返回**
當pred()為true，則返回true；當超過relative_time並且pred()返回false時，返回false。

**NOTE**:潛在的偽喚醒意味著不會指定pred調用的次數。通過lock進行上鎖，pred經常會被互斥量引用所調用，並且函數必須返回(只能返回)一個值，在`(bool)pred()`評估後返回true，或在指定時間relative_time內完成。線程阻塞的時間就要比指定的時間長了。在有這樣可能性的地方，流逝的時間是由穩定時鐘決定。

**拋出**
當效果沒有達成時，會拋出`std::system_error`異常或者由pred拋出任意異常。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::wait_until 成員函數

`std::condition_variable`在調用notify_one()、調用notify_all()、指定時間內達成條件或線程偽喚醒時，結束等待。

**聲明**

```
template<typename Clock,typename Duration>
cv_status wait_until(
    std::unique_lock<std::mutex>& lock,
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**先決條件**
當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
當其他線程調用notify_one()或notify_all()函數，或Clock::now()返回一個大於或等於absolute_time的時間，亦或線程偽喚醒，lock都將自動解鎖，並且喚醒阻塞的線程。在wait_until()返回之前lock對象會再次上鎖。

**返回**
線程被notify_one()、notify_all()或偽喚醒喚醒時，會返回`std::cv_status::no_timeout`；反之，則返回`std::cv_status::timeout`。

**拋出**
當效果沒有達成的時候，會拋出`std::system_error`異常。當lock對象在調用wait_for()函數前解鎖，那麼lock對象會在wait_for()退出前再次上鎖，即使函數是以異常的方式退出。

**NOTE**:偽喚醒意味著一個線程調用wait()後，在沒有其他線程調用notify_one()或notify_all()時，還處以甦醒狀態。因此，這裡建議重載wait_until()函數，重載函數可以使用謂詞。要不，則建議wait_until()使用循環的方式對與謂詞相關的條件變量進行檢查。這裡不保證線程會被阻塞多長時間，只有當函數返回false後(Clock::now()的返回值大於或等於absolute_time)，線程才能解除阻塞。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable::wait_until 需要一個謂詞的成員函數重載

`std::condition_variable`在調用notify_one()、調用notify_all()、謂詞返回true或指定時間內達到條件，結束等待。

**聲明**

```
template<typename Clock,typename Duration,typename Predicate>
bool wait_until(
    std::unique_lock<std::mutex>& lock,
    std::chrono::time_point<Clock,Duration> const& absolute_time,
    Predicate pred);
```

**先決條件**
pred()必須是合法的，並且其返回值能轉換為bool值。當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
等價於

```
while(!pred())
{
  if(wait_until(lock,absolute_time)==std::cv_status::timeout)
    return pred();
}
return true;
```

**返回**
當調用pred()返回true時，返回true；當Clock::now()的時間大於或等於指定的時間absolute_time，並且pred()返回false時，返回false。

**NOTE**:潛在的偽喚醒意味著不會指定pred調用的次數。通過lock進行上鎖，pred經常會被互斥量引用所調用，並且函數必須返回(只能返回)一個值，在`(bool)pred()`評估後返回true，或Clock::now()返回的時間大於或等於absolute_time。這裡不保證調用線程將被阻塞的時長，只有當函數返回false後(Clock::now()返回一個等於或大於absolute_time的值)，線程接觸阻塞。

**拋出**
當效果沒有達成時，會拋出`std::system_error`異常或者由pred拋出任意異常。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::notify_all_at_thread_exit 非成員函數

噹噹前調用函數的線程退出時，等待`std::condition_variable`的所有線程將會被喚醒。

**聲明**

```
void notify_all_at_thread_exit(
  condition_variable& cv,unique_lock<mutex> lk);
```

**先決條件**
當線程調用wait()即可獲得鎖的所有權,lk.owns_lock()必須為true。lk.mutex()需要返回的值要與併發等待線程相關的任意cv中鎖對象提供的wait(),wait_for()或wait_until()相同。

**效果**
將lk的所有權轉移到內部存儲中，並且當有線程退出時，安排被提醒的cv類。這裡的提醒等價於

```
lk.unlock();
cv.notify_all();
```

**拋出**
當效果沒有達成時，拋出`std::system_error`異常。

**NOTE**:在線程退出前，掌握著鎖的所有權，所以這裡要避免死鎖發生。這裡建議調用該函數的線程應該儘快退出，並且在該線程可以執行一些阻塞的操作。用戶必須保證等地線程不會錯誤的將喚醒線程當做已退出的線程，特別是偽喚醒。可以通過等待線程上的謂詞測試來實現這一功能，在互斥量保護的情況下，只有謂詞返回true時線程才能被喚醒，並且在調用notify_all_at_thread_exit(std::condition_variable_any類中函數)前是不會釋放鎖。

## D.2.2 std::condition_variable_any類

`std::condition_variable_any`類允許線程等待某一條件為true的時候繼續運行。不過`std::condition_variable`只能和`std::unique_lock<std::mutex>`一起使用，`std::condition_variable_any`可以和任意可上鎖(Lockable)類型一起使用。

`std::condition_variable_any`實例不能進行拷貝賦值(CopyAssignable)、拷貝構造(CopyConstructible)、移動賦值(MoveAssignable)或移動構造(MoveConstructible)。

### 類型定義

```
class condition_variable_any
{
public:
  condition_variable_any();
  ~condition_variable_any();

  condition_variable_any(
      condition_variable_any const& ) = delete;
  condition_variable_any& operator=(
      condition_variable_any const& ) = delete;

  void notify_one() noexcept;
  void notify_all() noexcept;

  template<typename Lockable>
  void wait(Lockable& lock);

  template <typename Lockable, typename Predicate>
  void wait(Lockable& lock, Predicate pred);

  template <typename Lockable, typename Clock,typename Duration>
  std::cv_status wait_until(
      Lockable& lock,
      const std::chrono::time_point<Clock, Duration>& absolute_time);

  template <
      typename Lockable, typename Clock,
      typename Duration, typename Predicate>
  bool wait_until(
      Lockable& lock,
      const std::chrono::time_point<Clock, Duration>& absolute_time,
      Predicate pred);

  template <typename Lockable, typename Rep, typename Period>
  std::cv_status wait_for(
      Lockable& lock,
      const std::chrono::duration<Rep, Period>& relative_time);

  template <
      typename Lockable, typename Rep,
      typename Period, typename Predicate>
  bool wait_for(
      Lockable& lock,
      const std::chrono::duration<Rep, Period>& relative_time,
      Predicate pred);
};
```

### std::condition_variable_any 默認構造函數

構造一個`std::condition_variable_any`對象。

**聲明**

```
condition_variable_any();
```

**效果**
構造一個新的`std::condition_variable_any`實例。

**拋出**
當條件變量構造成功，將拋出`std::system_error`異常。

### std::condition_variable_any 析構函數

銷燬`std::condition_variable_any`對象。

**聲明**

```
~condition_variable_any();
```

**先決條件**
之前沒有使用*this總的wait(),wait_for()或wait_until()阻塞過線程。

**效果**
銷燬*this。

**拋出**
無

### std::condition_variable_any::notify_one 成員函數

`std::condition_variable_any`喚醒一個等待該條件變量的線程。

**聲明**

```
void notify_all() noexcept;
```

**效果**
喚醒一個等待*this的線程。如果沒有線程在等待，那麼調用沒有任何效果

**拋出**
當效果沒有達成，就會拋出std::system_error異常。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::notify_all 成員函數

喚醒所有等待當前`std::condition_variable_any`實例的線程。

**聲明**

```
void notify_all() noexcept;
```

**效果**
喚醒所有等待*this的線程。如果沒有線程在等待，那麼調用沒有任何效果

**拋出**
當效果沒有達成，就會拋出std::system_error異常。

**同步**
`std::condition_variable`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::wait 成員函數

通過`std::condition_variable_any`的notify_one()、notify_all()或偽喚醒結束等待。

**聲明**

```
template<typename Lockable>
void wait(Lockable& lock);
```

**先決條件**
Lockable類型需要能夠上鎖，lock對象擁有一個鎖。

**效果**
自動解鎖lock對象，對於線程等待線程，當其他線程調用notify_one()或notify_all()時被喚醒，亦或該線程處於偽喚醒狀態。在wait()返回前，lock對象將會再次上鎖。

**拋出**
當效果沒有達成的時候，將會拋出`std::system_error`異常。當lock對象在調用wait()階段被解鎖，那麼當wait()退出的時候lock會再次上鎖，即使函數是通過異常的方式退出。

**NOTE**:偽喚醒意味著一個線程調用wait()後，在沒有其他線程調用notify_one()或notify_all()時，還處以甦醒狀態。因此，建議對wait()進行重載，在可能的情況下使用一個謂詞。否則，建議wait()使用循環檢查與條件變量相關的謂詞。

**同步**
std::condition_variable_any實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::wait 需要一個謂詞的成員函數重載

等待`std::condition_variable_any`上的notify_one()或notify_all()被調用，或謂詞為true的情況，來喚醒線程。

**聲明**

```
template<typename Lockable,typename Predicate>
void wait(Lockable& lock,Predicate pred);
```

**先決條件**
pred()謂詞必須是合法的，並且需要返回一個值，這個值可以和bool互相轉化。當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
正如

```
while(!pred())
{
wait(lock);
}
```

**拋出**
pred中可以拋出任意異常，或者當效果沒有達到的時候，拋出`std::system_error`異常。

**NOTE**:潛在的偽喚醒意味著不會指定pred調用的次數。通過lock進行上鎖，pred經常會被互斥量引用所調用，並且函數必須返回(只能返回)一個值，在`(bool)pred()`評估後，返回true。

**同步**
`std::condition_variable_any`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::wait_for 成員函數

`std::condition_variable_any`在調用notify_one()、調用notify_all()、超時或線程偽喚醒時，結束等待。

**聲明**

```
template<typename Lockable,typename Rep,typename Period>
std::cv_status wait_for(
    Lockable& lock,
    std::chrono::duration<Rep,Period> const& relative_time);
```

**先決條件**
當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
當其他線程調用notify_one()或notify_all()函數時，或超出了relative_time的時間，亦或是線程被偽喚醒，則將lock對象自動解鎖，並將阻塞線程喚醒。當wait_for()調用返回前，lock對象會再次上鎖。

**返回**
線程被notify_one()、notify_all()或偽喚醒喚醒時，會返回`std::cv_status::no_timeout`；反之，則返回std::cv_status::timeout。

**拋出**
當效果沒有達成的時候，會拋出`std::system_error`異常。當lock對象在調用wait_for()函數前解鎖，那麼lock對象會在wait_for()退出前再次上鎖，即使函數是以異常的方式退出。

**NOTE**:偽喚醒意味著，一個線程在調用wait_for()的時候，即使沒有其他線程調用notify_one()和notify_all()函數，也處於甦醒狀態。因此，這裡建議重載wait_for()函數，重載函數可以使用謂詞。要不，則建議wait_for()使用循環的方式對與謂詞相關的條件變量進行檢查。在這樣做的時候還需要小心，以確保超時部分依舊有效；wait_until()可能適合更多的情況。這樣的話，線程阻塞的時間就要比指定的時間長了。在有這樣可能性的地方，流逝的時間是由穩定時鐘決定。

**同步**
`std::condition_variable_any`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::wait_for 需要一個謂詞的成員函數重載

`std::condition_variable_any`在調用notify_one()、調用notify_all()、超時或線程偽喚醒時，結束等待。

**聲明**

```
template<typename Lockable,typename Rep,
    typename Period, typename Predicate>
bool wait_for(
    Lockable& lock,
    std::chrono::duration<Rep,Period> const& relative_time,
    Predicate pred);
```

**先決條件**
pred()謂詞必須是合法的，並且需要返回一個值，這個值可以和bool互相轉化。當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
正如

```
internal_clock::time_point end=internal_clock::now()+relative_time;
while(!pred())
{
  std::chrono::duration<Rep,Period> remaining_time=
      end-internal_clock::now();
  if(wait_for(lock,remaining_time)==std::cv_status::timeout)
      return pred();
}
return true;
```

**返回**
當pred()為true，則返回true；當超過relative_time並且pred()返回false時，返回false。

**NOTE**:
潛在的偽喚醒意味著不會指定pred調用的次數。通過lock進行上鎖，pred經常會被互斥量引用所調用，並且函數必須返回(只能返回)一個值，在(bool)pred()評估後返回true，或在指定時間relative_time內完成。線程阻塞的時間就要比指定的時間長了。在有這樣可能性的地方，流逝的時間是由穩定時鐘決定。

**拋出**
當效果沒有達成時，會拋出`std::system_error`異常或者由pred拋出任意異常。

**同步**
`std::condition_variable_any`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::wait_until 成員函數

`std::condition_variable_any`在調用notify_one()、調用notify_all()、指定時間內達成條件或線程偽喚醒時，結束等待

**聲明**

```
template<typename Lockable,typename Clock,typename Duration>
std::cv_status wait_until(
    Lockable& lock,
    std::chrono::time_point<Clock,Duration> const& absolute_time);
```

**先決條件**
Lockable類型需要能夠上鎖，lock對象擁有一個鎖。

**效果**
當其他線程調用notify_one()或notify_all()函數，或Clock::now()返回一個大於或等於absolute_time的時間，亦或線程偽喚醒，lock都將自動解鎖，並且喚醒阻塞的線程。在wait_until()返回之前lock對象會再次上鎖。

**返回**
線程被notify_one()、notify_all()或偽喚醒喚醒時，會返回std::cv_status::no_timeout；反之，則返回`std::cv_status::timeout`。

**拋出**
當效果沒有達成的時候，會拋出`std::system_error`異常。當lock對象在調用wait_for()函數前解鎖，那麼lock對象會在wait_for()退出前再次上鎖，即使函數是以異常的方式退出。

**NOTE**:偽喚醒意味著一個線程調用wait()後，在沒有其他線程調用notify_one()或notify_all()時，還處以甦醒狀態。因此，這裡建議重載wait_until()函數，重載函數可以使用謂詞。要不，則建議wait_until()使用循環的方式對與謂詞相關的條件變量進行檢查。這裡不保證線程會被阻塞多長時間，只有當函數返回false後(Clock::now()的返回值大於或等於absolute_time)，線程才能解除阻塞。

**同步**
`std::condition_variable_any`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。

### std::condition_variable_any::wait_unti 需要一個謂詞的成員函數重載

`std::condition_variable_any`在調用notify_one()、調用notify_all()、謂詞返回true或指定時間內達到條件，結束等待。

**聲明**

```
template<typename Lockable,typename Clock,
    typename Duration, typename Predicate>
bool wait_until(
    Lockable& lock,
    std::chrono::time_point<Clock,Duration> const& absolute_time,
    Predicate pred);
```

**先決條件**
pred()必須是合法的，並且其返回值能轉換為bool值。當線程調用wait()即可獲得鎖的所有權,lock.owns_lock()必須為true。

**效果**
等價於

```
while(!pred())
{
  if(wait_until(lock,absolute_time)==std::cv_status::timeout)
    return pred();
}
return true;
```

**返回**
當調用pred()返回true時，返回true；當Clock::now()的時間大於或等於指定的時間absolute_time，並且pred()返回false時，返回false。

**NOTE**：潛在的偽喚醒意味著不會指定pred調用的次數。通過lock進行上鎖，pred經常會被互斥量引用所調用，並且函數必須返回(只能返回)一個值，在(bool)pred()評估後返回true，或Clock::now()返回的時間大於或等於absolute_time。這裡不保證調用線程將被阻塞的時長，只有當函數返回false後(Clock::now()返回一個等於或大於absolute_time的值)，線程接觸阻塞。

**拋出**
當效果沒有達成時，會拋出`std::system_error`異常或者由pred拋出任意異常。

**同步**
`std::condition_variable_any`實例中的notify_one(),notify_all(),wait(),wait_for()和wait_until()都是序列化函數(串行調用)。調用notify_one()或notify_all()只能喚醒正在等待中的線程。