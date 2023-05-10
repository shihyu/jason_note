# auto_ptr、unique_ptr、shared_ptr



範本auto_ptr是C++98提供的解決方案，C++11已摒棄。

範本unique_ptr、shared_ptr是C++11提供的解決方案.

為什麼要摒棄auto_ptr呢？

先來看下面的賦值語句：

```cpp
auto_ptr<string> ps(new string("I am a boy."));
auto_ptr<stirng> vocation;
vocation = ps;
```

上述賦值語句將完成什麼工作呢？如果ps和vocation是常規指針，則兩個指針將指向同一個string對象。這是不能接受的，因為程序將試圖刪除同一個對像兩次--一次是ps過期時，一次是vocation過期時。要避免這種問題，方法有多種。

- 定義賦值運算子，使之執行深賦值。這樣兩個指針將指向不同的對象，其中的一個對像是另一個對象的副本。
- 建立所有權（ownership）概念，對於特定的對象，只能有一個智能指針可擁有它，這樣只能擁有對象的智能指針的建構函式會刪除該對象。然後，讓賦值操作轉讓所有權。這就是用於auto_ptr和unique_ptr的策略，但**unique_ptr**的策略更嚴格。
- 建立智能更高的指針，跟蹤引用特定對象的智能指針數。這稱為引用計數（reference counting）。例如，賦值時，計數將加1，而指針過期時，計數將減1。僅當最後一個指針過期時，才呼叫delete。這是**shared_ptr**採用的策略。

每種方法都有其用途，

### 1 下面是一個不適合使用auto_ptr的示例：

```cpp
#include <iostream>
#include <string>
#include <memory>

using namespace std;

int main()
{
    auto_ptr<string> films[5] =
    {
        auto_ptr<string> (new string("one")),
        auto_ptr<string> (new string("two")),
        auto_ptr<string> (new string("three")),
        auto_ptr<string> (new string("four")),
        auto_ptr<string> (new string("five"))
    };
    auto_ptr<string> pwin;
    pwin = films[2];  // films[2] lose ownership

    cout << "films data is: " << endl;
    for(auto_ptr<string> s : films)
        cout << *s << endl;
    cout << "pwin: " << *pwin << endl;

    return 0;
}
```

下面是該程序的輸出：

```cpp
films data is:
one
two

Process returned -1073741819 (0xC0000005)   execution time : 1.659 s
Press any key to continue.
```

錯誤的使用auto_ptr可能導致問題（這種程式碼的行為是不確定的，其行為可能隨系統而異）。這裡的問題在於，下面的語句將所有權從films[2]轉讓給pwin：

```text
pwin = films[2];  // films[2] lose ownership
```

這導致films[2]不再引用該字串。在auto_ptr放棄對象的所有權後，邊可能使用它來訪問該對象。當程序列印films[2]指向的字串時，卻發現這是一個空指針，因此發生錯誤。

### 2 如果使用shared_ptr替換auto_ptr，則程序將正常運行。

示例程式碼：

```cpp
#include <iostream>
#include <string>
#include <memory>

using namespace std;

int main()
{
    shared_ptr<string> films[5] =
    {
        shared_ptr<string> (new string("one")),
        shared_ptr<string> (new string("two")),
        shared_ptr<string> (new string("three")),
        shared_ptr<string> (new string("four")),
        shared_ptr<string> (new string("five"))
    };
    shared_ptr<string> pwin;
    pwin = films[2];

    cout << "films data is: " << endl;
    for(shared_ptr<string> s : films)
        cout << *s << endl;
    cout << "pwin: " << *pwin << endl;

    return 0;
}
```

其輸出如下：

```cpp
films data is:
one
two
three
four
five
pwin: three
```

這次pwin和films[2]指向同一個對象，而引用計數從1增加到2。在程序末尾，後聲明的pwin首先呼叫其解構函式，該解構函式將引用計數降低到1。然後，shared_ptr陣列的成員被釋放，對films[2]呼叫解構函式時，將引用計數降低到0，並釋放以前分配的空間。

### 3 如果使用unique_ptr替換auto_ptr

```cpp
#include <iostream>
#include <string>
#include <memory>

using namespace std;

int main()
{
    unique_ptr<string> films[5] =
    {
        unique_ptr<string> (new string("one")),
        unique_ptr<string> (new string("two")),
        unique_ptr<string> (new string("three")),
        unique_ptr<string> (new string("four")),
        unique_ptr<string> (new string("five"))
    };
    unique_ptr<string> pwin;
    pwin = films[2];

    cout << "films data is: " << endl;
    for(unique_ptr<string> s : films)
        cout << *s << endl;
    cout << "pwin: " << *pwin << endl;

    return 0;
}
```

則程序將在下述程式碼行出現編譯錯誤。

```cpp
pwin = films[2];  // films[2] lose ownership
```

