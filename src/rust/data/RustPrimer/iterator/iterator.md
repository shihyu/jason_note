# 迭代器

## 從for循環講起

我們在控制語句裡學習了Rust的`for`循環表達式，我們知道，Rust的for循環實際上和C語言的循環語句是不同的。這是為什麼呢？因為，`for`循環不過是Rust編譯器提供的語法糖！

首先，我們知道Rust有一個`for`循環能夠依次對迭代器的任意元素進行訪問，即：

```rust
for i in 1..10 {
    println!("{}", i);
}
```

這裡我們知道， (1..10) 其本身是一個迭代器，我們能對這個迭代器調用 `.next()` 方法，因此，`for`循環就能完整的遍歷一個循環。
而對於`Vec`來說：

```
let values = vec![1,2,3];
for x in values {
    println!("{}", x);
}
```

在上面的代碼中，我們並沒有顯式地將一個`Vec`轉換成一個迭代器，那麼它是如何工作的呢？現在就打開標準庫翻api的同學可能發現了,`Vec`本身並沒有實現 `Iterator` ，也就是說，你無法對`Vec`本身調用 `.next()` 方法。但是，我們在搜索的時候，發現了`Vec`實現了 `IntoIterator` 的 trait。

其實，`for`循環真正循環的，並不是一個迭代器(Iterator)，真正在這個語法糖裡起作用的，是 `IntoIterator` 這個 trait。

因此，上面的代碼可以被展開成如下的等效代碼(只是示意，不保證編譯成功):

```rust
let values = vec![1, 2, 3];

{
    let result = match IntoIterator::into_iter(values) {
        mut iter => loop {
            match iter.next() {
                Some(x) => { println!("{}", x); },
                None => break,
            }
        },
    };
    result
}
```

在這個代碼裡，我們首先對`Vec`調用 `into_iter` 來判斷其是否能被轉換成一個迭代器，如果能，則進行迭代。

那麼，迭代器自己怎麼辦？

為此，Rust在標準庫裡提供了一個實現：

```rust
impl<I: Iterator> IntoIterator for I {
    // ...
}
```

也就是說，Rust為所有的迭代器默認的實現了 `IntoIterator`，這個實現很簡單，就是每次返回自己就好了。

也就是說：

任意一個 `Iterator` 都可以被用在 `for` 循環上！

### 無限迭代器

Rust支持通過省略高位的形式生成一個無限長度的自增序列，即：

```rust
let inf_seq = (1..).into_iter();
```

不過不用擔心這個無限增長的序列撐爆你的內存，佔用你的CPU，因為適配器的惰性的特性，它本身是安全的，除非你對這個序列進行`collect`或者`fold`！
不過，我想聰明如你，不會犯這種錯誤吧！
因此，想要應用這個，你需要用`take`或者`take_while`來截斷他，必須？ 除非你將它當作一個生成器。當然了，那就是另外一個故事了。

## 消費者與適配器

說完了`for`循環，我們大致弄清楚了 `Iterator` 和 `IntoIterator` 之間的關係。下面我們來說一說消費者和適配器。

消費者是迭代器上一種特殊的操作，其主要作用就是將迭代器轉換成其他類型的值，而非另一個迭代器。

而適配器，則是對迭代器進行遍歷，並且其生成的結果是另一個迭代器，可以被鏈式調用直接調用下去。

由上面的推論我們可以得出: *迭代器其實也是一種適配器！*

### 消費者

就像所有人都熟知的生產者消費者模型，迭代器負責生產，而消費者則負責將生產出來的東西最終做一個轉化。一個典型的消費者就是`collect`。前面我們寫過`collect`的相關操作，它負責將迭代器裡面的所有數據取出，例如下面的操作：

```rust
let v = (1..20).collect(); //編譯通不過的！
```

嘗試運行上面的代碼，卻發現編譯器並不讓你通過。因為你沒指定類型！指定什麼類型呢？原來collect只知道將迭代器收集到一個實現了 `FromIterator` 的類型中去，但是，事實上實現這個 trait 的類型有很多（Vec, HashMap等），因此，collect沒有一個上下文來判斷應該將v按照什麼樣的方式收集！！

要解決這個問題，我們有兩種解決辦法：

1. 顯式地標明`v`的類型:

    ```rust
    let v: Vec<_> = (1..20).collect();
    ```

2. 顯式地指定`collect`調用時的類型：

    ```rust
    let v = (1..20).collect::<Vec<_>>();
    ```

當然，一個迭代器中還存在其他的消費者，比如取第幾個值所用的 `.nth()`函數，還有用來查找值的 `.find()` 函數，調用下一個值的`next()`函數等等，這裡限於篇幅我們不能一一介紹。所以，下面我們只介紹另一個比較常用的消費者—— `fold` 。

當然了，提起Rust裡的名字你可能沒啥感覺，其實，`fold`函數，正是大名鼎鼎的 MapReduce 中的 Reduce 函數(稍微有點區別就是這個Reduce是帶初始值的)。

`fold`函數的形式如下：

```rust
fold(base, |accumulator, element| .. )
```

