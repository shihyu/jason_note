# D.1 &lt;chrono&gt;頭文件

&lt;chrono&gt;頭文件作為`time_point`的提供者，具有代表時間點的類，duration類和時鐘類。每個時鐘都有一個`is_steady`靜態數據成員，這個成員用來表示該時鐘是否是一個*穩定的*時鐘(以勻速計時的時鐘，且不可調節)。`std::chrono::steady_clock`是唯一個能保證穩定的時鐘類。

頭文件正文

```c++
namespace std
{
  namespace chrono
  {
    template<typename Rep,typename Period = ratio<1>>
    class duration;
    template<
        typename Clock,
        typename Duration = typename Clock::duration>
    class time_point;
    class system_clock;
    class steady_clock;
    typedef unspecified-clock-type high_resolution_clock;
  }
}
```

## D.1.1 std::chrono::duration類型模板

`std::chrono::duration`類模板可以用來表示時間。模板參數`Rep`和`Period`是用來存儲持續時間的數據類型，`std::ratio`實例代表了時間的長度(幾分之一秒)，其表示了在兩次“時鐘滴答”後的時間(時鐘週期)。因此，`std::chrono::duration<int, std::milli>`即為，時間以毫秒數的形式存儲到int類型中，而`std::chrono::duration<short, std::ratio<1,50>>`則是記錄1/50秒的個數，並將個數存入short類型的變量中，還有`std::chrono::duration <long long, std::ratio<60,1>>`則是將分鐘數存儲到long long類型的變量中。

### 類的定義

```c++
template <class Rep, class Period=ratio<1> >
class duration
{
public:
  typedef Rep rep;
  typedef Period period;

  constexpr duration() = default;
  ~duration() = default;

  duration(const duration&) = default;
  duration& operator=(const duration&) = default;

  template <class Rep2>
  constexpr explicit duration(const Rep2& r);

  template <class Rep2, class Period2>
  constexpr duration(const duration<Rep2, Period2>& d);

  constexpr rep count() const;
  constexpr duration operator+() const;
  constexpr duration operator-() const;

  duration& operator++();
  duration operator++(int);
  duration& operator--();
  duration operator--(int);

  duration& operator+=(const duration& d);
  duration& operator-=(const duration& d);
  duration& operator*=(const rep& rhs);
  duration& operator/=(const rep& rhs);

  duration& operator%=(const rep& rhs);
  duration& operator%=(const duration& rhs);

  static constexpr duration zero();
  static constexpr duration min();
  static constexpr duration max();
};

template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator==(
    const duration<Rep1, Period1>& lhs,
    const duration<Rep2, Period2>& rhs);

template <class Rep1, class Period1, class Rep2, class Period2>
    constexpr bool operator!=(
    const duration<Rep1, Period1>& lhs,
    const duration<Rep2, Period2>& rhs);

template <class Rep1, class Period1, class Rep2, class Period2>
    constexpr bool operator<(
    const duration<Rep1, Period1>& lhs,
    const duration<Rep2, Period2>& rhs);

template <class Rep1, class Period1, class Rep2, class Period2>
    constexpr bool operator<=(
    const duration<Rep1, Period1>& lhs,
    const duration<Rep2, Period2>& rhs);

template <class Rep1, class Period1, class Rep2, class Period2>
    constexpr bool operator>(
    const duration<Rep1, Period1>& lhs,
    const duration<Rep2, Period2>& rhs);

template <class Rep1, class Period1, class Rep2, class Period2>
    constexpr bool operator>=(
    const duration<Rep1, Period1>& lhs,
    const duration<Rep2, Period2>& rhs);

template <class ToDuration, class Rep, class Period>
    constexpr ToDuration duration_cast(const duration<Rep, Period>& d);
```

**要求**

`Rep`必須是內置數值類型，或是自定義的類數值類型。

`Period`必須是`std::ratio<>`實例。

### std::chrono::duration::Rep 類型

用來記錄`dration`中時鐘週期的數量。

**聲明**

```c++
typedef Rep rep;
```

`rep`類型用來記錄`duration`對象內部的表示。

