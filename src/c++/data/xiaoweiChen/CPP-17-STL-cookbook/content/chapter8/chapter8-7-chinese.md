# 存儲不同的類型——std::variant

C++中支持使用`struct`和`class`的方式將不同類型的變量進行包裝。當我們想要使用一種類型來表示多種類型時，也可以使用`union`。不過`union`的問題在於我們無法知道，其是以哪種類型為基礎進行的初始化。

看一下下面的代碼：

```c++
union U {
    int a;
    char *b;
    float c;
};
void func(U u) { std::cout << u.b << '\n'; }	
```

當我們調用`func`時，其會將已整型`a`為基礎進行初始化的聯合體`t`進行打印，當然也無法阻止我們對其他成員進行訪問，就像使用字符串指針對成員`b`進行初始化了一樣，這段代碼會引發各種bug。當我們開始對聯合體進行打包之前，有一種輔助變量能夠告訴我們其對聯合體進行的初始化是安全的，其就是`std::variant`，在C++17中加入STL。

`variant`是一種新的類型，類型安全，並高效的聯合體類型。其不使用堆上的內存，所以在時間和空間上都非常高效。基於聯合體的解決方案，我們就不用自己再去進行實現了。其能單獨存儲引用、數組或`void`類型的成員變量。

本節中，我們將會瞭解一下由`vriant`帶來的好處。

## How to do it...

我們實現一個程序，其中有兩個類型：`cat`和`dog`。然後將貓狗混合的存儲於一個列表中，這個列表並不具備任何運行時多態性：

1. 包含必要的頭文件，並聲明所使用的命名空間：

   ```c++
   #include <iostream>
   #include <variant>
   #include <list>
   #include <string>
   #include <algorithm>
   
   using namespace std;
   ```

2. 接下來，我們將實現兩個具有類似功能的類，不過兩個類型之間並沒有什麼聯繫。第一個類型是`cat`。`cat`對象具有名字，並能喵喵叫：

   ```c++
   class cat {
       string name;
       
   public:
       cat(string n) : name{n} {}
       
       void meow() const {
       	cout << name << " says Meow!\n";
       }
   };
   ```

3. 另一個類是`dog`。`dog`能汪汪叫：

   ```c++
   class dog {
   	string name;
       
   public:
   	dog(string n) : name{n} {}
       
   	void woof() const {
   		cout << name << " says Woof!\n";
   	}
   };
   ```

4. 現在我們就可以來定義一個`animal`類型，其為`std::variant<dog, cat>`的別名類型。其和以前的聯合體一樣，同時具有`variant`的特性：

   ```c++
   using animal = variant<dog, cat>;
   ```

5. 編寫主函數之前，我們再來實現兩個輔助者。其中之一為動物判斷謂詞，通過調用`is_type<cat>(...)`或`is_type<dog>(...)`，可以判斷動物實例中的動物為`cat`或`dog`。其實現只需要對`holds_alternative`進行調用即可，其為`variant`類型的一個通用謂詞函數：

   ```c++
   template <typename T>
   bool is_type(const animal &a) {
   	return holds_alternative<T>(a);
   }
   ```

6. 第二個輔助者為一個結構體，其看起來像是一個函數對象。其實際是一個雙重函數對象，因為其`operator()`實現了兩次。一種實現是接受`dog`作為參數輸入，另一個實現是接受`cat`類型作為參數輸入。對於兩種實現，其會調用`woof`或`meow`函數：

   ```c++
   struct animal_voice
   {
       void operator()(const dog &d) const { d.woof(); }
       void operator()(const cat &c) const { c.meow(); }
   };
   ```

7. 現在讓我們使用這些輔助者和類型。首先，定義一個`animal`變量的實例，然後對其進行填充：

   ```c++
   int main()
   {
   	list<animal> l {cat{"Tuba"}, dog{"Balou"}, cat{"Bobby"}};
   ```

8. 現在，我們會將列表的中內容打印三次，並且每次都使用不同的方式。第一種使用`variant::index()`。因為`animal`類型是`variant<dog, cat>`類型的別名，其返回值的0號索引代表了一個`dog`的實例。1號索引則代表了`cat`的實例。這裡的關鍵是變量特化的順序。`switch-cast`代碼塊中，可以通過`get<T>`的方式獲取內部的`cat`或`dog`實例：

    ```c++
       for (const animal &a : l) {
           switch (a.index()) {
           case 0:
               get<dog>(a).woof();
               break;
           case 1:
               get<cat>(a).meow();
               break;
           }
       }
       cout << "-----\n";
    ```

