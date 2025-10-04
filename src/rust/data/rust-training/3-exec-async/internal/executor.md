
自己定義並實現一個executor

首先先實現一個future

```
//file:future_timer.rs
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
```

再實現一個executor，用於執行`Future`。

```
// file:main.rs
use {
    futures::{
        future::{BoxFuture, FutureExt},
        task::{waker_ref, ArcWake},
    },
    std::{
        future::Future,
        sync::mpsc::{sync_channel, Receiver, SyncSender},
        sync::{Arc, Mutex},
        task::Context,
        time::Duration,
    },
   
};

mod future_timer;
 // 引入之前實現的定時器模塊
use future_timer::TimerFuture;

/// 任務執行器，負責從通道中接收任務然後執行
struct Executor {
    ready_queue: Receiver<Arc<Task>>,
}

/// `Spawner`負責創建新的`Future`然後將它發送到任務通道中
#[derive(Clone)]
struct Spawner {
    task_sender: SyncSender<Arc<Task>>,
}

/// 一個 Future，它可以調度自己(將自己放入任務通道中)，然後等待執行器去`poll`
struct Task {
    /// 進行中的Future，在未來的某個時間點會被完成
    ///
    /// 按理來說`Mutex`在這裡是多餘的，因為我們只有一個線程來執行任務。但是由於
    /// Rust並不聰明，它無法知道`Future`只會在一個線程內被修改，並不會被跨線程修改。因此
    /// 我們需要使用`Mutex`來滿足這個笨笨的編譯器對線程安全的執著。
    ///
    /// 如果是生產級的執行器實現，不會使用`Mutex`，因為會帶來性能上的開銷，取而代之的是使用`UnsafeCell`
    future: Mutex<Option<BoxFuture<'static, ()>>>,

    /// 可以將該任務自身放回到任務通道中，等待執行器的poll
    task_sender: SyncSender<Arc<Task>>,
}

fn new_executor_and_spawner() -> (Executor, Spawner) {
    // 任務通道允許的最大緩衝數(任務隊列的最大長度)
    // 當前的實現僅僅是為了簡單，在實際的執行中，並不會這麼使用
    const MAX_QUEUED_TASKS: usize = 10_000;
    let (task_sender, ready_queue) = sync_channel(MAX_QUEUED_TASKS);
    (Executor { ready_queue }, Spawner { task_sender })
}

impl Spawner {
    fn spawn(&self, future: impl Future<Output = ()> + 'static + Send) {
        let future = future.boxed();
        let task = Arc::new(Task {
            future: Mutex::new(Some(future)),
            task_sender: self.task_sender.clone(),
        });
        println!("first dispatch the future task to executor.");
        self.task_sender.send(task).expect("too many tasks queued.");
    }
}

/// 實現ArcWake，表明怎麼去喚醒任務去調度執行。
impl ArcWake for Task {
    fn wake_by_ref(arc_self: &Arc<Self>) {
        // 通過發送任務到任務管道的方式來實現`wake`，這樣`wake`後，任務就能被執行器`poll`
        let cloned = arc_self.clone();
        arc_self
            .task_sender
            .send(cloned)
            .expect("too many tasks queued");
    }
}

impl Executor {
     // 實際運行具體的Future任務，不斷的接收Future task執行。
    fn run(&self) {
        let mut count = 0;
        while let Ok(task) = self.ready_queue.recv() {
            count = count + 1;
            println!("received task. {}", count);
            // 獲取一個future，若它還沒有完成(仍然是Some，不是None)，則對它進行一次poll並嘗試完成它
            let mut future_slot = task.future.lock().unwrap();
            if let Some(mut future) = future_slot.take() {
                // 基於任務自身創建一個 `LocalWaker`
                let waker = waker_ref(&task);
                let context = &mut Context::from_waker(&*waker);
                // `BoxFuture<T>`是`Pin<Box<dyn Future<Output = T> + Send + 'static>>`的類型別名
                // 通過調用`as_mut`方法，可以將上面的類型轉換成`Pin<&mut dyn Future + Send + 'static>`
                if future.as_mut().poll(context).is_pending() {
                    println!("executor run the future task, but is not ready, create a future again.");
                    // Future還沒執行完，因此將它放回任務中，等待下次被poll
                    *future_slot = Some(future);
                } else {
                    println!("executor run the future task, is ready. the future task is done.");
                }
            }
        }
    }
}

fn main() {
    let (executor, spawner) = new_executor_and_spawner();

   // 將 TimerFuture 封裝成一個任務，分發到調度器去執行
    spawner.spawn(async {
        println!("TimerFuture await");
        // 創建定時器Future，並等待它完成
        TimerFuture::new(Duration::new(10, 0)).await;
        println!("TimerFuture Done");
    });

    // drop掉任務，這樣執行器就知道任務已經完成，不會再有新的任務進來
    drop(spawner);

    // 運行執行器直到任務隊列為空
    // 任務運行後，會先打印`howdy!`, 暫停2秒，接著打印 `done!`
    executor.run();
}

```