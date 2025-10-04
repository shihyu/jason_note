# Map

**1.map的定義與元素添加**  
使用make來創建map。  
```go  
m1 := make(map[string]int)
m1["key1"] = 1
m1["key2"] = 2
fmt.Println(m1) //map[key1:1 key2:2]
```

**2.判斷key是否存在**  
通過 key 作為索引下標來訪問 map，如果 key 不存在，那麼將得到 value 對應類型的零值，比如nil、''、false 和 0，取值操作總會有值返回。判斷key是否存在可以通過第二個參數來判斷，如下：  
```go  
value, ok := m1["key2"]
if ok {
    fmt.Println("key2", value)
}
```
**3.map元素刪除**  
golang提供了內建函數 delete() 從 map 中刪除一組鍵值對。  
```go  
delete(m1, "key2")
```
**4.map元素遍歷**  
使用 for range 遍歷 map，遍歷的順序是隨機的，每一次遍歷的順序都不相同，與添加鍵值對的順序無關。
```go  
for k, v := range m1 {
    fmt.Println(k, v)
}
```
