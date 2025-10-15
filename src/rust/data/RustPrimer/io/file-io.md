# 文件輸入與輸出

文件 `std::fs::File` 本身實現了 `Read` 和 `Write` trait，所以文件的輸入輸出非常簡單，只要得到一個 `File` 類型實例就可以調用讀寫接口進行文件輸入與輸出操作了。而要得到 `File` 就得讓操作系統打開(open)或新建(create)一個文件。還是拿例子來說明

```rust
use std::io;
use std::io::prelude::*;
use std::fs::File;

// create file and write something
fn create_file(filename: &str, buf: &[u8]) -> io::Result<()> {
	let mut f = try!(File::create(filename));
	try!(f.write(&buf));
	Ok(())
}

// read from file to String
fn read_file(filename: &str, buf: &mut String) -> io::Result<()> {
	let mut f = try!(File::open(filename));
	try!(f.read_to_string(&buf));
	Ok(())
}

fn main() {
	let f = "foo.txt";
	let mut buf = String::new();
	match create_file(f, b"Hello, World!") {
		Ok(()) => {
		    match read_file(f, &mut buf) {
		        Ok(()) => {println!("{}", buf);},
		        Err(e) => {println!("{}", e);},
            };
		},
		Err(e) => {println!("{}", e);},
	}
}
```

文件操作上面 Rust 與其它語言處理方式有些不一樣，其它語言一般把讀寫選項作為函數參數傳給 open 函數，而 Rust 則是在 option 上面調用 open 函數。 [`std::fs::OpenOptions`](http://doc.rust-lang.org/stable/std/fs/struct.OpenOptions.html) 是一個 builder，通過 new 函數創建後，可以鏈式調用設置打開文件的選項，是 read, write, append, truncate 還是 create 等，OpenOptions 構建完成後就可以再接著調用 open 方法了，看下下面的例子就明白了

```rust
use std::fs::OpenOptions;

let file = OpenOptions::new().write(true).truncate(true).open("foo.txt");
```

Rust 這種用 builder pattern 來設置打開文件選項，相比於將選項以字符作為參數傳給 open 函數的一個優點是可以讓編譯器保證檢查選項合法性，不用等到運行時才發現手抖把 read-mode 的 `r` 寫成了 `t`。
