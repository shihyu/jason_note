# Golang - 深入理解 interface 常見用法

出處: https://blog.kennycoder.io/2020/02/03/Golang-%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3interface%E5%B8%B8%E8%A6%8B%E7%94%A8%E6%B3%95/



此篇文章介紹在 Golang 中 interface 的常見用法，interface 在 Golang 中是一個很重要的環節。interface 可以拿來實現多種用途，請看介紹。

## interface 定義

interface 又稱接口，其實功能有點類似於 Java 中的 interface，但是在一些地方完全不同於 Java 中 interface 的設計。

在 Golang 中，interface 其中一個功能就是可以使用 interface 定義行為，也就是說 interface 中可以定義一些方法來表示一個對象的行為，而當我們有自定義的型態假設想要擁有這些行為，就是去實踐 interface 裡面的方法。

## interface 定義行為

來看個例子：

```go
package main

import "fmt"

type Animal interface {
	Eat()
	Run()
}

type Dog struct {
	Name string
}

func (d *Dog) Eat() {
	fmt.Printf("%s is eating\n", d.Name)
}

func (d *Dog) Run() {
	fmt.Printf("%s is running\n", d.Name)
}

func ShowEat(animal Animal) {
	animal.Eat()
}

func ShowRun(animal Animal) {
	animal.Run()
}

func main() {
	dog := Dog{Name:"Kenny"}
	ShowEat(&dog)
	ShowRun(&dog)
}
```

1. 建立一個 Animal 型態的 interface，其定義了 Eat () 跟 Run ()，來表達動物都會擁有的行為。
2. 建立一個 Dog Struct，並且實踐 interface 裡面的 Eat () 跟 Run ()。要注意的是，由於在實作 `Eat` 與 `Run` 方法時，都是用指標 `(d *Dog)` ，這個所代表的意思是透過傳遞指標來操控同一個 Struct 實例，如果沒有用指標則會導致淺複製的行為，並不是操控同一個 Struct。
3. 建立 ShowEat、ShowRun 方法，並且參數型態用 Animal。

以上的程式碼可以得知以下兩件事情：

1. 在 Golang 中如果自定義型態實現了 interface 的所有方法，那麼它就會認定該自定義型態也是 interface 型態的一種。也就是所謂的鴨子型別 (Duck typing) 的實現。只要你有符合這些種種的行為，即使你不是真的鴨子，那麼還是會認定你是一隻鴨子。
2. 透過 ShowRun 跟 ShowEat () 得知實現了多型的行為。所謂多型的意思是相同的訊息給予不同的物件會引發不同的動作，因為參數型態用 Animal 所以，每個動物會有各自的吃跟跑的行為，執行出來的結果也會各自不一樣。

## interface 型態與值

將 main 裡面程式碼改成這樣：

```go
func main() {
	var animal Animal
	fmt.Println(animal)
}
```

這樣輸出會是 nil。

1. 這代表著 `animal` 在底層儲存的型態為 `nil`。interface 類型默認是一個指針 (引用類型)，如果沒有對 interface 初始化就使用，那麼會輸出 `nil`。

2. 但是我們可以指定自定義型態給 nil interface，如果該自定義型態有實現該 interface 方法即可。

   ```go
   func main() {
   	var animal Animal
   	animal = &Dog{Name:"Kenny"}
   	fmt.Println(animal)
   }
   ```

   運行結果為 `&{Kenny}`。

   也就是說 `animal` 底層儲存的型態會 `*Dog`，而值是 `Dog` 結構實例的位址值。

## interface 繼承

一個自定義型態是可以實現多個 interface 的。此外，interface 也可以繼承別的 interface 的行為：

```go
package main

import "fmt"

type Eater interface {
	Eat()
}

type Runner interface {
	Run()
}

type Animal interface {
	Eater
	Runner
}

type Dog struct {
	Name string
}

func (d *Dog) Eat() {
	fmt.Printf("%s is eating\n", d.Name)
}

func (d *Dog) Run() {
	fmt.Printf("%s is running\n", d.Name)
}

func ShowEat(animal Animal) {
	animal.Eat()
}

func ShowRun(animal Animal) {
	animal.Run()
}

func ShowEat2(eater Eater) {
	eater.Eat()
}

func ShowRun2(runner Runner) {
	runner.Run()
}

func main() {
	dog := Dog{Name:"Kenny"}
	ShowEat(&dog)
	ShowRun(&dog)
	ShowEat2(&dog)
	ShowRun2(&dog)
}
```

在 Animal interface 透過內嵌的方式，將 Eater interface、Runner interface 定義的行為放進去。

