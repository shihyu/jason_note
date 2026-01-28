> 原文連結：https://www.oracle.com/cn/servers/technologies/howto-use-lambda-exp-cpp11.html
### Lambda 表達式不僅具有函式指標的靈活性，還可以通過捕獲局部變數提高可擴展性。本文介紹 Lambda 表達式的語法和用法。

### 簡介

Lambda 可能是最新的 C++11 標準的典型特性之一。Lambda 表達式把函式看作物件。Lambda 表達式可以像物件一樣使用，比如可以將它們賦給變數和作為參數傳遞，還可以像函式一樣對其求值。

當一個函式需要將另一個函式用作參數時，可以使用 Lambda。例如，C qsort() 函式接受一個指向比較函式的指標，如清單 1 所示。

```c++
#include <stdlib.h> 
 #include <stdio.h> 
 static int intcompare(const void *p1, const void *p2) 
 {   
 int i = *((int *)p1);  
 int j = *((int *)p2); 
 return (i < j) ;
 }  
 int main() 
 {   
 int a[10] = { 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 }; 
 qsort((void *)a, 10, sizeof (int), intcompare);
 for (int i = 0; i < 10; i++) { printf("%d ", a[i]); }  
 printf("\n"); 
 return 0;  }
```

**清單 1**

清單 1 中的程式碼有以下幾點不足：

- 比較函式需要單獨聲明。這增加了將錯誤的比較函式傳遞給 qsort() 操作的風險。
- 比較函式接受 void * 參數，因此缺失了某種程度的型別檢查。
- 比較函式看不到任何局部作用的變數。因此，如果存在其他影響排序的因素，必須在更大範圍內聲明。

清單 2 顯示重新編寫後的清單 1 中的示例，將 C++ std::sort() 演演算法與 lambda 表達式結合使用。由於 std::sort() 是一個樣板，因此會保留所有型別資訊。注意如何在通常出現函式名的位元元置編寫 lambda 表達式。

```c++
#include <algorithm> 
 int main() 
 {
 int a[10] = { 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 };   
std::sort( a, &a[10], [](int x, int y){ return x < y; } );
    for(int i=0; i<10; i++) { printf("%i ", a[i]); }  
  printf("\n");    
  return 0; 
  }
```

**清單 2**

### Lambda 表達式的基本語法

Lambda 表達式本質上與函式聲明非常類似。我們可以提取清單 2 中的 lambda 表達式，詳加說明。提取的 lambda 表達式如清單 3 所示：

```c++
[](int x, int y){ return x < y ; }
```

**清單 3**

如果我們將 lambda 表達式比作函式，可以看到它與函式名對應的是一對空的方括號，即*捕獲表達式*。這些括號表示後面跟著一個 lambda 表達式。這些方括號不必為空；稍後將討論其內容。

如果 lambda 主體只含一個返回型別，則暗示返回的表達式型別為 lambda 返回型別。如果要顯式指定返回型別，需使用新的 C++11 語法表示函式聲明中的後置返回型別。對於返回型別 T 的普通函式，您可以這樣編寫：

```c++
auto foo(...) -> T { ... }
```

對於 lambda，您需要要這樣編寫：

```c++
[] (...) -> T { ... }
```

lambda 表達式的其餘部分與常規 C 或 C++ 函式主體類似。

### 將 Lambda 傳遞到函式指標

C++11 標準庫中有一個名為 function 的樣板，它可以接受指定型別的函式或者具有匹配的返回型別和參數列表的 lambda。這將產生一個指向函式型別的指標，例如，清單 4 可用作函式參數型別，接受 int 參數，返回 void。您可以向其傳遞任何類似匹配函式或 lambda 的內容。

```c++
std::function<void(int)>
```

**清單 4**

清單 5 顯示的函式掃描一個陣列，對每個元素應用一個給定函式。

```c++
void scan( int* a, int length, std::function<void(int)> process ) 
 {  
 for(int i=0; i<length; i++) 
 {   
 process(a[i]); 
 } 
 }
```

**清單 5**

清單 6 顯示如何通過傳遞一個函式或 lambda 表達式作為參數來調用 scan() 函式。

```c++
void f(int);
  int a[10];  
  ... 
  scan(a, 10, f); 
  scan(a, 10, [](int k)->void { ... } );
```

**清單 6**

### Lambda 表達式中的變數捕獲

到目前為止，我們對 lambda 表達式的處理基本與標準函式調用類似：傳入參數，返回結果。然而，在函式主體中聲明的 lambda 表達式還是可以捕獲在聲明 lambda 處可見的函式的任何局部變數。

