# 改變容器內容

如果說`std::copy`是STL中最簡單的算法，那麼`std::transform`就是第二簡單的算法。和`copy`類似，其可將容器某一範圍的元素放置到其他容器中，在這個過程中允許進行一些變換(變換函數會對輸入值進行一定操作，然後再賦給目標容器)。此外，兩個具有不同元素類型的容間也可以使用這個函數。這個函數超級簡單，並且非常有用，這個函數會讓標準組件具有更好的可移植性。

## How to do it...

本節，我們將使用`std::transform`在拷貝的同時，修改`vector`中的元素：

1. 包含必要的頭文件，並且聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <vector>
   #include <string>
   #include <sstream>
   #include <algorithm>
   #include <iterator>

   using namespace std;
   ```

2. `vector`由簡單的整數組成：

   ```c++
   int main()
   {
   	vector<int> v {1, 2, 3, 4, 5};
   ```

3. 為了打印元素，會將所有元拷貝素到`ostream_iterator`適配器中。`transform`函數可以接受一個函數對象，其能在拷貝過程中對每個元素進行操作。這個例子中，我們將計算每個元素的平方值，所以代碼將打印出平方數。因為直接進行了打印，所以平方數並沒有進行保存：

   ```c++
       transform(begin(v), end(v),
           ostream_iterator<int>{cout, ", "},
           [] (int i) { return i * i; });
       cout << '\n';
   ```

4. 再來做另一個變換。例如，對於數字3來說，顯示成`3^2 = 9`顯然有更好的可讀性。下面的輔助函數`int_to_string`函數對象就會使用`std::stringstream`對象進行打印操作：

   ```c++
   auto int_to_string ([](int i) {
       stringstream ss;
       ss << i << "^2 = " << i * i;
       return ss.str();
   });
   ```

5. 這樣就可以將整型值放入字符串中。可以說我麼將這個證書映射到字符串中。使用`transform`函數，使我們可以拷貝所有數值到一個字符串`vector`中：

   ```c++
       vector<string> vs;

       transform(begin(v), end(v), back_inserter(vs),
       	int_to_string);
   ```

6. 在打印完成後，我們的例子就結束了：

   ```c++
       copy(begin(vs), end(vs),
      		ostream_iterator<string>{cout, "\n"});
   }
   ```

7. 編譯並運行程序：

   ```c++
   $ ./transforming_items_in_containers
   1, 4, 9, 16, 25,
   1^2 = 1
   2^2 = 4
   3^2 = 9
   4^2 = 16
   5^2 = 25
   ```

## How it works...

`std::transform`函數工作原理和`std::copy`差不多，不過在拷貝的過程中會對源容器中的元素進行變換，這個變換函數由用戶提供。