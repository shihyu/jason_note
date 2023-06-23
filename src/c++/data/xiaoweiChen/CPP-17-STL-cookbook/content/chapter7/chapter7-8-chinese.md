# 迭代器填充容器——std::istream

上節中，我們學習瞭如何從輸入流中向數據結構中讀入數據，然後用這些數據填充列表或向量。

這次，我們將使用標準輸入來填充`std::map`。問題在於我們不能將一個結構體進行填充，然後從後面推入到線性容器中，例如`lis`t和`vector`，因為`map`的負載分為鍵和值兩部分。

完成本節後，我們會瞭解到如何從字符流中將複雜的數據結構進行序列化和反序列化。

## How to do it...

本節，我們會定義一個新的結構體，不過這次將其放入`map`中，這會讓問題變得複雜，因為容器中使用鍵值來表示所有值。

1. 包含必要的頭文件，並聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <map>
   #include <iterator>
   #include <algorithm>
   #include <numeric>
   
   using namespace std;
   ```

2. 我們會引用網絡上的一些梗。這裡的梗作為一個名詞，我們記錄其描述和誕生年份。我們會將這些梗放入`std::map`，其名稱為鍵，包含在結構體中的其他信息作為值：

   ```c++
   struct meme {
       string description;
       size_t year;
   };
   ```

3. 我們暫時先不去管鍵，我們先來實現結構體`meme`的流操作符`operator>>`。我們假設相關梗的描述由雙引號括起來，後跟對應年份。舉個栗子，` "some description" 2017`。通過使用`is >> quoted(m.description)`，雙引號會被當做限定符，直接被丟棄。這就非常的方便。然後我們繼續讀取年份即可：

   ```c++
   istream& operator>>(istream &is, meme &m) {
   	return is >> quoted(m.description) >> m.year;
   }
   ```

4. OK，現在將梗的名稱作為鍵插入`map`中。為了實現插入`map`，需要一個`std::pair<key_type, value_type>`實例。`key_type`為`string`，那麼`value_type`就是`meme`了。名字中允許出現空格，所以可以使用`quoted`對名稱進行包裝。`p.first`是名稱，`p.second`代表的是相關`meme`結構體變量。可以使用`operator>>`實現直接對其進行賦值：

   ```c++
   istream& operator >>(istream &is,
   				    pair<string, meme> &p) {
   	return is >> quoted(p.first) >> p.second;
   }
   ```

5. 現在來寫主函數，創建一個`map`實例，然後對其進行填充。因為對流函數`operator>>`進行了重載，所以可以直接對`istream_iterator`類型直接進行處理。我們將會從標準輸入中解析出更多的信息，然後使用`inserter`迭代器將其放入`map`中：

   ```c++
   int main()
   {
       map<string, meme> m;
       
       copy(istream_iterator<pair<string, meme>>{cin},
      		{},
       	inserter(m, end(m))); 
   ```

6. 對梗進行打印前，先在`map`中找到名稱最長的梗吧。可以對其使用`std::accumulate`。累加的初始值為0u(u為無符號類型)，然後逐個訪問`map`中的元素，將其進行合併。使用`accumulate`合併，就意味著疊加。例子中，並不是對數值進行疊加，而是對最長字符串的長度進行進行累加。為了得到長度，我們為`accumulate`提供了一個輔助函數`max_func`，其會將當前最大的變量與當前梗的名字長度進行比較(這裡兩個數值類型需要相同)，然後找出這些值中最大的那個。這樣`accumulate`函數將會返回當前梗中，名稱最長的梗：

   ```c++
       auto max_func ([](size_t old_max,
       				 const auto &b) {
       	return max(old_max, b.first.length());
       });
       size_t width {accumulate(begin(m), end(m),
       					    0u, max_func)};
   ```

7. 現在，對`map`進行遍歷，然後打印其中每一個元素。使用`<< left << setw(width)`打印出漂亮的“表格”：

   ```c++
       for (const auto &[meme_name, meme_desc] : m) {
           const auto &[desc, year] = meme_desc;
           
           cout << left << setw(width) << meme_name
                << " : " << desc
                << ", " << year << '\n';
       }
   }
   ```

8. 現在需要一些梗的數據，我們寫了一些梗在文件中：

   ```c++
   "Doge" "Very Shiba Inu. so dog. much funny. wow." 2013
   "Pepe" "Anthropomorphic frog" 2016
   "Gabe" "Musical dog on maximum borkdrive" 2016
   "Honey Badger" "Crazy nastyass honey badger" 2011
   "Dramatic Chipmunk" "Chipmunk with a very dramatic look" 2007
   ```

9. 編譯並運行程序，將文件作為數據庫進行輸入：

   ```c++
   $ cat memes.txt | ./filling_containers
   Doge: Very Shiba Inu. so dog. much funny. wow., 2013
   Dramatic Chipmunk : Chipmunk with a very dramatic look, 2007
   Gabe: Musical dog on maximum borkdrive, 2016
   Honey Badger: Crazy nastyass honey badger, 2011
   Pepe: Anthropomorphic frog, 2016
   ```

## How it works...

本節有三點需要注意。第一，沒有選擇`vector`或`list`比較簡單的結構，而是選擇了`map`這樣比較複雜的結構。第二，使用了`quoted`控制符對輸入流進行處理。第三，使用`accumulate`來找到最長的鍵值。

我們先來看一下`map`，結構體`meme`只包含一個`description`和`year`。因為我們將梗的名字作為鍵，所以沒有將其放入結構體中。可以將`std::pair`實例插入`map`中，首先實現了結構體`meme`的流操作符`operator>>`，然後對`pair<string, meme>`做同樣的事。最後，使用` istream_iterator<pair<string, meme>>{cin}`從標準輸入中獲取每個元素的值，然後使用` inserter(m, end(m)) `將組對插入`map`中。

當我們使用流對`meme`元素進行賦值時，允許梗的名稱和描述中帶有空格。我們使用引號控制符，很輕易的將問題解決，得到的信息類似於這樣，`"Name with spaces" "Description with spaces" 123`。

當輸入和輸出都對帶有引號的字符串進行處理時，`std::quoted`就能幫助到我們。當有一個字符串`s`，使用`cout << quoted(s)`對其進行打印，將會使其帶引號。當對流中的信息進行解析時，`cin >> quoted(s)`其就能幫助我們將引號去掉，保留引號中的內容。

疊加操作是對`max_func`的調用看起來很奇怪：

```c++
auto max_func ([](size_t old_max, const auto &b) {
	return max(old_max, b.first.length());
});

size_t width {accumulate(begin(m), end(m), 0u, max_func)};
```

實際上，`max_func`能夠接受一個`size_t`和一個`auto`類型的參數，這兩個參數將轉換成一個`pair`，從而就能插入`map`中。這看起來很奇怪，因為二元函數會將兩個相同類型的變量放在一起操作，例如`std::plus`。我們會從每個組對中獲取鍵值的長度，將當前元素的長度值與之前的最長長度相對比。

疊加調用會將`max_func`的返回值與0u值進行相加，然後作為左邊參數的值與下一個元素進行比較。第一次左邊的參數為0u，所以就可以寫成`max(0u, string_length)`，這時返回的值就作為之前最大值，與下一個元素的名稱長度進行比較，以此類推。