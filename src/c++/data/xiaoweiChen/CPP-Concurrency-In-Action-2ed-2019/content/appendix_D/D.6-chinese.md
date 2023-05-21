# D.6 &lt;ratio&gt;頭文件

`<ratio>`頭文件提供在編譯時進行的計算。

**頭文件內容**

```
namespace std
{
  template<intmax_t N,intmax_t D=1>
  class ratio;

  // ratio arithmetic
  template <class R1, class R2>
  using ratio_add = see description;

  template <class R1, class R2>
  using ratio_subtract = see description;

  template <class R1, class R2>
  using ratio_multiply = see description;

  template <class R1, class R2>
  using ratio_divide = see description;

  // ratio comparison
  template <class R1, class R2>
  struct ratio_equal;

  template <class R1, class R2>
  struct ratio_not_equal;

  template <class R1, class R2>
  struct ratio_less;

  template <class R1, class R2>
  struct ratio_less_equal;

  template <class R1, class R2>
  struct ratio_greater;

  template <class R1, class R2>
  struct ratio_greater_equal;

  typedef ratio<1, 1000000000000000000> atto;
  typedef ratio<1, 1000000000000000> femto;
  typedef ratio<1, 1000000000000> pico;
  typedef ratio<1, 1000000000> nano;
  typedef ratio<1, 1000000> micro;
  typedef ratio<1, 1000> milli;
  typedef ratio<1, 100> centi;
  typedef ratio<1, 10> deci;
  typedef ratio<10, 1> deca;
  typedef ratio<100, 1> hecto;
  typedef ratio<1000, 1> kilo;
  typedef ratio<1000000, 1> mega;
  typedef ratio<1000000000, 1> giga;
  typedef ratio<1000000000000, 1> tera;
  typedef ratio<1000000000000000, 1> peta;
  typedef ratio<1000000000000000000, 1> exa;
}
```

##D.6.1 std::ratio類型模板

`std::ratio`類型模板提供了一種對在編譯時進行計算的機制，通過調用合理的數，例如：半(`std::ratio<1,2>`),2/3(std::ratio<2, 3>)或15/43(std::ratio<15, 43>)。其使用在C++標準庫內部，用於初始化`std::chrono::duration`類型模板。

**類型定義**

```
template <intmax_t N, intmax_t D = 1>
class ratio
{
public:
  typedef ratio<num, den> type;
  static constexpr intmax_t num= see below;
  static constexpr intmax_t den= see below;
};
```

**要求**
D不能為0。

**描述**
num和den分別為分子和分母，構造分數N/D。den總是正數。當N和D的符號相同，那麼num為正數；否則num為負數。

**例子**

```
ratio<4,6>::num == 2
ratio<4,6>::den == 3
ratio<4,-6>::num == -2
ratio<4,-6>::den == 3
```

## D.6.2 std::ratio_add模板別名

`std::ratio_add`模板別名提供了兩個`std::ratio`在編譯時相加的機制(使用有理計算)。

**定義**

```
template <class R1, class R2>
using ratio_add = std::ratio<see below>;
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**效果**
ratio_add<R1, R2>被定義為一個別名，如果兩數可以計算，且無溢出，該類型可以表示兩個`std::ratio`對象R1和R2的和。如果計算出來的結果溢出了，那麼程序裡面就有問題了。在算術溢出的情況下，`std::ratio_add<R1, R2>`應該應該與`std::ratio<R1::num * R2::den + R2::num * R1::den, R1::den * R2::den>`相同。

**例子**

```
std::ratio_add<std::ratio<1,3>, std::ratio<2,5> >::num == 11
std::ratio_add<std::ratio<1,3>, std::ratio<2,5> >::den == 15

std::ratio_add<std::ratio<1,3>, std::ratio<7,6> >::num == 3
std::ratio_add<std::ratio<1,3>, std::ratio<7,6> >::den == 2
```

## D.6.3 std::ratio_subtract模板別名

`std::ratio_subtract`模板別名提供兩個`std::ratio`數在編譯時進行相減(使用有理計算)。

**定義**

```
template <class R1, class R2>
using ratio_subtract = std::ratio<see below>;
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**效果**
ratio_add<R1, R2>被定義為一個別名，如果兩數可以計算，且無溢出，該類型可以表示兩個`std::ratio`對象R1和R2的和。如果計算出來的結果溢出了，那麼程序裡面就有問題了。在算術溢出的情況下，`std::ratio_subtract<R1, R2>`應該應該與`std::ratio<R1::num * R2::den - R2::num * R1::den, R1::den * R2::den>`相同。

**例子**

```
std::ratio_subtract<std::ratio<1,3>, std::ratio<1,5> >::num == 2
std::ratio_subtract<std::ratio<1,3>, std::ratio<1,5> >::den == 15

std::ratio_subtract<std::ratio<1,3>, std::ratio<7,6> >::num == -5
std::ratio_subtract<std::ratio<1,3>, std::ratio<7,6> >::den == 6
```

## D.6.4 std::ratio_multiply模板別名

`std::ratio_multiply`模板別名提供兩個`std::ratio`數在編譯時進行相乘(使用有理計算)。

**定義**