這樣的話 Dog Struct 必須都實現 Eat () 跟 Run () 才能是 Animal 的一種。此外，因為這樣做也代表，Dog Struct 也是 Eater 及 Runner 的一種。

所以看到定義的 ShowEat2 () 跟 ShowRun2 () 皆能接受 Dog Struct。

## 透過 interface 儲存異質陣列或 slice

前面說過 Golang 會檢查類型的實例，是否都有實現 interface 定義的行為，如果是的話就可以接受介面型態是不同型態實例的指定。

透過這種特性，假設我們有個需求是一個陣列或 slice 存放的型態無法事先確定，且每個元素的型態可能都不是一樣，就可以透過 interface 來解決！

```go
package main

import "fmt"

type Eater interface {
	Eat()
}

type Runner interface {
	Run()
}

type Animal interface {
	Eater
	Runner
}

type Dog struct {
	Name string
}

func (d *Dog) Eat() {
	fmt.Printf("%s is eating\n", d.Name)
}

func (d *Dog) Run() {
	fmt.Printf("%s is running\n", d.Name)
}

type Cat struct {
	Name string
}

func (c *Cat) Eat() {
	fmt.Printf("%s is eating\n", c.Name)
}

func (c *Cat) Run() {
	fmt.Printf("%s is running\n", c.Name)
}

func ShowEat(animal Animal) {
	animal.Eat()
}

func ShowRun(animal Animal) {
	animal.Run()
}

func ShowEat2(eater Eater) {
	eater.Eat()
}

func ShowRun2(runner Runner) {
	runner.Run()
}

func main() {
	animals := [...]Animal{
		&Dog{Name:"Kenny"},
		&Cat{Name:"Nicole"},
	}

	for _, animal := range animals {
		fmt.Println(animal)
	}

	instances := [...]interface{}{
		123,
		"Hello World",
		&Dog{Name:"Kenny"},
		&Cat{Name:"Nicole"},
	}

	for _, instance := range instances {
		fmt.Println(instance)
	}
}
```

在這邊多定義了 Cat Struct，並且同樣實現了 Animal interface。

因此在前面可以建立 Animal 型態的陣列，裡面可以放不同結構體的實例，只要裡面放置的結構體有實現 Animal interface 行為，就會被當作 Animal 實例。

而第二個例子是利用空接口型態，裡面可以放置各種型態的元素，以這個例子來看既能放 int、string、Dog Struct、Cat Struct。

也因為空接口的特性也是實現泛型的重要關鍵。

## 型態斷言

但是根據以上的例子會發現一個問題：

假設利用自定義型態為 Animal interface 指定型態的話，該型態就能存取 interface 的行為，並不能存取自定義型態的屬性及其它自定義型態的方法。

這時候可以利用 Golang 提供的型態斷言的特性，請看：

```go
func main() {
	var animal Animal
	animal = &Dog{Name:"Kenny"}
	dog := animal.(*Dog)
	fmt.Println(dog.Name)

	animal = &Cat{Name:"Nicole"}
	cat := animal.(*Dog)
	fmt.Println(cat.Name)
}
```

透過`.(type)` 的方式來斷定該接口實際上是存放哪個實例。但是有個缺點是如果型態判斷錯誤，會直接造成 panic。

出現以下錯誤訊息：

```
panic: interface conversion: main.Animal is *main.Cat, not *main.Dog
```

這是因為後面的 animal 是指定 Cat 實例，結果後面型態斷言用 Dog，會造成執行時期的錯誤。

要怎麼避免呢？

可以透過 switch 的方式一一去判斷型態：

```go
func main() {
	animals := [...]Animal{
			&Dog{Name:"Kenny"},
			&Cat{Name:"Nicole"},
		}

	for _, animal := range animals {
		switch animal.(type) {
		case *Dog:
			fmt.Println(animal.(*Dog).Name)
		case *Cat:
			fmt.Println(animal.(*Cat).Name)
		default:
			fmt.Println("you are not animal!!")
		}
	}
}
```

透過`.(type)` 來一一比對出對的型態。

此外，Golang 型態斷言也提供了檢測機制：

```go
func main() {
	animals := [...]Animal{
			&Dog{Name:"Kenny"},
			&Cat{Name:"Nicole"},
		}

	for _, animal := range animals {
		if dog, ok := animal.(*Dog); ok {
			fmt.Println(dog.Name)
		}

		if cat, ok := animal.(*Cat); ok {
			fmt.Println(cat.Name)
		}
	}
}
```

當然了，如果斷言的形態越多用 switch 相對可讀性會較高。

## 空 interface 的限制

根據以上的例子可以空接口提供很多便利性，但是也有其限制：

