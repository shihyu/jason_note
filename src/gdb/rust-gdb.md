## Rust

- test.rs

```rust
trait Printable {
    fn print(&self);
}

struct Point {
    x: i32,
    y: i32,
}

impl Printable for Point {
    fn print(&self) {
        println!("({}, {})", self.x, self.y);
    }
}

fn print_all<T: Printable>(list: Vec<T>) {
    for item in list {
        item.print();
    }
}

fn main() {
    let list = vec![Point { x: 1, y: 2 }, Point { x: 3, y: 4 }];
    print_all(list);
}
```

```sh
rustc -C debuginfo=2 test.rs
```

```sh
https://github.com/zupzup/rust-gdb-example
```

