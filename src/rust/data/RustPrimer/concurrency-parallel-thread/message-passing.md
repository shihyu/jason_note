## 消息傳遞
稍加考慮，上一節的練習題其實是不完整的，它只是評分系統中的一環，一個評分系統是需要先把信息從數據庫或文件中讀取出來，然後才是評分，最後還需要把評分結果再保存到數據庫或文件中去。如果一步一步串行地做這三個步驟，是完全沒有問題的。那麼我們是否可以用三個線程來分別做這三個步驟呢？上一節練習題我們已經用了一個線程來實現評分，那麼我們是否也可以再用一個線程來讀取成績，再用另個線程來實現保存呢？ 如果能這樣的話，那麼我們就可以利用上多核多cpu的優勢，加快整個評分的效率。既然在此提出這個問題，答案就很明顯了。問題在於我們要怎麼在Rust中來實現，關鍵在於三個線程怎麼交換信息，以達到串行的邏輯處理順序？

為瞭解決這個問題，下面將介紹一種Rust在標準庫中支持的消息傳遞技術。**消息傳遞**是併發模型裡面大家比較推崇的模式，不僅僅是因為使用起來比較簡單，關鍵還在於它可以減少數據競爭，提高併發效率，為此值得深入學習。Rust是通過一個叫做通道(`channel`)的東西來實現這種模式的，下面直接進入主題。

### 初試通道(channel)
Rust的通道(`channel`)可以把一個線程的消息(數據)傳遞到另一個線程，從而讓信息在不同的線程中流動，從而實現協作。詳情請參見[`std::sync::mpsc`](https://doc.rust-lang.org/std/sync/mpsc/index.html)。通道的兩端分別是發送者(`Sender`)和接收者(`Receiver`)，發送者負責從一個線程發送消息，接收者則在另一個線程中接收該消息。下面我們來看一個簡單的例子：

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    // 創建一個通道
    let (tx, rx): (mpsc::Sender<i32>, mpsc::Receiver<i32>) = 
        mpsc::channel();

    // 創建線程用於發送消息
    thread::spawn(move || {
        // 發送一個消息，此處是數字id
        tx.send(1).unwrap();
    });

    // 在主線程中接收子線程發送的消息並輸出
    println!("receive {}", rx.recv().unwrap());
}
```

程序說明參見代碼中的註釋，程序執行結果為：

```
receive 1
```

結果表明`main`所在的主線程接收到了新建線程發送的消息，用Rust在線程間傳遞消息就是這麼簡單！

雖然簡單，但使用過其他語言就會知道，通道有多種使用方式，且比較靈活，為此我們需要進一步考慮關於`Rust`的`Channel`的幾個問題：

1. 通道能保證消息的順序嗎？是否先發送的消息，先接收？
2. 通道能緩存消息嗎？如果能的話能緩存多少？
3. 通道的發送者和接收者支持N:1，1:N，N:M模式嗎？
4. 通道能發送任何數據嗎？
5. 發送後的數據，在線程中繼續使用沒有問題嗎？

讓我們帶著這些問題和思考進入下一個小節，那裡有相關的答案。

### 消息類型
上面的例子中，我們傳遞的消息類型為`i32`，除了這種類型之外，是否還可以傳遞更多的原始類型，或者更復雜的類型，和自定義類型？下面我們嘗試發送一個更復雜的`Rc`類型的消息：

```rust
use std::fmt;
use std::sync::mpsc;
use std::thread;
use std::rc::Rc;

pub struct Student {
    id: u32
}

impl fmt::Display for Student {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "student {}", self.id)
    }
}

