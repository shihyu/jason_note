> 原文鏈接：https://liuxizai.ac.cn/post/notes-cpp14/

基於 Ubuntu 20.04 的 NOI 2.0 發佈後，我們或許有機會開始使用 C++14。

這篇 Blog 將對 OI 中可能會使用到的 C++14 的新特性進行簡要總結。

> 由於大部分 OIer 被 CCF 迫害可能是 C++98 轉 C++14，文中部分特性實際上是來源於 C++11 標準的。
>
> 另一個重要原因是，C++14 並不是 C++ 的一個主要版本（主要版本：C++03 C++11 C++17），其被認為是 C++11 一個更加完善的版本，C++11 這一更新經歷了整整8年時間，引入了大量更改，可以說是 C++98 以來最重要的更新，所以提到 C++11 的特性確實很有必要。

這篇 Blog 以簡潔易懂為主要目標，為此可能有些地方會在不影響理解的情況下使用一些不準確的表達，這些地方往往都有腳註，可以通過我給出的鏈接查看更詳細的內容。

## constexpr

C++ 中一直存在著常量表達式的概念，在 C++98 中我們可以這樣定義一個常量

```cpp
const int SIZE = 100005;
```

常量將無法修改，並且這也是編譯器的一個優化機會，編譯器往往會在編譯時就處理好常量表達式的值，並在程序中硬編碼結果，也就是不會在程序運行時再去計算表達式的值。

```cpp
const int MOD = 1e9 + 7;

// source code
ans = ans % MOD;

// after compilation
ans = ans % 1000000007; // yes, 1e9 + 7 has been calculated
ans = ans % (1e9 + 7); // no
```

另外，常量可以用來初始化數組

```cpp
int len = 10;
int a[len]; // compile error

const int len = 10;
int a[len]; // ok
```

C++11 中的 `constexpr` 關鍵字更進一步放寬了常量表達式的限制

```cpp
const int f() { return 10; }
int a[f()+5]; // compile error

constexpr int f() { return 10; }
int a[f()+5]; // ok
```

你可能已經發現了，C++11 允許將函數作為常量表達式，但是 C++11 要求函數必須恰由一條 `return` 語句組成，而 C++14 解除了這一限制，但你仍需要保證函數中沒有：

- `goto` 語句

- 未進行初始化的變量定義

  ```cpp
  int a; // no
  int a = 10; // yes
  ```

- 非字面類型的變量定義（算術類型如 `int` 屬於字面類型，而自定義類型如 `string` 屬於非字面類型）

為了方便 OIer 理解，以上內容並不完全準確。

## lambda

C++11 中允許使用匿名函數，其能夠內聯於語句中

```cpp
struct node { int x, y; };
std::vector<node> arr;

// C++98
bool cmp(node a, node b) { return a.x < b.x; }
std::sort(arr.begin(), arr.end(), cmp);

// C++11
std::sort(arr.begin(), arr.end(), [](node a, node b){ return a.x < b.x; });
```

兩種寫法效果都是一樣的。

具體地說，`lambda` 表達式的語法為

```cpp
[捕獲](形參){函數體}
```

其中需要具體講解的是捕獲這一部分。

捕獲分為這樣幾個類型：

- `[]` - 空捕獲列表，`lambda` 表達式只能夠使用非局部變量。
- `[names]` - `names` 是一個逗號分割的名字列表，這些名字為匿名函數所在的局部變量，這些局部變量將被拷貝（也就是說在函數中修改其值後並不會影響到其本身），如果 `name` 前面使用了 `&`，將會使用引用的方式捕獲。
- `[&]` - 隱式的以引用方式捕獲所有匿名函數使用的局部變量。
- `[=]` - 隱式的以值方式（即拷貝）捕獲所有匿名函數使用的局部變量。
- `[&, list]` - `list` 是一個逗號分割的列表，列表中的變量以值方式捕獲，其他局部變量隱式的以引用方式捕獲。
- `[=, list]` - `list` 是一個逗號分割的列表，列表中的變量以引用方式捕獲，其他局部變量隱式的以值方式捕獲。

