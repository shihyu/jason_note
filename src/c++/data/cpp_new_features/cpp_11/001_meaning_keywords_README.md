#### <h2 id="cpp_11_new_keywords">C++11含義變化或者新增含義關鍵字</h2>

##### <h4 id="auto">auto</h4>

C++11標準和C++98/03標準的auto是不同的。C++98/03標準中，auto表示自動儲存型別 ；C++11標準中，auto表示由編譯器靜態判斷其應有的型別。

C++98 auto

```C++
int a =10 ;  //擁有自動生命期
auto int b = 20 ;//擁有自動生命期
static int c = 30 ;//延長了生命期
```

C++11 auto

auto可以在聲明變數的時候根據變數初始值的型別自動為此變數選擇匹配的型別，類似的關鍵字還有decltype。

```C++
int a = 10;
auto b = a;//自動推斷型別，b為 int型別
auto c = 1.9;//自動推斷型別，c為double型別
auto d = 1.2e12L;//自動推斷型別，d 是 long double
```

<br />

##### <h4 id="clazz">class</h4>

C++11中對類(class)新增的特性：
* default/delete 控制預設函式
* override /final 強制覆寫/禁止覆寫虛擬函式
* 委託建構函式 Delegating constructors
* 繼承的建構函式 Inheriting constructors
* 類內部成員的初始化 Non-static data member initializers
* 移動建構和移動賦值

<br />

##### <h4 id="default">default</h4>

在C+11中，對於defaulted函式，編譯器會為其自動生成預設的函式定義體，從而獲得更高的程式碼執行效率，也可免除程式員手動定義該函式的工作量。

C++的類有四類特殊成員函式，它們分別是：預設建構函式、解構函式、複製建構函式以及複製賦值運算子。這些類的特殊成員函式負責創建、初始化、銷燬，或者複製類的物件。如果程式員沒有顯式地為一個類定義某個特殊成員函式，而又需要用到該特殊成員函式時，則編譯器會隱式的為這個類生成一個預設的特殊成員函式。當存在用戶自定義的特殊成員函式時，編譯器將不會隱式的自動生成預設特殊成員函式，而需要程式員手動編寫，加大了程式員的工作量。並且手動編寫的特殊成員函式的程式碼執行效率比編譯器自動生成的特殊成員函式低。

C++11標準引入了一個新特性：defaulted函式。程式員只需在函式聲明後加上”=default;”，就可將該函式聲明為defaulted函式，編譯器將為顯式聲明的defaulted函式自動生成函式體。

defaulted函式特性僅適用於類的特殊成員函式，且該特殊成員函式沒有預設參數。

defaulted函式既可以在類體裡(inline)定義，也可以在類體外(out-of-line)定義。

```C++
#include "default.hpp"
#include <iostream>
 
class Foo
{
	Foo(int x); // Custom constructor
	Foo() = default; // The compiler will now provide a default constructor for class Foo as well
};
 

struct A
{
	int x;
	A(int x = 1) : x(x) {} // user-defined default constructor
};
 
struct B : A
{
	// B::B() is implicitly-defined, calls A::A()
};
 
struct C
{
	A a;
	// C::C() is implicitly-defined, calls A::A()
};
 
struct D : A
{
	D(int y) : A(y) {}
	// D::D() is not declared because another constructor exists
};
 
struct E : A
{
	E(int y) : A(y) {}
	E() = default; // explicitly defaulted, calls A::A()
};
 
struct F
{
	int& ref; // reference member
	const int c; // const member
	// F::F() is implicitly defined as deleted
};
 
int test_default1()
{
	A a;
	B b;
	C c;
	// D d; // compile error
	E e;
	// F f; // compile error
 
	return 0;
}
 
///
struct widget
{
	widget() = default;
 
	inline widget& operator=(const widget&);
};
 
// Notice that you can default a special member function outside the body of a class as long as it’s inlinable.
inline widget& widget::operator=(const widget&) = default;
```

<br />

##### <h4 id="delete">delete</h4>

C++11 中，可在想要 “禁止使用” 的特殊成員函式聲明後加 “= delete”，而需要保留的加 "= default" 或者不採取操作
```C++
class LeafOfTree{
public:
　　LeafOfTree() = default;
    ~LeafOfTree() = default;　　
    LeafOfTree(const LeafOfTree&) = delete;　　// mark copy ctor or copy assignment operator as deleted functions
　　LeafOfTree & operator=(const LeafOfTree&) = delete; 
};
```

delete 的擴展
C++11 中，delete 關鍵字可用於任何函式，不僅僅侷限於類成員函式

<br />

##### <h4 id="export">export</h4>

C++11 中，不使用並保留該關鍵詞

<br />

##### <h4 id="extern">extern</h4>

外部樣板
```C++
extern template<class T>void(T t);
```

<br />

##### <h4 id="inline">inline</h4>

