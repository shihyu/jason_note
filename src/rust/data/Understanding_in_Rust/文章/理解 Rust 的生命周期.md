# 理解 Rust 的生命週期

作者：丹尼爾·P·克拉克

原文鏈接：https://www.cloudbees.com/blog/lifetimes-in-rust

高級語言很方便地處理我們代碼中的每個對象的存活的範圍(`scope`), 我們不需要理解這些對象的生命週期。Rust同樣為我們管理著生命週期，我們可以通過所有權(`ownership`)和借用(`borrowing`)對簡單情況進行更多的控制,但是對於複雜的情況，我們需要在代碼中給出識別標識，以便編譯器能夠理解更大的生命週期的範圍。

簡單的說，一切的一切歸根結底都是為了在對象使用完之後就釋放它。高級語言如Go、Ruby、Python等等，使用垃圾回收器在整個代碼中掃描和標記對象，以查看它們是否準備好從內存中釋放掉，並將對所有已標記可釋放的對象執行釋放操作。當你不再使用對象時，低級語言如C、彙編要求你手工釋放它們。

Rust避免了垃圾回收和手寫代碼釋放內存的成本，它根據代碼庫中每個對象的生命週期維護釋放內存的時間。生存期主要由所有權系統決定（描述代碼的哪個部分負責擁有內存中對象的系統），以及在複雜情況下，由幫助編譯器而提供的手動生命週期描述符來決定。一旦對象的生命週期束，內存將立即釋放。

## 簡單的生命週期

Rust的**const**類型的生命週期是整個程序，它的值可以內聯到代碼中的任何地方。

```rust
const MAJOR_VERSION: i32 = 1;
```

**static**類型的生命週期也是整個程序，但它不會被內聯，它存在於內存的固定位置。

```rust
static MINOR_VERSION: i32 = 0;
```

大多數其他對象的生命週期只發生在塊(`block`)的範圍內，或者直到某個方法調用奪走了它們的所有權。如果一個對象要在方法調用中超出其使用範圍而存在(意思是方法調用完還繼續存活)，那麼該方法需要借用(`borrow`)它，或者複製(`copy`)它，以便在方法完成後，它的生命週期可以在外部作用域中繼續長存。

```rust
let money: String = "42".to_string();
fn borrow_it(qty: &String) {
  println!("Your money total is ${}", qty)
}
borrow_it(&money); // borrowed ownership
// the ownership of money has been returned to this higher scope
fn consume_it(qty: String) {
  println!("My money total is ${}", qty)
}
consume_it(money);
// money memory is freed as the ownership has been
// taken into the methods scope and that scope has ended.
println!("No money: ${}", money);
// This fails
```

當我們運行上面的代碼的時候，Rust會告訴我們哪裡出錯了:

```rust
error[E0382]: use of moved value: `money`
  --> src/main.rs:19:29
   |
15 |   consume_it(money);
   |              ----- value moved here
...
19 |   println!("No money: ${}", money);
   |                             ^^^^^ value used here after move
   |
   = note: move occurs because `money` has type `std::string::String`, which does not implement the `Copy` trait
```

請注意，它告訴我們，如果`std::string::String`如果實現了`Copy trait`，我們的代碼就可以工作。如果您將上述代碼更改為使用`i32`類型而不是String，它將正常地工作；`i32`確實實現了`Copy trait`，編譯器將從塊中的用法推斷出該值稍後將被使用，因此在這種情況下，將在借用時執行復制。即使複製後，money的生命週期也會在最後一次使用時結束，因為它會被最後的`println!`命令所使用。

## 複雜的生命週期

有時候，當代碼中沒有足夠的信息來確定生命週期時，Rust編譯器會要求描述/註釋生命週期。

