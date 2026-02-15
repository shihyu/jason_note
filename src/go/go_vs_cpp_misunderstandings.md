# Go vs C++ --- 常見誤解與核心差異整理

## 1️⃣ Go 沒有 class，只有 type

### C++

``` cpp
class Dog {
public:
    void Speak() { std::cout << "woof"; }
};
```

### Go

``` go
type Dog struct{}

func (d Dog) Speak() {
    fmt.Println("woof")
}
```

### 重點

-   Go 沒有 `class`
-   `type` 是在定義型別
-   method 是「掛在型別上」的 function
-   `(d Dog)` 不是參數宣告錯誤，而是 receiver（接收者）

白話：\
Go 是「先定義型別，再幫它加能力」，\
不是像 C++ 把所有東西包在 class 裡。

------------------------------------------------------------------------

## 2️⃣ method 其實就是特殊語法的 function

``` go
func (d Dog) Speak()
```

等價概念：

``` go
func Speak(d Dog)
```

差別只是呼叫方式：

    d.Speak()   // method
    Speak(d)    // function

白話：\
method 本質還是 function，只是語法糖。

------------------------------------------------------------------------

## 3️⃣ Interface 是「隱式實作」

### Go

``` go
type Speaker interface {
    Speak()
}

type Dog struct{}

func (Dog) Speak() {}
```

Dog 沒有寫：

    implements Speaker

但它自動符合。

### C++

``` cpp
class Dog : public Speaker
```

必須明確繼承。

白話：\
C++：你要報名參加俱樂部。\
Go：你會做這件事，就算會員。

------------------------------------------------------------------------

## 4️⃣ 實作者不需要知道 interface 存在

Go 設計哲學：

> Interface 屬於「使用者」，不是「實作者」。

例如：

``` go
func Process(s Speaker) {}
```

Dog 不需要依賴 Speaker。

這降低耦合。

C++ 則必須依賴抽象類別。

------------------------------------------------------------------------

## 5️⃣ 沒有繼承，只有組合

C++ 有 inheritance tree。

Go 沒有 extends / subclass。

只用： - struct 組合 - interface 抽象

白話：\
Go 故意不讓你設計很複雜的 class hierarchy。

------------------------------------------------------------------------

## 6️⃣ 沒有 constructor / destructor / RAII

C++： - 建構子 - 解構子 - RAII

Go： - 沒有 constructor 語法 - 沒有 destructor - 用 GC 管理記憶體

通常寫：

``` go
func NewDog() *Dog {
    return &Dog{}
}
```

------------------------------------------------------------------------

## 7️⃣ Error Handling 不用 Exception

C++：

``` cpp
try { } catch(...) {}
```

Go：

``` go
if err != nil {
    return err
}
```

Go 強制顯式處理錯誤。

------------------------------------------------------------------------

## 8️⃣ 沒有 function overloading / operator overloading

C++ 可以多載：

``` cpp
int add(int, int);
double add(double, double);
```

Go 不行。

必須改名或用 generics。

------------------------------------------------------------------------

## 9️⃣ 指標限制較多

C++： - 可以 pointer arithmetic - 可以 placement new - 可能 UB

Go： - 禁止 pointer arithmetic - 不允許未定義行為 - 更安全

------------------------------------------------------------------------

## 🔟 Concurrency 模型不同

C++： - thread - mutex - condition variable

Go：

``` go
go func() {}
ch := make(chan int)
```

Go 採 CSP 模型（channel 傳遞資料）。

白話：\
C++：共享記憶體 + 鎖\
Go：不要共享記憶體，用 channel 溝通

------------------------------------------------------------------------

# 🎯 核心哲學差異總結

  C++                        Go
  -------------------------- ----------------
  Powerful                   Simple
  Template metaprogramming   保守 generics
  Inheritance                Composition
  RAII                       GC
  顯式繼承                   隱式 interface
  高度彈性                   刻意限制複雜度

------------------------------------------------------------------------

# 最重要的轉換心法

從 C++ 轉 Go 要改的是「設計思維」，不是語法。

❌ 不要設計複雜 class hierarchy\
✅ 小 interface + 組合\
✅ 明確 error handling\
✅ 保持簡單

------------------------------------------------------------------------

*整理給 C++ 背景工程師學 Go 使用*
