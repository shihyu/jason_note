

## GoLang - 物件導向

在這幾篇，會以 Go 語言的入門基礎進行逐步說明，本篇針對物件導向進行說明

在 Go 語言沒有像其他語言一樣有明確定義物件導向(Class, object, instance…) 封裝層，並且沒有 this, self 這種可以代表物件本身的屬性，以及沒有靜態屬性 (那麼本篇結束？)

當然，答案其實是不盡然，在 Go 雖然沒有其他語言有明確定義物件導向，但其實一樣也可實作出物件導向結構。

由於在實作方式會和其他語言有所不同，這部分會讓多數人搞混，就連官方看待 “Go是否為物件導向語言?” 問題，他們回答的是 “yes and no”，以含糊的方式回答。因此，當你進入 Go 的領域時，請放下過去 OO 包袱，重新在這裡學習 Go 語言的物件導向結構。

### struct:

在開始說明 struct 在實作物件導向的用法前，先說明他的基本結構，基本上在宣告一個 struct 時，可以同時宣告他的屬性，例如:

> struct 命名，若字首大寫則為 public 權限，如果小寫則只在自己的 package 內可以訪問。

```go
type User struct{
	name string
	age int
	phone int
}
```

例如：

```go
type User struct {
  name  string
  age   int
  phone string
}

func main() {

  var user1 User
  user1.name = "Adam"
  user1.age = 10
  user1.phone = "0912345678"

  fmt.Println(user1)
}
//output {Adam 10 0912345678}
```

另外，也可直接宣告 struct 預設值

```go
type User struct {
  name  string
  age   int
  phone string
}

func main() {

  user1 := User{"Adam", 10, "0912345678"}

  fmt.Println(user1)
}
//output {Adam 10 0912345678}
```

這裡不詳細說明 struct 的各種用法，後續再針對這部份進行介紹，接著來說明如何在 method 如何來結合 struct與func做出物件導向。

### method:

struct 的結構可以在 Go 語言中實作 Class 以及可定義屬性，而 函數 則可實作方法。並且 func 會各自獨立存在。

而 method 可以將 struct 與 func 建立關聯，他的基本結構為：

```go
func (receiverParam ReceiverType) funcName(param paramType) (resultsType) {

}
```

在下方示範一個例子， user 表示為一般用戶，member 表示為付費會員，在這裡透過 methods 各別定義出兩者的 struct與 func，

func 可以看到，帶入的參數會指定是什麼 struct。

在這裡例子，兩個 methods 名稱都一樣 (都叫 data()) ，但是會依照收的 struct 不同來做區分：

```go
type User struct {
  name  string
  age   int
  phone string
}

func (tg User) data() string {
  return "this is user:" + tg.name
}

type Member struct {
  name    string
  balance int
  age     int
  phone   string
}

func (tg Member) data() string {
  return "this is member:" + tg.name
}

func main() {

  user1 := User{"Adam", 10, "0912345678"}
  member1 := Member{"Brown", 11, 233, "0912345679"}

  fmt.Println(user1.data()) //output this is user:Adam
  fmt.Println(member1.data()) //output this is member:Brown

}
```

當然，這裡透過一個簡單的例子說明，希望對於學習 Go 語言的物件導向應用能有所幫助。在 Go 語言可以做出非常簡單優雅的物件導向架構。更進階的，可以透過 struct 匿名欄位來做出更多元的應用。最後，雖然沒有像其他程式語言，預設就攜帶著豐富的物件導向結構，但是在實際開發需求中，還是可以透過這樣的功能堆疊，進行開發。

## 建立類別 (Class) 和物件 (Object)

傳統的程序式程式設計 (procedural programming) 或是指令式程式設計 (imperative programming) 學到函式大概就算學完基本概念。

不過，近年來，物件導向程式設計 (object-oriented programming) 是程式設計主流的模式 (paradigm)，即使 C 這種非物件導向的語言，我們也會用結構和函式模擬物件的特性。本文將介紹如何在 Go 撰寫物件導向程式。

### 五分鐘的物件導向概論

