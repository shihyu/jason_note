Golang 中包含三種類型的指針
- 普通指針
- 內置指針類型uintptr,是一個無符號整數，用來保存一個指針地址
- unsafe.Pointer，可以指向任意類型的指針

# 一、普通指針
**指針的聲明、賦值、訪問**  
有過C編程經驗的同學對指針可是太熟系不過了。Golang中的指針和C中概念差不多，不過在使用上要簡單不少。

```go  
//聲明
var n int = 20
var pn *int

//空指針判斷
if nil == pn {
    fmt.Println("這是一個空指針哦！")
}

//指針賦值
pn = &n
fmt.Println("變量n的地址是:", pn)

//使用指針訪問值
fmt.Printf("%d\n", *pn)
```

**指針作為函數的參數**  
如果在函數中需要修改參數的值的話，可能就需要通過指針來進行傳遞了。

```go  
package main

import "fmt"

func swap1(n1 int, n2 int) {
	nTemp := n2
	n2 = n1
	n1 = nTemp
}

func swap2(n1 *int, n2 *int) {
	var nTemp int
	nTemp = *n2
	*n2 = *n1
	*n1 = nTemp
}

func main() {
	var n1 int = 100
	var n2 int = 200
    
    //不使用指針無法在函數中修改n1,n2的值
	swap1(n1, n2)
	fmt.Println("n1:", n1, "\tn2:", n2)

    //使用指針作為參數，才能成功交換n1,n2的值
	swap2(&n1, &n2)
	fmt.Println("n1:", n1, "\tn2:", n2)
}
```

## 二、uintptr與unsafe.Pointer

uintptr可以進行偏移操作，通過uintptr + offset進行算術運算
unsafe.Pointer做的主要是用來進行橋接，用於不同類型的指針進行互相轉換

uintptr和unsafe.Pointer之間可以互相轉換

例如如果想對指針進行偏移操作，可以按如下的方式進行：
```go
p = unsafe.Pointer(uintptr(p) + offset)
```


## 參考
- [Golang學習筆記--unsafe.Pointer和uintptr](https://studygolang.com/articles/33151)