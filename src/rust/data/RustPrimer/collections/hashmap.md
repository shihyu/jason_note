# 哈希表 HashMap

和動態數組`Vec`一樣，哈希表(HashMap)也是Rust內置的集合類型之一，同屬`std::collections`模塊下。

它提供了一個平均複雜度為`O(1)`的查詢方法，是實現快速搜索必備的類型之一。

這裡呢，主要給大家介紹一下HashMap的幾種典型用法。

## HashMap的要求

顧名思義, HashMap 要求一個可哈希（實現 Hash trait）的Key類型，和一個編譯時知道大小的Value類型。
同時，Rust還要求你的Key類型必須是可比較的，在Rust中，你可以為你的類型輕易的加上編譯器屬性：

```rust
#[derive(PartialEq, Eq, Hash)]
```

這樣，即可將你的類型轉換成一個可以作為Hash的Key的類型。
但是，如果你想要自己實現`Hash`這個trait的話，你需要謹記兩點：

* 1. 如果 Key1==Key2 ,那麼一定有 Hash(Key1) == Hash(Key2)
* 2. 你的Hash函數本身不能改變你的Key值，否則將會引發一個邏輯錯誤（很難排查，遇到就完的那種）

什麼？你看到 `std::hash::Hash` 這個 trait 中的函數沒有`&mut self`的啊！但是，你不要忘了Rust中還有`Cell`和`RefCell`這種存在，他們提供了不可變對象的內部可變性，具體怎麼變呢，請參照第20章。

另外，要保證你寫的Hash函數不會被很輕易的碰撞，即 `Key1! = Key2`，但 `Hash(Key1)==Hash(Key2)`，碰撞的嚴重了，HashMap甚至有可能退化成鏈表！

這裡筆者提議，別費勁，就按最簡單的來就好。

## 增刪改查

對於這種實用的類型，我們推薦用一個例子來解釋：

```rust
use std::collections::HashMap;

// 聲明
let mut come_from = HashMap::new();
// 插入
come_from.insert("WaySLOG", "HeBei");
come_from.insert("Marisa", "U.S.");
come_from.insert("Mike", "HuoGuo");

// 查找key
if !come_from.contains_key("elton") {
    println!("Oh, 我們查到了{}個人，但是可憐的Elton貓還是無家可歸", come_from.len());
}

// 根據key刪除元素
come_from.remove("Mike");
println!("Mike貓的家鄉不是火鍋！不是火鍋！不是火鍋！雖然好吃！");

// 利用get的返回判斷元素是否存在
let who = ["MoGu", "Marisa"];
for person in &who {
    match come_from.get(person) {
        Some(location) => println!("{} 來自: {}", person, location),
        None => println!("{} 也無家可歸啊.", person),
    }
}

// 遍歷輸出
println!("那麼，所有人呢？");
for (name, location) in &come_from {
    println!("{}來自: {}", name, location);
}
```

這段代碼輸出：

```
Oh, 我們查到了3個人，但是可憐的Elton貓還是無家可歸
Mike貓的家鄉不是火鍋！不是火鍋！不是火鍋！雖然好吃！
MoGu 也無家可歸啊.
Marisa 來自: U.S.
那麼，所有人呢？
Marisa來自: U.S.
WaySLOG來自: HeBei
```

## entry

我們在編程的過程中，經常遇到這樣的場景，統計一個字符串中所有的字符總共出現過幾次。藉助各種語言內置的Map類型我們總能完成這件事，但是完成的幾乎都並不令人滿意。很多人討厭的一點是：為什麼我要判斷這個字符在字典中有沒有出現，就要寫一個大大的if條件！煩不煩？煩！於是，現代化的編程語言開始集成了類似Python裡`setdefault`類似的特性（方法），下面是一段Python代碼：

```python
val = {}
for c in "abcdefasdasdawe":
    val[c] = 1 + val.setdefault(c, 0)
print val
```

唔，總感覺怪怪的。那麼Rust是怎麼解決這個問題的呢？
以下內容摘自標註庫api註釋：

```rust
use std::collections::HashMap;

let mut letters = HashMap::new();

for ch in "a short treatise on fungi".chars() {
    let counter = letters.entry(ch).or_insert(0);
    *counter += 1;
}

assert_eq!(letters[&'s'], 2);
assert_eq!(letters[&'t'], 3);
assert_eq!(letters[&'u'], 1);
assert_eq!(letters.get(&'y'), None);
```

Rust為我們提供了一個名叫 `entry` 的api，它很有意思，和Python相比，我們不需要在一次迭代的時候二次訪問原map，只需要借用 entry 出來的Entry類型（這個類型持有原有HashMap的引用）即可對原數據進行修改。就語法來說，毫無疑問Rust在這個方面更加直觀和具體。
