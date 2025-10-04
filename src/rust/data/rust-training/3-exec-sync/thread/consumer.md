以下是一個使用多線程來實現的生產者消費者的例子。

傳遞給thread::spawn的是一個閉包。 通過 move 將主線程中的 sender, receiver 傳遞給子線程來使用。
move 關鍵字操作後，閉包中用到的變量將移入子線程中，從而實現線程安全。如果沒有用到的變量不會被移入。

```shell
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    let (sender, receiver) = mpsc::channel();
    let sender1 = sender.clone();
    let sender2 = sender.clone();

    // 生產者線程1
    let producer1 = thread::spawn(move || {
        for i in 0..10 {
            sender1.send(i).unwrap();
            thread::sleep(Duration::from_secs(1));
            println!("Produced: {}", i);
        }
    });

    // 生產者線程1
    let producer2 = thread::spawn(move || {
        for i in 0..10 {
            sender2.send(i).unwrap();
            thread::sleep(Duration::from_secs(1));
            println!("Produced: {}", i);
        }
    });

    // 消費者線程
    let consumer = thread::spawn(move || {
        for _ in 0..50 {
            let data = receiver.recv().unwrap();
            println!("Consumed: {}", data);
        }
    });

    producer1.join().unwrap();
    producer2.join().unwrap();
    consumer.join().unwrap();
}
```