由於物件導向是程式設計主流的模式 (paradigm)，很多語言都直接在語法機制中支援物件導向，然而，每個語言支援的物件導向特性略有不同，像 C++ 的物件系統相當完整，而 Perl 的原生物件系統則相對原始。物件導向在理論上是和語言無關的，但在實務上卻受到不同語言特性 (features) 的影響。學習物件導向時，除了學習在某個特定語言下的實作方式外，更應該學習其抽象層次的思維，有時候，暫時放下實作細節，從更高的視角看物件及物件間訊息的流動，對於學習物件導向有相當的幫助。

物件導向是一種將程式碼以更高的層次組織起來的方法。大部分的物件導向以類別 (class) 為基礎，透過類別可產生實際的物件 (object) 或實體 (instance) ，類別和物件就像是餅乾模子和餅乾的關係，透過同一個模子可以產生很多片餅乾。物件擁有屬性 (field) 和方法 (method)，屬性是其內在狀態，而方法是其外在行為。透過物件，狀態和方法是連動的，比起傳統的程序式程式設計，更容易組織程式碼。

許多物件導向語言支援封裝 (encapsulation)，透過封裝，程式設計者可以決定物件的那些部分要對外公開，那些部分僅由內部使用，封裝不僅限於靜態的資料，決定物件應該對外公開的行為也是封裝。當多個物件間互動時，封裝可使得程式碼容易維護，反之，過度暴露物件的內在屬性和細部行為會使得程式碼相互糾結，難以除錯。

物件間可以透過組合 (composition) 再利用程式碼。物件的屬性不一定要是基本型別，也可以是其他物件。組合是透過有… (has-a) 關係建立物件間的關連。例如，汽車物件有引擎物件，而引擎物件本身又有許多的狀態和行為。繼承 (inheritance) 是另一個再利用程式碼的方式，透過繼承，子類別 (child class) 可以再利用父類別 (parent class) 的狀態和行為。繼承是透過是… (is-a) 關係建立物件間的關連。例如，研究生物件是學生物件的特例。然而，過度濫用繼承，容易使程式碼間高度相依，造成程式難以維護。可參考組合勝過繼承 (composition over inheritance) 這個指導原則來設計自己的專案。

透過多型 (polymorphism) 使用物件，不需要在意物件的實作，只需依照其公開介面使用即可。例如，我們想要開車，不論駕駛 Honda 汽車或是 Ford 汽車，由於汽車的儀錶板都大同小異，都可以執行開車這項行為，而不需在意不同廠牌的汽車的內部差異。多型有許多種形式，如：

- 特定多態 (ad hoc polymorphism)：
  - 函數重載 (functional overloading)：同名而不同參數型別的方法 (method)
  - 運算子重載 (operator overloading) ： 對不同型別的物件使用相同運算子 (operator)
- 泛型 (generics)：對不同型別使用相同實作
- 子類型 (Subtyping)：不同子類別共享相同的公開介面，不同語言有不同的繼承機制

以物件導向實作程式，需要從宏觀的角度來思考，不僅要設計單一物件的公開行為，還有物件間如何互動，以達到良好且易於維護的程式碼結構。除了閱讀本教程或其他程式設計的書籍以學習如何實作物件外，可閱讀關於 物件導向分析及設計 (object-oriented analysis and design) 或是設計模式 (design pattern) 的書籍，以增進對物件導向的瞭解。

**[Update on 2018/05/20]** 嚴格來說，Go 只能撰寫基於物件的程式 (object-based programming)，無法撰寫物件導向程式 (object-oriented programming)，因為 Go 僅支援一部分的物件導向特性，像是 Go 不支援繼承。

由於 Go 的設計思維，以 Go 實作基於物件的程式時，會和 Java 或 Python 等相對傳統的物件系統略有不同，本文會在相關處提及相同及相異處，供讀者參考。

## 建立物件 (Object)

以下範例程式碼建立簡單的 Point 類別和物件：

