# 動態數組Vec
在第七章我們粗略介紹了一下Vec的用法。實際上，作為Rust中一個非常重要的數據類型，熟練掌握Vec的用法能大大提升我們在Rust世界中的編碼能力。

## 特性及聲明方式

和我們之前接觸到的Array不同，`Vec`具有動態的添加和刪除元素的能力，並且能夠以`O(1)`的效率進行隨機訪問。同時，對其尾部進行push或者pop操作的效率也是平攤`O(1)`的。
同時，有一個非常重要的特性（雖然我們編程的時候大部分都不會考量它）就是，Vec的所有內容項都是生成在heap空間上的，也就是說，你可以輕易的將Vec move出一個stack而不用擔心內存拷貝影響執行效率——畢竟只是拷貝的stack上的指針。

另外的就是，`Vec<T>`中的泛型`T`必須是`Sized`的，也就是說必須在編譯的時候就知道存一個內容項需要多少內存。對於那些在編譯時候未知大小的項（函數類型等），我們可以用`Box`將其包裹，當成一個指針。

### new
我們可以用`std::vec::Vec::new()`的方式來聲明一個Vec。

```rust
let mut v1: Vec<i32> = Vec::new();
```

這裡需要注意的是，`new`函數並沒有提供一個能顯式規定其泛型類型的參數，也就是說，上面的代碼能根據`v1`的類型自動推導出`Vec`的泛型;但是，你不能寫成如下的形式：

```rust
let mut v1 = Vec::new::<i32>();
// 與之對比的,collect函數就能指定：
// let mut v2 = (0i32..5).collect::<Vec<i32>>();
```

這是因為這兩個函數的聲明形式以及實現形式，在此，我們不做深究。


### 宏聲明

相比調用new函數，Rust提供了一種更加直觀便捷的方式聲明一個動態數組： `vec!` 宏。

```rust
let v: Vec<i32> = vec![];

// 以下語句相當於：
// let mut temp = Vec::new();
// temp.push(1);
// temp.push(2);
// temp.push(3);
// let v = temp;
let v = vec![1, 2, 3];

let v = vec![0; 10]; //注意分號，這句話聲明瞭一個 內容為10個0的動態數組
```

### 從迭代器生成

因為Vec實現了`FromIterator`這個trait，因此，藉助collect，我們能將任意一個迭代器轉換為Vec。

```rust
let v: Vec<_> = (1..5).collect();
```

## 訪問及修改

### 隨機訪問

就像數組一樣，因為Vec藉助`Index`和`IndexMut`提供了隨機訪問的能力，我們通過`[index]`來對其進行訪問，當然，既然存在隨機訪問就會出現越界的問題。而在Rust中，一旦越界的後果是極其嚴重的，可以導致Rust當前線程panic。因此，除非你確定自己在幹什麼或者在`for`循環中，不然我們不推薦通過下標訪問。

以下是例子：

```rust
let a = vec![1, 2, 3];
assert_eq!(a[1usize], 2);
```

那麼，Rust中有沒有安全的下標訪問機制呢？答案是當然有：—— `.get(n: usize)` （`.get_mut(n: usize)`） 函數。
對於一個數組，這個函數返回一個`Option<&T>` (`Option<&mut T>`)，當Option==None的時候，即下標越界，其他情況下，我們能安全的獲得一個Vec裡面元素的引用。

```rust
let v =vec![1, 2, 3];
assert_eq!(v.get(1), Some(&2));
assert_eq!(v.get(3), None);
```

### 迭代器

對於一個可變數組，Rust提供了一種簡單的遍歷形式—— for 循環。
我們可以獲得一個數組的引用、可變引用、所有權。

```rust
let v = vec![1, 2, 3];
for i in &v { .. } // 獲得引用
for i in &mut v { .. } // 獲得可變引用
for i in v { .. } // 獲得所有權，注意此時Vec的屬主將會被轉移！！
```

但是，這麼寫很容易出現多層`for`循環嵌套，因此，`Vec`提供了一個`into_iter()`方法，能顯式地將自己轉換成一個迭代器。然而迭代器怎麼用呢？我們下一章將會詳細說明。

### push的效率研究

前面說到，`Vec`有兩個`O(1)`的方法，分別是`pop`和`push`，它們分別代表著將數據從尾部彈出或者裝入。理論上來說，因為`Vec`是支持隨機訪問的，因此`push`效率應該是一致的。但是實際上，因為Vec的內部存在著內存拷貝和銷燬，因此，如果你想要將一個數組，從零個元素開始，一個一個的填充直到最後生成一個非常巨大的數組的話，預先為其分配內存是一個非常好的辦法。

這其中，有個關鍵的方法是reserve。

如下代碼(注意：由於SystemTime API在1.8以後才穩定, 請使用1.8.0 stable 以及以上版本的rustc編譯)：

```rust
use std::time;

fn push_1m(v: &mut Vec<usize>, total: usize) {
    let e = time::SystemTime::now();
    for i in 1..total {
        v.push(i);
    }
    let ed = time::SystemTime::now();
    println!("time spend: {:?}", ed.duration_since(e).unwrap());
}

fn main() {
    let mut v: Vec<usize> = vec![];
    push_1m(&mut v, 5_000_000);
    let mut v: Vec<usize> = vec![];
    v.reserve(5_000_000);
    push_1m(&mut v, 5_000_000);
}
```

在筆者自己的筆記本上，編譯好了debug的版本，上面的代碼跑出了：

```
➜  debug git:(master) ✗ time ./demo
time spend: Duration { secs: 0, nanos: 368875346 }
time spend: Duration { secs: 0, nanos: 259878787 }
./demo  0.62s user 0.01s system 99% cpu 0.632 total

```

好像並沒有太大差異？然而切換到release版本的時候:

```
➜  release git:(master) ✗ time ./demo
time spend: Duration { secs: 0, nanos: 53389934 }
time spend: Duration { secs: 0, nanos: 24979520 }
./demo  0.06s user 0.02s system 97% cpu 0.082 total
```

注意消耗的時間的位數。可見，在去除掉debug版本的調試信息之後，是否預分配內存消耗時間降低了一倍！

這樣的成績，可見，預先分配內存確實有助於提升效率。

有人可能會問了，你這樣糾結這點時間，最後不也是節省在納秒級別的麼，有意義麼？當然有意義。

第一，納秒也是時間，這還是因為這個測試的`Vec`只是最簡單的內存結構。一旦涉及到大對象的拷貝，所花費的時間可就不一定這麼少了。
第二，頻繁的申請和刪除heap空間，其內存一旦達到瓶頸的時候你的程序將會異常危險。

更多`Vec`的操作，請參照標準庫的api。
