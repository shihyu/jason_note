## 學習筆記之第1章 Go基礎入門



- [第1章 Go基礎入門](https://blog.csdn.net/oqqyx1234567/article/details/119815145#1_Go_2)
- - [1.1 安裝Go](https://blog.csdn.net/oqqyx1234567/article/details/119815145#11_Go_3)
  - [1.2 第一個Go程序](https://blog.csdn.net/oqqyx1234567/article/details/119815145#12_Go_7)
  - [1.3 Go基礎語法與使用](https://blog.csdn.net/oqqyx1234567/article/details/119815145#13_Go_71)
  - - [1.3.1 基礎語法](https://blog.csdn.net/oqqyx1234567/article/details/119815145#131__72)
    - [1.3.2 變量](https://blog.csdn.net/oqqyx1234567/article/details/119815145#132__126)
    - [1.3.3 常量](https://blog.csdn.net/oqqyx1234567/article/details/119815145#133__244)
    - [1.3.4 運算符](https://blog.csdn.net/oqqyx1234567/article/details/119815145#134__325)
    - [1.3.5 流程控制語句](https://blog.csdn.net/oqqyx1234567/article/details/119815145#135__359)
  - [1.4 Go數據類型](https://blog.csdn.net/oqqyx1234567/article/details/119815145#14_Go_611)
  - - [1.4.1 布爾型](https://blog.csdn.net/oqqyx1234567/article/details/119815145#141__619)
    - [1.4.2 數字類型](https://blog.csdn.net/oqqyx1234567/article/details/119815145#142__650)
    - [1.4.3 字符串類型](https://blog.csdn.net/oqqyx1234567/article/details/119815145#143__653)
    - [1.4.4 指針類型](https://blog.csdn.net/oqqyx1234567/article/details/119815145#144__752)
    - [1.4.5 復合類型](https://blog.csdn.net/oqqyx1234567/article/details/119815145#145__854)
  - [1.5 函數](https://blog.csdn.net/oqqyx1234567/article/details/119815145#15__1043)
  - - [1.5.1 聲明函數](https://blog.csdn.net/oqqyx1234567/article/details/119815145#151__1045)
    - [1.5.2 函數參數](https://blog.csdn.net/oqqyx1234567/article/details/119815145#152__1109)
    - [1.5.3 匿名函數](https://blog.csdn.net/oqqyx1234567/article/details/119815145#153__1173)
    - [1.5.4 defer延遲語句](https://blog.csdn.net/oqqyx1234567/article/details/119815145#154_defer_1244)
  - [1.6 Go面向對象編程](https://blog.csdn.net/oqqyx1234567/article/details/119815145#16_Go_1341)
  - - [1.6.1 封裝](https://blog.csdn.net/oqqyx1234567/article/details/119815145#161__1342)
    - [1.6.2 繼承](https://blog.csdn.net/oqqyx1234567/article/details/119815145#162__1430)
    - [1.6.3 多態](https://blog.csdn.net/oqqyx1234567/article/details/119815145#163__1449)
  - [1.7 接口](https://blog.csdn.net/oqqyx1234567/article/details/119815145#17__1491)
  - - [1.7.1 接口定義](https://blog.csdn.net/oqqyx1234567/article/details/119815145#171__1493)
    - [1.7.2 接口賦值](https://blog.csdn.net/oqqyx1234567/article/details/119815145#172__1539)
    - [1.7.3 接口查詢](https://blog.csdn.net/oqqyx1234567/article/details/119815145#173__1667)
    - [1.7.4 接口組合](https://blog.csdn.net/oqqyx1234567/article/details/119815145#174__1707)
    - [1.7.5 接口應用](https://blog.csdn.net/oqqyx1234567/article/details/119815145#175__1725)
  - [1.8 反射](https://blog.csdn.net/oqqyx1234567/article/details/119815145#18__1796)
  - - [1.8.1 反射的定義](https://blog.csdn.net/oqqyx1234567/article/details/119815145#181__1797)
    - [1.8.2 反射的三大法則](https://blog.csdn.net/oqqyx1234567/article/details/119815145#182__1809)
  - [1.9 goroutine簡介](https://blog.csdn.net/oqqyx1234567/article/details/119815145#19_goroutine_1936)
  - [1.10 單元測試（go test）](https://blog.csdn.net/oqqyx1234567/article/details/119815145#110_go_test_1962)
  - [1.11 Go編譯與工具](https://blog.csdn.net/oqqyx1234567/article/details/119815145#111_Go_2006)
  - - [1.11.1 編譯（go build）](https://blog.csdn.net/oqqyx1234567/article/details/119815145#1111_go_build_2007)
    - [1.11.2 編譯後運行（go run）](https://blog.csdn.net/oqqyx1234567/article/details/119815145#1112_go_run_2103)
    - [1.11.3 編譯並安裝（go install）](https://blog.csdn.net/oqqyx1234567/article/details/119815145#1113_go_install_2120)
    - [1.11.4 獲取代碼（go get）](https://blog.csdn.net/oqqyx1234567/article/details/119815145#1114_go_get_2153)



# 第1章 Go基礎入門

## 1.1 安裝Go

https://golang.google.cn/dl/

## 1.2 第一個Go程序

```
package main

import "fmt"

func main() {
	fmt.Println("Hello World～")
}
```

1. 包聲明

包管理單位。

```go
package xxx
```

- 目錄下同級文件屬於同一個包
- 包名與目錄名可以不同
- 有且僅有一個main包（入口包）

1. 包導入

調用其他包的變量或方法。

```go
import "package_name"
import (
	"os"
	"fmt"
)
別名
import (
	alias1 "os"
	alias2 "fmt"
)
import (
	_ "os" //只初始化包(調用包中init函數)，不使用包中變量或函數。
	alias2 "fmt"
)
```

1. main函數

入口函數，只能聲明在main包中，有且僅有一個。

```go
func 函數名(參數列表) (返回值列表) {
	函數體
}
```

## 1.3 Go基礎語法與使用

### 1.3.1 基礎語法

1. Go語言標記

Go程序由關鍵字、標識符、常量、字符串、符號等多種標記組成。

```go
fmt . Println ( "Hi" )
```

1. 行分隔符

一般一行一個語句，多個語句用；隔開。

1. 注釋

//單行注釋
/*
多行注釋
多行注釋
*/

1. 標識符

標識符通常用來對變量、類型等命名。[a-zA-Z0-9_]組成，不能以數字開始，不能是Go語言關鍵字。

1. 字符串連接

```go
package main

import "fmt"

func main() {
	fmt.Println("hello" + " world")
}
```

1. 關鍵字

| continue | for         | import | return    | var    |
| -------- | ----------- | ------ | --------- | ------ |
| const    | fallthrough | if     | range     | type   |
| chan     | else        | goto   | package   | swith  |
| case     | defer       | go     | map       | struct |
| break    | default     | func   | interface | select |

- 常量相關預定義標識符：true、false、ioto、nil
- 類型相關預定義標識符：int、int8、int16、int32、int64、uint、uint8、uint16、uint32、uint64、uintptr、float32、float64、complex128、complex64、bool、byte、rune、string、error
- 函數相關預定義標識符：make、len、cap、new、append、copy、close、delete、complex、real、imag、panic、recover

1. Go語言空格

var name string
name = “y” + “x”

### 1.3.2 變量

變量（variable）是一段或多段用來存儲數據的內存，有明確類型。

```go
var name type
var c, d *int
```

默認零值或空值，int為0，float為0.0，bool為false，string為""，指針為nil。
建議駝峰命名法totalPrice或下劃線命名法total_price。

```go
var (
	age int
	name string
	balance float32
)
```

名字 := 表達式
簡短模式（short variable declaration）限制：

- 只用於定義變量，同時顯示初始化
- 表達式自動推導數據類型
- 用於函數內部，即不能聲明全局變量

```go
package main

import (
	"fmt"
)

func main() {
	//var 變量名 [類型] = 變量值
	var language1 string = "Go"
	fmt.Printf("language1=%s\n", language1)
	var language2 = "Go"
	fmt.Printf("language2=%s\n", language2)
	
	//變量名 := 變量值
	language3 := "Go"
	fmt.Printf("language3=%s\n", language3)
	
	/*
	var (
		變量名1 [變量類型1] = 變量值1
		變量名2 [變量類型2] = 變量值2
	)
	*/
	var (
		age1 int = 18
		name1 string = "yx"
		balance1 = 999.9
	)
	fmt.Printf("age1=%d, name1=%s, balance1=%f\n", age1, name1, balance1)
	
	//var 變量名1, 變量名2 = 變量值1, 變量值2
	var age2, name2, balance2 = 18, "yx", 999.9
	fmt.Printf("age2=%d, name2=%s, balance2=%f\n", age2, name2, balance2)
	
	//變量名1, 變量名2 := 變量值1, 變量值2
	age3, name3, balance3 := 18, "yx", 999.9
	fmt.Printf("age3=%d, name3=%s, balance3=%f\n", age3, name3, balance3)
	
	//變量交換值
	d, c := "D", "C"
	fmt.Printf("d=%s, c=%s\n", d, c)
	c, d = d, c
	fmt.Printf("d=%s, c=%s\n", d, c)
}
```

局部變量，函數體內聲明的變量，參數和返回值變量都是局部變量。

```go
package main

import "fmt"

func main() {
	var local1, local2, local3 int

	local1 = 8
	local2 = 10
	local3 = local1 + local2 
	
	fmt.Printf("local1=%d, local2=%d, local3=%d\n", local1, local2, local3)
}
```

全局變量，函數體外聲明的變量，可以在整個包甚至外部包（被導出）中使用，也可在任何函數中使用。

```go
package main

import "fmt"

var global int

func main() {
	var local1, local2 int

	local1 = 8
	local2 = 10
	global = local1 + local2 
	
	fmt.Printf("local1=%d, local2=%d, global=%d\n", local1, local2, global)
}
package main

import "fmt"

var global int = 8

func main() {
	var global int = 99
	fmt.Printf("global=%d\n", global)
}
```

### 1.3.3 常量

const聲明，編譯時創建（聲明在函數內部也是），存儲不會改變的數據，只能是布爾型、數字型（整數、浮點和復數）和字符串型。

```go
package main

import (
	"fmt"
)

//const 常量名 [類型] = 常量表達式
const PI float32 = 3.1415926

//itoa用於生成一組以相似規則初始化的常量。
type Direction int
const (
	North Direction = iota
	East
	South
	West
)

/*
常量間算術、邏輯、比較運算都是常量。
常量進行類型轉換，返回常量結果。
len()，cap()，real()，imag()，complex()和unsafe.Sizeof()等函數調用返回常量結果。
*/
const IPv4Len = 4
func paraseIPv4(s string) ([4]byte, error) {
	var p [IPv4Len]byte	
	return p, nil
}

func main() {
	const (
		e = 2.7182818
		pi = 3.1415926
	)

	fmt.Printf("PI=%v\n", PI)
	fmt.Printf("e=%v, pi=%v\n", e, pi)
	
	fmt.Printf("West=%v\n", West)

	if ip, err := paraseIPv4("192.168.1.1"); err != nil {
		fmt.Printf("ip=%v\n", ip)
	}
}
```

6種未明確類型的常量類型：

- 無類型的布爾型(true和false)
- 無類型的整數(0)
- 無類型的字符(\u0000)
- 無類型的浮點數(0.0)
- 無類型的復數(0i)
- 無類型的字符串("")

延遲明確常量的具體類型，可以直接用於更多的表達式而不需要顯示的類型轉換。

```go
package main

import (
	"math"
	"fmt"
)

func main() {
	var a float32 = math.Pi
	var b float64 = math.Pi
	var c complex128 = math.Pi
	fmt.Printf("a=%v, b=%v, c=%v\n", a, b, c)
	
	const Pi64 float64 = math.Pi
	a = float32(Pi64)
	b = Pi64
	c = complex128(Pi64)
	fmt.Printf("a=%v, b=%v, c=%v\n", a, b, c)
}
```

### 1.3.4 運算符

運算符是用來在程序運行時執行數學運算或邏輯運算的符號。

```go
package main

import (
	"fmt"
)

func main() {
	var a, b, c = 3, 6, 9
	d := a + b * c
	fmt.Printf("d=%v\n", d)
}
```

優先級是指，同一表達式中多個運算符，先執行哪一個。

| 優先級 | 分類       | 運算符                                               | 結合性   |
| ------ | ---------- | ---------------------------------------------------- | -------- |
| 1      | 逗號運算符 | ,                                                    | 從左到右 |
| 2      | 賦值運算符 | =、+=、-=、*=、/=、%=、>=、<<=、&=、^=、\|=          | 從右到左 |
| 3      | 邏輯或     | \|\|                                                 | 從左到右 |
| 4      | 邏輯與     | &&                                                   | 從左到右 |
| 5      | 按位或     | \|                                                   | 從左到右 |
| 6      | 按位異或   | ^                                                    | 從左到右 |
| 7      | 按位與     | &                                                    | 從左到右 |
| 8      | 等不等     | ==、!=                                               | 從左到右 |
| 9      | 關系運算符 | <、<=、>、>=                                         | 從左到右 |
| 10     | 位移運算符 | <<、>>                                               | 從左到右 |
| 11     | 加減法     | +、-                                                 | 從左到右 |
| 12     | 乘除法取餘 | *（乘號）、/、%                                      | 從左到右 |
| 13     | 單目運算符 | !、*（指針）、&（取址）、++、–、+（正號）、-（負號） | 從右到左 |
| 14     | 後綴運算符 | ()、[]                                               | 從左到右 |

### 1.3.5 流程控制語句

```
if-else
package main

import (
	"fmt"
)

func if_else_return(b int) int {
	if b > 10 {
		return 1
	} else if b == 10 {
		return 2
	} else {
		return 3
	}
}

func main() {
	fmt.Println(if_else_return(10))
}
```

`for`
Go不支持while和do while。

```go
package main

import (
	"fmt"
)

func main() {
	product := 1
	for i := 1; i < 5; i++ {
		product *= i
	}
	fmt.Println(product)

	i := 0
	for {
		if i > 50 {
			break
		}
		i++
	}
	fmt.Println(i)

	j := 2
	for ; j > 0; j-- {
		fmt.Println(j)
	}

JumpLoop:
	for i := 0; i < 5; i++ {
		for j := 0; j < 5; j++ {
			if i > 2 {
				break JumpLoop
			}
			fmt.Println(i)
			if j == 2 {
				continue
			}
		}
	}
}
```

`for-range`
可以遍歷數組、切片、字符串、map和channel。

```go
for key, val := range 復合變量值 {
	//val對應索引值的復制值，只讀。
	//修改val值，不會影響原有集合中的值。
}
for position, runeChar := range str {
	//
}
package main

import (
	"fmt"
)

func main() {
	//遍歷數組、切片
	for key, value := range []int{0, 1, -1, -2} {
		fmt.Printf("key:%d value:%d\n", key, value)
	}

	//遍歷字符串
	var str = "hi 加油"
	for key, value := range str {
		fmt.Printf("key:%d value:0x%x\n", key, value)
	}

	//遍歷map
	m1 := map[string]int{
		"go":  100,
		"web": 100,
	}
	//輸出無序
	for key, value := range m1 {
		fmt.Printf(key, value)
	}

	//遍歷通道
	c := make(chan int)
	go func() {
		c <- 7
		c <- 8
		c <- 9
		close(c)
	}()
	for v := range c {
		fmt.Println(v)
	}

	//_匿名變量，佔位符，不參與空間分配，也不佔用變量名字。
	m2 := map[string]int{
		"go":  100,
		"web": 100,
	}
	for _, v := range m2 {
		fmt.Println(v)
	}
	for key, _ := range []int{0, 1, -1, -2} {
		fmt.Printf("key:%d\n", key)
	}
}
```

`swith-case`
表達式不必為常量，甚至整數，不需通過break跳出，各case中類型一致。

```go
package main

import (
	"fmt"
)

func main() {
	var a = "love"
	switch a {
	default:
		fmt.Println("none")
	case "love":
		fmt.Println("love")
	case "programming":
		fmt.Println("programming")
	}
	switch a {
	default:
		fmt.Println("none")
	case "love", "programming":
		fmt.Println("find")
	}

	var r int = 6
	switch {
	case r > 1 && r < 10:
		fmt.Println(r)
	}
}
goto
package main

import (
	"fmt"
)

func main() {
	var isBreak bool
	for x := 0; x < 20; x++ {
		for y := 0; y < 20; y++ {
			if y == 2 {
				isBreak = true
				break
			}
		}
		if isBreak {
			break
		}
	}
	fmt.Println("over")
}
package main

import (
	"fmt"
)

func main() {
	for x := 0; x < 20; x++ {
		for y := 0; y < 20; y++ {
			if y == 2 {
				goto breakTag
			}
		}
	}
breakTag:
	fmt.Println("over")
}
```

goto在`多錯誤處理`中優勢

```go
func main() {
	err := getUserInfo()
	if err != nil {
		fmt.Println(err)
		exitProcess()
	}

	err = getEmail()
	if err != nil {
		fmt.Println(err)
		exitProcess()
	}
	
	fmt.Println("over")
}
func main() {
	err := getUserInfo()
	if err != nil {
		goto doExit
	}

	err = getEmail()
	if err != nil {
		goto doExit
	}
	
	fmt.Println("over")
	return

doExit:
	fmt.Println(err)
	exitProcess()
}
```

## 1.4 Go數據類型

| 類型       | 說明                                                         |
| ---------- | ------------------------------------------------------------ |
| 布爾型     | true或false                                                  |
| 數字類型   | uint8、uint16、uint32、uint64、int8、int16、int32、int64 、float32（IEEE-754）、float64（IEEE-754）、complex64、complex128、byte（uint8）、rune（int32）、uint（32或64）、int（32或64）、uintptr（存放指針） |
| 字符串類型 | 一串固定長度的字符連接起來的字符序列，utf-8編碼              |
| 復合類型   | 數組、切片、map、結構體                                      |

### 1.4.1 布爾型

只有兩個相同類型的值才能比較：

- 值的類型是接口（interface），兩者必須都實現了相同的接口。
- 一個是常量，另一個不是常量，類型必須和常量類型相同。
- 類型不同，必須轉換為相同類型，才能比較。

&&優先級高於||，有短路現象。

```go
package main

import (
	"fmt"
)

func bool2int(b bool) int {
	if b {
		return 1
	} else {
		return 0
	}
}

func int2bool(i int) bool { return i != 0 }

func main() {
	fmt.Println(bool2int(true))
	fmt.Println(int2bool(0))
}
```

### 1.4.2 數字類型

位運算採用補碼。int、uint和uintptr，長度由操作系統類型決定。

### 1.4.3 字符串類型

由一串固定長度的字符連接起來的字符序列，utf-8編碼。值類型，字節的定長數組。

```go
//聲明和初始化
str := "string"
```

字符串字面量用"或`創建

- "創建可解析的字符串，支持轉義，不能引用多行
- `創建原生的字符串字面量，不支持轉義，可多行，不能包含反引號字符

```go
str1 := "\"hello\"\nI love you"
str2 := `"hello"
I love you
`
//字符串連接
str := "I love" + " Go Web"
str += " programming"
package main

import (
	"fmt"
	"unicode/utf8"
)

func main() {
	str := "我喜歡Go Web"
	fmt.Println(len(str))
	fmt.Println(utf8.RuneCountInString(str))
	fmt.Println(str[9])
	fmt.Println(string(str[9]))
	fmt.Println(str[:3])
	fmt.Println(string(str[:3]))
	fmt.Println(str[3:])
	fmt.Println([]rune(str))
}
package main

import (
	"fmt"
)

func main() {
	str := "我喜歡Go Web"
	chars := []rune(str)
	for ind, char := range chars {
		fmt.Printf("%d: %s\n", ind, string(char))
	}
	for ind, char := range str {
		fmt.Printf("%d: %s\n", ind, string(char))
	}
	for ind, char := range str {
		fmt.Printf("%d: %U %c\n", ind, char, char)
	}
}
var buffer bytes.Buffer
for {
	if piece, ok := getNextString(); ok {
		buffer.WriteString(piece)
	} else {
		break
	}
}
fmt.Println(buffer.String())
```

不能通過str[i]方式修改字符串中的字符。
只能將字符串內容復制到可寫變量（[]byte或[]rune），然後修改。轉換類型過程中會自動復制數據。

```go
str := "hi 世界"
by := []byte(str)
by[2] = ','
fmt.Printf("%s\n", str)
fmt.Printf("%s\n", by)
fmt.Printf("%s\n", string(by))
str := "hi 世界"
by := []rune(str)
by[3] = '中'
by[4] = '國'
fmt.Println(str)
fmt.Println(by)
fmt.Println(string(by))
```

### 1.4.4 指針類型

指針類型指存儲內存地址的變量類型。

```go
var b int = 66
var p * int = &b
package main

import (
	"fmt"
)

func main() {
	var score int = 100
	var name string = "barry"
	fmt.Printf("%p %p\n", &score, &name)
}
package main

import (
	"fmt"
)

func main() {
	var address string = "hangzhou, China"
	ptr := &address
	
	fmt.Printf("address type: %T\n", address)
	fmt.Printf("address value: %v\n", address)
	fmt.Printf("address address: %p\n", &address)
	
	fmt.Printf("ptr type: %T\n", ptr)
	fmt.Printf("ptr value: %v\n", ptr)
	fmt.Printf("ptr address: %p\n", &ptr)
	fmt.Printf("point value of ptr : %v\n", *ptr)
}
package main

import (
	"fmt"
)

func exchange1(c, d int) {
	t := c
	c = d
	d = t
}

func exchange2(c, d int) {
	c, d = d, c
}

func exchange3(c, d *int) {
	t := *c
	*c = *d
	*d = t
}

func exchange4(c, d *int) {
	d, c = c, d
}

func exchange5(c, d *int) {
	*d, *c = *c, *d
}

func main() {
	x, y := 6, 8
	x, y = y, x
	fmt.Println(x, y)

	x, y = 6, 8
	exchange1(x, y)
	fmt.Println(x, y)
	
	x, y = 6, 8
	exchange2(x, y)
	fmt.Println(x, y)
	
	x, y = 6, 8
	exchange3(&x, &y)
	fmt.Println(x, y)
	
	x, y = 6, 8
	exchange4(&x, &y)
	fmt.Println(x, y)
	
	x, y = 6, 8
	exchange5(&x, &y)
	fmt.Println(x, y)
}
```

### 1.4.5 復合類型

1. 數組類型

數組是具有相同類型（整數、字符串、自定義類型等）的一組長度固定的數據項的序列。

```go
var array [10]int
var numbers = [5]float32{100.0, 8.0, 9.4, 6.8, 30.1}
var numbers = [...]float32{100.0, 8.0, 9.4, 6.8, 30.1}
package main

import (
	"fmt"
)

func main() {
	var arr [6]int
	var i, j int
	for i = 0; i < 6; i++ {
		arr[i] = i + 66
	}
	for j = 0; j < 6; j++ {
		fmt.Printf("arr[%d] = %d\n", j, arr[j])
	}
}
```

1. 結構體類型

結構體是由0或多個任意類型的數據構成的數據集合。

```go
type 類型名 struct {
	字段1 類型1
	結構體成員2 類型2
}
type Pointer struct {
	A float32
	B float32
}

type Color struct {
	Red, Green, Blue byte
}

variable_name := struct_variable_type {value1, value2, ...}
variable_name := struct_variable_type {key2: value2, key1: value1, ...}
package main

import "fmt"

type Book struct {
	title string
	author string
	subject string
	press string
}

func main() {
	fmt.Println(Book{author: "yx", title: "學習 Go Web"})
	
	var bookGo Books
	bookGo.title = "學習 Go Web"
	bookGo.author = "yx"
	bookGo.subject = "Go"
	bookGo.press = "電力工業出版社"
	fmt.Printf("bookGo.title: %s\n", bookGo.title)
	fmt.Printf("bookGo.author: %s\n", bookGo.author)
	fmt.Printf("bookGo.subject: %s\n", bookGo.subject)
	fmt.Printf("bookGo.press: %s\n", bookGo.press)
	printBook(bookGo)
	printBook(&bookGo)
}

func printBook(book Books) {
	fmt.Printf("book.title: %s\n", book.title)
	fmt.Printf("book.author: %s\n", book.author)
	fmt.Printf("book.subject: %s\n", book.subject)
	fmt.Printf("book.press: %s\n", book.press)
}

func printBook2(book *Books) {
	fmt.Printf("book.title: %s\n", book.title)
	fmt.Printf("book.author: %s\n", book.author)
	fmt.Printf("book.subject: %s\n", book.subject)
	fmt.Printf("book.press: %s\n", book.press)
}
```

1. 切片類型

slice是對數組或切片連續片段的引用。
切片內部結構包含內存地址pointer、大小len和容量cap。

```go
//不含結束位置
slice[開始位置:結束位置]
var sliceBuilder [20]int
for i := 0; i < 20; i++ {
	sliceBuilder[i] = i + 1
}
fmt.Println(sliceBuilder[5:15])
fmt.Println(sliceBuilder[15:])
fmt.Println(sliceBuilder[:2])
b := []int{6, 7, 8}
fmt.Println(b[:])
fmt.Println(b[0:0])
var sliceStr []string
var sliceNum []int
var emptySliceNum = []int{}
fmtp.Println(sliceStr, sliceNum, emptySliceNum)
fmtp.Println(len(sliceStr), len(sliceNum), (emptySliceNum))
fmtp.Println(sliceStr == nil, sliceNum == nil, emptySliceNum == nil)
slice1 := make([]int, 6)
slice2 := make([]int, 6, 10)
fmtp.Println(slice1, slice2)
fmtp.Println(len(slice1), len(slice2))
fmtp.Println(cap(slice1), cap(slice2))
```

1. map類型

關聯數組，字典，元素對（pair）的無序集合，引用類型。

```go
var name map[key_type]value_type
var literalMap map[string]string
var assignedMap map[string]string
literalMap = map[string]string{"first": "go", "second": "web"}
createdMap := make(map[string]float32)
assignedMap = literalMap	//引用
createdMap["k1"] = 99
createdMap["k2"] = 199
assignedMap["second"] = "program"

fmt.Println(literalMap["first"])
fmt.Println(literalMap["second"])
fmt.Println(literalMap["third"])
fmt.Println(createdMap["k2"])
createdMap := new(map[string]float32)
//錯誤
//聲明瞭一個未初始化的變量並取了它的地址
//map到達容量上限，自動增1
make(map[key_type]value_type, cap)
map := make(map[string]float32, 100)

achievement := map[string]float32{
	"zhang": 99.5, "xiao": 88,
	"wange": 96, "ma": 100,
}
map1 := make(map[int][]int)
map2 := make(map[int]*[]int)
```

## 1.5 函數

### 1.5.1 聲明函數

```go
func function_name([parameter list]) [return_types] {
	//bunction_body
}
package main

import "fmt"

func main() {
	array := []int{6, 8, 10}
	var ret int
	ret = min(array)
	fmt.Println("最小值是: %d\n", ret)
}

func min(arr []int) (m int) {
	m = arr[0]
	for _, v := range arr {
		if v < m {
			m = v
		}
	}
	return
}
package main

import "fmt"

func compute(x, y int) (int, int) {
	return x+y, x*y
}
func main() {
	a, b := compute(6, 8)
	fmt.Println(a, b)
}
package main

import "fmt"

func change(a, b int) (x, y int) {
	x = a + 100
	y = b + 100
	return
	//return x, y
	//return y, x
}
func main() {
	a := 1
	b := 2
	c, d := compute(a, b)
	fmt.Println(c,d)
}
```

### 1.5.2 函數參數

1. 參數使用

- 形參：定義函數時，用於接收外部傳入的數據。
- 實參：調用函數時，傳給形參的實際的數據。

1. 可變參數

```go
func myFunc(arg ...string) {
	for _, v := range arg {
		fmt.Printf("the string is: %s\n", v)
	}
}
```

1. 參數傳遞

- 值傳遞

```go
package main

import "fmt"

func exchange(a, b int) {
	var tmp int
	tmp = a
	a = b
	b = tmp
}
func main() {
	a := 1
	b := 2
	fmt.Printf("交換前a=%d\n", a)
	fmt.Printf("交換前b=%d\n", b)
	exchange(a, b)
	fmt.Printf("交換後a=%d\n", a)
	fmt.Printf("交換後b=%d\n", b)
}
```

- 引用傳遞

```go
package main

import "fmt"

func exchange(a, b *int) {
	var tmp int
	tmp = *a
	*a = *b
	*b = tmp
}
func main() {
	a := 1
	b := 2
	fmt.Printf("交換前a=%d\n", a)
	fmt.Printf("交換前b=%d\n", b)
	exchange(&a, &b)
	fmt.Printf("交換後a=%d\n", a)
	fmt.Printf("交換後b=%d\n", b)
}
```

### 1.5.3 匿名函數

匿名函數（閉包），一類無須定義標識符（函數名）的函數或子程序。

1. 定義

```go
func (參數列表) (返回值列表) {
	//函數體
}
package main

import "fmt"

func main() {
	x, y := 6, 8
	defer func(a int) {
		fmt.Println("defer x, y = ", a, y) //y為閉包引用
	}(x)
	x += 10
	y += 100
	fmt.Println(x, y)
}
/*
輸出
16 108
defer x,y = 6 108
*/
```

1. 調用

- 定義時調用

```go
package main

import "fmt"

func main() {
	//定義匿名函數並賦值給f變量
	f := func(data int) {
		fmt.Println("closure", data)
	}
	f(6)

	//直接聲明並調用
	func(data int) {
		fmt.Println("closure, directly", data)
	}(8)
}
```

- 回調函數（call then back）

```go
package main

import "fmt"

func visitPrint(list []int, f func(int)) {
	for _, value := range list {
		f(value)
	}
}

func main() {
	sli := []int{1, 6, 8}
	visitPrint(sli, func(value int) {
		fmt.Println(value)
	})
}
```

### 1.5.4 defer延遲語句

defer用於函數結束（return或panic）前最後執行的動作，便於及時的釋放資源（數據庫連接、文件句柄、鎖等）。

defer語句執行邏輯：

1. 函數執行到defer時，將defer後的語句壓入專門存儲defer語句的棧中，然後繼續執行函數下一個語句。
2. 函數執行完畢，從defer棧頂依次取出語句執行（先進後出，後進先出）。
3. defer語句放在defer棧時，相關值會復制入棧中。

```go
package main

import "fmt"

func main() {
	deferCall()
}

func deferCall() {
	defer func1()
	defer func2()
	defer func3()
}

func func1() {
	fmt.Println("A")
}

func func2() {
	fmt.Println("B")
}

func func3() {
	fmt.Println("C")
}

//輸出
//C
//B
//A
package main

import "fmt"

var name string = "go"

func myfunc() string {
	defer func() {
		name = "python"	//最後一個動作，修改全局變量name為"python"
	}()

	fmt.Printf("myfunc()函數裡的name: %s\n", name)//全局變量name（"go"）未修改
	return name	//倒數第二個動作，將全局變量name（"go"）賦值給myfunc函數返回值
}

func main() {
	myname := myfunc()
	fmt.Printf("main()函數裡的name: %s\n", name)
	fmt.Printf("main()函數裡的myname: %s\n", myname)
}

//輸出
//myfunc()函數裡的name: go
//main()函數裡的name: python
//main()函數裡的myname: go
```

defer常用應用場景：

1. 關閉資源。
   創建資源（數據庫連接、文件句柄、鎖等）語句下一行，defer語句註冊關閉資源，避免忘記。
2. 和recover()函數一起使用。
   程序宕機或panic時，recover()函數恢復執行，而不報錯。

```go
func f() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered in f", r)
        }
    }()	//func()函數含recover，不可封裝成外部函數調用，必須defer func(){}()匿名函數調用
    fmt.Println("Calling g.")
    g(0)
    fmt.Println("Returned normally from g.")
}

func g(i int) {
    if i > 3 {
        fmt.Println("Panicking!")
        panic(fmt.Sprintf("%v", i))
    }
    defer fmt.Println("Defer in g", i)
    fmt.Println("Printing in g", i)
    g(i + 1)
}
```

## 1.6 Go面向對象編程

### 1.6.1 封裝

隱藏對象屬性和實現細節，僅公開訪問方式。
Go使用結構體封裝屬性。

```go
type Triangle struct {
	Bottom float32
	Height float32
}
```

方法（Methods）是作用在接收者（receiver）（某種類型的變量）上的函數。

```go
func (recv recv_type) methodName(parameter_list) (return_value_list) {...}
package main

import "fmt"

type Triangle struct {
	Bottom float32
	Height float32
}

func (t *Triangle) Area() float32 {
	return (t.Bottom * t.Height) / 2
}

func main() {
	t := Triangle(6, 8)
	fmt.Println(t.Area())
}
```

訪問權限指類屬性是公開還是私有的，Go通過首字母大小寫來控制可見性。
常量、變量、類型、接口、結構體、函數等若是大寫字母開頭，則能被其他包訪問或調用（public）；非大寫開頭則只能包內使用（private）。

```go
package person
type Student struct {
	name string
	score float32
	Age int
}

package pkg
import (
	person
	"fmt"
)
s := new(person.Student)
s.name = "yx" //錯誤
s.Age = 22
fmt.Println(s.Age)
package person

type Student struct {
	name string
	score float32
}

func (s *Student) GetName() string {
	return s.name
}

func (s *Student) SetName(newName string) {
	s.name = newName
}

package main

import (
	person
	"fmt"
)

func main() {
	s := new(person.Student)
	s.SetName("yx")
	s.Age = 22
	fmt.Println(s.GetName())
}
```

### 1.6.2 繼承

結構體中內嵌匿名類型的方法來實現繼承。

```go
type Engine interface {
	Run()
	Stop()
}

type Bus struct {
	Engine
}

func (c *Bus) Working() {
	c.Run()
	c.Stop()
}
```

### 1.6.3 多態

多態指不同對象中同種行為的不同實現方法，通過接口實現。

```go
package main

import (
	"fmt"
)

type Shape interface {
	Area() float32
}

type Square struct {
	sideLen float32
}

func (sq *Square) Area() float32 {
	return sq.sideLen * sq.sideLen
}

type Triangle struct {
	Bottom float32
	Height float32
}

func (t *Triangle) Area() float32 {
	return t.Bottom * t.Height
}

func main() {
	t := &Tri8angle{6, 8}
	s := &Square{}
	shapes := []Shape{t, s}
	for n, _ := range shapes {
		fmt.Println("圖形數據：", shapes[n])
		fmt.Println("面積：", shapes[n].Area())
	}
}
```

## 1.7 接口

### 1.7.1 接口定義

接口類型是對其他類型行為的概括與抽象，定義了零及以上個方法，但沒具體實現這些方法。
接口本質上是指針類型，可以實現多態。

```go
//接口定義格式
type 接口名稱 interface {
	method1(參數列表) 返回值列表
	method2(參數列表) 返回值列表
	//...
	methodn(參數列表) 返回值列表
}
```

空接口（interface{}），無任何方法聲明，類似面向對象中的根類型，c中的void*，默認值nil。實現接口的類型支持相等運算，才能比較。

```go
var var1, var2 interface{}
fmt.Println(var1 == nil, var1 == var2)
var1, var2 = 66, 88
fmt.Println(var1 == var2)
//比較map[string]interface{}
func CompareTwoMapInterface(data1 map[string]interface{}, data2 map[string]interface{}) bool {
	keySlice := make([]string, 0)
	dataSlice1 := make([]interface{}, 0)
	dataSlice2 := make([]interface{}, 0)
	for key, value := range data1 {
		keySlice = append(keySlice, key)
		dataSlice1 = append(dataSlice1, value)
	}
	for _, key := range keySlice {
		if data, ok := data2[key]; ok {
			dataSlice2 = append(dataSlice2, data)
		} else {
			return false
		}
	}
	dataStr1, _ := json.Marshal(dataSlice1)
	dataStr2, _ := json.Marshal(dataSlice2)

	return string(dataStr1) == string(dataStr2)
}
```

### 1.7.2 接口賦值

接口不支持直接實例化，但支持賦值操作。

1. 實現接口的對象實例賦值給接口

要求該對象實例實現了接口的所有方法。

```go
type Num int

func (x Num) Equal(i Num) bool {
	return x == i
}

func (x Num) LessThan(i Num) bool {
	return x < i
}

func (x Num) MoreThan(i Num) bool {
	return x > i
}

func (x *Num) Multiple(i Num) {
	*x = *x * i
}

func (x *Num) Divide(i Num) {
	*x = *x / i
}

type NumI interface {
	Equal(i Num) bool
	LessThan(i Num) bool
	MoreThan(i Num) bool
	Multiple(i Num)
	Divide(i Num)
}

//&Num實現NumI所有方法
//Num未實現NumI所有方法
var x Num = 8
var y NumI = &x

/*
Go語言會根據非指針成員方法，自動生成對應的指針成員方法
func (x Num) Equal(i Num) bool
func (x *Num) Equal(i Num) bool
*/
```

1. 一個接口賦值給另一個接口

兩個接口擁有相同的方法列表（與順序無關），則等同，可相互賦值。

```go
package oop1

type NumInterface1 interface {
	Equal(i int) bool
	LessThan(i int) bool
	BiggerThan(i int) bool
}

package oop2

type NumInterface2 interface {
	Equal(i int) bool
	BiggerThan(i int) bool
	LessThan(i int) bool
}

type Num int

//int不能改為Num
func (x Num) Equal(i int) bool {
	return int(x) == i
}

func (x Num) LessThan(i int) bool {
	return int(x) < i
}

func (x Num) BiggerThan(i int) bool {
	return int(x) > i
}

var f1 Num = 6
var f2 oop1.NumInterface1 = f1
var f3 oop2.NumInterface2 = f2
```

若接口A的方法列表是接口B的方法列表的子集，則接口B可以直接賦值給接口A。

```go
type NumInterface1 interface {
	Equal(i int) bool
	LessThan(i int) bool
	BiggerThan(i int) bool
}

type NumInterface2 interface {
	Equal(i int) bool
	BiggerThan(i int) bool
	LessThan(i int) bool
	Sum(i int)
}

type Num int

func (x Num) Equal(i int) bool {
	return int(x) == i
}

func (x Num) LessThan(i int) bool {
	return int(x) < i
}

func (x Num) BiggerThan(i int) bool {
	return int(x) > i
}

func (x *Num) Sum(i int) {
	*x = *x + Num(i)
}

var f1 Num = 6
var f2 NumInterface2 = &f1
var f3 NumInterface1 = f2
```

### 1.7.3 接口查詢

程序運行時，詢問接口指向的對像是否時某個類型。

```go
var filewriter Write = ...
if filew, ok := filewriter.(*File); ok {
	//...
}
slice := make([]int, 0)
slice = append(slice, 6, 7, 8)
var I interface{} = slice
if res, ok := I.([]int); ok {
	fmt.Println(res) //[6 7 8]
	fmt.Println(ok) //true
}
func Len(array interface{}) int {
	var length int
	
	switch b := array.(type) {
	case nil:
		length = 0
	case []int:
		length = len(b)
	case []string:
		length = len(b)
	case []float32:
		length = len(b)
	default:
		length = 0
	}
	return length
}
```

### 1.7.4 接口組合

接口間通過嵌套創造出新接口。

```go
type Interface1 interface {
	Write(p []byte) (n int, err error)
}

type Interface2 interface {
	Close() error
}

type InterfaceCombine interface {
	Interface1
	Interface2
}
```

### 1.7.5 接口應用

1. 類型推斷

類型推斷可將接口還原為原始類型，或用來判斷是否實現了某種更具體的接口類型。

```go
package main

import "fmt"

func main() {
	var a interface{} = func(a int) string {
		rteurn fmt.Sprintf("d:%d", a)
	}
	
	switch b := a.(type) {
	case nil:
		fmt.Println("nil")
	case *int:
		fmt.Println(*b)
	case func(int) string:
		fmt.Println(b(66))
	case fmt.Stringer:
		fmt.Println(b)
	default:
		fmt.Println("unknown")
	}
}
```

1. 實現多態功能

```go
package main

import "fmt"

type Message interface {
	sending()
}

type User struct {
	name string
	phone string
}

func (u *User) sending() {
	fmt.Printf("Sending user phone to %s<%s>\n", u.name, u.phone)
}

type admin struct {
	name string
	phone string
}

func (a *admin) sending() {
	fmt.Printf("Sending admin phone to %s<%s>\n", a.name, a.phone)
}

func main() {
	bill := User{"Barry", "barry@gmail.com"}
	sendMessage(&bill)
	
	lisa := admin{"Barry", "barry@gmail.com"}
	sendMessage(&lisa)
}

func sendMessage(n Message) {
	n.sending()
}
```

## 1.8 反射

### 1.8.1 反射的定義

反射指，編譯時不知道變量的具體類型，運行時（Run time）可以訪問、檢測和修改狀態或行為的能力。

reflect包定義了接口和結構體，獲取類型信息。

- reflect.Type接口提供類型信息
- reflect.Value結構體提供值相關信息，可以獲取甚至改變類型的值

```go
func TypeOf(i interface{}) Type
func ValueOf(i interface{}) Value
```

### 1.8.2 反射的三大法則

1. 接口類型變量轉換為反射類型對象

```go
package main

import (
	"fmt"
	"reflect"
)

func main() {
	var x float64 = 3.4
	fmt.Println("type:", reflect.TypeOf(x))
	fmt.Println("value:", reflect.ValueOf(x))
	
	v := reflect.ValueOf(x)
	fmt.Println("type:", v.Type())
	fmt.Println("kind is float64:", v.Kind() == reflect.Float64)
	fmt.Println("value:", v.Float())
}
//輸出
//type: float64
//value: 3.4
//kind is float64: true
//type: float64
//value: 3.4
```

1. 反射類型對象轉換為接口類型變量

```go
func (v Value) Interface() interface{}
y := v.Interface().(float64)
fmt.Println(y)
package main

import (
	"fmt"
	"reflect"
)

func main() {
	var name interface{} = "shirdon"
	fmt.Printf("原始接口變量類型為%T，值為%v\n", name, name)
	
	t := reflect.TypeOf(name)
	v := reflect.ValueOf(name)
	fmt.Printf("Type類型為%T，值為%v\n", t, t)
	fmt.Printf("Value類型為%T，值為%v\n", v, v)
	
	i := v.Interface()
	fmt.Printf("新對象interface{}類型為%T，值為%v\n", i, i)
}
//輸出
//原始接口變量類型為string，值為shirdon
//Type類型為*reflect.rtype，值為string
//Value類型為reflect.Value，值為shirdon
//新對象interface{}類型為string，值為shirdon
```

1. 修改反射類型對象，其值必須是可寫的（settable）

reflect.TypeOf()和reflect.ValueOf()函數中若傳遞的不是指針，則只是變量復制，對該反射對象修改，不會影響原始變量。
反射對象可寫性要點:

- 變量指針創建的反射對象
- CanSet()可判斷
- Elem()返回指針指向的數據

```go
package main

import (
	"fmt"
	"reflect"
)

func main() {
	var name string = "shirdon"
	//var name int = 12
	
	v1 := reflect.ValueOf(&name)
	v2 := v1.Elem()
	fmt.Println("可寫性:", v1.CanSet())
	fmt.Println("可寫性:", v2.CanSet())
}

//輸出
//可寫性：false
//可寫性：true
func (v Value) SetBool(x bool)
func (v Value) SetBytes(x []byte)
func (v Value) SetFloat(x float64)
func (v Value) SetInt(x int64)
func (v Value) SetString(x string)
package main

import (
	"fmt"
	"reflect"
)

func main() {
	var name string = "shirdon"
	fmt.Println("name原始值:", name)
	
	v1 := reflect.ValueOf(&name)
	v2 := v1.Elem()
	
	v2.SetString("yx")
	fmt.Println("反射對象修改後，name值:", name)
}

//輸出
//name原始值: shirdon
//反射對象修改後，name值: yx
```

## 1.9 goroutine簡介

每一個並發執行的活動叫goroutine。

```go
go func_name()
package main

import (
	"fmt"
	"time"
)

func hello() {
	fmt.Println("hello")
}

func main() {
	go hello()
	time.Sleep(1*time.Second)
	fmt.Println("end")
}
```

## 1.10 單元測試（go test）

testing庫，*_test.go文件。

```go
//sum.go
package testexample

func Min(arr []int) (min int) {
	min = arr[0]
	for _, v := range arr {
		if v < min {
			min = v
		}
	}
	return
}

//sum_test.go
package testexample

import (
	"fmt"
	"testing"
)

func TestMin(t *testing.T) {
	array := []int{6, 8, 10}
	ret := Min(array)
	fmt.Println(ret)
}

//go test
//go test -v
//go test -v -run="Test"
```

| 參數 | 作用                                           |
| ---- | ---------------------------------------------- |
| -v   | 打印每個測試函數的名字和運行時間               |
| -c   | 生成測試可執行文件，但不執行，默認命名pkg.test |
| -i   | 重新安裝運行測試依賴包，但不編譯和運行測試代碼 |
| -o   | 指定生成測試可執行文件的名稱                   |

## 1.11 Go編譯與工具

### 1.11.1 編譯（go build）

```go
//build
//----main.go
//----utils.go

//main.go
package main

import (
	"fmt"
)

func main() {
	printString()
	fmt.Println("go build")
}

//utils.go
package main

import "fmt"

func printString() {
	fmt.Println("test")
}

//cd build
//go build
//go build main.go utils.go
//go build -o file.exe main.go utils.go
//pkg
//----mainpkg.go
//----buildpkg.go

//mainpkg.go
package main

import (
	"fmt"
	"pkg"
)

func main() {
	pkg.CallFunc()
	fmt.Println("go build")
}

//buildpkg.go
package pkg

import "fmt"

func CallFunc() {
	fmt.Println("test")
}
//go build .../pkg
//compile.go
package main

import (
	"fmt"
)

func main() {
	fmt.Println("go build")
}
//CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build compile.go
```

- CGO_ENABLED: 是否使用C語言的Go編譯器；
- GOOS：目標操作系統
- GOARCH：目標操作系統的架構

| 系統編譯參數                      | 架構              |
| --------------------------------- | ----------------- |
| linux(>=Linux 2.6)                | 386 / amd64 / arm |
| darwin(OS X(Snow Lepoard + Lion)) | 386 / amd64       |
| freebsd(>=FreeBSD 7)              | 386 / amd64       |
| windows(>=Windows 2000)           | 386 / amd64       |

| 附加參數 | 作用                                     |
| -------- | ---------------------------------------- |
| -v       | 編譯時顯示包名                           |
| -p n     | 開啟並發編譯，默認值為CPU邏輯核數        |
| -a       | 強制重新構建                             |
| -n       | 打印編譯時會用到的所有命令，但不真正執行 |
| -x       | 打印編譯時會用到的所有命令               |
| -race    | 開啟競態檢測                             |

### 1.11.2 編譯後運行（go run）

編譯後直接運行，且無可執行文件。

```go
//hello.go
package main

import (
	"fmt"
)

func main() {
	fmt.Println("go run")
}
//go run hello.go
```

### 1.11.3 編譯並安裝（go install）

類似go build，只是編譯中間文件放在$GOPATH/pkg目錄下，編譯結果放在$GOPATH/bin目錄下。

```go
//install
//|----main.go
//|----pkg
//    |----installpkg.go

//main.go
package main

import (
	"fmt"
	"pkg"
)

func main() {
	pkg.CallFunc()
	fmt.Println("go build")
}

//installpkg.go
package pkg

import "fmt"

func CallFunc() {
	fmt.Println("test")
}
//go install
```

### 1.11.4 獲取代碼（go get）

動態遠程拉取或更新代碼包及其依賴包，自動完成編譯和安裝。需要安裝Git，SVN，HG等。

| 標記名稱  | 標記描述                                                     |
| --------- | ------------------------------------------------------------ |
| -d        | 只下載，不安裝                                               |
| -f        | 使用-u時才有效，忽略對已下載代碼包導入路徑的檢查。適用於從別人處Fork代碼包 |
| -fix      | 下載代碼包後先修正，然後編譯和安裝                           |
| -insecure | 運行非安全scheme(如HTTP)下載代碼包。                         |
| -t        | 同時下載測試源碼文件中的依賴代碼包                           |
| -u        | 更新已有代碼包及其依賴包                                     |

```go
go get -u github.com/shirdon1/TP-Link-HS110
```