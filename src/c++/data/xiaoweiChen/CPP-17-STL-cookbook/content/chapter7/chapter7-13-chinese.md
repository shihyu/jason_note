# 簡單打印不同格式的數字

之前的章節中，我們已經瞭解如何打印出帶格式的輸出，同時也意識到了兩點：

- 輸入輸出控制符是有粘性的，所以當我們要臨時使用的時候，需要在用完之後進行還原。
- 其控制符和較少的要打印的對象相比，會顯得很冗長。

這些原因導致一些開發者使用C++的時候，還是依舊使用`printf`進行打印輸出。

本節，我們將來看一下如何不用太多代碼就能進行很好的類型打印。

## How to do it...

我們會先來實現一個類`format_guard`，其會自動的將打印格式進行恢復。另外，我們添加了一個包裝類型，其可以包含任意值，當對其進行打印時，其能使用相應的格式進行輸出，而無需添加冗長的控制符：

1. 包含必要的頭文件，並聲明所使用的命名空間。

   ```c++
   #include <iostream>
   #include <iomanip>
   
   using namespace std; 
   ```

2. 輔助類在調用`format_guard`時，其會對輸出流的格式進行清理。其構造函數保存了格式符，也就是在這裡對`std::cout`進行設置。析構函數會將這些狀態進行去除，這樣就不會後續的打印有所影響：

   ```c++
   class format_guard {
   	decltype(cout.flags()) f {cout.flags()};
   public:
   	~format_guard() { cout.flags(f); }
   };
   ```

3. 定義另一個輔助類`scientific_type`。因為其是一個模板類，所以其能擁有任意類型的成員變量。這個類沒有其他任何作用：

   ```c++
   template <typename T>
   struct scientific_type {
   	T value;
       
   	explicit scientific_type(T val) : value{val} {}
   };
   ```

4. 封裝成`scientific_type`之後，可以對任意類型進行自定義格式設置，當對`operator>>`進行重載後，輸出流就會在執行時，運行完全不同的代碼。這樣就能在使用科學計數法表示浮點數時，以大寫的格式，並且其為正數時，數字前添加'+'號。我們也會在跳出函數時，使用`format_guard`類對打印格式進行清理：

   ```c++
   template <typename T>
   ostream& operator<<(ostream &os, const scientific_type<T> &w) {
       format_guard _;
       os << scientific << uppercase << showpos;
       return os << w.value;
   }
   ```

5. 主函數中，我們將使用到`format_guard`類。我們會創建一段新的代碼段，首先對類進行實例化，並且對`std::cout`進行輸出控制符的設置：

   ```c++
   int main()
   {
       {
           format_guard _;
           cout << hex << scientific << showbase << uppercase;
           
           cout << "Numbers with special formatting:\n";
           cout << 0x123abc << '\n';
           cout << 0.123456789 << '\n';
       }
   ```

6. 使用控制符對這些數字進行打印後，跳出這個代碼段。這時`format_guard`的析構函數會將格式進行清理。為了對清理結果進行測試，會再次打印相同的數字。其將會輸出不同的結果：

   ```c++
   	cout << "Same numbers, but normal formatting again:\n";
   	cout << 0x123abc << '\n';
   	cout << 0.123456789 << '\n';
   ```

7. 現在使用`scientific_type`，將三個浮點數打印在同一行。我們將第二個數包裝成`scientific_type`類型。這樣其就能按照我們指定的風格進行打印，不過在之前和之後的輸出都是以默認的格式進行。與此同時，我們也避免了冗長的格式設置代碼：

   ```c++
       cout << "Mixed formatting: "
           << 123.0 << " "
           << scientific_type{123.0} << " "
           << 123.456 << '\n';
   }
   ```

8. 編譯並運行程序，我們就會得到如下的輸出。前兩行按照我們的設定進行打印。接下來的兩行則是以默認的方式進行打印。這樣就證明了我們的`format_guard`類工作的很好。最後三個數在一行上，也是和我們的期望一致。只有中間的數字是`scientific_type`類型的，前後兩個都是默認類型：

   ```c++
   $ ./pretty_print_on_the_fly
   Numbers with special formatting:
   0X123ABC
   1.234568E-01
   Same numbers, but normal formatting again:
   1194684
   0.123457
   Mixed formatting: 123 +1.230000E+02 123.456
   ```

   