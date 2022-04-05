# Rust 筆記

## as_ptr()

```rust
fn print_type_of<T>(_: T) {
    println!("{}", std::any::type_name::<T>());
}

fn main() {
    let free_coloring_book = vec![
        "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune",
    ];
    // 1. free_coloring_book堆上数据的地址
    println!("address: {:p}", free_coloring_book.as_ptr());

    // 2. free_coloring_book栈上的地址
    let a = &free_coloring_book;
    println!("address: {:p}", a);

    let mut friends_coloring_book = free_coloring_book;

    // 3. friends_coloring_book堆上数据的地址，和1一样
    println!("address: {:p}", friends_coloring_book.as_ptr());

    // 4. friends_coloring_book栈上的地址
    let b = &friends_coloring_book;
    println!("address: {:p}", b);
}
```

