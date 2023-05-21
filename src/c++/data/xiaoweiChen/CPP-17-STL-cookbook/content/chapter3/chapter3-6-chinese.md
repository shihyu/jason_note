# 使用哨兵終止迭代

對於STL算法和基於範圍的for循環來說，都會假設迭代的位置是提前知道的。在有些情況下，並不是這樣，我們在迭代器到達末尾之前，我們是很難確定結束的位置在哪裡。

這裡使用C風格的字符串來舉例，我們在編譯時無法知道字符串的長度，只能在運行時使用某種方法進行判斷。字符串遍歷的代碼如下所示：

```c
for (const char *c_ponter = some_c_string; *c_pointer != '\0'; ++c_pointer) {
    const char c = *c_pointer;
    // do something with c
}
```

對於基於範圍的for循環來說，我們可以將這段字符串包裝進一個`std::string`實例中，`std::string`提供`begin()`和`end()`函數：

```c++
for (char c : std::string(some_c_string)) { /* do something with c */ }
```

不過，`std::string`在構造的時候也需要對整個字符串進行遍歷。C++17中加入了`std::string_view`，但在構造的時候也會對字符串進行一次遍歷。對於比較短的字符串來說這是沒有必要的，不過對於其他類型來說就很有必要。`std::istream_iterator`可以用來從`std::cin`捕獲輸入，當用戶持續輸入的時候，其`end`迭代器並不能指向輸入字符串真實的末尾。

C++17添加了一項新的特性，其不需要`begin`迭代器和`end`迭代器是同一類型的迭代器。本節我們看看，這種小修改的大用途。

## How to do it...

本節，我們將在範圍類中構造一個迭代器，其就不需要知道字符串的長度，也就不用提前找到字符串結束的位置。

1. 包含必要的頭文件。

   ```c++
   #include <iostream> 
   ```

2. 迭代器哨兵是本節的核心內容。奇怪的是，它的定義完全是空的。

   ```c++
   class cstring_iterator_sentinel {};
   ```

3. 我們先來實現迭代器。其包含一個字符串指針，指針指向的容器就是我們要迭代的：

   ```c++
   class cstring_iterator {
   	const char *s {nullptr};
   ```

4. 構造函數只是初始化內部字符串指針，對應的字符串是外部輸入。顯式聲明構造函數是為了避免字符串隱式轉換為字符串迭代器:

   ```c++
   public:
       explicit cstring_iterator(const char *str)
       	: s{str}
       {}
   ```

5. 當對迭代器進行解引用，其就會返回對應位置上的字符：

   ```c++
   	char operator*() const { return *s; }
   ```

6. 累加迭代器只增加迭代器指向字符串的位置：

   ```c++
       cstring_iterator& operator++() {
           ++s;
           return *this;
       }
   ```

7. 這一步是最有趣的。我們為了比較，實現了`!=`操作符。不過，這次我們不會去實現迭代器的比較操作，這次迭代器要和哨兵進行比較。當我們比較兩個迭代器時，在當他們指向的位置相同時，我們可以認為對應範圍已經完成遍歷。通過和空哨兵對象比較，當迭代器指向的字符為`\0`字符時，我們可以認為到達了字符串的末尾。

   ```c++
       bool operator!=(const cstring_iterator_sentinel) const {
       	return s != nullptr && *s != '\0';
       }
   };
   ```

8. 為了使用基於範圍的`for`循環，我們需要一個範圍類，用來指定`begin`和`end`迭代器：

   ```c++ 
   class cstring_range {
   	const char *s {nullptr};
   ```

9. 實例化時用戶只需要提供需要迭代的字符串：

   ```c++
   public:
       cstring_range(const char *str)
       	: s{str}
       {}
   ```

10. `begin()`函數將返回一個`cstring_iterator`迭代器，其指向了字符串的起始位置。`end()`函數會返回一個哨兵類型。需要注意的是，如果不使用哨兵類型，這裡將返回一個迭代器，這個迭代器要指向字符串的末尾，但是我們無法預知字符串的末尾在哪裡。

   ```c++
       cstring_iterator begin() const {
      		return cstring_iterator{s};
       }
       cstring_iterator_sentinel end() const {
       	return {};
       }
   };
   ```

11. 類型定義完，我們就來使用它們。例子中字符串是用戶輸入，我們無法預知其長度。為了讓使用者給我們一些輸入，我們的例子會判斷是否有輸入參數。

    ```c++
    int main(int argc, char *argv[])
    {
        if (argc < 2) {
            std::cout << "Please provide one parameter.\n";
            return 1;
        }
    ```

12. 當程序運行起來時，我們就知道`argv[1]`中包含的是使用者的字符串。

    ```c++
        for (char c : cstring_range(argv[1])) {
        	std::cout << c;
        }
        std::cout << '\n';
    } 
    ```

13. 編譯運行程序，就能得到如下的輸出：

    ```c++
    $ ./main "abcdef"
    abcdef
    ```

循環會將所有的字符打印出來。這是一個很小的例子，只是為了展示如何使用哨兵確定迭代的範圍。當在無法獲得`end`迭代器的位置時，這是一種很有用的方法。當能夠獲得`end`迭代器時，就不需要使用哨兵了。