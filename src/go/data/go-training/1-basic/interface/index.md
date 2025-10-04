Go 語言不是一種 “傳統” 的面向對象編程語言：它裡面沒有類和繼承的概念，但是 Go 語言裡有非常靈活的 接口 概念，通過它可以實現很多面向對象的特性。

接口是定義了一組需要被實現的方法的抽象類型，但是這些方法不包含（實現）代碼， 接口類型是對其它類型行為的抽象和概括，對於需要滿足接口的數據類型，它需要實現接口所需的所有方法，一個接口包含兩部分：一組接口方法和一個接口類型。

使用接口的最大優勢，就是在定義函數時使用接口作為參數，那麼在調用函數時，任何實現該接口類型的變量都可以作為函數的參數被傳遞。


# 1.接口的定義
每個接口由數個方法組成，接口的定義格式如下：
```go  
type 接口類型名 interface{
    方法名1( 參數列表1 ) 返回值列表1
    方法名2( 參數列表2 ) 返回值列表2
    …
}
```
- 接口名：使用 type 將接口定義為自定義的類型名， Go 語言的接口在命名時，（按照約定，只包含一個方法的）接口的名字由方法名加 [e]r 後綴組成，例如 Printer、Reader、Writer、Logger、Converter 等等。還有一些不常用的方式（當後綴 er 不合適時），比如 Recoverable，此時接口名以 able 結尾。
- 方法名：當方法名首字母是大寫且這個接口類型名首字母也是大寫時，這個方法可以被接口所在的包之外的包代碼訪問。
- 參數列表、返回值列表：參數列表和返回值列表中的參數變量名可以省略：

```go  
type Caller interface {
	call()
}
```

# 2.接口的實現
一個類型如果擁有一個接口需要的所有方法，那麼這個類型就實現了這個接口。

```go  
type Iphone6s struct {
}

func (i Iphone6s) call() {
	fmt.Println("使用IPhone 6s打個電話")
}
```

# 3.接口的使用
```go  
//可以使用接口作為參數
func CallToMom(c Caller) {
	c.call()
}
//任意實現了該接口中聲明方法的對象都可以作為參數傳入
var i Iphone6s
CallToMom(i)
```

# 4.特殊接口之空接口
空接口是指沒有定義任何方法的接口。
- 1.因此任何類型都實現了空接口，可以給一個空接口類型的變量賦任何類型的值。
- 2.如果一個函數的參數是空接口類型，那麼它也可以接收任何參數

```go  
type Any interface{}

func main() {
    var val Any
    val = 5
    fmt.Printf("type:%T value:%v\n", val)   //type:int value:5
    
    str := "string"
    val = str
    fmt.Printf("type:%T value:%v\n", val)  //type:string value:string
}
```

# 5.特殊接口之接口嵌套
一個接口可以包含一個或多個其他的接口，這相當於直接將這些內嵌接口的方法列舉在外層接口中一樣。
```go  
type ReadWrite interface {
    Read(b Buffer) bool
    Write(b Buffer) bool
}

type Lock interface {
    Lock()
    Unlock()
}

// 接口 File 包含了 ReadWrite 和 Lock 的所有方法，它還額外有一個 Close() 方法
type File interface {
    ReadWrite
    Lock
    Close()
}
```

# 6.測試一個值是否實現了某個接口
這是類型斷言中的一個特例：假定 v 是一個值，然後我們想測試它是否實現了 Stringer 接口，可以這樣做：

```go  
var i Iphone6s
CallToMom(i)

var e interface{} = i
v, ok := e.(Caller)
if ok {
    fmt.Println("該對象實現了Caller接口", v) 
} else {
    fmt.Println("該對象沒有實現Caller接口", v)
}
```