```rust
// 地球
#[derive(Debug)]
struct Earth {
  location: String,
}
// 恐龍
#[derive(Debug)]
struct Dinosaur<'a> {
  location: &'a Earth,
  name: String,
}
fn main() {
  let new_york = Earth {
    location: "New York, NY".to_string(),
  };
  let t_rex = Dinosaur {
    location: &new_york,
    name: "T Rex".to_string(),
  };
  println!("{:?}", t_rex);
}
```

在上面的例子中，你可以看到一個生命週期的註釋`'a`。當我們的struct借用`Earth`實例的時候, 它需要增加生命週期標識，它會幫助編譯器理解🦕恐龍(`Dinosaur`)不能比🌍地球(`Earth`)還長壽，因為它引用了Earth。

當我第一次在自己的項目中處理實現和學習生命週期的時候，有一個技巧幫助了我。當程序建議需要它們時，就是在它們可能不需要放置的地方放置了更多的生命週期引用。我發現編譯器的錯誤消息在“生命週期註釋存在並且錯誤時”比“不存在和錯誤時”更能理解我的意圖。當然，我建議查看實現了生存期的代碼，以幫助您開始工作。一點點的嘗試和錯誤將幫助您快速理解。

上面恐龍的一個示例`impl`代碼如下：

```rust
impl<'a> From<Dinosaur<'a>> for String {
  fn from(d: Dinosaur) -> String {
    format!("{:?}", d)
  }
}
// replace the above println! with
println!("{}", String::from(t_rex));
```

## 範圍生命週期

當需要從一個底層的或者內部(lower/inner)的scope中獲取值時， 最好的方法就是把需要的結果值賦值給更高的scope中的變量:

```rust
{
  // outer scope
  let result: i32;
  {
    // inner scope
    result = 42 + 42;
  }
  println!("{}", result);
}
```

如果我們嘗試在內部的scope中將結果直接賦值給外部的變量而沒有預先聲明它，我們會得到如下的錯誤：

```rust
error[E0425]: cannot find value `result` in this scope
  --> src/main.rs:10:18
   |
10 |   println!("{}", result);
   |                  ^^^^^^ not found in this scope
```

這是因為在inner scope中對象的生命週期只限於inner scope, 除非它們被賦值給外部的更長的scope中的對象。返回值可以看作是外部的scope的對象。我們改造一下上面的例子：

```rust
{
  let result: i32 = {
    42 + 42
  };
  println!("{}", result);
}
```

正常輸出 84。

當我們沒有正確使用scope時編譯器會洞悉到我們的錯誤。所以我們直接寫我們認為正確的代碼就好了，簡單按照編譯的反饋信息修改我們的錯誤就好了，這裡有個錯誤的例子：

```rust
{
  let result: &i32;
  
  {
    let x = 42 + 42;
    result = &x;
  }
  println!("{}", result);
}
```

編譯它:

```rust
error[E0597]: `x` does not live long enough
  --> src/main.rs:7:3
   |
6  |     result = &x;
   |               - borrow occurs here
7  |   }
   |   ^ `x` dropped here while still borrowed
...
10 | }
   | - borrowed value needs to live until here
```

這裡輸出很清晰的生命週期圖。或者使用`clone`或者使用`copy`等手段可以把值返回給更高的scope。但是這經常會帶來一些性能上的影響因為複製內存中的數據要比傳引用要化更長的時間。

## 總結

在Rust所有涉及生命週期的事情中，註釋似乎是一個很大的障礙，因為語法看起來有點過時。但重要的是，當你使用它們的時候，你不會改變它們的方式——你其實只是簡單地宣佈它們。也就是說，有註釋的生命週期與沒有寫註釋的生命週期的工作方式是相同的。它們只是幫助編譯器澄清生命週期所涉及的上下文的標記。
除此之外，生命週期很簡單。只需編寫代碼，看看會發生什麼。Rust語言的編譯器將是您的導師，您的理解將隨著您從編譯器非常智能的錯誤消息中學習而增長。你可以大膽地編碼，因為Rust可以幫助你在未知的海洋中遨遊。
