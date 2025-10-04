# 類型轉換
Golang是強類型語言，而且不會像C、C++那樣進行進行隱式類型轉換，如下的代碼會報錯

```go  
package main

import "fmt"

func main() {
    var a float32 = 5.6
    var b int = 10
    fmt.Println (a * b)
}
```

報錯如下
```go  
invalid operation: a * b (mismatched types float32 and int)
```

必須進行顯式的類型轉換才可以相乘
```go  
fmt.Println(a * float32(b))
```

