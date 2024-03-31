# Rust不可恢復的錯誤

不可恢復的錯誤是檢測到的錯誤，程式員無法處理它。當發生這種錯誤時，列印失敗訊息。清理堆疊然後退出。`panic!``panic!``panic!`

![img](https://tw511.com/upload/images/201910/20191014013938396.png)

**展開(Unwinding) 但是，展開過程需要大量工作。的替代方案是 中止(Aborting) 作業系統將刪除資料。如果從展開切換到中止，那麼需要新增以下語句：**`Unwinding` `Aborting`

```rust
panic = 'abort';
```

下面來看一個`panic!`

```rust
fn main()  
{
   panic!(?No such file exist?);
}
```

執行上面範例程式碼，得到如下結果 -

![img](https://tw511.com/upload/images/201910/20191014013938397.png)

在上面的輸出中，第一行顯示錯誤訊息，它傳達兩個資訊，即 訊息是「沒有這樣的檔案存在」 和 `panic` `panic` `error.rs:3:5`

> 注意：一般來說，不實現`panic!` `panic!`

## panic!的好處

Rust語言沒有緩衝區重讀問題。緩衝區重寫是一種情況，當從緩衝區讀取資料並且程式超出緩衝區時，即它讀取相鄰的儲存器。這導致違反記憶體安全。

下面來看一個簡單的例子：

```rust
fn main()  
{  
   let v = vec![20,30,40];  
   print!("element of a vector is :",v[5]);  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013938398.png)



在上面的例子中，試圖存取索引 在這種情況下，Rust會因為存取無效索引而引發 因此，Rust不會返回任何內容。但是，對於其他語言(如C和C++)，它們會返回一些內容，儘管該向量不屬於該記憶體。這稱為緩衝區重寫，它會導致安全問題。`5` `panic`

**Rust回溯 需要設定**
`RUST_BACKTRACE`
