# 實現分割算法

很多情況下，STL中的算法並不夠我們使用，有些算法需要我們自己去實現。解決具體問題之前，我們需要確定，這個問題是否有通解。當我們自己遇到一些問題時，我們可以實現一些輔助函數幫助我們，這些輔助函數逐漸的就可以形成庫。這裡關鍵是要明白什麼樣的代碼是足夠通用的，否則我們就需要創造一套通用語言了。

本節我們將實現一個算法，叫做**分割**(split)。該算法可以通過給定的值，對任何範圍的元素進行分割，將分割後的結果塊拷貝到輸出區域中。

## How to do it...

本節，將實現類似於STL的算法叫做分割，並且用這個算法對字符串進行分割：

1. 首先，包含必要的頭文件，並聲明相應的命名空間。

   ```c++
   #include <iostream>
   #include <string>
   #include <algorithm>
   #include <iterator>
   #include <list>
   
   using namespace std; 
   ```

2. 本節的所有算法都圍繞分割來進行。其接受一對`begin/end`迭代器和一個輸出迭代器，其用法和`std::copy`或`std::transform`類似。其他參數為`split_val`和`bin_func`。`split_val`參數是要在輸入範圍內要查找的值，其表示要當碰到這個值時，要對範圍進行分割。`bin_func`參數是一個函數，其為分割的子序列的開始和結尾。我們可以使用`std::find`對輸入範圍進行迭代查找，這樣就能直接跳轉到`split_val`所在的位置。當將一個長字符串分割成多個單詞，可以通過分割空格字符達到目的。對於每一個分割值，都會做相應的分割，並將對應的分割塊拷貝到輸出範圍內：

   ```c++
   template <typename InIt, typename OutIt, typename T, typename F>
   InIt split(InIt it, InIt end_it, OutIt out_it, T split_val,
   		  F bin_func)
   {
       while (it != end_it) {
           auto slice_end (find(it, end_it, split_val));
           *out_it++ = bin_func(it, slice_end);
           
           if (slice_end == end_it) { return end_it; }
           it = next(slice_end);
       }
       return it;
   }
   ```

3. 現在嘗試一下我們的新算法，構建一個需要進行分割的字符串。其中的字符使用`-`進行連接：

   ```c++
   int main()
   {
   	const string s {"a-b-c-d-e-f-g"};
   ```

4. 創建一個`bin_func`對象，其能接受一組迭代器，我們需要通過該函數創建一個新的字符串：

   ```c++
   	auto binfunc ([](auto it_a, auto it_b) {
       	return string(it_a, it_b);
       });
   ```

5. 輸出的子序列將保存在`std::list`中。我們現在可以調用`split`算法：

   ```c++
       list<string> l;
       split(begin(s), end(s), back_inserter(l), '-', binfunc);
   ```

6. 為了看一下結果，我們將對子字符串進行打印：

   ```c++
   	copy(begin(l), end(l), ostream_iterator<string>{cout, "\n"});
   } 
   ```

7. 編譯並運行程序，就可以看到如下輸出。其子序列將不會包含破折號，只有單個單詞(在我們的例子中，為單個字母)：

   ```c++
   $ ./split
   a
   b
   c
   d
   e
   f
   g
   ```



## How it works...

`split`算法與`std::transform`的工作原理很類似，因為其能接受一對`begin/end`迭代器和一個輸出迭代器。其也會將最終的算法結果拷貝到輸出迭代器所在的容器。除此之外，其接受一個`split_val`值和一個二元函數。讓我們再來看一起其整體實現：

```c++
template <typename InIt, typename OutIt, typename T, typename F>
InIt split(InIt it, InIt end_it, OutIt out_it, T split_val, F bin_func)
{
    while (it != end_it) {
        auto slice_end (find(it, end_it, split_val));
        *out_it++ = bin_func(it, slice_end);
        
        if (slice_end == end_it) { return end_it; }
        it = next(slice_end);
    }
    return it;
}
```

實現中的循環會一直進行到輸入範圍結束。每次迭代中都會調用`std::find`用來在輸入範圍內查找下一個與`split_val`匹配的元素。在我們的例子中，分割字符就是`-`。每次的下一個減號字符的位置會存在`slice_end`。每次循環迭代之後，`it`迭代器將會更新到下一個分割字符所在的位置。循環起始範圍將從一個減號跳到下一個減號，而非每一個獨立的元素。

這一系列的操作中，迭代器`it`指向的是最後子字符串的起始位置，`slice_end`指向的是子字符串的末尾位置。通過這兩個迭代器，就能表示分割後的子字符串。對於字符串`foo-bar-baz`來說，循環中就有三個迭代器。對於用戶而言，迭代器什麼的並不重要，他們想要的是子字符串，所以這裡就是`bin_func`來完成這個任務。當我們調用`split`時，我們可以給定其一個如下的二元函數：

```c++
[](auto it_a, auto it_b) {
	return string(it_a, it_b);
}
```

`split`函數會將迭代器傳遞給`bin_func`，並通過迭代器將結果放入輸出迭代器中。這樣我們就能通過`bin_func`獲得相應的單詞，這裡的結果是`foo`，`bar`和`baz`。

## There's more...

我們也可以實現相應的迭代器來完成這個算法的實現。我們現在不會去實現這樣一個迭代器，但是可以簡單的看一下。

迭代的每次增長，都會跳轉到下一個限定符。

當對迭代器進行解引用時，其會通過迭代器指向的當前位置，創建一個字符串對象，就如同之前用到的`bin_func`函數那樣。

迭代器類可以稱為`split_iterator`，用來替代算法`split`，用戶的代碼可以寫成如下的樣式：

```c++
string s {"a-b-c-d-e-f-g"};
list<string> l;

auto binfunc ([](auto it_a, auto it_b) {
	return string(it_a, it_b);
});

copy(split_iterator{begin(s), end(s), "-", binfunc},{}, back_inserter(l));
```

雖然在使用中很方便，但是在實現時，迭代器的方式要比算法的形式複雜許多。並且，迭代器實現中很多邊緣值會觸發代碼的bug，並且迭代器實現需要經過非常龐雜的測試。不過，其與其他STL算法能夠很好的兼容。