### std::chrono::duration::Period 類型

這個類型必須是一個`std::ratio`特化實例，用來表示在繼續時間中，1s所要記錄的次數。例如，當`period`是`std::ratio<1, 50>`，`duration`變量的count()就會在N秒鐘返回50N。

**聲明**

```c++
typedef Period period;
```

### std::chrono::duration 默認構造函數

使用默認值構造`std::chrono::duration`實例

**聲明**

```c++
constexpr duration() = default;
```

**效果**
`duration`內部值(例如`rep`類型的值)都已初始化。

### std::chrono::duration 需要計數值的轉換構造函數

通過給定的數值來構造`std::chrono::duration`實例。

**聲明**

```c++
template <class Rep2>;
constexpr explicit duration(const Rep2& r);
```

**效果**

`duration`對象的內部值會使用`static_cast<rep>(r)`進行初始化。

**結果**
當Rep2隱式轉換為Rep，Rep是浮點類型或Rep2不是浮點類型，這個構造函數才能使用。

**後驗條件**

```c++
this->count()==static_cast<rep>(r)
```

### std::chrono::duration 需要另一個std::chrono::duration值的轉化構造函數

通過另一個`std::chrono::duration`類實例中的計數值來構造一個`std::chrono::duration`類實例。

**聲明**

```c++
template <class Rep2, class Period>
constexpr duration(const duration<Rep2,Period2>& d);
```

**結果**

duration對象的內部值通過`duration_cast<duration<Rep,Period>>(d).count()`初始化。

**要求**

當Rep是一個浮點類或Rep2不是浮點類，且Period2是Period數的倍數(比如，ratio_divide&lt;Period2,Period&gt;::den==1)時，才能調用該重載。當一個較小的數據轉換為一個較大的數據時，使用該構造函數就能避免數位截斷和精度損失。

**後驗條件**

`this->count() == dutation_cast&lt;duration<Rep, Period>>(d).count()`

**例子**

```c++
duration<int, ratio<1, 1000>> ms(5);  // 5毫秒
duration<int, ratio<1, 1>> s(ms);  // 錯誤：不能將ms當做s進行存儲
duration<double, ratio<1,1>> s2(ms);  // 合法：s2.count() == 0.005
duration<int, ration<1, 1000000>> us<ms>;  // 合法:us.count() == 5000
```

### std::chrono::duration::count 成員函數

查詢持續時長。

**聲明**

```c++
constexpr rep count() const;
```

**返回**

返回duration的內部值，其值類型和rep一樣。

### std::chrono::duration::operator+ 加法操作符

這是一個空操作：只會返回*this的副本。

**聲明**

```c++
constexpr duration operator+() const;
```

**返回**
`*this`

### std::chrono::duration::operator- 減法操作符

返回將內部值只為負數的*this副本。

**聲明**

```c++
constexpr duration operator-() const;
```

**返回**
`duration(--this->count());`

### std::chrono::duration::operator++ 前置自加操作符

增加內部計數值。

**聲明**

```c++
duration& operator++();
```

**結果**

```c++
++this->internal_count;
```

**返回**
`*this`

### std::chrono::duration::operator++ 後置自加操作符

自加內部計數值，並且返回還沒有增加前的*this。

**聲明**

```c++
duration operator++(int);
```

**結果**

```c++
duration temp(*this);
++(*this);
return temp;
```

### std::chrono::duration::operator-- 前置自減操作符

自減內部計數值

**聲明**

```c++
duration& operator--();
```

**結果**

```c++
--this->internal_count;
```

**返回**
`*this`

### std::chrono::duration::operator-- 前置自減操作符

自減內部計數值，並且返回還沒有減少前的*this。

**聲明**

```c++
duration operator--(int);
```

**結果**

```c++
duration temp(*this);
--(*this);
return temp;
```

### std::chrono::duration::operator+= 複合賦值操作符

將其他duration對象中的內部值增加到現有duration對象當中。

**聲明**

```c++
duration& operator+=(duration const& other);
```

**結果**

```c++
internal_count+=other.count();
```

**返回**
`*this`