```go
package main                                  /*  1 */

import (                                      /*  2 */
        "log"                                 /*  3 */
)                                             /*  4 */

// `X` and `Y` are public fields.             /*  5 */
type Point struct {                           /*  6 */
        X float64                             /*  7 */
        Y float64                             /*  8 */
}                                             /*  9 */

// Use an ordinary function as constructor    /* 10 */
func NewPoint(x float64, y float64) *Point {  /* 11 */
        p := new(Point)                       /* 12 */

        p.X = x                               /* 13 */
        p.Y = y                               /* 14 */

        return p                              /* 15 */
}                                             /* 16 */

func main() {                                 /* 17 */
        p := NewPoint(3, 4)                   /* 18 */

        if !(p.X == 3.0) {                    /* 19 */
                log.Fatal("Wrong value")      /* 20 */
        }                                     /* 21 */

        if !(p.Y == 4.0) {                    /* 22 */
                log.Fatal("Wrong value")      /* 23 */
        }                                     /* 24 */
}                                             /* 25 */
```

第 6 行至第 9 行的部分是形態宣告。Golang 沿用結構體為類別的型態，而沒有用新的保留字。

第 11 行至第 16 行的部分是建構函式。在一些程式語言中，會有為了建立物件使用特定的建構子 (constructor)，而 Golang 沒有引入額外的新語法，直接以一般的函式充當建構函式來建立物件即可。

第 17 行至第 25 行為外部程式。在我們的 Point 物件 `p` 中，我們直接存取 `p` 的屬性 `X` 和 `Y`，這在物件導向上不是好的習慣，因為我們無法控管屬性，物件可能會產生預期外的行為，比較好的方法，是將屬性隱藏在物件內部，由公開方法去存取。我們在後文中會討論。

## 類別宣告不限定於結構體

雖然大部分的 Golang 類別都使用結構體，但其實 Golang 類別內部可用其他的型別，如下例：

```go
type Vector []float64                     /*  1 */

func NewVector(args ...float64) Vector {  /*  2 */
        return args                       /*  3 */
}                                         /*  4 */

func WithSize(s int) Vector {             /*  5 */
        v := make([]float64, s)           /*  6 */

        return v                          /*  7 */
}                                         /*  8 */
```

在第 1 行中，我們宣告 `Vector` 型態，該型態內部不是使用結構體，而是使用陣列。

我們在第 2 行至第 4 行間及第 5 行至第 8 間宣告了兩個建構函式。由此例可知，Go 不限定建構函式的數量，我們可以視需求使用多個不同的建構函式。

## 撰寫方法 (Method)

在物件導向程式中，我們很少直接操作屬性 (field)，通常會將屬性私有化，再加入相對應的公開方法 (method)。我們將先前的 Point 物件改寫如下：

```go
package main                                  /*  1 */

import (                                      /*  2 */
        "log"                                 /*  3 */
)                                             /*  4 */

// `x` and `y` are private fields.            /*  5 */
type Point struct {                           /*  6 */
        x float64                             /*  7 */
        y float64                             /*  8 */
}                                             /*  9 */

func NewPoint(x float64, y float64) *Point {  /* 10 */
        p := new(Point)                       /* 11 */

        p.SetX(x)                             /* 12 */
        p.SetY(y)                             /* 13 */

        return p                              /* 14 */
}                                             /* 15 */

// The getter of x                            /* 16 */
func (p *Point) X() float64 {                 /* 17 */
        return p.x                            /* 18 */
}                                             /* 19 */

// The getter of y                            /* 20 */
func (p *Point) Y() float64 {                 /* 21 */
        return p.y                            /* 22 */
}                                             /* 23 */

// The setter of x                            /* 24 */
func (p *Point) SetX(x float64) {             /* 25 */
        p.x = x                               /* 26 */
}                                             /* 27 */

// The setter of y                            /* 28 */
func (p *Point) SetY(y float64) {             /* 29 */
        p.y = y                               /* 30 */
}                                             /* 31 */

func main() {                                 /* 32 */
        p := NewPoint(0, 0)                   /* 33 */

        if !(p.X() == 0) {                    /* 34 */
                log.Fatal("Wrong value")      /* 35 */
        }                                     /* 36 */

        if !(p.Y() == 0) {                    /* 37 */
                log.Fatal("Wrong value")      /* 38 */
        }                                     /* 39 */

        p.SetX(3)                             /* 40 */
        p.SetY(4)                             /* 41 */

        if !(p.X() == 3.0) {                  /* 42 */
                log.Fatal("Wrong value")      /* 43 */
        }                                     /* 44 */

        if !(p.Y() == 4.0) {                  /* 45 */
                log.Fatal("Wrong value")      /* 46 */
        }                                     /* 47 */
}                                             /* 48 */
```