一個空的接口會隱藏值對應的表示方式和所有的公開的方法，必須使用類型斷言才能來來訪問內部的值，如果事先不知道空接口指向的值的具體類型，就無法操作。

為此，才需要 **reflect 機制**，可以知道一個接口類型的變量具體是什麼（什麼類型），有什麼能力（有哪些方法）。這也是在寫 Golang 程式庫常常會用到的特性，因為有 interface 可以實現泛型的特性，有了泛型的特性又可以透過 reflect 機制來促發其不同型態的屬性及方法。

## 總結

- Golang interface 重點是「行為」，不管定義的介面型態是什麼，只要行為符合就屬於該介面型態的一種。
- Golang interface 可以說是動態語言鴨子型別的展現。
- 利用 interface 可實現泛型、多型的功能，從而可以調用同一個函數名的函數但實現完全不同的功能。

所以根據以上 interface 的特點，在看看 Golang 的標準程式庫裡面運用大量的 interface 的特性來完成，例如標準程式庫定義檔案讀寫的 Reader、Writer interface：

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}

type Writer interface {
	Write(p []byte) (n int, err error)
}
```

利用 `os.File` 實現了 Reader、Writer interface，來實作檔案讀寫的實現。



---

## Interface 接口

要特別注意，這個interface跟其他語言中的定義與作用會不太一樣。

首先讓我們回憶一下golang的特性，會想起他是「輕量級的物件導向」，也就是他沒有完全實作物件導向的所有特徵。具體來說，golang沒有class（類別）與繼承（這樣還能稱之為物件導向嗎？）。但是現代軟體開發，如果需要類似「多型」的需求怎麼辦呢？interface就是golang中用來實踐多型的利器，雖然並不是完全符合多型的概念，但至少在概念上是接近的。尤其是在golang這種強型別的語言，interface可以發揮更高的潛能。

interface有兩種，分別是型態與定義。**interface可以代表任何型態，這在開發上可以帶來極大的便利（弱型別語言表示）**，我們來看看具體上要如何實作：

```go
func Hello(value interface{}) {  
}
```

將interface作為參數宣告，這個函數就可以接受任意型態的參數。但在實際使用之前，我們還是必須先辨別傳遞進來的參數型別，才能做接下來的邏輯實作，畢竟golang依然是個強型別的語言，沒有因為有了interface就做出讓步。

```go
func Hello(value interface{}) {  
    // 透過型態斷言揭露 interface{} 真正的型態。
    switch v := value.(type) {
        // 如果 value 是字串型態。
        case string:
            fmt.Println("value 是字串，內容是 " + v)
        // 如果 value 是 int 型態。
        case int:
            fmt.Printf("value 是數值，加上二就是 %d", v + 2)
    }
}
```

延續第一個範例，我們從外部得到型別未知的參數`value`，透過`switch`與`value.(type)`方法，可以將不同型別的邏輯分離出來，做不同的處理。如果你很確定參數的型別，也可以直接使用宣告的方式來取代`switch`判斷，方法如下：

```go
func Hello(value interface{}) {  
    fmt.Println("value 是字串，內容是 " + value.(string))
}
```

但如果interface參數與你預期的型別不同，會出現`panic`警告。作為參數可以為任意類別，如果函數的返回值為interface，也就代表函數可以返回任意類別值。

在變數的方面，**當我們定義一個空的interface，它可以指定為任意型別**：

```go
var a interface{}
var i int = 5
s := "Hello world"
// a可以儲存任意類別的值
a = i
a = s
```

到這邊你可能會想，一個強型別語言為什麼需要想辦法實作一個可以是任何型態的參數或變數，這不是根本否定的強型別的價值嗎？我想到一個長久以來在工程師圈關於「限制-自由」的拉扯，有一句名言是這樣總結的：

> 限制帶給你新的自由

限制的好處是當我們在規則與紀律之中妥協，我們可以更早發現不協調之處，讓bug無所遁形。如果毫無限制邊界，反而讓人無從發揮。我認為這並不是一個布林的問題，而是float，在光譜之中有眾多選擇，可以讓每個人依喜好與需求做選擇。

這樣的設計讓golang在大部份的時候受到型別拘束保護，不會產生型別的意外狀況；當在需要開發套件與第三方程式串接的時候，又不需要把自己綁死侷限了開發空間的可能，是語言設計者的一個優雅的權衡。

我們來看另一個例子，如何在golang中用interface實現多型：

```go
package main

import (
	"fmt"
)

type Animal interface {
	Speak() string
}

type Dog struct {
}

func (d Dog) Speak() string {
	return "Woof!"
}

type Cat struct {
}