C++11中引入了內聯命名空間（inline namespace），它的特點就是不需要使用using語句就可以直接在外層命名空間使用該命名空間內部的內容，而且無需使用命名空間前綴。
```C++
inline namespace inline_namespacel{
    class Inlinel{
    public:
        int iv;
    };
}
namespace inline_namespaceli
    class Inline2{
    public:
        double dv;
    };
}
```

內聯命名空間的聲明方法就是在原來的聲明語法前面增加inline關鍵字。除此之外上面程式碼還有以下特點：

兩處聲明的命名空間同名，它們同屬一個命名空間。這是C++命名空間從來就有的特性。

第一次聲明命名空間時使用了inline關鍵字，這叫顯式內聯；第二次沒有使用inline關鍵字，但是由於第一次已經聲明瞭inline，這裡聲明的還是內聯命名空間。這種情況成為隱式內聯。

內聯命名空間聲明之後，就可以在外層命名空間不適用前綴而直接使用它們了。

```C++
namespace inline_test{
    inline namespace inline_namespace1{
        class Inlinel {
        public :
            int iv;
        };
    }
    namespace inline_namespace1{
        class Inline2{
        public :
            double dv ;
        };
    }
    void test_inline_namespace(){
        Inlinel inl;
        inl.iv = 5;
        Inline2 in2;in2.dv = 2;
    }
}
void test_inline_namespace2(){
    inline_test::Inlinel inl;
    in1.iv = 5;
    inline_test::Inline2 in2;
    in2.dv = 2;
}
```
上述程式碼中test_inline_namespace處在linline_namespace1的外層，所以可以直接使用Inline1和Inline2。test_inline_namespace2處在更外層，這時也只是需要使用外層命名空間inline_test前綴即可。
看起來inline_namespace就像不存在一樣。

<br />

##### <h4 id="mutable">mutable</h4>

C++11中的mutable是用來修改const函式中的不可修改類成員的缺陷

```C++
class Log{
 
public:
    //
    void print(const std::string& str) const
    {    
        printf("%s", str_cstr());
        //統計輸出次數
        printNums++;
    }
 
private:
    //這裡必須聲明為mutable
    mutable int printNums;
}
```

<br />

##### <h4 id="sizeof">sizeof</h4>

在標準C++，sizeof可以作用在物件以及類別上。但是不能夠做以下的事：
```C++
struct someType { otherType member; } ;
sizeof(SomeType: :member); //直接由someType型別取得非靜態成員的大小，C++03不行。C++11允哥
```
這會傳回OtherType的大小。C++03並不允許這樣做，所以會引發編譯錯誤。C++11將會允許這種使用。

```C++
#include <iostream>
using namespace  std;
struct Empty{};
struct Base{int a;};
struct Derived:Base
{
    int b;
};
struct Bit
{
    unsigned bit:1;
};
int main()
{
    Empty e;
    Derived d;
    Base& b = d;
    Bit bit;
    cout << sizeof(e) << endl;
    cout << sizeof(Empty) << endl;
    cout << sizeof(&e) << endl;
    cout << sizeof(Derived) << endl;
    cout << sizeof(d) << endl;
    cout << sizeof(void) << endl;//BAD
    return 0;
}
```

<br />

##### <h4 id="struct">struct</h4>

C++11 struct可以給每個成員變數賦予預設的初始值
```C++
struct Student{
    char* name = nullptr;
    unsigned int age  = 15;
    int number = 21509111;  
};
```
所有聲明的新結構物件就是預設上面的值。

<br />

##### <h4 id="using">using</h4>

* using 在 C++11之前主要用於名字空間、型別、函式與物件的引入，實際上是去除作用域的限制。
```C++
//引入名字空間
using namespace std;
//引入型別
using std::iostream;
//引入函式
using std::to_string;
//引入物件
using std::cout;
```

* 通過using引入函式可以解除函式隱藏
“隱藏”是指派生類的函式屏蔽了與其同名的基類函式，規則如下：
1）如果派生類的函式與基類的函式同名，但是參數不同。此時，不論有無virtual關鍵字，基類的函式將被隱藏（注意別與多載混淆）
2）如果派生類的函式與基類的函式同名，並且參數也相同，但是基類函式沒有virtual關鍵字。此時，基類的函式被隱藏（注意別與覆蓋混淆）
使用了using關鍵字，就可以避免1的情況，是的父類同名函式在子類中得以多載，不被隱藏
```C++
class Base{
public:
  void func()	{ cout << "in Base::func()" << endl; }
  void func(int n) { cout << "in Base::func(int)" << endl;}
};

class Sub : public Base {
public:
  using Base::func;	//引入父類所有同名函式func，解除函式隱藏
  void func()	{ cout<<"in Sub::func()"<<endl;}
};

int main() {
  Sub s;
  s.func();
  s.func(1); // Success!
}
```

* 使用 using 代替 typedef，給型別命名
```C++
using uint8=unsigned char; //等價於typedef unsigned char uint8;
using FunctionPtr = void (*)(); //等價於typedef void (FunctionPtr)();
template using MapString = std::map<T, char>; //定義樣板別名，注意typedef無法定義樣板別名，因為typedef只能作用於具體型別而非樣板
```

