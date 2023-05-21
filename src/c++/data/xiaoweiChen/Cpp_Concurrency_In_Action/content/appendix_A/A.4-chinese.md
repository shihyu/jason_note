# A.4 常量表達式函數

整型字面值，例如42，就是常量表達式。所以，簡單的數學表達式，例如，23x2-4。可以使用其來初始化const整型變量，然後將const整型變量作為新表達的一部分：

```
const int i=23;
const int two_i=i*2;
const int four=4;
const int forty_two=two_i-four;
```

使用常量表達式創建變量也可用在其他常量表達式中，有些事只能用常量表達式去做：

- 指定數組長度：

```
int bounds=99;
int array[bounds];  // 錯誤，bounds不是一個常量表達式
const int bounds2=99;
int array2[bounds2];  // 正確，bounds2是一個常量表達式
```

- 指定非類型模板參數的值：

```
template<unsigned size>
struct test
{};
test<bounds> ia;  // 錯誤，bounds不是一個常量表達式
test<bounds2> ia2;  // 正確，bounds2是一個常量表達式
```

- 對類中static const整型成員變量進行初始化：

```
class X
{
  static const int the_answer=forty_two;
};
```

- 對內置類型進行初始化或可用於靜態初始化集合：

```
struct my_aggregate
{
  int a;
  int b;
};
static my_aggregate ma1={forty_two,123};  // 靜態初始化
int dummy=257;
static my_aggregate ma2={dummy,dummy};  // 動態初始化
```

- 靜態初始化可以避免初始化順序和條件變量的問題。

這些都不是新添加的——你可以在1998版本的C++標準中找到對應上面實例的條款。不過，新標準中常量表達式進行了擴展，並添加了新的關鍵字——`constexpr`。

`constexpr`會對功能進行修改，當參數和函數返回類型符合要求，並且實現很簡單，那麼這樣的函數就能夠被聲明為`constexpr`，這樣函數可以當做常數表達式來使用：

```
constexpr int square(int x)
{
  return x*x;
}
int array[square(5)];
```

在這個例子中，array有25個元素，因為square函數的聲明為`constexpr`。當然，這種方式可以當做常數表達式來使用，不意味著什麼情況下都是能夠自動轉換為常數表達式：

```
int dummy=4;
int array[square(dummy)];  // 錯誤，dummy不是常數表達式
```

dummy不是常數表達式，所以square(dummy)也不是——就是一個普通函數調用——所以其不能用來指定array的長度。

## A.4.1 常量表達式和自定義類型

目前為止的例子都是以內置int型展開的。不過，在新C++標準庫中，對於滿足字面類型要求的任何類型，都可以用常量表達式來表示。

要想劃分到字面類型中，需要滿足一下幾點：

- 一般的拷貝構造函數。

- 一般的析構函數。

- 所有成員變量都是非靜態的，且基類需要是一般類型。

- 必須具有一個一般的默認構造函數，或一個constexpr構造函數。

後面會了解一下constexpr構造函數。

現在，先將注意力集中在默認構造函數上，就像下面清單中的CX類一樣。

清單A.3（一般)默認構造函數的類

```
class CX
{
private:
  int a;
  int b;
public:
  CX() = default;  // 1
  CX(int a_, int b_):  // 2
    a(a_),b(b_)
  {}
  int get_a() const
  {
    return a;
  }
  int get_b() const
  {
    return b;
  }
  int foo() const
  {
    return a+b;
  }
};
```

注意，這裡顯式的聲明瞭默認構造函數①(見A.3節)，為了保存用戶定義的構造函數②。因此，這種類型符合字面類型的要求，可以將其用在常量表達式中。

可以提供一個constexpr函數來創建一個實例，例如：

```
constexpr CX create_cx()
{
  return CX();
}
```

也可以創建一個簡單的constexpr函數來拷貝參數：

```
constexpr CX clone(CX val)
{
  return val;
}
```

不過，constexpr函數只有其他constexpr函數可以進行調用。CX類中聲明成員函數和構造函數為constexpr：

```
class CX
{
private:
  int a;
  int b;
public:
  CX() = default;
  constexpr CX(int a_, int b_):
    a(a_),b(b_)
  {}
  constexpr int get_a() const  // 1
  {
    return a;
  }
  constexpr int get_b()  // 2
  {
    return b;
  }
  constexpr int foo()
  {
    return a+b;
  }
};
```

