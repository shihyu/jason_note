
## []byte 到 string 的零拷貝

一般我們使用 string() 將 []byte 轉換為字符串
```
var b1 = []byte("hello123234349493053405")
s1 := string(b1[4:l])
```

但這樣設計到了內存拷貝，如果數組很大的話會浪費內存申請、內存拷貝開銷。
以下是一個零拷貝的函數

```
// BytesToString 零拷貝將[]byte轉換為字符串
func BytesToString(b []byte) string {
	// 獲取字節切片的底層結構指針
	sliceHeader := (*reflect.SliceHeader)(unsafe.Pointer(&b))

	// 構造字符串的底層結構，複用切片的Data和Len
	strHeader := reflect.StringHeader{
		Data: sliceHeader.Data + 4,
		Len:  sliceHeader.Len - 4,
	}

	// 將字符串結構指針轉換為string
	return *(*string)(unsafe.Pointer(&strHeader))
}
```

拷貝後，通過分別查看 slice 和 string 的header，可以確認其 Data 指向的是同一塊區域。

``` 
slice1Header := (*reflect.SliceHeader)(unsafe.Pointer(&b1))
fmt.Printf("byte array 1：%+v\n", slice1Header)
fmt.Println(unsafe.Pointer(slice1Header.Data))
fmt.Println(slice1Header.Len)
fmt.Println(slice1Header.Cap)

string1Header := (*reflect.StringHeader)(unsafe.Pointer(&s1))
fmt.Printf("byte array 2：%+v\n", string1Header)
fmt.Println(unsafe.Pointer(string1Header.Data))
fmt.Println(string1Header.Len)
```