# 列出目錄下的所有文件

每個操作系統都會提供一些工具，以列出目錄下的所有文件。Linux，MacOS和類UNIX的操作系統中，`ls`就是一個最簡單的例子。Windows和Dos系統下，命令為`dir`。其會提供一些文件的補充信息，比如文件大小，訪問權限等。

可以通過對文件夾的遞歸和文件遍歷來對這樣的工具進行實現。所以，讓我們來試一下吧！

我們的`ls/dir`命令會將目錄下的文件名，元素索引，以及一些訪問權限標識，以及對應文件的文件大小，分別進行展示。

## How to do it...

本節中，我們將實現一個很小的工具，為使用者列出對應文件夾下的所有文件。會將文件名，文件類型，大小和訪問權限分別列出來。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <sstream>
   #include <iomanip>
   #include <numeric>
   #include <algorithm>
   #include <vector>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. `file_info`是我們要實現的一個輔助函數。其能接受一個`directory_entry`對象的引用，並從這個路徑中提取相應的信息，實例化`file_status`對象(使用`status`函數)，其會包含文件類型和權限信息。最後，如果是一個常規文件，則會提取其文件大小。對於文件夾或一些特殊的文件，我們將返回大小設置為0。所有的信息都將會封裝到一個元組中：

   ```c++
   static tuple<path, file_status, size_t>
   file_info(const directory_entry &entry)
   {
       const auto fs (status(entry));
       return {entry.path(),
               fs,
               is_regular_file(fs) ? file_size(entry.path()) : 0u};
   }
   ```

3. 另一個輔助函數就是`type_char`。路徑不能僅表示目錄和簡單文本/二進制文件。操作系統提供了多種抽象類型，比如字符/塊形式的硬件設備接口。STL庫也提供了為此提供了很多為此函數。我們通過返回`'d'`表示文件夾，通過返回`'f'`表示普通文件等。

   ```c++
   static char type_char(file_status fs)
   {
       if (is_directory(fs)) { return 'd'; }
       else if (is_symlink(fs)) { return 'l'; }
       else if (is_character_file(fs)) { return 'c'; }
       else if (is_block_file(fs)) { return 'b'; }
       else if (is_fifo(fs)) { return 'p'; }
       else if (is_socket(fs)) { return 's'; }
       else if (is_other(fs)) { return 'o'; }
       else if (is_regular_file(fs)) { return 'f'; }
       
       return '?';
   }
   ```

4. 下一個輔助函數為`rwx`。其能接受一個`perms`變量(其為文件系統庫的一個`enum`類)，並且會返回一個字符串，比如`rwxrwxrwx`，用來表示文件的權限設置。`"rwx" `分別為**r**ead, **w**rite和e**x**ecution，分別代表了文件的權限屬性。每三個字符表示一個組，也就代表對應的組或成員，能對文件進行的操作。`rwxrwxrwx`則代表著每個人多能對這個文件進行訪問和修改。`rw-r--r--`代表著所有者可以的對文件進行讀取和修改，不過其他人只能對其進行讀取操作。我們將這些`讀取/修改/執行`所代表的字母進行組合，就能形成文件的訪問權限列表。Lambda表達式可以幫助我們完成重複性的檢查工作，檢查`perms`變量`p`中是否包含特定的掩碼位，然後返回`'-'`或正確的字符。

   ```c++
   static string rwx(perms p)
   {
       auto check ([p](perms bit, char c) {
       	return (p & bit) == perms::none ? '-' : c;
       });
       return {check(perms::owner_read, 'r'),
               check(perms::owner_write, 'w'),
               check(perms::owner_exec, 'x'),
               check(perms::group_read, 'r'),
               check(perms::group_write, 'w'),
               check(perms::group_exec, 'x'),
               check(perms::others_read, 'r'),
               check(perms::others_write, 'w'),
               check(perms::others_exec, 'x')};
   }
   ```

