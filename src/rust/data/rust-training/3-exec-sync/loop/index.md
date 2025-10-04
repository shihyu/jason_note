
## for 循環

```rust
fn main() {
    let arr = [1,2,3,4,5];
    for item in arr {
        println!("{}", item); 
    }
}
```

## while 循環

```rust
fn main() {
    let arr = [1,2,3,4,5];
    let mut i = 0;
    while i < arr.len() {
        println!("{}", arr[i]); 
        i = i+1;
    }
}
```