C++14 標準中規定了泛型 `lambda`，由於過於複雜，選擇不將其寫入 Blog。

另外，你會發現匿名函數沒有規定返回值，編譯器將會自行判斷函數的返回值，如果需要指定函數返回值，可以使用以下語法

```cpp
[捕獲](形參)->返回值類型 {函數體}
```

## 變量模板（variable template）

C++14 允許通過變量模板定義一族變量。

```cpp
template<typename T> // variable template
const T pi = T(3.14159265);

template<typename T> // function template
T circleArea(T r){
    return pi<T> * r * r; // variable template instantiation
}
```

## 聚合初始化（aggregate initialization）

聚合初始化是 C++11 中列表初始化的一種形式。

首先，聚合體是下列類型之一：

- 數組類型
- 滿足一下條件的類類型（常為struct）
  - 沒有私有或受保護的非靜態數據成員（在類中聲明的非 `static` 數據成員）
  - 沒有用戶提供的構造函數
  - 沒有虛成員函數

你可以像這樣進行聚合初始化

```cpp
struct node{
    int a, b;
    int c[3];
    int d;
};
node nd = {2, 3, 5, 6, 3, 4};
```

這樣初始化過後

```cpp
a = 2;
b = 3;
c = {5, 6, 3};
d = 4;
```

可以發現聚合初始化是按照地址順序依次進行的，所以對於類中的數組成員可以很方便的進行初始化，當然這也意味著聚合初始化無法直接指定一些成員進行初始化。

> 在 C++20 中允許進行指派初始化器的聚合初始化，即可以指定成員進行初始化

另一個很重要的特性，聚合初始化是遞歸進行的，也就是說其允許嵌套

```cpp
struct A{
    struct B{
        int a;
        int b;
        int c;
    };
    B d;
    int e;
    vector<int> f;
};
```

這樣一個結構體我們仍然可以使用聚合初始化

```cpp
A a = {{1, 2, 3}, 4, {5, 6}};
```

初始化結果如下

```cpp
d.a = 1;
d.b = 2;
d.c = 3;
e = 4;
f = {5, 6};
```

在 C++11 中，聚合初始化要求類成員沒有默認初始化器（`int a = 10`），但在 C++14 中允許我們這麼做，所以另外很重要的一點是，當聚合初始化與默認初始化器結合時，到底會產生怎麼樣的結果。

舉個例子說明

```cpp
struct A {
    struct B {
        int a = 21;
        int b;
        int c = 22;
        int d;
        int e = 23;
    };
    B b1  = { 11, 12 };
    B b2  = { 11, 12, 13 };
    int x;
};
```

接下來進行聚合初始化

```cpp
A a = { { 1, 2, 3, 4 }, { 1 }, 5 };
```

你會得到這樣的結果

```cpp
b1.a = 1;
b1.b = 2;
b1.c = 3;
b1.d = 4;
b1.e = 23;
b2.a = 1;
b2.b = 0;
b2.c = 22;
b2.d = 0;
b2.e = 23;
x = 5;
```

你會發現，`b2`的初始化好像失效了，否則我們應該得到這樣的結果

```cpp
b2.a = 1;
b2.b = 12;
b2.c = 13;
b2.d = 0;
b2.e = 23;
```

初始化器提供的值比類成員少時，根據 N3605，C++14 會採用如下策略

- 從成員的默認初始化器進行初始化
- 如果沒有默認初始化器，用一個空初始化器列表進行初始化

那麼，我們在對 `a` 進行聚合初始化時， 實際上為 `b2` 提供了值 `{1}`，所以 `b2` 的初始化器**完全失效**，接下來，`b2.a` 從聚合初始化中的到了值，其他成員沒有得到值，所以隱式的按照 N3605 進行初始化。

