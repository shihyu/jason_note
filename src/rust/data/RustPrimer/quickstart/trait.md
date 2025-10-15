# 特性

## 特性與接口
為了描述類型可以實現的抽象接口 (abstract interface)，
Rust引入了特性 (trait) 來定義函數類型簽名 (function type signature)：

```rust
trait HasArea {
    fn area(&self) -> f64;
}

struct Circle {
    x: f64,
    y: f64,
    radius: f64,
}

impl HasArea for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * (self.radius * self.radius)
    }
}

struct Square {
    x: f64,
    y: f64,
    side: f64,
}

impl HasArea for Square {
    fn area(&self) -> f64 {
        self.side * self.side
    }
}

fn print_area<T: HasArea>(shape: T) {
    println!("This shape has an area of {}", shape.area());
}
```

其中函數`print_area()`中的泛型參數`T`被添加了一個名為`HasArea`的特性約束 (trait constraint)，
用以確保任何實現了`HasArea`的類型將擁有一個`.area()`方法。
如果需要多個特性限定 (multiple trait bounds)，可以使用`+`：

```rust
use std::fmt::Debug;

fn foo<T: Clone, K: Clone + Debug>(x: T, y: K) {
    x.clone();
    y.clone();
    println!("{:?}", y);
}

fn bar<T, K>(x: T, y: K)
    where T: Clone,
          K: Clone + Debug
{
    x.clone();
    y.clone();
    println!("{:?}", y);
}
```

其中第二個例子使用了更靈活的`where`從句，它還允許限定的左側可以是任意類型，
而不僅僅是類型參數。

定義在特性中的方法稱為默認方法 (default method)，可以被該特性的實現覆蓋。
此外，特性之間也可以存在繼承 (inheritance)：

```rust
trait Foo {
    fn foo(&self);

    // default method
    fn bar(&self) { println!("We called bar."); }
}

// inheritance
trait FooBar : Foo {
    fn foobar(&self);
}

struct Baz;

impl Foo for Baz {
    fn foo(&self) { println!("foo"); }
}

impl FooBar for Baz {
    fn foobar(&self) { println!("foobar"); }
}
```

如果兩個不同特性的方法具有相同的名稱，可以使用通用函數調用語法 (universal function call syntax)：

```rust
// short-hand form
Trait::method(args);

// expanded form
<Type as Trait>::method(args);
```

關於實現特性的幾條限制：

* 如果一個特性不在當前作用域內，它就不能被實現。
* 不管是特性還是`impl`，都只能在當前的包裝箱內起作用。
* 帶有特性約束的泛型函數使用單態化實現 (monomorphization)，
所以它是靜態派分的 (statically dispatched)。

下面列舉幾個非常有用的標準庫特性：

* `Drop`提供了當一個值退出作用域後執行代碼的功能，它只有一個`drop(&mut self)`方法。
* `Borrow`用於創建一個數據結構時把擁有和借用的值看作等同。
* `AsRef`用於在泛型中把一個值轉換為引用。
* `Deref<Target=T>`用於把`&U`類型的值自動轉換為`&T`類型。
* `Iterator`用於在集合 (collection) 和惰性值生成器 (lazy value generator) 上實現迭代器。
* `Sized`用於標記運行時長度固定的類型，而不定長的切片和特性必須放在指針後面使其運行時長度已知，
比如`&[T]`和`Box<Trait>`。

## 泛型和多態

泛型 (generics) 在類型理論中稱作參數多態 (parametric polymorphism)，
意為對於給定參數可以有多種形式的函數或類型。先看Rust中的一個泛型例子：  

Option在rust標準庫中的定義:  

```rust
enum Option<T> {
    Some(T),
    None,
}
```
Option的典型用法:  
```rust
let x: Option<i32> = Some(5);
let y: Option<f64> = Some(5.0f64);
```

其中`<T>`部分表明它是一個泛型數據類型。當然，泛型參數也可以用於函數參數和結構體域：

```rust
// generic functions
fn make_pair<T, U>(a: T, b: U) -> (T, U) {
    (a, b)
}
let couple = make_pair("man", "female");

// generic structs
struct Point<T> {
    x: T,
    y: T,
}
let int_origin = Point { x: 0, y: 0 };
let float_origin = Point { x: 0.0, y: 0.0 };
```

對於多態函數，存在兩種派分 (dispatch) 機制：靜態派分和動態派分。
前者類似於C++的模板，Rust會生成適用於指定類型的特殊函數，然後在被調用的位置進行替換，
好處是允許函數被內聯調用，運行比較快，但是會導致代碼膨脹 (code bloat)；
後者類似於Java或Go的`interface`，Rust通過引入特性對象 (trait object) 來實現，
在運行期查找虛表 (vtable) 來選擇執行的方法。特性對象`&Foo`具有和特性`Foo`相同的名稱，
通過轉換 (casting) 或者強制多態化 (coercing) 一個指向具體類型的指針來創建。

當然，特性也可以接受泛型參數。但是，往往更好的處理方式是使用關聯類型 (associated type)：

```rust
// use generic parameters
trait Graph<N, E> {
    fn has_edge(&self, &N, &N) -> bool;
    fn edges(&self, &N) -> Vec<E>;
}

fn distance<N, E, G: Graph<N, E>>(graph: &G, start: &N, end: &N) -> u32 {

}

// use associated types
trait Graph {
    type N;
    type E;

    fn has_edge(&self, &Self::N, &Self::N) -> bool;
    fn edges(&self, &Self::N) -> Vec<Self::E>;
}

fn distance<G: Graph>(graph: &G, start: &G::N, end: &G::N) -> uint {

}

struct Node;

struct Edge;

struct SimpleGraph;

impl Graph for SimpleGraph {
    type N = Node;
    type E = Edge;

    fn has_edge(&self, n1: &Node, n2: &Node) -> bool {

    }

    fn edges(&self, n: &Node) -> Vec<Edge> {

    }
}

let graph = SimpleGraph;
let object = Box::new(graph) as Box<Graph<N=Node, E=Edge>>;

```

