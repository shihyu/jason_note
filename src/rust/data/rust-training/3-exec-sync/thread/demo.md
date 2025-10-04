一個創建新線程的例子

```shell
use std::thread;
use std::time::Duration;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(move || {
        println!("Here's a vector: {:?}", v);
        
        for i in 1..100 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }
    handle.join().unwrap();
    println!("main thread exit!");
}
```

其中 
- move 將會把 v 移動進閉包的環境中（如此將不能在主線程中對其調用 drop 了）
- thread::spawn 的返回值類型是 JoinHandle。JoinHandle 是一個擁有所有權的值，當對其調用 join 方法時，它會等待其線程結束。


為閉包增加 