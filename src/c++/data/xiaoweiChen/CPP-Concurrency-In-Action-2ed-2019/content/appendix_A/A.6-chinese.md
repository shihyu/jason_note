# A.6 變參模板

變參模板：就是可以使用不定數量的參數進行特化的模板。就像你接觸到的變參函數一樣，printf就接受可變參數。現在，就可以給你的模板指定不定數量的參數了。變參模板在整個`C++`線程庫中都有使用，例如：`std::thread`的構造函數就是一個變參類模板。從使用者的角度看，僅知道模板可以接受無限個參數就夠了，不過當要寫一個模板或對其工作原理很感興趣就需要了解一些細節。

和變參函數一樣，變參部分可以在參數列表章使用省略號`...`代表，變參模板需要在參數列表中使用省略號：

```c++
template<typename ... ParameterPack>
class my_template
{};
```

即使主模板不是變參模板，模板進行部分特化的類中，也可以使用可變參數模板。例如，`std::packaged_task<>`(見4.2.1節)的主模板就是一個簡單的模板，這個簡單的模板只有一個參數：

```c++
template<typename FunctionType>
class packaged_task;
```

不過，並不是所有地方都這樣定義。對於部分特化模板來說像是一個“佔位符”：

```c++
template<typename ReturnType,typename ... Args>
class packaged_task<ReturnType(Args...)>;
```

部分特化的類就包含實際定義的類。在第4章，可以寫一個`std::packaged_task<int(std::string,double)>`來聲明一個以`std::string`和double作為參數的任務，當執行這個任務後結果會由`std::future<int>`進行保存。

聲明展示了兩個變參模板的附加特性。第一個比較簡單：普通模板參數(例如ReturnType)和可變模板參數(Args)可以同時聲明。第二個特性，展示了`Args...`特化類的模板參數列表中如何使用，為了展示實例化模板中的Args的組成類型。實際上，因為是部分特化，所以其作為一種模式進行匹配。在列表中出現的類型(被Args捕獲)都會進行實例化。參數包(parameter pack)調用可變參數Args，並且使用`Args...`作為包的擴展。

和可變參函數一樣，變參部分可能什麼都沒有，也可能有很多類型項。例如，`std::packaged_task<my_class()>`中ReturnType參數就是my_class，並且Args參數包是空的，不過`std::packaged_task<void(int,double,my_class&,std::string*)>`中，ReturnType為void，並且Args列表中的類型就有：int, double, my_class&和std::string*。

## A.6.1 擴展參數包

變參模板主要依賴擴展功能，因為不能限制有更多的類型添加到模板參數中。首先，列表中的參數類型使用到的時候，可以使用包擴展，比如：需要給其他模板提供類型參數。

```c++
template<typename ... Params>
struct dummy
{
  std::tuple<Params...> data;
};
```

成員變量data是一個`std::tuple<>`實例，包含所有指定類型，所以dummy<int, double, char>的成員變量就為`std::tuple<int, double, char>`。可以將包擴展和普通類型相結合：

```c++
template<typename ... Params>
struct dummy2
{
  std::tuple<std::string,Params...> data;
};
```

這次，元組中添加了額外的(第一個)成員類型`std::string`。其優雅之處在於，可以通過包擴展的方式創建一種模式，這種模式會在之後將每個元素拷貝到擴展之中，可以使用`...`來表示擴展模式的結束。例如，創建使用參數包來創建元組中所有的元素，不如在元組中創建指針，或使用`std::unique_ptr<>`指針，指向對應元素：

```c++
template<typename ... Params>
struct dummy3
{
  std::tuple<Params* ...> pointers;
  std::tuple<std::unique_ptr<Params> ...> unique_pointers;
};
```

類型表達式會比較複雜，提供的參數包是在類型表達式中產生，並且表達式中使用`...`作為擴展。當參數包已經擴展 ，包中的每一項都會代替對應的類型表達式，在結果列表中產生相應的數據項。因此，當參數包Params包含int，int，char類型，那麼`std::tuple<std::pair<std::unique_ptr<Params>,double> ... >`將擴展為`std::tuple<std::pair<std::unique_ptr<int>,double>`,`std::pair<std::unique_ptr<int>,double>`,`std::pair<std::unique_ptr<char>, double> >`。如果包擴展當做模板參數列表使用時，模板就不需要變長的參數了。如果不需要了，參數包就要對模板參數的要求進行準確的匹配：

```c++
template<typename ... Types>
struct dummy4
{
  std::pair<Types...> data;
};
dummy4<int,char> a;  // 1 ok，為std::pair<int, char>
dummy4<int> b;  // 2 錯誤，無第二個類型
dummy4<int,int,int> c;  // 3 錯誤，類型太多
```

可以使用包擴展的方式，對函數的參數進行聲明：

```c++
template<typename ... Args>
void foo(Args ... args);
```

這將會創建一個新參數包args，其是一組函數參數，而非一組類型，並且這裡`...`也能像之前一樣進行擴展。例如，可以在`std::thread`的構造函數中使用，使用右值引用的方式獲取函數所有的參數(見A.1節)：

```c++
template<typename CallableType,typename ... Args>
thread::thread(CallableType&& func,Args&& ... args);
```

函數參數包也可以用來調用其他函數，將制定包擴展成參數列表，匹配調用的函數。如同類型擴展一樣，也可以使用某種模式對參數列表進行擴展。例如，使用`std::forward()`以右值引用的方式來保存提供給函數的參數：

```c++
template<typename ... ArgTypes>
void bar(ArgTypes&& ... args)
{
  foo(std::forward<ArgTypes>(args)...);
}
```

注意一下這個例子，包擴展包括對類型包ArgTypes和函數參數包args的擴展，並且省略了其餘的表達式。當這樣調用bar函數：

```c++
int i;
bar(i,3.141,std::string("hello "));
```

將會擴展為

```c++
template<>
void bar<int&,double,std::string>(
         int& args_1,
         double&& args_2,
         std::string&& args_3)
{
  foo(std::forward<int&>(args_1),
      std::forward<double>(args_2),
      std::forward<std::string>(args_3));
}
```

這樣就將第一個參數以左值引用的形式，正確的傳遞給了foo函數，其他兩個函數都是以右值引用的方式傳入的。

最後一件事，參數包中使用`sizeof...`操作可以獲取類型參數類型的大小，`sizeof...(p)`就是p參數包中所包含元素的個數。不管是類型參數包或函數參數包，結果都是一樣的。這可能是唯一一次在使用參數包的時候，沒有加省略號；這裡的省略號是作為`sizeof...`操作的一部分，所以不算是用到省略號。

下面的函數會返回參數的數量：

```c++
template<typename ... Args>
unsigned count_args(Args ... args)
{
  return sizeof... (Args);
}
```

就像普通的sizeof操作一樣，`sizeof...`的結果為常量表達式，所以其可以用來指定定義數組長度，等等。