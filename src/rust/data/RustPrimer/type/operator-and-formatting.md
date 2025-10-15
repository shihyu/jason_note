# 操作符和格式化字符串

現在的Rust資料，無論是Book還是RustByExample都沒有統一而完全的介紹Rust的操作符。一個很重要的原因就是，Rust的操作符號和C++大部分都是一模一樣的。

## 一元操作符

顧名思義，一元操作符是專門對一個Rust元素進行操縱的操作符，主要包括以下幾個:

* `-`: 取負，專門用於數值類型。
* `*`: 解引用。這是一個很有用的符號，和`Deref`（`DerefMut`）這個trait關聯密切。
* `!`: 取反。取反操作相信大家都比較熟悉了，不多說了。有意思的是，當這個操作符對數字類型使用的時候，會將其每一位都置反！也就是說，你對一個`1u8`進行`!`的話你將會得到一個`254u8`。
* `&`和`&mut`: 租借，borrow。向一個owner租借其使用權，分別是租借一個只讀使用權和讀寫使用權。

## 二元操作符

### 算數操作符

算數運算符都有對應的trait的，他們都在`std::ops`下：

* `+`: 加法。實現了`std::ops::Add`。
* `-`: 減法。實現了`std::ops::Sub`。
* `*`: 乘法。實現了`std::ops::Mul`。
* `/`: 除法。實現了`std::ops::Div`。
* `%`: 取餘。實現了`std::ops::Rem`。

### 位運算符

和算數運算符差不多的是，位運算也有對應的trait。

* `&`: 與操作。實現了`std::ops::BitAnd`。
* `|`: 或操作。實現了`std::ops::BitOr`。
* `^`: 異或。實現了`std::ops::BitXor`。
* `<<`: 左移運算符。實現了`std::ops::Shl`。
* `>>`: 右移運算符。實現了`std::ops::Shr`。

### 惰性boolean運算符

邏輯運算符有三個，分別是`&&`、`||`、`!`。其中前兩個叫做惰性boolean運算符，之所以叫這個名字。是因為在Rust裡也會出現其他類C語言的邏輯短路問題。所以取了這麼一個高大上然並卵的名字。
其作用和C語言裡的一毛一樣啊！哦，對了，有點不同的是Rust裡這個運算符只能用在bool類型變量上。什麼 `1 && 1` 之類的表達式給我死開。

### 比較運算符

比較運算符其實也是某些trait的語法糖啦，不同的是比較運算符所實現的trait只有兩個`std::cmp::PartialEq`和`std::cmp::PartialOrd`

其中， `==`和`!=`實現的是`PartialEq`。
而，`<`、`>`、`>=`、`<=`實現的是`PartialOrd`。

邊看本節邊翻開標準庫（好習慣，鼓勵）的同學一定會驚奇的發現，不對啊，`std::cmp`這個mod下明明有四個trait，而且從肉眼上來看更符合邏輯的`Ord`和`Eq`豈不是更好？其實，Rust對於這四個trait的處理是很明確的。分歧主要存在於浮點類型。
熟悉IEEE的同學一定知道浮點數有一個特殊的值叫`NaN`，這個值表示未定義的一個浮點數。在Rust中可以用`0.0f32 / 0.0f32`來求得其值。那麼問題來了，這個數他是一個確定的值，但是它表示的是一個不確定的數！那麼 `NaN != NaN` 的結果是啥？標準告訴我們，是 `true` 。但是這麼寫又不符合`Eq`的定義裡`total equal`(每一位一樣兩個數就一樣)的定義。因此有了`PartialEq`這麼一個定義，我們只支持部分相等好吧，NaN這個情況我就給它特指了。

為了普適的情況，Rust的編譯器選擇了`PartialOrd`和`PartialEq`來作為其默認的比較符號的trait。我們也就和中央保持一致就好。

## 類型轉換運算符

其實這個並不算運算符，因為他是個單詞`as`。

這個就是C語言中各位熟悉的顯式類型轉換了。

show u the code:

```rust
fn avg(vals: &[f64]) -> f64 {
    let sum: f64 = sum(vals);
    let num: f64 = len(vals) as f64;
    sum / num
}
```

## 重載運算符

上面說了很多trait。有人會問了，你說這麼多幹啥？

答，為了運算符重載！

Rust是支持運算符重載的（某咖啡語言哭暈在廁所）。

關於這部分呢，在本書的第30節會有很詳細的敘述，因此在這裡我就不鋪開講了，上個栗子給大家，僅作參考：

```rust
use std::ops::{Add, Sub};

#[derive(Copy, Clone)]
struct A(i32);

impl Add for A {
    type Output = A;
    fn add(self, rhs: A) -> A {
        A(self.0 + rhs.0)
    }
}

impl Sub for A {
    type Output = A;
    fn sub(self, rhs: A) -> A{
        A(self.0 - rhs.0)
    }
}

fn main() {
    let a1 = A(10i32);
    let a2 = A(5i32);
    let a3 = a1 + a2;
    println!("{}", (a3).0);
    let a4 = a1 - a2;
    println!("{}", (a4).0);
}
```