第 6 行至第 9 行是類別宣告的部分。在這個版本的宣告中，我們將 `x` 和 `y` 改為小寫，代表該屬性是私有屬性，其可視度僅限於同一 package 中。

第 10 行至第 15 行是 `Point` 類別的建構函式。請注意我們刻意在第 12 行及第 13 行用該類別的 setters 來初始化屬性，這是刻意的動作。因為我們要確保在設置屬性時的行為保持一致。

第 16 行至第 31 行是 `Point` 類別的 getters 和 setters。所謂的 getters 和 setters 是用來存取內部屬性的 method。比起直接暴露屬性，使用 getters 和 setters 會有比較好的控制權。日後要修改 getters 或 setters 的實作時，也只要修改同一個地方即可。

在本例中，getters 和 setters 都是公開 method。但 getters 或 setters 不一定必為公開 method。例如，我們想做唯讀的 `Point` 物件時，就可以把 setters 的部分設為私有 method，留給類別內部使用。

在 Go 語言中，沒有 `this` 或 `self` 這種代表物件的關鍵字，而是由程式設計者自訂代表物件的變數，在本例中，我們用 `p` 表示物件本身。透過這種帶有物件的函式宣告後，函式會和物件連動；在物件導向中，將這種和物件連動的函式稱為方法 (method)。

雖然在這個例子中，暫時無法直接看出使用方法的好處，比起直接操作屬性，透過私有屬性搭配公開方法帶來許多的益處。例如，如果我們希望 Point 在建立之後是唯讀的，我們只要將 `SetX` 和 `SetY` 改為私有方法即可。或者，我們希望限定 Point 所在的範圍為 0.0 至 1000.0，我們可以在 `SetX` 和 `SetY` 中檢查參數是否符合我們的要求。

## 靜態方法 (Static Method)

有些讀者學過 Java 或 C#，可能有聽過過靜態方法 (static method)。這是因為 Java 和 C# 直接將物件導向的概念融入其語法中，然而，為了要讓某些方法在不建立物件時即可使用，所使用的一種補償性的語法機制。由於 Go 語言沒有將物件導向的概念直接加在語法中，不需要用這種語法，直接用頂層函式即可。

例如：我們撰寫一個計算兩點間長度的函式：

```go
package main                                   /*  1 */

import (                                       /*  2 */
        "log"                                  /*  3 */
        "math"                                 /*  4 */
)                                              /*  5 */

type Point struct {                            /*  6 */
        x float64                              /*  7 */
        y float64                              /*  8 */
}                                              /*  9 */

func NewPoint(x float64, y float64) *Point {   /* 10 */
        p := new(Point)                        /* 11 */

        p.SetX(x)                              /* 12 */
        p.SetY(y)                              /* 13 */

        return p                               /* 14 */
}                                              /* 15 */

func (p *Point) X() float64 {                  /* 16 */
        return p.x                             /* 17 */
}                                              /* 18 */

func (p *Point) Y() float64 {                  /* 19 */
        return p.y                             /* 20 */
}                                              /* 21 */

func (p *Point) SetX(x float64) {              /* 22 */
        p.x = x                                /* 23 */
}                                              /* 24 */

func (p *Point) SetY(y float64) {              /* 25 */
        p.y = y                                /* 26 */
}                                              /* 27 */

// Use an ordinary function as static method.  /* 28 */
func Dist(p1 *Point, p2 *Point) float64 {      /* 29 */
        xSqr := math.Pow(p1.X()-p2.X(), 2)     /* 30 */
        ySqr := math.Pow(p1.Y()-p2.Y(), 2)     /* 31 */

        return math.Sqrt(xSqr + ySqr)          /* 32 */
}                                              /* 33 */

func main() {                                  /* 34 */
        p1 := NewPoint(0, 0)                   /* 35 */
        p2 := NewPoint(3.0, 4.0)               /* 36 */

        if !(Dist(p1, p2) == 5.0) {            /* 37 */
                log.Fatal("Wrong value")       /* 38 */
        }                                      /* 39 */
}                                              /* 40 */
```

