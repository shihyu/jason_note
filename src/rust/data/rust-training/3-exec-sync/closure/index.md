
## 閉包的簡單使用
閉包的定義以一對豎線（|）開始，在豎線中指定閉包的參數；如果有多於一個參數，可以使用逗號分隔，比如 |param1, param2|
使用閉包的原因是我們需要在一個位置定義代碼，儲存代碼，並在之後的位置實際調用它；期望調用的代碼現在儲存在 expensive_closure 中。

```
use std::thread;
use core::time::Duration;
fn main() {
    let expensive_closure = |num| {
        println!("calculating slowly...");
        thread::sleep(Duration::from_secs(2));
        num
    };
    expensive_closure(2);
}
```

當我們需要調用它時，向函數一樣執行它。

值得注意的是，上面的閉包中的參數num並沒有參數類型，這是因為閉包的參數類型是由上下文決定的。
當然也可以為參數指定類型，比如 |num: u32|。這樣閉包就更像函數了。

```
fn  add_one_v1   (x: u32) -> u32 { x + 1 }
let add_one_v2 = |x: u32| -> u32 { x + 1 };

```