這正是我們得到的結果。

## auto

`auto` 於 C++11 引入作為佔位類型說明符，其能夠從初始化器自動推導變量類型。

```cpp
auto a = 12;        // int
auto b = 2 + 4 * 7; // int
auto c = 0.17;      // double
auto d = a;         // int
auto e = a + c;     // double
複製代碼
```

C++14 還允許使用 `auto` 自動推斷函數返回值類型

```cpp
auto f() { return 2 + 3; } // int
```

如下寫法將會被推導為列表初始化器

```cpp
auto g = {1, 2, 3, 4, 5}; // std::initializer_list<int>
auto h{1, 2, 3, 4, 5}; // std::initializer_list<int>
```

> 第二種寫法在 C++17 中被棄用

另外，`auto` 還常用於無名類型，如 `lambda` 表達式類型

```cpp
auto lambda = []() { return 9 + 12; }
std::cout << lambda() << std::endl; // 21
```

需要注意的是，`auto` 說明符要求變量必須擁有初始化器

```cpp
auto x; // compile error
auto y = 10; // ok
```

> `auto x;` 這種寫法在 C 中被允許。

如果想要了解更多，可以參考 cppreference。

## 基於範圍的 for 循環（range-based for loop）

C++11 規定了基於範圍的 `for` 循環，其在一個範圍上執行 `for` 循環，是傳統 `for` 循環一個更加可讀的等價版本，OI 中常用於圖遍歷。

其語法如下

```cpp
[屬性-可選]
for(範圍聲明: 範圍表達式){
    循環語句
}
```

> 屬性：屬性說明符序列，不在 Blog 中進行說明，幾乎不會用到。

- 範圍聲明：一個具名變量的聲明，類型為範圍表達式中元素的類型或其引用，一般使用 `auto` 對其類型進行推導。
- 範圍表達式：一個序列（數組，或是定義了 `begin` 和 `end` 的對象，如 `vector`），或是一個花括號列表初始化器（如 `{1, 2, 3, 4, 5}`）。
- 循環語句：常規函數體。

基於範圍的 `for` 循環可以用這樣的常規 `for` 循環替代

```cpp
for(auto __begin = 首表達式, __end = 尾表達式; __begin != __end; __begin++){
    範圍聲明 = *__begin;
    循環語句
}
```

其中，對於數組 `a[]`，其首表達式為 `a`，尾表達式為 `(a + __bound)`，`__bound` 為數組長度，我們要求數組是有確定長度的。

對於定義了 `begin` 和 `end` 的對象 `b`，其首表達式為 `b.begin()`，尾表達式為 `b.end()`。

否則，通過實參依賴查找進行查找。

一些實際使用的例子

```cpp
vector<int> g[10005];
for(auto v: g[u]){
    /* something here */
}

int a[] = {1, 2, 3, 4, 5};
for(auto &x: a){
   	x++;
    std::cout << x << ' ';
}
// after - a: {2, 3, 4, 5, 6}

for(auto x: {1, 3, 5, 7}){
    std::cout << x << ' ';
}
```

## 變參數模板（variadic template）

在我看來無比實用的特性之一，你可以在我的 `template` 中找到這樣一個函數

```cpp
void input() {}
template<typename Type, typename... Types>
void input(Type& arg, Types&... args){
    arg = read<Type>();
    input(args...);
}
```

這就是一個變參數模板的使用案例，你可以通過 `input()` 函數一次性對任意個變量通過快讀進行讀入。

```cpp
int x, y, z;
input(x); // ok
input(x, y, z); // ok
```

常用的變參數模板格式和上面大同小異，都是通過遞歸調用，`input(Type& arg, Types&... args)` 遞歸變參函數，`input(args...)` 就是在進行遞歸調用，我們當然需要給這樣一個遞歸函數一個終止條件，`input()` 被稱為基礎函數，遞歸變參數函數最終在這裡停止。
