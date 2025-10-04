
定義一個vector，向其中插入元素，並訪問之

```shell
fn main() {
    let mut v: Vec<i32> = Vec::new();
    v.push(5);
    v.push(6);
    v.push(7);
    v.push(8);
}
```

也可以通過vec! 宏來創建一個新的 Vec

```
let v = vec![1, 2, 3];
```

## 使用for循環遍歷vector

```shell
fn main() {

    for i in &v {
        println!("{}", i);
    }

    match v.get(8) {
        Some(third) => println!("The third element is {}", third),
        None => println!("There is no third element."),
    }
}
```

## 訪問其中某個元素

```shell
fn main() {
    match v.get(8) {
        Some(third) => println!("The third element is {}", third),
        None => println!("There is no third element."),
    }
}
```


## 使用迭代器遍歷vector

```shell
fn main() {
    let mut v: Vec<i32> = Vec::new();
    v.push(5);
    v.push(6);
    v.push(7);
    v.push(8);

    let v_iter = v.iter();
    for val in v_iter {
        println!("Got: {}", val);
    }
}
```