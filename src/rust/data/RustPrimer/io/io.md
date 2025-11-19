# 標準輸入與輸出

回顧一下我們寫的第一個 Rust 程序就是帶副作用的，其副作用就是向標準輸出(stdout)，通常是終端或屏幕，輸出了 Hello, World! 讓屏幕上這幾個字符的地方點亮起來。`println!` 宏是最常見的輸出，用宏來做輸出的還有 `print!`，兩者都是向標準輸出(stdout)輸出，兩者的區別也一眼就能看出。至於格式化輸出，[基礎運算符和字符串格式化小節](../type/operator-and-formatting.md)有詳細說明，這裡就不再囉嗦了。

更通用的標準輸入與輸出定義在 `std::io` 模塊裡，調用 `std::io::stdin()` 和 `std::io::stdout()` 兩個函數分別會得到輸入句柄和輸出句柄(哎，[句柄](https://zh.wikipedia.org/wiki/%E5%8F%A5%E6%9F%84)這個詞是計算機史上最莫名其妙的翻譯了)，這兩個句柄默認會通過互斥鎖同步，也就是說不讓多個進程同時讀或寫標準輸入輸出，不然的話如果一個進程要往標準輸出畫馬，一個進程要畫驢，兩個進程同時寫標準輸出的話，最後可能就給畫出一頭騾子了，如果更多進程畫不同的動物最後可能就成四不像了。除了隱式地用互斥鎖，我們還可以顯式地在句柄上調用 `.lock()`。輸入輸出句柄實現了前面講的讀寫 Trait，所以是 reader/writer，就可以調接口來讀寫標準輸入與輸出了。舉幾個栗子：

```rust
use std::io;

fn read_from_stdin(buf: &mut String) -> io::Result<()> {
	try!(io::stdin().read_line(buf));
	Ok(())
}
```

```rust
use std::io;

fn write_to_stdout(buf: &[u8]) -> io::Result<()> {
	try!(io::stdout().write(&buf));
	Ok(())
}
```

可以看到上面的例子都是返回了 `io::Result<()>` 類型，這不是偶然，而是 IO 操作通用的寫法，因為 IO 操作是程序與外界打交道，所以都是有可能失敗的，用 `io::Result<T>` 把結果包起來，`io::Result<T>` 只是標準 `Result<T,E>` 中 `E` 固定為 `io::Error` 後類型的別名，而作為有副作用的操作我們一般是不用關心其返回值的，因為執行這類函數其真正的意義都體現在副作用上面了，所以返回值只是用來表示是否成功執行，而本身 `Result` 類型本身已經可以表示執行狀態了，裡面的 `T` 是什麼則無關緊要，既然 `T` 沒什麼意義，那我們就選沒什麼意義的 `unit` 類型好了，所以 IO 操作基本上都是使用 `io::Result<()>`。

另外有一個地方需要注意的是由於 IO 操作可能會失敗所以一般都是和 `try!` 宏一起使用的，但是 `try!` 在遇到錯誤時會把錯誤 `return` 出去的，所以需要保證包含 `try!` 語句的函數其返回類型是 `io::Result<T>`，很多新手文檔沒仔細看就直接查 std api 文檔，然後照著 api 文檔裡面的例子把帶 IO 操作的 `try!` 宏寫到了 `main` 函數裡。結果一編譯，擦，照著文檔寫都編譯不過，什麼爛文檔。其實點一下 api 文檔上面的運行按鈕就會發現文檔裡面的例子都是把 `try!` 放在另一個函數裡面的，因為 `main` 函數是沒有返回值的，而 `try!` 會返回 `io::Result<T>`，所以直接把 `try!` 放 `main` 函數裡面肯定要跪。比如下面的從標準輸入讀取一行輸入，由於把 `try!` 放在了 main 函數裡，所以是編譯不過的。

```rust
use std::io;

fn main() {
	let mut input = String::new();
	try!(io::stdin().read_line(&mut input));
	println!("You typed: {}", input.trim());
}
```

這裡有一件事需要主要的是 Rust 裡面沒有辦法從鍵盤獲取一個數字類型的值。實際上像 C 這樣的語言也不是直接獲取了數字類型，它只不過是做了一種轉換。那麼我們如果想要從鍵盤獲取一個數字類型應該怎麼做呢？

```rust
fn main() {
	let mut input = String::new();
		std::io::stdin()
			.read_line(&mut input)
			.expect("Failed to read line");
    // 這裡等效的寫法是：
    // let num: i32 = input.trim().parse().unwrap(); 
	let num = input.trim().parse::<i32>().unwrap();
	println!("您輸入的數字是：{}", num);
}
```

如果有很多地方都需要輸入數字可以自行編寫一個 `numin` 宏:

```rust
macro_rules! numin {
	  () =>{
	      {
            let mut input = String::new();
	          std::io::stdin()
	              .read_line(&mut input)
                .expect("Failed to read line");
	          input.trim().parse().unwrap()
        }
    };
}
```

於是上面的程序可以被改寫成：

```

fn main() {
    let num: i32 = numin!();
	println!("您輸入的數字是：{}", num);
}
```

不過如果用戶輸入的不是數字，那麼就會導致錯誤。這一點和 C 裡面是非常相似的。當然您可以把程序寫得再複雜一點兒來保證用戶輸入的一定是數字。不過這些就不是我們這一節要討論的內容了。

還有一點一些從其它語言轉過來的程序員可能會疑惑的是，如何從命令行接受輸入參數，因為 C 裡面的 main 函數可以帶參數所以可以直接從 main 函數的參數裡獲取輸入參數。但其實這類輸入與我們這裡講的有很大的差別的，它在 Rust 裡面被歸為環境變量，可以通過 `std::env::args()` 獲取，這個函數返回一個 `Args` 迭代器，其中第一個就是程序名，後面的都是輸入給程序的命令行參數。

```rust
use std::env;

fn main() {
	let args = env::args();
	for arg in args {
		println!("{}", arg);
	}
}
```

將上面的程序存為 *args.rs* 然後編譯執行，結果如下

```
$ rustc args.rs
$ ./args a b c
./args
a
b
c
```