### std::chrono::duration::operator-= 複合賦值操作符

現有duration對象減去其他duration對象中的內部值。

**聲明**

```c++
duration& operator-=(duration const& other);
```

**結果**

```c++
internal_count-=other.count();
```

**返回**
`*this`

### std::chrono::duration::operator*= 複合賦值操作符

內部值乘以一個給定的值。

**聲明**

```c++
duration& operator*=(rep const& rhs);
```

**結果**

```c++
internal_count*=rhs;
```

**返回**
`*this`

### std::chrono::duration::operator/= 複合賦值操作符

內部值除以一個給定的值。

**聲明**

```c++
duration& operator/=(rep const& rhs);
```

**結果**

```c++
internal_count/=rhs;
```

**返回**
`*this`

### std::chrono::duration::operator%= 複合賦值操作符

內部值對一個給定的值求餘。

**聲明**

```c++
duration& operator%=(rep const& rhs);
```

**結果**

```c++
internal_count%=rhs;
```

**返回**
`*this`

### std::chrono::duration::operator%= 複合賦值操作符(重載)

內部值對另一個duration類的內部值求餘。

**聲明**

```c++
duration& operator%=(duration const& rhs);
```

**結果**

```c++
internal_count%=rhs.count();
```

**返回**
`*this`

### std::chrono::duration::zero 靜態成員函數

返回一個內部值為0的duration對象。

**聲明**

```c++
constexpr duration zero();
```

**返回**

```c++
duration(duration_values<rep>::zero());
```

### std::chrono::duration::min 靜態成員函數

返回duration類實例化後能表示的最小值。

**聲明**

```c++
constexpr duration min();
```

**返回**

```c++
duration(duration_values<rep>::min());
```

### std::chrono::duration::max 靜態成員函數

返回duration類實例化後能表示的最大值。

**聲明**

```c++
constexpr duration max();
```

**返回**

```c++
duration(duration_values<rep>::max());
```

### std::chrono::duration 等於比較操作符

比較兩個duration對象是否相等。

**聲明**

```c++
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator==(
const duration<Rep1, Period1>& lhs,
const duration<Rep2, Period2>& rhs);
```

**要求**

`lhs`和`rhs`兩種類型可以互相進行隱式轉換。當兩種類型無法進行隱式轉換，或是可以互相轉換的兩個不同類型的duration類，則表達式不合理。

**結果**

當`CommonDuration`和`std::common_type< duration< Rep1, Period1>, duration< Rep2, Period2>>::type`同類，那麼`lhs==rhs`就會返回`CommonDuration(lhs).count()==CommonDuration(rhs).count()`。

### std::chrono::duration 不等於比較操作符

比較兩個duration對象是否不相等。

**聲明**

```c++
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator!=(
   const duration<Rep1, Period1>& lhs,
   const duration<Rep2, Period2>& rhs);
```

**要求**

`lhs`和`rhs`兩種類型可以互相進行隱式轉換。當兩種類型無法進行隱式轉換，或是可以互相轉換的兩個不同類型的duration類，則表達式不合理。

**返回**
`!(lhs==rhs)`

### std::chrono::duration 小於比較操作符

比較兩個duration對象是否小於。

**聲明**

```c++
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator<(
   const duration<Rep1, Period1>& lhs,
   const duration<Rep2, Period2>& rhs);
```

**要求**

`lhs`和`rhs`兩種類型可以互相進行隱式轉換。當兩種類型無法進行隱式轉換，或是可以互相轉換的兩個不同類型的duration類，則表達式不合理。

**結果**

當`CommonDuration`和`std::common_type< duration< Rep1, Period1>, duration< Rep2, Period2>>::type`同類，那麼`lhs&lt;rhs`就會返回`CommonDuration(lhs).count()&lt;CommonDuration(rhs).count()`。

### std::chrono::duration 大於比較操作符

比較兩個duration對象是否大於。

**聲明**

```c++
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator>(
   const duration<Rep1, Period1>& lhs,
   const duration<Rep2, Period2>& rhs);
```

**要求**