```
template <class R1, class R2>
using ratio_multiply = std::ratio<see below>;
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**效果**
ratio_add<R1, R2>被定義為一個別名，如果兩數可以計算，且無溢出，該類型可以表示兩個`std::ratio`對象R1和R2的和。如果計算出來的結果溢出了，那麼程序裡面就有問題了。在算術溢出的情況下，`std::ratio_multiply<R1, R2>`應該應該與`std::ratio<R1::num * R2::num, R1::den * R2::den>`相同。

**例子**

```
std::ratio_multiply<std::ratio<1,3>, std::ratio<2,5> >::num == 2
std::ratio_multiply<std::ratio<1,3>, std::ratio<2,5> >::den == 15

std::ratio_multiply<std::ratio<1,3>, std::ratio<15,7> >::num == 5
std::ratio_multiply<std::ratio<1,3>, std::ratio<15,7> >::den == 7
```

## D.6.5 std::ratio_divide模板別名

`std::ratio_divide`模板別名提供兩個`std::ratio`數在編譯時進行相除(使用有理計算)。

**定義**

```
template <class R1, class R2>
using ratio_multiply = std::ratio<see below>;
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**效果**
ratio_add<R1, R2>被定義為一個別名，如果兩數可以計算，且無溢出，該類型可以表示兩個`std::ratio`對象R1和R2的和。如果計算出來的結果溢出了，那麼程序裡面就有問題了。在算術溢出的情況下，`std::ratio_multiply<R1, R2>`應該應該與`std::ratio<R1::num * R2::num * R2::den, R1::den * R2::den>`相同。

**例子**

```
std::ratio_divide<std::ratio<1,3>, std::ratio<2,5> >::num == 5
std::ratio_divide<std::ratio<1,3>, std::ratio<2,5> >::den == 6

std::ratio_divide<std::ratio<1,3>, std::ratio<15,7> >::num == 7
std::ratio_divide<std::ratio<1,3>, std::ratio<15,7> >::den == 45
```

## D.6.6 std::ratio_equal類型模板

`std::ratio_equal`類型模板提供在編譯時比較兩個`std::ratio`數(使用有理計算)。

**類型定義**

```
template <class R1, class R2>
class ratio_equal:
  public std::integral_constant<
    bool,(R1::num == R2::num) && (R1::den == R2::den)>
{};
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**例子**

```
std::ratio_equal<std::ratio<1,3>, std::ratio<2,6> >::value == true
std::ratio_equal<std::ratio<1,3>, std::ratio<1,6> >::value == false
std::ratio_equal<std::ratio<1,3>, std::ratio<2,3> >::value == false
std::ratio_equal<std::ratio<1,3>, std::ratio<1,3> >::value == true
```

## D.6.7 std::ratio_not_equal類型模板

`std::ratio_not_equal`類型模板提供在編譯時比較兩個`std::ratio`數(使用有理計算)。

**類型定義**

```
template <class R1, class R2>
class ratio_not_equal:
  public std::integral_constant<bool,!ratio_equal<R1,R2>::value>
{};
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**例子**

```
std::ratio_not_equal<std::ratio<1,3>, std::ratio<2,6> >::value == false
std::ratio_not_equal<std::ratio<1,3>, std::ratio<1,6> >::value == true
std::ratio_not_equal<std::ratio<1,3>, std::ratio<2,3> >::value == true
std::ratio_not_equal<std::ratio<1,3>, std::ratio<1,3> >::value == false
```

## D.6.8 std::ratio_less類型模板

`std::ratio_less`類型模板提供在編譯時比較兩個`std::ratio`數(使用有理計算)。

**類型定義**

```
template <class R1, class R2>
class ratio_less:
  public std::integral_constant<bool,see below>
{};
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

**效果**
std::ratio_less<R1,R2>可通過`std::integral_constant<bool, value >`導出，這裡value為`(R1::num*R2::den) < (R2::num*R1::den)`。如果有可能，需要實現使用一種機制來避免計算結果已出。當溢出發生，那麼程序中就肯定有錯誤。

**例子**

```
std::ratio_less<std::ratio<1,3>, std::ratio<2,6> >::value == false
std::ratio_less<std::ratio<1,6>, std::ratio<1,3> >::value == true
std::ratio_less<
  std::ratio<999999999,1000000000>,
  std::ratio<1000000001,1000000000> >::value == true
std::ratio_less<
  std::ratio<1000000001,1000000000>,
  std::ratio<999999999,1000000000> >::value == false
```

## D.6.9 std::ratio_greater類型模板

`std::ratio_greater`類型模板提供在編譯時比較兩個`std::ratio`數(使用有理計算)。

**類型定義**

```
template <class R1, class R2>
class ratio_greater:
  public std::integral_constant<bool,ratio_less<R2,R1>::value>
{};
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

## D.6.10 std::ratio_less_equal類型模板

`std::ratio_less_equal`類型模板提供在編譯時比較兩個`std::ratio`數(使用有理計算)。

**類型定義**

```
template <class R1, class R2>
class ratio_less_equal:
  public std::integral_constant<bool,!ratio_less<R2,R1>::value>
{};
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。

## D.6.11 std::ratio_greater_equal類型模板

`std::ratio_greater_equal`類型模板提供在編譯時比較兩個`std::ratio`數(使用有理計算)。

**類型定義**

```
template <class R1, class R2>
class ratio_greater_equal:
  public std::integral_constant<bool,!ratio_less<R1,R2>::value>
{};
```

**先決條件**
R1和R2必須使用`std::ratio`進行初始化。