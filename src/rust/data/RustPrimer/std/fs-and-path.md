# 目錄操作:簡單grep

上一節我們實現了通過`Command`調用subprocess。這一節，我們將通過自己的代碼去實現一個簡單的grep。當然了，這種基礎的工具你是能找到源碼的，而我們的實現也並不像真正的grep那樣注重效率，本節的主要作用就在於演示標準庫API的使用。

首先，我們需要對當前目錄進行遞歸，遍歷，每當查找到文件的時候，我們回調一個函數。

於是，我們就有了這麼個函數：

```rust
use std::env::args;
use std::io;
use std::fs::{self, File, DirEntry};
use std::path::Path;

fn visit_dirs(dir: &Path, pattern: &String, cb: &Fn(&DirEntry, &String)) -> io::Result<()> {
    if try!(fs::metadata(dir)).is_dir() {
        for entry in try!(fs::read_dir(dir)) {
            let entry = try!(entry);
            if try!(fs::metadata(entry.path())).is_dir() {
                try!(visit_dirs(&entry.path(), pattern, cb));
            } else {
                cb(&entry, pattern);
            }
        }
    }else{
        let entry = try!(try!(fs::read_dir(dir)).next().unwrap());
        cb(&entry, pattern);
    }
    Ok(())
}

```

我們有了這樣的一個函數，有同學可能覺得這代碼眼熟。這不是標準庫裡的例子改了一下麼？

.

.

.

是啊！

好了，繼續，我們需要讀取每個查到的文件，同時判斷每一行裡有沒有所查找的內容。
我們用一個BufferIO去讀取各個文件，同時用String的自帶方法來判斷內容是否存在。

```rust
fn call_back(de: &DirEntry, pt: &String) {
    let mut f = File::open(de.path()).unwrap();
    let mut buf = io::BufReader::new(f);
    for line in io::BufRead::lines(buf) {
        let line = line.unwrap_or("".to_string());
        if line.contains(pt) {
            println!("{}", &line);
        }
    }
}
```

最後，我們將整個函數調用起來，如下：

```rust
use std::env::args;
use std::io;
use std::fs::{self, File, DirEntry};
use std::path::Path;

fn visit_dirs(dir: &Path, pattern: &String, cb: &Fn(&DirEntry, &String)) -> io::Result<()> {
    if try!(fs::metadata(dir)).is_dir() {
        for entry in try!(fs::read_dir(dir)) {
            let entry = try!(entry);
            if try!(fs::metadata(entry.path())).is_dir() {
                try!(visit_dirs(&entry.path(), pattern, cb));
            } else {
                cb(&entry, pattern);
            }
        }
    }else{
        let entry = try!(try!(fs::read_dir(dir)).next().unwrap());
        cb(&entry, pattern);
    }
    Ok(())
}

fn call_back(de: &DirEntry, pt: &String) {
    let mut f = File::open(de.path()).unwrap();
    let mut buf = io::BufReader::new(f);
    for line in io::BufRead::lines(buf) {
        let line = line.unwrap_or("".to_string());
        if line.contains(pt) {
            println!("{}", &line);
        }
    }
}

// 實現調用grep命令搜索文件
fn main() {
    let mut arg_iter = args();
    arg_iter.next();
    // panic if there is no one
    let pattern = arg_iter.next().unwrap_or("main".to_string());
    let pt =  arg_iter.next().unwrap_or("./".to_string());
    let pt = Path::new(&pt);
    visit_dirs(&pt, &pattern, &call_back).unwrap();
}

```

調用如下：

```
➜  demo git:(master) ✗ ./target/debug/demo "fn main()" ../
fn main() {
fn main() { }
fn main() {
    pub fn main() {
    pub fn main() {}
fn main() {
    pub fn main() {
    pub fn main() {}
```