fn main() {
    // 創建一個通道
    let (tx, rx): (mpsc::Sender<Rc<Student>>, mpsc::Receiver<Rc<Student>>) = 
        mpsc::channel();

    // 創建線程用於發送消息
    thread::spawn(move || {
        // 發送一個消息，此處是數字id
        tx.send(Rc::new(Student{
            id: 1,
        })).unwrap();
    });

    // 在主線程中接收子線程發送的消息並輸出
    println!("receive {}", rx.recv().unwrap());
}
```

編譯代碼，奇蹟沒有出現，編譯時錯誤，錯誤提示：

```
error: the trait `core::marker::Send` is not 
implemented for the type `alloc::rc::Rc<Student>` [E0277]
note: `alloc::rc::Rc<Student>` cannot be sent between threads safely
```

看來並不是所有類型的消息都可以通過通道發送，消息類型必須實現`marker trait Send`。Rust之所以這樣強制要求，主要是為瞭解決併發安全的問題，再一次強調，**安全**是Rust考慮的重中之重。如果一個類型是`Send`，則表明它可以在線程間安全的轉移所有權(`ownership`)，當所有權從一個線程轉移到另一個線程後，同一時間就只會存在一個線程能訪問它，這樣就避免了數據競爭，從而做到線程安全。`ownership`的強大又一次顯示出來了。通過這種做法，在編譯時即可要求所有的代碼必須滿足這一約定，這種方式方法值得借鑑，`trait`也是非常強大。

看起來問題得到了完美的解決，然而由於`Send`本身是一個不安全的`marker trait`，並沒有實際的`API`，所以實現它很簡單，但沒有強制保障，就只能靠開發者自己約束，否則還是可能引發併發安全問題。對於這一點，也不必太過擔心，因為Rust中已經存在的類，都已經實現了`Send`或`!Send`，我們只要使用就行。`Send`是一個默認應用到所有Rust已存在類的trait，所以我們用`!Send`顯式標明該類沒有實現`Send`。目前幾乎所有的原始類型都是`Send`，例如前面例子中發送的`i32`。對於開發者而言，我們可能會更關心哪些是非`Send`，也就是實現了`!Send`，因為這會導致線程不安全。更全面的信息參見[`Send`官網API](https://doc.rust-lang.org/std/marker/trait.Send.html)。

對於不是`Send`的情況（`!Send`），大致分為兩類：

1. 原始指針，包括`*mut T`和`*const T`，因為不同線程通過指針都可以訪問數據，從而可能引發線程安全問題。
2. `Rc`和`Weak`也不是，因為引用計數會被共享，但是並沒有做併發控制。

雖然有這些`!Send`的情況，但是逃不過編譯器的火眼金睛，只要你錯誤地使用了消息類型，編譯器都會給出類似於上面的錯誤提示。我們要擔心的不是這些，因為錯誤更容易出現在新創建的自定義類，有下面兩點需要注意：

1. 如果自定義類的所有字段都是`Send`，那麼這個自定義類也是`Send`。
    反之，如果有一個字段是`!Send`，那麼這個自定義類也是`!Send`。
    如果類的字段存在遞歸包含的情況，按照該原則以此類推來推論類是`Send`還是`!Send`。

2. 在為一個自定義類實現`Send`或者`!Send`時，必須確保符合它的約定。

到此，消息類型的相關知識已經介紹完了，說了這麼久，也該讓大家自己練習一下了：請實現一個自定義類，該類包含一個Rc字段，讓這個類變成可以在通道中發送的消息類型。

### 異步通道(Channel)
在粗略地嘗試通道之後，是時候更深入一下了。Rust的標準庫其實提供了兩種類型的通道：異步通道和同步通道。上面的例子都是使用的異步通道，為此這一小節我們優先進一步介紹異步通道，後續再介紹同步通道。異步通道指的是：不管接收者是否正在接收消息，消息發送者在發送消息時都不會阻塞。為了驗證這一點，我們嘗試多增加一個線程來發送消息：

```rust
use std::sync::mpsc;
use std::thread;

// 線程數量
const THREAD_COUNT :i32 = 2;

