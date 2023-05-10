

# C++ std::move

https://medium.com/@berton1679/c-std-move-133d99d87fc1

一開始接觸c++11/14的人而言，絕大多數都會對 `std::move()` 這個神奇的function 所困惑。首先讓我們直接看一下[cppreference](https://en.cppreference.com/w/cpp/utility/move) 中的介紹，

```
std::move is used to indicate that an object t may be "moved from", i.e. allowing the efficient transfer of resources from t to another object.In particular, std::move produces an xvalue expression that identifies its argument t. It is exactly equivalent to a static_cast to an rvalue reference type.
```

而其實 `std::move()` 並沒有移動任何的物件，基本上只是轉型而已，程式碼基本上是如下

```
static_cast<typename std::remove_reference<T>::type&&>(t)
```

所以他並不是什麼神奇的黑魔法，就只是轉型!

至於使用時機，我們用以下的class 作為例子方便說明

```cpp
class BigObject
{
public:
    BigObject()
    {
        std::cout<<__PRETTY_FUNCTION__<<std::endl;
    }
    BigObject(int g)
    {
        std::cout<<__PRETTY_FUNCTION__<<std::endl;
        gg = g;
    }
    ~BigObject()
    {
        std::cout<<__PRETTY_FUNCTION__<<std::endl;
    }
    BigObject (const BigObject &b)
    {
        std::cout<<__PRETTY_FUNCTION__<<std::endl;
    }
    BigObject (BigObject &&b)
    {
        std::cout<<__PRETTY_FUNCTION__<<std::endl;
        this->gg = std::move(b.gg);
    }
    int gg = 0;
};
```

許多人一開始接觸 `std::move()` 誤以為可以增進效能，因為可以減少copy constructor 的次數，但這其實不一定正確的!!!!!

例如

```cpp
BigObject test1(int i)
{
    auto dd = BigObject();
    if (i <= 0){
        dd.gg = 5;
        return dd;
    }
    dd.gg = i;
    return std::move(dd);
}
BigObject test2(int i)
{
    auto dd = BigObject();
    if (i <= 0){
        dd.gg = 5;
        return dd;
    }
    dd.gg = i;
    return dd;
}int main()
{
  auto tt1 = test1(5);
  auto tt2 = test2(5);  return 0;
}
```

output 則為

```
BigObject::BigObject()
BigObject::BigObject(BigObject&&)
BigObject::~BigObject()BigObject::BigObject()
BigObject::~BigObject()
BigObject::~BigObject()
```

很多人以為function return object 會多一個copy constructor 而使用 `std::move()` ，因為很多人以為overload 較低，但是很明顯看到 `test2` 卻比 `test1` 更有效率，因為沒有多餘的copy/move constructor， 因為compiler 會自動做 RVO(Return Value Optimization)， 所以切記

**function 裡面能使用RVO 就使用RVO 不要自作聰明使用** `**std::move**`

那麼到底什麼時候可以使用 `std::move` 讓程式加快呢?

可以參考以下例子

`std::array<T>` , `std::vector<T>` 基本上都可以支援random access 的container，但是 `std::move` 的實作卻差別很大

```cpp
int main()
{
  std::vector<BigObject> test;
  test.resize(2);
  auto m_test = std::move(test);
  for(auto &it : test)
    std::cout<<it.gg<<std::endl;
  for(auto &it : m_test)
    std::cout<<it.gg<<std::endl;}
```

output

```
BigObject::BigObject()
BigObject::BigObject()
0
0
BigObject::~BigObject()
BigObject::~BigObject()
```

可以看到 `std::vector` 對應的move constructor 可以不會做多餘的constructor ，且原本的element 都移到 `m_test` 之中。

output

```
BigObject::BigObject()
BigObject::BigObject()
BigObject::BigObject(BigObject&&)
BigObject::BigObject(BigObject&&)
0
0
0
0
BigObject::~BigObject()
BigObject::~BigObject()
BigObject::~BigObject()
BigObject::~BigObject()
```

但是 `std::array<T>` 對應的 move constructor 卻有很大的分別，基本上是會對每個element 都 call move constructor 而不是對container

所以在使用 `std::move()` 語法的時候，最好要知道到底程式會怎麼跑，不然往往會自成程式碼的失控…..

最後分享一下，減少copy/move constructor 次數的確可以增進程式效能，但通常都是 演算法 > 程式優化 ，所以往往演算法都是優化的第一步，但是如果在特定產業的話，對程式的速度非常在意，那優化 c++ 程式邏輯的確可以增進效能，因為現在產業的關係常常做這類似的優化，之前就有利用 universal reference 降低constructor 次數增進約10%的效能。

第一篇先以 `std::move()` 開頭，之後可能會多講一下 c++ optimization 的心得，順便紀錄工作用到的能力

---

C++ 11引進了move semantic。在C++03時，”temporaries” or ”rvalues”都被視為non-modifiable，但C++11允許了右值的改動，因為這會有些時候相當有用。更精準來說：

> 當右值被初始化之後，即可以被更改。其註記方式為 T&&, for a type of T

而move semantics要解決的問題是：**C++ 03中常常有不必要的copy，尤其在object pass by value的時候。**

而move semantics是為了提升這部分的效能。

舉個例子：

假設現在有個 std::vector<T> type（可以想像裡面有個 C-style array以及定義的size)。想像一個函數創造了這個vector並要將其回傳。按照C++03的方法則是宣告一個container來接收。如std::vector<T> ret = f()。此時函數內部創造的temporary內容會被完整複製一份放到ret，接著從記憶體中抹去所有temporary memory。這個過程很繁瑣，因為**複製與刪去**這兩個步驟是不必要的。

