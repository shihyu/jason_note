
## 構建一個定時器

在創建計時器時創建新線程，休眠特定時間，然後過了時間窗口時通知（signal） 計時器 future

Cargo.toml

```shell
[dependencies]
internal = "0.3"
```

main.rs

```rust
use futures;
use std::{
    future::Future,
    pin::Pin,
    sync::{Arc, Mutex},
    task::{Context, Poll, Waker},
    thread,
    time::Duration,
};

pub struct TimerFuture {
    shared_state: Arc<Mutex<SharedState>>,
}

/// 在Future和等待的線程間共享狀態
struct SharedState {
    /// 定時(睡眠)是否結束
    completed: bool,

    /// 當睡眠結束後，線程可以用`waker`通知`TimerFuture`來喚醒任務
    waker: Option<Waker>,
}

impl Future for TimerFuture {
    type Output = ();
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        // 通過檢查共享狀態，來確定定時器是否已經完成
        let mut shared_state = self.shared_state.lock().unwrap();
        if shared_state.completed {
            println!("future ready. execute poll to return.");
            Poll::Ready(())
        } else {
            println!("future not ready, tell the future task how to wakeup to executor");
            // 設置`waker`，這樣新線程在睡眠(計時)結束後可以喚醒當前的任務，接著再次對`Future`進行`poll`操作,
            // 下面的`clone`每次被`poll`時都會發生一次，實際上，應該是隻`clone`一次更加合理。
            // 選擇每次都`clone`的原因是： `TimerFuture`可以在執行器的不同任務間移動，如果只克隆一次，
            // 那麼獲取到的`waker`可能已經被篡改並指向了其它任務，最終導致執行器運行了錯誤的任務
            shared_state.waker = Some(cx.waker().clone());
            Poll::Pending
        }
    }
}

impl TimerFuture {
    /// 創建一個新的`TimerFuture`，在指定的時間結束後，該`Future`可以完成
    pub fn new(duration: Duration) -> Self {
        let shared_state = Arc::new(Mutex::new(SharedState {
            completed: false,
            waker: None,
        }));

        // 創建新線程
        let thread_shared_state = shared_state.clone();
        thread::spawn(move || {
            // 睡眠指定時間實現計時功能
            thread::sleep(duration);
            let mut shared_state = thread_shared_state.lock().unwrap();
            // 通知執行器定時器已經完成，可以繼續`poll`對應的`Future`了
            shared_state.completed = true;
            if let Some(waker) = shared_state.waker.take() {
                println!("detect future is ready, wakeup the future task to executor.");
                waker.wake()
            }
        });

        TimerFuture { shared_state }
    }
}

fn main() {
    // 我們現在還沒有實現調度器，所以要用一下futues庫裡的一個調度器。
    futures::executor::block_on(TimerFuture::new(Duration::new(10, 0)));    
}
```

該demo函數的執行過程如下。

1.最開始執行器會先 poll 一次 Future，此時shared_state.completed為false，future返回Poll::Pending，執行器會掛起該future，並等待waker被喚醒。
2.當定時器線程結束後，會調用waker.wake()來喚醒執行器，執行器就會把它們放入隊列並再一次 poll，此時shared_state.completed為true，future返回Poll::Ready(())，執行器會繼續執行下一個任務。