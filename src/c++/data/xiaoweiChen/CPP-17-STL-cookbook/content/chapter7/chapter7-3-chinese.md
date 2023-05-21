# 無需構造獲取std::string

`std::string`類是一個十分有用的類，因為其對字符串的處理很方便。其有一個缺陷，當我們想要根據一個字符串獲取其子字符串時，我們需要傳入一個指針和一個長度變量，兩個迭代器或一段拷貝的子字符串。我在之前的章節也這樣使用過，消除字符串前後的空格的最後，使用的是拷貝的方式獲得前後無空格的字符串。

當我們想要傳遞一個字符串或一個子字符串到一個不支持`std::string`的庫中時，需要提供裸指針，這樣的用法就回退到C的時代。與子字符串問題一樣，裸指針不攜帶字符串長度信息。這樣的話就需要將指針和字符串長度進行捆綁。

另一個十分簡單的方式就是使用`std::string_view`。這個類是C++17添加的新特性，並且能提供將字符串指針與其長度捆綁的方法，其體現了數組引用的思想。

當設計函數時，將`std::string`實例作為參數，但在函數中使用了額外的內存來存儲這些字符，以確保原始的字符串不被修改，這時就可以使用`std::string_view`，其可移植性很好，與STL無關。可以讓其他庫來提供一個`string_view`實現，然後將複雜的實現隱藏在背後，並且可以將其用在我們的STL代碼中。這樣，`string_view`類就顯得非常小，非常好用，因為其能在不同的庫間都可以用。

`string_view`另一個很酷的特性，就是可以使用非拷貝的方式引用大字符串中的子字符串。本節將使用`string_view`，從而瞭解其優點和缺點。我們還會看到如何使用字符串代理來去除字符兩端的空格，並不對原始字符串進行修改和拷貝。

## How to do it...

本節，將使用`string_view`的一些特性來實現一個函數，我們將會看到有多少種類型可以輸入：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <string_view>
   
   using namespace std; 
   ```

2.  將`string_view`作為函數的參數：

   ```c++
   void print(string_view v)
   { 
   ```

3. 對輸入字符串做其他事情之前，將移除字符開頭和末尾的空格。將不會對字符串進行修改，僅適用字符串代理獲取沒有空格字符串。`find_first_not_of`函數將會在字符串找到第一個非空格的字符，適用`remove_prefix`，`string_view`將指向第一個非空格的字符。當字符串只有空格，`find_first_not_of`函數會返回`npos`，其為`size_type(-1)`。`size_type`是一個無符號類型，其可以是一個非常大的值。所以，會在字符串代理的長度和`words_begin`中選擇較小的那個：

   ```c++
   	const auto words_begin (v.find_first_not_of(" \t\n"));
   	v.remove_prefix(min(words_begin, v.size()));
   ```

4. 我們對尾部的空格做同樣的事情。`remove_suffix`將收縮到代理的大小：

   ```c++
   	const auto words_end (v.find_last_not_of(" \t\n"));
   	if (words_end != string_view::npos) {
   		v.remove_suffix(v.size() - words_end - 1);
   	} 
   ```

5. 現在可以打印字符串代理和其長度：

   ```c++
   	cout << "length: " << v.length()
   		 << " [" << v << "]\n";
   }
   ```

6. 主函數中，將使用`print`的函數答應一系列完全不同的參數類型。首先，會通過`argv`傳入`char*`類型的變量，運行時其會包含可執行文件的名字。然後，傳入一個`string_view`的實例。然後，使用C風格的靜態字符串，並使用`""sv`字面字符構造的`string_view`類型。最後，傳入一個`std::string`。`print`函數不需要對參數進行修改和拷貝。這樣就沒有多餘的內存分配發生。對於很多大型的字符串，這將會非常有效：

   ```c++
   int main(int argc, char *argv[])
   {
   	print(argv[0]);
   	print({});
   	print("a const char * array");
   	print("an std::string_view literal"sv);
   	print("an std::string instance"s); 
   ```

7. 這裡還沒對空格移除特性進行測試。這裡也給出一個頭尾都有空格的字符串：

   ```c++
   	print(" \t\n foobar \n \t "); 
   ```

8. `string_view`另一個非常酷的特性是，其給予的字符串是不包含終止符的。當構造一個字符串，比如"abc"，沒有終止符，`print`函數就能很安全的對其進行處理，因為`string_view`攜帶字符串的長度信息和指向信息：

   ```c++
   	char cstr[] {'a', 'b', 'c'};
   	print(string_view(cstr, sizeof(cstr)));
   }
   ```

9. 編譯並運行程序，就會得到如下的輸出，所有字符串都能被正確處理。前後有很多空格的字符串都被正確的處理，`abc`字符串沒有終止符也能被正確的打印，而沒有任何內存溢出：

   ```c++
   $ ./string_view
   length: 17 [./string_view]
   length: 0 []
   length: 20 [a const char * array]
   length: 27 [an std::string_view literal]
   length: 23 [an std::string instance]
   length: 6 [foobar]
   length: 3 [abc]
   ```

## How it works...

我們可以看到，函數可以接受傳入一個`string_view`的參數，其看起來與字符串類型沒有任何區別。我們實現的`print`，對於傳入的字符串不進行任何的拷貝。

對於`print(argv[0])`的調用是非常有趣的，字符串代理會自動的推斷字符串的長度，因為需要將其適用於無終止符的字符串。另外，我們不能通過查找終止符的方式來確定`string_view`實例的長度。正因如此，當使用裸指針(`string_view::data()`)的時候就需要格外小心。通常字符串函數都會認為字符串具有終止符，這樣就很難出現使用裸指針時出現內存溢出的情況。這裡還是使用字符串代理的接口比較好。

除此之外，`std::string`接口陣容已經非常豪華了。

> Note：
>
> 使用`std::string_view`用於解析字符或獲取子字符串時，能避免多餘的拷貝和內存分配，並且還不失代碼的舒適感。不過，對於`std::string_view`將終止符去掉這點，需要特別注意。

