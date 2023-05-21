# 使用Lambda為std::function添加多態性

我們現在想編寫一些觀察函數，用來觀察一些變量的變化，當相應變量的數值發生改變時會進行提示，比如氣壓儀或是股票軟件這類的東西。當有些值發生變化時，對應的觀察對象就會被調用，之後以對應的方式進行反應。

為了實現這個觀察器，我們存儲了一些相關的函數對象在一個`vector`中，這些函數都接受以`int`變量作為參數，這個參數就是觀察到的值。 我們不清楚這些函數對於傳入值會做什麼特殊的處理，不過我們也沒有必要知道。

那麼`vector`中的函數對象類型是什麼呢？`std::vector<void (*)(int)>`，只要函數聲明成`void f(int)`就符合這個這個函數指針類型的定義。這對於Lambda表達式同樣有效，不過Lambda表達就是不能捕獲任何值了——` [](int x) {...} `。對於捕獲列表來說，Lambda表達式確實和普通的函數指針不同，因為其就不是一個函數指針，是一個函數對象，也就是將很多數據耦合到一個函數當中！想想在C++11時代之前，C++中沒有Lambda表達式，類和結構體通常會將數據和函數耦合在一起，並且當你修改一個類中的數據成員時，你得到的是一個完全不同類型的數據。

這樣`vector`中就無法將使用同樣類型名字的不同類別的對象存儲在一起。不能捕獲已存在的變量，這個限制對於用戶來說非常的不友好，也限制了代碼的使用範圍。用戶該如何保存不同類型的函數對象呢？對接口進行約束，採用特定的傳參方式傳入已經觀察到的值？

本節中，我們將展示使用`std::function`來解決這個問題，其將扮演一個“Lambda表達式多態包裝器”的角色，捕獲列表是不是空的都沒有關係。

## How to do it...

本節我們將創建很多Lambda表達式，其捕獲類型是完全不同的，但是其函數簽名的類型是相同的。然後，使用`std::function`將這些函數對象存入一個`vector`：

1. 包含必要的頭文件：

    ```c++
    #include <iostream>
    #include <deque>
    #include <list>
    #include <vector>
    #include <functional>
    ```
2. 我們先實現一個簡單的函數，其返回值是一個Lambda表達式。其需要傳入一個容器，並且返回一個函數對象，這個函數對象會以引用的方式捕獲容器。且函數對象本身接受傳入一個整型參數。當向函數對象傳入一個整型時，表達式將會把傳入的整型，添加到捕獲的容器尾部：

   ```c++
   template <typename C>
   static auto consumer (C &container)
       return [&] (auto value) {
       	container.push_back(value);
       };
   }
   ```

3. 另一個輔助函數將會打印傳入的容器中所有的內容：

   ```c++
   template <typename C>
   static void print (const C &c)
   {
       for (auto i : c) {
       	std::cout << i << ", ";
       }
       std::cout << '\n';
   }
   ```

4. 主函數中，我們先實例化一個`deque`和一個`list`，還有一個`vector`，這些容器存放的元素都是`int`類型。

   ```c++
   int main()
   {
       std::deque<int> d;
       std::list<int> l;
       std::vector<int> v;
   ```

5. 現在使用`consumer`函數對象與剛剛實例化的容器進行配合：將在`vector`中存儲生成自定義的函數對象。然後，用一個`vector`存放著三個函數對象。每個函數對象都會捕獲對應的容器對象。這些容器對象都是不同的類型，不過都是函數對象。所以，`vector`中的實例類型為` std::function<void(int)>`。所有函數對象都將隱式轉換成一個`std::function`對象，這樣就可以存儲在`vector`中了。

   ```c++
       const std::vector<std::function<void(int)>> consumers
       	{consumer(d), consumer(l), consumer(v)};
   ```

6. 現在我們將10個整型值傳入自定義函數對象：

   ```c++
       for (size_t i {0}; i < 10; ++i) {
           for (auto &&consume : consumers) {
           	consume(i);
           }
       }
   ```

7. 三個容器都包含了同樣的10個整數。讓我們來打印它們：

   ```c++
       print(d);
       print(l);
       print(v);
   }
   ```

8. 編譯運行程序，就會看到如下輸出，和我們的期望是一樣的。

   ```c++
   $ ./std_function
   0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
   0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
   0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
   ```

## How it works...

本節中比較複雜的地方就是這一行：

```c++
const std::vector<std::function<void(int)>> consumers
	{consumer(d), consumer(l), consumer(v)};
```

d，l和v對象都包裝進一個`consumer(...)`調用中。這個調用會返回多個函數對象，這樣每個函數對象都能捕獲這三個容器實例。雖然函數對象只能接受`int`型變量為參數，但是其捕獲到的是完全不同的類型。這就將不同類型的A、B和C變量存入到一個`vector`中一樣。

為了這個功能，需要找到一個共同的類型，也就是能保存不同類型的函數對象，這個類型就是`std::function`。一個`std::function<void(int)>`對象可以存儲我們的函數對象或傳統函數，其接受只有一個整型參數和返回為空的函數類型。這裡使用了多態性，為函數類型進行解耦。思考如下的寫法：

```c++
std::function<void(int)> f (
	[&vector](int x) { vector.push_back(x); });
```

這裡有個函數對象，將Lambda表達式包裝入`std::function`對象當中，當我們調用`f(123)`時，會產生一個虛函數調用，其會重定向到對象內部的實際執行函數。

當存儲函數對象時，`std::function`就顯得非常智能。當我們使用Lambda表達式捕獲越來越多的變量時，`std::function`實例的體積也會越來越大。如果對象體積特別特別巨大，那麼其將會在堆上分配出對應內存空間來存放這個函數對象。這些對於我們代碼的功能性並沒有什麼影響，這裡需要讓你瞭解一下是因為這樣的存儲方式會對性能有一定的影響。

> Note:
>
> 很多初學者都認為或希望`std::function<...>`的實際表達類型是一個Lambda表達式。不過這是錯誤的理解！因為有多態庫的幫助，其才能將Lambda表達式進行包裝，從而抹去類型的差異。



