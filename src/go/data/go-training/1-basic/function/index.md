# 函數
```go  
func 函數名(參數)(返回值){
    函數體
}
```
參數由參數變量和參數變量的類型組成，多個參數之間使用英文逗號,分隔，參數中如果相鄰變量的類型相同，則可以合併聲明只寫一個類型。

**1.變長參數**  
Go 語言中可通過在參數名後加...來標識變長參數，變長參數是指函數的參數數量不固定，變長參數通常作為函數的最後一個參數，本質上，函數的變長參數是通過切片來實現的。
```go  
package main
import "fmt"
func Greeting(who ...string) {
	fmt.Printf("%#v", who) //[]string{"Joe", "Anna", "Eileen"}
}
func main() {
	Greeting("Joe", "Anna", "Eileen")
}
```

**2.多個返回值**
返回值由返回值變量和其變量類型組成，也可以只寫返回值的類型，Go 語言中函數支持多返回值，多個返回值必須用()包裹，並用英文逗號,分隔；函數定義時可以給返回值命名，並在函數體中直接使用這些變量，最後通過 return 關鍵字返回。
```go  
func devide(a int, b int) (int, int) {
	var n1, n2 int
	n1 = a / b
	n2 = a % b
	return n1, n2
}

func main() {
	n1, n2 := devide(21, 10)
	fmt.Println(n1, n2)
}
```

# 匿名函數
匿名函數就是沒有函數名的函數，當我們不希望給函數起名字的時候，可以使用匿名函數，匿名函數不能夠獨立存在，它可以被賦值於某個變量或直接對匿名函數進行調用。 

```go  
// 將匿名函數保存到變量
add := func(x, y int) {
    fmt.Printf("The sum of %d and %d is: %d\n", x, y, x+y)
}
add(10, 20) // 通過變量調用匿名函數

// 直接對匿名函數進行調用，最後的一對括號表示對該匿名函數的直接調用執行
func(x, y int) {
    fmt.Printf("The sum of %d and %d is: %d\n", x, y, x+y)
}(10, 20)
```

# 閉包
閉包指的是一個函數和與其相關的引用環境組合而成的實體(即：閉包=函數+引用環境)。
```go  
// 函數 incr 返回了一個函數，返回的這個函數就是一個閉包。這個函數中本身是沒有定義變量 i 的，而是引用了它所在的環境（函數incr）中的變量 i。
func incr() func() int {
	var x int
	return func() int {
		x++
		return x
	}
}

func main() {
    // 這裡的 i 就成為了一個閉包，閉包對外層詞法域變量是引用的，即 i 保存著對 x 的引用。
    i := incr()
    fmt.Println(i()) // 1
    fmt.Println(i()) // 2
    fmt.Println(i()) // 3
    
    // 這裡調用了三次 incr()，返回了三個閉包，這三個閉包引用著三個不同的 x，它們的狀態是各自獨立的
    fmt.Println(incr()()) // 1
    fmt.Println(incr()()) // 1
    fmt.Println(incr()()) // 1
}

```