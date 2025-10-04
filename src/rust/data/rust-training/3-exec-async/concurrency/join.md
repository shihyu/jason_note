futures::join 宏等待併發執行的多個不同 future 完成。

下面是一個使用 join 宏的示例：

```shell
use futures::join;
use futures::executor::block_on;
use std::{thread, time};

async fn read_book(){
    let mut i = 0;
    while i < 10 {
        i += 1;
        println!("I am reading book");
        thread::sleep(time::Duration::from_secs(1));
    } 
}

async fn listen_music(){
    let mut i = 0;
    while i < 10 {
        i += 1;
        println!("I am listening music");
        thread::sleep(time::Duration::from_secs(1));
    } 
}

async fn study(){
    let future1 = read_book();
    let future2 = listen_music();
    join!(future1, future2);
}


fn main() {
    let future = study();
    block_on(future);
}
```