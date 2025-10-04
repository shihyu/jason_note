## async和await配合使用
運行 Future 最常見的方法是 .await 它。當 .await 在 Future 上調用時，它會嘗試把 future 跑到完成狀態。
如果 Future 被阻塞了，它會讓出當前線程的控制權。能取得進展時，執行器就會撿起這個 Future 並繼續執行，讓 .await 求解

在async函數中，可以使用await來等待一個Future完成。以下是一個例子。

```
async fn learn_song() -> bool { 
    println!("learn_song");
    true
}

async fn sing_song() { 
    let future = learn_song();
    let ret = future.await;
    println!("learn_song {}, then sing_song", ret);
}

fn main() {
    let future = sing_song();
    block_on(future)
}
```