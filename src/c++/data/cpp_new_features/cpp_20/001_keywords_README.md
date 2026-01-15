#### <h2 id="cpp_20_new_keywords">C++20新增關鍵字</h2>

##### <h4 id="char8_t">char8_t</h4>

char8_t - UTF-8 字符表示的型別，要求大到足以表示任何 UTF-8 編碼單元（ 8 位元元）。它與 unsigned char 具有相同的大小、符號性和對齊（從而與 char 和 signed char 具有相同的大小和對齊），但它是獨立的型別。

##### <h4 id="concept">concept</h4>

C++20引進了概念（Concepts）這一新特性。
概念是指給一組要求（Requirements）所起的名字。概念是一種具名謂詞。
使用這些要求和概念可以給函式和類樣板的參數加上約束（Constraints）。

###### <h6 id="concept">引入概念的目的</h6>

* 約束成為樣板界面的一部分
* 基於概念的多載成為可能
* 樣板的出錯資訊更加友好
* 沒有約束的 auto 和有約束的概念得到統一

###### <h6 id="concept">約束的種類</h6>

約束有三種型別
* 合取（conjunction）
  約束的合取:使用 && 運算子
* 析取（disjunction）
  約束的析取:使用 || 運算子
* 原子約束（atomic constraint）

###### <h6 id="concept">Requires 子句</h6>

Requires 子句由關鍵字 requires 後加上常數表達式構成，用於指定約束。

###### <h6 id="concept">Requires 表達式</h6>

Requires 表達式是 bool 型別的右值表達式，用於表達約束。其形式為
requires ( 形式參數列表(可選) ) { 要求序列 }

要求序列中的要求有以下四種形式：

* 簡單要求（simple requirement）
  * 簡單要求是任意表達式語句。
* 型別要求（type requirement）
  * 型別要求是關鍵字 typename 加一個型別名。
* 複合要求（compound requirement）
  * { 表達式 } noexcept(可選) 返回型別要求(可選) ;
  * 返回型別要求 - -> 型別約束
* 嵌套要求（nested requirement）
  * reuires 約束表達式 ;

###### <h6 id="concept">Concepts的定義</h6>
```C++
template < template-parameter-list >
concept  concept-name = constraint-expression;
```
其中，constraint-expression是一個可以被eval為bool的表達式或者編譯期函式。 在使用定義好的concept時，constraint-expression會根據上面template-parameter-list傳入的型別，執行編譯期計算，判斷使用該concept的樣板定義是否滿足。 如果不滿足，則編譯期會給定一個具有明確語義的錯誤，即 這個concept沒有匹配成功啦啦這種。 注意到，上述匹配的行為都是在編譯期完成的，因此concept其實是zero-cost的。 舉個例子來描述一下，最基本的concept的定義。
```C++
// 一個永遠都能匹配成功的concept
template <typename T>
concept always_satisfied = true; 

// 一個約束T只能是整數型別的concept，整數型別包括 char, unsigned char, short, ushort, int, unsinged int, long等。
template <typename T>
concept integral = std::is_integral_v<T>;

// 一個約束T只能是整數型別，並且是有符號的concept
template <typename T>
concept signed_integral = integral<T> && std::is_signed_v<T>;
```
接下來，我們再簡單示例一下如何使用一個concept
```C++
// 任意型別都能匹配成功的約束，因此mul只要支援乘法運算子的型別都可以匹配成功。
template <always_satisfied T>
T mul(T a, T b) {
    return a * b;
}

// 整型才能匹配add函式的T
template <integral T>
T add(T a, T b) {
    return a + b;
}

// 有符號整型才能匹配subtract函式的T
template <signed_integral T>
T subtract(T a, T b) {
    return a - b;
}

int main() {
    mul(1, 2); // 匹配成功, T => int
    mul(1.0f, 2.0f);  // 匹配成功，T => float

    add(1, -2);  // 匹配成功, T => int
    add(1.0f, 2.0f); // 匹配失敗, T => float，而T必須是整型
    subtract(1U, 2U); // 匹配失敗，T => unsigned int,而T必須是有符號整型
    subtract(1, 2); // 匹配成功, T => int
}
```