再仔細看move constructor的運作方式。今天一個std::vector<T>要透過rvalue形式的std::vector<T>來創建，則會發生以下步驟。

1. rvalue的vector中，C-style array pointer會被複製到destination vector<T>中。
2. 原本rvalue的C-array pointer會被指向null。
3. 因為rvalue是temporaries，接下來的context也不會再使用到，所以其null pointer也不會被access（所以不用擔心out of scope之後，嘗試去delete一個null pointer的memory）。

由此可見，這裡完全摒棄了deep copy的過程，但仍是safe的狀態。

除了move constructor的case，還有在function return 一個新的物件的時候（舉例: std::vector<T>），move semantics也可以避免多餘的deep copy。其原因是函數回傳一個新物件時，多了一步deep copy也是不必要的。在function return的這個case，temporary vector會自動被當作右值，move constructor會implicitly called。（在C++ 03中，如果沒有move constructor，則會自動呼叫copy constructor）

再來看一個stackoveflow的例子，幫助理解lvalue, rvalue以及move。

假設現在有個string class，同時也定義其copy constructor和destructor。

```cpp
class string
{
char* datapublic:
    string(const char* p)
    {
        size_t size = std::strlen(p) + 1;
        data = new char[size];
        std::memcpy(data, p, size);
    }

    ~string()
    {
        delete[] data;
    }
}

```

接著我們執行三種string的操作：

```cpp
string a(x);
string b(x + y);
string c(// a function returning string);
```

這裡只有第一行的操作會使用到deep copy。這裡x代表的就是string這個object。一個實際存在記憶體中，透過x去reference的物件。這我們稱為**lvalue**。

而第二與第三行都是在程式執行過程中產生的temporaries。我們沒辦法透過一個name去取得x + y或函數回傳的string object。這稱為**rvalue**。這些rvalues會在其存在的expression結束之後就被destroy。

而在接下來的部份我們要加入move constructor。我們可以透過rvalue reference &&偵測constructor的argument是否為rvalue。

因此我們定義：

```cpp
string(string&& rhs)
{
    data = rhs.data;
    rhs.data = nullptr;
}
```

在move constructor中，我們可以對記憶體進行任何操作。只要最後右值是在一個valid state就可以。在這裡我們將rhs.data改成nullptr是為了避免rhs呼叫了destructor，刪除了被移動的string。

