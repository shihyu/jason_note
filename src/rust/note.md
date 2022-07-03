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

- data  bss text heap stack

```rust
/// .Text段存放的是程序中的可執行代碼
/// .Data段保存的是已經初始化了的全局變量和靜態變量
/// .ROData（ReadOnlyData）段存放程序中的常量值，如字符串常量
/// .BSS段存放的是未初始化的全局變量和靜態變量，程序執行前會先進行一遍初始化
const G_ARRAY: [i32; 5] = [10; 5];
const G_X: i32 = 100;
static G_VAR: i32 = 1000;

fn test06_heap_or_stack() {
    let s: &str = "test list";
    //字符串字面量，位於ROData段
    println!("&str: {:p}", s); //&str: 0x7ff77e4c6b88
    println!("{:p}", &G_ARRAY); //data段:0x7ff6c5fc6bb8
    println!("{:p}", &G_X); //data段:0x7ff6c5fc64f0
    println!("{:p}", &G_VAR); //data段:0x7ff77e4c6200
    println!("{}", "-".repeat(10));

    // 位於堆
    let bi = Box::new(30);
    println!("{:p}", bi); //堆:0x19f6c6585e0
                          // 將字符串字面量從內存中的代碼區（ROData段）復制一份到堆
                          // 棧上分配的變量s1指向堆內存
    let mut s1: String = String::from("Hello");
    // 可以通過std::mem::transmute將
    // 從24字節的長度的3個uszie讀出來
    let pstr: [usize; 3] = unsafe { std::mem::transmute(s1) };
    // pstr[0]是一個堆內存地址
    println!("ptr: 0x{:x}", pstr[0]); //ptr: 0x19f6c658750

    println!("{}", "-".repeat(10));
    // 位於棧
    let nums1 = [1, 2, 3, 4, 5, 6];
    let mut list: Vec<i32> = vec![20, 30, 40];
    let t = 100;
    println!("{:p}", &t); //棧0x116aeff104
    println!("{:p}", &nums1); //棧0x116aeff0d0
    println!("{:p}", &list); //棧0x116aeff0e8
                             // 從ROData區復制了一份字符串字面量放到堆上，
                             // 然後用棧上分配的s指向堆
    let s: String = "Hello".to_owned();
    println!("{:p}", &s); //0x116aeff1f8
    let s: String = String::from("Hello");
    println!("{:p}", &s); //0x116aeff260
    let s: String = "Hello".into();
    println!("{:p}", &s); //0x116aeff2c8
}

fn main() {
    test06_heap_or_stack();
}
```

