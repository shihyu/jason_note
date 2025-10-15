# print! 宏

我們在快速入門中就提到過標準輸出的行緩衝。它一個表現就是 `print!` 宏。如果你在 `print!` 宏後面接上一個輸入就會發現這種按行緩衝的機制。

```rust
fn main() {
	print!("hello!\ninput:");
	let mut input = String::new();
		std::io::stdin()
			.read_line(&mut input)
			.expect("Failed to read line");
	println!("line:{}",input);
}
```

您可以編譯並運行這段程序試一試，您會發現我們並沒有得到預期的（下劃線代表光標的位置）：

```
hello!
input:_
```

而是得到了：

```
hello!
_
```

這就是由於標準輸出中的這種行緩衝機制，在遇到換行符之前，輸出的內容並不會隱式的刷新，這就導致 `print!` 宏和 `println!` 宏實際上並不完全相同。在標準庫中 `print!` 宏是這樣的：

```rust
macro_rules! print {
    ($($arg:tt)*) => { ... };
}
```

由此，我們可以對它進行改進，使它和 `println!` 宏被自動刷新，不過這種刷新是一種顯式的刷新。

```rust
use std::io::{self, Write};

macro_rules! printf {
	($($arg:tt)*) =>{
		print!($($arg)*);
		io::stdout().flush().unwrap();
	}
}
```

此外，當您需要刷新還沒有遇到換行符的一行內容的時候您都可以使用 `io::stdout().flush().unwrap();` 進行刷新，不過需要注意的是要先 `use std::io::{self, Write};` 如果您不這樣做，將會得到一個錯誤。