本範例和前一節的範例大同小異。主要的差別在於第 29 行至第 33 間多了一個用來計算距離的函式。該函式不綁定特定的物件，相當於 Java 的靜態函式。

因為 Golang 不是 Java 這種純物件導向語言，而是混合命令式和物件式兩種語法，所以不需要使用特定的語法來實踐靜態函式，使用一般的函式即可。

或許有讀者會擔心，使用過多的頂層函式會造成全域空間的汙染和衝突；實際上不需擔心，雖然我們目前將物件和主程式寫在一起，實務上，物件會寫在獨立的package 中，藉由 package 即可大幅減低命名空間衝突的議題。

## 使用嵌入 (Embedding) 取代繼承 (Inheritance)

繼承 (inheritance) 是一種重用程式碼的方式，透過從父類別 (parent class) 繼承程式碼，子類別 (child class) 可以少寫一些程式碼。此外，對於靜態型別語言來說，繼承也是實現多型 (polymorphism) 的方式。然而，Go 語言卻刻意地拿掉繼承，這是出自於其他語言的經驗。

繼承雖然好用，但也引起許多的問題。像是 C++ 相對自由，可以直接使用多重繼承，但這項特性會引來菱型繼承 (diamond inheritance) 的議題，Java 和 C# 刻意把這個機制去掉，改以介面 (interface) 進行有限制的多重繼承。從過往經驗可知過度地使用繼承，會增加程式碼的複雜度，使得專案難以維護。出自於工程上的考量，Go 捨去繼承這個語法特性。

為了補償沒有繼承的缺失，Go 加入了嵌入 (embedding) 這個新的語法特性，透過嵌入，也可以達到程式碼共享的功能。

例如，我們擴展 Point 類別至三維空間：

```go
package main                                                 /*  1 */

import (                                                     /*  2 */
        "log"                                                /*  3 */
)                                                            /*  4 */

type Point struct {                                          /*  5 */
        x float64                                            /*  6 */
        y float64                                            /*  7 */
}                                                            /*  8 */

func NewPoint(x float64, y float64) *Point {                 /*  9 */
        p := new(Point)                                      /* 10 */

        p.SetX(x)                                            /* 11 */
        p.SetY(y)                                            /* 12 */

        return p                                             /* 13 */
}                                                            /* 14 */

func (p *Point) X() float64 {                                /* 15 */
        return p.x                                           /* 16 */
}                                                            /* 17 */

func (p *Point) Y() float64 {                                /* 18 */
        return p.y                                           /* 19 */
}                                                            /* 20 */

func (p *Point) SetX(x float64) {                            /* 21 */
        p.x = x                                              /* 22 */
}                                                            /* 23 */

func (p *Point) SetY(y float64) {                            /* 24 */
        p.y = y                                              /* 25 */
}                                                            /* 26 */

type Point3D struct {                                        /* 27 */
        // Point is embedded                                 /* 28 */
        Point                                                /* 29 */
        z float64                                            /* 30 */
}                                                            /* 31 */

func NewPoint3D(x float64, y float64, z float64) *Point3D {  /* 32 */
        p := new(Point3D)                                    /* 33 */

        p.SetX(x)                                            /* 34 */
        p.SetY(y)                                            /* 35 */
        p.SetZ(z)                                            /* 36 */

        return p                                             /* 37 */
}                                                            /* 38 */

func (p *Point3D) Z() float64 {                              /* 39 */
        return p.z                                           /* 40 */
}                                                            /* 41 */

func (p *Point3D) SetZ(z float64) {                          /* 42 */
        p.z = z                                              /* 43 */
}                                                            /* 44 */

func main() {                                                /* 45 */
        p := NewPoint3D(1, 2, 3)                             /* 46 */

        // GetX method is from Point                         /* 47 */
        if !(p.X() == 1) {                                   /* 48 */
                log.Fatal("Wrong value")                     /* 49 */
        }                                                    /* 50 */

        // GetY method is from Point                         /* 51 */
        if !(p.Y() == 2) {                                   /* 52 */
                log.Fatal("Wrong value")                     /* 53 */
        }                                                    /* 54 */

        // GetZ method is from Point3D                       /* 55 */
        if !(p.Z() == 3) {                                   /* 56 */
                log.Fatal("Wrong value")                     /* 57 */
        }                                                    /* 58 */
}                                                            /* 59 */
```

