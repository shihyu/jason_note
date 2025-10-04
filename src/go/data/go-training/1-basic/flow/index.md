和c語言相比，golang對流程控制語句進行了一些精簡，比如省去了c裡面的括號。對於if/for都是。

# if/else
基本格式如下:
```go  
if condition {
    分支1
} else if condition {
    分支2
} else {
    分支3
}
```  

# for循環
```go  
for 初始語句;條件表達式;結束語句 {
    循環體語句
}
```

## 條件循環
```go
for i := 0; i < 10; i++ {
	fmt.Println(i)
}
```
## while循環
注意，golang沒有提供while循環，都統一使用for的
```go
for != nil {
    ...
}
```

## 無限循環
不加任何東西就是無限循環
```go
for {
    ...
}
```

# for/range
在golang中，對於數組、切片、map以及channel等數據結構，用for/range遍歷起來會更方便

```go  
//遍歷切片
s := []int{1, 2, 3, 4, 5}
for k, v := range s {
    fmt.Println(k, v)
}

//遍歷map
m := make(map[string]int)
m["key1"] = 1
m["key2"] = 2
m["key3"] = 3
for k, v := range m {
    fmt.Println(k, v)
}
```

# switch分支
需要特別說一下的是，和c裡的switch不同，Go 語言中不需要特別使用 break 語句來表示分支結束。

```go  
n := 2
switch n {
case 1:
    fmt.Println("case 1 hit!")
case 2:
    fmt.Println("case 2 hit!")
default:
    fmt.Println("no case hit!")
}
```
