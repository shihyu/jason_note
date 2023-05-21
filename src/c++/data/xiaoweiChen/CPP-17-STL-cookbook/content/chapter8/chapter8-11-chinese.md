# 使用智能指針簡化處理遺留API

智能指針(`unique_ptr`，`shared_ptr`和`weak_ptr`)非常有用，並且對於開發者來說，可以使用其來代替手動分配和釋放空間。

當有對象不能使用`new`操作進行創建，或不能使用`delete`進行釋放呢？過去有很多庫都有自己的分配和釋放函數。這看起來好像是個問題，因為我麼瞭解的智能指針都依賴於`new`和`delete`。那麼如何在智能指針中，使用指定的工廠函數對特定類型的對象進行創建或是銷燬呢？

這個問題一點都不難。本節中，我們將來了解一下如何為智能指針指定特定的分配器和銷燬器。

## How to do it...

本節中，我們將定義一種不能使用`new`創建的類型，並且也不能使用`delete`進行釋放。對於這種限制，我們依舊選擇直接使用智能指針，這裡使用`unique_ptr`和`shared_ptr`實例來進行演示。

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <memory>
   #include <string>
   
   using namespace std; 
   ```

2. 聲明一個類，將其構造函數和析構函數聲明為`private`。我們使用這樣的方式來模擬無法直接和銷燬對象實例的情況：

   ```c++
   class Foo
   {
       string name;
       
       Foo(string n)
       	: name{n}
       { cout << "CTOR " << name << '\n'; }
       
       ~Foo() { cout << "DTOR " << name << '\n';}
   ```

3. 然後，聲明兩個靜態函數`create_foo`和`destroy_foo`，這兩個函數用來對`Foo`實例進行創建和銷燬，其會對裸指針進行操作。這是用來模擬使用舊C風格的API，這樣我們就不能用之前的方式直接對`shared_ptr`指針進行使用：

   ```c++
   public:
       static Foo* create_foo(string s) {
       	return new Foo{move(s)};
       }
   
       static void destroy_foo(Foo *p) { delete p; }
   };
   ```

4. 現在，我們用`shared_ptr`來對這樣的對象進行管理。對於共享指針，我們可以通過`create_foo`函數來構造相應的對象。只有銷燬的方式有些問題，因為`shared_ptr`默認的銷燬方式會有問題。解決方法就是我們將自定義的銷燬器給予`shared_ptr`。刪除函數或刪除可調用對象的函數簽名需要需要與`destroy_foo`函數統一。當我們的刪除函數非常複雜，那我們可以使用Lambda表達式對其進行包裝：

   ```c++
   static shared_ptr<Foo> make_shared_foo(string s)
   {
   	return {Foo::create_foo(move(s)), Foo::destroy_foo};
   }
   ```

5. 需要注意的是`make_shared_foo`函數，將會返回一個普通的`shared_ptr<Foo>`實例，因為設置了自定義的銷燬器，並不會對其類型有所影響。從編程角度上，之前是因為`shared_ptr`調用了虛函數，將設置銷燬器的步驟隱藏了。唯一指針(`unique_ptr`)不會帶來任何額外開銷，所以這種方式不適合唯一指針。目前，我們就需要對`unique_ptr`所持有的類型進行修改。我們將`void(*)(Foo*)`類型作為第二個模板參數傳入，其也就是`destroy_foo`函數的類型：

   ```c++
   static unique_ptr<Foo, void (*)(Foo*)> make_unique_foo(string s)
   {
   	return {Foo::create_foo(move(s)), Foo::destroy_foo};
   }
   ```

6. 主函數中，我們直接使用函數對兩個智能指針進行實例化。程序的輸出中，我們將看到相應的對象會被創建，然後自動銷燬：

   ```c++
   int main()
   {
       auto ps (make_shared_foo("shared Foo instance"));
       auto pu (make_unique_foo("unique Foo instance"));
   }
   ```

7. 編譯並運行程序，我們就會得到如下輸出，輸出與我們的期望一致：

   ```c++
   $ ./legacy_shared_ptr
   CTOR shared Foo instance
   CTOR unique Foo instance
   DTOR unique Foo instance
   DTOR shared Foo instance
   ```

## How it works...

通常來說，當`unique_ptr`和`shared_ptr`要銷燬其持有的對象時，只會對內部指針使用`delete`。本節中，我們的類無法使用C++常用的方式進行創建和銷燬。`Foo::create_foo`函數會返回一個構造好的`Foo`指針，這對於智能指針來說沒什麼，因為指針指針也可以對裸指針進行管理。

其問題在於，當對象不能使用默認方式刪除時，如何讓`unique_ptr`和`shared_ptr`接觸到對象的析構函數。

在這方面，兩種智能指針有些不同。為了為`unique_ptr`設置一個自定義銷燬器，我們需要對其類型進行修改。因為`Foo`的銷燬函數為` void Foo::destroy_foo(Foo*); `，那麼`unique_ptr`所是有`Foo`的類型必須為` unique_ptr<Foo, void(*)(Foo*)> `。現在，`unique_ptr`也就獲取了`destroy_foo`的指針了，在`make_unique_foo`函數中其作為構造的第二個模板參數傳入。

`unique_ptr`為了自定義銷燬器函數，需要對持有類型進行修改，那麼為什麼`shared_ptr`就不需要呢？我們也能向`shared_ptr`的第二個模板參數傳入對應的類型的呀。為什麼`shared_ptr`的操作就要比`unique_ptr`簡單呢？

這是因為`shared_ptr`支持可調用刪除器對象，而不用影響共享指針做指向的類型，這種功能在控制塊中進行。共享指針的控制塊是一個對象的虛函數。這也就意味著標準共享指針的控制塊，與給定了自定義的銷燬器的共享指針的控制塊不同！當我們要讓一個唯一指針使用一個自定義銷燬器時，就需要改變唯一指針所指向的類型。當我們想讓共享指針使用自定義銷燬器時，只需要對內部控制塊的類型進行修改即可，這種修改的過程對我們是不可見的，因為其不同隱藏在虛函數的函數接口中。

當然，我們可以手動的為`unique_ptr`做發生在`shared_ptr`上的事情，不過這會增加運行時的開銷。這是我們所不希望看到的，因為`unique_ptr`能夠保證在運行時無任何額外開銷。