# 實現一個工具：通過符號鏈接減少重複文件，從而控制文件夾大小

很多工具以不同的方式對數據進行壓縮。其中最著名的文件壓縮算法/格式就是ZIP和RAR。這種工具通過減少文件內部冗餘，從而減少文件的大小。

將文件壓縮成壓縮包外，另一個非常簡單的減少磁盤使用率的範式就是刪除重複的文件。本節中，我們將實現一個小工具，其會對目錄進行遞歸。遞歸中將對文件內容進行對比，如果找到相同的文件，我們將對其中一個進行刪除。所有刪除的文件則由一個符號鏈接替代，該鏈接指向目前唯一存在的文件。這種方式可以不通過壓縮對空間進行節省，同時對所有的數據能夠進行保存。

## How to do it...

本節中，將實現一個小工具用來查找那些重複的文件。我們將會刪除其中一個重複的文件，並使用符號鏈接的方式對其進行替換，這樣就能減小文件夾的大小。

> Note：
>
> 為了對系統數據進行備份，我們將使用STL函數對文件進行刪除。一個簡單的拼寫錯誤就可能會刪除很多並不想刪除的文件。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <fstream>
   #include <unordered_map>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. 為了查找重複的文件，我們將構造一個哈希表，並對將文件哈希值與其第一次產生的地址相對應。最好的方式就是通過哈希算法，對文件計算出一個MD5或SHA碼。為了保證例子的簡潔，我們將會把文件讀入一個字符串中，然後使用`hash`函數計算出對應的哈希值：

   ```c++
   static size_t hash_from_path(const path &p)
   {
       ifstream is {p.c_str(),
       	ios::in | ios::binary};
       if (!is) { throw errno; }
       
       string s;
       
       is.seekg(0, ios::end);
       s.reserve(is.tellg());
       is.seekg(0, ios::beg);
       
       s.assign(istreambuf_iterator<char>{is}, {});
       
       return hash<string>{}(s);
   }
   ```

3. 然後，我們會實現一個哈希表，並且刪除重複的文件。其會對當前文件夾和其子文件夾進行遍歷：

   ```c++
   static size_t reduce_dupes(const path &dir)
   {
       unordered_map<size_t, path> m;
       size_t count {0};
       
       for (const auto &entry :
       	 recursive_directory_iterator{dir}) { 
   ```

4. 對於每個文件入口，我們都會進行檢查，當其是文件夾時就會跳過。對於每一個文件，我們都會產生一個哈希值，並且嘗試將其插入哈希表中。當哈希表已經包含有相同的哈希值，這也就意味著有文件重複了。並且插入操作會終止，`try_emplace`所返回的第二個值就是false:

   ```c++
       const path p {entry.path()};
   
       if (is_directory(p)) { continue; }
   
       const auto &[it, success] =
           m.try_emplace(hash_from_path(p), p);
   ```

5. `try_emplace`的返回值將告訴我們，該鍵是否是第一次插入的。這樣我們就能找到重複的，並告訴用戶文件有重複的，並將重複的進行刪除。刪除之後，我們將為重複的文件創建符號鏈接：

   ```c++
       if (!success) {
           cout << "Removed " << p.c_str()
                << " because it is a duplicate of "
                << it->second.c_str() << '\n';
           
           remove(p);
           create_symlink(absolute(it->second), p);
           ++count;
       }	
   ```

6. 對文件系統進行插入後，我們將會返回重複文件的數量：

   ```c++
   	}
   
   	return count;
   }
   ```

7. 主函數中，我們會對用戶在命令行中提供的目錄進行檢查。

   ```c++
   int main(int argc, char *argv[])
   {
       if (argc != 2) {
           cout << "Usage: " << argv[0] << " <path>\n";
           return 1;
       }
       
       path dir {argv[1]};
       
       if (!exists(dir)) {
           cout << "Path " << dir << " does not exist.\n";
           return 1;
       }
   ```

8. 現在我們只需要對`reduce_dupes`進行調用，並打印出有多少文件被刪除了：

   ```c++
       const size_t dupes {reduce_dupes(dir)};
   
       cout << "Removed " << dupes << " duplicates.\n";
   }
   ```

9. 編譯並運行程序，輸出中有一些看起來比較複雜的文件。程序執行之後，我會使用`du`工具來檢查文件夾的大小，並證明這種方法是有效的。

   ```c++
   $ du -sh dupe_dir
   1.1Mdupe_dir
   
   $ ./dupe_compress dupe_dir
   Removed dupe_dir/dir2/bar.jpg because it is a duplicate of
   dupe_dir/dir1/bar.jpg
   Removed dupe_dir/dir2/base10.png because it is a duplicate of
   dupe_dir/dir1/base10.png
   Removed dupe_dir/dir2/baz.jpeg because it is a duplicate of
   dupe_dir/dir1/baz.jpeg
   Removed dupe_dir/dir2/feed_fish.jpg because it is a duplicate of
   dupe_dir/dir1/feed_fish.jpg
   Removed dupe_dir/dir2/foo.jpg because it is a duplicate of
   dupe_dir/dir1/foo.jpg
   Removed dupe_dir/dir2/fox.jpg because it is a duplicate of
   dupe_dir/dir1/fox.jpg
   Removed 6 duplicates.
       
   $ du -sh dupe_dir
   584Kdupe_dir
   ```

## How it works...

使用`create_symlink`函數在文件系統中鏈接一個文件，指向另一個地方。這樣就能避免重複的文件出現，也可以使用`create_hard_link`設置一些硬鏈接。硬鏈接和軟連接相比，有不同的技術含義。有些格式的文件系統可能不支持硬鏈接，或者是使用一定數量的硬鏈接，指向相同的文件。另一個問題就是，硬鏈接沒有辦法讓兩個文件系統進行鏈接。

不過，除開實現細節，使用`create_symlink`或`create_hard_link`時，會出現一個明顯的錯誤。下面的幾行代碼中就有一個bug。你能很快的找到它嗎？

```c++
path a {"some_dir/some_file.txt"};
path b {"other_dir/other_file.txt"};
remove(b);
create_symlink(a, b);
```

在程序執行的時候，不會發生任何問題，不過符號鏈接將失效。符號鏈接將錯誤的指向`some_dir/some_file.txt`。正確指向的地址應該是`/absolute/path/some_dir/some_file.txt`或`../some_dir/some_file.txt`。`create_symlink`使用正確的絕對地址，可以使用如下寫法：

 ```c++
create_symlink(absolute(a), b);
 ```

> Note：
>
> `create_symlink`不會對鏈接進行檢查

## There's more...

可以看到，哈希函數非常簡單。為了讓程序沒有多餘的依賴，我們採用了這種方式。

我們的哈希函數有什麼問題呢？有兩個問題：

- 會將一個文件完全讀入到字符串中。如果對於很大的文件來說，這將是一場災難。
- C++ 中的哈希函數`  hash<string>`可能不是這樣使用的。

要尋找一個更好的哈希函數時，我們需要找一個快速、內存友好、簡單的，並且保證不同的文件具有不同的哈希值，最後一個需求可能是最關鍵的。因為我們使用哈希值了判斷兩個文件是否一致，當我們認為兩個文件一致時，但哈希值不一樣，就能肯定有數據受到了損失。

比較好的哈希算法有MD5和SHA(有變體)。為了讓我們程序使用這樣的函數，可能需要使用OpenSSL中的密碼學API。

