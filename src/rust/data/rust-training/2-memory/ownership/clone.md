## 所有權克隆
如果想要兩個變量都可以訪問，則需要使用克隆。
```shell
fn main() {
    let s1 = String::from("hello");
    let s2 = s1.clone();
    println!("{}", s1);
    println!("{}", s2);
}
```