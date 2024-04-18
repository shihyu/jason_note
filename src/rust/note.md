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
    // 1. free_coloring_book堆上數據的地址
    println!("address: {:p}", free_coloring_book.as_ptr());

    // 2. free_coloring_book棧上的地址
    let a = &free_coloring_book;
    println!("address: {:p}", a);

    let mut friends_coloring_book = free_coloring_book;

    // 3. friends_coloring_book堆上數據的地址，和1一樣
    println!("address: {:p}", friends_coloring_book.as_ptr());

    // 4. friends_coloring_book棧上的地址
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
    let a1 = Aa { id: 1 }; // 數據分配在棧中
    let a1 = Rc::new(a1); // 數據 move 到了堆中？
    print_type_of(&a1);
    //drop(a1);
    println!("xxxxxxx");
}

fn test_2() {
    let a1 = Aa { id: 1 }; // 數據分配在棧中
    let a1 = Box::new(a1); // 數據 move 到了堆中？
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

## ownership有個特性是個大坑

```rust
// ownership有個特性，感覺是個大坑，把不可變資料的ownership move到可變資料，那麼就改值了。這個設定不安全。
fn main() {
    let immutable = Box::new(5u32);
    println!("{:}", immutable);

    let mut mutable_box = immutable;
    println!("{:}", mutable_box);
    *mutable_box = 4;
    println!("{:}", mutable_box);
} 
```

## Rust中mut, &, &mut的區別

資源：記憶體區塊。不同的記憶體區塊位置和大小就是不同的資源。

### str
let a = "xxx".to_string();　　
含義：a繫結到字串資源A上，擁有資源A的所有權

let mut a = "xxx".to_string();　
含義：a繫結到字串資源A上，擁有資源A的所有權，同時a還可繫結到新的資源上面去（更新繫結的能力，但新舊資源類型要同）；

### value
let b = a;
含義：a繫結的資源A轉移給b，b擁有這個資源A

let b = &a;　　
含義：a繫結的資源A借給b使用，b只有資源A的讀權限

let b = &mut a;　　
含義：a繫結的資源A借給b使用，b有資源A的讀寫權限

let mut b = &mut a;　　
含義：a繫結的資源A借給b使用，b有資源A的讀寫權限。同時，b可繫結到新的資源上面去（更新繫結的能力）

### String
fn do(c: String) {}　　
含義：傳參的時候，實參d繫結的資源D的所有權轉移給c

fn do(c: &String) {}　　
含義：傳參的時候，實參d將繫結的資源D借給c使用，c對資源D唯讀

fn do(c: &mut String) {}　　
含義：傳參的時候，實參d將繫結的資源D借給c使用，c對資源D可讀寫

fn do(mut c: &mut String) {}　　
含義：傳參的時候，實參d將繫結的資源D借給c使用，c對資源D可讀寫。同時，c可繫結到新的資源上面去（更新繫結的能力）

函數參數裡面，冒號左邊的部分，mut c，這個mut是對函數體內部有效；冒號右邊的部分，&mut String，這個 &mut 是針對外部實參傳入時的形式化（類型）說明。

下面的例子輸出是什麼：

```rust
fn concat_literal(s: &mut String) {     
    s.extend("world!".chars());         
}                                       
                                          
fn main() {                             
    let mut s = "hello, ".to_owned();   
    concat_literal(&mut s);             
    println!("{}", s);                  
}  
```

## 打印 borrow 位址

```rust
fn print_type_of<T>(_: T) {
    println!("{}", std::any::type_name::<T>());
}

fn test(a: &mut i32) {
    println!("{:p}", *&a); // 打印 reference address 
    println!("{:p}", a); // 打印 reference address 
    println!("{:}", a);
    *a = 100;
    println!("{:p}", &a);
}

fn main() {
    let mut a = 10;
    print_type_of(a);
    let b = &mut a;
    *b = 50;
    print_type_of(b);
    println!("{:p}", &a);
    test(&mut a);
    println!("{:}", a);
}
```

```rust
fn print_type_of<T>(_: T) {
    println!("{}", std::any::type_name::<T>());
}

fn main() {
    let a: i32 = 5;
    print_type_of(a);
    println!("addr：{:p}", &a);
    let b = &a;
    print_type_of(b);
    println!("addr：{:p}", b);
    println!("value ：{:}", b);
    //&a先轉成raw指針，然後再把指針轉成usize，這個可以print的
    let addr = &a as *const i32 as usize;
    println!("addr：0x{:X}", addr);

    //為了驗證剛才的地址是不是正確的，我們修改這個指針指向的數據
    //pa就是addr對應的raw指針
    let pa = addr as *mut i32;
    //解引用，*pa其實就是&mut a了，給他賦值100
    unsafe { *pa = 100 };

    //打印a，可以看到a已經變成100了
    println!("value:{}", a);
}
```

## &self 和 self 的區別

在 Rust 的方法中，第一個參數為 & self，那麼如果改成 self（不是大寫的 Self）行不行，兩者有什麼區別。
&self，表示向函數傳遞的是一個引用，不會發生對像所有權的轉移；
self，表示向函數傳遞的是一個對象，會發生所有權的轉移，對象的所有權會傳遞到函數中。
原文作者：linghuyichong
轉自鏈接：https://learnku.com/articles/39050

```rust
#[derive(Debug)]
struct MyType {
    name: String,
}

impl MyType {
    fn do_something(self, age: u32) {
        //等價於 fn do_something(self: Self, age: u32) {
        //等價於 fn do_something(self: MyType, age: u32) {
        println!("name = {}", self.name);
        println!("age = {}", age);
    }

    fn do_something2(&self, age: u32) {
        println!("name = {}", self.name);
        println!("age = {}", age);
    }
}

fn main() {
    let my_type = MyType {
        name: "linghuyichong".to_string(),
    };
    //使用self
    my_type.do_something(18); //等價於MyType::do_something(my_type, 18);
                              //println!("my_type: {:#?}", my_type);    //在do_something中，傳入的是對象，而不是引用，因此my_type的所有權就轉移到函數中了，因此不能再使用

    //使用&self
    let my_type2 = MyType {
        name: "linghuyichong".to_string(),
    };
    my_type2.do_something2(18);
    my_type2.do_something2(18);
    println!("my_type2: {:#?}", my_type2); //在do_something中，傳入是引用，函數並沒有獲取my_type2的所有權，因此此處可以使用
    println!("Hello, world!");
}
```

- 模擬C++ 建構/解構

  ```rust
  use std::thread;
  use std::process;
  
  struct MyStruct {
      value: i32,
  }
  
  impl MyStruct {
      fn new(value: i32) -> MyStruct {
          println!("MyStruct with value {} created by pid {} tid {:?}", value, process::id(), thread::current().id());
          MyStruct { value: value }
      }
  }
  
  impl Drop for MyStruct {
      fn drop(&mut self) {
          println!("MyStruct with value {} dropped by pid {} tid {:?}", self.value, process::id(), thread::current().id());
      }
  }
  
  fn main() {
      let my_struct = MyStruct::new(42);
  }
  ```


- trait

```rust

/*
 * 這個程式碼定義了一個名叫 Movable 的 trait，這個 trait 定義了一個 movement 方法。
 * Human 和 Rabbit 是兩個結構體，分別實現了 Movable trait。在每個實現中，
 * 都定義了一個 movement 方法，實現了結構體如何移動的行為。
 * 在 main 函數中，我們創建了一個 Human 和一個 Rabbit 的實例，存儲在 human 和 rabbit 變數中。
 * 然後，我們依次對這兩個變數分別調用了 movement 方法，分別輸出了 "Human walk" 和 "Rabbit jump"。
 * 這個程式碼展示瞭如何使用 Rust 的 trait 和結構體來實現多態行為。
 * 使用 trait，可以將類似的操作組織成一個介面，並將其實現為多個不同的類型。這使得代碼更加模組化，可重用性更高。
 * */
trait Movable {
    fn movement(&self);
}

struct Human;

impl Movable for Human {
    fn movement(&self) {
        println!("Human walk");
    }
}

struct Rabbit;

impl Movable for Rabbit {
    fn movement(&self) {
        println!("Rabbit jump");
    }
}

fn main() {
    let human = Human;
    let rabbit = Rabbit;

    human.movement();
    rabbit.movement();
}
```

-  Rust 中有三種方式來引用這個結構實例：`self`、`&self`、`&mut self`。下面舉例說明這三種實例引用方式的不同之處。

  self` 和 `&mut self` 都用於引用結構體實例，但有著不同的含義。

  `self` 表示方法使用結構體實例的所有權；而 `&mut self` 則表示方法使用結構體實例的可變引用。

  具體來說，當使用 `self` 定義方法時，這個方法會接受結構體實例的所有權，即將結構體實例移動到方法中，可以在方法內部進行修改或銷毀。當方法執行完畢後，結構體實例的控制權會返回到調用方。

  而使用 `&mut self` 定義方法時，這個方法會接受結構體實例的可變引用。當方法被調用時，結構體實例依然保持存在，並且可以在方法內部進行修改。當方法執行完畢後，結構體實例保持存在並且可以繼續使用。

  總體來說，使用 `self` 比使用 `&mut self` 更加靈活，但也更加危險，因為它轉移了結構體實例的所有權。而使用 `&mut self` 可以讓方法在調用時保留結構體實例，並可以在方法內部進行修改，但需要注意如果結構體同時被多個可讀寫的引用進行修改，就會產生賽博會同步錯誤。因此，方法的實現必須小心處理對結構體實例的存儲和修改依賴關係。

  

  首先，讓我們定義一個結構 `Person`，其中包含了一個名稱屬性：

  ```rust
  struct Person {
      name: String,
  }
  ```

  接下來，我們為這個結構定義三種方法，分別使用 `self`、`&self` 和 `&mut self` 來引用實例。

  1. 使用 `self` 引用實例，並修改結構屬性：

  ```rust
  impl Person {
      fn set_name(self, new_name: String) -> Person {
          Person { name: new_name }
      }
  }
  ```

  在這個方法中，`self` 為結構體的值，透過使用 `set_name` 方法，我們可以將一個 `Person` 結構體的名稱屬性更改為一個新的名稱，然後返回一個新的 `Person` 結構體，原來的實例沒有被修改。這種方式可以原地修改實例，因為它轉移了所有權。

  1. 使用 `&self` 引用實例，但不修改結構屬性：

  ```rust
  impl Person {
      fn greet(&self) {
          println!("Hi, my name is {}", self.name);
      }
  }
  ```

  在這個方法中，`&self` 為結構體的借用引用，它將 `Person` 結構體的所有權借用給了 `greet` 方法，但不允許 `greet` 方法修改該實例的任何屬性。因此，這種方式適用於只需要讀取結構屬性的方法。

  1. 使用 `&mut self` 引用實例，並修改結構屬性：

  ```rust
  impl Person {
      fn rename(&mut self, new_name: String) {
          self.name = new_name;
      }
  }
  ```

  在這個方法中，`&mut self` 為結構體的可變引用，透過使用 `rename` 方法，我們可以將一個 `Person` 結構體的名稱屬性更改為一個新的名稱。這種方式允許修改結構屬性，因為它使用了結構體的可變引用。

  總結來說，這三種方式分別提供了不同的實例引用方法。使用 `self` 從原始的實例移動所有權，這在歸還新創建的 `Person` 結構體時特別有用。使用 `&self` 或 `&mut self` 以引用的方式讀取和修改結構屬性。使用 `&self`可以保證實例是不可變的，而使用 `&mut self` 允許修改實例的內容。

- 在 Rust 中，`self` 和 `Self` 都表示結構體或枚舉的類型，但有著不同的含義。

  self` 在方法定義中是用來引用實例自身，而 `Self` 則用來表示結構體或枚舉本身的類型。下面是一個示例，說明瞭 `Self` 和 `self` 的使用：

  在這個示例中，我們定義了一個名為 `Rectangle` 的結構體，並為其實現了三個方法：`new`、`area` 和 `same`。

  在 `new` 方法中，我們使用了 `Self` 來表示結構體的類型，並使用了 `self` 變量，它是一個引用結構體實例的不可變引用。這個方法創建了一個新的 `Rectangle` 結構體實例，並將其返回。

  在 `area` 方法中，我們使用了 `&self` 引用，這個方法只是計算結構體實例的面積，但不修改它。

  在 `same` 方法中，我們使用了 `&Self` 引用，這個方法不需要引用結構體實例本身，而是可以直接使用 `Rectangle` 類型來比較兩個實例是否具有相同的寬度和高度。

  在 `main` 函數中，我們創建了一個 `Rectangle` 結構體實例，調用了 `area` 方法來計算實例的面積，並調用了 `same` 方法來檢查實例是否是一個正方形。

  總結來說，`self` 主要用於方法中引用結構體實例本身，而 `Self` 則用作表示結構體或枚舉的類型。

  ```rust
  struct Rectangle {
      width: u32,
      height: u32,
  }
  
  impl Rectangle {
      fn new(width: u32, height: u32) -> Self {
          Self { width, height }
      }
  
      fn area(&self) -> u32 {
          self.width * self.height
      }
  
      fn same(rect: &Self) -> bool {
          rect.width == rect.height
      }
  }
  
  fn main() {
      let rectangle = Rectangle::new(10, 5);
      println!(
          "The area of the rectangle is {} square pixels.",
          rectangle.area()
      );
      println!("Is the rectangle a square? {}", Rectangle::same(&rectangle));
  }
  
  ```

  ## `Handle` trait 的方式不同
  
  第一個代碼示例中，我們在 `Handle` trait 中定義了一個實例方法 `handle()`，它接受一個 `&self` 參數，表示該方法是與 `Handler` 結構體實例相關聯的。在實現 `Handle` trait 時，我們對每個需要處理的類型都分別實現了 `handle()` 方法，通過 `impl Handle<i32> for Handler` 和 `impl Handle<f64> for Handler` 定義了對 `i32` 和 `f64` 類型的處理過程。在 `main()` 中，我們創建了 `Handler` 結構體對象 `handler`，然後調用 `handler.handle(10)` 和 `handler.handle(10.5)` 方法來處理輸入的不同類型數據。
  
  ```rust
  struct Handler;
  
  trait Handle<T> {
      fn handle(&self, input: T);
  }
  
  impl Handle<i32> for Handler {
      fn handle(&self, input: i32) {
          println!("This is i32: {}", input);
      }
  }
  
  impl Handle<f64> for Handler {
      fn handle(&self, input: f64) {
          println!("This is f64: {}", input);
      }
  }
  
  fn main() {
      let handler = Handler;
  
      // 使用 i32 類型的 Handler
      handler.handle(10);
  
      // 使用 f64 類型的 Handler
      handler.handle(10.5);
  }
  ```
  
  
  
  第二個代碼示例中，我們在 `Handle` trait 中定義了一個關聯函數 `handle()`，它不需要 `&self` 參數，表示該函數與 `Handler` 結構體實例無關。在實現 `Handle` trait 時，我們同樣對每個需要處理的類型都分別實現了 `handle()` 關聯函數，通過 `impl Handle<i32> for Handler` 和 `impl Handle<f64> for Handler` 定義了對 `i32` 和 `f64` 類型的處理過程。在 `main()` 中，我們不創建任何 `Handler` 的對象，而是直接對 `Handler` 結構體類型調用 `Handler::handle(10)` 和 `Handler::handle(10.5)`方法來處理輸入的不同類型數據。
  
  因此，這兩段代碼的區別在於實現 `Handle` trait 的方式不同。第一個代碼示例中實現了一個實例方法 `handle()`，第二個代碼示例中實現了一個關聯函數 `handle()`。這兩個方法/函數的調用方式也不同。
  
  ```rust
  struct Handler;
  
  trait Handle<T> {
      fn handle(&self, input: T);
  }
  
  impl Handle<i32> for Handler {
      fn handle(&self, input: i32) {
          println!("This is i32: {}", input);
      }
  }
  
  impl Handle<f64> for Handler {
      fn handle(&self, input: f64) {
          println!("This is f64: {}", input);
      }
  }
  
  fn main() {
      let handler = Handler;
  
      // 使用 i32 類型的 Handler
      handler.handle(10);
  
      // 使用 f64 類型的 Handler
      handler.handle(10.5);
  }
  ```
  



### enum 用法

```rust
#[allow(clippy::all)]
enum WebsocketAPI {
    Default,
    MultiStream,
    Custom(String),
}

fn handle_websocket_api(api: WebsocketAPI) {
    match api {
        WebsocketAPI::Default => {
            println!("Handling default WebSocket API");
            // Your code for the default case
        }
        WebsocketAPI::MultiStream => {
            println!("Handling multi-stream WebSocket API");
            // Your code for the multi-stream case
        }
        WebsocketAPI::Custom(custom_api) => {
            println!("Handling custom WebSocket API: {}", custom_api);
            // Your code for the custom case, using the custom API string
        }
    }
}

fn main() {
    let default_api = WebsocketAPI::Default;
    let multi_stream_api = WebsocketAPI::MultiStream;
    let custom_api = WebsocketAPI::Custom(String::from("wss://custom.api"));

    handle_websocket_api(default_api);
    handle_websocket_api(multi_stream_api);
    handle_websocket_api(custom_api);
}

```



### HashMap 用法：

`HashMap`是一種鍵-值對的集合，其中每個鍵必須是唯一的。它是Rust標準庫的一部分，用於實現字典或關聯數組。

這是一個使用`HashMap`的例子：

```rust
use std::collections::HashMap;

fn main() {
    // Creating a new HashMap
    let mut my_map = HashMap::new();

    // Inserting key-value pairs
    my_map.insert("key1", "value1");
    my_map.insert("key2", "value2");
    my_map.insert("key3", "value3");

    // Accessing values using keys
    if let Some(value) = my_map.get("key2") {
        println!("Value for key2: {}", value);
    }

    // Iterating over key-value pairs
    for (key, value) in &my_map {
        println!("Key: {}, Value: {}", key, value);
    }
}
```

### 迭代器的 `map` 方法：

在Rust中，迭代器具有`map`方法，它通過將函數應用於每個元素來轉換迭代器中的每個項目。這裡是一個簡單的例子：

在此示例中，使用`map`方法創建了一個新的迭代器，其中每個元素都加倍。然後使用`collect`方法將迭代器轉換迴向量。

```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];

    // Using map to double each number
    let doubled_numbers: Vec<_> = numbers.into_iter().map(|x| x * 2).collect();

    println!("Original numbers: {:?}", numbers);
    println!("Doubled numbers: {:?}", doubled_numbers);
}
```



### 閉包（closures）

是一種特殊的函數類型，它可以捕獲其環境中的變數。閉包具有以下幾個用法和優勢：

### 簡潔性和靈活性：

閉包允許你編寫更為簡潔、直觀的程式碼。相比於定義一個完整的函數，閉包可以直接在需要時聲明和使用，使程式碼更具靈活性。

```rust
// 使用閉包
let add = |x, y| x + y;
println!("Sum: {}", add(3, 4));

// 相同的功能使用函數
fn add_function(x: i32, y: i32) -> i32 {
    x + y
}
println!("Sum: {}", add_function(3, 4));
```

### 捕獲環境變數：

閉包可以捕獲其所在範疇中的變數，可以是引用（`&`）或移動（`move`）。這允許你在閉包內部使用外部變數，而不需要顯式傳遞參數。

```rust
let x = 10;
let closure = || println!("x: {}", x);
closure();
```

### **所有權轉移：**

使用 `move` 關鍵字，閉包可以將其環境中的所有權轉移到閉包內，從而實現所有權的轉移。這對於將資料傳遞給執行緒或其他閉包非常有用。

```rust
let data = vec![1, 2, 3];
let closure = move || {
    // data 所有權已轉移到閉包
    println!("{:?}", data);
};
closure();
// 下面的行將會引發編譯錯誤，因為 data 所有權已轉移
// println!("{:?}", data);
```

### **函數式程式設計：**

閉包使Rust更加適合函數式程式設計風格。你可以將閉包傳遞給其他函數，或者將其作為迭代器的參數。

```rust
let numbers = vec![1, 2, 3, 4, 5];
let squared: Vec<_> = numbers.into_iter().map(|x| x * x).collect();
println!("{:?}", squared);
```

### **泛型和trait的使用：**

閉包可以與泛型和trait一起使用，使其更加通用和靈活。你可以定義一個接受閉包作為參數的泛型函數，以處理不同類型的操作。

```rust
fn perform_operation<T, U, F>(value: T, operation: F) -> U
where
    F: Fn(T) -> U,
{
    operation(value)
}

fn main() {
    // 對整數進行操作
    let result_int = perform_operation(5, |x| x * 2);
    println!("Result for integer: {}", result_int);

    // 對浮點數進行操作
    let result_float = perform_operation(3.5, |x| x * 2.0);
    println!("Result for float: {}", result_float);

    // 對字串進行操作
    let result_string = perform_operation("Hello", |x| format!("{}!", x));
    println!("Result for string: {}", result_string);
}
```

1. `fn perform_operation<T, U, F>(value: T, operation: F) -> U`: 這是一個泛型函數的聲明。它有三個泛型參數，分別為 `T`、`U` 和 `F`。這表示這個函數可以接受不同類型的值（`T`）和返回不同類型的結果（`U`），同時還接受一個泛型的函數或閉包（`F`）。
2. `where F: Fn(T) -> U`: 這是一個 trait bound（特徵約束），它規定了泛型 `F` 必須實現 `Fn(T) -> U` 這個特徵。這表示 `F` 必須是一個接受 `T` 類型參數的函數，並返回 `U` 類型的值。換句話說，`operation` 參數必須是一個可以接受 `value` 類型的函數或閉包。
3. `{ operation(value) }`: 函數體中的這一行是具體的實現。它調用了傳入的 `operation` 函數或閉包，並將 `value` 作為參數傳遞給它。整個函數最終返回 `operation` 的結果，這個結果的類型是 `U`。

這段程式碼的目的是創建一個通用的函數，可以將一個值和一個函數或閉包傳遞給它，並返回該函數或閉包對該值的操作結果。通過使用泛型，這個函數可以處理不同類型的輸入和輸出。

`T`、`U` 和 `F` 只是慣例上常用的泛型參數名稱，實際上你可以使用任何有效的識別符號作為泛型參數名稱。這些字母通常代表不同的概念：

- `T`：通常表示 "Type"，表示泛型的類型參數。
- `U`：通常用於表示第二個泛型類型參數。
- `F`：通常表示 "Function"，用於表示接受或返回函數的泛型參數。

這些僅僅是慣例，而不是強制的規則。當你閱讀其他人的代碼或寫自己的代碼時，習慣上使用這樣的字母可以讓代碼更容易閱讀和理解。

```rust
fn perform_operation<Input, Output, Func>(value: Input, operation: Func) -> Output
where
    Func: Fn(Input) -> Output,
{
    operation(value)
}

fn main() {
    // 對整數進行操作
    let result_int = perform_operation(5, |x| x * 2);
    println!("Result for integer: {}", result_int);

    // 對浮點數進行操作
    let result_float = perform_operation(3.5, |x| x * 2.0);
    println!("Result for float: {}", result_float);

    // 對字串進行操作
    let result_string = perform_operation("Hello", |x| format!("{}!", x));
    println!("Result for string: {}", result_string);
}
```



## trait

trait是一種定義共享行為的機制，它類似於其他語言中的接口（interface）。trait可以用於定義方法簽名，然後類型實現這些trait，以提供對這些方法的具體實現。

以下是一個簡單的示例，演示瞭如何定義trait和實現它：

```rust
// 定義一個名為 Printable 的 trait
trait Printable {
    // 方法簽名，表示實現這個 trait 的類型需要實現 print 方法
    fn print(&self);
}

// 實現 Printable trait 的結構體
struct Dog {
    name: String,
}

// 實現 Printable trait 的結構體
struct Cat {
    name: String,
}

// 實現 Printable trait for Dog
impl Printable for Dog {
    // 實現 print 方法
    fn print(&self) {
        println!("Dog named {}", self.name);
    }
}

// 實現 Printable trait for Cat
impl Printable for Cat {
    // 實現 print 方法
    fn print(&self) {
        println!("Cat named {}", self.name);
    }
}

fn main() {
    // 創建一個 Dog 實例
    let dog = Dog { name: String::from("Buddy") };
    // 呼叫 Printable trait 中的 print 方法
    dog.print();

    // 創建一個 Cat 實例
    let cat = Cat { name: String::from("Whiskers") };
    // 呼叫 Printable trait 中的 print 方法
    cat.print();
}
```

- 我們定義了一個名為 `Printable` 的 trait，它包含一個方法 `print`。
- 我們創建了兩個結構體 `Dog` 和 `Cat`。
- 我們為每個結構體實現了 `Printable` trait，提供了對 `print` 方法的具體實現。
- 在 `main` 函數中，我們創建了一個 `Dog` 實例和一個 `Cat` 實例，然後分別呼叫了它們的 `print` 方法。

這就是trait的基本用法。trait還可以用於實現泛型，以及在函數中指定trait約束，這樣可以在不同類型上使用相同的trait方法。

## trait 和泛型是 Rust 中的兩個不同的概念，但它們經常一起使用。

泛型（Generics）是一種通用編程概念，它允許編寫可以處理多種不同類型的代碼而不失靈活性和安全性的方式。通過使用泛型，可以在函數、結構、列舉和方法等多種場景中創建通用的代碼。

**範例：**

```rust
use std::fmt::Debug; // 引入 Debug trait

fn print<T: Debug>(value: T) {
    println!("Value: {:#?}", value);
}

fn main() {
    print(5);
    print("Hello");
}
```

這裡的 `print` 函數使用泛型，可以接受任何類型的參數。

### Trait：

Trait 定義了一組可以由類型實現的方法的集合，這樣就可以共享某種行為。Trait 提供了一種方式來描述類型之間的共同特徵。

**範例：**

```rust
trait Printable {
    fn print(&self);
}

struct Dog {
    name: String,
}

impl Printable for Dog {
    fn print(&self) {
        println!("Dog named {}", self.name);
    }
}

struct Cat {
    name: String,
}

impl Printable for Cat {
    fn print(&self) {
        println!("Cat named {}", self.name);
    }
}

fn main() {
    let dog = Dog {
        name: String::from("Buddy"),
    };
    dog.print();

    let cat = Cat {
        name: String::from("Whiskers"),
    };
    cat.print();
}
```

在這裡，`Printable` 是一個 trait，`Dog` 和 `Cat` 結構體實現了這個 trait，提供了對 `print` 方法的具體實現。

### 結論：

總體而言，泛型是一種更通用的編程概念，用於創建可以處理多種類型的代碼，而 trait 則用於描述類型之間的共同特徵，讓不同的類型可以共享某種行為。在實踐中，泛型和 trait 經常一起使用，使得代碼更加靈活和可擴展。



## Self 與 self 差異

`Self` 是一個特殊的關鍵字，通常用於表示實現 trait 的類型。它表示實際類型，即實現 trait 的類型本身。使用 `Self` 的時機主要包括：

1. **返回類型聲明：** 當你在 trait 的方法中聲明返回類型時，可以使用 `Self` 來表示實現該 trait 的具體類型。這允許實現方在方法中返回其實際類型。

   ```rust
   trait ExampleTrait {
       fn example_method(&self) -> Self;
   }
   ```

2. **關聯類型：** `Self` 也可用於關聯類型，這是一種在 trait 中聲明類型並在實現中具體化的方式。

   ```rust
   trait ExampleTrait {
       type Item;
       
       fn get_item(&self) -> Self::Item;
   }
   ```

總體而言，`Self` 用於在 trait 中表示實現該 trait 的類型，並在需要指代實際類型的地方使用。

`type` 是一個關鍵字，用於聲明與trait關聯的關聯類型。關聯類型允許trait中使用的類型在實現trait時具體化。在你的例子中，`type Item;` 就是在trait `ExampleTrait` 中聲明瞭一個關聯類型 `Item`。

```rust
trait ExampleTrait {
    type Item;  // 關聯類型聲明
    
    fn create_instance() -> Self;  // 使用Self作為返回類型
    fn get_item(&self) -> Self::Item;  // 使用Self::Item作為返回類型
}

struct ExampleType;

impl ExampleTrait for ExampleType {
    type Item = i32;  // 具體化關聯類型
    
    fn create_instance() -> Self {
        ExampleType  // 返回實現trait的具體類型
    }

    fn get_item(&self) -> Self::Item {
        42  // 在實現中返回關聯類型的實例
    }
}

fn main() {
    let instance = ExampleType::create_instance();
    let item = instance.get_item();
    
    println!("Item: {}", item);
}
```



## python 繼承 用 Rust 實作

```python
# 定義父類
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass  # 父類中的方法，子類將覆蓋它

# 定義子類，繼承自 Animal
class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

# 定義另一個子類，也繼承自 Animal
class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

# 創建實例並調用方法
dog_instance = Dog("Buddy")
cat_instance = Cat("Whiskers")

print(dog_instance.speak())  # 輸出: Buddy says Woof!
print(cat_instance.speak())  # 輸出: Whiskers says Meow!
```

```rust
// 定義 trait
trait Animal {
    fn new(name: &str) -> Self;
    fn speak(&self) -> String;
}

// 定義結構體實現 trait
struct Dog {
    name: String,
}

impl Animal for Dog {
    fn new(name: &str) -> Self {
        Dog {
            name: name.to_string(),
        }
    }

    fn speak(&self) -> String {
        format!("{} says Woof!", self.name)
    }
}

// 定義另一個結構體實現 trait
struct Cat {
    name: String,
}

impl Animal for Cat {
    fn new(name: &str) -> Self {
        Cat {
            name: name.to_string(),
        }
    }

    fn speak(&self) -> String {
        format!("{} says Meow!", self.name)
    }
}

fn main() {
    // 創建實例並調用方法
    let dog_instance = Dog::new("Buddy");
    let cat_instance = Cat::new("Whiskers");

    println!("{}", dog_instance.speak()); // 輸出: Buddy says Woof!
    println!("{}", cat_instance.speak()); // 輸出: Whiskers says Meow!
}
```



### enum 跟 impl

在這個例子中，我們使用了列舉 `Animal` 來表示不同類型的動物（狗和貓）。每個動物類型都有一個 `name` 欄位。我們通過在列舉上實現方法來模擬建構函式（`new_dog` 和 `new_cat`）和 `speak` 方法。在 `main` 函數中，我們建立了兩個不同類型的動物實例並呼叫了它們的 `speak` 方法。

```rust
// 定義一個枚舉，表示不同類型的動物
enum Animal {
    Dog { name: String },
    Cat { name: String },
}

// 枚舉上的方法
impl Animal {
    // 構造函數
    fn new_dog(name: &str) -> Self {
        Animal::Dog { name: name.to_string() }
    }

    fn new_cat(name: &str) -> Self {
        Animal::Cat { name: name.to_string() }
    }

    // 說話的方法
    fn speak(&self) -> String {
        match self {
            Animal::Dog { name } => format!("{} says Woof!", name),
            Animal::Cat { name } => format!("{} says Meow!", name),
        }
    }
}

fn main() {
    // 創建實例並調用方法
    let dog_instance = Animal::new_dog("Buddy");
    let cat_instance = Animal::new_cat("Whiskers");

    println!("{}", dog_instance.speak()); // 輸出: Buddy says Woof!
    println!("{}", cat_instance.speak()); // 輸出: Whiskers says Meow!
}
```



### struct 跟 impl

在這個例子中，我們使用了 `struct` 定義了 `Animal` 結構體，其中包含了 `kind` 表示動物的種類（"Dog" 或 "Cat"），以及 `name` 表示動物的名字。建構函式 `new` 用於建立新的 `Animal` 實例，而 `speak` 方法根據動物的種類輸出不同的聲音。在 `main` 函數中，我們建立了兩個不同類型的動物實例並呼叫了它們的 `speak` 方法。

```rust
// 定義結構體
struct Animal {
    kind: String,
    name: String,
}

// Animal 結構體的方法
impl Animal {
    // 構造函數
    fn new(kind: &str, name: &str) -> Self {
        Animal {
            kind: kind.to_string(),
            name: name.to_string(),
        }
    }

    // 說話的方法
    fn speak(&self) -> String {
        match self.kind.as_str() {
            "Dog" => format!("{} says Woof!", self.name),
            "Cat" => format!("{} says Meow!", self.name),
            _ => format!("Unknown animal"),
        }
    }
}

fn main() {
    // 創建實例並調用方法
    let dog_instance = Animal::new("Dog", "Buddy");
    let cat_instance = Animal::new("Cat", "Whiskers");

    println!("{}", dog_instance.speak()); // 輸出: Buddy says Woof!
    println!("{}", cat_instance.speak()); // 輸出: Whiskers says Meow!
}
```

```rust
// 定義結構體
struct Point {
    x: f64,
    y: f64,
}

// 在結構體上實現方法
impl Point {
    // 構造函數
    fn new(x: f64, y: f64) -> Point {
        Point { x, y }
    }

    // 計算兩點之間的距離
    fn distance(&self, other: &Point) -> f64 {
        ((self.x - other.x).powi(2) + (self.y - other.y).powi(2)).sqrt()
    }

    // 移動點的位置
    fn translate(&mut self, dx: f64, dy: f64) {
        self.x += dx;
        self.y += dy;
    }
}

fn main() {
    // 創建 Point 的實例
    let point1 = Point::new(0.0, 0.0);
    let point2 = Point::new(3.0, 4.0);

    // 調用 Point 上的方法
    println!("Distance between points: {}", point1.distance(&point2));

    let mut point3 = Point::new(1.0, 1.0);
    point3.translate(2.0, 3.0);
    println!("New point location: ({}, {})", point3.x, point3.y);
}
```



## Async Await spawn 用法

```rust
use tokio::time::{sleep, Duration};

// 異步函數
async fn async_function(id: usize) {
    println!("Start of async function {}", id);

    // 模擬異步操作，例如 I/O 操作
    sleep(Duration::from_secs(2)).await;

    println!("End of async function {}", id);
}

// 您可以一次連續呼叫 async_function 多次。在非同步程式設計中，您可以使用 tokio::spawn 或其他類似的功能來並行執行多個非同步任務。下面是一個例子，演示如何連續呼叫 async_function 5 次
#[tokio::main]
async fn main() {
    println!("Start of main function");

    // 創建一個 Vec 來存儲任務句柄
    let mut handles = Vec::new();

    // 調用 async_function 5 次
    for i in 0..5 {
        // 使用 tokio::spawn 啟動異步任務，並將任務句柄存儲在 Vec 中
        let handle = tokio::spawn(async_function(i));
        handles.push(handle);
    }

    // 等待所有任務完成
    for handle in handles {
        handle.await.expect("Failed to await task");
    }

    println!("End of main function");
}
```

```toml
[package]
name = "rust_async_test"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
tokio = { version = "1", features = ["full"] }
```

### into

`Into` trait 是一種常見的用於類型轉換的 trait，但並不是唯一的方式。Rust 還提供了一種簡化類型轉換的手段，即使用 `Into` trait 的 `into` 方法。

在 Rust 中，對於任何實現了 `From` trait 的類型，都可以使用 `into` 方法進行類型轉換。這是因為 `Into` trait 是 `From` trait 的逆。具體來說，`Into<T>` trait 的實現是由 `T` 實現的 `From<U>` trait 決定的。

```rust
// 定義一個結構 Point
struct Point {
    x: i32,
    y: i32,
}

// 實現 Into<T> trait for Point
impl Into<(i32, i32)> for Point {
    fn into(self) -> (i32, i32) {
        (self.x, self.y)
    }
}

fn main() {
    // 創建一個 Point 實例
    let point = Point { x: 10, y: 20 };

    // 使用 .into() 將 Point 轉換成 (i32, i32)
    let tuple: (i32, i32) = point.into();

    // 打印轉換後的結果
    println!("Tuple: {:?}", tuple);
}
```

```rust
// 定義一個結構 Point
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // 創建一個 Point 實例
    let point = Point { x: 10, y: 20 };

    // 使用 .into() 將 Point 轉換成 (i32, i32)
    let tuple: (i32, i32) = point.into();

    // 打印轉換後的結果
    println!("Tuple: {:?}", tuple);
}
```

struct 用於定義結構體（structure），即一種用來組織和存儲數據的自定義類型。而 trait 則用於定義接口，即一組方法的集合，這些方法可以被實現在各種不同的類型上。

```rust
// 定義特徵 Displayable
trait Displayable {
    fn display(&self);
}

// 實現特徵 Displayable for Point
struct Point {
    x: f64,
    y: f64,
}

impl Displayable for Point {
    fn display(&self) {
        println!("Point: ({}, {})", self.x, self.y);
    }
}

// 實現特徵 Displayable for Circle
struct Circle {
    radius: f64,
}

impl Displayable for Circle {
    fn display(&self) {
        println!("Circle with radius: {}", self.radius);
    }
}

// 定義特徵 Add
trait Add {
    fn add(&self, other: &Self) -> Self;
}

// 實現特徵 Add for i32
impl Add for i32 {
    fn add(&self, other: &Self) -> Self {
        *self + *other
    }
}

// 實現特徵 Add for f64
impl Add for f64 {
    fn add(&self, other: &Self) -> Self {
        *self + *other
    }
}

// 定義特徵 Double
trait Double {
    fn double(&self) -> Self;
}

// 實現特徵 Double for i32
impl Double for i32 {
    fn double(&self) -> Self {
        *self * 2
    }
}

// 實現特徵 Double for f64
impl Double for f64 {
    fn double(&self) -> Self {
        *self * 2.0
    }
}

// 主函數
fn main() {
    // 使用 Displayable 特徵的方法
    let point = Point { x: 1.0, y: 2.0 };
    point.display();

    let circle = Circle { radius: 3.0 };
    circle.display();

    // 使用 Add 特徵的方法
    let sum_i32 = 10i32.add(&5);
    let sum_f64 = 3.5f64.add(&2.5);

    println!("Sum of i32: {}", sum_i32);
    println!("Sum of f64: {}", sum_f64);

    // 使用 Double 特徵的方法
    let doubled_i32 = 7i32.double();
    let doubled_f64 = 4.2f64.double();

    println!("Doubled i32: {}", doubled_i32);
    println!("Doubled f64: {}", doubled_f64);
}
```

```rust
// 定義特徵 Add
trait Add {
    fn add(&self, other: &Self) -> Self;
}

// 實現特徵 Add for i32
impl Add for i32 {
    fn add(&self, other: &Self) -> Self {
        *self + *other
    }
}

// 實現特徵 Add for f64
impl Add for f64 {
    fn add(&self, other: &Self) -> Self {
        *self + *other
    }
}

// 主函數
fn main() {
    // 使用 Add 特徵的方法
    let sum_i32 = 10i32.add(&5);
    let sum_f64 = 3.5f64.add(&2.5);

    println!("Sum of i32: {}", sum_i32);
    println!("Sum of f64: {}", sum_f64);
}
```

## 多型（polymorphism）

在 Rust 中通常是通過 trait 和泛型實現的。下面是一個簡單的多型範例，其中使用了 trait 和泛型，允許一個函數接受不同類型的參數：

```rust
// 定義一個特徵 Display
trait Display {
    fn display(&self);
}

// 實現 Display 特徵的結構體 Point
struct Point {
    x: f64,
    y: f64,
}

impl Display for Point {
    fn display(&self) {
        println!("Point: ({}, {})", self.x, self.y);
    }
}

// 實現 Display 特徵的結構體 Circle
struct Circle {
    radius: f64,
}

impl Display for Circle {
    fn display(&self) {
        println!("Circle with radius: {}", self.radius);
    }
}

// 多型函數，接受實現 Display 特徵的任意類型
fn show_displayable<T: Display>(item: T) {
    item.display();
}

fn main() {
    let point = Point { x: 1.0, y: 2.0 };
    let circle = Circle { radius: 3.0 };

    // 調用多型函數，可以接受不同類型的參數
    show_displayable(point);
    show_displayable(circle);
}
```

## 泛型

```rust
// 定義一個泛型函數，接受兩個參數並返回它們的和
fn add<T>(a: T, b: T) -> T
where
    T: std::ops::Add<Output = T>,
{
    a + b
}

fn main() {
    // 使用泛型函數，可以處理不同類型的數據
    let sum_i32 = add(5, 3);
    let sum_f64 = add(3.5, 2.5);

    println!("Sum of i32: {}", sum_i32);
    println!("Sum of f64: {}", sum_f64);
}
```

在這個範例中，`add` 函數是一個泛型函數，它接受兩個相同類型的參數 `a` 和 `b`，並返回它們的和。泛型參數 `T` 表示可以是任何類型。`where T: std::ops::Add<Output = T>` 確保 `T` 實現了 `Add` trait，並指定了 `Output` 類型為 `T`。

在 `main` 函數中，我們分別使用整數和浮點數調用了 `add` 函數，顯示了泛型函數可以處理不同類型的數據並返回正確的結果。

在上述的泛型範例中，`where T: std::ops::Add<Output = T>` 是一個泛型約束（generic constraint）子句，用於指定泛型參數 `T` 必須滿足的條件。

這個約束的意義是，泛型參數 `T` 必須實現 `std::ops::Add` trait，並且其 `Add` 實現的輸出類型（Output）必須是 `T`。換句話說，`T` 只能與自己相加，而不是與其他類型相加。

這樣的約束確保了 `add` 函數在編譯時期只能被用於那些支持 `+` 運算的類型，並保證了在編譯時期就能夠確定 `add` 函數的行為。

不使用 `where` 子句的版本可能看起來像這樣：

```rust
fn add<T: std::ops::Add<Output = T>>(a: T, b: T) -> T {
    a + b
}
```

```rust
fn multiply_value<T>(value: T, factor: T) -> T
where
    T: std::ops::Mul<Output = T>,
{
    value * factor
}

fn main() {
    let integer_result = multiply_value(5, 3);
    let float_result = multiply_value(3.5, 2.0);

    println!("Result of multiplying integers: {}", integer_result);
    println!("Result of multiplying floats: {}", float_result);
}
```

`where` 子句的存在讓約束條件更為清晰，有時可以提高代碼的可讀性，特別是當約束條件較長或較複雜時。這種寫法的主要優勢是可以將約束從函數的簽名中分離出來，讓簽名更加簡潔。

總體而言，`where` 子句的使用是為了確定泛型參數滿足特定的條件，提高代碼的可讀性和可維護性。

## `#[derive(Debug)] `

使用 `#[derive(Debug)]` 時，Rust 編譯器會自動生成一個 `Debug` trait 的實現。這個生成的實現通常包含一個 `fmt::Debug` trait 的 `fmt` 方法，該方法負責將類型的偵錯表示格式化為字串。

```rust
#[derive(Debug)]
struct Point {
    x: f64,
    y: f64,
}
```

當你使用 `#[derive(Debug)]` 註解時，Rust 編譯器會自動生成類似以下的程式碼：

```rust
impl std::fmt::Debug for Point {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        // 使用 Formatter 將調試信息格式化為字符串
        f.debug_struct("Point")
            .field("x", &self.x)
            .field("y", &self.y)
            .finish()
    }
}
```

這個生成的實現為 `Point` 類型實現了 `Debug` trait 中的 `fmt` 方法。在這個方法中，使用了 `std::fmt::Debug` 中提供的 `debug_struct`、`field` 和 `finish` 方法來建構偵錯表示。具體來說：

- `debug_struct("Point")` 建立一個名為 "Point" 的偵錯結構體。
- `field("x", &self.x)` 新增一個名為 "x" 的欄位，並將 `self.x` 的偵錯表示新增到結構體中。
- `field("y", &self.y)` 同樣新增一個名為 "y" 的欄位，並將 `self.y` 的偵錯表示新增到結構體中。
- `finish()` 完成結構體的建構，生成最終的偵錯表示。

這樣，當你使用 `println!` 宏並使用 `{:?}` 預留位置列印 `Point` 類型的實例時，編譯器自動生成的 `Debug` trait 實現將被呼叫，輸出類似於 `Point { x: 3.0, y: 4.0 }` 的偵錯資訊。這種自動生成的實現簡化了偵錯過程，使得偵錯資訊更加易讀和友好。

## Result

`Result` 是一個列舉類型，用於表示函數執行的結果，特別是可能發生錯誤的情況。`Result` 的定義如下：

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

這裡有兩個變數，`T` 和 `E`。`T` 代表成功時返回的值的類型，而 `E` 代表錯誤時返回的值的類型。`Result` 列舉有兩個變體：

1. `Ok(T)`: 表示操作成功，包含一個成功時返回的值 `T`。
2. `Err(E)`: 表示操作發生錯誤，包含一個錯誤時返回的值 `E`。

例如，一個函數可能返回 `Result` 類型來表示執行結果：

```rust
fn divide(a: i32, b: i32) -> Result<i32, &'static str> {
    if b == 0 {
        // 如果嘗試除以零，則返回一個 Err 變體，包含錯誤信息
        Err("Cannot divide by zero!")
    } else {
        // 如果成功，返回 Ok 變體，包含結果值
        Ok(a / b)
    }
}
```

`Result<i32, &'static str>` 是一個 `Result` 類型的實例，表示可能返回一個整數（`i32`類型）的成功結果，或者返回一個靜態字串切片（`&'static str`類型）的錯誤資訊。

讓我們詳細解釋這個類型：

- `Result`: 這是Rust標準庫中的列舉類型，用於表示操作的結果，可以是成功的值（`Ok`變體）或錯誤的值（`Err`變體）。
- `<i32, &'static str>`: 這是 `Result` 的兩個類型參數。第一個參數 `i32` 表示成功時返回的值的類型，第二個參數 `&'static str` 表示錯誤時返回的值的類型。`&'static str` 是一個指向靜態字串切片的引用，通常用於表示在整個程序生命週期中都有效的字串。

在使用 `Result` 類型時，通常會使用模式匹配（pattern matching）或 `Result` 的方法來處理操作的成功和失敗情況。例如：

```rust
match divide(10, 2) {
    Ok(result) => println!("Result: {}", result),
    Err(err) => println!("Error: {}", err),
}
```

或者使用 `unwrap`、`expect`、`map`、`and_then` 等方法進行更複雜的處理。這樣的設計使得在Rust中明確處理可能發生的錯誤，避免了在執行階段出現未處理的異常。這也是Rust中的一種推崇錯誤處理的哲學，通過強制使用 `Result` 類型鼓勵開發者更加關注和處理潛在的錯誤情況。

## 模擬 Result 列舉

```rust
enum _Result<T, E> {
    Ok(T),
    Err(E),
}

fn divide(a: i32, b: i32) -> _Result<i32, &'static str> {
    if b == 0 {
        // 如果嘗試除以零，則返回一個 Err 變體，包含錯誤信息
        _Result::Err("Cannot divide by zero!")
    } else {
        // 如果成功，返回 Ok 變體，包含結果值
        _Result::Ok(a / b)
    }
}

fn main() {
    match divide(10, 2) {
        _Result::Ok(result) => println!("Result: {}", result),
        _Result::Err(err) => println!("Error: {}", err),
    }
}
```

## Rust中字串操作的擁有權和可變引用

這兩個程式碼的主要區別在於函數 `greet` 如何處理字串的擁有權（ownership）：

### 第一個範例：

```rust
rustCopy codefn greet(mut message: String) -> String {
    message.push_str(", World!"); // 修改字串的內容
    println!("{}", message);
    message
}

fn main() {
    let message = String::from("Hello");
    println!("{}", message);
    let msg = greet(message);
    println!("{}", msg);
}
```

1. `greet` 函數接受一個 `String` 的擁有權，對它進行修改（push_str），然後返回修改後的字串，同時也轉移了擁有權。
2. 在 `main` 函數中，`message` 的擁有權在調用 `greet` 函數時轉移到了 `greet` 內，因此 `main` 無法再使用原始的 `message`。

### 第二個範例：

```rust
rustCopy codefn greet(message: &mut String) {
    message.push_str(", World!"); // 修改字串的內容
    println!("{}", message);
}

fn main() {
    let mut message = String::from("Hello");
    println!("{}", message);

    greet(&mut message); // 傳遞字串的可變引用
    println!("{}", message);
}
```

1. `greet` 函數接受一個 `&mut String`，這是字串的可變引用，它允許 `greet` 修改字串的內容，但不轉移擁有權。
2. 在 `main` 函數中，`message` 保留了擁有權，你可以通過傳遞 `&mut message` 來傳遞對字串的可變引用，使 `greet` 能夠修改字串的內容。
3. `main` 仍然擁有 `message` 並且可以在 `greet` 被呼叫後繼續使用修改後的 `message`。

總的來說，第二個範例使用了引用和可變引用，保留了 `message` 的擁有權，允許在函數間進行資料的共享，而不是轉移擁有權。


##  Borrow Checker 的限制
 Rust 的 Borrow Checker 的限制，這是為了確保在編譯時能夠避免數據競爭和安全性問題。具體來說，在同一個作用域中，你不能同時擁有兩個可變引用指向同一個值。這就是為什麼你無法同時擁有 a 和 b 兩個可變引用指向 array 的兩個元素的原因。

Rust 提供了一些方法來處理這種情況，其中一個方法是使用 .split_at_mut() 方法來將陣列分成兩個不重疊的可變引用。這裡是如何修改你的程式碼以解決這個問題：
```rust
fn main() {
    let mut array = [123, 456];
    
    // 將陣列拆分成兩個可變引用，分別指向不同的元素
    let (a, b) = array.split_at_mut(1);
    let a = &mut a[0];
    let b = &mut b[0];
    
    *a = 789;
    *b = 101112;
    println!("{:?}", array);
}
```
