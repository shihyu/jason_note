# 計算文件類型的統計信息

上一節中，我們實現了一個用於統計任意文件夾中所有文件大小的工具。

本節中，我們將遞歸的對文件夾中的文件名後綴進行統計。這樣對每種文件類型的文件進行個數統計，並且計算每種文件類型大小的平均值。

## How to do it...

本節中將實現一個簡單的工具用於對給定的文件夾進行遞歸，同時對所有文件的數量和大小進行統計，並通過文件後綴進行分組。最後，會對文件夾中具有的文件名擴展進行打印，並打印出有多少個對應類型擴展的文件和文件的平均大小。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <sstream>
   #include <iomanip>
   #include <map>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. `size_string`函數已經在上一節中使用過了。這裡我們繼續使用：

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

3. 然後，實現一個函數用於接受一個`path`對象，並對該路徑下的所有文件進行遍歷。我們使用一個`map`來收集所有的信息，用對應的擴展名與總體數量和所有文件的總大小進行統計：

   ```c++
   static map<string, pair<size_t, size_t>> ext_stats(const path &dir)
   {
       map<string, pair<size_t, size_t>> m;
       
       for (const auto &entry :
       	recursive_directory_iterator{dir}) {	
   ```

4. 如果目錄入口是一個目錄，我們將跳過這個入口。跳過的意思就是不會對這個目錄進行遞歸操作。`recursive_directory_iterator`可以完成這個工作，但是不需要去查找所有文件夾中的文件。

   ```c++
           const path p {entry.path()};
           const file_status fs {status(p)};
   
           if (is_directory(fs)) { continue; }		
   ```

5. 接下來，會對文件的擴展名進行提取。如果文件沒有擴展名，就會對其進行忽略：

   ```c++
   		const string ext {p.extension().string()};
   
   		if (ext.length() == 0) { continue; }
   ```

6. 接著，計算我們查找到文件的總體大小。然後，將會對`map`中同一擴展的對象進行聚合。如果對應類型還不存在，創建起來也很容易。我們可以簡單的對文件計數進行增加，並且對擴展總體大小進行累加：

   ```c++
           const size_t size {file_size(p)};
   
           auto &[size_accum, count] = m[ext];
   
           size_accum += size;
           count += 1;
       }
   ```

7. 之後，我們會返回這個`map`：

   ```c++
   	return m;
   }
   ```

8. 主函數中，我們會從用戶提供的路徑中獲取對應的路徑，或是使用當前路徑。當然，需要對地址是否存在進行檢查，否則繼續下去就沒有任何意義：

   ```c++
   int main(int argc, char *argv[])
   {
       path dir {argc > 1 ? argv[1] : "."};
       
       if (!exists(dir)) {
           cout << "Path " << dir << " does not exist.\n";
           return 1;
       }
   ```

9. 可以對`ext_stats`進行遍歷。因為`map`中的`accum_size`元素包含有同類型擴展文件的總大小，然後用其除以總數量，以計算出平均值：

   ```c++
       for (const auto &[ext, stats] : ext_stats(dir)) {
           const auto &[accum_size, count] = stats;
           
           cout << setw(15) << left << ext << ": "
                << setw(4) << right << count
                << " items, avg size "
                << setw(4) << size_string(accum_size / count)
                << '\n';
       }
   }
   ```

10. 編譯並運行程序，我們將會得到如下的輸出。我將C++離線手冊的地址，作為命令行的參數：

  ```c++
  $ ./file_type ~/Documents/cpp_reference/
  .css :2 items, avg size 41K
  .gif :7 items, avg size 902B
  .html: 4355 items, avg size 38K
  .js:3 items, avg size 4K
  .php :1 items, avg size 739B
  .png : 34 items, avg size 2K
  .svg : 53 items, avg size 6K
  .ttf :2 items, avg size 421K
  ```