以上很容易看出來，move constructor做的事情是透過改變pointer，把source (rhs)的記憶體內容搬移到string中。

最後來看看assignment operator。當assignment接收的是lvalue時，呼叫的就會是copy constructor，**若是rvalue，那就會是move constructor**。如：

```cpp
string c = a;
string c = a + b;
```

這裡move constructor做的事情只是更改了pointer指向的位置，而source object在之後也不可能被使用者操作，所以是個安全的操作。

---

# 一文讀懂C++右值引用和std::move

https://zhuanlan.zhihu.com/p/335994370?utm_id=0

C++11引入了右值引用，有一定的理解成本，工作中發現不少同事對右值引用理解不深，認為右值引用性能更高等等。本文從實用角度出發，用儘量通俗易懂的語言講清左右值引用的原理，性能分析及其應用場景，幫助大家在日常程式設計中用好右值引用和std::move。



### **1. 什麼是左值、右值**

首先不考慮引用以減少幹擾，可以從2個角度判斷：左值**可以取地址、位於等號左邊**；而右值**沒法取地址，位於等號右邊**。

```cpp
int a = 5;
```

- a可以通過 & 取地址，位於等號左邊，所以a是左值。
- 5位於等號右邊，5沒法通過 & 取地址，所以5是個右值。

再舉個例子：

```cpp
struct A {
    A(int a = 0) {
        a_ = a;
    }
 
    int a_;
};
 
A a = A();
```

- 同樣的，a可以通過 & 取地址，位於等號左邊，所以a是左值。
- A()是個臨時值，沒法通過 & 取地址，位於等號右邊，所以A()是個右值。

可見左右值的概念很清晰，有地址的變數就是左值，沒有地址的字面值、臨時值就是右值。

### **2. 什麼是左值引用、右值引用**

引用本質是別名，可以通過引用修改變數的值，傳參時傳引用可以避免複製，其實現原理和指針類似。 個人認為，引用出現的本意是為了降低C語言指針的使用難度，但現在指針+左右值引用共同存在，反而大大增加了學習和理解成本。

### **2.1 左值引用**

左值引用大家都很熟悉，**能指向左值，不能指向右值的就是左值引用**：

```cpp
int a = 5;
int &ref_a = a; // 左值引用指向左值，編譯通過
int &ref_a = 5; // 左值引用指向了右值，會編譯失敗
```

**引用是變數的別名，由於右值沒有地址，沒法被修改，所以左值引用無法指向右值。**

但是，const左值引用是可以指向右值的：

```cpp
const int &ref_a = 5;  // 編譯通過
```

const左值引用不會修改指向值，因此可以指向右值，這也是為什麼要使用`const &`作為函數參數的原因之一，如`std::vector`的`push_back`：

```cpp
void push_back (const value_type& val);
```

如果沒有`const`，`vec.push_back(5)`這樣的程式碼就無法編譯通過了。

### **2.2 右值引用**

再看下右值引用，右值引用的標誌是`&&`，顧名思義，右值引用專門為右值而生，**可以指向右值，不能指向左值**：

```cpp
int &&ref_a_right = 5; // ok
 
int a = 5;
int &&ref_a_left = a; // 編譯不過，右值引用不可以指向左值
 
ref_a_right = 6; // 右值引用的用途：可以修改右值
```

### **2.3 對左右值引用本質的討論**

下邊的論述比較複雜，也是本文的核心，對理解這些概念非常重要。

### **2.3.1 右值引用有辦法指向左值嗎？**

有辦法，`std::move`：

```cpp
int a = 5; // a是個左值
int &ref_a_left = a; // 左值引用指向左值
int &&ref_a_right = std::move(a); // 通過std::move將左值轉化為右值，可以被右值引用指向
 
cout << a; // 列印結果：5
```

在上邊的程式碼裡，看上去是左值a通過std::move移動到了右值ref_a_right中，那是不是a裡邊就沒有值了？並不是，列印出a的值仍然是5。

