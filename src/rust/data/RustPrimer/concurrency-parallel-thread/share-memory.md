## 共享內存
在消息傳遞之外，還存在一種廣為人知的併發模型，那就是共享內存。其實如果不能共享內存，消息傳遞也是不能在不同的線程間傳遞消息，也談不上在不同的線程間等待和通知了。共享內存是這一切得以發生的基礎。如果查看源碼，你會發現消息傳遞的內部實現就是借用了共享內存機制。相對於消息傳遞而言，共享內存會有更多的競爭，但是不用進行多次拷貝，在某些情況下，也需要考慮使用這種方式來處理。在Rust中，能共享內存的情況，主要體現在下面兩個方面：

### static
Rust語言中也存在static變量，其生命週期是整個應用程序，並且在內存中某個固定地址處只存在一份實例。所有線程都能夠訪問到它。這種方式也是最簡單和直接的共享方式。幾乎大多數語言都存在這種機制。下面簡單看一下Rust中多個線程訪問static變量的用法：

```rust
use std::thread;

static VAR: i32 = 5;

fn main() {
	// 創建一個新線程
	let new_thread = thread::spawn(move|| {
	    println!("static value in new thread: {}", VAR);
	});

	// 等待新線程先運行
	new_thread.join().unwrap();
	println!("static value in main thread: {}", VAR);
}
```

運行結果：

```
static value in new thread: 5
static value in main thread: 5
```

`VAR`這個`static`變量在各線程中可以直接使用，非常方便。當然上面只是讀取，那麼要修改也是很簡單的：

```rust
use std::thread;

static mut VAR: i32 = 5;

fn main() {
	// 創建一個新線程
	let new_thread = thread::spawn(move|| {
	    unsafe {
	    	println!("static value in new thread: {}", VAR);
	    	VAR = VAR + 1;
	    }
	});

	// 等待新線程先運行
	new_thread.join().unwrap();
	unsafe {
		println!("static value in main thread: {}", VAR);
	}
}
```

運行結果：

```
static value in new thread: 5
static value in main thread: 6
```

從結果來看`VAR`的值變了，從代碼上來看，除了在`VAR`變量前面加了`mut`關鍵字外，更加明顯的是在使用`VAR`的地方都添加了`unsafe`代碼塊。為什麼？所有的線程都能訪問`VAR`，且它是可以被修改的，自然就是不安全的。上面的代碼比較簡單，同一時間只會有一個線程讀寫`VAR`，不會有什麼問題，所以用`unsafe`來標記就可以。如果是更多的線程，還是請使用接下來要介紹的同步機制來處理。

static如此，那const呢？ const會在編譯時內聯到代碼中，所以不會存在某個固定的內存地址上，也不存在可以修改的情況，並不是內存共享的。

### 堆
由於現代操作系統的設計，線程寄生於進程，可以共享進程的資源，如果要在各個線程中共享一個變量，那麼除了上面的static，還有就是把變量保存在堆上了。當然Rust也不例外，遵從這一設計。只是我們知道Rust在安全性上肯定又會做一些考量，從而在語言設計和使用上稍有不同。

為了在堆上分配空間，Rust提供了`std::boxed::Box`，由於堆的特點，存活時間比較長，所以除了我們這個地方介紹的線程間共享外，還有其他的用處，此處不詳細說明，若不甚瞭解，請學習或回顧**堆、棧與Box**章節的介紹。下面我們來看一下如何在多個線程間訪問`Box`創建的變量：

```rust
use std::thread;
use std::sync::Arc;

fn main() {
	let var : Arc<i32> = Arc::new(5);
	let share_var = var.clone();

	// 創建一個新線程
	let new_thread = thread::spawn(move|| {
		println!("share value in new thread: {}, address: {:p}", share_var, &*share_var);
	});

	// 等待新建線程先執行
	new_thread.join().unwrap();
	println!("share value in main thread: {}, address: {:p}", var, &*var);
}
```

運行結果：

```
share value in new thread: 5, address: 0x2825070
share value in main thread: 5, address: 0x2825070
```

你可能會覺得很奇怪，上面怎麼沒有看到Box創建的變量啊，這明明就是`Arc`的使用呀？`Box`創建的變量要想在多個線程中安全使用，我們還需要實現很多功能才行，需要是`Sync`，而`Arc`正是利用`Box`來實現的一個通過引用計數來共享狀態的包裹類。下面引用一段`Arc::new`的源碼即可看出它是通過`Box`來實現的：

```rust
pub fn new(data: T) -> Arc<T> {
    // Start the weak pointer count as 1 which is the weak pointer that's
    // held by all the strong pointers (kinda), see std/rc.rs for more info
    let x: Box<_> = box ArcInner {
        strong: atomic::AtomicUsize::new(1),
        weak: atomic::AtomicUsize::new(1),
        data: data,
    };
    Arc { _ptr: unsafe { NonZero::new(Box::into_raw(x)) } }
}
```

通過上面的運行結果，我們也可以發現新建線程和主線程中打印的`address`是一樣的，說明狀態確實是在同一個內存地址處。

如果`Box`在堆上分配的資源僅在一個線程中使用，那麼釋放時，就非常簡單，使用完，及時釋放即可。如果是要在多個線程中使用，就需要面臨兩個關鍵問題：

1. 資源何時釋放？
2. 線程如何安全的併發修改和讀取？

由於上面兩個問題的存在，這就是為什麼我們不能直接用`Box`變量在線程中共享的原因，可以看出來，共享內存比消息傳遞機制似乎要複雜許多。Rust用了引用計數的方式來解決第一個問題，在標準庫中提供了兩個包裹類，除了上面一個用於多線程的`std::sync::Arc`之外，還有一個不能用於多線程的`std::rc::Rc`。在使用時，可以根據需要進行選擇。如果你一不小心把`std::rc::Rc`用於多線程中，編譯器會毫不客氣地糾正你的。

關於上面的第二個問題，Rust語言及標準庫提供了一系列的同步手段來解決。下面的章節我們將詳細講解這些方式和用法。
