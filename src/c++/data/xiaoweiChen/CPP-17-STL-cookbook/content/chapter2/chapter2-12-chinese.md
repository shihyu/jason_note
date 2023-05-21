# 實現寫作風格助手用來查找文本中很長的句子——std::multimap

當有超級多的元素需要排序時，某些鍵值描述可能會出現多次，那麼使用`std::multimap`完成這項工作無疑是個不錯的選擇。

先找個應用場景：當使用德文寫作時，使用很長的句子是沒有問題的。不過，使用英文時，就不行了。我們將實現一個輔助工具來幫助德國作家們分析他們的英文作品，著重於所有句子的長度。為了幫助這些作家改善其寫作的文本風格，工具會按句子的長度對每個句子進行分組。這樣作家們就能挑出比較長的句子，然後截斷這些句子。

## How to do it...

本節中，我們將從標準輸入中獲取用戶輸入，用戶會輸入所有的句子，而非單詞。然後，我們將這些句子和其長度收集在`std::multimap`中。之後，我們將對所有句子的長度進行排序，打印給用戶看。

1. 包含必要的頭文件。`std::multimap`和`std::map`在同一個頭文件中聲明。

   ```c++
   #include <iostream>
   #include <iterator>
   #include <map>
   #include <algorithm>
   ```

2. 聲明所使用的命名空間。

   ```c++
   using namespace std;
   ```

3. 我們使用句號將輸入字符串分成若干個句子，句子中的每個單詞以空格隔開。句子中的一些對於句子長度無意義的符號，也會計算到長度中，所以，這裡要使用輔助函數將這些符號過濾掉。

   ```c++
   string filter_ws(const string &s)
   {
       const char *ws {" \r\n\t"};
       const auto a (s.find_first_not_of(ws));
       const auto b (s.find_last_not_of(ws));
       if (a == string::npos) {
       	return {};
       }
       return s.substr(a, b);
   }
   ```

4. 計算句子長度函數需要接收一個包含相應內容的字符串，並且返回一個`std::multimap`實例，其映射了排序後的句子長度和相應的句子。

   ```c++
   multimap<size_t, string> get_sentence_stats(const string &content)
   {
   ```

5. 這裡聲明一個`multimap`結構，以及一些迭代器。在計算長度的循環中，我們需要`end`迭代器。然後，我們使用兩個迭代器指向文本的開始和結尾。所有句子都在這個文本當中。

   ```c++
       multimap<size_t, string> ret;
       const auto end_it (end(content));
       auto it1 (begin(content));
       auto it2 (find(it1, end_it, '.'));
   ```

6. `it2`總是指向句號，而`it1`指向句子的開頭。只要`it1`沒有到達文本的末尾就好。第二個條件就是要檢查`it2`是否指向字符。如果不滿足這些條件，那麼就意味著這兩個迭代器中沒有任何字符了：

   ```c++
   	while (it1 != end_it && distance(it1, it2) > 0) {	
   ```

7. 我們使用兩個迭代器間的字符創建一個字符串，並且過濾字符串中所有的空格，只是為了計算句子純單詞的長度。

   ```c++
   		string s {filter_ws({it1, it2})};
   ```

8. 當句子中不包含任何字符，或只有空格時，我們就不統計這句。另外，我們要計算有多少單詞在句子中。這很簡單，每個單詞間都有空格隔開，單詞的數量很容易計算。然後，我們就將句子和其長度保存在`multimap`中。

   ```c++
           if (s.length() > 0) {
               const auto words (count(begin(s), end(s), ' ') + 1);
               ret.emplace(make_pair(words, move(s)));
           }
   ```

9. 對於下一次循環迭代，我們將會讓`it1`指向`it2`的後一個字符。然後將`it2`指向下一個句號。

   ```c++
           it1 = next(it2, 1);
           it2 = find(it1, end_it, '.');
       } 
   ```

10. 循環結束後，`multimap`包含所有句子以及他們的長度，這裡我們將其返回。

    ```c++
    	return ret;
    }
    ```

11. 現在，我們來寫主函數。首先，我們讓`std::cin`不要跳過空格，因為我們需要句子中有空格。為了讀取整個文件，我們使用`std::cin`包裝的輸入流迭代器初始化一個`std::string`實例。

    ```c++
    int main()
    {
        cin.unsetf(ios::skipws);
        string content {istream_iterator<char>{cin}, {}};
    ```

12. 只需要打印`multimap`的內容，在循環中調用`get_sentence_stats`，然後打印`multimap`中的內容。

    ```c++
        for (const auto & [word_count, sentence]
        		: get_sentence_stats(content)) {
       	 cout << word_count << " words: " << sentence << ".\n";
        }
    }
    ```

13. 編譯完成後，我們可以使用一個文本文件做例子。由於長句子的輸出量很長，所以先把最短的句子打印出來，最後打印最長的句子。這樣，我們就能首先看到最長的句子。

    ```
    $ cat lorem_ipsum.txt | ./sentence_length
    ...
    10 words: Nam quam nunc, blandit vel, luctus pulvinar,
    hendrerit id, lorem.
    10 words: Sed consequat, leo eget bibendum sodales,
    augue velit cursus nunc,.
    12 words: Cum sociis natoque penatibus et magnis dis
    parturient montes, nascetur ridiculus mus.
    17 words: Maecenas tempus, tellus eget condimentum rhoncus,
    sem quam semper libero, sit amet adipiscing sem neque sed ipsum.
    ```

## How it works...

整個例子中，我們將一個很長的字符串，分割成多個短句，從而評估每個句子的長度，並且在`multimap`中進行排序。因為`std::multimap`很容易使用，所以變成較為複雜的部分就在於循環，也就是使用迭代器獲取每句話的內容。

```c++
const auto end_it (end(content));

// (1) Beginning of string
auto it1 (begin(content)); 

// (1) First '.' dot
auto it2 (find(it1, end_it, '.')); 
while (it1 != end_it && std::distance(it1, it2) > 0) {
    string sentence {it1, it2};
    // Do something with the sentence string...
    
    // One character past current '.' dot
    it1 = std::next(it2, 1); 
    
    // Next dot, or end of string
    it2 = find(it1, end_it, '.'); 
}
```

將代碼和下面的圖結合起來可能會更好理解，這裡使用具有三句話的字符串來舉例。

![](../../images/chapter2/2-12-1.png)

`it1`和`it2`總是隨著字符串向前移動。通過指向句子的開頭和結尾的方式，確定一個句子中的內容。`std::find`算法會幫助我們尋找下一個句號的位置。

> std::find的描述：
>
> 從當前位置開始，返回首先找到的目標字符迭代器。如果沒有找到，返回結束迭代器。

這樣我們就獲取了一個句子，然後通過構造對應字符串的方式，將句子的長度計算出來，並將長度和原始句子一起插入`multimap`中。我們使用句子的長度作為元素的鍵，原句作為值存儲在`multimap`中。通常一個文本中，長度相同的句子有很多。這樣使用`std::map`就會比較麻煩。不過`std::multimap`就沒有重複鍵值的問題。這些鍵值也是排序好的，從而能得到用戶們想要的輸出。

## There's more...

將整個文件讀入一個大字符串中後，遍歷字符串時需要為每個句子創建副本。這是沒有必要的，這裡可以使用`std::string_view`來完成這項工作，該類型我們將會放在後面來介紹。

另一種從兩個句號中獲取句子的方法就是使用`std::regex_iterator`(正則表達式)，我們將會在後面的章節中進行介紹。