`std::move`是一個非常有迷惑性的函數，不理解左右值概念的人們往往以為它能把一個變數裡的內容移動到另一個變數，**但事實上std::move移動不了什麼，唯一的功能是把左值強制轉化為右值**，讓右值引用可以指向左值。其實現等同於一個類型轉換：`static_cast<T&&>(lvalue)`。 所以，**單純的std::move(xxx)不會有性能提升**，std::move的使用場景在第三章會講。

同樣的，右值引用能指向右值，本質上也是把右值提升為一個左值，並定義一個右值引用通過std::move指向該左值：

```cpp
int &&ref_a = 5;
ref_a = 6; 
 
等同於以下程式碼：
 
int temp = 5;
int &&ref_a = std::move(temp);
ref_a = 6;
```

### **2.3.2 左值引用、右值引用本身是左值還是右值？**

**被聲明出來的左、右值引用都是左值**。 因為被聲明出的左右值引用是有地址的，也位於等號左邊。仔細看下邊程式碼：

```cpp
// 形參是個右值引用
void change(int&& right_value) {
    right_value = 8;
}
 
int main() {
    int a = 5; // a是個左值
    int &ref_a_left = a; // ref_a_left是個左值引用
    int &&ref_a_right = std::move(a); // ref_a_right是個右值引用
 
    change(a); // 編譯不過，a是左值，change參數要求右值
    change(ref_a_left); // 編譯不過，左值引用ref_a_left本身也是個左值
    change(ref_a_right); // 編譯不過，右值引用ref_a_right本身也是個左值
     
    change(std::move(a)); // 編譯通過
    change(std::move(ref_a_right)); // 編譯通過
    change(std::move(ref_a_left)); // 編譯通過
 
    change(5); // 當然可以直接接右值，編譯通過
     
    cout << &a << ' ';
    cout << &ref_a_left << ' ';
    cout << &ref_a_right;
    // 列印這三個左值的地址，都是一樣的
}
```

看完後你可能有個問題，std::move會返回一個右值引用`int &&`，它是左值還是右值呢？ 從表示式`int &&ref = std::move(a)`來看，右值引用`ref`指向的必須是右值，所以move返回的`int &&`是個右值。所以右值引用既可能是左值，又可能是右值嗎？ 確實如此：**右值引用既可以是左值也可以是右值，如果有名稱則為左值，否則是右值**。

或者說：**作為函數返回值的 && 是右值，直接聲明出來的 && 是左值**。 這同樣也符闔第一章對左值，右值的判定方式：其實引用和普通變數是一樣的，`int &&ref = std::move(a)`和 `int a = 5`沒有什麼區別，等號左邊就是左值，右邊就是右值。

最後，從上述分析中我們得到如下結論：

1. **從性能上講，左右值引用沒有區別，傳參使用左右值引用都可以避免複製。**
2. **右值引用可以直接指向右值，也可以通過std::move指向左值；而左值引用只能指向左值(const左值引用也能指向右值)。**
3. **作為函數形參時，右值引用更靈活。雖然const左值引用也可以做到左右值都接受，但它無法修改，有一定侷限性。**

```cpp
void f(const int& n) {
    n += 1; // 編譯失敗，const左值引用不能修改指向變數
}

void f2(int && n) {
    n += 1; // ok
}

int main() {
    f(5);
    f2(5);
}
```

### **3. 右值引用和std::move的應用場景**

按上文分析，`std::move`只是類型轉換工具，不會對性能有好處；右值引用在作為函數形參時更具靈活性，看上去還是挺雞肋的。他們有什麼實際應用場景嗎？

### **3.1 實現移動語義**

在實際場景中，右值引用和std::move被廣泛用於在STL和自訂類中**實現移動語義，避免複製，從而提升程序性能**。 在沒有右值引用之前，一個簡單的陣列類通常實現如下，有`建構函式`、`複製建構函式`、`賦值運算子多載`、`解構函式`等。深複製/淺複製在此不做講解。

