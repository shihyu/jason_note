# 迭代器進行打印——std::ostream

使用輸出流進行打印是一件很容易的事情，STL中的大多數基本類型都對`operator<<`操作符進行過重載。所以使用`std::ostream_iterator`類，就可以將數據類型中所具有的的元素進行打印，我們已經在之前的章節中這樣做了。

本節中，我們將關注如何將自定義的類型進行打印，並且可以通過模板類進行控制。對於調用者來說，無需寫太多的代碼。

## How to do it...

我們將對一個新的自定義的類使用`std::ostream_iterator`，並且看起來其具有隱式轉換的能力，這就能幫助我們進行打印：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <vector>
   #include <iterator>
   #include <unordered_map>
   #include <algorithm>
   
   using namespace std;
   using namespace std::string_literals;
   ```

2. 讓我們實現一個轉換函數，其會將數字和字符串相對應。比如輸入1，就會返回“one”；輸入2，就會返回“two”，以此類推：

   ```c++
   string word_num(int i) {
   ```

3. 將會對哈希表進行填充，我們後續可以對它進行訪問：

   ```c++
   	unordered_map<int, string> m {
           {1, "one"}, {2, "two"}, {3, "three"},
           {4, "four"}, {5, "five"}, //...
   	};
   ```

4. 現在可以使用哈希表的`find`成員函數，通過傳入相應的鍵值，返回對應的值。如果`find`函數找不到任何東西，我們就會得到一個"unknown"字符串：

   ```c++
       const auto match (m.find(i));
       if (match == end(m)) { return "unknown"; }
       return match->second;
   }; 
   ```

5. 接下來我們就要定義一個結構體`bork`。其僅包含一個整型成員，其可以使用一個整型變量進行隱式構造。其具有`print`函數，其能接受一個輸出流引用，通過`borks`結構體的整型成員變量，重複打印"bork"字符串：

   ```c++
   struct bork {
       int borks;
       
       bork(int i) : borks{i} {}
       
       void print(ostream& os) const {
           fill_n(ostream_iterator<string>{os, " "},
           	   borks, "bork!"s);
       }
   };
   ```

6. 為了能夠更方便的對`bork`進行打印，對`operator<<`進行了重載，當通過輸出流對`bork`進行輸出時，其會自動的調用`bork::print`：

   ```c++
   ostream& operator<<(ostream &os, const bork &b) {
       b.print(os);
       return os;
   }
   ```

7. 現在來實現主函數，先來初始化一個`vector`:

   ```c++
   int main()
   {
   	const vector<int> v {1, 2, 3, 4, 5};
   ```

8. `ostream_iterator`需要一個模板參數，其能夠表述哪種類型的變量我們能夠進行打印。當使用`ostream_iterator<T>`時，其會使用` ostream& operator(ostream&, const T&)`進行打印。這也就是之前在`bork`類型中重載的輸出流操作符。我們這次只對整型數字進行打印，所以使用`ostream_iterator<int> `。使用`cout`進行打印，並可以將其作為構造參數。我們使用循環對`vector`進行訪問，並且對每個輸出迭代器`i`進行解引用。這也就是在STL算法中流迭代器的用法：

   ```c++
   	ostream_iterator<int> oit {cout};
       for (int i : v) { *oit = i; }
       cout << '\n';
   ```

9. 使用的輸出迭代器還不錯，不過其打印沒有任何分隔符。當需要空格分隔符對所有打印的元素進行分隔時，我們可以將空格作為第二個參數傳入輸出流構造函數中。這樣，其就能打印"1, 2, 3, 4, 5, "，而非"12345"。不過，不能在打印最後一個數字的時候將“逗號-空格”的字符串丟棄，因為迭代器並不知道哪個數字是最後一個：

   ```c++
       ostream_iterator<int> oit_comma {cout, ", "};
       
   	for (int i : v) { *oit_comma = i; }
       cout << '\n';
   ```

10. 為了將其進行打印，我們將值賦予一個輸出流迭代器。這個方法可以和算法進行結合，其中最簡單的方式就是`std::copy`。我們可以通過提供`begin`和`end`迭代器來代表輸入的範圍，在提供輸出流迭代器作為輸出迭代器。其將打印`vector`中的所有值。這裡我們會將兩個輸出循環進行比較：

   ```c++
   	copy(begin(v), end(v), oit);
   	cout << '\n';
   
   	copy(begin(v), end(v), oit_comma);
   	cout << '\n';
   ```

11. 還記得`word_num`函數嗎？其會將數字和字符串進行對應。我們也可以使用進行打印。我們只需要使用一個輸出流操作符，因為我們不需要對整型變量進行打印，所以這裡使用的是`string`的特化版本。使用`std::transfrom`替代`std::copy`，因為需要使用轉換函數將輸入範圍內的值轉換成其他值，然後拷貝到輸出中：

    ```c++
        transform(begin(v), end(v),
        		 ostream_iterator<string>{cout, " "}, word_num);
        cout << '\n';
    ```

12. 程序的最後一行會對`bork`結構體進行打印。可以直接使用，也並不需要為`std::transform`函數提供任何轉換函數。另外，可以創建一個輸出流迭代器，其會使用`bork`進行特化，然後再調用`std::copy`。`bork`實例可以通過輸入範圍內的整型數字進行隱式創建。然後，將會得到一些有趣的輸出：

    ```c++
        copy(begin(v), end(v),
        	 ostream_iterator<bork>{cout, "\n"});
    }
    ```

13. 編譯並運行程序，就會得到以下輸出。前兩行和第三四行的結果非常類似。然後，會得到數字對應的字符串，然後就會得到一堆`bork!`字符串。其會打印很多行，因為我們使用換行符替換了空格：

    ```c++
    $ ./ostream_printing
    12345
    1, 2, 3, 4, 5,
    12345
    1, 2, 3, 4, 5,
    one two three four five
    bork!
    bork! bork!
    bork! bork! bork!
    bork! bork! bork! bork!
    bork! bork! bork! bork! bork!
    ```

## How it works...

作為一個語法黑客，我們應知道`std::ostream_iterator`可以用來對數據進行打印，其在語法上為一個迭代器，對這個迭代器進行累加是無效的。對其進行解引用會返回一個代理對象，這些賦值操作符會將這些數字轉發到輸出流中。

輸出流迭代器會對類型T進行特化(`ostream_iterator<T> `)，對於所有類型的` ostream& operator<<(ostream&, const T&)`來說，都需要對其進行實現。

`ostream_iterator`總是會調用` operator<<`，通過模板參數，我們已經對相應類型進行了特化。如果類型允許，這其中會發生隱式轉換。當A可以隱式轉換為B時，我們可以對A類型的元素進行迭代，然後將這些元素拷貝到` output_iterator<B>`的實例中。我們會對`bork`結構體做同樣的事情：`bork`實例也可以隱式轉換為一個整數，這也就是我們能夠很容易的在終端輸出一堆`bork!`的原因。

如果不能進行隱式轉換，可使用`std::treansform`和`word_num`函數相結合，對元素類型進行轉換。

> Note：
>
> 通常，對於自定義類型來說，隱式轉換是一種不好的習慣，因為這是一個常見的Bug源，並且這種Bug非常難找。例子中，隱式構造函數有用程度要超過其危險程度，因為相應的類只是進行打印。