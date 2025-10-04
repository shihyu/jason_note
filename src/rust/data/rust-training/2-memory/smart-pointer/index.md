box 允許你將一個值放在堆上而不是棧上。留在棧上的則是指向堆數據的指針。


```shell
fn main() {
    let b = Box::new(5);
    println!("b = {}", b);
}
```