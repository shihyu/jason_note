# 生命週期（ Lifetime ）


下面是一個資源借用的例子：

```rust
fn main() {
	let a = 100_i32;

	{
		let x = &a;
	}  // x 作用域結束
	println!("{}", x);
}
```

編譯時，我們會看到一個嚴重的錯誤提示：

> error: unresolved name `x`.

錯誤的意思是“無法解析 `x` 標識符”，也就是找不到 `x` , 這是因為像很多編程語言一樣，Rust中也存在作用域概念，當資源離開離開作用域後，資源的內存就會被釋放回收，當借用/引用離開作用域後也會被銷燬，所以 `x` 在離開自己的作用域後，無法在作用域之外訪問。


上面的涉及到幾個概念：

* **Owner**: 資源的所有者 `a`
* **Borrower**: 資源的借用者 `x`
* **Scope**: 作用域，資源被借用/引用的有效期


強調下，無論是資源的所有者還是資源的借用/引用，都存在在一個有效的存活時間或區間，這個時間區間稱為**生命週期**， 也可以直接以**Scope作用域**去理解。

所以上例子代碼中的生命週期/作用域圖示如下：


```
            {    a    {    x    }    *    }
所有者 a:         |________________________|
借用者 x:                   |____|            x = &a
  訪問 x:                             |       失敗：訪問 x
```

可以看到，借用者 `x` 的生命週期是資源所有者 `a` 的生命週期的**子集**。但是 `x` 的生命週期在第一個 `}` 時結束並銷燬，在接下來的 `println!` 中再次訪問便會發生嚴重的錯誤。

我們來修正上面的例子：

```rust
fn main() {
	let a = 100_i32;

	{
		let x = &a;
		println!("{}", x);
	}  // x 作用域結束

}
```

這裡我們僅僅把 `println!` 放到了中間的 `{}`, 這樣就可以在 `x`的生命週期內正常的訪問 `x` ，此時的Lifetime圖示如下：

```
            {    a    {    x    *    }    }
所有者 a:         |________________________|
借用者 x:                   |_________|       x = &a
  訪問 x:                        |            OK：訪問 x
```



## 隱式Lifetime
我們經常會遇到參數或者返回值為引用類型的函數：

```rust
fn foo(x: &str) -> &str {
	x
}
```

上面函數在實際應用中並沒有太多用處，`foo` 函數僅僅接受一個 `&str ` 類型的參數（`x`為對某個`string`類型資源`Something`的借用），並返回對資源`Something`的一個新的借用。

實際上，上面函數包含該了隱性的生命週期命名，這是由編譯器自動推導的，相當於：

```rust
fn foo<'a>(x: &'a str) -> &'a str {
	x
}
```

在這裡，約束返回值的Lifetime必須大於或等於參數`x`的Lifetime。下面函數寫法也是合法的：

```rust
fn foo<'a>(x: &'a str) -> &'a str {
	"hello, world!"
}
```

為什麼呢？這是因為字符串"hello, world!"的類型是`&'static str`，我們知道`static`類型的Lifetime是整個程序的運行週期，所以她比任意傳入的參數的Lifetime`'a`都要長，即`'static >= 'a`滿足。


在上例中Rust可以自動推導Lifetime，所以並不需要程序員顯式指定Lifetime `'a` 。

`'a`是什麼呢？它是Lifetime的標識符，這裡的`a`也可以用`b`、`c`、`d`、`e`、...，甚至可以用`this_is_a_long_name`等，當然實際編程中並不建議用這種冗長的標識符，這樣會嚴重降低程序的可讀性。`foo`後面的`<'a>`為Lifetime的聲明，可以聲明多個，如`<'a, 'b>`等等。

另外，除非編譯器無法自動推導出Lifetime，否則不建議顯式指定Lifetime標識符，會降低程序的可讀性。

## 顯式Lifetime
當輸入參數為多個借用/引用時會發生什麼呢？