###### <h6 id="concept">Concept的使用方法</h6>
與auto關鍵字的一些結合方式
```C++
// 約束函式樣板方法1
template <my_concept T>
void f(T v);

// 約束函式樣板方法2
template <typename T>
requires my_concept<T>
void f(T v);

// 約束函式樣板方法3
template <typename T>
void f(T v) requires my_concept<T>;

// 直接約束C++14的auto的函式參數
void f(my_concept auto v);

// 約束樣板的auto參數
template <my_concept auto v>
void g();

// 約束auto變數
my_concept auto foo = ...;
```

Concept當然也可以用在lambda函式上，使用方法跟上面一樣
```C++
// 約束lambda函式的方法1
auto f = []<my_concept T> (T v) {
  // ...
};
// 約束lambda函式的方法2
auto f = []<typename T> requires my_concept<T> (T v) {
  // ...
};
// 約束lambda函式的方法3
auto f = []<typename T> (T v) requires my_concept<T> {
  // ...
};
// auto函式參數約束
auto f = [](my_concept auto v) {
  // ...
};
// auto樣板參數約束
auto g = []<my_concept auto v> () {
  // ...
};
```
###### <h6 id="concept">concept的組合(與或非)</h6>
concept的本質是一個樣板的編譯期的bool變數，因此它可以使用C++的與或非三個操作符。例如，我們可以在定義concept的時候，使用其他concept或者表達式，進行邏輯操作。
```C++
template <typename T>
concept Integral = std::is_integral<T>::value;
template <typename T>
concept SignedIntegral = Integral<T> && std::is_signed<T>::value;
template <typename T>
concept UnsignedIntegral = Integral<T> && !SignedIntegral<T>;
```
當然，我們也可以在使用concept的時候使用 邏輯操作符。
```C++
template <typename T>
requires Integral<T> && std::is_signed_v<T>
T add(T a, T b);
```

##### <h4 id="requires">requires</h4>

###### <h6 id="concept">requires關鍵字的其他用法</h6>

requires關鍵字不僅能用在concept的使用上，也可以用在定義中。 例如
```C++
// requires用在使用concept時
template <typename T>
  requires my_concept<T>
void f(T);

// requires用在concept的定義，它表達了型別T的參數f，必須符合大括號內的模式，也就是能被調用。
// 也就是它是一個函式或者一個多載了operator()的型別
template <typename T>
concept callable = requires (T f) { f(); }; 

template <typename T>
  requires requires (T x) { x + x; } // `requires` 同時使用在concept的定義和使用上
T add(T a, T b) {
  return a + b;
}
``
requires的語法理解：requires後接的東西本質上是一個表達式
```C++
// requires後面接的是一個正在被eval的concept，用在上面的concept的使用中。
requires evaled-concept

// 本質上，concept在evaluate時，是一個編譯期返回結果為bool的表達式。這種其實等價於上面那種。
requires expression

// 例如 下面這種就是requires後直接接個bool表達式了
template <typename T>
requires std::is_integral_v<T>
T add(T a, T b) {
    return a + b;
}
```

###### <h6 id="concept">使用requires關鍵字進行約束嵌套或組合</h6>

為了提高concept定義的能力，requires支援用大括號的語法，進行多個約束分開表達，這些約束之間的關係是與的關係。

requires的這種方式的語法形式是
```C++
requires { requirement-seq }
requires ( parameter-list(optional) ) { requirement-seq }
```
這裡每個requirement-seq是可以由多行約束組成，每一行之間以分號分隔。 這些約束的形式有以下幾種

* 簡單約束(Simple Requirements)
* 型別約束(Type Requirements)
* 複合約束(Compound Requirements)
* 嵌套約束(Nested Requirements)

1) 簡單約束
簡單約束就是一個任意的表達式，編譯器對這個約束的檢查就是檢查這個表達式是否是合法的。注意，不是說這個表達式在編譯期運行返回true或者false。而是這個表達式是否合法。 例如
```C++
template<typename T>
concept Addable =
requires (T a, T b) {
    a + b; // "the expression a+b is a valid expression that will compile"
};

