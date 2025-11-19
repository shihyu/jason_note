## 同步

同步指的是線程之間的協作配合，以共同完成某個任務。在整個過程中，需要注意兩個關鍵點：一是共享資源的訪問， 二是訪問資源的順序。通過前面的介紹，我們已經知道了如何讓多個線程訪問共享資源，但並沒介紹如何控制訪問順序，才不會出現錯誤。如果兩個線程同時訪問同一內存地址的數據，一個寫，一個讀，如果不加控制，寫線程只寫了一半，讀線程就開始讀，必然讀到的數據是錯誤的，不可用的，從而造成程序錯誤，這就造成了併發安全問題，為此我們必須要有一套控制機制來避免這樣的事情發生。就好比兩個人喝一瓶可樂，只有一根吸管，那肯定也得商量出一個規則，才能相安無事地都喝到可樂。本節就將具體介紹在Rust中，我們要怎麼做，才能解決這個問題。

繼續上面喝可樂的例子，一人一口的方式，就是一種解決方案，只要不是太笨，幾乎都能想到這個方案。具體實施時，A在喝的時候，B一直在旁邊盯著，要是A喝完一口，B馬上拿過來喝，此時A肯定也是在旁邊盯著。在現實生活中，這樣的示例比比皆是。細想一下，貌似同步中都可能涉及到等待。諸葛先生在萬事具備，只欠東風時，也只能等，因為條件不成熟啊。依照這個邏輯，在操作系統和各大編程語言中，幾乎都支持當前線程等待，當然Rust也不例外。

### 等待
Rust中線程等待和其他語言在機制上並無差異，大致有下面幾種：