`lhs`和`rhs`兩種類型可以互相進行隱式轉換。當兩種類型無法進行隱式轉換，或是可以互相轉換的兩個不同類型的duration類，則表達式不合理。

**返回**
`rhs<lhs`

### std::chrono::duration 小於等於比較操作符

比較兩個duration對象是否小於等於。

**聲明**

```c++
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator<=(
   const duration<Rep1, Period1>& lhs,
   const duration<Rep2, Period2>& rhs);
```

**要求**

`lhs`和`rhs`兩種類型可以互相進行隱式轉換。當兩種類型無法進行隱式轉換，或是可以互相轉換的兩個不同類型的duration類，則表達式不合理。

**返回**
`!(rhs<lhs)`

### std::chrono::duration 大於等於比較操作符

比較兩個duration對象是否大於等於。

**聲明**

```c++
template <class Rep1, class Period1, class Rep2, class Period2>
constexpr bool operator>=(
   const duration<Rep1, Period1>& lhs,
   const duration<Rep2, Period2>& rhs);
```

**要求**

`lhs`和`rhs`兩種類型可以互相進行隱式轉換。當兩種類型無法進行隱式轉換，或是可以互相轉換的兩個不同類型的duration類，則表達式不合理。

**返回**
`!(lhs<rhs)`

### std::chrono::duration_cast 非成員函數

顯示將一個`std::chrono::duration`對象轉化為另一個`std::chrono::duration`實例。

**聲明**

```c++
template <class ToDuration, class Rep, class Period>
constexpr ToDuration duration_cast(const duration<Rep, Period>& d);
```

**要求**

ToDuration必須是`std::chrono::duration`的實例。

**返回**

duration類d轉換為指定類型ToDuration。這種方式可以在不同尺寸和表示類型的轉換中儘可能減少精度損失。

## D.1.2 std::chrono::time_point類型模板

`std::chrono::time_point`類型模板通過(特別的)時鐘來表示某個時間點。這個時鐘代表的是從epoch(1970-01-01 00:00:00 UTC，作為UNIX系列系統的特定時間戳)到現在的時間。模板參數Clock代表使用的使用(不同的使用必定有自己獨特的類型)，而Duration模板參數使用來測量從epoch到現在的時間，並且這個參數的類型必須是`std::chrono::duration`類型。Duration默認存儲Clock上的測量值。

### 類型定義

```c++
template <class Clock,class Duration = typename Clock::duration>
class time_point
{
public:
  typedef Clock clock;
  typedef Duration duration;
  typedef typename duration::rep rep;
  typedef typename duration::period period;
  
  time_point();
  explicit time_point(const duration& d);

  template <class Duration2>
  time_point(const time_point<clock, Duration2>& t);

  duration time_since_epoch() const;
  
  time_point& operator+=(const duration& d);
  time_point& operator-=(const duration& d);
  
  static constexpr time_point min();
  static constexpr time_point max();
};
```

### std::chrono::time_point 默認構造函數

構造time_point代表著，使用相關的Clock，記錄從epoch到現在的時間；其內部計時使用Duration::zero()進行初始化。

**聲明**

```c++
time_point();
```

**後驗條件**

對於使用默認構造函數構造出的time_point對象tp，`tp.time_since_epoch() == tp::duration::zero()`。

### std::chrono::time_point 需要時間長度的構造函數

構造time_point代表著，使用相關的Clock，記錄從epoch到現在的時間。

**聲明**

```c++
explicit time_point(const duration& d);
```

**後驗條件**

當有一個time_point對象tp，是通過duration d構造出來的(tp(d))，那麼`tp.time_since_epoch() == d`。

### std::chrono::time_point 轉換構造函數

構造time_point代表著，使用相關的Clock，記錄從epoch到現在的時間。

**聲明**

```c++
template <class Duration2>
time_point(const time_point<clock, Duration2>& t);
```

**要求**

Duration2必須呢個隱式轉換為Duration。

**效果**

當`time_point(t.time_since_epoch())`存在，從t.time_since_epoch()中獲取的返回值，可以隱式轉換成Duration類型的對象，並且這個值可以存儲在一個新的time_point對象中。

