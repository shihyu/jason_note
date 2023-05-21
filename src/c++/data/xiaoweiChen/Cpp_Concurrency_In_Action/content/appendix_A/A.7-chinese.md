# A.7 自動推導變量類型

`C++`是靜態語言：所有變量的類型，都會在編譯時被準確指定。所以，作為程序員你需要為每個變量指定對應的類型。

有些時候就需要使用一些繁瑣類型定義，比如：

```
std::map<std::string,std::unique_ptr<some_data>> m;
std::map<std::string,std::unique_ptr<some_data>>::iterator
      iter=m.find("my key");
```

常規的解決辦法是使用typedef來縮短類型名的長度。這種方式在`C++`11中仍然可行，不過這裡要介紹一種新的解決辦法：如果一個變量需要通過一個已初始化的變量類型來為其做聲明，那麼就可以直接使用`auto`關鍵字。這樣，編譯器就會通過已初始化的變量，去自動推斷變量的類型。

```
auto iter=m.find("my key");
```

當然，`auto`還有很多種用法：可以使用它來聲明const、指針或引用變量。這裡使用`auto`對相關類型進行了聲明：

```
auto i=42; // int
auto& j=i; // int&
auto const k=i; // int const
auto* const p=&i; // int * const
```

變量類型的推導規則是建立一些語言規則基礎上：函數模板參數。其聲明形式如下：

```
some-type-expression-involving-auto var=some-expression;
```

var變量的類型與聲明函數模板的參數的類型相同。要想替換`auto`，需要使用完整的類型參數：

```
template<typename T>
void f(type-expression var);
f(some-expression);
```

在使用`auto`的時候，數組類型將衰變為指針，引用將會被刪除(除非將類型進行顯式為引用)，比如：

```
int some_array[45];
auto p=some_array; // int*
int& r=*p;
auto x=r; // int
auto& y=r; // int&
```

這樣能大大簡化變量的聲明過程，特別是在類型標識符特別長，或不清楚具體類型的時候(例如，調用函數模板，等到的目標值類型就是不確定的)。