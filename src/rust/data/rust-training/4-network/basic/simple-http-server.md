在rust中
- 使用TcpListener::bind來實現綁定端口
- 使用listener.incoming來遍歷所有連接
- 使用stream.read來讀取連接上的請求數據
- 使用stream.write來向連接發送響應數據

```shell
use std::io::prelude::*;
use std::net::TcpListener;
use std::net::TcpStream;

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

    for stream in listener.incoming() {
        let stream = stream.unwrap();

        handle_connection(stream);
    }
}

fn handle_connection(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    stream.read(&mut buffer).unwrap();

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

    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}
```