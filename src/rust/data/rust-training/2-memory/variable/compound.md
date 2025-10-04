## 元組類型

元組類型（tuple type）是一種將多個其他類型組合成一個類型的方法。它通過在括號內列出元素類型來定義。

```rust
fn main() {
    let tuple:(i32,f64,u8) = (500,6.4,1);
    println!("{}", tuple.0); 
    println!("{}", tuple.1); 
    println!("{}", tuple.2); 
    
    let (x, y, z) = tuple;
    println!("{}", x); 
    println!("{}", y); 
    println!("{}", z); 
}
```

在上面的例子中，我們定義了一個名為`tuple`的變量，它的類型是一個元組。訪問方式
- 可以通過下標的方式來訪問
- 可以通過元組結構的方式來訪問元組中的元素。

### 數組類型

```rust
fn main() {
    let arr1 = [1,2,3,4,5];
    let arr2:[i32;5] = [1,2,3,4,5];

    println!("{}", arr1[0]); 
    println!("{}", arr1[2]); 
    println!("{}", arr2[2]); 
}
```