```cpp
class Array {
public:
    Array(int size) : size_(size) {
        data = new int[size_];
    }
     
    // 深複製構造
    Array(const Array& temp_array) {
        size_ = temp_array.size_;
        data_ = new int[size_];
        for (int i = 0; i < size_; i ++) {
            data_[i] = temp_array.data_[i];
        }
    }
     
    // 深複製賦值
    Array& operator=(const Array& temp_array) {
        delete[] data_;
 
        size_ = temp_array.size_;
        data_ = new int[size_];
        for (int i = 0; i < size_; i ++) {
            data_[i] = temp_array.data_[i];
        }
    }
 
    ~Array() {
        delete[] data_;
    }
 
public:
    int *data_;
    int size_;
};
```

該類的複製建構函式、賦值運算子多載函數已經通過使用左值引用傳參來避免一次多餘複製了，但是內部實現要深複製，無法避免。 這時，有人提出一個想法：是不是可以提供一個`移動建構函式`，把被複製者的資料移動過來，被複製者後邊就不要了，這樣就可以避免深複製了，如：

```cpp
class Array {
public:
    Array(int size) : size_(size) {
        data = new int[size_];
    }
     
    // 深複製構造
    Array(const Array& temp_array) {
        ...
    }
     
    // 深複製賦值
    Array& operator=(const Array& temp_array) {
        ...
    }
 
    // 移動建構函式，可以淺複製
    Array(const Array& temp_array, bool move) {
        data_ = temp_array.data_;
        size_ = temp_array.size_;
        // 為防止temp_array析構時delete data，提前置空其data_      
        temp_array.data_ = nullptr;
    }
     
 
    ~Array() {
        delete [] data_;
    }
 
public:
    int *data_;
    int size_;
};
```

這麼做有2個問題：

- 不優雅，表示移動語義還需要一個額外的參數(或者其他方式)。
- 無法實現！`temp_array`是個const左值引用，無法被修改，所以`temp_array.data_ = nullptr;`這行會編譯不過。當然函數參數可以改成非const：`Array(Array& temp_array, bool move){...}`，這樣也有問題，由於左值引用不能接右值，`Array a = Array(Array(), true);`這種呼叫方式就沒法用了。

可以發現左值引用真是用的很不爽，**右值引用的出現解決了這個問題**，在STL的很多容器中，都實現了以**右值引用為參數**的`移動建構函式`和`移動賦值多載函數`，或者其他函數，最常見的如std::vector的`push_back`和`emplace_back`。參數為左值引用意味著複製，為右值引用意味著移動。

```cpp
class Array {
public:
    ......
 
    // 優雅
    Array(Array&& temp_array) {
        data_ = temp_array.data_;
        size_ = temp_array.size_;
        // 為防止temp_array析構時delete data，提前置空其data_      
        temp_array.data_ = nullptr;
    }
     
 
public:
    int *data_;
    int size_;
};
```

如何使用：

```cpp
// 例1：Array用法
int main(){
    Array a;
 
    // 做一些操作
    .....
     
    // 左值a，用std::move轉化為右值
    Array b(std::move(a));
}
```

### **3.2 實例：vector::push_back使用std::move提高性能**

```cpp
// 例2：std::vector和std::string的實際例子
int main() {
    std::string str1 = "aacasxs";
    std::vector<std::string> vec;
     
    vec.push_back(str1); // 傳統方法，copy
    vec.push_back(std::move(str1)); // 呼叫移動語義的push_back方法，避免複製，str1會失去原有值，變成空字串
    vec.emplace_back(std::move(str1)); // emplace_back效果相同，str1會失去原有值
    vec.emplace_back("axcsddcas"); // 當然可以直接接右值
}
 
// std::vector方法定義
void push_back (const value_type& val);
void push_back (value_type&& val);
 
void emplace_back (Args&&... args);
```

在vector和string這個場景，加個`std::move`會呼叫到移動語義函數，避免了深複製。

