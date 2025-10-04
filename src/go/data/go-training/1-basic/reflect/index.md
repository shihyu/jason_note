反射是指在程序運行期對程序本身進行訪問和修改的能力。程序在編譯時，變量被轉換為內存地址，變量名不會被編譯器寫入到可執行部分。在運行程序時，程序無法獲取自身的信息。

支持反射的語言可以在程序編譯期將變量的反射信息，如字段名稱、類型信息、結構體信息等整合到可執行文件中，並給程序提供接口訪問反射信息，這樣就可以在程序運行期獲取類型的反射信息，並且有能力修改它們。

Go 語言由 reflect 包提供的反射功能，它定義了兩個重要的類型, Type 和 Value， 一個 Type 表示一個 Go 類型。任意接口值在反射中都可以理解為由 reflect.Type 和 reflect.Value 兩部分組成，並且 reflect 包提供了 reflect.TypeOf 和 reflect.ValueOf 兩個函數來獲取任意對象的 Value 和 Type。

# TypeOf函數
函數 reflect.TypeOf 接受任意的 interface{} 類型, 並以 reflect.Type 形式返回其動態類型:

```go
var a int = 64
t1 := reflect.TypeOf(a)            //注意 TypeOf的參數類型是 interface{}
fmt.Printf("type:%v\n", t1.Name()) //type:int
```

在反射中關於類型還劃分為兩種：類型（Type）和種類（Kind）。因為在Go語言中我們可以使用type關鍵字構造很多自定義類型，而種類（Kind）就是指底層的類型，但在反射中，當需要區分指針、結構體等大品種的類型時，就會用到種類（Kind）

```go
var id UserId
t2 := reflect.TypeOf(id)
fmt.Printf("type:%v kind:%v\n", t2.Name(), t2.Kind()) //輸出 type:UserId kind:int
```

# ValueOf 函數
reflect.ValueOf() 返回的是 reflect.Value 類型，其中包含了原始值的值信息。reflect.Value 與原始值之間可以互相轉換。

```go
var n int = 100
v := reflect.ValueOf(n)
fmt.Println(v.Int()) //輸出100
```

reflect.Value類型提供的獲取原始值的方法如下：
- Interface() interface {}	將值以 interface{} 類型返回，可以通過類型斷言轉換為指定類型
- Int() int64	將值以 int 類型返回，所有有符號整型均可以此方式返回
- Uint() uint64	將值以 uint 類型返回，所有無符號整型均可以此方式返回
- Float() float64	將值以雙精度（float64）類型返回，所有浮點數（float32、float64）均可以此方式返回
- Bool() bool	將值以 bool 類型返回
- Bytes() []bytes	將值以字節數組 []bytes 類型返回
- String() string	將值以字符串類型返回


如果想要在函數中通過反射修改變量的值，需要注意函數參數傳遞的是值拷貝，必須傳遞變量地址才能修改變量值。而反射中使用專有的 Elem() 方法來獲取指針對應的值。

```go
var n2 int = 100
v2 := reflect.ValueOf(&n2)
fmt.Println(v2) //得到的是一個地址：0xc0000b4048
v2.Elem().SetInt(200)
fmt.Println(n2) //輸出200，修改成功！
```