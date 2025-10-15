# Cell, RefCell

前面我們提到，Rust 通過其所有權機制，嚴格控制擁有和借用關係，來保證程序的安全，並且這種安全是在編譯期可計算、可預測的。但是這種嚴格的控制，有時也會帶來靈活性的喪失，有的場景下甚至還滿足不了需求。

因此，Rust 標準庫中，設計了這樣一個系統的組件：`Cell`, `RefCell`，它們彌補了 Rust 所有權機制在靈活性上和某些場景下的不足。同時，又沒有打破 Rust 的核心設計。它們的出現，使得 Rust 革命性的語言理論設計更加完整，更加實用。

具體是因為，它們提供了 `內部可變性`（相對於標準的 `繼承可變性` 來講的）。

通常，我們要修改一個對象，必須

1. 成為它的擁有者，並且聲明 `mut`；
2. 或 以 `&mut` 的形式，借用；

而通過 `Cell`, `RefCell`，我們可以在需要的時候，就可以修改裡面的對象。而不受編譯期靜態借用規則束縛。

## `Cell`

`Cell` 有如下特點：

1. `Cell<T>` 只能用於 `T` 實現了 `Copy` 的情況；

### `.get()`

`.get()` 方法，返回內部值的一個拷貝。比如：

```rust
use std::cell::Cell;

let c = Cell::new(5);

let five = c.get();
```

### `.set()`

`.set()` 方法，更新值。

```rust
use std::cell::Cell;

let c = Cell::new(5);

c.set(10);
```


## `RefCell`

相對於 `Cell` 只能包裹實現了 `Copy` 的類型，`RefCell` 用於更普遍的情況（其它情況都用 `RefCell`）。

相對於標準情況的 `靜態借用`，`RefCell` 實現了 `運行時借用`，這個借用是臨時的。這意味著，編譯器對 `RefCell` 中的內容，不會做靜態借用檢查，也意味著，出了什麼問題，用戶自己負責。

`RefCell` 的特點：

1. 在不確定一個對象是否實現了 `Copy` 時，直接選 `RefCell`；
2. 如果被包裹對象，同時被可變借用了兩次，則會導致線程崩潰。所以需要用戶自行判斷；
3. `RefCell` 只能用於線程內部，不能跨線程；
4. `RefCell` 常常與 `Rc` 配合使用（都是單線程內部使用）；

我們來看實例：

```rust
use std::collections::HashMap;
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let shared_map: Rc<RefCell<_>> = Rc::new(RefCell::new(HashMap::new()));
    shared_map.borrow_mut().insert("africa", 92388);
    shared_map.borrow_mut().insert("kyoto", 11837);
    shared_map.borrow_mut().insert("piccadilly", 11826);
    shared_map.borrow_mut().insert("marbles", 38);
}
```

從上例可看出，用了 `RefCell` 後，外面是 `不可變引用` 的情況，一樣地可以修改被包裹的對象。

常用方法
### `.borrow()`
不可變借用被包裹值。同時可存在多個不可變借用。

比如：

```rust
use std::cell::RefCell;

let c = RefCell::new(5);

let borrowed_five = c.borrow();
let borrowed_five2 = c.borrow();
```

下面的例子會崩潰：

```rust
use std::cell::RefCell;
use std::thread;

let result = thread::spawn(move || {
   let c = RefCell::new(5);
   let m = c.borrow_mut();

   let b = c.borrow(); // this causes a panic
}).join();

assert!(result.is_err());
```

### `.borrow_mut()`

可變借用被包裹值。同時只能有一個可變借用。

比如：

```rust
use std::cell::RefCell;

let c = RefCell::new(5);

let borrowed_five = c.borrow_mut();
```

下面的例子會崩潰：

```rust
use std::cell::RefCell;
use std::thread;

let result = thread::spawn(move || {
   let c = RefCell::new(5);
   let m = c.borrow();

   let b = c.borrow_mut(); // this causes a panic
}).join();

assert!(result.is_err());
```

### `.into_inner()`

取出包裹值。

```rust
use std::cell::RefCell;

let c = RefCell::new(5);

let five = c.into_inner();
```

## 一個綜合示例

下面這個示例，表述的是如何實現兩個對象的循環引用。綜合演示了 `Rc`, `Weak`, `RefCell` 的用法

```rust

use std::rc::Rc;
use std::rc::Weak;
use std::cell::RefCell;

struct Owner {
    name: String,
    gadgets: RefCell<Vec<Weak<Gadget>>>,
    // 其他字段
}

struct Gadget {
    id: i32,
    owner: Rc<Owner>,
    // 其他字段
}

fn main() {
    // 創建一個可計數的Owner。
    // 注意我們將gadgets賦給了Owner。
    // 也就是在這個結構體裡， gadget_owner包含gadets
    let gadget_owner : Rc<Owner> = Rc::new(
        Owner {
            name: "Gadget Man".to_string(),
            gadgets: RefCell::new(Vec::new()),
        }
    );

    // 首先，我們創建兩個gadget，他們分別持有 gadget_owner 的一個引用。
    let gadget1 = Rc::new(Gadget{id: 1, owner: gadget_owner.clone()});
    let gadget2 = Rc::new(Gadget{id: 2, owner: gadget_owner.clone()});

    // 我們將從gadget_owner的gadgets字段中持有其可變引用
    // 然後將兩個gadget的Weak引用傳給owner。
    gadget_owner.gadgets.borrow_mut().push(Rc::downgrade(&gadget1));
    gadget_owner.gadgets.borrow_mut().push(Rc::downgrade(&gadget2));

    // 遍歷 gadget_owner的gadgets字段
    for gadget_opt in gadget_owner.gadgets.borrow().iter() {

        // gadget_opt 是一個 Weak<Gadget> 。 因為 weak 指針不能保證他所引用的對象
        // 仍然存在。所以我們需要顯式的調用 upgrade() 來通過其返回值(Option<_>)來判
        // 斷其所指向的對象是否存在。
        // 當然，這個Option為None的時候這個引用原對象就不存在了。
        let gadget = gadget_opt.upgrade().unwrap();
        println!("Gadget {} owned by {}", gadget.id, gadget.owner.name);
    }

    // 在main函數的最後， gadget_owner, gadget1和daget2都被銷燬。
    // 具體是，因為這幾個結構體之間沒有了強引用（`Rc<T>`），所以，當他們銷燬的時候。
    // 首先 gadget1和gadget2被銷燬。
    // 然後因為gadget_owner的引用數量為0，所以這個對象可以被銷燬了。
    // 循環引用問題也就避免了
}
```
