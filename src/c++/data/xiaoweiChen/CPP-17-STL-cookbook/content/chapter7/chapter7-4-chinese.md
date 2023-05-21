# 從用戶的輸入讀取數值

本書中大多數例程的輸入都是從文件或標準輸入中獲得。這次我們重點來了解一下讀取，以及當遇到一些有問題的流時，不能直接終止程序，而是要做一些錯誤處理的工作。

本節只會從用戶輸入中讀取，知道如何讀取後，將瞭解如何從其他的流中讀取數據。用戶輸入通常通過`std::cin`，其為最基礎的輸入流對象，類似這樣的類還有`ifstream`和`istringstream`。

## How to do it...

本節，將從用戶輸入中讀取不同值，並且瞭解如何進行錯誤處理，並對輸入中有用的部分進行較為複雜的標記。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>

   using namespace std;
   ```

2. 首先，提示用戶輸入兩個數字。將這兩個數字解析為`int`和`double`類型。例如，用戶輸入`1 2.3`:

   ```c++
   int main()
   {
       cout << "Please Enter two numbers:\n> ";
       int x;
       double y;
   ```

3. 解析和錯誤檢查同時在`if`判斷分支中進行。只有兩個數都被解析成有效的數字，才能對其進行打印：

   ```c++
       if (cin >> x >> y) {
       	cout << "You entered: " << x
       		 << " and " << y << '\n';
   ```

4. 如果因為任何原因，解析不成功，那麼我們要告訴用戶為什麼會出錯。`cin`流對象現在處於失敗的狀態，並且將錯誤狀態進行清理之前，無法為我們提供輸入功能。為了能夠對新的輸入進行解析需要調用`cin.clear()`，並且將之前接受到的字符丟棄。使用`cin.ignore`完成丟棄的任務，這裡我們指定了丟棄字符的數量，直到遇到下一個換行符為止。完成這些事之後，輸入有可以用了：

   ```c++
       } else {
           cout << "Oh no, that did not go well!\n";
           cin.clear();
           cin.ignore(
           	std::numeric_limits<std::streamsize>::max(),
           	'\n');
       }
   ```

5. 讓用戶輸入一些其他信息。我們讓用戶輸入名字，名字由多個字母組成，字母間使用空格隔開。因此，可以使用`std::getline`函數，其需要傳入一個流對象和一個分隔字符。我們選逗號作為分隔字符。這裡使用`getline`來代替`cin >> ws`的方式讀入字符，這樣我們就能丟棄在名字前的所有空格。對於每一個循環中都會打印當前的名字，如果名字為空，那麼我們會將其丟棄：

   ```c++ 
       cout << "now please enter some "
       		"comma-separated names:\n> ";
       for (string s; getline(cin >> ws, s, ',');) {
       	if (s.empty()) { break; }
       	cout << "name: \"" << s << "\"\n";
       }
   }
   ```

6. 編譯並運行程序，就會得到如下的輸出，其會讓用戶進行輸入，然後我們輸入合法的字符。數字`1 2`都能被正確的解析，並且後面輸入的名字也能立即排列出來。兩個逗號間沒有單詞的情況將會跳過：

   ```c++
   $ ./strings_from_user_input
   Please Enter two numbers:
   > 1 2
   You entered: 1 and 2
   now please enter some comma-separated names:
   > john doe,ellen ripley, alice,chuck norris,,
   name: "john doe"
   name: "ellen ripley"
   name: "alice"
   name: "chuck norris"
   ```

7. 再次運行程序，這次將在一開始就輸入一些非法數字，可以看到程序就會走到不同的分支，然後丟棄相應的輸入，並繼續監聽正確的輸入。可以看到`cin.clear()`和`cin.ignore(...)`的調用如何對名字讀取進行影響：

   ```c++
   $ ./strings_from_user_input
   Please Enter two numbers:
   > a b
   Oh no, that did not go well!
   now please enter some comma-separated names:
   > bud spencer, terence hill,,
   name: "bud spencer"
   name: "terence hill"
   ```

## How it works...

本節，我們對一些複雜輸入進行了檢索。首要注意的是，我們的檢索和錯誤處理是同時進行。

表達式`cin >> x`是對`cin`的再次引用。因此，就可以將輸入些為`cin >> x >> y >> z >> ...`。與此同時，其也能將輸入內容轉換成為一個布爾值，並在`if`條件中使用。這個布爾值告訴我們最後一次讀取是否成功，這也就是為什麼我們會將代碼寫成`if (cin >> x >> y) { ... }`的原因。

當我們想要讀取一個整型，但輸入中包含`foobar`為下一個表示，那麼流對象將無法對這段字符進行解析，並且這讓輸入流的狀態變為失敗。這對於解析來說是非常關鍵的，但對於整個程序來說就不是了。這裡可以將輸入流的狀態進行重置，然後在進行其他的操作。在我們的例程中，我們嘗試在讀取兩個數值失敗後，讀取一組姓名。例子中，我們使用`cin.clear()`對`cin`的工作狀態進行了重置。不過，這樣內部的光標就處於我們的現在的類型上，而非之前的數字。為了將之前輸入的內容丟棄，並對姓名輸入進行流水式的讀取，我們使用了一個比較長的表達式，`  cin.ignore(std::numeric_limits<std::streamsize>::max(),'\n');`。這裡對內存的清理是十分有必要的，因為我們需要在用戶輸入一組姓名時，對緩存進行刷新。

下面的循環看起來也挺奇怪的：

```c++
for (string s; getline(cin >> ws, s, ',');) { ... }
```

`for`循環的判斷部分，使用了`getline`函數。`getline`函數接受一個輸入流對象，一個字符串引用作為輸出，以及一個分隔符。通常，分隔字符代表新的一行。這裡使用逗號作為分隔符，所以姓名輸入列表為`john, carl, frank`，這樣就可以單個的進行讀取。

目前為止還不錯。不過，`cin >> ws`的操作是怎麼回事呢？這可以讓`cin`對所有空格進行刷新，其會讀取下一個非空格字符到下一個逗號間的字符。回看一下"john, carl, frank"例子，當我們不使用`ws`時，將獲取到"john"，" carl"和" frank"字符串。這裡需要注意"carl"和"frank"開頭不必要的空格，因為在`ws`中對輸入流進行了預處理，所以能夠避免開頭出現空格的情況。