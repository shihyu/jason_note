# 實現一個類似grep的文本搜索工具

大多數操作系統都會提供本地的搜索引擎。用戶可以使用一些快捷鍵，對本地文件進行查找。

這種功能出現之前，命令行用戶會通過`grep`或`awk`工具對文件進行查找。用戶可以簡單的輸入` grep -r foobar . `，然後工具將會基於當前目錄，進行遞歸的的查找，並顯示包含有`"foobar"`名字的文件。

本節中，將實現這樣一種應用。我們的`grep`使用命令行方式使用，並基於給定文件夾遞歸的對文件進行查找。然後，將找到的文件名打印出來。我們將使用線性的模式匹配方式，將匹配文件中的對應行號進行打印。

## How to do it...

我們將實現小工具，用於查找與用戶提供的文本段匹配的文件。這工具與UNIX中的`grep`工具類似，不過為了簡單起見，其功能沒有那麼強大：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <fstream>
   #include <regex>
   #include <vector>
   #include <string>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. 先來實現一個輔助函數，這個函數能接受一個文件地址和一個正則表達式對象，正則表達式對象用來描述我們要查找的文本段。然後，實例化一個`vector`，用於保存匹配的文件行和其對應的內容。然後，實例化一個輸入文件流對象，讀取文件，並進行逐行的文本匹配。

   ```c++
   static vector<pair<size_t, string>>
   matches(const path &p, const regex &re)
   {
       vector<pair<size_t, string>> d;
       ifstream is {p.c_str()};
   ```

3. 通過`getline`函數對文件進行逐行讀取，當字符串中包含有我們提供文本段，則`regex_search`返回true，如果匹配會將字符串和對應的行號保存在`vector`中。最後，我們將返回所有匹配的結果：

   ```c++
       string s;
       for (size_t line {1}; getline(is, s); ++line) {
           if (regex_search(begin(s), end(s), re)) {
           	d.emplace_back(line, move(s));
           }
       }
   
       return d;
   }
   ```

4. 主函數會先對用戶提供的文本段進行檢查，如果這個文本段不能用，則返回錯誤信息：

   ```c++
   int main(int argc, char *argv[])
   {
       if (argc != 2) {
           cout << "Usage: " << argv[0] << " <pattern>\n";
           return 1;
       }
   ```

5. 接下來，會通過輸入文本創建一個正則表達式對象。如果表達式是一個非法的正則表達式，這將會導致一個異常拋出。如果觸發了異常，我們將對異常進行捕獲並處理：

   ```c++
       regex pattern;
   
       try { pattern = regex{argv[1]}; }
       catch (const regex_error &e) {
           cout << "Invalid regular expression provided.n";
           return 1;
       }
   ```

6. 現在，可以對文件系統進行迭代，然後對我們提供的文本段進行匹配。使用`recursive_directory_iterator`對工作目錄下的所有文件進行迭代。原理和之前章節的`directory_iterator`類似，不過會對子目錄進行遞歸迭代。對於每個匹配的文件，我們都會調用輔助函數`matches`：

   ```c++
   	for (const auto &entry :
               recursive_directory_iterator{current_path()}) {
           auto ms (matches(entry.path(), pattern));
   ```

7. 如果有匹配的結果，我們將會對文件地址，對應文本行數和匹配行的內容進行打印：

   ```c++
       for (const auto &[number, content] : ms) {
           cout << entry.path().c_str() << ":" << number
           	 << " - " << content << '\n';
           }
       }
   }
   ```

8. 現在，準備一個文件`foobar.txt`，其中包含一些測試行：

   ```c++
   foo
   bar
   baz
   ```

9. 編譯並運行程序，就會得到如下輸出。我們在`/Users/tfc/testdir`文件夾下運行這個程序，我們先來對`bar`進行查找。在這個文件夾下，其會在`foobar.txt`的第二行和`testdir/dir1`文件夾下的另外一個文件`text1.txt`中匹配到：

   ```c++
   $ ./grepper bar
   /Users/tfc/testdir/dir1/text1.txt:1 - foo bar bla blubb
   /Users/tfc/testdir/foobar.txt:2 - bar
   ```

10. 再次運行程序，這次我們對`baz`進行查找，其會在第三行找到對應內容：

   ```c++
   $ ./grepper baz
   /Users/tfc/testdir/foobar.txt:3 - baz
   ```

##  How it works...

本節的主要任務是使用正則表達式對文件的內容進行查找。不過，讓我們關注一下`recursive_directory_iterator`，因為我們會使用這個迭代器來進行本節的子文件夾的遞歸迭代。

與`directory_iterator`和`recursive_directory_iterator`迭代類似，其可以用來對子文件夾進行遞歸，就如其名字一樣。當進入文件系統中的一個文件夾時，將會產生一個`directory_entry`實例。當遞歸到子文件夾時，也會產生對應的`directory_entry`實例。

`recursive_directory_iterator`具有一些有趣的成員函數：

- `depth()`代表我們需要迭代多少層子文件夾。
- `recursion_pending()`代表在進行當前迭代器後，是否會在進行對子文件夾進行迭代。
- `disable_recursion_pending()`當迭代器需要再對子文件夾進行迭代時，提前調用這個函數，則會讓遞歸停止。
- `pop()`將會終止當前級別的迭代，並返回上一級目錄。

## There's more...

我們需要了解的另一個就是`directory_options`枚舉類。`recursive_directory_iterator`能將`directory_options`的實例作為其構造函數的第二個參數，通常將` directory_options::none`作為默認值傳入。其他值為：

- `follow_directory_symlink`能允許對符號鏈接的文件夾進行遞歸迭代。
- `skip_permission_denied`這會告訴迭代器，是否跳過由於權限錯誤而無法訪問的目錄。

這兩個選項可以通過`|`進行組合。