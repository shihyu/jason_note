
## 字符串的追加操作
字符串追加之push_str

```shell
fn main() {
    let s2 = String::from("basket");
    let s3 = String::from("ball!");
    let s4 = s2 + &s3;
    println!("s4 is {}", s4);
}
```

字符串追加之add操作

```shell
fn main() {
    let s2 = String::from("basket");
    let s3 = String::from("ball!");
    let s4 = s2 + &s3;
    println!("s4 is {}", s4);
}
```

注意 + 對應的是 add 操作
```shell
fn add(self, s: &str) -> String {
```

在 add 操作之後，self 的所有權被轉移走了，所以 s2 不再有效。
另外s3使用引用進行操作，所以它仍然有效。

由於add比較難於理解，對於多個字符串拼接，更推薦使用format!宏


```shell
fn main() {
    let s4 = String::from("one");
    let s5 = String::from("two");
    let s6 = String::from("three");
    let s7 = format!("{}-{}-{}", s4, s5, s6);
    println!("s4 is {}", s7);
}
```

## 遍歷字符串
字符串是一個 UTF-8 數組，正確的遍歷方式如下
```shell
fn main() {
    for c in "我是中國人".chars() {
        println!("{}", c);
    }
    for c in "我是中國人".bytes() {
        println!("{}", c);
    }  
}
```

輸出：
```shell
我
是
中
國
人
230
136
145
230
152
175
228
184
173
229
155
189
228
186
186
```