fn main() {
    // 創建一個通道
    let (tx, rx): (mpsc::Sender<i32>, mpsc::Receiver<i32>) = mpsc::channel();

    // 創建線程用於發送消息
    for id in 0..THREAD_COUNT {
        // 注意Sender是可以clone的，這樣就可以支持多個發送者
        let thread_tx = tx.clone();
        thread::spawn(move || {
            // 發送一個消息，此處是數字id
            thread_tx.send(id + 1).unwrap();
            println!("send {}", id + 1);
        });
    }

    thread::sleep_ms(2000);
    println!("wake up");
    // 在主線程中接收子線程發送的消息並輸出
    for _ in 0..THREAD_COUNT {
        println!("receive {}", rx.recv().unwrap());
    }
}
```

運行結果:

```
send 1
send 2
wake up
receive 1
receive 2
```

在代碼中，我們故意讓`main`所在的主線程睡眠2秒，從而讓發送者所在線程優先執行，通過結果可以發現，發送者發送消息時確實沒有阻塞。還記得在前面提到過很多關於通道的問題嗎？從這個例子裡面還發現什麼沒？除了不阻塞之外，我們還能發現另外的三個特徵：

1.通道是可以同時支持多個發送者的，通過`clone`的方式來實現。
    這類似於`Rc`的共享機制。
    其實從`Channel`所在的庫名`std::sync::mpsc`也可以知道這點。
    因為`mpsc`就是多生產者單消費者(Multiple Producers Single Consumer)的簡寫。
    可以有多個發送者,但只能有一個接收者，即支持的N:1模式。

2.異步通道具備消息緩存的功能，因為1和2是在沒有接收之前就發了的，在此之後還能接收到這兩個消息。

那麼通道到底能緩存多少消息？在理論上是無窮的，嘗試一下便知：

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    // 創建一個通道
    let (tx, rx): (mpsc::Sender<i32>, mpsc::Receiver<i32>) = mpsc::channel();

    // 創建線程用於發送消息
    let new_thread = thread::spawn(move || {
        // 發送無窮多個消息
        let mut i = 0;
        loop {
            i = i + 1;
            // add code here
            println!("send {}", i);
            match tx.send(i) {
                Ok(_) => (),
                Err(e) => {
                    println!("send error: {}, count: {}", e, i);
                    return;
                },
            }
        }
    });

    // 在主線程中接收子線程發送的消息並輸出
    new_thread.join().unwrap();
    println!("receive {}", rx.recv().unwrap());
}
```

最後的結果就是耗費內存為止。

3.消息發送和接收的順序是一致的，滿足先進先出原則。

上面介紹的內容大多是關於發送者和通道的，下面開始考察一下接收端。通過上面的幾個例子，細心一點的可能已經發現接收者的`recv`方法應該會阻塞當前線程，如果不阻塞，在多線程的情況下，發送的消息就不可能接收完全。所以沒有發送者發送消息，那麼接收者將會一直等待，這一點要謹記。在某些場景下，一直等待是符合實際需求的。但某些情況下並不需一直等待，那麼就可以考慮釋放通道，只要通道釋放了，`recv`方法就會立即返回。

異步通道的具有良好的靈活性和擴展性，針對業務需要，可以靈活地應用於實際項目中，實在是必備良藥！

### 同步通道
同步通道在使用上同異步通道一樣，接收端也是一樣的，唯一的區別在於發送端，我們先來看下面的例子：

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    // 創建一個同步通道
    let (tx, rx): (mpsc::SyncSender<i32>, mpsc::Receiver<i32>) = mpsc::sync_channel(0);

    // 創建線程用於發送消息
    let new_thread = thread::spawn(move || {
        // 發送一個消息，此處是數字id
        println!("before send");
        tx.send(1).unwrap();
        println!("after send");
    });

    println!("before sleep");
    thread::sleep_ms(5000);
    println!("after sleep");
    // 在主線程中接收子線程發送的消息並輸出
    println!("receive {}", rx.recv().unwrap());
    new_thread.join().unwrap();
}
```

運行結果：

```
before sleep
before send
after sleep
receive 1
after send
```

除了多了一些輸出代碼之外，上面這段代碼幾乎和前面的異步通道的沒有什麼區別，唯一不同的在於創建同步通道的那行代碼。同步通道是`sync_channel`，對應的發送者也變成了`SyncSender`。為了顯示出同步通道的區別，故意添加了一些打印。和異步通道相比，存在兩點不同：

1. 同步通道是需要指定緩存的消息個數的，但需要注意的是，最小可以是0，表示沒有緩存。
2. 發送者是會被阻塞的。當通道的緩存隊列不能再緩存消息時，發送者發送消息時，就會被阻塞。

對照上面兩點和運行結果來分析，由於主線程在接收消息前先睡眠了，從而子線程這個時候會被調度執行發送消息，由於通道能緩存的消息為0，而這個時候接收者還沒有接收，所以`tx.send(1).unwrap()`就會阻塞子線程，直到主線程接收消息，即執行`println!("receive {}", rx.recv().unwrap());`。運行結果印證了這點，要是沒阻塞，那麼在`before send`之後就應該是`after send`了。

相比較而言，異步通道更沒有責任感一些，因為消息發送者一股腦的只管發送，不管接收者是否能快速處理。這樣就可能出現通道里面緩存大量的消息得不到處理，從而佔用大量的內存，最終導致內存耗盡。而同步通道則能避免這種問題，把接受者的壓力能傳遞到發送者，從而一直傳遞下去。