注意，const對於get_a()①來說就是多餘的，因為在使用constexpr時就為const了，所以const描述符在這裡會被忽略。

這就允許更多複雜的constexpr函數存在：

```
constexpr CX make_cx(int a)
{
  return CX(a,1);
}
constexpr CX half_double(CX old)
{
  return CX(old.get_a()/2,old.get_b()*2);
}
constexpr int foo_squared(CX val)
{
  return square(val.foo());
}
int array[foo_squared(half_double(make_cx(10)))];  // 49個元素
```

函數都很有趣，如果想要計算數組的長度或一個整型常量，就需要使用這種方式。最大的好處是常量表達式和constexpr函數會設計到用戶定義類型的對象，可以使用這些函數對這些對象進行初始化。因為常量表達式的初始化過程是靜態初始化，所以就能避免條件競爭和初始化順序的問題：

```
CX si=half_double(CX(42,19));  // 靜態初始化
```

當構造函數被聲明為constexpr，且構造函數參數是常量表達式時，那麼初始化過程就是常數初始化(可能作為靜態初始化的一部分)。隨著併發的發展，C++11標準中有一個重要的改變：允許用戶定義構造函數進行靜態初始化，就可以在初始化的時候避免條件競爭，因為靜態過程能保證初始化過程在代碼運行前進行。

特別是關於`std::mutex`(見3.2.1節)或`std::atomic<>`(見5.2.6節)，當想要使用一個全局實例來同步其他變量的訪問時，同步訪問就能避免條件競爭的發生。構造函數中，互斥量不可能產生條件競爭，因此對於`std::mutex`的默認構造函數應該被聲明為constexpr，為了保證互斥量初始化過程是一個靜態初始化過程的一部分。

## A.4.2 常量表達式對象

目前，已經瞭解了constexpr在函數上的應用。constexpr也可以用在對象上，主要是用來做判斷的；驗證對象是否是使用常量表達式，constexpr構造函數或組合常量表達式進行初始化。

且這個對象需要聲明為const：

```
constexpr int i=45;  // ok
constexpr std::string s(“hello”);  // 錯誤，std::string不是字面類型

int foo();
constexpr int j=foo();  // 錯誤，foo()沒有聲明為constexpr
```

## A.4.3 常量表達式函數的要求

將一個函數聲明為constexpr，也是有幾點要求的；當不滿足這些要求，constexpr聲明將會報編譯錯誤。

- 所有參數都必須是字面類型。

- 返回類型必須是字面類型。

- 函數體內必須有一個return。

- return的表達式需要滿足常量表達式的要求。

- 構造返回值/表達式的任何構造函數或轉換操作，都需要是constexpr。

看起來很簡單，要在內聯函數中使用到常量表達式，返回的還是個常量表達式，還不能對任何東西進行改動。constexpr函數就是無害的純潔的函數。

constexpr類成員函數，需要追加幾點要求：

- constexpr成員函數不能是虛函數。

- 對應類必須有字面類的成員。

constexpr構造函數的規則也有些不同：

- 構造函數體必須為空。

- 每一個基類必須可初始化。

- 每個非靜態數據成員都需要初始化。

- 初始化列表的任何表達式，必須是常量表達式。

- 構造函數可選擇要進行初始化的數據成員，並且基類必須有constexpr構造函數。

- 任何用於構建數據成員的構造函數和轉換操作，以及和初始化表達式相關的基類必須為constexpr。

這些條件同樣適用於成員函數，除非函數沒有返回值，也就沒有return語句。

另外，構造函數對初始化列表中的所有基類和數據成員進行初始化。一般的拷貝構造函數會隱式的聲明為constexpr。

## A.4.4 常量表達式和模板

將constexpr應用於函數模板，或一個類模板的成員函數；根據參數，如果模板的返回類型不是字面類，編譯器會忽略其常量表達式的聲明。當模板參數類型合適，且為一般inline函數，就可以將類型寫成constexpr類型的函數模板。

```
template<typename T>
constexpr T sum(T a,T b)
{
  return a+b;
}
constexpr int i=sum(3,42);  // ok，sum<int>是constexpr
std::string s=
  sum(std::string("hello"),
      std::string(" world"));  // 也行，不過sum<std::string>就不是constexpr了
```

函數需要滿足所有constexpr函數所需的條件。不能用多個constexpr來聲明一個函數，因為其是一個模板；這樣也會帶來一些編譯錯誤。
