多線程之間可以訪問同一個共享變量。不過為了安全起見，需要使用Mutex<T>互斥器。
關聯函數 new 來創建一個 Mutex<T>。使用 lock 方法獲取鎖。這裡我們使用 Mutex 浮點數。

另外還需要將new出來的Mutex<T>進行克隆，因為一個線程在獲取鎖之後，另一個線程將無法獲取鎖。
值得注意的是，跨線程之間的克隆需要使用現成安全的原子引用計數Arc<T>

如下是一個在多線程之間訪問同一個共享變量，並使用Mutex<T>避免數據競爭的示例：

```shell
use std::sync::{Mutex, Arc};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0.1));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();

            *num += 1.1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}
```