## <h1 id="cpp_14">C++14新特性</h1>

![C++14思維導圖](https://www.0voice.com/uiwebsite/cpp_new_features/C++14_new_features.png)
-----------

<h4 id="cpp_14_01">函式回傳值型別推導</h4>

C++14對函式返回型別推導規則做了最佳化，先看一段程式碼：

```CPP
#include <iostream>

using namespace std;

auto func(int i) {
    return i;
}

int main() {
    cout << func(4) << endl;
    return 0;
}
```
使用C++11編譯：
```CPP
~/test$ g++ test.cc -std=c++11
test.cc:5:16: error: ‘func’ function uses ‘auto’ type specifier without trailing return type
 auto func(int i) {
                ^
test.cc:5:16: note: deduced return type only available with -std=c++14 or -std=gnu++14
```
上面的程式碼使用C++11是不能通過編譯的，通過編譯器輸出的資訊也可以看見這個特性需要到C++14才被支援。

回傳值型別推導也可以用在樣板中：

```CPP
#include <iostream>
using namespace std;

template<typename T> auto func(T t) { return t; }

int main() {
    cout << func(4) << endl;
    cout << func(3.4) << endl;
    return 0;
}
```

注意：

）函式內如果有多個return語句，它們必須返回相同的型別，否則編譯失敗。

```CPP
auto func(bool flag) {
    if (flag) return 1;
    else return 2.3; // error
}
// inconsistent deduction for auto return type: ‘int’ and then ‘double’
```

）如果return語句返回初始化列表，回傳值型別推導也會失敗

```CPP
auto func() {
    return {1, 2, 3}; // error returning initializer list
}
```

) 如果函式是虛擬函式，不能使用回傳值型別推導
```CPP
struct A {
	// error: virtual function cannot have deduced return type
	virtual auto func() { return 1; } 
}
```

） 返回型別推導可以用在前向聲明中，但是在使用它們之前，翻譯單元中必須能夠得到函式定義
```CPP
auto f();               // declared, not yet defined
auto f() { return 42; } // defined, return type is int

int main() {
	cout << f() << endl;
}
```

）返回型別推導可以用在遞歸函式中，但是遞歸調用必須以至少一個返回語句作為先導，以便編譯器推導出返回型別。
```CPP
auto sum(int i) {
    if (i == 1)
        return i;              // return int
    else
        return sum(i - 1) + i; // ok
}
```

<br/>
<br/>

<h4 id="cpp_14_02">lambda參數auto</h4>

在C++11中，lambda表達式參數需要使用具體的型別聲明：

```CPP
auto f = [] (int a) { return a; }
```

在C++14中，對此進行最佳化，lambda表達式參數可以直接是auto：

```CPP
auto f = [] (auto a) { return a; };
cout << f(1) << endl;
cout << f(2.3f) << endl;
```

<br/>
<br/>

<h4 id="cpp_14_03">變數樣板</h4>

C++14支援變數樣板：

```CPP
template<class T>
constexpr T pi = T(3.1415926535897932385L);

int main() {
    cout << pi<int> << endl; // 3
    cout << pi<double> << endl; // 3.14159
    return 0;
}
```

<br/>
<br/>

<h4 id="cpp_14_04">別名樣板</h4>

C++14也支援別名樣板：

```CPP
template<typename T, typename U>
struct A {
    T t;
    U u;
};

template<typename T>
using B = A<T, int>;

int main() {
    B<double> b;
    b.t = 10;
    b.u = 20;
    cout << b.t << endl;
    cout << b.u << endl;
    return 0;
}
```

<br/>
<br/>

<h4 id="cpp_14_05">constexpr的限制</h4>

C++14相較於C++11對constexpr減少了一些限制：

）C++11中constexpr函式可以使用遞歸，在C++14中可以使用局部變數和迴圈

```CPP
constexpr int factorial(int n) { // C++14 和 C++11均可
    return n <= 1 ? 1 : (n * factorial(n - 1));
}
```

在C++14中可以這樣做：
```CPP
constexpr int factorial(int n) { // C++11中不可，C++14中可以
    int ret = 0;
    for (int i = 0; i < n; ++i) {
        ret += i;
    }
    return ret;
}
```

）C++11中constexpr函式必須必須把所有東西都放在一個單獨的return語句中，而constexpr則無此限制：
```CPP
constexpr int func(bool flag) { // C++14 和 C++11均可
    return 0;
}
```

在C++14中可以這樣：
```CPP
constexpr int func(bool flag) { // C++11中不可，C++14中可以
    if (flag) return 1;
    else return 0;
}
```