func (c Cat) Speak() string {
	return "Meow!"
}

type Pikachu struct {
}

func (p Pikachu) Speak() string {
	return "Pika pika!"
}

type Programmer struct {
}

func (j Programmer) Speak() string {
	return "Design patterns!"
}
func main() {
	animals := []Animal{Dog{}, Cat{}, Pikachu{}, Programmer{}}
	for _, animal := range animals {
		fmt.Println(animal.Speak())
	}
}
```

如果執行這段程式，我們會得到：

```repl
Woof!
Meow!
Pika pika!
Design patterns!
```

Animal作為一個interface定義一個空的`Speak()`方法，藉由宣告一個Animal陣列`animals`將貓、狗、皮卡丘、工程師實體傳進陣列中，接著實體各自執行自己實作的`Speak()`方法。



---

**struct**

struct 用來自定義複雜資料結構，可以包含多個欄位（屬性），可以巢狀；go中的struct型別理解為類，可以定義方法，和函式定義有些許區別；struct型別是值型別。

```go
package main

type User struct {
	Name string
	Age  int32
	mess string
}

var user User
var user1 *User = &User{}
var user2 *User = new(User)
```

**struct的方法**

在go語言中，我們可以為自定義型別定義型別相關的方法，比如：

```go
func (p *player) Name() string {
	return p.name
}
```

上面的程式碼為player這個自定義型別宣告一個名為Name的方法，該方法返回一個string。值得注意的是（p *player）這段程式碼指定了我們是**為player建立方法**，並將呼叫該方法的例項指標當作變數p傳入該函式，如果沒有（p *player）這段程式碼，這個方法就變成了一個普通的全域性函式。

**struct的嵌入（Embedding）**

go語言中的“繼承”和其他語言中的繼承有很大區別，比如：

```go
type player struct {
	User
}
```

這是一種**繼承**的寫法，在go語言中這種方式叫做**嵌入（embed）**，此時player型別就擁有了User型別的Name, Age, mess 等變數

**struct的tag**

這種方式主要是用在xml，json和struct間相互轉換，非常方便直觀，比如介面給的引數一般是json傳過來，但是內部我們要轉為struct再進行處理。

```go
package main

import "encoding/json"
import "fmt"

type User struct {
	Name string `json:"userName"`
	Age  int    `json:"userAge"`
}

func main() {
	var user User
	user.Name = "nick"
	user.Age = 18
	conJson, _ := json.Marshal(user)
	fmt.Println(string(conJson)) //{"userName":"nick","userAge":0}
}
```

**interface**

golang不支援完整的物件導向思想，它沒有繼承，多型則完全依賴介面實現。golang只能模擬繼承，**其本質是組合**，只不過golang語言為我們提供了一些語法糖使其看起來達到了繼承的效果。Golang中的介面，不需要顯示的實現。Interface型別可以定義一組方法，但是這些不需要實現。並且interface不能包含任何變數。只要一個變數，含有介面型別中的所有方法，那麼這個變數就實現這個介面。因此，golang中沒有implement類似的關鍵字；如果一個變數含有了一個interface型別的多個方法，那麼這個變數就實現了多個介面；如果一個變數只含有了一個interface的方部分方法，那麼這個變數沒有實現這個介面。

**interface的定義**

interface型別預設是一個指標。

```go
package main

type Car interface {
	NameGet() string
	Run(n int)
	Stop()
}
```

空介面 Interface{}：空介面沒有任何方法，所以所有型別都實現了空介面。

```go
var a int
var b interface{} //空介面
b = a
```

**interface的多型**

一種事物的多種形態，都可以按照統一的介面進行操作。這種方式是用的最多的，有點像c 中的類繼承。

```go
package main

type Item interface {
	Name() string
	Price() float64
}
type VegBurger struct {
}

func (r *VegBurger) Name() string {
	return "vegburger"
}
func (r *VegBurger) Price() float64 {
	return 1.5
}

type ChickenBurger struct {
}

func (r *ChickenBurger) Name() string {
	return "chickenburger"
}
func (r *ChickenBurger) Price() float64 {
	return 5.5
}
```

**Interface巢狀**

一個介面可以巢狀在另外的介面。即需要實現2個介面的方法。在下面的例子中Used就包含了Car這個介面的所有方法。

```go
package main

type Car interface {
	NameGet() string
	Run(n int)
	Stop()
}
type Used interface {
	Car
	Cheap()
}
```

**總結**

以上就是這篇文章的全部內容了，希望本文的內容對大家的學習或者工作具有一定的參考學習價值，如果有疑問大家可以留言交流，謝謝大家對指令碼之家的支援。