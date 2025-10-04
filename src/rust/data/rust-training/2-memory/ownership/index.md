## 管理內存的方式
- 開發者親自申請和釋放內存
- 自動的垃圾回收機制，不斷尋找不使用的內存
- 通過所有權系統管理內存

## 所有權移動

- Rust 中的每一個值都有一個被稱為其 所有者（owner）的變量。
- 值在任一時刻有且只有一個所有者。
- 當所有者（變量）離開作用域，這個值將被丟棄。

所有權的移動（只有堆上的變量受影響）
```sh
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;
    
    //此時訪問s1會報錯
    println!("{}, world!", s1);
}
```
在 let s2 = s1後， s1 變量不再有效，s1的所有權已經被移動到s2中。再訪問s1的時候會報錯。


```shell
fn main() {
    let s1 = String::from("hello");
    somefunc(s1);
    println!("{}", s1);
}

fn somefunc(s2: String) { 
    println!("{}", s2);
}
```

### 不移動所有權的借用
如果函數需要使用參數，但是又不想轉移所有權，可以使用引用。
```rust
fn main() {
    let s1 = String::from("hello");
    somefunc(&s1);
    println!("{}", s1);
}

fn somefunc(s2: &String) { 
    println!("{}", s2);
}
```

值得注意的是，引用是不允許修改變量的值的。 

如果確實需要修改變量的值，則需要使用可變引用。
```rust
fn main() {
    let mut s1 = String::from("hello");
    somefunc(&mut s1);
    println!("{}", s1);
}

fn somefunc(s2: &mut String) { 
    s2.push_str(", world");
}
```
可變引用有一個很大的限制：在同一時間，只能有一個對某一特定數據的可變引用。嘗試創建兩個可變引用的代碼將會失敗

### 部分借用

```shell
fn main() {
    let s = String::from("hello world");
    let str1 = &s[0..5];
    let str2 = &s[6..11];

    println!("{}", str1);
    println!("{}", str2);
}
```