我們可以寫成如下例子：

```rust
let m = (1..20).fold(1u64, |mul, x| mul*x);
```

需要注意的是，`fold`的輸出結果的類型，最終是和`base`的類型是一致的（如果`base`的類型沒指定，那麼可以根據前面`m`的類型進行反推，除非`m`的類型也未指定），也就是說，一旦我們將上面代碼中的`base`從 `1u64` 改成 `1`，那麼這行代碼最終將會因為數據溢出而崩潰！

### 適配器

我們所熟知的生產消費的模型裡，生產者所生產的東西不一定都會被消費者買賬，因此，需要對原有的產品進行再組裝。這個再組裝的過程，就是適配器。因為適配器返回的是一個新的迭代器，所以可以直接用鏈式請求一直寫下去。

前面提到了 Reduce 函數，那麼自然不得不提一下另一個配套函數 —— `map` :

熟悉Python語言的同學肯定知道，Python裡內置了一個`map`函數，可以將一個迭代器的值進行變換，成為另一種。Rust中的`map`函數實際上也是起的同樣的作用，甚至連調用方法也驚人的相似！

```rust
(1..20).map(|x| x+1);
```

上面的代碼展示了一個“迭代器所有元素的自加一”操作，但是，如果你嘗試編譯這段代碼，編譯器會給你提示：

```
warning: unused result which must be used: iterator adaptors are lazy and
         do nothing unless consumed, #[warn(unused_must_use)] on by default
(1..20).map(|x| x + 1);
 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

呀，這是啥？

因為，所有的適配器，都是惰性求值的！

**也就是說，除非你調用一個消費者，不然，你的操作，永遠也不會被調用到！**

現在，我們知道了`map`，那麼熟悉Python的人又說了，是不是還有`filter`！？答，有……用法類似，`filter`接受一個閉包函數，返回一個布爾值，返回`true`的時候表示保留，`false`丟棄。

```rust
let v: Vec<_> = (1..20).filter(|x| x%2 == 0).collect();
```

以上代碼表示篩選出所有的偶數。

## 其他

上文中我們瞭解了迭代器、適配器、消費者的基本概念。下面將以例子來介紹Rust中的其他的適配器和消費者。

### skip和take

`take(n)`的作用是取前`n`個元素，而`skip(n)`正好相反，跳過前`n`個元素。

```rust
let v = vec![1, 2, 3, 4, 5, 6];
let v_take = v.iter()
    .cloned()
    .take(2)
    .collect::<Vec<_>>();
assert_eq!(v_take, vec![1, 2]);

let v_skip: Vec<_> = v.iter()
    .cloned()
    .skip(2)
    .collect();
assert_eq!(v_skip, vec![3, 4, 5, 6]);
```

### zip 和 enumerate的恩怨情仇

`zip`是一個適配器，他的作用就是將兩個迭代器的內容壓縮到一起，形成 `Iterator<Item=(ValueFromA, ValueFromB)>` 這樣的新的迭代器；

```rust
let names = vec!["WaySLOG", "Mike", "Elton"];
let scores = vec![60, 80, 100];
let score_map: HashMap<_, _> = names.iter()
    .zip(scores.iter())
    .collect();
println!("{:?}", score_map);
```

而`enumerate`, 熟悉的Python的同學又叫了：Python裡也有！對的，作用也是一樣的，就是把迭代器的下標顯示出來，即：

```rust
let v = vec![1u64, 2, 3, 4, 5, 6];
let val = v.iter()
    .enumerate()
    // 迭代生成標，並且每兩個元素剔除一個
    .filter(|&(idx, _)| idx % 2 == 0)
    // 將下標去除,如果調用unzip獲得最後結果的話，可以調用下面這句，終止鏈式調用
    // .unzip::<_,_, vec<_>, vec<_>>().1
    .map(|(idx, val)| val)
    // 累加 1+3+5 = 9
    .fold(0u64, |sum, acm| sum + acm);

println!("{}", val);
```

### 一系列查找函數

Rust的迭代器有一系列的查找函數，比如：

* `find()`: 傳入一個閉包函數，從開頭到結尾依次查找能令這個閉包返回`true`的第一個元素，返回`Option<Item>`
* `position()`: 類似`find`函數，不過這次輸出的是`Option<usize>`，第幾個元素。
* `all()`: 傳入一個函數，如果對於任意一個元素，調用這個函數返回`false`,則整個表達式返回`false`，否則返回`true`
* `any()`: 類似`all()`，不過這次是任何一個返回`true`，則整個表達式返回`true`，否則`false`
* `max()`和`min()`: 查找整個迭代器裡所有元素，返回最大或最小值的元素。注意：因為第七章講過的`PartialOrder`的原因，`max`和`min`作用在浮點數上會有不符合預期的結果。


以上，為常用的一些迭代器和適配器及其用法，僅作科普，對於這一章。我希望大家能夠多練習去理解，而不是死記硬背。

好吧，留個習題：

## 習題

利用迭代器生成一個升序的長度為10的水仙花數序列，然後對這個序列進行逆序,並輸出