9. 我們也可以顯示的使用類型作為其索引。`get_if<dog>`會返回一個指向`dog`類型的指針。如果沒有`dog`實例在列表中，那麼指針則為`null`。這樣，我們可以嘗試獲取下一種不同類型的實例，直到成功為止：

   ```c++
   	for (const animal &a : l) {
           if (const auto d (get_if<dog>(&a)); d) {
           	d->woof();
           } else if (const auto c (get_if<cat>(&a)); c) {
           	c->meow();
           }
       }
       cout << "-----\n";
   ```

10. 使用`variant::visit`是一種非常優雅的方式。這個函數能夠接受一個函數對象和一個`variant`實例。函數對象需要對`variant`中所有可能類型進行重載。我們在之前已經對`operator()`進行了重載，所以這裡可以直接對其進行使用：

    ```c++
    	for (const animal &a : l) {
    		visit(animal_voice{}, a);
    	}
    	cout << "-----\n";
    ```

11. 最後，我們將回來數一下`cat`和`dog`在列表中的數量。`is_type<T>`的`cat`和`dog`特化函數，將會與`std::count_if`結合起來使用，用來返回列表中不同實例的個數：

    ```c++
        cout << "There are "
            << count_if(begin(l), end(l), is_type<cat>)
            << " cats and "
            << count_if(begin(l), end(l), is_type<dog>)
            << " dogs in the list.\n";
    }
    ```

12. 編譯並運行程序，我們就會看到打印三次的結果都是相同的。然後，可以看到`is_type`和`count_if`配合的很不錯：

    ```c++
    $ ./variant
    Tuba says Meow!
    Balou says Woof!
    Bobby says Meow!
    -----
    Tuba says Meow!
    Balou says Woof!
    Bobby says Meow!
    -----
    Tuba says Meow!
    Balou says Woof!
    Bobby says Meow!
    -----
    There are 2 cats and 1 dogs in the list.
    ```

## How it works...

`std::variant`與`std::any`類型很相似，因為這兩個類型都能持有不同類型的變量，並且我們需要在運行時對不同對象進行區分。

另外，`std::variant`有一個模板列表，需要傳入可能在列表中的類型，這點與`std::any`截然不同。也就是說` std::variant<A, B, C>`必須是A、B或C其中一種實例。當然這也意味著其就不能持有其他類型的變量，除了列表中的類型`std::variant`沒有其他選擇。

` variant<A, B, C>`的類型定義，與以下聯合體定義類似：

 ``` c++
union U {
    A a;
    B b;
    C c;
};
 ```

當我們對`a`, `b`或`c`成員變量進行初始化時，聯合體中對其進行構建機制需要我們自行區分。`std::variant`類型就沒有這個問題。

本節的代碼中，我們使用了三種方式來處理`variant`中成員的內容。

首先，使用了`variant`的`index()`成員函數。對變量類型進行索引，`variant<A, B, C>` 中，索引值0代表A類型，1為B類型，2為C類型，以此類推來訪問複雜的`variant`對象。

下一種就是使用`get_if<T>`函數進行獲取。其能接受一個`variant`對象的地址，並且返回一個類型`T`的指針，指向其內容。如果`T`類型是錯誤，那麼返回的指針就為`null`指針。其也可能對`variant`變量使用`get<T>(x)`來獲取對其內容的引用，不過當這樣做失敗時，函數將會拋出一個異常(使用get-系列函數進行轉換之前，需要使用`holds_alternative<T>(x)`對其類型進行檢查)。

最後一種方式就是使用`std::visit`函數來進行，其能接受一個函數對象和一個`variant`實例。`visit`函數會對`variant`中內容的類型進行檢查，然後調用對應的函數對象的重載`operator()`操作符。

為了這個目的，我們實現為了`animal_voice`類型，將`visit`和`variant<dog, cat>`類型結合在了一起：

```c++
struct animal_voice
{
    void operator()(const dog &d) const { d.woof(); }
    void operator()(const cat &c) const { c.meow(); }
};
```

以`visit`的方式對`variant`進行訪問看起來更加的優雅一些，因為使用這種方法就不需要使用硬編碼的方式對`variant`內容中的類型進行判別。這就讓我們的代碼更加容易擴展。

> Note：
>
> `variant`類型不能為空的說法並不完全正確。將[std::monostate](http://zh.cppreference.com/w/cpp/utility/variant/monostate)類型添加到其類型列表中，其就能持有空值了。