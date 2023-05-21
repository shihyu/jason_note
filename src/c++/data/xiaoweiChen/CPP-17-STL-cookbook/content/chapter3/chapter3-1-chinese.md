# 建立可迭代區域

我們已經認識了STL中提供的各種迭代器。我們只需實現一個迭代器，支持前綴加法`++`，解引用`*`和比較操作`==`，這樣我們就能使用C++11基於範圍的for循環對該迭代器進行遍歷。

為了更好的瞭解迭代器，本節中將展示如何實現一個迭代器。迭代該迭代器時，只輸出一組數字。實現的迭代器並不支持任何容器，以及類似的結構。這些數字是在迭代過程中臨時生成的。

## How to do it...

本節中，我們將實現一個迭代器類，並且對該迭代器進行迭代：

1. 包含必要的頭文件。

   ```c++
   #include <iostream> 
   ```

2. 迭代器結構命名為`num_iterator`:

   ```c++
   class num_iterator { 
   ```

3. 其數據類型只能是整型，僅用是用來計數的，構造函數會初始化它們。顯式聲明構造函數是一個好習慣，這就能避免隱式類型轉換。需要注意的是，我們會使用`position`值來初始化`i`。這就讓`num_iterator`可以進行默認構造。雖然我們的整個例子中都沒有使用默認構造函數，但默認構造函數對於STL的算法卻是很重要的。

   ```c++
   	int i;
   public:
   	explicit num_iterator(int position = 0) : i{position} {}
   ```

4. 當對迭代器解引用時*it`，將得到一個整數：

   ```c++
   	int operator*() const { return i; }
   ```

5. 前綴加法操作`++it`：

   ```c++
       num_iterator& operator++() {
           ++i;
           return *this;
       }
   ```

6. `for`循環中需要迭代器之間進行比較。如果不相等，則繼續迭代：

   ```c++
       bool operator!=(const num_iterator &other) const {
       	return i != other.i;
       }
   };
   ```

7. 迭代器類就實現完成了。我們仍需要一箇中間對象對應於` for (int i : intermediate(a, b)) {...}`寫法，其會從頭到尾的遍歷，其為一種從a到b遍歷的預編程。我們稱其為`num_range`:

   ```c++
   class num_range {
   ```

8. 其包含兩個整數成員，一個表示從開始，另一個表示結束。如果我們要從0到9遍歷，那麼a為0，b為10(`[0, 10)`)：

   ```c++
       int a;
       int b;
   public:
       num_range(int from, int to)
       	: a{from}, b{to}
       {}
   ```

9. 該類也只有兩個成員函數需要實現：`begin`和`end`函數。兩個函數都返回指向對應數字的指針：一個指向開始，一個指向末尾。

   ```c++
       num_iterator begin() const { return num_iterator{a}; }
       num_iterator end() const { return num_iterator{b}; }
   };
   ```

10. 所有類都已經完成，讓我們來使用一下。讓我們在主函數中寫一個例子，遍歷100到109間的數字，並打印這些數值：

   ```c++
   int main()
   {
       for (int i : num_range{100, 110}) {
       	std::cout << i << ", ";
       }
       std::cout << '\n';
   }
   ```

11. 編譯運行後，得到如下輸出：

    ```c++
    100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
    ```

## How it works...

考慮一下如下的代碼段：

```c++
for (auto x : range) { code_block; }
```

這段代碼將被編譯器翻譯為類似如下的代碼：

```c++
{
    auto __begin = std::begin(range);
    auto __end = std::end(range);
    for ( ; __begin != __end; ++__begin) {
        auto x = *__begin;
        code_block
    }
}
```

這樣看起來就直觀許多，也能清楚的瞭解我們的迭代器需要實現如下操作：

- operator!=
- operatpr++
- operator*

也需要`begin`和`end`方法返回相應的迭代器，用來確定開始和結束的範圍。

> Note:
>
> 本書中，我們使用`std::begin(x)`替代`x.begin()`。如果有`begin`成員函數，那麼`std::begin(x)`會自動調用`x.begin()`。當`x`是一個數組，沒有`begin()`方法是，`std::begin(x)`會找到其他方式來處理。同樣的方式也適用於`std::end(x)`。當用戶自定義的類型不提供`begin/end`成員函數時，`std::begin/std::end`就無法工作了。

本例中的迭代器是一個前向迭代器。再來看一下使用`num_range`的循環，從另一個角度看是非常的簡單。

> Note:
>
> 回頭看下構造出迭代器的方法在`range`類中為`const`。這裡不需要關注編譯器是否會因為修飾符`const`而報錯，因為迭代`const`的對象是很常見的事。