output:

```
15
5
```

# 格式化字符串

說起格式化字符串，Rust採取了一種類似Python裡面format的用法，其核心組成是五個宏和兩個trait:`format!`、`format_arg!`、`print!`、`println!`、`write!`;`Debug`、`Display`。

相信你們在寫Rust版本的Hello World的時候用到了`print!`或者`println!`這兩個宏，但是其實最核心的是`format!`，前兩個宏只不過將`format!`的結果輸出到了console而已。

那麼，我們來探究一下`format!`這個神奇的宏吧。

在這裡呢，列舉`format!`的定義是沒卵用的，因為太複雜。我只為大家介紹幾種典型用法。學會了基本上就能覆蓋你平時80%的需求。

首先我們來分析一下format的一個典型調用

```rust
fn main() {
    let s = format!("{1}是個有著{0:>0width$}KG重，{height:?}cm高的大胖子",
                    81, "wayslog", width=4, height=178);
    // 我被逼的犧牲了自己了……
    print!("{}", s);
}
```

我們可以看到，`format!`宏調用的時候參數可以是任意類型，而且是可以position參數和key-value參數混合使用的。但是要注意的一點是，key-value的值只能出現在position值之後並且不佔position。例如例子裡你用`3$`引用到的絕對不是`width`，而是會報錯。
這裡面關於參數稍微有一個規則就是，參數類型必須要實現 `std::fmt` mod 下的某些trait。比如我們看到原生類型大部分都實現了`Display`和`Debug`這兩個宏，其中整數類型還會額外實現一個`Binary`，等等。

當然了，我們可以通過 `{:type}`的方式去調用這些參數。

比如這樣：

```rust
format!("{:b}", 2);
// 調用 `Binary` trait
// Get : 10
format!("{:?}", "Hello");
// 調用 `Debug`
// Get : "Hello"
```

另外請記住：type這個地方為空的話默認調用的是`Display`這個trait。

關於`:`號後面的東西其實還有更多式子，我們從上面的`{0:>0width$}`來分析它。

首先`>`是一個語義，它表示的是生成的字符串向右對齊，於是我們得到了 `0081`這個值。與之相對的還有`<`(向左對齊)和`^`(居中)。

再接下來`0`是一種特殊的填充語法，他表示用0補齊數字的空位，要注意的是，當0作用於負數的時候，比如上面例子中wayslog的體重是-81，那麼你最終將得到`-0081`;當然了，什麼都不寫表示用空格填充啦;在這一位上，還會出現`+`、`#`的語法，使用比較詭異，一般情況下用不上。

最後是一個組合式子`width$`，這裡呢，大家很快就能認出來是表示後面key-value值對中的`width=4`。你們沒猜錯，這個值表示格式化完成後字符串的長度。它可以是一個精確的長度數值，也可以是一個以`$`為結尾的字符串，`$`前面的部分可以寫一個key或者一個postion。

最後，你需要額外記住的是，在width和type之間會有一個叫精度的區域（可以省略不寫如例子），他們的表示通常是以`.`開始的，比如`.4`表示小數點後四位精度。最讓人遭心的是，你仍然可以在這個位置引用參數，只需要和上面width一樣，用`.N$`來表示一個position的參數，但是就是不能引用key-value類型的。這一位有一個特殊用法，那就是`.*`，它不表示一個值，而是表示兩個值！第一個值表示精確的位數，第二個值表示這個值本身。這是一種很尷尬的用法，而且極度容易匹配到其他參數。因此，我建議在各位能力或者時間不欠缺的時候儘量把格式化表達式用標準的形式寫的清楚明白。尤其在面對一個複雜的格式化字符串的時候。

好了好了，說了這麼多，估計你也頭昏腦漲的了吧，下面來跟我寫一下format宏的完整用法。仔細體會並提煉每一個詞的意思和位置。

```
format_string := <text> [ format <text> ] *
format := '{' [ argument ] [ ':' format_spec ] '}'
argument := integer | identifier

format_spec := [[fill]align][sign]['#'][0][width]['.' precision][type]
fill := character
align := '<' | '^' | '>'
sign := '+' | '-'
width := count
precision := count | '*'
type := identifier | ''
count := parameter | integer
parameter := integer '$'
```

最後，留個作業吧。
給出參數列表如下：
`(500.0, 12, "ELTON", "QB", 4, CaiNiao="Mike")`

請寫出能最後輸出一下句子並且將參數*都*被用過*至少一遍*的格式化字符串，並自己去play實驗一下。

```
rust.cc社區的唐Mike眼睛度數足有0500.0度卻還是每天辛苦碼代碼才能賺到100個QB。
但是ELTON卻只需睡  12  個小時就可以迎娶白富美了。
```
