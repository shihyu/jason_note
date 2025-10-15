# stack

## stack簡介

- stack作為一種數據結構，是一種只能在**一端**進行**插入**和**刪除**操作的特殊線性表。

- 它按照**先進後出**的原則存儲數據，先進入的數據被壓入stack底，最後的數據在stack頂，需要讀數據的時候從stack頂開始彈出數據（最後一個數據被第一個讀出來）。

>stack（stack）又名heapstack，它是一種運算受限的線性表。其限制是僅允許在表的一端進行插入和刪除運算。這一端被稱為stack頂，相對地，把另一端稱為stack底。向一個stack插入新元素又稱作進stack、入stack或壓stack，它是把新元素放到stack頂元素的上面，使之成為新的stack頂元素；從一個stack刪除元素又稱作出stack或退stack，它是把stack頂元素刪除掉，使其相鄰的元素成為新的stack頂元素。

## stack的實現步驟：

- 定義一個stack結構`Stack`
- 定義組成stack結構的stack點`StackNode`
- 實現stack的初始化函數`new( )`
- 實現進stack函數`push( )`
- 實現退stack函數`pop( )`

## 定義一個stack結構`Stack`

```rust
#[derive(Debug)]
struct Stack<T> {
    top: Option<Box<StackNode<T>>>,
}
```

讓我們一步步來分析

- 第一行的`#[derive(Debug)]`是為了讓`Stack`結構體可以打印調試。
- 第二行是定義了一個`Stack`結構體，這個結構體包含一個泛型參數`T`。
- 第三行比較複雜，在定義`StackNode`的時候介紹

## 定義組成stack結構的stack點`StackNode`

```rust
#[derive(Clone,Debug)]
struct StackNode<T> {
    val: T,
    next: Option<Box<StackNode<T>>>,
}
```

在這段代碼的第三行， 我們定義了一個`val`保存`StackNode`的值。

>現在我們重點來看看第四行：
我們**從裡到外**拆分來看看，首先是`Box<StackNode<T>`，這裡的`Box`是 Rust 用來顯式分配heap內存的類型：

> `pub struct Box<T> where T: ?Sized(_);`  
[詳細文檔請參考Rust的標準庫](http://doc.rust-lang.org/nightly/std/boxed/struct.Box.html)

> 在 Rust 裡面用強大的類型系統做了統一的抽象。在這裡相當於在heap空間裡申請了一塊內存保存`StackNode<T>`。  

> **為什麼要這麼做了？如果不用Box封裝會怎麼樣呢？**  

> 如果不用 Box 封裝，rustc 編譯器會報錯，在 Rust 裡面，rustc 默認使用stack空間，但是這裡的`StackNode`定義的時候使用了遞歸的數據結構，next 屬性的類型是 `StackNode<T>`，而這個類型是無法確定大小的，所有這種無法確定大小的類型，都不能保存在stack空間。所以需要使用`Box`來封裝。這樣的話`next`的類型就是一個指向某一塊heap空間的指針，而指針是可以確定大小的，因此能夠保存在stack空間。  

> **那麼為什麼還需要使用`Option`來封裝呢？**  

> `Option`是 Rust 裡面的一個抽象類型，定義如下：  
>

```rust
pub enum Option<T> {
    None,
    Some(T),
}
```

Option 裡面包括元素，None 和 Some(T) ，這樣就很輕鬆的描述了 next 指向stack尾的元素的時候，都是在 Option 類型下，方便了功能實現，也方便了錯誤處理。Option 還有很多強大的功能，讀者可以參考下面幾個連接：

[Option標準庫文檔](http://doc.rust-lang.org/nightly/std/option/enum.Option.html)

[Error Handling in Rust](http://blog.burntsushi.net/rust-error-handling/)

[rustbyexample 的 Error handling](https://doc.rust-lang.org/stable/rust-by-example/error.html)

## 實現 `new( ) push( ) pop( )`
接下來是實現 stack 的主要功能了。

```rust
impl<T> Stack<T> {
    fn new() -> Stack<T> {
        Stack{ top: None }
    }

    fn push(&mut self, val: T) {
        let mut node = StackNode::new(val);
        let next = self.top.take();
        node.next = next;
        self.top = Some(Box::new(node));
    }

    fn pop(&mut self) -> Option<T> {
        let val = self.top.take();
        match val {
            None => None,
            Some(mut x) => {
                self.top = x.next.take();
                Some(x.val)
            },
        }
    }
}
```

- `new( )`比較簡單，Stack 初始化的時候為空，stack頂元素 `top` 就沒有任何值，所以 `top` 為 `None`。

- `push( )`的主要功能是往stack裡面推入元素，把新的 StackNode 指向 Stack 裡面舊的值，同時更新 Stack stack頂指向新進來的值。
> 這裡有個需要注意的地方是第8行代碼裡面，`let next = self.top.take();`，使用了 Option 類型的 take 方法：  
`fn take(&mut self) -> Option<T>`
它會把 Option 類型的值取走，並把它的元素改為 None

- `pop( )`的功能是取出stack頂的元素，如果stack頂為 None 則返回 None。

## 完整代碼（包含簡單的測試）

```rust
#[derive(Debug)]
struct Stack<T> {
    top: Option<Box<StackNode<T>>>,
}

#[derive(Clone,Debug)]
struct StackNode<T> {
    val: T,
    next: Option<Box<StackNode<T>>>,
}

impl <T> StackNode<T> {
    fn new(val: T) -> StackNode<T> {
        StackNode { val: val, next: None }
    }
}

impl<T> Stack<T> {
    fn new() -> Stack<T> {
        Stack{ top: None }
    }

    fn push(&mut self, val: T) {
        let mut node = StackNode::new(val);
        let next = self.top.take();
        node.next = next;
        self.top = Some(Box::new(node));
    }

    fn pop(&mut self) -> Option<T> {
        let val = self.top.take();
        match val {
            None => None,
            Some(mut x) => {
                self.top = x.next.take();
                Some(x.val)
            },
        }
    }
}

fn main() {
    #[derive(PartialEq,Eq,Debug)]
    struct TestStruct {
        a: i32,
    }

    let a = TestStruct{ a: 5 };
    let b = TestStruct{ a: 9 };

    let mut s = Stack::<&TestStruct>::new();
    assert_eq!(s.pop(), None);

    s.push(&a);
    s.push(&b);
    println!("{:?}", s);

    assert_eq!(s.pop(), Some(&b));
    assert_eq!(s.pop(), Some(&a));
    assert_eq!(s.pop(), None);
}
```
