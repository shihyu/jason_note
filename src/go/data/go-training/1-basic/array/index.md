# 數組
**1.數組的定義**  
var 數組變量名 [元素數量]類型  

```go  
var arr [10]int
```

**2.數組的初始化**  
```go  
var a [5]int                  //數組會初始化所有元素為 int 類型的零值，[0 0 0 0 0]
var b = [5]int{1, 2, 3, 4, 5}
var c = [...]int{1, 2, 3}
```

**3.數組的遍歷**
```go  
var a = [5]int{1, 2, 3, 4, 5}
for i := 0; i < len(a); i++ {
	fmt.Println(a[i])
}
var b = [5]int{1, 2, 3, 4, 5}
for index, value := range b {
	fmt.Println(index, value)
}
```

注意： 數組是值類型，賦值和傳參會複製整個數組，因此只改變副本的值，不會改變數組本身的值，想要在函數內部修改數組的值，可通過指針來傳遞數組參數。

# 切片

因為數組的長度是固定的，因此在 Go 語言中很少直接使用數組。  

slice 是一個擁有相同類型元素的可變長度的序列，它是基於數組類型做的一層封裝，功能更靈活，支持自動擴容和收縮。  

切片是一個引用類型，底層引用一個數組對象，它的內部結構包含指針址、長度和容量，指針指向第一個 slice 元素對應的底層數組元素的地址（slice 的第一個元素並不一定就是數組的第一個元素），長度對 應slice 中元素的數目，容量一般是從 slice 的開始位置到底層數據的結尾位置，長度不能超過容量。  

可以通過使用內置的 len() 函數求長度，使用內置的 cap() 函數求切片的容量。  

**1.切片的基本定義與初始化**
```go  
var s0 []int
s1 := []int{1, 2, 3}
fmt.Println(len(s0), cap(s0)) //0 0
fmt.Println(len(s1), cap(s1)) //3 3
```

**2.通過make創建切片,並用空值初始化**
```go  
s2 := make([]int, 3, 5)
fmt.Println(len(s2), cap(s2), s2) //3 5 [0 0 0]
```
	
**3.空切片判斷**
```go  
var s3 []int
if 0 == len(s3) {
    fmt.Println("This is a empty slice")
}
```

**4.為切片添加元素**
```go  
s4 := make([]int, 0, 5)
s4 = append(s4, 1)
s4 = append(s4, 1)
s4 = append(s4, 1)
fmt.Println(len(s4), cap(s4), s4) //3 5 [1 1 1]
```
**5.切片淺拷貝**  
在C++中有淺拷貝的概念，我們這裡沿用過來非常便於理解。

```go  
s5 := []int{1, 2, 3}
s6 := s5
s6[0] = 5
fmt.Println(s5) //[5 2 3]

//淺拷貝情況2
s7 := []int{1, 2, 3}
s8 := s7[1:]
s8[0] = 5
fmt.Println(s7) //[1 5 3]
fmt.Println(s8) //[5 3]
```

**6.切片深拷貝**
```go  
s9 := []int{1, 2, 3}
s10 := make([]int, 2, 5)
copy(s10, s9) //注意：只會拷貝到目標切片的len長度，超過的丟棄
s7[0] = 5
fmt.Println(s9)  //[1 2 3]
fmt.Println(s10) //[1 2]
```

**7.切片刪除**  
golang沒有直接的刪除功能，可以使用append來模擬

```go  
s11 := []int{1, 2, 3, 4, 5}
s11 = append(s11[:2], s11[3:]...)
fmt.Println(s11) //s11:[1 2 4 5]
```
	
