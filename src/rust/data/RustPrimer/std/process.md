# 系統命令:調用grep

我們知道，Linux系統中有一個命令叫grep，他能對目標文件進行分析並查找相應字符串，並該字符串所在行輸出。
今天，我們先來寫一個Rust程序，來調用一下這個 grep 命令

```rust
use std::process::*;
use std::env::args;

// 實現調用grep命令搜索文件
fn main() {
    let mut arg_iter = args();
    // panic if there is no one
    arg_iter.next().unwrap();
    let pattern = arg_iter.next().unwrap_or("main".to_string());
    let pt =  arg_iter.next().unwrap_or("./".to_string());
    let output = Command::new("/usr/bin/grep")
        .arg("-n")
        .arg("-r")
        .arg(&pattern)
        .arg(&pt)
        .output()
        .unwrap_or_else(|e| panic!("wg panic because:{}", e));
    println!("output:");
    let st = String::from_utf8_lossy(&output.stdout);
    let lines = st.split("\n");
    for line in lines {
        println!("{}", line);
    }
}

```

看起來好像還不錯，但是，以上的程序有一個比較致命的缺點——因為Output是同步的，因此，一旦調用的目錄下有巨大的文件，grep的分析將佔用巨量的時間。這對於一個高可用的程序來說是不被允許的。

那麼如何改進呢？

其實在上面的代碼中，我們隱藏了一個 `Child` 的概念，即——子進程。

下面我來演示怎麼操作子進程：

```rust
use std::process::*;
use std::env::args;

// 實現調用grep命令搜索文件
fn main() {
    let mut arg_iter = args();
    // panic if there is no one
    arg_iter.next();
    let pattern = arg_iter.next().unwrap_or("main".to_string());
    let pt =  arg_iter.next().unwrap_or("./".to_string());
    let child = Command::new("grep")
        .arg("-n")
        .arg("-r")
        .arg(&pattern)
        .arg(&pt)
        .spawn().unwrap();
    // 做些其他的事情
    std::thread::sleep_ms(1000);
    println!("{}", "計算很費時間……");
    let out = child.wait_with_output().unwrap();
    let out_str = String::from_utf8_lossy(&out.stdout);
    for line in out_str.split("\n") {
        println!("{}", line);
    }
}

```

但是，這個例子和我們預期的並不太一樣！

```
./demo main /home/wayslog/rust/demo/src
/home/wayslog/rust/demo/src/main.rs:5:fn main() {
/home/wayslog/rust/demo/src/main.rs:9:    let pattern = arg_iter.next().unwrap_or("main".to_string());
計算很費時間……

```

為什麼呢？

很簡單，我們知道，在Linux中，`fork`出來的函數會繼承父進程的所有句柄。因此，子進程也就會繼承父進程的標準輸出，也就是造成了這樣的問題。這也是最後我們用out無法接收到最後的輸出也就知道了，因為在前面已經被輸出出來了呀！

那麼怎麼做呢？給這個子進程一個pipeline就好了！

```rust
use std::process::*;
use std::env::args;

// 實現調用grep命令搜索文件
fn main() {
    let mut arg_iter = args();
    // panic if there is no one
    arg_iter.next();
    let pattern = arg_iter.next().unwrap_or("main".to_string());
    let pt =  arg_iter.next().unwrap_or("./".to_string());
    let child = Command::new("grep")
        .arg("-n")
        .arg("-r")
        .arg(&pattern)
        .arg(&pt)
        // 設置pipeline
        .stdout(Stdio::piped())
        .spawn().unwrap();
    // 做些其他的事情
    std::thread::sleep_ms(1000);
    println!("{}", "計算很費時間……");
    let out = child.wait_with_output().unwrap();
    let out_str = String::from_utf8_lossy(&out.stdout);
    for line in out_str.split("\n") {
        println!("{}", line);
    }
}
```

這段代碼相當於給了`stdout`一個緩衝區，這個緩衝區直到我們計算完成之後才被讀取，因此就不會造成亂序輸出的問題了。

這邊需要注意的一點是，一旦你開啟了一個子進程，那麼，無論你程序是怎麼處理的，最後一定要記得對這個`child`調用`wait`或者`wait_with_output`，除非你顯式地調用`kill`。因為如果父進程不`wait`它的話，它將會變成一個殭屍進程！！！

*注*： 以上問題為Linux下Python多進程的日常問題，已經見怪不怪了。