// example constraint from the standard library (ranges TS)
template <class T, class U = T>
concept Swappable = requires(T&& t, U&& u) {
    swap(std::forward<T>(t), std::forward<U>(u));
    swap(std::forward<U>(u), std::forward<T>(t));
};
```
2) 型別約束
型別的約束是類似樣板裡面的參數一樣，在typename後接一個型別。這個約束表達的含義是該型別在該concept進行evaluate時，必須是存在的。 如下面的例子：
```C++
struct foo {
    int foo;
};

struct bar {
    using value = int;
    value data;
};

struct baz {
    using value = int;
    value data;
};

// Using SFINAE, enable if `T` is a `baz`.
template <typename T, typename = std::enable_if_t<std::is_same_v<T, baz>>>
struct S {};

template <typename T>
using Ref = T&;

template <typename T>
concept C = requires {
    // Requirements on type `T`:
    typename T::value;  // A) has an inner member named `value`
    typename S<T>;     // B) must have a valid class template specialization for `S`
    typename Ref<T>;   // C) must be a valid alias template substitution
};

template <C T>
void g(T a);

g(foo{}); // ERROR: Fails requirement A.
g(bar{}); // ERROR: Fails requirement B.
g(baz{}); // PASS.
```

3) 複合約束
複合約束用於約束表達式的回傳值的型別。它的寫法形式為：
```C++
// 這裡 ->和type-constraint是可選的.
{expression} noexcept(optional) -> type-constraint;
```

這裡的約束的行為主要有三點,並且約束進行evaluate的順序按照以下順序

* 樣板型別代換到表達式中是否使得表達式合法
* 如果用了noexcept,表達式必須不能可能拋出異常.
* 如果用了->後的型別約束, 則按照以下步驟進行evaluate
* 代換樣板型別到 type-constraint中,
* 並且 decltype((expression))的型別必須滿足type-constraint的約束.

上述步驟任何一個失敗,則evaluate的結果是false.

```C++
template <typename T>
concept C = requires(T x) {
  {*x} -> typename T::inner; // the type of the expression `*x` is convertible to `T::inner`
  {x + 1} -> std::same_as<int>; // the expression `x + 1` satisfies `std::same_as<decltype((x + 1))>`
  {x * 1} -> T; // the type of the expression `x * 1` is convertible to `T`
};
```

4) 嵌套約束

requires內部還可以嵌套requires. 這種方式被稱為嵌套的約束.它的形式為
```C++
requires constraint-expression ;
```
例如
```C++
template <class T>
concept Semiregular = DefaultConstructible<T> &&
    CopyConstructible<T> && Destructible<T> && CopyAssignable<T> &&
requires(T a, size_t n) {  
    requires Same<T*, decltype(&a)>;  // nested: "Same<...> evaluates to true"
    { a.~T() } noexcept;  // compound: "a.~T()" is a valid expression that doesn't throw
    requires Same<T*, decltype(new T)>; // nested: "Same<...> evaluates to true"
    requires Same<T*, decltype(new T[n])>; // nested
    { delete new T };  // compound
    { delete new T[n] }; // compound
};
```


##### <h4 id="consteval">consteval</h4>

consteval關鍵字，用來修飾函式時常數值的表達式，而且是強制性的。如果函式本身不是常數值的表達式的話則會編譯失敗。
constexpr修飾函式時其實只是告訴編譯器該函式可以按常數值的表達式去最佳化，但是如果函式本身不是常數值的表達式的話依然能夠編譯通過。
```C++

constexpr int add100_constexpr(int n) {
  return n + 100;
}
 
consteval int add100_consteval(int n) {
  return n + 100;
}
 
void test() {
    constexpr int c_constexpr = add100_consteval(200);
    int x = 200;
    // int d_consteval = add100_consteval(x);   // 編譯失敗
    int d_constexpr = add100_constexpr(x);      //編譯成功，constexpr並非強制限定為常數表達式
}
```

##### <h4 id="co_await">co_await</h4>

co_await可以掛起和恢復函式的執行。

##### <h4 id="co_yield">co_yield</h4>

co_yield可以在不結束協程的情況下從協程返回一些值。因此，可以用它來編寫無終止條件的生成器函式。

##### <h4 id="co_return">co_return</h4>

co_return允許從協程返回一些值，需要自行定製。

#### <h2 id="cpp_20_meaning_keywords">C++20含義變化或者新增含義關鍵字</h2>

##### <h5 id="export">export</h5>

C++20不使用並保留該關鍵詞。
