首先實現一個線程池
- 定義一個ThreadPool、包含一個vector來存儲線程、一個channel來收發任務
- ThreadPool的new方法來
  - 創建線程池，
  - 創建通道，並將通道的receiver發給每個線程
  - 線程的閉包中通過move接收receiver，先獲得receiver的鎖，然後從receiver中接收任務，執行任務
- ThreadPool的execute方法中將任務發送給通道

```shell
use std::thread;
use std::sync::mpsc;
use std::sync::Arc;
use std::sync::Mutex;


pub struct ThreadPool{
    workers: Vec<Worker>,
    sender: mpsc::Sender<Job>,
}

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }
        ThreadPool {
            workers,
            sender,
        }
    }
}

struct Worker {
    id: usize,
    thread: thread::JoinHandle<()>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || {
            loop {
                let job = receiver.lock().unwrap().recv().unwrap();

                println!("Worker {} got a job; executing.", id);

                job();
            }
        });

        Worker {
            id,
            thread,
        }
    }
}

type Job = Box<dyn FnOnce() + Send + 'static>;

impl ThreadPool {
    pub fn execute<F>(&self, f: F)
        where
            F: FnOnce() + Send + 'static
    {
        let job = Box::new(f);

        self.sender.send(job).unwrap();
    }
}
```

在主線程中
- 使用TcpListener::bind來實現綁定端口
- 調用ThreadPool::new來創建一個線程池
- 使用listener.incoming來遍歷所有連接
- 將連接上獲得的請求交給線程池處理
- 定義每個請求的處理方法handle_connection
  - 使用stream.read來讀取連接上的請求數據
  - 使用stream.write來向連接發送響應數據

```
use std::io::prelude::*;
use std::net::TcpListener;
use std::net::TcpStream;
use std::thread;
use std::time::Duration;
use helloworld::ThreadPool;



fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(4);

    for stream in listener.incoming() {
        let stream = stream.unwrap();
        pool.execute(|| {
            handle_connection(stream);
        });
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
    thread::sleep(Duration::from_secs(10));
    stream.write(response.as_bytes()).unwrap();
    stream.flush().unwrap();
}






```