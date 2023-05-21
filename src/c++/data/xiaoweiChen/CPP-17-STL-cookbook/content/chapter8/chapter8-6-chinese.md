# 將`void*`替換為更為安全的std::any

有時我們會需要將一個變量保存在一個未知類型中。對於這樣的變量，我們通常會對其進行檢查，以確保其是否包含一些信息，如果是包括，那我們將會去判別所包含的內容。以上的所有操作，都需要在一個類型安全的方法中進行。

以前，我們會將可變對象存與`void*`指針當中。void類型的指針無法告訴我們其所指向的對象類型，所以我們需要將其進行手動轉換成我們期望的類型。這樣的代碼看起來很詭異，並且不安全。

C++17在STL中添加了一個新的類型——`std::any`。其設計就是用來持有任意類型的變量，並且能提供類型的安全檢查和安全訪問。

本節中，我們將會來感受一下這種工具類型。

## How to do it...

我們將實現一個函數，這個函數能夠打印所有東西。其就使用`std::any`作為參數：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <list>
   #include <any>
   #include <iterator>
   
   using namespace std;
   ```

2. 為了減少後續代碼中尖括號中的類型數量，我們對`list<int>`進行了別名處理： 

   ```c++
   using int_list = list<int>;
   ```

3. 讓我們實現一個可以打印任何東西的函數。其確定能打印任意類型，並以`std::any`作為其參數：

   ```c++
   void print_anything(const std::any &a)
   {
   ```

4. 首先，要做的事就是對傳入的參數進行檢查，確定參數中是否包含任何東西，還是隻是一個空實例。如果為空，那就沒有必要再進行接下來的打印了：

   ```c++
   	if (!a.has_value()) {
   		cout << "Nothing.\n";
   ```

5. 當非空時，就要需要對其進行類型比較，直至匹配到對應類型。這裡第一個類型為`string`，當傳入的參數是一個`string`，我們可以使用`std::any_cast`將`a`轉化成一個`string`類型的引用，然後對其進行打印。我們將雙引號當做打印字符串的修飾：

   ```c++
       } else if (a.type() == typeid(string)) {
           cout << "It's a string: "
           	<< quoted(any_cast<const string&>(a)) << '\n';
   ```

6. 當其不是`string`類型時，其也可能是一個`int`類型。當與之匹配是使用`any_cast<int>`將`a`轉換成`int`型數值：

   ```c++
       } else if (a.type() == typeid(int)) {
       	cout << "It's an integer: "
       		<< any_cast<int>(a) << '\n';
   ```

7. `std::any`並不只對`string`和`int`有效。我們將`map`或`list`，或是更加複雜的數據結構放入一個`any`變量中。讓我們輸入一個整數列表看看，按照我們的預期，函數也將會打印出相應的列表：

   ```c++
       } else if (a.type() == typeid(int_list)) {
           const auto &l (any_cast<const int_list&>(a));
          
           cout << "It's a list: ";
           copy(begin(l), end(l),
           	ostream_iterator<int>{cout, ", "});
           cout << '\n'; 
   ```

8. 如果沒有類型能與之匹配，那就不會進行猜測了。我們會放棄對類型進行匹配，然後告訴使用者，我們對輸入毫無辦法：

   ```c++
       } else {
       	cout << "Can't handle this item.\n";
       }
   }
   ```

9. 主函數中，我們能夠對調用函數傳入任何類型的值。我們可以使用大括號對來構建一個空的`any`變量，或是直接輸入字符串“abc”，或是一個整數。因為`std::any`可以由任何類型隱式轉換而成，這裡並沒有語法上的開銷。我們也可以直接構造一個列表，然後丟入函數中：

   ```c++
   int main()
   {
       print_anything({});
       print_anything("abc"s);
       print_anything(123);
       print_anything(int_list{1, 2, 3});
   ```

10. 當我們想要傳入的參數比較大，那麼拷貝到`any`變量中就會花費很長的時間，這是可以使用立即構造的方式。`in_place_type_t<int_list>{}`表示一個空的對象，對於`any`來說其就能夠知道應該如何去構建對象了。第二個參數為`{1,2,3}`其為一個初始化列表，其會用來初始化`int_list`對象，然後被轉換成`any`變量。這樣，我們就避免了不必要的拷貝和移動：

    ```c++
    	print_anything(any(in_place_type_t<int_list>{}, {1, 2, 3}));
    }
    ```

11. 編譯並運行程序，我們將得到如下的輸入出：

    ```c++
    $ ./any
    Nothing.
    It's a string: "abc"
    It's an integer: 123
    It's a list: 1, 2, 3,
    It's a list: 1, 2, 3,
    ```

## How it works...

`std::any`類型與`std::optional`類型很類似——具有一個`has_value()`成員函數，能告訴我們其是否攜帶一個值。不過這裡，我們還需要對字面的數據進行保存，所以`any`要比`optional`類型複雜的多。

訪問any變量的內容前，我們需要知道其所承載的類型，然後將`any`變量轉換成那種類型。

這裡，使用的比較方式為`x.type == typeid(T)`。如果比較結果匹配，那麼就使用`any_cast`對其內容進行轉換。

需要注意的是`any_cast<T>(x)`將會返回`x`中`T`值的副本。如果想要避免對複雜對象不必要的拷貝，那就需要使用`any_cast<T&>(x)`。本節的代碼中，我們使用引用的方式來獲取`string`和`list<int>`對象的值。

> Note：
>
> 如果`any`變量轉換成為一種錯誤的類型，其將會拋出`std::bad_any_cast`異常。





