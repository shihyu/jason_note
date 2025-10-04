
# 結構體

**1.結構體定義**
```go  
type 類型名 struct {
    字段名 字段類型
    字段名 字段類型
    …
}
```

其中：  
- 類型名：表示結構體的名稱，在同一個包內不能重複。
- 字段名：表示結構體成員的字段名，結構體中的字段名必須唯一。
- 字段類型：表示結構體字段的具體類型，如果相鄰的成員類型如果相同的話可以被合併到一行。

如果結構體成員名字是以大寫字母開頭的，那麼該成員就是可導出的，小寫表示僅在定義當前結構體的包中可訪問。

**2.結構體實例化**  

結構體必須實例化後才能使用結構體的字段，只有實例化後才會分配內存。實例化方法有兩種:  
```go  
var 結構體實例 結構體類型
var 結構體實例 = new(結構體類型)
```

剛實例化完沒有賦值的結構體，其成員變量都是對應其類型的零值。  
```go 
type Device struct {
	Phone string
	Imei  string
}
 
//1.實例化方式1
var s1 Device
fmt.Printf("%#v\n", s1) //main.Device{Phone:"", Imei:""}  

//2.實例化方式2
var s2 = new(Device)  
fmt.Printf("%#v\n", s2) //&main.Device{Phone:"", Imei:""}  
```

**3.結構體賦值**  
當結構體實例化完了以後，就可以使用其中的字段並進行賦值了。  
```go  
var s3 Device
s3.Phone = "13811111111"
s3.Imei = "867029040684350"
fmt.Println(s3) //{13811111111 867029040684350} 
```

如果嫌實例化、賦值分開略繁瑣的話，可以將這兩個步驟合併到一起。如下：  
```go  
//實例化同時賦值1
s4 := Device{
    Phone: "13822222222",
    Imei:  "967029040684350",
}
fmt.Printf("%#v\n", s4) //main.Device{Phone:"13811111111", Imei:"867029040684350"}

//實例化同時賦值2
s5 := Device{
    "13833333333",
    "967029040684350",
}
fmt.Println(s5) //main.Device{Phone:"13822222222", Imei:"967029040684350"}
```

**4.嵌套結構體**
結構體中的成員有可能是另外一個結構體，對於這種嵌套型的結構體來說，它的賦值方法稍微有一點點的不同，但也同樣很簡單。

```go  
type Device struct {
	Phone string
	Imei  string
}

type User struct {
	Id     int
	Name   string
	Device Device
}

//嵌套結構體賦值方式1
var s6 User
s6.Id = 1
s6.Name = "張三"
s6.Device.Phone = "13833333333"
s6.Device.Imei = "967029040684350"
fmt.Printf("%#v\n", s6) //main.User{Id:1, Name:"張三", Device:main.Device{Phone:"13833333333", Imei:"967029040684350"}}

//嵌套結構體賦值方式2
s7 := User{
    Id:   2,
    Name: "李四",
    Device: Device{
        Phone: "13833333333",
        Imei:  "967029040684350",
    },
}
fmt.Printf("%#v\n", s7) //main.User{Id:2, Name:"李四", Device:main.Device{Phone:"13833333333", Imei:"967029040684350"}}
```  

**5.結構體的標籤**  
結構體可以在字段後邊定義 Tag，由一對反引號包裹起來。標籤最經常是在json處理的地方會用到。
```go  
//json序列化
data, err := json.Marshal(s7)
if err != nil {
    fmt.Println("json marshal failed:", err)
    return
}
fmt.Printf("%s\n", data) //{"id":2,"name":"李四","device":{"phone":"13833333333","imei":"967029040684350"}}

//json反序列化
var s8 User
err = json.Unmarshal(data, &s8)
if err != nil {
    fmt.Println("json unmarshal failed:", err)
    return
}
fmt.Printf("%#v\n", s8) //main.User{Id:2, Name:"李四", Device:main.Device{Phone:"13833333333", Imei:"967029040684350"}}
```


 