第 5 行至第 26 行是原本的 `Point` 類別，這和先前的實作是雷同的，不多做說明。

第 27 行至第 44 行是 `Point3D` 類別，我們來看一下這個類別。

第 27 行至第 31 行是 `Point3D` 的類別宣告。請注意我們在第 29 行嵌入了 `Point` 類別。

第 32 行至第 38 行是 `Point3d` 的建構函式。雖然我們沒有為 `Point3D` 宣告 `SetX()` 及 `SetY()` method，但我們有嵌入 `Point` 類別，所以我們在第 34 行及第 35 行可以直接使用這些 method。

第 45 行至第 59 行是外部程式的部分。由於我們的 `Point3D` 內嵌了 `Point`，雖然 `Point3D` 沒有自己實作 `X()` 和 `Y()` method，我們在第 48 行及第 52 行可直接呼叫這些 method。

在本例中，我們重用了 `Point` 的方法，再加入 `Point3D` 特有的方法。實際上的效果等同於繼承。

然而，`Point` 和 `Point3D` 兩者在類別關係上卻是不相干的獨立物件。在以下例子中，我們想將 `Point3D` 加入 `Point` 物件組成的切片，而引發程式的錯誤：

```go
// Declare Point and Point3D as above.
 
func main() {
    points := make([]*Point, 0)
 
    p1 := NewPoint(3, 4)
    p2 := NewPoint3D(1, 2, 3)
 
    // Error!
    points = append(points, p1, p2)
}
```

在 Go 語言中，需要使用介面 (interface) 來解決這個議題，這就是我們下一篇文章所要探討的主題。

## 嵌入指標

除了嵌入其他結構外，結構也可以嵌入指標。我們將上例改寫如下：

```go
package main
 
import (
    "log"
)
 
type Point struct {
    x float64
    y float64
}
 
func NewPoint(x float64, y float64) *Point {
    p := new(Point)
 
    p.SetX(x)
    p.SetY(y)
 
    return p
}
 
func (p *Point) X() float64 {
    return p.x
}
 
func (p *Point) Y() float64 {
    return p.y
}
 
func (p *Point) SetX(x float64) {
    p.x = x
}
 
func (p *Point) SetY(y float64) {
    p.y = y
}
 
type Point3D struct {
    // Point is embedded as a pointer
    *Point
    z float64
}
 
func NewPoint3D(x float64, y float64, z float64) *Point3D {
    p := new(Point3D)
 
    // Forward promotion
    p.Point = NewPoint(x, y)
 
    // Forward promotion
    p.Point.SetX(x)
    p.Point.SetY(y)
 
    p.SetZ(z)
 
    return p
}
 
func (p *Point3D) Z() float64 {
    return p.z
}
 
func (p *Point3D) SetZ(z float64) {
    p.z = z
}
 
func main() {
    p := NewPoint3D(1, 2, 3)
 
    // GetX method is from Point
    if !(p.X() == 1) {
        log.Fatal("Wrong value")
    }
 
    // GetY method is from Point
    if !(p.Y() == 2) {
        log.Fatal("Wrong value")
    }
 
    // GetZ method is from Point3D
    if !(p.Z() == 3) {
        log.Fatal("Wrong value")
    }
}
```

同樣地，仍然不能透過嵌入指楆讓型別直接互通，而需要透過介面 (interface)。

## 結語

在本文中，我們介紹了 Golang 的物件系統。相較於 C++ 或 Java 或 C#，Golang 的物件系統相對比較輕量，儘量不使用新的保留字，而用現用的語法來實現物件的特性。

Golang 的物件系統刻意拿掉繼承，改用嵌入來重用程式碼，這是由先前的程式語言中學習到的經驗和教訓。但嵌入無法實踐子類別 (subtyping)，這個問題要等到我們下一篇講到的介面 (interface) 才有解。

