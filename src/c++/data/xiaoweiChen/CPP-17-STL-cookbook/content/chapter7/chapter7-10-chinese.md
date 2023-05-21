# 使用特定代碼段將輸出重定向到文件

`std::cout`為我們提供了一種非常方便的打印方式，使用起來也十分方便，易於擴展，並可全局訪問。即使我們想打印對應的信息時，比如錯誤信息，我們可以使用錯誤輸出`std::cerr`進行輸出，其和`cout`的用法一樣，只不過一個從標準通道進行輸出，另一個從錯誤通道進行輸出。

當我們要打印比較複雜的日誌信息時。比如，要將函數的輸出重定向到一個文件中，或者將函數的打印輸出處於靜默狀態，而不需要對函數進行任何修改。或許這個函數為一個庫函數，我們沒有辦法看到其源碼。可能，這個函數並沒有設計為寫入到文件的函數，但是我們還是想將其輸出輸入到文件中。

這裡可以重定向輸出流對象的輸出。本節中，我們將看到如何使用一種簡單並且優雅地方式來完成輸出流的重定向。

## How to do it...

我們將實現一個輔助類，其能在構造和析構階段，幫助我們完成流的重定向，以及對流的定向進行恢復。然後，我們來看其是怎麼使用的：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <fstream>
   
   using namespace std;
   ```

2. 我們實現了一個類，其具有一個文件輸出流對象和一個指向流內部緩衝區的指針。`cout`作為流對象，其內部具有一個緩衝區，其可以用來進行數據交換，我們可以保存我們之前做過的事情，這樣就很方便進行對後續修改的撤銷。我們可以在C++手冊中查詢對其返回類型的解釋，也可以使用`decltype`對`cout.rdbuf()`所返回的類型進行查詢。這並不是一個很好的體驗，在我們的例子中，其就是一個指針類型：

   ```c++
   class redirect_cout_region
   {
       using buftype = decltype(cout.rdbuf());
       
       ofstream ofs;
       buftype buf_backup; 
   ```

3. 類的構造函數接受一個文件名字符串作為輸入參數。這個字符串用來初始化文件流成員`ofs`。對其進行初始化後，可以將其輸入到`cout`作為一個新的流緩衝區。`rdbuf`在接受一個新緩衝區的同時，會將舊緩衝區以指針的方式進行返回，這樣當需要對緩衝區進行恢復時，就可以直接使用了：

   ```c++
   public:
       explicit
       redirect_cout_region (const string &filename)
       : ofs{filename}
   	, buf_backup{cout.rdbuf(ofs.rdbuf())}
       {}
   ```

4. 默認構造函數和其他構造函數做的事情幾乎一樣。其區別在於，默認構造函數不會打開任何文件。默認構造的文件流會直接替換`cout`的流緩衝，這樣會導致`cout`的一些功能失效。其會丟棄一些要打印的東西。這在某些情況下是非常有用的：

   ```c++
       redirect_cout_region()
       : ofs{}
       ,buf_backup{cout.rdbuf(ofs.rdbuf())}
       {}
   ```

5. 析構函數會對重定向進行恢復。當類在運行過程中超出了範圍，可以使用原始的`cout`流緩衝區對其進行還原：

   ```c++
       ~redirect_cout_region() {
       	cout.rdbuf(buf_backup);
       }
   };
   ```

6. 讓我們模擬一個有很多輸出的函數：

   ```c++
   void my_output_heavy_function()
   {
       cout << "some output\n";
       cout << "this function does really heavy work\n";
       cout << "... and lots of it...\n";
       // ...
   }
   ```

7. 主函數中，我們先會進行一次標準打印：

   ```c++
   int main()
   {
   	cout << "Readable from normal stdout\n";
   ```

8. 現在進行重定向，首先使用一個文本文件名對類進行實例化。文件流會使用讀取和寫入模式作為默認模式，所以其會創建一個文件。所以即便是後續使用`cout`進行打印，其輸出將會重定向到這個文件中：

   ```c++
   	{
           redirect_cout_region _ {"output.txt"};
           cout << "Only visible in output.txt\n";
           my_output_heavy_function();
   	}
   ```

9. 離開這段代碼後，文件將會關閉，打印輸出也會重歸標準輸出。我們再開啟一個代碼段，並使用默認構造函數對類進行構造。這樣後續的打印信息將無法看到，都會被丟棄：

   ```c++
       {
           redirect_cout_region _;
           cout << "This output will "
                   "completely vanish\n";
       }
   ```

10. 離開這段代碼後，我們的標準輸出將再度恢復，並且將程序的最後一行打印出來：

   ```c++
   	cout << "Readable from normal stdout again\n";
   }
   ```

11. 編譯並運行這個程序，其輸出和我們期望的一致。我們只看到了第一行和最後一行輸出：

    ```c++
    $ ./log_regions
    Readable from normal stdout
    Readable from normal stdout again
    ```

12. 我們可以將新文件output.txt打開，其內容如下：

    ```c++
    $ cat output.txt
    Only visible in output.txt
    some output
    this function does really heavy work
    ... and lots of it...
    ```

## How it works...

每個流對象都有一個內部緩衝區，這樣的緩衝區可以進行交換。當我們有一個流對象`s`時，我們將其緩衝區存入到變量`a`中，並且為流對象換上了一個新的緩衝區`b`，這段代碼就可以完成上述的過程:` a = s.rdbuf(b)`。需要恢復的時候只需要執行`s.rdbuf(a)`。

這就如同我們在本節所做的。另一件很酷的事情是，可以將這些`redirect_cout_region`輔助函數放入堆棧中：

```c++
{
    cout << "print to standard output\n";
    
    redirect_cout_region la {"a.txt"};
    cout << "print to a.txt\n";
    
    redirect_cout_region lb {"b.txt"};
    cout << "print to b.txt\n";
}
cout << "print to standard output again\n";
```

這也應該好理解，通常析構的順序和構造的順序是相反的。這種模式是將對象的構造和析構進行緊耦合，其也稱作為**資源獲得即初始化(RAII)**。

這裡有一個很重要的點需要注意——`redirect_cout_region`類中成員變量的初始化順序：

```c++
class redirect_cout_region {
    using buftype = decltype(cout.rdbuf());
    ofstream ofs;
    buftype buf_backup;
public:
    explicit
    redirect_cout_region(const string &filename)
    : ofs{filename},
    buf_backup{cout.rdbuf(ofs.rdbuf())}
    {}
...
```

我們可以看到，成員`buf_backup`的初始化需要依賴成員`ofs`進行。有趣的是，這些成員初始化的順序，不會按照初始化列表中給定元素的順序進行初始化。這裡初始化的順序值與成員變量聲明的順序有關！

> Note：
>
> 當一成員變量需要在另一個成員變量之後進行初始化，其需要在類聲明的時候以相應的順序進行聲明。初始化列表中的順序，對於構造函數來說沒有任何影響。