5. 最後一個輔助函數能接受一個整型的文件大小，並將其轉換為跟容易讀懂的模式。將其大小除以表示的對應邊界，然後使用K, M或G來表示這個文件的大小：

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

6. 現在來實現主函數。我們會對用戶在命令行輸入的路徑進行檢查。如果沒有傳入，則默認為當前路徑。然後，再來檢查文件夾是否存在。如果不存在，就不會列出任何文件：

   ```c++
   int main(int argc, char *argv[])
   {
       path dir {argc > 1 ? argv[1] : "."};
       
       if (!exists(dir)) {
           cout << "Path " << dir << " does not exist.\n";
           return 1;
       }
   ```

7. 現在，將使用文件信息元組來填充一個`vector`。實例化一個`directory_iterator`，並且將其傳入`path`對象的構造函數中。並通過目錄迭代器對文件進行迭代，我們將`directory_entry`對象轉換成文件信息元組，然後將其插入相應的`vector`。

   ```c++
       vector<tuple<path, file_status, size_t>> items;
       
       transform(directory_iterator{dir}, {},
       	back_inserter(items), file_info);	
   ```

8. 現在，將所有文件的信息都存在於`vector`之中，並且使用輔助函數將其進行打印：

   ```c++
       for (const auto &[path, status, size] : items) {
           cout << type_char(status)
                << rwx(status.permissions()) << " "
                << setw(4) << right << size_string(size)
                << " " << path.filename().c_str()
                << '\n';
   	}
   }
   ```

9. 編譯並運行程序，並通過命令行傳入C++文檔文件所在的地址。我們能瞭解到對應文件夾所包含的文件，因為文件夾下只有`'d'`和`'f'`作為輸出的表示。這些文件具有不同的權限，並且都有不同的大小。需要注意的是，這些文件的顯示順序，是按照名字在字母表中的順序排序，不過我們不依賴這個順序，因為C++17標準不需要字母表排序：

   ```c++
   $ ./list ~/Documents/cpp_reference/en/cpp
   drwxrwxr-x 0B   algorithm
   frw-r--r-- 88K  algorithm.html
   drwxrwxr-x 0B   atomic
   frw-r--r-- 35K  atomic.html
   drwxrwxr-x 0B   chrono
   frw-r--r-- 34K  chrono.html
   frw-r--r-- 21K  comment.html
   frw-r--r-- 21K  comments.html
   frw-r--r-- 220K compiler_support.html
   drwxrwxr-x 0B   concept
   frw-r--r-- 67K  concept.html
   drwxr-xr-x 0B   container
   frw-r--r-- 285K container.html
   drwxrwxr-x 0B   error
   frw-r--r-- 52K  error.html
   ```

## How it works...

本節中，我們迭代了文件夾中的所有文件，並且對每個文件的狀態和大小進行檢查。對於每個文件的操作都非常直接和簡單，我們對文件夾的遍歷看起來也很魔幻。

為了對我們的文件夾進行遍歷，只是對`directory_iterator`進行實例化，然後對該對象進行遍歷。使用文件系統庫來遍歷一個文件夾是非常簡單的。

```c++
for (const directory_entry &e : directory_iterator{dir}) {
	// do something
}
```

除了以下幾點，`directory_iterator`也沒有什麼特別的：

- 會對文件夾中的每個文件訪問一次
- 文件中元素的遍歷順序未指定
- 文件節元素中`.`和`..`都已經被過濾掉

不過，`directory_iterator`看起來是一個迭代器，並且同時具有一個可迭代的範圍。為什麼需要注意這個呢？對於簡單的`for`循環來說，其需要一個可迭代的範圍。本節例程中，我們會將其當做一個迭代器使用：

```c++
transform(directory_iterator{dir}, {},
		 back_inserter(items), file_info);
```

實際上，就是一個迭代器類型，只不過這個類將`std::begin`和`std::end`函數進行了重載。當調用`begin`和`end`時，其會返回相應的迭代器。雖說第一眼看起來比較奇怪，但是讓這個類型的確更加有用。