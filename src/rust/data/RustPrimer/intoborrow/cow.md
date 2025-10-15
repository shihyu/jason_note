# Cow

直譯為奶牛！開玩笑。
`Cow` 是一個枚舉類型，通過 `use std::borrow::Cow;` 引入。它的定義是 `Clone-on-write`，即寫時克隆。本質上是一個智能指針。

它有兩個可選值：
- `Borrowed`，用於包裹對象的引用（通用引用）；
- `Owned`，用於包裹對象的所有者；

`Cow` 提供

1. 對此對象的不可變訪問（比如可直接調用此對象原有的不可變方法）；
2. 如果遇到需要修改此對象，或者需要獲得此對象的所有權的情況，`Cow` 提供方法做克隆處理，並避免多次重複克隆。

`Cow` 的設計目的是提高性能（減少複製）同時增加靈活性，因為大部分情況下，業務場景都是讀多寫少。利用 `Cow`，可以用統一，規範的形式實現，需要寫的時候才做一次對象複製。這樣就可能會大大減少複製的次數。

它有以下幾個要點需要掌握：

1. `Cow<T>` 能直接調用 `T` 的不可變方法，因為 `Cow` 這個枚舉，實現了 `Deref`；
2. 在需要寫 `T` 的時候，可以使用 `.to_mut()` 方法得到一個具有所有權的值的可變借用；
    1. 注意，調用 `.to_mut()` 不一定會產生克隆；
    2. 在已經具有所有權的情況下，調用 `.to_mut()` 有效，但是不會產生新的克隆；
    3. 多次調用 `.to_mut()` 只會產生一次克隆。
3. 在需要寫 `T` 的時候，可以使用 `.into_owned()` 創建新的擁有所有權的對象，這個過程往往意味著內存拷貝並創建新對象；
    1. 如果之前 `Cow` 中的值是借用狀態，調用此操作將執行克隆；
    2. 本方法，參數是`self`類型，它會“吃掉”原先的那個對象，調用之後原先的對象的生命週期就截止了，在 `Cow` 上不能調用多次；


## 舉例

`.to_mut()` 舉例

```rust
use std::borrow::Cow;

let mut cow: Cow<[_]> = Cow::Owned(vec![1, 2, 3]);

let hello = cow.to_mut();

assert_eq!(hello, &[1, 2, 3]);
```

`.into_owned()` 舉例

```rust
use std::borrow::Cow;

let cow: Cow<[_]> = Cow::Owned(vec![1, 2, 3]);

let hello = cow.into_owned();

assert_eq!(vec![1, 2, 3], hello);
```

綜合舉例

```rust
use std::borrow::Cow;

fn abs_all(input: &mut Cow<[i32]>) {
    for i in 0..input.len() {
        let v = input[i];
        if v < 0 {
            // clones into a vector the first time (if not already owned)
            input.to_mut()[i] = -v;
        }
    }
}
```

## `Cow` 在函數返回值上的應用實例

題目：寫一個函數，過濾掉輸入的字符串中的所有空格字符，並返回過濾後的字符串。

對這個簡單的問題，不用思考，我們都可以很快寫出代碼：

```rust
fn remove_spaces(input: &str) -> String {
   let mut buf = String::with_capacity(input.len());

   for c in input.chars() {
      if c != ' ' {
         buf.push(c);
      }
   }

   buf
}
```

設計函數輸入參數的時候，我們會停頓一下，這裡，用 `&str` 好呢，還是 `String` 好呢？思考一番，從性能上考慮，有如下結論：

1. 如果使用 `String`， 則外部在調用此函數的時候，
    1. 如果外部的字符串是 `&str`，那麼，它需要做一次克隆，才能調用此函數；
    2. 如果外部的字符串是 `String`，那麼，它不需要做克隆，就可以調用此函數。但是，一旦調用後，外部那個字符串的所有權就被 `move` 到此函數中了，外部的後續代碼將無法再使用原字符串。
2. 如果使用 `&str`，則不存在上述兩個問題。但可能會遇到生命週期的問題，需要注意。

繼續分析上面的例子，我們發現，在函數體內，做了一次新字符串對象的生成和拷貝。

讓我們來仔細分析一下業務需求。最壞的情況下，如果字符串中沒有空白字符，那最好是直接原樣返回。這種情況做這樣一次對象的拷貝，完全就是浪費了。

於是我們心想改進這個算法。很快，又遇到了另一個問題，返回值是 `String` 的嘛，我不論怎樣，要把 `&str` 轉換成 `String` 返回，始終都要經歷一次複製。於是我們快要放棄了。

好吧，`Cow`君這時出馬了。奶牛君很快寫出瞭如下代碼：

```rust
use std::borrow::Cow;

fn remove_spaces<'a>(input: &'a str) -> Cow<'a, str> {
    if input.contains(' ') {
        let mut buf = String::with_capacity(input.len());

        for c in input.chars() {
            if c != ' ' {
                buf.push(c);
            }
        }

        return Cow::Owned(buf);
    }

    return Cow::Borrowed(input);
}

```

完美解決了業務邏輯與返回值類型衝突的問題。本例可細細品味。

外部程序，拿到這個 `Cow` 返回值後，按照我們上文描述的 `Cow` 的特性使用就好了。