* 等待一段時間後，再接著繼續執行。看起來就像一個人工作累了，休息一會再工作。通過調用相關的API可以讓當前線程暫停執行進入睡眠狀態，此時調度器不會調度它執行，等過一段時間後，線程自動進入就緒狀態，可以被調度執行，繼續從之前睡眠時的地方執行。對應的API有`std::thread::sleep`，`std::thread::sleep_ms`，`std::thread::park_timeout`，`std::thread::park_timeout_ms`，還有一些類似的其他API，由於太多，詳細信息就請參見官網[`std::thread`](https://doc.rust-lang.org/stable/std/thread/index.html)。
* 這一種方式有點特殊，時間非常短，就一個時間片，當前線程自己主動放棄當前時間片的調度，讓調度器重新選擇線程來執行，這樣就把運行機會給了別的線程，但是要注意的是，如果別的線程沒有更好的理由執行，當然最後執行機會還是它的。在實際的應用業務中，比如生產者製造出一個產品後，可以放棄一個時間片，讓消費者獲得執行機會，從而快速地消費才生產的產品。這樣的控制粒度非常小，需要合理使用，如果需要連續放棄多個時間片，可以借用循環實現。對應的API是`std::thread::yield_now`，詳細信息參見官網[`std::thread`](https://doc.rust-lang.org/stable/std/thread/index.html)。
* 1和2的等待都無須其他線程的協助，即可在一段時間後繼續執行。最後我們還遇到一種等待，是需要其他線程參與，才能把等待的線程叫醒，否則，線程會一直等待下去。好比一個女人，要是沒有遇到一個男人，就永遠不可能擺脫單身的狀態。相關的API包括`std::thread::JoinHandle::join`，`std::thread::park`，`std::sync::Mutex::lock`等，還有一些同步相關的類的API也會導致線程等待。詳細信息參見官網[`std::thread`](https://doc.rust-lang.org/stable/std/thread/index.html)和[`std::sync`](https://doc.rust-lang.org/stable/std/sync/index.html)。

第一種和第三種等待方式，其實我們在上面的介紹中，都已經遇到過了，它們也是使用的最多的兩種方式。在此，也可以回過頭去看看前面的使用方式和使用效果，結合自己的理解，做一些簡單的練習。

毫無疑問，第三種方式稍顯複雜，要將等待的線程叫醒，必然基於一定的規則，比如早上7點必須起床，那麼就定一個早上7點的鬧鐘，到時間了就響，沒到時間別響。不管基於什麼規則，要觸發叫醒這個事件，就肯定是某個條件已經達成了。基於這樣的邏輯，在操作系統和編程語言中，引入了一種叫著**條件變量**的東西。可以模擬現實生活中的鬧鐘的行為，條件達成就通知等待條件的線程。Rust的條件變量就是`std::sync::Condvar`，詳情參見官網[條件變量](https://doc.rust-lang.org/std/sync/struct.Condvar.html)。但是通知也並不只是條件變量的專利，還有其他的方式也可以觸發通知，下面我們就來瞧一瞧。

### 通知
看是簡單的通知，在編程時也需要注意以下幾點：

* 通知必然是因為有等待，所以通知和等待幾乎都是成對出現的，比如`std::sync::Condvar::wait`和`std::sync::Condvar::notify_one`，`std::sync::Condvar::notify_all`。
* 等待所使用的對象，與通知使用的對象是同一個對象，從而該對象需要在多個線程之間共享，參見下面的例子。
* 除了`Condvar`之外，其實*鎖*也是具有自動通知功能的，當持有鎖的線程釋放鎖的時候，等待鎖的線程就會自動被喚醒，以搶佔鎖。關於鎖的介紹，在下面有詳解。
* 通過條件變量和鎖，還可以構建更加複雜的自動通知方式，比如`std::sync::Barrier`。
* 通知也可以是1:1的，也可以是1:N的，`Condvar`可以控制通知一個還是N個，而鎖則不能控制，只要釋放鎖，所有等待鎖的其他線程都會同時醒來，而不是隻有最先等待的線程。

下面我們分析一個簡單的例子：

```rust
use std::sync::{Arc, Mutex, Condvar};
use std::thread;

fn main() {

	let pair = Arc::new((Mutex::new(false), Condvar::new()));
	let pair2 = pair.clone();

	// 創建一個新線程
	thread::spawn(move|| {
	    let &(ref lock, ref cvar) = &*pair2;
	    let mut started = lock.lock().unwrap();
	    *started = true;
	    cvar.notify_one();
	    println!("notify main thread");
	});

	// 等待新線程先運行
	let &(ref lock, ref cvar) = &*pair;
	let mut started = lock.lock().unwrap();
	while !*started {
		println!("before wait");
	    started = cvar.wait(started).unwrap();
	    println!("after wait");
	}
}
```

運行結果：

```
before wait
notify main thread
after wait
```

這個例子展示瞭如何通過條件變量和鎖來控制新建線程和主線程的同步，讓主線程等待新建線程執行後，才能繼續執行。從結果來看，功能上是實現了。對於上面這個例子，還有下面幾點需要說明：

* `Mutex`是Rust中的一種鎖。
* `Condvar`需要和`Mutex`一同使用，因為有`Mutex`保護，`Condvar`併發才是安全的。
* `Mutex::lock`方法返回的是一個`MutexGuard`，在離開作用域的時候，自動銷燬，從而自動釋放鎖，從而避免鎖沒有釋放的問題。
* `Condvar`在等待時，時會釋放鎖的，被通知喚醒時，會重新獲得鎖，從而保證併發安全。

到此，你應該對鎖比較感興趣了，為什麼需要鎖？鎖存在的目的就是為了保證資源在同一個時間，能有序地被訪問，而不會出現異常數據。但其實要做到這一點，也並不是隻有鎖，包括鎖在內，主要涉及兩種基本方式：

### 原子類型
原子類型是最簡單的控制共享資源訪問的一種機制，相比較於後面將介紹的鎖而言，原子類型不需要開發者處理加鎖和釋放鎖的問題，同時支持修改，讀取等操作，還具備較高的併發性能，從硬件到操作系統，到各個語言，基本都支持。在標準庫`std::sync::atomic`中，你將在裡面看到Rust現有的原子類型，包括`AtomicBool`，`AtomicIsize`，`AtomicPtr`，`AtomicUsize`。這4個原子類型基本能滿足百分之九十的共享資源安全訪問的需要。下面我們就用原子類型，結合共享內存的知識，來展示一下一個線程修改，一個線程讀取的情況：

```rust
use std::thread;
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};

fn main() {
	let var : Arc<AtomicUsize> = Arc::new(AtomicUsize::new(5));
	let share_var = var.clone();

	// 創建一個新線程
	let new_thread = thread::spawn(move|| {
		println!("share value in new thread: {}", share_var.load(Ordering::SeqCst));
		// 修改值
		share_var.store(9, Ordering::SeqCst);
	});

	// 等待新建線程先執行
	new_thread.join().unwrap();
	println!("share value in main thread: {}", var.load(Ordering::SeqCst));
}
```

運行結果：

```
share value in new thread: 5
share value in main thread: 9
```

結果表明新建線程成功的修改了值，並在主線程中獲取到了最新值，你也可以嘗試使用其他的原子類型。此處我們可以思考一下，如果我們用`Arc::new(*mut Box<u32>)`是否也可以做到？ 為什麼？ 思考後，大家將體會到Rust在多線程安全方面做的有多麼的好。除了原子類型，我們還可以使用鎖來實現同樣的功能。

### 鎖
在多線程中共享資源，除了原子類型之外，還可以考慮用鎖來實現。在操作之前必須先獲得鎖，一把鎖同時只能給一個線程，這樣能保證同一時間只有一個線程能操作共享資源，操作完成後，再釋放鎖給等待的其他線程。在Rust中`std::sync::Mutex`就是一種鎖。下面我們用`Mutex`來實現一下上面的原子類型的例子：

```rust
use std::thread;
use std::sync::{Arc, Mutex};

fn main() {
	let var : Arc<Mutex<u32>> = Arc::new(Mutex::new(5));
	let share_var = var.clone();

	// 創建一個新線程
	let new_thread = thread::spawn(move|| {
		let mut val = share_var.lock().unwrap();
		println!("share value in new thread: {}", *val);
		// 修改值
		*val = 9;
	});

	// 等待新建線程先執行
	new_thread.join().unwrap();
	println!("share value in main thread: {}", *(var.lock().unwrap()));
}
```

運行結果：

```
share value in new thread: 5
share value in main thread: 9
```

結果都一樣，看來用`Mutex`也能實現，但如果從效率上比較，原子類型會更勝一籌。暫且不論這點，我們從代碼裡面看到，雖然有`lock`，但是並麼有看到有類似於`unlock`的代碼出現，並不是不需要釋放鎖，而是Rust為了提高安全性，已然在`val`銷燬的時候，自動釋放鎖了。同時我們發現，為了修改共享的值，開發者必須要調用`lock`才行，這樣就又解決了一個安全問題。不得不再次讚歎一下Rust在多線程方面的安全性做得真是太好了。如果是其他語言，我們要做到安全，必然得自己來實現這些。

為了保障鎖使用的安全性問題，Rust做了很多工作，但從效率來看還不如原子類型，那麼鎖是否就沒有存在的價值了？顯然事實不可能是這樣的，既然存在，那必然有其價值。它能解決原子類型鎖不能解決的那百分之十的問題。我們再來看一下之前的一個例子：

```rust
use std::sync::{Arc, Mutex, Condvar};
use std::thread;

fn main() {

	let pair = Arc::new((Mutex::new(false), Condvar::new()));
	let pair2 = pair.clone();

	// 創建一個新線程
	thread::spawn(move|| {
	    let &(ref lock, ref cvar) = &*pair2;
	    let mut started = lock.lock().unwrap();
	    *started = true;
	    cvar.notify_one();
	    println!("notify main thread");
	});

	// 等待新線程先運行
	let &(ref lock, ref cvar) = &*pair;
	let mut started = lock.lock().unwrap();
	while !*started {
		println!("before wait");
	    started = cvar.wait(started).unwrap();
	    println!("after wait");
	}
}
```

代碼中的`Condvar`就是條件變量，它提供了`wait`方法可以主動讓當前線程等待，同時提供了`notify_one`方法，讓其他線程喚醒正在等待的線程。這樣就能完美實現順序控制了。看起來好像條件變量把事都做完了，要`Mutex`幹嘛呢？為了防止多個線程同時執行條件變量的`wait`操作，因為條件變量本身也是需要被保護的，這就是鎖能做，而原子類型做不到的地方。

在Rust中，`Mutex`是一種獨佔鎖，同一時間只有一個線程能持有這個鎖。這種鎖會導致所有線程串行起來，這樣雖然保證了安全，但效率並不高。對於寫少讀多的情況來說，如果在沒有寫的情況下，都是讀取，那麼應該是可以併發執行的，為了達到這個目的，幾乎所有的編程語言都提供了一種叫讀寫鎖的機制，Rust中也存在，叫[`std::sync::RwLock`](https://doc.rust-lang.org/std/sync/struct.RwLock.html)，在使用上同`Mutex`差不多，在此就留給大家自行練習了。

同步是多線程編程的永恆主題，Rust已經為我們提供了良好的編程範式，並強加檢查，即使你之前沒有怎麼接觸過，用Rust也能編寫出非常安全的多線程程序。
