
## 無法編譯通過的函數
如下的函數無法通過編譯，原因生命週期檢查器無法判斷要返回的值是哪個，進而無法確定返回值的生命週期。
生命週期檢查器也就無法正常工作。

```shell
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";
    let result = longest(string1.as_str(), string2);
    println!("The longest string is {}", result);
}
```

對其編譯後的報錯提示是

```shell
help: this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `x` or `y`
help: consider introducing a named lifetime parameter
```

## 函數聲明週期標註

解決方法是，在函數簽名中對輸入、返回值進行生命週期標註。在函數中借用時指定生命週期標註 <'a>
- 普通引用： &i32        
- 帶有顯式生命週期的引用： &'a i32     
- 帶有顯式生命週期的可變引用：&'a mut i32

對於這個例子，我們指定一個生命週期參數 <'a>，並將其應用到所有引用參數和返回值上。

```
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

這個函數簽名的意思是，有某個生命週期 <'a>，該函數的輸入參數和返回值的生命週期都是 <'a> 這麼長。
被 'a 所替代的具體生命週期是 x 的作用域與 y 的作用域相重疊的那一部分。
這樣編譯時的生命週期檢查器可以確定返回值的生命週期，並判斷是否允許編譯通過。

生命週期檢查器允許下面的調用通過
```
fn main() {
    let string1 = String::from("long string is long");
    {
        let string2 = String::from("xyz");
        let result = longest(string1.as_str(), string2.as_str());
        println!("The longest string is {}", result);
    }
}
```

但不允許下面的調用通過

```
fn main() {
    let string1 = String::from("long string is long");
    {
        let string2 = String::from("xyz");
        let result = longest(string1.as_str(), string2.as_str());
    }
    println!("The longest string is {}", result);
}
```

如果輸入參數和輸出參數沒有任何關係，則不需要標註生命週期。

```shell
fn longest<'a>(x: &'a str, y:  &str) -> &'a str {
    let result = String::from("really long string");
    result.as_str()
}
```

如果輸出參數和輸入參數沒有任何關係，也不應該通過引用的方式標準生命週期。而是應該返回一個帶生命週期的值

```shell
fn longest(x: &str, y:  &str) -> String {
    String::from("really long string")
}
```

如果返回的是一個字符串字面量
```shell
fn longest(x: &str, y:  &str) -> &'static str {
    "really long string"
}
```


## 生命週期省略規則

如果函數的參數沒有生命週期標註，則編譯器會自動標註生命週期。

規則如下：
- 1. 每個參數都擁有自己的生命週期
- 2. 如果只有一個輸入生命週期參數，則它被賦予所有輸出生命週期參數
- 3. 如果方法有多個輸入生命週期參數並且其中一個參數是 &self 或 &mut self，說明是個對象的方法(method)。那麼所有輸出生命週期參數被賦予 self 的生命週期。

例如下面的函數，開發者沒有標註生命週期，則編譯器的標註方式如下
```shell
fn first_word(s: &str) -> &str {}
```
應用規則1
```shell
fn first_word(s: &'a str) -> &str {}
```
應用規則2
```shell
fn first_word(s: &'a str) -> &'a str {}
```
然後編譯器可以繼續它的分析而無須開發者標記這個函數簽名中的生命週期。

但如果有兩個參數，編譯器嘗試自動標註

```shell
fn longest(x: &str, y: &str) -> &str { }
```

應用規則1
```shell
fn longest<'a, 'b>(x: &'a str, y: &'b str) -> &str { }
```
規則2，規則3都無法應用 。編譯器發現使用所有已知的生命週期省略規則，仍不能計算出簽名中所有引用的生命週期。則編譯報錯。