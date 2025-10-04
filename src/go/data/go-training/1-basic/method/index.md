
Go 語言的方法是作用在接收者（receiver）上的一個函數，接收者是某種類型的變量，因此方法是一種特殊類型的函數。接收者類型可以是（幾乎）任何類型，不僅僅是結構體類型：任何類型都可以有方法，甚至可以是函數類型，但是接收者不能是一個接口類型，因為接口是一個抽象定義，但方法是具體實現。

方法與函數的區別是，函數不屬於任何類型，方法屬於特定的類型。

# 方法的定義
```go  
func (接收者變量 接收者類型) 方法名(參數列表) (返回參數) {
    函數體
}
```

接收者中的參數變量名在命名時，官方建議使用接收者類型名稱首字母的小寫，而不是而不是 self、this 之類的命名，例如，Context 類型的接收者變量應該命名為 c。

# 值接收者
在值類型接收者的方法中可以獲取接收者的成員值，但修改操作只是針對副本，無法修改接收者變量本身。
原因是當方法作用於值類型接收者時，Go語言會在代碼運行時將接收者的值複製一份。

```go  
type User struct {
	Name  string
	Email string
}

//值作為接收者，可以訪問對象成員
func (u User) printName1() {
	fmt.Println(u.Name)
}

//值作為接收者， 無法修改對象成員
func (u User) changeName1(name string) {
	u.Name = name
}

func main() {
	var u1 User
	u1.Name = "張三"
	u1.Email = "demo@163.com"

	u1.printName1() //張三

	u1.changeName1("李四")
	fmt.Printf("%#v\n", u1) //main.User{Name:"張三", Email:"demo@163.com"}
}

```
# 指針接收者
在指針類型接收者的方法中也可以獲取接收者的成員值，而且可以修改接收者變量本身。

```go  
type User struct {
	Name  string
	Email string
}

//指針作為接收者，也可以訪問對象成員
func (u *User) printName2() {
	fmt.Println(u.Name)
}

//指針作為接收者，可以修改對象成員
func (u *User) changeName2(name string) {
	u.Name = name
}

func main() {

	var u1 User
	u1.Name = "張三"
	u1.Email = "demo@163.com"

	u1.printName2() //張三

	u1.changeName2("李四")
	fmt.Printf("%#v\n", u1) //main.User{Name:"李四", Email:"demo@163.com"}
}
```

鑑於性能的原因，接收者是拷貝代價比較大的大對象時，接收者通常會是一個指向接收者類型的指針，比如接收者的類型是結構體時。
另外通常為了保證一致性，如果有某個方法使用了指針接收者，那麼其他的方法也應該使用指針接收者。
  