<br/>
<br/>

<h4 id="cpp_14_06">[[deprecated]]標記</h4>

C++14中增加了deprecated標記，修飾類、變、函式等，當程式中使用到了被其修飾的程式碼時，編譯時被產生警告，用戶提示開發者該標記修飾的內容將來可能會被丟棄，儘量不要使用。

```CPP
struct [[deprecated]] A { };

int main() {
    A a;
    return 0;
}
```

當編譯時，會出現如下警告：
```CPP
~/test$ g++ test.cc -std=c++14
test.cc: In function ‘int main()’:
test.cc:11:7: warning: ‘A’ is deprecated [-Wdeprecated-declarations]
     A a;
       ^
test.cc:6:23: note: declared here
 struct [[deprecated]] A {
 ```
 
<br/>
<br/>

<h4 id="cpp_14_07">二進制字面量與整形字面量分隔符</h4>

C++14引入了二進制字面量，也引入了分隔符，防止看起來眼花哈~
```CPP
int a = 0b0001'0011'1010;
double b = 3.14'1234'1234'1234;
```

<br/>
<br/>

<h4 id="cpp_14_08">std::make_unique</h4>

C++11中有std::make_shared，卻沒有std::make_unique，在C++14已經改善。

```CPP
struct A {};
std::unique_ptr<A> ptr = std::make_unique<A>();
```

<br/>
<br/>

<h4 id="cpp_14_08">std::shared_timed_mutex與std::shared_lock</h4>

C++14通過std::shared_timed_mutex和std::shared_lock來實現讀寫鎖，保證多個執行緒可以同時讀，但是寫執行緒必須獨立運行，寫操作不可以同時和讀操作一起進行。

實現方式如下：

```CPP
struct ThreadSafe {
    mutable std::shared_timed_mutex mutex_;
    int value_;

    ThreadSafe() {
        value_ = 0;
    }

    int get() const {
        std::shared_lock<std::shared_timed_mutex> loc(mutex_);
        return value_;
    }

    void increase() {
        std::unique_lock<std::shared_timed_mutex> lock(mutex_);
        value_ += 1;
    }
};
```

<br/>
<br/>

<h4 id="cpp_14_09">std::integer_sequence</h4>
```CPP
template<typename T, T... ints>
void print_sequence(std::integer_sequence<T, ints...> int_seq)
{
    std::cout << "The sequence of size " << int_seq.size() << ": ";
    ((std::cout << ints << ' '), ...);
    std::cout << '\n';
}

int main() {
    print_sequence(std::integer_sequence<int, 9, 2, 5, 1, 9, 1, 6>{});
    return 0;
}
```

輸出：

```CPP
7 9 2 5 1 9 1 6
```

std::integer_sequence和std::tuple的配合使用：

```CPP
template <std::size_t... Is, typename F, typename T>
auto map_filter_tuple(F f, T& t) {
    return std::make_tuple(f(std::get<Is>(t))...);
}

template <std::size_t... Is, typename F, typename T>
auto map_filter_tuple(std::index_sequence<Is...>, F f, T& t) {
    return std::make_tuple(f(std::get<Is>(t))...);
}

template <typename S, typename F, typename T>
auto map_filter_tuple(F&& f, T& t) {
    return map_filter_tuple(S{}, std::forward<F>(f), t);
}
```

<br/>
<br/>

<h4 id="cpp_14_10">std::exchange</h4>

直接看程式碼吧：

```CPP
int main() {
    std::vector<int> v;
    std::exchange(v, {1,2,3,4});
    cout << v.size() << endl;
    for (int a : v) {
        cout << a << " ";
    }
    return 0;
}
```
看樣子貌似和std::swap作用相同，那它倆有什麼區別呢？

可以看下exchange的實現：

```CPP
template<class T, class U = T>
constexpr T exchange(T& obj, U&& new_value) {
    T old_value = std::move(obj);
    obj = std::forward<U>(new_value);
    return old_value;
}
```

可以看見new_value的值給了obj，而沒有對new_value賦值！

<br/>
<br/>

<h4 id="cpp_14_11">std::quoted</h4>

C++14引入std::quoted用於給字串添加雙引號，直接看程式碼：

```CPP
int main() {
    string str = "hello world";
    cout << str << endl;
    cout << std::quoted(str) << endl;
    return 0;
}
```

編譯&輸出：

```CPP
~/test$ g++ test.cc -std=c++14
~/test$ ./a.out
hello world
"hello world"
```