---



沒有 object、沒有 class 、沒有繼承的 Go，
靠著 struct / method / interface，
好像也享有 OOP 語言的優點呢

## method

本來以為 Go 是物件導向，後來發現**沒有 class**！
基本上使用 struct 與 method 來達到類似的效果。

method 是一個有 receiver argument 的 function
we can define method on a type. （不一定是 struct，但這個 type 要在同個 package 中，int 這些 built-in type 要先透過 type 關鍵字來定義一個新型別才能用，例如 `type myint int`）

```
// 定義 Vertex struct
type Vertex struct {
	X, Y float64
}
// Abs method
func (v Vertex) Abs() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func main() {
	v := Vertex{3, 4}
    // 使用 method 時就像別的語言使用一個 class 內ㄉ function 一樣
	fmt.Println(v.Abs())
}
```

- **receiver argument 的型別很重要！golang 會依據他的型別幫忙轉～所以如果這個 method 要改值，記得在 receiver 那邊寫好是吃 pointer（打星星）**

```
// v *Vertex 這樣就算下面的 v 並不是一個 pointer，go 也會幫忙轉 &v
func (v *Vertex) Scale(f float64) { 
	v.X = v.X * f
	v.Y = v.Y * f
}
func main() {
    // 如果拿掉上面 receiver 的*，也可以在這邊 &Vertex{3, 4}
	v := Vertex{3, 4}
    // 或是 (&v).Scale(10)
	v.Scale(10)
}
```

## interface

Go 裡 interface 是一個型別，裡面有定義一堆 method signatures，
只要合乎這些簽章的數值（通常是 struct）就可以放進這個介面變數。
如果這個變數沒有實作規定的 method 的話，就會噴錯。

- empty interface
  沒有定義任何 method 的 interface 當作 input 的型別，就可以接受任意型別的 input。

