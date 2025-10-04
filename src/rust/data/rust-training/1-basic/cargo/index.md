在 Rust 中，最推薦的創建項目方式是使用 cargo。 

使用 cargo new 命令，可以創建一個新的 Rust 項目，並自動生成項目的目錄結構和文件。

```shell
# cargo new hello_world
```

檢查項目使用是否可以通過編譯

```shell
# cargo check
```

編譯項目
```shell
# cargo build
# cargo build --release
```

運行項目
```shell
# cargo run
```


## cargo 測試

如下是一段單元測試的代碼
```
struct Counter {
    count: u32,
}

impl Counter {
    fn new() -> Counter {
        Counter { count: 0 }
    }
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;

        if self.count < 6 {
            Some(self.count)
        } else {
            None
        }
    }
}

#[test]
fn calling_next_directly() {
    let mut counter = Counter::new();

    assert_eq!(counter.next(), Some(1));
    assert_eq!(counter.next(), Some(2));
    assert_eq!(counter.next(), Some(3));
    assert_eq!(counter.next(), Some(4));
    assert_eq!(counter.next(), Some(5));
    assert_eq!(counter.next(), None);
}
```

執行cargo test可以運行以上單元測試

```shell
# cargo test
```
