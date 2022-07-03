# Rust 筆記

- as_ptr()

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

- Rc / Box 用法

```rust
use std::rc::Rc;

struct Aa {
    id: i32,
}

impl Drop for Aa {
    fn drop(&mut self) {
        println!("Aa Drop, id: {}", self.id);
    }
}

fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>());
}

fn test_1() {
    let a1 = Aa { id: 1 }; // 数据分配在栈中
    let a1 = Rc::new(a1); // 数据 move 到了堆中？
    print_type_of(&a1);
    //drop(a1);
    println!("xxxxxxx");
}

fn test_2() {
    let a1 = Aa { id: 1 }; // 数据分配在栈中
    let a1 = Box::new(a1); // 数据 move 到了堆中？
    print_type_of(&a1);
}

fn main() {
    test_1();
    test_2();
}
```

