# 構造函數自動推導模板的類型

C++中很多類都需要指定類型，其實這個類型可以從用戶所調用的構造函數中推導出來。不過，在C++17之前，這是一個未標準化的特性。C++17能讓編譯器自動的從所調用的構造函數，推導出模板類型。

## How to do it...

使用最簡單的方法創建`std::pair`和`std::tuple`實例。其可以實現一步創建。

```c++
std::pair my_pair (123, "abc"); // std::pair<int, const char*>
std::tuple my_tuple (123, 12.3, "abc"); // std::tuple<int, double, const char*>
```

## How it works...

讓我們定義一個類，瞭解自動化的對模板類型進行推斷的價值。

```c++
template <typename T1, typename T2, typename T3>
class my_wrapper {
  T1 t1;
  T2 t2;
  T3 t3;
public:
  explicit my_wrapper(T1 t1_, T2 t2_, T3 t3_)
  : t1{t1_}, t2{t2_}, t3{t3_}
  {}
/* ... */
};
```

好！我們定義了一個模板類。C++17之前，我們為了創建該類的實例：

```c++
my_wrapper<int, double, const char *> wrapper {123, 1.23, "abc"};
```

我們省略模板特化的部分：

```c++
my_wrapper wrapper {123, 1.23, "abc"};
```

C++17之前，我們可能會通過以下的方式實現一個工廠函數：

```c++
my_wrapper<T1, T2, T3> make_wrapper(T1 t1, T2 t2, T3 t3)
{
  return {t1, t2, t3};
}
```

使用工廠函數：

```c++
auto wrapper (make_wrapper(123, 1.23, "abc"));
```

> Note:
>
> STL中有很多工廠函數，比如`std::make_shared`、`std::make_unique`、`std::make_tuple`等等。C++17中，這些工廠函數就過時了。當然，考慮到兼容性，這些工廠函數在之後還會保留。



## There's more...

我們已經瞭解過*隱式模板類型推導*。但一些例子中，不能依賴類型推導。如下面的例子：

```c++
// example class
template <typename T>
struct sum{
    T value;
    
    template <typename ... Ts>
    sum(Ts&& ... values) : value{(values + ...)} {}
};
```

結構體中，`sum`能接受任意數量的參數，並使用摺疊表達式將它們添加到一起(本章稍後的一節中，我們將討論摺疊表達式，以便了解摺疊表達式的更多細節)。加法操作後得到的結果保存在`value`變量中。現在的問題是，`T`的類型是什麼？如果我們不顯式的進行指定，那就需要通過傳遞給構造函數的變量類型進行推導。當我們提供了多個字符串實例，其類型為`std::string`。當我們提供多個整型時，其類型就為`int`。當我們提供多個整型、浮點和雙浮點時，編譯器會確定哪種類型適合所有的值，而不丟失信息。為了實現以上的推導，我們提供了*指導性顯式推導*：

```c++
template <typename ... Ts>
sum(Ts&& ... ts) -> sum<std::common_type_t<Ts...>>;
```

指導性推導會告訴編譯器使用`std::common_type_t`的特性，其能找到適合所有值的共同類型。來看下如何使用：

```c++
sum s {1u, 2.0, 3, 4.0f};
sum string_sum {std::string{"abc"}, "def"};
std::cout << s.value << '\n'
          << string_sum.value << '\n';
```

第1行中，我們創建了一個`sum`對象，構造函數的參數類型為`unsigned`, `double`, `int`和`floa`t。`std::common_type_t`將返回`double`作為共同類型，所以我們獲得的是一個`sun<double>`實例。第2行中，我們創建了一個`std::string`實例和一個C風格的字符串。在我們的指導下，編譯器推導出這個實例的類型為`sum<std::string>`。

當我們運行這段代碼時，屏幕上會打印出10和abcdef。其中10為數值`sum`的值，abcdef為字符串`sum`的值。


