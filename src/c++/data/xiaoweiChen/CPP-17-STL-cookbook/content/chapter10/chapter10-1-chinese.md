# 實現標準化路徑

本節中我們通過一個非常簡單的例子來瞭解`std::filesystem::path`類，並實現一個智能標準化系統路徑的輔助函數。

本節中的例子可以在任意的文件系統中使用，並且返回一種標準化格式的路徑。標準化就意味著獲取的是絕對路徑，路徑中不包括`.`和`..`。

實現函數的時候，我們將會瞭解，當使用文件系統庫的基礎部分時，需要注意哪些細節。

## How to do it...

本節中，我們的程序可以從命令行參數中獲得文件系統路徑，並使用標準化格式進行打印：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <filesystem>
   
   using namespace std;
   using namespace filesystem;
   ```

2. 主函數中，會對命令行傳入的參數進行檢查。如果沒有傳入，我們將會直接返回，並在終端上打印程序具體的使用方式。當提供了一個路徑，那我們將用其對`filesystem::path`對象進行實例化：

   ```c++
   int main(int argc, char *argv[])
   {
       if (argc != 2) {
           cout << "Usage: " << argv[0] << " <path>\n";
           return 1;
       }
       
       const path dir {argv[1]};
   ```

3. 實例化`path`對象之後，還不能確定這個路徑是否真實存在於計算機的文件系統中。這裡我們使用了`  filesystem::exists`來確認路徑。如果路徑不存在，我們會再次返回：

   ```c++
   	if (!exists(dir)) {
           cout << "Path " << dir << " does not exist.\n";
           return 1;
       }	
   ```

4. Okay，如果完成了這個檢查，我們就能確定這是一個正確的路徑，並且將會對這個路徑進行標準化，然後將其進行打印。` filesystem::canonical`將會為我們返回另一個`path`對象，可以直接對其進行打印，不過`path`的`<<`重載版本會將雙引號進行打印。為了去掉雙引號，我們通過`.c_str()`或`.string()`方法對路徑進行打印：

   ```c++
   	cout << canonical(dir).c_str() << '\n';
   }
   ```

5. 編譯代碼並運行。當我們在家目錄下輸入相對地址`"src"`時，程序將會打印出其絕對路徑：

   ```c++
   $ ./normalizer src
   /Users/tfc/src
   ```

6. 當我們打印一些更復雜的路徑時，比如：給定路徑中包含桌面文件夾的路徑，`..`，還會有`Documents`文件夾，然後在到`src`文件夾。然而，程序會打印出與上次相同的地址！

   ```c++
   $ ./normalizer Desktop/../Documents/../src
   /Users/tfc/src
   ```

## How it works...

作為一個`std::filesystem `的新手，看本節的代碼應該也沒有什麼問題。通過文件系統路徑字符串初始化了一個`path`對象。`std::filesystem::path`類為文件系統庫的核心，因為庫中大多數函數和類與之相關。

`filesystem::exists`函數可以用來檢查給定的地址是否存在。檢查文件路徑的原因是，`path`對象中的地址，不確定在文件系統中是否存在。`exists`能夠接受一個`path`實例，如果地址存在，則返回`true`。`exists`無論是相對地址和絕對地址都能夠進行判斷。

最後，我們使用了`filesystem::canonical`將給定路徑進行標準化。

```c++
path canonical(const path& p, const path& base = current_path());
```

`canonical`函數能接受一個`path`對象和一個可選的第二參數，也就是另一個地址。如果`p`路徑是一個相對路徑，那麼`base`就是其基礎路徑。完成這些後，`canonical`會將`.`和`..`從路徑中移除。

打印時對標準化地址使用了`.c_str()`函數，這樣我們打印出來的地址前後就沒有雙引號了。

## There's more...

`canonical`在對應地址不存在時，會拋出一個`filesystem_error`類型的異常。為了避免函數拋出異常，我們需要使用`exists`函數對提供路徑進行檢查。這樣的檢查僅僅就是為了避免函數拋出異常嗎？肯定不是。

`exists` 和`canonical`函數都能拋出`bad_alloc`異常。如果我們遇到了，那程序肯定會失敗。更為重要的是，當我們對路徑進行標準化處理時，其他人將對應的文件重命名或刪除了，則會造成更嚴重的問題。這樣的話，即便是之前進行過檢查，`canonical`還是會拋出一個`filesystem_error`異常。

大多數系統函數都會有一些重載，他們能夠接受相同的參數，甚至是一個` std::error_code`引用：

```c++
path canonical(const path& p, const path& base = current_path());
path canonical(const path& p, error_code& ec);
path canonical(const std::filesystem::path& p,
               const std::filesystem::path& base,
               std::error_code& ec );
```

我們可以使用`try-catch`將系統函數進行包圍，手動的對其拋出的異常進行處理。需要注意的是，這裡只會改變系統相關錯誤的動作，而無法對其他進行修改。帶或不帶`ec`參數，更加基於異常，例如當系統沒有可分配內存時，還是會拋出`bad_alloc`異常。