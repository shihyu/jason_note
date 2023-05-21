# 快速或安全的訪問std::vector實例的方法

`std::vector`可能是STL容器中適用範圍最廣的，因為其存儲數據的方式和數組一樣，並且還有相對完善的配套設施。不過，非法訪問一個`vector`實例還是十分危險的。如果一個`vector`實例具有100個元素，那當我們想要訪問索引為123的元素時，程序就會崩潰掉。如果不崩潰，那麼你就麻煩了，未定義的行為會導致一系列奇奇怪怪的錯誤，查都不好查。經驗豐富的開發者會在訪問前，對索引進行檢查。這樣的檢查其實比較多餘，因為很多人不知道`std::vector`有內置的檢查機制。

## How to do it...

本節我們將使用兩種不同的方式訪問一個`std::vector`實例，並且利用其特性編寫更加安全的代碼。

1. 先包含相應的頭文件，並且用1000個123填滿一個vector實例：

   ```c++
   #include <iostream>
   #include <vector>
   using namespace std;
   int main()
   {
       const size_t container_size{1000};
       vector<int> v(container_size, 123);
   ```

2. 我們通過`[]`操作符訪問範圍之外的元素：

   ```c++
       cout << "Out of range element value: "
            << v[container_size + 10] << '\n';
   ```

3. 之後我們使用`at`函數訪問範圍之外的元素：

   ```c++
       cout << "Out of range element value: "
            << v.at(container_size + 10) << '\n';
   }
   ```

4. 讓我們運行程序，看下會發生什麼。下面的錯誤信息是由GCC給出。其他編譯器也會通過不同方式給出類似的錯誤提示。第一種方式得到的結果比較奇怪。超出範圍的訪問方式並沒有讓程序崩潰，但是訪問到了與123相差很大的數字。第二種方式中，我們看不到打印出來的結果，因為在打印之前程序已經崩潰了。當越界訪問發生的時候，我們可以通過異常的方式更早的得知！

   ```c++
   Out of range element value: -726629391
   terminate called after throwing an instance of 'std::out_of_range'
   what(): array::at: __n (which is 1010) >= _Nm (which is 1000)
   Aborted (core dumped)
   ```

## How it works...

`std::vector`提供了`[]`操作符和`at`函數，它們的作用幾乎是一樣的。`at`函數會檢查給定的索引值是否越界，如果越界則返回一個異常。這對於很多情景都十分適用，不過因為檢查越界要花費一些時間，所以`at`函數會讓程序慢一些。

當需要非常快的索引成員時，並能保證索引不越界，我們會使用`[]`快速訪問`vector`實例。很多情況下，`at`函數在犧牲一點性能的基礎上，有助於發現程序內在的bug。

> Note：
>
> 默認使用`at`函數是一個好習慣。當代碼的性能很差，但沒有bug存在時，可以使用性能更高的操作符來替代`at`函數。

## There's more...

當然，我們需要處理越界訪問，避免整個程序崩潰。為了對越界訪問進行處理，我們可以使用截獲異常的方式。可以用`try`代碼塊將調用at函數的部分包圍，並且定義錯誤處理的`catch`代碼段。

```c++
try {
	std::cout << "Out of range element value: "
        	  << v.at(container_size + 10) << '\n';
} catch (const std::out_of_range &e) {
	std::cout << "Ooops, out of range access detected: "
              << e.what() << '\n';
}
```

> Note:
>
> 順帶一提，`std::array`也提供了`at`函數。

