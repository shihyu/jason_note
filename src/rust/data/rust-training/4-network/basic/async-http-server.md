
轉化 listener.incoming()，從阻塞迭代器轉換成非阻塞的流。流類似於迭代器，但是會異步地被消耗。


```shell
use std::io::prelude::*;
use std::time::Duration;
use async_std::task;
use async_std::net::TcpListener;
use async_std::net::TcpStream;
use async_std::io::ReadExt;
use async_std::io::WriteExt;
use futures::stream::StreamExt;

#[async_std::main]
async fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").await.unwrap();
    listener
        .incoming()
        .for_each_concurrent(/* limit */ None, |tcpstream| async move {
            let tcpstream = tcpstream.unwrap();
            handle_connection(tcpstream).await;
        })
        .await;
}

async fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).await.unwrap();

    task::sleep(Duration::from_secs(5)).await;

    let contents = "<!DOCTYPE html> \
    <html lang=\"en\"> \
      <head> \
        <meta charset=\"utf-8\"> \
        <title>Hello!</title> \
      </head> \
      <body> \
        <h1>Hello!</h1> \
        <p>Hi from Rust</p> \
      </body> \
    </html>";

    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}",
        contents.len(),
        contents
    );

    stream.write(response.as_bytes()).await.unwrap();
    stream.flush().await.unwrap();
}
```
