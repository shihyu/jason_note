# 使用結構化綁定來解包綁定的返回值

C++17配備了一種新的特性——**結構化綁定**，其可以結合語法糖來自動推到類型，並可以從組對、元組和結構體中提取單獨的變量。其他編程語言中，這種特性也被成為**解包**。

## How to do it...

使用結構化綁定是為了能夠更加簡單的，為綁定了多個變量的結構體進行賦值。我們先來看下在C++17標準之前是如何完成這個功能的。然後，我們將會看到一些使用C++17實現該功能的例子：

- 訪問`std::pair`中的一個元素：假設我們有一個數學函數`divide_remainder`，需要輸入一個除數和一個被除數作為參數，返回得到的分數的整數部分和餘數。可以使用一個`std::pair`來綁定這兩個值:

  `std::pair<int, int> divide_remainder(int dividend, int divisor);`

考慮使用如下的方式訪問組對中的單個值：

```c++
const auto result (divide_remainder(16, 3));
std::cout << "16 / 3 is " <<
          << result.first << " with a remainder of "
          << result.second << '\n';
```

與上面的代碼段不同，我們現在可以將相應的值賦予對應的變量，這樣寫出來的代碼可讀性更高:

```c++
auto [fraction, remainder] = divide_remainder(16, 3);
std::cout << "16 / 3 is "
          << fraction << " with a remainder of "
          << remainder << '\n';
```

- 也能對`std::tuple`進行結構化綁定：讓我們使用下面的實例函數，獲取股票的在線信息：

```c++
std::tuple<std::string, std::chrono::system_clock::time_point, unsigned>
stock_info(const std::string &name);
```

我們可以使用如下的方式獲取這個例子的各個變量的值：

```c++
const auto [name, valid_time, price] = stock_info("INTC");
```

* 結構化綁定也能用在自定義結構體上。假設有這麼一個結構體：

```c++
struct employee{
    unsigned id;
    std::string name;
    std::string role;
    unsigned salary;
};
```

現在我們來看下如何使用結構化綁定訪問每一個成員。我們假設有一組`employee`結構體的實例，存在於`vector`中，下面使用循環將其內容進行打印：

```c++
int main(){
    std::vector<employee> employees{
        /* Initialized from somewhere */
    };
    
    for (const auto &[id, name, role, salary] : employees){
        std::cout << "Name: " << name
                  << "Role: " << role
                  << "Salary: " << salary << '\n';
    }
}
```

## How it works...

結構化綁定以以下方式進行應用：

`auto [var1, var2, ...] = <pair, tuple, struct, or array expression>;`

- `var1, var2, ...`表示一個變量列表，其變量數量必須匹配表達式所對應的結構。
- `<pair, tuple, struct, or array expression>`必須是下面的其中一種：
  - 一個`std::pair`實例。
  - 一個`std::tuple`實例。
  - 一個結構體實例。其所有成員都必須是非靜態成員，每個成員以基礎類定義。結構體中的第一個聲明成員賦予第一個變量的值，第二個聲明的編程賦予第二個變量的值，依次類推。
  - 固定長度的數組。
- `auto`部分，也就是`var`的類型，可以是`auto`,`const auto`,`const auto&`和`auto&&`。

> Note:
>
> 不僅為了性能，還必須確保在適當的時刻使用引用，儘量減少不必要的副本。

如果中括號中變量不夠，那麼編譯器將會報錯:

```c++
std::tuple<int, float, long> tup(1, 2.0, 3);
auto [a, b] = tup; // Does not work
```

這個例子中想要將三個成員值，只賦予兩個變量。編譯器會立即發現這個錯誤，並且提示我們:

```
error: type 'std::tuple<int, float, long>' decomposes into 3 elements, but only 2 names were provided
auto [a, b] = tup;
```

## There's more...

STL中的基礎數據結構都能通過結構結構化綁定直接進行訪問，而無需修改任何東西。考慮下面這個例子，循環中打印`std::map`中的元素：

```c++
std::map<std::string, size_t> animal_population {
  {"humans", 7000000000},
  {"chickens", 17863376000},
  {"camels", 24246291},
  {"sheep", 1086881528},
  /* ... */
};

for (const auto &[species, count] : animal_population) {
  std::cout << "There are " << count << " " << species
            << " on this planet.\n";
}
```

從`std::map`容器中獲取元素的方式比較特殊，我們會在每次迭代時獲得一個`std::pair<const key_type, value_type>`實例。另外每個實例都需要進行結構化綁定(`key_type`綁定到`species`字符串上，`value_type`為一個`size_t`格式的統計數字)，從而達到訪問每一個成員的目的。

在C++17之前，使用`std::tie`可達到類似的效果:

```c++
int remainder;
std::tie(std::ignore, remainder) = divide_remainder(16, 5);
std::cout << "16 % 5 is " << remainder << '\n';
```

這個例子展示瞭如何將結果組對解壓到兩個變量中。`std::tie`的能力遠沒有結構化綁定強，因為在進行賦值的時候，所有變量需要提前定義。另外，本例也展示了一種在`std::tie`中有，而結構化綁定沒有的功能：可以使用`std::ignore`的值，作為虛擬變量。分數部分將會賦予到這個虛擬變量中，因為這裡我們不需要用到分數值，所以使用虛擬變量忽略分數值。

> Note:
>
> 使用結構化綁定時，就不能再使用std::tie創建虛擬變量了，所以我們不得不綁定所有值到命名過的變量上。對部分成員進行綁定的做法是高效的，因為編譯器可以很容易的對未綁定的變量進行優化。

回到之前的例子，`divide_remainder`函數也可以通過使用傳入輸出參數的方式進行實現：

```c++
bool divide_remainder(int dividend, int divisor, int &fraction, int &remainder);
```

調用該函數的方式如下所示：

```c++
int fraction, remainder;
const bool success {divide_remainder(16, 3, fraction, remainder)};
if (success) {
  std::cout << "16 / 3 is " << fraction << " with a remainder of "
            << remainder << '\n';
}
```

很多人都很喜歡使用特別複雜的結構，比如組對、元組和結構體，他們認為這樣避免了中間拷貝過程，所以代碼會更快。對於現代編譯器來說，這種想法不再是正確的了，這裡編譯器並沒有刻意避免拷貝過程，而是優化了這個過程。(其實拷貝過程還是存在的)。

> Note:
>
> 與C的語法特徵不同，將複雜結構體作為返回值傳回會耗費大量的時間，因為對象需要在返回函數中進行初始化，之後將這個對象拷貝到相應容器中返回給調用端。現代編譯器支持**[返回值優化](https://zh.wikipedia.org/wiki/%E8%BF%94%E5%9B%9E%E5%80%BC%E4%BC%98%E5%8C%96)**(RVO, *return value optimization*)技術，這項技術可以省略中間副本的拷貝。