以下例子來自[day15 - 介面(續)](https://ithelp.ithome.com.tw/articles/10218401)
empty interface + 以 type 為不同 case 的 switch

```
func main() {
	printAnyType(2020)
	printAnyType("Iron Man")
	printAnyType(0.25)
}

// 定義一個函式，接收任何型別，並且格式化輸出值
func printAnyType(i interface{}) {
	switch v := i.(type) {
	case int:
		fmt.Printf("case int: %d \n", v)
	case string:
		fmt.Printf("case string: %s \n", v)
	default:
		fmt.Printf("default: %v \n", v)
	}
}
```

## 沒有繼承

畢竟沒有 class，也沒有繼承的概念。
而是使用 struct 中包 struct，稱之為 composition。
go 中還能使用 embbeded，這裡不打了。

在物件導向程式中，通常會用繼承來共享上層元件的程式碼。然而，go語言沒有繼承的特性，但我們能用組合的方式來共享程式碼。不僅如此，go語言還提供一種優於組合的語法特性，稱作內嵌。

### 組合(composition)

先來談談我所知道的組合，大部分的文章會講到組合是聚合(aggregation)的一種，而它們都是源自於UML的產物，實際上UML定義的定義很模糊也很難理解。因此，我要講的是它們最基本的一面，也就是 `Is-A` 和 `Has-A` 關係:

- Is-A: 繼承關係，表示一個物件也是另一個物件。
- Has-A: 組合關係，表示一個物件擁有另一個物件。

很多文章和書都建議我們要多用**組合少用繼承**，這是因為繼承會對物件造成巨大的依賴關係。我們用一個範例來說明組合:

```go
// 定義一個英雄結構，包含了正常人結構
type Hero struct {
	Person   *Person
	HeroName string
	HerkRank int
}

// 定義一個正常人結構
type Person struct {
	Name string
}

func main() {
	var tony = &Hero{&Person{"Tony Stark"}, "Iron Man", 1}
	fmt.Printf("Hero=%+v\n", *tony)
	fmt.Printf("Person=%+v\n", *(tony.Person))
}
```

執行結果:

```bash
Hero={Person:0xc0000841e0 HeroName:Iron Man HerkRank:1}
Person={Name:Tony Stark}
```

上面範例中，我們看到了所謂的組合就是結構再包結構的概念，透過這樣的方式共享結構資料或方法。

### 內嵌(Embedding)

再來談談go語言的內嵌特性，這個特性並沒有寫在**A Tour of Go**，而是在**Effective Go**裡頭。

Effective Go: [Embedding](https://golang.org/doc/effective_go.html#embedding)

Go語言的內嵌其實就是組合的概念，只是它更加簡潔及強大。內嵌允許我們在結構內組合其他結構時，不需要定義欄位名稱，並且能直接透過該結構叫用欄位或方法。我們將上面的範例改成使用內嵌，如下:

```go
// 定義一個英雄結構
type Hero struct {
	*Person   // 不需要欄位名稱
	HeroName string
	HerkRank int
}

// 定義一個正常人結構
type Person struct {
	Name string
}

func main() {
	var tony = &Hero{
		&Person{"Tony Stark"},
		"Iron Man",
		1}

	fmt.Printf("%s\n", tony.Name)    // 直接叫用內部結構資料
	// 等於 fmt.Printf("%s\n", tony.Person.Name)
}
// 執行結果: Tony Stark
```

實際上，內嵌的結構欄位還是會有名稱，就是和結構本身的名稱同名。

另外，上面範例是用匿名初始化，也可以使用具名初始化，差別在於初始化參數的數量和順序是可以被調整的:

```go
var tony = &Hero{
		Person:   &Person{"Tony Stark"},
		HeroName: "Iron Man",
		HeroRank: 1}
```

### 內嵌與方法

上面看到的範例都是內嵌結構資料，現在我們來試試看內嵌結構方法，修改同一個範例如下:

```go
// 定義一個英雄結構
type Hero struct {
	*Person
	HeroName string
	HeroRank int
}

// 英雄都會飛
func (*Hero) Fly() {
	fmt.Println("I can fly.")
}

// 定義一個正常人結構
type Person struct {
	Name string
}

// 正常人會走路
func (*Person) Walk() {
	fmt.Println("I can walk.")
}

func main() {
	var tony = &Hero{
		Person:   &Person{"Tony Stark"},
		HeroName: "Iron Man",
		HeroRank: 1}

	tony.Walk()   // 等於 tony.Person.Walk()
	tony.Fly()
}
```

執行結果:

```bash
I can walk.
I can fly.
```

### 內嵌結構欄位同名

當有多個內嵌結構時，就有可能發生欄位同名的問題。我們稍微修改一下範例，超級英雄也會想養一隻寵物，這很合理的。因此，我們就加入一個寵物結構:

```go
// 定義一個英雄結構
type Hero struct {
	*Person
	*Pet
	HeroName string
	HeroRank int
}

// 定義一個正常人結構
type Person struct {
	Name string
}

// 定義一個寵物結構
type Pet struct {
	Name string
}

func main() {
	var tony = &Hero{
		Person:   &Person{"Tony Stark"},
		Pet:   &Pet{"Pepper"},
		HeroName: "Iron Man",
		HeroRank: 1}

	fmt.Printf("%s\n", tony.Name)
}
```

由於 Person 和 Parner 都有 Name 這個欄位，直接叫用 tony.Name 就會產生衝突，編譯器會顯示錯誤訊息:

```bash
./main.go:40:25: ambiguous selector tony.Name
```

### 內嵌其他型別

事實上，可以被內嵌的型別不只有結構，也可以是基本型別，範例如下:

```go
type Data struct {
	int
	string
	float32
	bool
}

func main() {
	var data = &Data{1, "Iron Man", 1.2, true}
	fmt.Println(*data)
	fmt.Printf("%+v \n", *data)
}
```

執行結果

```bash
{1 Iron Man 1.2 true}
{int:1 string:Iron Man float32:1.2 bool:true} 
```

基本型別被內嵌之後，欄位名稱就是型別的原始名稱，ex: int, string, ...。

### 小結

今天介紹了go語言的內嵌特性，使得沒有繼承的go語言，依然可以相互共享結構內的程式碼。而這樣的作法在實務上究竟是否優於繼承，可能需要寫久一點，才會深刻了解。