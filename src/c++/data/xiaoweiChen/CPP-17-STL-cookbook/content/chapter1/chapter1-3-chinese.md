# 新的括號初始化規則

C++11引入了新的括號初始化語法`{}`。其不僅允許集合式初始化，而且還是對常規構造函數的調用。遺憾的是，當與`auto`類型變量結合時，這種方式就很容易出現錯誤。C++17將會增強這一系列初始化規則。本節中，我們將瞭解到如何使用C++17語法正確的初始化變量。

## How to do it...

一步初始化所有變量。使用初始化語法時，注意兩種不同的情況：

- 不使用auto聲明的括號初始化：

```c++
// Three identical ways to initialize an int:
int x1 = 1;
int x2{1};
int x3(1);

std::vector<int> v1{1, 2, 3}; // Vector with three ints
std::vector<int> v2 = {1, 2, 3}; // same here
std::vector<int> v3(10, 20); // Vector with 10 ints, each have value 20
```

- 使用auto聲明的括號初始化：

```c++
auto v {1}; // v is int
auto w {1, 2}; // error: only single elements in direct
              // auto initialization allowed! (this is new)
auto x = {1}; // x is std::initializer_list<int>
auto y = {1, 2}; // y is std::initializer_list<int>
auto z = {1, 2, 3.0}; // error: Cannot deduce element type
```

## How it works...

無`auto`類型聲明時，`{}`的操作沒什麼可大驚小怪的。當在初始化STL容器時，例如`std::vector`，`std::list`等等，括號初始化就會去匹配`std::initializer_list`(初始化列表)的構造函數，從而初始化容器。其構造函數會使用一種“貪婪”的方式，這種方式就意味著不可能匹配非聚合構造函數(與接受初始化列表的構造函數相比，非聚合構造函數是常用構造函數)。

`std::vector`就提供了一個特定的非聚合構造函數，其會使用任意個相同的數值填充`vector`容器：`std::vector<int> v(N, value)`。當寫成`std::vector<int> v{N, value}`時，就選擇使用`initializer_list`的構造函數進行初始化，其會將`vector`初始化成只有N和value兩個元素的變量。這個“陷阱”大家應該都知道。

`{}`與`()`調用構造函數初始化的方式，不同點在於`{}`沒有類型的隱式轉換，比如`int x(1.2);`和`int x = 1.2;`通過靜默的對浮點值進行向下取整，然後將其轉換為整型，從而將x的值初始化為1。相反的，`int x{1.2};`將會遇到編譯錯誤，初始化列表中的初始值，需要與變量聲明的類型完全匹配。

> Note:
>
> 哪種方式是最好的初始化方式，目前業界是有爭議的。括號初始化的粉絲們提出，使用括號的方式非常直觀，直接可以調用構造函數對變量進行初始化，並且代碼行不會做多於的事情。另外，使用{}括號將會是匹配構造函數的唯一選擇，這是因為使用()進行初始化時，會嘗試匹配最符合條件的構造函數，並且還會對初始值進行類型轉換，然後進行匹配(這就會有處理構造函數二義性的麻煩)。

C++17添加的條件也適用於auto(推斷類型)——C++11引入，用於正確的推導匹配變量的類型。`auto x{123};`中`std::initializer_list<int>`中只有 一個元素，這並不是我們想要的結果。C++17將會生成一個對應的整型值。

經驗法則：

- `auto var_name {one_element};`將會推導出var_name的類型——與one_element一樣。
- `auto var_name {element1, element2, ...};`是非法的，並且無法通過編譯。
- `auto var_name = {element1, element2, ...};`將會使用`std::initializer_list<T>`進行初始化，列表中elementN變量的類型均為T。

C++17加強了初始化列表的魯棒性。

> Note:
>
> 使用C++11/C++14模式的編譯器解決這個問題時，有些編譯器會將`auto x{123};`的類型推導成整型，而另外一些則會推導成 `std::initializer_list<int>`。所以，這裡需要特別注意，編寫這樣的代碼，可能會導致有關可移植性的問題！







