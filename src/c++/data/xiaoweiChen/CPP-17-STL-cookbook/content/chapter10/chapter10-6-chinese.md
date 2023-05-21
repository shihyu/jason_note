# 實現一個磁盤使用統計器

我們已經實現了一個列出文件夾下所有文件的工具，不過和系統自帶的工具一樣，其都不會對文件夾的大小進行打印。

為了獲取文件夾的大小，我們需要將其子文件夾進行迭代，然後將其包含的所有文件的大小進行累加，才能得到該文件夾的大小。

本節中，我們將實現一個工具用來做這件事。這個工具能在任意的文件夾下運行，並且對文件夾中包含的文件總體大小進行統計。

## How to do it...

本節中，我們將會實現一個程序用於迭代目錄中的所有文件，並將所有文件的大小進行統計。對於統計一個文件的大小就很簡單，但是要統計一個文件夾的大小，就需要將文件夾下的所有文件的大小進行相加。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <sstream>
   #include <iomanip>
   #include <numeric>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. 我們將實現一個輔助函數使用`directory_entry`對象作為其參數，然後返回其在文件系統中對應的大小。如果傳入的不是一個文件夾地址，將通過`file_size`獲得文件的大小。

   ```c++
   static size_t entry_size(const directory_entry &entry)
   {
   	if (!is_directory(entry)) { return file_size(entry); }
   ```

3. 如果傳入的是一個文件夾，需要對其中所有元素進行文件大小的計算。需要調用輔助函數`entry_size`對子文件夾進行再次遞歸：

   ```c++
       return accumulate(directory_iterator{entry}, {}, 0u,
           [](size_t accum, const directory_entry &e) {
           	return accum + entry_size(e);
           });
   }
   ```

4. 為了具有更好的可讀性，本節使用了其他章節中的`size_string`函數。

   ```c++
   static string size_string(size_t size)
   {
       stringstream ss;
       if (size >= 1000000000) {
       	ss << (size / 1000000000) << 'G';
       } else if (size >= 1000000) {
       	ss << (size / 1000000) << 'M';
       } else if (size >= 1000) {
       	ss << (size / 1000) << 'K';
       } else { ss << size << 'B'; }
       
       return ss.str();
   }
   ```

5. 主函數中，首先就是要檢查用戶通過命令行提供的文件系統路徑。如果沒有提供，則默認為當前文件夾。處理之前，我們會檢查路徑是否存在。

   ```c++
   int main(int argc, char *argv[])
   {
       path dir {argc > 1 ? argv[1] : "."};
       
       if (!exists(dir)) {
       cout << "Path " << dir << " does not exist.\n";
       	return 1;
       } 
   ```

6. 現在，我們可以對所有的文件夾進行迭代，然後打印其名字和大小：

   ```c++
       for (const auto &entry : directory_iterator{dir}) {
           cout << setw(5) << right
                << size_string(entry_size(entry))
                << " " << entry.path().filename().c_str()
                << '\n';
       }
   }
   ```

7. 編譯並運行程序，我們將獲得如下的輸出。我提供了一個C++離線手冊的目錄，其當然具有子目錄，我們可以用我們的程序對其大小進行統計：

   ```c++
   $ ./file_size ~/Documents/cpp_reference/en/
   19M c
   12K c.html
   147M cpp
   17K cpp.html
   22K index.html
   22K Main_Page.html
   ```

## How it works...

整個程序通過`file_size`對普通的文件進行大小的統計。當程序遇到一個文件夾，其將會對子文件夾進行遞歸，然後通過`file_size`計算出文件夾中包含所有文件的大小。

有件事我們需要區別一下，當我們直接調用`file_size`時，或需要進行遞歸時，需要通過`is_directory`謂詞進行判斷。這對於只包含有普通文件和文件夾的文件夾是有用的。

與我們的簡單程序一樣，程序會在如下的情況下崩潰，因為有未處理的異常拋出：

- `file_size`只能對普通文件和符號鏈接有效。否則，會拋出異常。
- `file_size`對符號鏈接有效，如果鏈接失效，函數還是會拋出異常。

為了讓本節的程序更加成熟，我們需要更多的防禦性編程，避免遇到錯誤的文件和手動處理異常。

