#### <h2 id="cpp_11_new_keywords">C++11新增關鍵字</h2>

##### <h4 id="thread_local">thread_local</h4>

thread_local是C++11增加的存儲類指定符

C++中有4種存儲週期：
  * automatic
  * static
  * dynamic
  * thread

有且只有thread_local關鍵字修飾的變數具有執行緒週期(thread duration)，這些變數(或者說物件）在執行緒開始的時候被生成(allocated)，在執行緒結束的時候被銷燬(deallocated)。並且每 一個執行緒都擁有一個獨立的變數實體(Each thread has its own instance of the object)。thread_local 可以和static 與 extern關鍵字聯合使用，這將影響變數的連結屬性(to adjust linkage)。

那麼，哪些變數可以被聲明為thread_local？可以是以下3類：

  * 命名空間下的全局變數
  * 類的static成員變數
  * 本地變數

thread_local案例

```C++
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
 
thread_local unsigned int rage = 1;
std::mutex cout_mutex;
 
void increase_rage(const std::string& thread_name) {
  ++rage; // 在鎖外修改 OK ；這是執行緒局域變數
  std::lock_guard<std::mutex> lock(cout_mutex);
  std::cout << "Rage counter for " << thread_name << ": " << rage << '\n';
}
 
void test() {
  thread_local int i = 0;
  printf("id=%d, n=%d\n", std::this_thread::get_id(), i);
  i++;
}
 
void test2() {
  test();
  test();
}
 
int main() {
  std::thread a(increase_rage, "a"), b(increase_rage, "b");
 
  {
    std::lock_guard<std::mutex> lock(cout_mutex);
    std::cout << "Rage counter for main: " << rage << '\n';
  }
 
  a.join();
  b.join();
 
  std::thread t1(test);
  std::thread t2(test);
  t1.join();
  t2.join();
 
  std::thread t3(test2);
  t3.join();
 
  system("pause");
  return 0;
}
```

<br/>

##### <h4 id="static_assert">static_assert</h4>

```C++
struct MyClass
{
    char m_value;
};

struct MyEmptyClass
{
    void func();
};

// 確保MyEmptyClass是一個空類（沒有任何非靜態成員變數，也沒有虛擬函式）
static_assert(std::is_empty<MyEmptyClass>::value, "empty class needed");

//確保MyClass是一個非空類
static_assert(!std::is_empty<MyClass>::value, "non-empty class needed");

template <typename T, typename U, typename V>
class MyTemplate
{
    // 確保樣板參數T是一個非空類
    static_assert(
        !std::is_empty<T>::value,
        "T should be n non-empty class"
    );

    // 確保樣板參數U是一個空類
    static_assert(
        std::is_empty<U>::value,
        "U should be an empty class"
    );

    // 確保樣板參數V是從std::allocator<T>直接或間接派生而來，
    // 或者V就是std::allocator<T>
    static_assert(
        std::is_base_of<std::allocator<T>, V>::value,
        "V should inherit from std::allocator<T>"
    );

};

// 僅當樣板實體化時，MyTemplate裡面的那三個static_assert才會真正被演算，
// 藉此檢查樣板參數是否符合期望
template class MyTemplate<MyClass, MyEmptyClass, std::allocator<MyClass>>;
```

<br/>

##### <h4 id="nullptr">nullptr</h4>

nullptr關鍵字用於標識空指標，是std::nullptr_t型別的（constexpr）變數。它可以轉換成任何指標型別和bool布爾型別（主要是為了兼容普通指標可以作為條件判斷語句的寫法），但是不能被轉換為整數。
```C++
char *p1 = nullptr;     // 正確
int  *p2 = nullptr;     // 正確
bool b = nullptr;       // 正確. if(b)判斷為false
int a = nullptr;        // error
```

<br/>

##### <h4 id="noexcept">noexcept</h4>

noexcept有兩類作用：noexcept指定符和noexcept運算子

* noexcept 指定符
```C++
void f() noexcept;  // 函式 f() 不拋出
void (*fp)() noexcept(false); // fp 指向可能拋出的函式
void g(void pfa() noexcept);  // g 接收指向不拋出的函式的指標
// typedef int (*pf)() noexcept; // 錯誤
```

* noexcept運算子
```C++
#include <iostream>
#include <utility>
#include <vector>
 
// noexcept 運算子 
void may_throw() {};
void no_throw() noexcept {};
auto lmay_throw = [] {};
auto lno_throw = []() noexcept {};
 
class T {
};
class T1 {
public:
  ~T1() {}
};
class T2 {
public:
  ~T2() {}
  int v;
};
class T3 {
public:
  ~T3() {}
  std::vector<int> v;
};
class T4 {
public:
  std::vector<int> v;
};
 
int main()
{
  T t;
  T1 t1;
  T2 t2;
  T3 t3;
  T4 t4;
 
  std::vector<int> vc;
 
  std::cout << std::boolalpha
    << "Is may_throw() noexcept? " << noexcept(may_throw()) << '\n'
    << "Is no_throw() noexcept? " << noexcept(no_throw()) << '\n'
    << "Is lmay_throw() noexcept? " << noexcept(lmay_throw()) << '\n'
    << "Is lno_throw() noexcept? " << noexcept(lno_throw()) << '\n'
    << "Is ~T1() noexcept? " << noexcept(std::declval<T1>().~T1()) << '\n'
    << '\n'
    << '\n'
 
    << "Is T(rvalue T) noexcept? " << noexcept(T(std::declval<T>())) << '\n'
    << "Is T(lvalue T) noexcept? " << noexcept(T(t)) << '\n'
    << '\n'
 
    << "Is T1(rvalue T1) noexcept? " << noexcept(T1(std::declval<T1>())) << '\n'
    << "Is T1(lvalue T1) noexcept? " << noexcept(T1(t1)) << '\n'
    << '\n'
 
    << "Is T2(rvalue T2) noexcept? " << noexcept(T2(std::declval<T2>())) << '\n'
    << "Is T2(lvalue T2) noexcept? " << noexcept(T2(t2)) << '\n'
    << '\n'
 
    << "Is T3(rvalue T3) noexcept? " << noexcept(T3(std::declval<T3>())) << '\n'
    << "Is T3(lvalue T3) noexcept? " << noexcept(T3(t3)) << '\n'
    << '\n'
 
    << "Is T4(rvalue T4) noexcept? " << noexcept(T4(std::declval<T4>())) << '\n'
    << "Is T4(lvalue T4) noexcept? " << noexcept(T4(t4)) << '\n'
    << '\n'
 
    << "Is std::vector<int>(rvalue std::vector<int>) noexcept? " << noexcept(std::vector<int>(std::declval<std::vector<int>>())) << '\n'
    << "Is std::vector<int>(lvalue std::vector<int>) noexcept? " << noexcept(std::vector<int>(vc)) << '\n';
 
  system("pause");
  return 0;
}
```

<br/>

##### <h4 id="decltype">decltype</h4>

decltype型別說明符，它的作用是選擇並返回操作數的數據型別，在此過程中，編譯器分析表達式並得到它的型別，卻不實際計算表達式的值。
decltype用法
* 基本用法
```C++
int getSize();

int main(void)
{
    int tempA = 2;
    
    /*1.dclTempA為int*/
    decltype(tempA) dclTempA;
    /*2.dclTempB為int，對於getSize根本沒有定義，但是程式依舊正常，因為decltype只做分析，並不調用getSize，*/
    decltype(getSize()) dclTempB;

    return 0;
}
```

* 與const結合
```C++
double tempA = 3.0;
    const double ctempA = 5.0;
    const double ctempB = 6.0；
    const double *const cptrTempA = &ctempA;
    
    /*1.dclTempA推斷為const double（保留頂層const，此處與auto不同）*/
    decltype(ctempA) dclTempA = 4.1;
    /*2.dclTempA為const double，不能對其賦值，編譯不過*/
    dclTempA = 5;
    /*3.dclTempB推斷為const double * const*/
    decltype(cptrTempA) dclTempB = &ctempA;
    /*4.輸出為4（32位元元電腦）和5*/
    cout<<sizeof(dclTempB)<<"    "<<*dclTempB<<endl;
    /*5.保留頂層const，不能修改指標指向的物件，編譯不過*/
    dclTempB = &ctempB;
    /*6.保留底層const，不能修改指標指向的物件的值，編譯不過*/
    *dclTempB = 7.0;
```C

* 與參照結合
```C
int tempA = 0, &refTempA = tempA;

    /*1.dclTempA為參照，綁定到tempA*/
    decltype(refTempA) dclTempA = tempA;
    /*2.dclTempB為參照，必須綁定到變數，編譯不過*/
    decltype(refTempA) dclTempB = 0;
    /*3.dclTempC為參照，必須初始化，編譯不過*/
    decltype(refTempA) dclTempC;
    /*4.雙層括號表示參照，dclTempD為參照，綁定到tempA*/
    decltype((tempA)) dclTempD = tempA;
    
    const int ctempA = 1, &crefTempA = ctempA;
    
    /*5.dclTempE為常數參照，可以綁定到普通變數tempA*/
    decltype(crefTempA) dclTempE = tempA;
    /*6.dclTempF為常數參照，可以綁定到常數ctempA*/
    decltype(crefTempA) dclTempF = ctempA;
    /*7.dclTempG為常數參照，綁定到一個臨時變數*/
    decltype(crefTempA) dclTempG = 0;
    /*8.dclTempH為常數參照，必須初始化，編譯不過*/
    decltype(crefTempA) dclTempH;
    /*9.雙層括號表示參照,dclTempI為常數參照，可以綁定到普通變數tempA*/
    decltype((ctempA))  dclTempI = ctempA;
```

* 與指標結合
```C++
int tempA = 2;
int *ptrTempA = &tempA;
/*1.常規使用dclTempA為一個int *的指標*/
decltype(ptrTempA) dclTempA;
/*2.需要特別注意，表達式內容為解參照操作，dclTempB為一個參照，參照必須初始化，故編譯不過*/
decltype(*ptrTempA) dclTempB;
```

decltype總結
decltype和auto都可以用來推斷型別，但是二者有幾處明顯的差異：
1.auto忽略頂層const，decltype保留頂層const；
2.對參照操作，auto推斷出原有型別，decltype推斷出參照；
3.對解參照操作，auto推斷出原有型別，decltype推斷出參照；
4.auto推斷時會實際執行，decltype不會執行，只做分析。
總之在使用中過程中和const、參照和指標結合時需要特別小心。

<br/>

##### <h4 id="constexpr">constexpr</h4>

constexpr意義
將變數聲明為constexpr型別以便由編譯器來驗證變數是否是一個常數表達式（不會改變，在編譯過程中就能得到計算結果的表達式）。是一種比const更強的約束，這樣可以得到更好的效率和安全性。

constexpr用法
* 修飾函式
```C++
/*1.如果size在編譯時能確定，那麼回傳值就可以是constexpr,編譯通過*/
constexpr int getSizeA(int size)
{
    return 4*size;
}
/*2.編譯通過，有告警：在constexpr中定義變數*/
constexpr int getSizeB(int size)
{
    int index = 0;
    return 4;
}
/*3.編譯通過，有告警：在constexpr中定義變數（這個有點迷糊）*/
constexpr int getSizeC(int size)
{
    constexpr int index = 0;
    return 4;
}
/*4.編譯通過，有告警：使用了if語句（使用switch也會告警）*/
constexpr int getSizeD(int size)
{
    if(0)
    {}
    return 4;
}
/*5.定義變數並且沒有初始化，編譯不過*/
constexpr int getSizeE(int size)
{
    int index;
    return 4;
}
/*6.rand()為運行期函式，不能在編譯期確定，編譯不過*/
constexpr int getSizeF(int size)
{
    return 4*rand();
}
/*7.使用了for，編譯不過*/
constexpr int getSizeG(int size)
{
    for(;0;)
    {}
    return 4*rand();
}
```

* 修改型別
```C++
int tempA;
cin>>tempA;

const int ctempA = 4;
const int ctempB = tempA;
/*1.可以再編譯器確定，編譯通過*/
constexpr int conexprA = 4;
constexpr int conexprB = conexprA + 1;
constexpr int conexprC = getSizeA(conexprA);
constexpr int conexprD = ctempA;
/*2.不能在編譯期決定，編譯不過*/
constexpr int conexprE = tempA;
constexpr int conexprF = ctempB;
```

* 修飾指標
```C++
int g_tempA = 4;
const int g_conTempA = 4;
constexpr int g_conexprTempA = 4;

int main(void)
{
    int tempA = 4;
    const int conTempA = 4;
    constexpr int conexprTempA = 4;
    
    /*1.正常運行,編譯通過*/
    const int *conptrA = &tempA;
    const int *conptrB = &conTempA;
    const int *conptrC = &conexprTempA;
    /*2.局部變數的地址要運行時才能確認，故不能在編譯期決定，編譯不過*/
    constexpr int *conexprPtrA = &tempA;
    constexpr int *conexprPtrB = &conTempA
    constexpr int *conexprPtrC = &conexprTempA;
    /*3.第一個通過，後面兩個不過,因為constexpr int *所限定的是指標是常數，故不能將常數的地址賦給頂層const*/
    constexpr int *conexprPtrD = &g_tempA;
    constexpr int *conexprPtrE = &g_conTempA
    constexpr int *conexprPtrF = &g_conexprTempA;
    /*4.局部變數的地址要運行時才能確認，故不能在編譯期決定，編譯不過*/
    constexpr const int *conexprConPtrA = &tempA;
    constexpr const int *conexprConPtrB = &conTempA;
    constexpr const int *conexprConPtrC = &conexprTempA;
    /*5.正常運行，編譯通過*/
    constexpr const int *conexprConPtrD = &g_tempA;
    constexpr const int *conexprConPtrE = &g_conTempA;
    constexpr const int *conexprConPtrF = &g_conexprTempA;

    return 0;
}
 ```
 
* 修飾參照
```C++
int g_tempA = 4;
const int g_conTempA = 4;
constexpr int g_conexprTempA = 4;

int main(void)
{
    int tempA = 4;
    const int conTempA = 4;
    constexpr int conexprTempA = 4;
    /*1.正常運行，編譯通過*/
    const int &conptrA = tempA;
    const int &conptrB = conTempA;
    const int &conptrC = conexprTempA;
    /*2.有兩個問題：一是參照到局部變數，不能再編譯器確定；二是conexprPtrB和conexprPtrC應該為constexpr const型別，編譯不過*/
    constexpr int &conexprPtrA = tempA;
    constexpr int &conexprPtrB = conTempA 
    constexpr int &conexprPtrC = conexprTempA;
    /*3.第一個編譯通過，後兩個不通過，原因是因為conexprPtrE和conexprPtrF應該為constexpr const型別*/
    constexpr int &conexprPtrD = g_tempA;
    constexpr int &conexprPtrE = g_conTempA;
    constexpr int &conexprPtrF = g_conexprTempA;
    /*4.正常運行，編譯通過*/
    constexpr const int &conexprConPtrD = g_tempA;
    constexpr const int &conexprConPtrE = g_conTempA;
    constexpr const int &conexprConPtrF = g_conexprTempA;

    return 0;
}
```

<br/>

##### <h4 id="char16_t">char16_t和char32_t</h4>

char16_t和char32_t:

產生原因：
隨著編程人員日益的熟悉Unicode，型別wchar_t顯然已經滿足不了需求，在電腦系統上進行的編碼字符和字串編碼時，僅僅使用Unicode碼點顯然是不夠的。
比如：如果在進行字串編碼時，如果有特定長度和符號特徵的型別將很有幫助，而型別wchar_t的長度和符號特徵隨實現而已。
因此C++11新增了型別char16_t,char32_t。

char16_t:無符號型別，長16位元元，
char32_t無符號型別，長32位元元

C++11使用前綴u表示char16_t字符常數和字串常數如：u‘L’；u“lilili”;
C++11使用前綴U表示char32_t字符常數和字串常數如：U'L';U"lilili";

型別char16_t與/u00F6形式的通用字符名匹配，
型別char32_t與/U0000222B形式的通用字符名匹配。
前綴u和U分別指出字符字面值的型別為char16_t和char32_t。

注意：
如果你在VS中使用char16_t或者char32_t的話，不要加前綴u或者U只能加前綴L.

<br/>

##### <h4 id="alignof">alignof和alignas</h4>

C++11新引入操作符alignof， 對齊描述符alignas，基本對齊值 alignof(std::max_align_t)

alignas可以接受常數表達式和型別作為參數，可以修飾變數、類的數據成員等，不能修飾位元元元欄和用register申明的變數。一般往大對齊。

```C++
struct s3
{
    char s;
    double d;
    int i;
};
 
 
struct s11
{
    alignas(16) char s;
    int i;
};
 
struct s12
{
    alignas(16) char s;
    int i;
};
 
 
// alignof
cout << "-------------------alignof---------------------" << endl;
// 基本對齊值
cout << "alignof(std::max_align_t)	" << alignof(std::max_align_t) << endl;
cout << endl;
cout << "-------basic type" << endl;
cout << "alignof(char)		" << alignof(char) << endl;
cout << "alignof(int)		" << alignof(int) << endl;
cout << "alignof(double)	" << alignof(double) << endl;
 
cout << endl;
cout << "-------struct" << endl;
cout << "alignof(s1)		" << alignof(s1) << endl;
cout << "alignof(s2)		" << alignof(s2) << endl;
cout << "alignof(s3)		" << alignof(s3) << endl;
 
cout << endl;
cout << endl;
 
// alignas
cout << "-------------------alignas---------------------" << endl;
cout << "alignof(s1)		" << alignof(s1) << endl;
cout << "alignof(s11)		" << alignof(s11) << endl;
cout << "alignof(s12)		" << alignof(s12) << endl;
 
cout << "sizeof(s1)    	" << sizeof(s1) << endl;
cout << "sizeof(s11)	" << sizeof(s11) << endl;
cout << "sizeof(s12)	" << sizeof(s12) << endl;
```

//結果如下：
```C++
-------------------alignof---------------------
alignof(std::max_align_t)	8

-------basic type
alignof(char)	1
alignof(int)	4
alignof(double)	8

-------struct
alignof(s1)	4
alignof(s2)	8
alignof(s3)	8


-------------------alignas---------------------
alignof(s1)	4
alignof(s11)	16
alignof(s12)	16
sizeof(s1)	4
sizeof(s11)	16
sizeof(s12)	16
```
