# 實現一個自動文件重命名器

本節的動機是因為我自己經常需要使用到這樣的功能。我們將假日中的照片彙總在一起時，不同朋友的照片和視頻都在一個文件夾中，並且每個文件的後綴看起來都不一樣。一些JPEG文件有`.jpg`的擴展，而另一些為`.jpeg`，還有一些則為`.JPEG`。

一些人會讓文件具有統一的擴展，其會使用一些有用的命令對於所有文件進行重命名。同時，我們會將使用下劃線來替代空格。

本節中，我們將試下一個類似的工具，叫做`renamer`。其能接受一些列輸入文本段，作為其替代，類似如下的方式：

```c++
$ renamer jpeg jpg JPEG jpg
```

本節中，重命名器將會對當前目錄進行遞歸，然後找到文件後綴為`jpeg`和`JPEG`的所有文件，並將這些文件的後綴統一為`jpg`。

##  How to do it...

我們將實現一個工具，通過對文件夾的遞歸對於所有文件名匹配的文件進行重命名。所有匹配到的文件，都會使用用戶提供的文本段進行替換。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <regex>
   #include <vector>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. 我們將實現一個簡單的輔助函數，其能接受一個使用字符串表示的輸入文件地址和一組替換對。每一個替換對都有一個文本段和其要替換文本段。對替換範圍進行循環時，我們使用了`regex_replace`用於對輸入字符串進行匹配，然後返回轉換後的字符串。之後，我們將返回結果字符串。

   ```c++
   template <typename T>
   static string replace(string s, const T &replacements)
   {
       for (const auto &[pattern, repl] : replacements) {
       	s = regex_replace(s, pattern, repl);
       }
       
       return s;
   }
   ```

3. 主函數中，我們首先對命令行的正確性進行檢查。可以成對的接受命令行參數，因為我們想要匹配段和替換段相對應。`argv`的第一個元素為執行文件的名字。當用戶提供了成對的匹配段和替換段時，`argc`肯定是大於3的奇數：

   ```c++
   int main(int argc, char *argv[])
   {
       if (argc < 3 || argc % 2 != 1) {
           cout << "Usage: " << argv[0]
           	 << " <pattern> <replacement> ...\n";
           return 1;
       }
   ```

4. 我們對輸入對進行檢查時，會將對應的`vector`進行填充：

   ```c++
       vector<pair<regex, string>> patterns;
   
       for (int i {1}; i < argc; i += 2) {
       	patterns.emplace_back(argv[i], argv[i + 1]);
       }
   ```

5. 現在，可以對整個文件系統進行遍歷。簡單起見，將當前目錄作為遍歷的默認起始地址。對於每一個文件夾入口，我們將其原始路徑命名為`opath`。然後，只在沒有剩餘路徑的情況下使用文件名，並根據之前創建的匹配列表，對對應的匹配段進行替換。我們將拷貝`opath`到`rpath`中，並且將文件名進行替換。

   ```c++
       for (const auto &entry :
       		recursive_directory_iterator{current_path()}) {
      		 		path opath {entry.path()};
       			string rname {replace(opath.filename().string(),
       			patterns)};
           
           path rpath {opath};
           rpath.replace_filename(rname);
   ```

6. 對於匹配的文件，我們將打印其重命名後的名字。當重命名後的文件存在，我們將不會對其進行處理。會跳過這個文件。當然，我們也可以添加一些數字或其他字符到地址中，從而解決這個問題：

   ```c++
           if (opath != rpath) {
               cout << opath.c_str() << " --> "
               	<< rpath.filename().c_str() << '\n';
               if (exists(rpath)) {
               	cout << "Error: Can't rename."
               		" Destination file exists.\n";
               } else {
               	rename(opath, rpath);
               }
           }
       }
   }
   ```

7. 編譯並運行程序，我們將會得到如下的輸出。我的文件夾下面有一些JPEG文件，但是都是以不同的後綴名結尾，有`jpg`，`jpeg`和`JPEG`。然後，執行程序將`jpeg`和`JPEG`替換成`jpg`。這樣，就可以對文件名進行統一化。

   ```c++
   $ ls
   birthday_party.jpeg holiday_in_dubai.jpgholiday_in_spain.jpg
   trip_to_new_york.JPEG
   $ ../renamer jpeg jpg JPEG jpg
   /Users/tfc/pictures/birthday_party.jpeg --> birthday_party.jpg
   /Users/tfc/pictures/trip_to_new_york.JPEG --> trip_to_new_york.jpg
   $ ls
   birthday_party.jpg holiday_in_dubai.jpg holiday_in_spain.jpg
   trip_to_new_york.jpg
   ```
