# 自動化管理資源——std::unique_ptr

C++11之後，STL提供了新的智能指針，能對動態內存進行跟蹤管理。C++11之前，C++中也有一個智能指針`auto_ptr`，也能對內存進行管理，但是很容易被用錯。

不過，使用C++11添加的智能指針的話，我們就很少需要使用到`new`和`delete`操作符。智能指針是自動化內存管理的一個鮮活的例子。當我們使用`unique_ptr`來動態分配對象，基本上不會遇到內存洩漏，因為在析構時會自動的為其所擁有內存使用`delete`操作。

唯一指針表達了其對對象指針的所有權，當對這段內存不在進行使用時，我們會將相關的對象所具有的內存進行釋放。這個類將讓我們永遠遠離內存洩漏(智能指針還有`shared_ptr`和`weak_ptr`，不過本節中，我們只關注於`unique_ptr`)。其不會多佔用空間，並且不會影響運行時性能，這相較於原始的裸指針和手動內存管理來說十分便捷。(當我們對相應的對象進行銷燬後，其內部的裸指針將會被設置為`nullptr`)。

本節中，我們將來看一下`unique_ptr`如何使用。

## How to do it...

我們將創建一個自定義的類型，在構造和析構函數中添加一些調試打印信息，之後展示`unique_ptr`如何對內存進行管理。我們將使用`unique`指針，並使用動態分配的方式對其進行實例化：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <memory>
   
   using namespace std;
   ```

2. 我們將實現一個小類型，後面會使用`unque_ptr`對其實例進行管理。其構造函數和析構函數都會在終端上打印相應的信息，所以之後的自動刪除中，我們會看到相應輸出的打印：

   ```c++
   class Foo
   {
   public:
       string name;
       
       Foo(string n)
       	: name{move(n)}
       { cout << "CTOR " << name << '\n'; }
       
       ~Foo() { cout << "DTOR " << name << '\n'; }
   };
   ```

3. 為了瞭解函數對唯一指針在作為參數傳入函數的限制，我們可以實現一個這樣的函數。其能處理一個`Foo`類型實例，並能將其名稱進行打印。注意，`unique`指針是非常智能的，其無額外開銷，並且類型安全，也可以為`null`。這就意味著我們仍然要在解引用之前，對指針進行檢查：

   ```c++
   void process_item(unique_ptr<Foo> p)
   {
       if (!p) { return; }
       
       cout << "Processing " << p->name << '\n';
   }
   ```

4. 主函數中，我們將開闢一個代碼段，在堆上創建兩個`Foo`對象，並且使用`unique`指針對內存進行管理。我們顯式的使用`new`操作符創建第一個對象實例，並且將其用來創建`unique_ptr<Foo>`變量`p1`。我們通過`make_unique<Foo>`的調用來創建第二個`unique`指針`p2`，我們直接傳入參數對`Foo`實例進行構建。這種方式更加的優雅，因為我們使用`auto`類型對類型進行推理，並且能在第一時間對對象進行訪問，並且其已經使用`unique_ptr`進行管理：

   ```c++
   int main()
   {
       {
           unique_ptr<Foo> p1 {new Foo{"foo"}};
           auto p2 (make_unique<Foo>("bar"));
       }
   ```

5. 離開這個代碼段時，所創建的對象將會立即銷燬，並且將內存進行釋放。讓我們來看一下`process_item`函數和如何使用`unique_ptr`。當創建一個新的`Foo`實例時，其就會被`unique_ptr`進行管理，然後參數的生命週期就在這個函數中。當`process_item`返回時，這個對象就會被銷燬：

   ```c++
   	process_item(make_unique<Foo>("foo1"));
   ```

6. 如將已經存在的對象傳入`process_item`函數，就需要將指針的所有權進行轉移，因為函數需要使用`unique_ptr`作為輸入參數，這就會有一次拷貝。但是，`unique_ptr`是無法進行拷貝的，其只能移動。現在讓我們來創建兩個`Foo`對象，並且將其中一個移動到`process_item`函數中。通過對輸出的查閱，我們可以瞭解到`foo2`在`process_item`返回時會被析構，因為其所有權已經被轉移。`foo3`將會持續留存於主函數中，直到主函數返回時才進行析構：

   ```c++
       auto p1 (make_unique<Foo>("foo2"));
       auto p2 (make_unique<Foo>("foo3"));
   
       process_item(move(p1));
   
       cout << "End of main()\n";
   }
   ```

7. 編譯並運行程序。首先，我們將看到`foo`和`bar`的構造和析構的輸出，離開代碼段時就被銷燬。我們要注意的是，銷燬的順序與創建的順序相反。下一個構造的就是`foo1`，其在對`process_item`調用時進行創建。當函數返回時，其就會被立即銷燬。然後，我們會創建`foo2`和`foo3`。因為之前轉移了指針的所有權，`foo2`會在`process_item`函數調用返回時被立即銷燬。另一個元素`foo3`將會在主函數返回時進行銷燬：

   ```c++
   $ ./unique_ptr
   CTOR foo
   CTOR bar
   DTOR bar
   DTOR foo
   CTOR foo1
   Processing foo1
   DTOR foo1
   CTOR foo2
   CTOR foo3
   Processing foo2
   DTOR foo2
   End of main()
   DTOR foo3
   ```

## How it works...

使用`std::unique_ptr`來處理堆上分配的對象非常簡單。我們初始化`unique`指針之後，其就會指向對應的對象，這樣程序就能自動的對其進行釋放操作。

當我們將`unique`指針賦予一些新指針時，其就會先刪除原先指向的對象，然後再存儲新的指針。一個`unique`指針變量`x`，我們可以使用`x.reset()`將其目前所指向的對象進行銷燬，然後在指向新的對象。另一種等價方式：`x = new_pointer`與`x.reset(new_pointer)`的方式等價。

> Note：
>
> 的確只有一種方式對`unique_ptr`所指向對象的內存進行釋放，那就是使用成員函數`release`，但這種方式並不推薦使用。

解引用之前，需要對指針進行檢查，並且其能使用於裸指針相同的方式進行運算。條件語句類似於`if (p){...}`和`if (p != nullptr){...}`，這與我們檢查裸指針的方式相同。

解引用一個`unique`指針可以通過`get()`函數完成，其會返回一個指向對應對象的裸指針，並且可以直接進行解引用。

`unique_ptr`有一個很重要的特性——實例無法進行拷貝，只能移動。這就是我們會將已經存在的`unique`指針的所有權轉移到`process_item`參數的原因。當我們想要拷貝`unique`指針時，就意味著兩個`unique`指針指向相應的對象，這與該指針的設計理念不符，所以`unique`指針對其指向對象的所有權必須唯一。

> Note：
>
> 對於其他的數據類型，由於智能指針的存在，所以很少使用`new`和`delete`對其進行手動操作。儘可能的使用智能指針！特別是`unqiue_ptr`，其在運行時無任何額外開銷。



