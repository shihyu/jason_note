泛型機制是編程語言用於表達類型抽象的機制，一般用於功能確定、數據類型待定的類，如鏈表、映射表等


下面是一個使用泛型的例子。

```
use std::cmp::PartialOrd;
fn largest<T: PartialOrd  + Copy>(list: &[T]) -> T {
    let mut largest = list[0];

    for &item in list.iter() {
        if item > largest {
            largest = item;
        }
    }

    largest
}
fn main() {
    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest(&number_list);
    println!("The largest number is {}", result);
}
```

要注意的是，在 largest 函數中，進行了 > 和 copy 等操作。而不一定所有的類型都實現了這兩個方法。
所以要求傳入的 T 必須要實現了 PartialOrd  和 Copy 這兩個 trait 才可以。