```rust
fn foo(x: &str, y: &str) -> &str {
	if true {
		x
	} else {
		y
	}
}
```

這時候再編譯，就沒那麼幸運了：

```
error: missing lifetime specifier [E0106]
fn foo(x: &str, y: &str) -> &str {
                            ^~~~
```

編譯器告訴我們，需要我們顯式指定Lifetime標識符，因為這個時候，編譯器無法推導出返回值的Lifetime應該是比 `x`長，還是比`y`長。雖然我們在函數中中用了 `if true` 確認一定可以返回`x`，但是要知道，編譯器是在編譯時候檢查，而不是運行時，所以編譯期間會同時檢查所有的輸入參數和返回值。

修復後的代碼如下：

```rust
fn foo<'a>(x: &'a str, y: &'a str) -> &'a str {
	if true {
		x
	} else {
		y
	}
}
```

## Lifetime推導

要推導Lifetime是否合法，先明確兩點：

* 輸出值（也稱為返回值）依賴哪些輸入值
* 輸入值的Lifetime大於或等於輸出值的Lifetime (準確來說：子集，而不是大於或等於)

**Lifetime推導公式：**
當輸出值R依賴輸入值X Y Z ...，當且僅當輸出值的Lifetime為所有輸入值的Lifetime交集的子集時，生命週期合法。

```
	Lifetime(R) ⊆ ( Lifetime(X) ∩ Lifetime(Y) ∩ Lifetime(Z) ∩ Lifetime(...) )
```

對於例子1：

```rust
fn foo<'a>(x: &'a str, y: &'a str) -> &'a str {
	if true {
		x
	} else {
		y
	}
}
```

因為返回值同時依賴輸入參數`x`和`y`，所以

```
	Lifetime(返回值) ⊆ ( Lifetime(x) ∩ Lifetime(y) )

	即：

	'a ⊆ ('a ∩ 'a)  // 成立
```


#### 定義多個Lifetime標識符
那我們繼續看個更復雜的例子，定義多個Lifetime標識符：

```rust
fn foo<'a, 'b>(x: &'a str, y: &'b str) -> &'a str {
	if true {
		x
	} else {
		y
	}
}
```

先看下編譯，又報錯了：

```
<anon>:5:3: 5:4 error: cannot infer an appropriate lifetime for automatic coercion due to conflicting requirements [E0495]
<anon>:5 		y
         		^
<anon>:1:1: 7:2 help: consider using an explicit lifetime parameter as shown: fn foo<'a>(x: &'a str, y: &'a str) -> &'a str
<anon>:1 fn bar<'a, 'b>(x: &'a str, y: &'b str) -> &'a str {
<anon>:2 	if true {
<anon>:3 		x
<anon>:4 	} else {
<anon>:5 		y
<anon>:6 	}
```

編譯器說自己無法正確地推導返回值的Lifetime，讀者可能會疑問，“我們不是已經指定返回值的Lifetime為`'a`了嗎？"。

這兒我們同樣可以通過生命週期推導公式推導：

因為返回值同時依賴`x`和`y`，所以

```
	Lifetime(返回值) ⊆ ( Lifetime(x) ∩ Lifetime(y) )

	即：

	'a ⊆ ('a ∩ 'b)  //不成立
```

很顯然，上面我們根本沒法保證成立。

所以，這種情況下，我們可以顯式地告訴編譯器`'b`比`'a`長（`'a`是`'b`的子集），只需要在定義Lifetime的時候, 在`'b`的後面加上`: 'a`, 意思是`'b`比`'a`長，`'a`是`'b`的子集:

```
fn foo<'a, 'b: 'a>(x: &'a str, y: &'b str) -> &'a str {
	if true {
		x
	} else {
		y
	}
}
```

這裡我們根據公式繼續推導：

```
	條件：Lifetime(x) ⊆ Lifetime(y)
	推導：Lifetime(返回值) ⊆ ( Lifetime(x) ∩ Lifetime(y) )

	即：

	條件： 'a ⊆ 'b
	推導：'a ⊆ ('a ∩ 'b) // 成立
```

