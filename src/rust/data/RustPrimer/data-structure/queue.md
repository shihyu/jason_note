# 隊列

## 隊列簡介
隊列是一種特殊的線性表，特殊之處在於它只允許在表的前端（front）進行刪除操作，而在表的後端（rear）進行插入操作，和棧一樣，隊列是一種操作受限制的線性表。進行插入操作的端稱為隊尾，進行刪除操作的端稱為隊頭。隊列中沒有元素時，稱為空隊列。

>在隊列的形成過程中，可以利用線性鏈表的原理，來生成一個隊列。基於鏈表的隊列，要動態創建和刪除節點，效率較低，但是可以動態增長。隊列採用的 **FIFO(first in first out)**，新元素（等待進入隊列的元素）總是被插入到鏈表的尾部，而讀取的時候總是從鏈表的頭部開始讀取。每次讀取一個元素，釋放一個元素。所謂的動態創建，動態釋放。因而也不存在溢出等問題。由於鏈表由結構體間接而成，遍歷也方便。

## 隊列實現
下面看一下我們使用 Vec 來實現的簡單 Queue：

主要實現的`new( ), push( ), pop( )`三個方法

```rust
#[derive(Debug)]
struct Queue<T> {
    qdata: Vec<T>,
}

impl <T> Queue<T> {
    fn new() -> Self {
        Queue{qdata: Vec::new()}
    }

    fn push(&mut self, item:T) {
        self.qdata.push(item);
    }

    fn pop(&mut self) -> T{
        self.qdata.remove(0)
    }
}

fn main() {
    let mut q = Queue::new();
    q.push(1);
    q.push(2);
    println!("{:?}", q);
    q.pop();
    println!("{:?}", q);
    q.pop();
}
```

## 練習
看起來比我們在上一節實現的Stack簡單多了。不過這個Queue實現是有Bug的。

練習：在這個代碼的上找到 Bug，並修改。

提示：`pop( )`方法有 Bug，請參考 Stack 小節的實現，利用 Option 來處理。
