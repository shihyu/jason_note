# 網絡模塊:W貓的迴音

本例子中，W貓將帶大家寫一個大家都寫過但是沒什麼人用過的TCP ECHO軟件，作為本章的結尾。本程序僅作為實例程序，我個人估計也沒有人在實際的生活中去使用她。不過，作為標準庫的示例來說，已經足夠。

首先，我們需要一個一個服務器端。

```rust
fn server<A: ToSocketAddrs>(addr: A) -> io::Result<()> {
    // 建立一個監聽程序
    let listener = try!(TcpListener::bind(&addr)) ;
    // 這個程序一次只需處理一個鏈接就好
    for stream in listener.incoming() {
        // 通過match再次解包 stream到
        match stream {
            // 這裡匹配的重點是如何將一個mut的匹配傳給一個Result
            Ok(mut st) => {
                // 我們總是要求client端先發送數據
                // 準備一個超大的緩衝區
                // 當然了，在實際的生活中我們一般會採用環形緩衝來重複利用內存。
                // 這裡僅作演示，是一種很低效的做法
                let mut buf: Vec<u8> = vec![0u8; 1024];
                // 通過try!方法來解包
                // try!方法的重點是需要有特定的Error類型與之配合
                let rcount = try!(st.read(&mut buf));
                // 只輸出緩衝區裡讀取到的內容
                println!("{:?}", &buf[0..rcount]);
                // 回寫內容
                let wcount = try!(st.write(&buf[0..rcount]));
                // 以下代碼實際上算是邏輯處理
                // 並非標準庫的一部分了
                if rcount != wcount {
                    panic!("Not Fully Echo!, r={}, w={}", rcount, wcount);
                }
                // 清除掉已經讀到的內容
                buf.clear();
            }
            Err(e) => {
                panic!("{}", e);
            }
        }
    }
    // 關閉掉Serve端的鏈接
    drop(listener);
    Ok(())
}

```


然後，我們準備一個模擬TCP短鏈接的客戶端：

```rust
fn client<A: ToSocketAddrs>(addr: A) -> io::Result<()> {

    let mut buf = vec![0u8;1024];
    loop {
        // 對比Listener，TcpStream就簡單很多了
        // 本次模擬的是tcp短鏈接的過程，可以看作是一個典型的HTTP交互的基礎IO模擬
        // 當然，這個通訊裡面並沒有HTTP協議 XD！
        let mut stream = TcpStream::connect(&addr).unwrap();
        let msg = "WaySLOG comming!".as_bytes();
        // 避免發送數據太快而刷屏
        thread::sleep_ms(100);
        let rcount = try!(stream.write(&msg));
        let _ = try!(stream.read(&mut buf));
        println!("{:?}", &buf[0..rcount]);
        buf.clear();
    }
    Ok(())
}

```

將我們的程序拼接起來如下：

```rust
use std::net::*;
use std::io;
use std::io::{Read, Write};
use std::env;
use std::thread;

fn server<A: ToSocketAddrs>(addr: A) -> io::Result<()> { .. }


fn client<A: ToSocketAddrs>(addr: A) -> io::Result<()> { .. }


fn main() {
    let mut args = env::args();
    args.next();
    let action = args.next().unwrap();
    if action == "s" {
        server(&args.next().unwrap()).unwrap();
    } else {
        client(&args.next().unwrap()).unwrap();
    }
}

```

各位可以自己試一下結果


寫網絡程序，註定了要處理各種神奇的條件和錯誤，定義自己的數據結構，粘包問題等都是需要我們去處理和關注的。相較而言，Rust本身在網絡方面的基礎設施建設並不盡如人意，甚至連網絡I/O都只提供瞭如上的block I/O 。可能其團隊更關注於語言基礎語法特性和編譯的改進，但其實，有著官方出品的這種網絡庫是非常重要的。同時，我也希望Rust能夠湧現出更多的網絡庫方案，讓Rust的明天更好更光明。