上面是成立的，所以可以編譯通過。

#### 推導總結
通過上面的學習相信大家可以很輕鬆完成Lifetime的推導，總之，記住兩點：

1. 輸出值依賴哪些輸入值。
2. 推導公式。



## Lifetime in struct
上面我們更多討論了函數中Lifetime的應用，在`struct`中Lifetime同樣重要。

我們來定義一個`Person`結構體：

```rust
struct Person {
	age: &u8,
}
```

編譯時我們會得到一個error：

```
<anon>:2:8: 2:12 error: missing lifetime specifier [E0106]
<anon>:2 	age: &str,
```

之所以會報錯，這是因為Rust要確保`Person`的Lifetime不會比它的`age`借用長，不然會出現`Dangling Pointer`的嚴重內存問題。所以我們需要為`age`借用聲明Lifetime：

```rust
struct Person<'a> {
	age: &'a u8,
}
```

不需要對`Person`後面的`<'a>`感到疑惑，這裡的`'a`並不是指`Person`這個`struct`的Lifetime，僅僅是一個泛型參數而已，`struct`可以有多個Lifetime參數用來約束不同的`field`，實際的Lifetime應該是所有`field`Lifetime交集的子集。例如：

```
fn main() {
	let x = 20_u8;
	let stormgbs = Person {
						age: &x,
					 };
}
```

這裡，生命週期/Scope的示意圖如下：

```
                  {   x    stormgbs      *     }
所有者 x:              |________________________|
所有者 stormgbs:                |_______________|  'a
借用者 stormgbs.age:            |_______________|  stormgbs.age = &x
```

既然`<'a>`作為`Person`的泛型參數，所以在為`Person`實現方法時也需要加上`<'a>`，不然：

```rust
impl Person {
	fn print_age(&self) {
		println!("Person.age = {}", self.age);
	}
}
```

報錯：

```
<anon>:5:6: 5:12 error: wrong number of lifetime parameters: expected 1, found 0 [E0107]
<anon>:5 impl Person {
              ^~~~~~
```

**正確的做法是**：

```rust
impl<'a> Person<'a> {
	fn print_age(&self) {
		println!("Person.age = {}", self.age);
	}
}
```

這樣加上`<'a>`後就可以了。讀者可能會疑問，為什麼`print_age`中不需要加上`'a`？這是個好問題。因為`print_age`的輸出參數為`()`，也就是可以不依賴任何輸入參數, 所以編譯器此時可以不必關心和推導Lifetime。即使是`fn print_age(&self, other_age: &i32) {...}`也可以編譯通過。

**如果`Person`的方法存在輸出值（借用）呢？**

```rust
impl<'a> Person<'a> {
	fn get_age(&self) -> &u8 {
		self.age
	}
}
```

`get_age`方法的輸出值依賴一個輸入值`&self`，這種情況下，Rust編譯器可以自動推導為：

```rust
impl<'a> Person<'a> {
	fn get_age(&'a self) -> &'a u8 {
		self.age
	}
}
```

**如果輸出值（借用）依賴了多個輸入值呢？**


```rust
impl<'a, 'b> Person<'a> {
	fn get_max_age(&'a self, p: &'a Person) -> &'a u8 {
		if self.age > p.age {
			self.age
		} else {
			p.age
		}
	}
}
```

類似之前的Lifetime推導章節，當返回值（借用）依賴多個輸入值時，需顯示聲明Lifetime。和函數Lifetime同理。



**其他**

無論在函數還是在`struct`中，甚至在`enum`中，Lifetime理論知識都是一樣的。希望大家可以慢慢體會和吸收，做到舉一反三。


## 總結

Rust正是通過所有權、借用以及生命週期，以高效、安全的方式近乎完美地管理了內存。沒有手動管理內存的負載和安全性，也沒有GC造成的程序暫停問題。