(擴展閱讀：[as-if準則](http://stackoverflow.com/questions/15718262/what-exactly-is-the-as-if-rule))

### std::chrono::time_point::time_since_epoch 成員函數

返回當前time_point從epoch到現在的具體時長。

**聲明**

```c++
duration time_since_epoch() const;
```

**返回**

duration的值存儲在*this中。

### std::chrono::time_point::operator+= 複合賦值函數

將指定的duration的值與原存儲在指定的time_point對象中的duration相加，並將加後值存儲在*this對象中。

**聲明**

```c++
time_point& operator+=(const duration& d);
```

**效果**

將d的值和duration對象的值相加，存儲在*this中，就如同this-&gt;internal_duration += d;

**返回**
`*this`

### std::chrono::time_point::operator-= 複合賦值函數

將指定的duration的值與原存儲在指定的time_point對象中的duration相減，並將加後值存儲在*this對象中。

**聲明**

```c++
time_point& operator-=(const duration& d);
```

**效果**

將d的值和duration對象的值相減，存儲在*this中，就如同this-&gt;internal_duration -= d;

**返回**
`*this`

### std::chrono::time_point::min 靜態成員函數

獲取time_point對象可能表示的最小值。

**聲明**

```c++
static constexpr time_point min();
```

**返回**

```c++
time_point(time_point::duration::min()) (see 11.1.1.15)
```

### std::chrono::time_point::max 靜態成員函數

獲取time_point對象可能表示的最大值。

**聲明**

```c++
static constexpr time_point max();
```

**返回**

```c++
time_point(time_point::duration::max()) (see 11.1.1.16)
```

##D.1.3 std::chrono::system_clock類

`std::chrono::system_clock`類提供給了從系統實時時鐘上獲取當前時間功能。可以調用`std::chrono::system_clock::now()`來獲取當前的時間。`std::chrono::system_clock::time_point`也可以通過`std::chrono::system_clock::to_time_t()`和`std::chrono::system_clock::to_time_point()`函數返回值轉換成time_t類型。系統時鐘不穩定，所以`std::chrono::system_clock::now()`獲取到的時間可能會早於之前的一次調用(比如，時鐘被手動調整過或與外部時鐘進行了同步)。

###類型定義

```c++
class system_clock
{
public:
  typedef unspecified-integral-type rep;
  typedef std::ratio<unspecified,unspecified> period;
  typedef std::chrono::duration<rep,period> duration;
  typedef std::chrono::time_point<system_clock> time_point;
  static const bool is_steady=unspecified;

  static time_point now() noexcept;

  static time_t to_time_t(const time_point& t) noexcept;
  static time_point from_time_t(time_t t) noexcept;
};
```

### std::chrono::system_clock::rep 類型定義

將時間週期數記錄在一個duration值中

**聲明**

```c++
typedef unspecified-integral-type rep;
```

### std::chrono::system_clock::period 類型定義

類型為`std::ratio`類型模板，通過在兩個不同的duration或time_point間特化最小秒數(或將1秒分為好幾份)。period指定了時鐘的精度，而非時鐘頻率。

**聲明**

```c++
typedef std::ratio<unspecified,unspecified> period;
```

### std::chrono::system_clock::duration 類型定義

類型為`std::ratio`類型模板，通過系統實時時鐘獲取兩個時間點之間的時長。

**聲明**

```c++
typedef std::chrono::duration<
   std::chrono::system_clock::rep,
   std::chrono::system_clock::period> duration;
```

### std::chrono::system_clock::time_point 類型定義

類型為`std::ratio`類型模板，通過系統實時時鐘獲取當前時間點的時間。

**聲明**

```c++
typedef std::chrono::time_point&lt;std::chrono::system_clock&gt; time_point;
```

### std::chrono::system_clock::now 靜態成員函數

從系統實時時鐘上獲取當前的外部設備顯示的時間。

**聲明**

```c++
time_point now() noexcept;
```

**返回**

time_point類型變量來代表當前系統實時時鐘的時間。

**拋出**

當錯誤發生，`std::system_error`異常將會拋出。

### std::chrono::system_clock:to_time_t 靜態成員函數

將time_point類型值轉化為time_t。

**聲明**

```c++
time_t to_time_t(time_point const& t) noexcept;
```

**返回**

通過對t進行舍入或截斷精度，將其轉化為一個time_t類型的值。

**拋出**

當錯誤發生，`std::system_error`異常將會拋出。

### std::chrono::system_clock::from_time_t 靜態成員函數

**聲明**

```c++
time_point from_time_t(time_t const& t) noexcept;
```

**返回**

time_point中的值與t中的值一樣。

**拋出**

當錯誤發生，`std::system_error`異常將會拋出。

## D.1.4 std::chrono::steady_clock類

`std::chrono::steady_clock`能訪問系統穩定時鐘。可以通過調用`std::chrono::steady_clock::now()`獲取當前的時間。設備上顯示的時間，與使用`std::chrono::steady_clock::now()`獲取的時間沒有固定的關係。穩定時鐘是無法回調的，所以在`std::chrono::steady_clock::now()`兩次調用後，第二次調用獲取的時間必定等於或大於第一次獲得的時間。

### 類型定義

```c++
class steady_clock
{
public:
  typedef unspecified-integral-type rep;
  typedef std::ratio<
      unspecified,unspecified> period;
  typedef std::chrono::duration<rep,period> duration;
  typedef std::chrono::time_point<steady_clock>
      time_point;
  static const bool is_steady=true;

  static time_point now() noexcept;
};
```

### std::chrono::steady_clock::rep 類型定義

定義一個整型，用來保存duration的值。

**聲明**

```c++
typedef unspecified-integral-type rep;
```

### std::chrono::steady_clock::period 類型定義

類型為`std::ratio`類型模板，通過在兩個不同的duration或time_point間特化最小秒數(或將1秒分為好幾份)。period指定了時鐘的精度，而非時鐘頻率。

**聲明**

```c++
typedef std::ratio<unspecified,unspecified> period;
```

### std::chrono::steady_clock::duration 類型定義

類型為`std::ratio`類型模板，通過系統實時時鐘獲取兩個時間點之間的時長。

**聲明**

```c++
typedef std::chrono::duration<
   std::chrono::system_clock::rep,
   std::chrono::system_clock::period> duration;
```

### std::chrono::steady_clock::time_point 類型定義

`std::chrono::time_point`類型實例，可以存儲從系統穩定時鐘返回的時間點。

**聲明**

```c++
typedef std::chrono::time_point<std::chrono::steady_clock> time_point;
```

### std::chrono::steady_clock::now 靜態成員函數

從系統穩定時鐘獲取當前時間。

**聲明**

```c++
time_point now() noexcept;
```

**返回**

time_point表示當前系統穩定時鐘的時間。

**拋出**
當遇到錯誤，會拋出`std::system_error`異常。

**同步**
當先行調用過一次`std::chrono::steady_clock::now()`，那麼下一次time_point獲取的值，一定大於等於第一次獲取的值。

## D.1.5 std::chrono::high_resolution_clock類定義

`td::chrono::high_resolution_clock`類能訪問系統高精度時鐘。和所有其他時鐘一樣，通過調用`std::chrono::high_resolution_clock::now()`來獲取當前時間。`std::chrono::high_resolution_clock`可能是`std::chrono::system_clock`類或`std::chrono::steady_clock`類的別名，也可能就是獨立的一個類。

通過`std::chrono::high_resolution_clock`具有所有標準庫支持時鐘中最高的精度，這就意味著使用
`std::chrono::high_resolution_clock::now()`要花掉一些時間。所以，當你再調用`std::chrono::high_resolution_clock::now()`的時候，需要注意函數本身的時間開銷。

### 類型定義

```c++
class high_resolution_clock
{
public:
  typedef unspecified-integral-type rep;
  typedef std::ratio<
      unspecified,unspecified> period;
  typedef std::chrono::duration<rep,period> duration;
  typedef std::chrono::time_point<
      unspecified> time_point;
  static const bool is_steady=unspecified;

  static time_point now() noexcept;
};
```