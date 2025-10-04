futures::select 宏同時跑多個 future，允許用戶在任意 future 完成時響應

下面的示例代碼中，只要有一個 future 完成，select 宏就會退出。
```shell
use futures::join;
use futures::executor::block_on;
use futures::{
    future::FutureExt, // 為了 `.fuse()`
    pin_mut,
    select,
};
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
    let future1 = read_book().fuse();
    let future2 = listen_music().fuse();
    pin_mut!(future1, future2);

    select! {
        () = future1 => println!("task one completed first"),
        () = future2 => println!("task two completed first"),
    }
}

fn main() {
    let future = study();
    block_on(future);
}
```