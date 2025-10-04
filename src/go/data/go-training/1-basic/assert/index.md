# 類型斷言
Golang中有一種interface{}可以代表任意類型，使用起來非常靈活。不過我們有的時候需要知道它到底包含的是啥類型的對象，這時候就需要用到類型斷言了

```go  
//類型斷言用法1
var c interface{} = 10
switch c.(type) {
case int:
    fmt.Println("int")
case float32:
    fmt.Println("string")
}

//類型斷言用法2
var d interface{} = 10
t1, ok := d.(int)
if ok {
    fmt.Println("int", t1)
}
t2, ok := d.(float32)
if ok {
    fmt.Println("float32", t2)
}
```