假設我們需要使用函式 scan()，但希望 process 函式只對大於某個閾值的值起作用。我們不能修改 scan()，不能讓 scan() 向 process 函式傳遞多個參數。但如果我們將一個 lambda 表達式傳遞給 scan() 函式，則可以從其環境捕獲一個局部變數。

在清單 7 中，我們將希望捕獲的變數放在方括號中，即放在捕獲表達式中。這實際上向 lambda 表達式中額外傳遞了一個參數，但無需更改 scan 函式的定義。就像傳遞參數給函式一樣，我們實際上是在函式的調用點捕獲值 threshold 的副本，這稱為*通過值捕獲*。

```c++
#include <algorithm> 
 void scan( int* a, int length, std::function<void(int)> process) 
 {  
 for(int i=0; i<length; i++) {   
 process(a[i]); 
 } 
 } 
 int main()  
 {   
 int a[10] = { 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 };   
 int threshold = 5;   
scan(a, 10,
     [threshold](int v)
  { if (v>threshold) { printf("%i ", v); } }
  );  
  printf("\n");   
  return 0;  }
```

**清單 7**

有一個簡寫形式 [=]，表示“通過值捕獲每個變數”。在清單 8 中，我們將函式調用重新編寫為使用這種更短的表達式。

```c++
scan(a, 10, [=](int v) { if (v>threshold) { printf("%i ", v); } });
```

**清單 8**

**注**：通過值捕獲變數意味著生成局部副本。如果有多個局部變數，全部捕獲可能會導致 lambda 產生顯著開銷。

但有些情況下，我們希望修改捕獲的變數。例如，假設我們要計算最大值並將其存儲在變數 max 中。在這種情況下，我們不想使用該變數值的副本，而是希望使用該變數的參照，這樣，我們就可以在樣板中修改該變數。這稱為*通過參照捕獲變數*。清單 9 顯示了這樣一個示例。

```c++
#include <algorithm> 
 void scan(int * a, int length, std::function<void (int)> func) 
 {   
 for(int i=0; i<length; i++) {  
 func(a[i]);   
 } 
 } 
 int main() 
 {  
 int a[10] = { 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 }; 
 int threshold = 5; 
 int max =0;   
 std::sort( a, &a[10], [](int x, int y){return (x < y);});  
 scan(a, 10,
 [threshold,&max](int v) { if (v>max) {max = v;}
if (v>threshold) { printf("%i ", v); } });
   printf("\n");  
   printf("Max = %i\n",max);  
   return 0; 
   }
```

**清單 9**

同樣，也有一個簡寫形式 [&]，用於應通過參照捕獲每個變數的情況。

### Lambda 表達式、函式物件和函子

雖然 lambda 表達式是 C++11 的新特性，但用這種方式訪問現有語言特性的確很方便。lambda 表達式是*函式物件* 的速記表示法。函式物件是一個具有成員 operator()()（函式調用運算子）的類型別物件，因此可以像函式一樣調用。函式物件型別被稱作*函子*。清單 10 顯示了一個函子的示例。

```c++
class compare_ints { 
 public:  
 compare_ints(int j, int k ) : l(j), r(k) { } 
 bool operator()() { return l < r; }  
 private:  
 int l, r;  };
```

**清單 10**

您可以創建一個 compare_ints 物件，用兩個整型值初始化，如果第一個值小於第二個值，使用函式調用運算子返回 true：

```c++
compare_ints comp(j, k); 
 bool less_than = comp();
```

也可以動態創建一個臨時物件，然後直接使用：

```c++
bool less_than = compare_ints(j, k)();
```

使用 lambda 表達式不必創建和命名函子類即可達到這種效果。編譯器為您創建一個匿名函子，如清單 11 所示。

```c++
auto comp = [](int j, int k) { return j < k; };  
bool less_than =  comp(l,r);
```

**清單 11**

在清單 11 中，comp 是匿名函子型別的物件。

您也可以動態執行此操作：

```c++
bool less_than = [l,r]() { return l < r; }();
```

### 總結

Lambda 表達式是一種非常強大的 C++ 擴展。它們不僅具有函式指標的靈活性，還可以通過捕獲局部變數提高可擴展性。

顯然，與 C++11 中廣泛的樣板特性結合時，lambda 表達式會變得更加 有用，這種情況在按 C++11 標準編寫的程式碼中會經常遇到。
