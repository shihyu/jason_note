# 計算文件中的單詞數量

我們在讀取一個文件的時候，也想知道這個文件中包含的單詞數量。我們定義的單詞是位於兩個空格之間的字符組合。那要如何進行統計呢？

根據對單詞的定義， 我們可以統計空格的數量。例如句子`John has a funny little dog.`，這裡有五個空格，所以說這句話有六個單詞。

如果句子中有空格幹擾怎麼辦，例如：`   John   has    \t   a\nfunny little dog  .`。這句中有很多不必要的空格、製表符和換行符。本書的其他章節中，我們已經瞭解如何將多餘空格從字符串中去掉。所以，可以對字符串進行預處理，將不必要的空格都去掉。這樣做的確可行，不過我們有更加簡單的方法。

為了尋找最優的解決方案，我們將讓用戶選擇，是從標準輸入中獲取數據，還是從文本文件中獲取數據。

## How to do it...

本節，我們將完成一個單行統計函數，其可以對輸入的數據進行計數，數據源的具體方式我們可以讓用戶來選擇。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <fstream>
   #include <string>
   #include <algorithm>
   #include <iterator>

   using namespace std;
   ```

2. `wordcount`函數能接受一個輸入流，例如`cin`。其能創建一個`std::input_iterator`迭代器，其能對輸出字符進行標記，然後交由`std::distance`進行計算。`distance`接受兩個迭代器作為參數，並確定從一個迭代器到另一個迭代器要用多少步(距離)。對於隨機訪問迭代器，因為有減法操作符的存在，所以實現起來非常簡單。其迭代器如同指針一樣，可以直接進行減法，計算出兩點的距離。不過`istream_iterator`就不行，因為其是前向迭代器，只能向前讀取，直至結束。最後所需要的步數也就是單詞的數量：

   ```c++
   template <typename T>
   size_t wordcount(T &is)
   {
   	return distance(istream_iterator<string>{is}, {});
   }
   ```

3. 主函數中，我們會讓用戶來選擇輸入源：

   ```c++
   int main(int argc, char **argv)
   {
   	size_t wc;
   ```

4. 如果用戶選擇使用文件進行輸入(例如：`./count_all_words some_textfile.txt`)，我們可以通過`argv`獲取命令行中的文件名稱，並將文件打開，讀取數據，從而對其文本進行單詞統計：

   ```c++
   	if (argc == 2) {
   		ifstream ifs {argv[1]};
   		wc = wordcount(ifs);
   ```

5. 如果用戶沒有傳入任何參數，就認為用戶要使用標準輸入流輸入數據：

   ```c++
   	} else {
   		wc = wordcount(cin);
   	}	
   ```

6. 然後只需要將統計出的單詞數量保存在變量`wc`中即可：

   ```c++
   	cout << "There are " << wc << " words\n";
   };
   ```

7. 編譯並運行程序。首先，從標準輸入中進行輸入。我們可以這裡通過echo命令將字符串，通過管道傳遞給程序。當然，我們也可以直接進行輸入，並使用`Ctrl+D`來結束輸入：

   ```c++
   $ echo "foo bar baz" | ./count_all_words
   There are 3 words
   ```

8. 這次我們使用文件作為輸入源，並對其中單詞數量進行統計：

   ```c++
   $ ./count_all_words count_all_words.cpp
   There are 61 words
   ```

## How it works...

本節也沒有什麼好多說的；實現很短，難度很低。需要提及的可能就是我們對`std::cin`和`std::ifstream`的實例進行了互換。`cin`是`std::istream`的類型之一，並且`std::ifstream`繼承於`std::istream`。可以回顧一下本章開頭的類型繼承表。這兩種類型即使在運行時，都能進行互換。

> Note：
>
> 使用流來保持代碼的模塊性，這有助於減少代碼的耦合性。因為其可以匹配任意類型的流對象，所以更容易對代碼進行測試。