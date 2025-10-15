# Mutex 與 RwLock

## Mutex

`Mutex` 意為互斥對象，用來保護共享數據。Mutex 有下面幾個特徵：

1. `Mutex` 會等待獲取鎖令牌(token)，在等待過程中，會阻塞線程。直到鎖令牌得到。同時只有一個線程的 `Mutex` 對象獲取到鎖；
2. `Mutex` 通過 `.lock()` 或 `.try_lock()` 來嘗試得到鎖令牌，被保護的對象，必須通過這兩個方法返回的 `RAII` 守衛來調用，不能直接操作；
3. 當 `RAII` 守衛作用域結束後，鎖會自動解開；
4. 在多線程中，`Mutex` 一般和 `Arc` 配合使用。

示例：

```rust
use std::sync::{Arc, Mutex};
use std::thread;
use std::sync::mpsc::channel;

const N: usize = 10;

// Spawn a few threads to increment a shared variable (non-atomically), and
// let the main thread know once all increments are done.
//
// Here we're using an Arc to share memory among threads, and the data inside
// the Arc is protected with a mutex.
let data = Arc::new(Mutex::new(0));

let (tx, rx) = channel();
for _ in 0..10 {
    let (data, tx) = (data.clone(), tx.clone());
    thread::spawn(move || {
        // The shared state can only be accessed once the lock is held.
        // Our non-atomic increment is safe because we're the only thread
        // which can access the shared state when the lock is held.
        //
        // We unwrap() the return value to assert that we are not expecting
        // threads to ever fail while holding the lock.
        let mut data = data.lock().unwrap();
        *data += 1;
        if *data == N {
            tx.send(()).unwrap();
        }
        // the lock is unlocked here when `data` goes out of scope.
    });
}

rx.recv().unwrap();
```

### `lock` 與 `try_lock` 的區別

`.lock()` 方法，會等待鎖令牌，等待的時候，會阻塞當前線程。而 `.try_lock()` 方法，只是做一次嘗試操作，不會阻塞當前線程。

當 `.try_lock()` 沒有獲取到鎖令牌時，會返回 `Err`。因此，如果要使用 `.try_lock()`，需要對返回值做仔細處理（比如，在一個循環檢查中）。


__點評__：Rust 的 Mutex 設計成一個對象，不同於 C 語言中的自旋鎖用兩條分開的語句的實現，更安全，更美觀，也更好管理。


## RwLock

`RwLock` 翻譯成 `讀寫鎖`。它的特點是：

1. 同時允許多個讀，最多隻能有一個寫；
2. 讀和寫不能同時存在；

比如：

```rust
use std::sync::RwLock;

let lock = RwLock::new(5);

// many reader locks can be held at once
{
    let r1 = lock.read().unwrap();
    let r2 = lock.read().unwrap();
    assert_eq!(*r1, 5);
    assert_eq!(*r2, 5);
} // read locks are dropped at this point

// only one write lock may be held, however
{
    let mut w = lock.write().unwrap();
    *w += 1;
    assert_eq!(*w, 6);
} // write lock is dropped here
```

### 讀寫鎖的方法

1. `.read()`
2. `.try_read()`
3. `.write()`
4. `.try_write()`

注意需要對 `.try_read()` 和 `.try_write()` 的返回值進行判斷。
