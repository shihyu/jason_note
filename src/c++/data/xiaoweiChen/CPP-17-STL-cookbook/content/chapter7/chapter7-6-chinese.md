# 格式化輸出

很多情況下，僅打印字符串和數字是不夠的。數字通常都以十進制進行打印，有時我們需要使用十六進制或八進制進行打印。並且在打印十六進制的時候，我們希望看到以`0x`為前綴的十六進制的數字，但有時卻不希望看到這個前綴。

當對浮點數進行打印的時候，也需要注意很多。以何種精度進行打印？要將數中的所有內容進行打印嗎？或者是如何打印科學計數法樣式的數？

除了數值表示方面的問題外，還需要規範我們打印的格式。有時我們要以表格的方式進行打印，以確保打印數據的可讀性。

這所有的一切都與輸出流有關，對輸入流的解析也十分重要。本節中，我們將來感受一下格式化輸出。有些顯示也會比較麻煩，不過我們會對其進行解釋。

## How to do it...

為了讓大家熟悉格式化輸出，本節我們將使用各種各樣的格式進行打印：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <iomanip>
   #include <locale>
   
   using namespace std;
   ```

2. 接下來，定義一個輔助函數，其會以不同的方式打印出一個數值。其能接受使用一種字符對寬度進行填充，其默認字符為空格：

   ```c++
   void print_aligned_demo(int val,
                           size_t width,
                           char fill_char = ' ')
   { 
   ```

3. 使用`setw`，我們可以設置打印數字的最小字符數輸出個數。當我們要將123的輸出寬度設置為6時，我們會得到"abc   "或"   abc"。我們也可以使用`std::left`, `std::right`和`std::internal`控制從哪邊進行填充。當我們以十進制的方式對數字進行輸出，`internal`看起來和`right`的作用一樣。不過，當打印`0x1`時，打印寬度為6時，`internal`會得到"0x  6"。`setfill`控制符可以用來定義填充字符。我麼可以嘗試使用使用以下方式進行打印：

   ```c++
       cout << "================\n";
       cout << setfill(fill_char);
       cout << left << setw(width) << val << '\n';
       cout << right << setw(width) << val << '\n';
       cout << internal << setw(width) << val << '\n';
   }
   ```

4. 主函數中，我們使用已經實現的函數。首先，打印數字12345，其寬度為15。我們進行兩次打印，不過第二次時，將填充字符設置為'_'：

   ```c++
   int main()
   {
       print_aligned_demo(123456, 15);
       print_aligned_demo(123456, 15, '_');
   ```

5. 隨後，我們將打印`0x123abc`，並使用同樣的寬度。不過，打印之前需要使用的是`std::hex`和`std::showbase`告訴輸出流對象`cout`輸出的格式，並且添加`0x`前綴，看起來是一個十六進制數：

   ```c++
   	cout << hex << showbase;
   	print_aligned_demo(0x123abc, 15); 
   ```

6. 對於八進制我們也可以做同樣的事：

   ```c++
   	cout << oct;
   	print_aligned_demo(0123456, 15);
   ```

7. 通過`hex`和`uppercase`，我們可以將`0x`中的x轉換成大寫字母。`0x123abc`中的`abc`同樣也轉換成大寫：

   ```c++
   	cout << "A hex number with upper case letters: "
   		<< hex << uppercase << 0x123abc << '\n';	
   ```

8. 如果我們要以十進制打印100，我們需要將輸出從`hex`切換回`dec`：

   ```c++
       cout << "A number: " << 100 << '\n';
       cout << dec;
       
   	cout << "Oops. now in decimal again: " << 100 << '\n';
   ```

9. 我們可以對布爾值的輸出進行配置，通常，true會打印出1，false為0。使用`boolalpha`，我們就可以得到文本表達：

   ```c++
   	cout << "true/false values: "
   		<< true << ", " << false << '\n';
   	cout << boolalpha
   		<< "true/false values: "
   		<< true << ", " << false << '\n';
   ```

10. 現在讓我們來一下浮點型變量`float`和`double`的打印。當我們有一個數12.3，那麼打印也應該是12.3。當我們有一個數12.0，打印時會將小數點那一位進行丟棄，不過我們可以通過`showpoint`來控制打印的精度。使用這個控制符，就能顯示被丟棄的一位小數了：

   ```c++
       cout << "doubles: "
           << 12.3 << ", "
           << 12.0 << ", "
           << showpoint << 12.0 << '\n';
   ```

11. 可以使用科學計數法或固定浮點的方式來表示浮點數。`scientific`會將浮點數歸一化成一個十進制的小數，並且其後面的位數使用10的冪級數表示，其需要進行乘法後才能還原成原始的浮點數。比如，300.0科學計數法就表示為"3.0E2"，因為300 = 3.0 x $10^2$。`fixed`將會恢復普通小數的表達方式：

    ```c++
    	cout << "scientific double: " << scientific
    		<< 123000000000.123 << '\n';
    	cout << "fixed double: " << fixed
    		<< 123000000000.123 << '\n';
    ```

12. 除此之外，我們也能對打印的精度進行控制。我們先創建一個特別小的浮點數，並對其小數點後的位數進行控制：

    ```c++
    	cout << "Very precise double: "
    		<< setprecision(10) << 0.0000000001 << '\n';
    	cout << "Less precise double: "
    		<< setprecision(1) << 0.0000000001 << '\n';
    }
    ```

13. 編譯並運行程序，我們就會得到如下的輸出。前四個塊都是有打印輔助函數完成，其使用`setw`對字符串進行了不同方向的填充。此外，我們也進行了數字的進制轉換、布爾數表示和浮點數表示。通過實際操作，我們會對其更加熟悉：

    ```c++
    $ ./formatting
    =====================
    123456         
             123456
             123456
    =====================
    123456_________
    _________123456
    _________123456
    =====================
    0x123abc       
           0x123abc
    0x       123abc
    =====================
    0123456        
            0123456
            0123456
    A hex number with upper case letters: 0X123ABC
    A number: 0X64
    Ooop. now in decimal again: 100
    true/false values: 1, 0
    true/false values: true, false
    doubles: 12.3, 12, 12.0000
    scientific double: 1.230000E+12
    fixed double: 1230000000000.123047
    Very precise double: 0.0000000001
    Less previse double: 0.0
    ```

## How it works...

例程看起來有些長，並且`<< foo << bar`的方式對於初級讀者來說會感覺到困惑。因此，讓我們來看一下格式化修飾符的表。其都是用`input_stream >> modifier `或` output_stream << modifier`來對之後的輸入輸出進行影響：

| 符號                                                         | 描述                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [setprecision(int)](http://zh.cppreference.com/w/cpp/io/manip/setprecision) | 打印浮點數時，決定打印小數點後的位數。                       |
| [showpoint / noshowpoint](http://zh.cppreference.com/w/cpp/io/manip/showpoint) | 啟用或禁用浮點數字小數點的打印，即使沒有小數位。             |
| [fixed /scientific / hexfloat /defaultfloat](http://zh.cppreference.com/w/cpp/io/manip/fixed) | 數字可以以固定格式和科學表達式的方式進行打印。`fixed`和`scientific`代表了相應的打印模式。`hexfloat`將會同時激活這兩種模式，用十六進制浮點表示法格式化浮點數。`defaultfloat`則會禁用這兩種模式。 |
| [showpos / noshowpos](http://zh.cppreference.com/w/cpp/io/manip/showpos) | 啟用或禁用使用'+'來標誌正浮點數。                            |
| [setw(int n)](http://zh.cppreference.com/w/cpp/io/manip/setw) | 設置打印的寬度`n`。在讀取的時候，這種設置會截斷輸入。當打印位數不夠時，其會使用填充字符將輸出填充到`n`個字符。 |
| [setfill(char c)](http://zh.cppreference.com/w/cpp/io/manip/setfill) | 當我們`setw`時，會涉及填充字符的設置。`setfill`可以將填充字符設置為`c`。其默認填充字符為空格。 |
| [internal / left / right](http://zh.cppreference.com/w/cpp/io/manip/left) | `left`和`right`控制填充的方向。`internal`會將填充字符放置在數字和符號之間，這對於十六進制打印和一些金融數字來說，十分有用。 |
| [dec / hex / oct](http://zh.cppreference.com/w/cpp/io/manip/hex) | 整數打印的類型，十進制、十六進制和八進制。                   |
| [setbase(int n)](http://zh.cppreference.com/w/cpp/io/manip/setbase) | 數字類型的同義函數，當`n`為`10/16/8`時，與`dec / hex / oct`完全相同。當傳入0時，則會恢復默認輸出，也就是十進制，或者使用數字的前綴對輸入進行解析。 |
| [quoted(string)](http://zh.cppreference.com/w/cpp/io/manip/quoted) | 將帶有引號的字符串的引號去掉，對其實際字符進行打印。這裡`string`的類型可以是`string`類的實例，也可以是一個C風格的字符串。 |
| [boolalpha / noboolalpha](http://zh.cppreference.com/w/cpp/io/manip/boolalpha) | 打印布爾變量，是打印字符形式的，還是數字形式的。             |
| [showbase / noshowbase](http://zh.cppreference.com/w/cpp/io/manip/showbase) | 啟用或禁用基於前綴的數字解析。對於`hex`來說就是`0x`，對於`octal`來說就是`0`。 |
| [uppercase / nouppercase](http://zh.cppreference.com/w/cpp/io/manip/uppercase) | 啟用或禁用將浮點數中的字母或十六進制中的字符進行大寫輸出。   |

看起來很多，想要熟悉這些控制符的最好方式，還是儘可能多的使用它們。

在使用中會發現，其中有一些控制符具有粘性，另一些沒有。這裡的粘性是說其會持續影響接下來的所有輸入或輸出，直到對控制符進行重置。表格中沒有粘性的為`setw`和`quoted`控制符。其只對下一次輸入或輸入有影響。瞭解這些非常重要，當我們要持續使用一個格式進行打印時，對於有粘性的控制符我們設置一次即可，其餘的則在需要是進行設置。這些對輸入解析同樣適用，不過錯誤的設置了控制符則會得到錯誤的輸入信息。

下面的一些控制符我們沒有使用它們，因為他們對於格式化沒有任何影響，但出於完整性的考量我們在這裡也將這些流狀態控制符列出來：

| 符號                                                         | 描述                                                       |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| [skipws / noskipws](http://zh.cppreference.com/w/cpp/io/manip/skipws) | 啟用或禁用輸入流對空格進行略過的特性。                     |
| [unitbuf / nounitbuf](http://zh.cppreference.com/w/cpp/io/manip/unitbuf) | 啟用或禁用在進行任何輸出操作後，就立即對輸出緩存進行刷新。 |
| [ws](http://zh.cppreference.com/w/cpp/io/manip/ws)           | 從輸入流捨棄前導空格。                                     |
| [ends](http://zh.cppreference.com/w/cpp/io/manip/ends)       | 向流中輸入一個終止符`\0`。                                 |
| [flush](http://zh.cppreference.com/w/cpp/io/manip/flush)     | 對輸出緩存區進行刷新。                                     |
| [endl](http://zh.cppreference.com/w/cpp/io/manip/endl)       | 向輸出流中插入`\n`字符，並且刷新輸出緩存區。               |

這些控制符中，只有`skipws / noskipws`和`unitbuf / nounitbuf`是具有粘性的。