除非設計不允許移動，STL類大都支援移動語義函數，即`可移動的`。 另外，編譯器會**默認**在使用者自訂的`class`和`struct`中生成移動語義函數，但前提是使用者沒有主動定義該類的`複製構造`等函數(具體規則自行百度哈)。 **因此，可移動對像在<需要複製且被複製者之後不再被需要>的場景，建議使用**`std::move`**觸發移動語義，提升性能。**

```cpp
moveable_objecta = moveable_objectb; 
改為： 
moveable_objecta = std::move(moveable_objectb);
```

還有些STL類是`move-only`的，比如`unique_ptr`，這種類只有移動建構函式，因此只能移動(轉移內部對像所有權，或者叫淺複製)，不能複製(深複製):

```cpp
std::unique_ptr<A> ptr_a = std::make_unique<A>();

std::unique_ptr<A> ptr_b = std::move(ptr_a); // unique_ptr只有‘移動賦值多載函數‘，參數是&& ，只能接右值，因此必須用std::move轉換類型

std::unique_ptr<A> ptr_b = ptr_a; // 編譯不通過
```

**std::move本身只做類型轉換，對性能無影響。** **我們可以在自己的類中實現移動語義，避免深複製，充分利用右值引用和std::move的語言特性。**

### **4. 完美轉發 std::forward**

和`std::move`一樣，它的兄弟`std::forward`也充滿了迷惑性，雖然名字含義是轉發，但他並不會做轉發，同樣也是做類型轉換.

與move相比，forward更強大，move只能轉出來右值，forward都可以。

> std::forward<T>(u)有兩個參數：T與 u。 a. 當T為左值引用類型時，u將被轉換為T類型的左值； b. 否則u將被轉換為T類型右值。

舉個例子，有main，A，B三個函數，呼叫關係為：`main->A->B`，建議先看懂*2.3節對左右值引用本身是左值還是右值的討論*再看這裡：

```cpp
void B(int&& ref_r) {
    ref_r = 1;
}
 
// A、B的入參是右值引用
// 有名字的右值引用是左值，因此ref_r是左值
void A(int&& ref_r) {
    B(ref_r);  // 錯誤，B的入參是右值引用，需要接右值，ref_r是左值，編譯失敗
     
    B(std::move(ref_r)); // ok，std::move把左值轉為右值，編譯通過
    B(std::forward<int>(ref_r));  // ok，std::forward的T是int類型，屬於條件b，因此會把ref_r轉為右值
}
 
int main() {
    int a = 5;
    A(std::move(a));
}
```

例2：

```cpp
void change2(int&& ref_r) {
    ref_r = 1;
}
 
void change3(int& ref_l) {
    ref_l = 1;
}
 
// change的入參是右值引用
// 有名字的右值引用是 左值，因此ref_r是左值
void change(int&& ref_r) {
    change2(ref_r);  // 錯誤，change2的入參是右值引用，需要接右值，ref_r是左值，編譯失敗
     
    change2(std::move(ref_r)); // ok，std::move把左值轉為右值，編譯通過
    change2(std::forward<int &&>(ref_r));  // ok，std::forward的T是右值引用類型(int &&)，符合條件b，因此u(ref_r)會被轉換為右值，編譯通過
     
    change3(ref_r); // ok，change3的入參是左值引用，需要接左值，ref_r是左值，編譯通過
    change3(std::forward<int &>(ref_r)); // ok，std::forward的T是左值引用類型(int &)，符合條件a，因此u(ref_r)會被轉換為左值，編譯通過
    // 可見，forward可以把值轉換為左值或者右值
}
 
int main() {
    int a = 5;
    change(std::move(a));
}
```

上邊的示例在日常程式設計中基本不會用到，`std::forward`最主要運於範本程式設計的參數轉發中，想深入瞭解需要學習`萬能引用(T &&)`和`引用摺疊(eg:& && → ?)`等知識，本文就不詳細介紹這些了。
