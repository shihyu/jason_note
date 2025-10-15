# 高階函數
  高階函數與普通函數的不同在於，它可以使用一個或多個函數作為參數，可以將函數作為返回值。rust的函數是first class type，所以支持高階函數。而，由於rust是一個強類型的語言，如果要將函數作為參數或返回值，首先需要搞明白函數的類型。下面先說函數的類型，再說函數作為參數和返回值。

## 函數類型
  前面說過，關鍵字`fn`可以用來定義函數。除此以外，它還用來構造函數類型。與函數定義主要的不同是，構造函數類型不需要函數名、參數名和函數體。在Rust Reference中的描述如下：
  > The function type constructor fn forms new function types. A function type consists of a possibly-empty set of function-type modifiers (such as unsafe or extern), a sequence of input types and an output type.

  來看一個簡單例子：
  
  ```rust
fn inc(n: i32) -> i32 {//函數定義
  n + 1
}

type IncType = fn(i32) -> i32;//函數類型

fn main() {
  let func: IncType = inc;
  println!("3 + 1 = {}", func(3));
}
  ```
  
  上例首先使用`fn`定義了`inc`函數，它有一個`i32`類型參數，返回`i32`類型的值。然後再用`fn`定義了一個函數類型，這個函數類型有i32類型的參數和i32類型的返回值，並用`type`關鍵字定義了它的別名`IncType`。在`main`函數中定義了一個變量`func`，其類型就為`IncType`，並賦值為`inc`，然後在`pirntln`宏中調用：`func(3)`。可以看到，`inc`函數的類型其實就是`IncType`。
  這裡有一個問題，我們將`inc`賦值給了`func`，而不是`&inc`，這樣是將`inc`函數的擁有權轉給了`func`嗎，賦值後還可以以`inc()`形式調用`inc`函數嗎？先來看一個例子：
  
  ```rust
fn main() {
  let func: IncType = inc;
  println!("3 + 1 = {}", func(3));
  println!("3 + 1 = {}", inc(3));
}

type IncType = fn(i32) -> i32;

fn inc(n: i32) -> i32 {
  n + 1
}
  ```
  
  我們將上例保存在rs源文件中，再用rustc編譯，發現並沒有報錯，並且運行也得到我們想要的結果：
  
  ```
3 + 1 = 4
3 + 1 = 4
  ```
  
  這說明，賦值時，`inc`函數的所有權並沒有被轉移到`func`變量上，而是更像不可變引用。在rust中，函數的所有權是不能轉移的，我們給函數類型的變量賦值時，賦給的一般是函數的指針，所以rust中的函數類型，就像是C/C++中的函數指針，當然，rust的函數類型更安全。可見，rust的函數類型，其實應該是屬於指針類型（Pointer Type）。rust的Pointer Type有兩種，一種為引用（Reference`&`），另一種為原始指針（Raw pointer `*`），詳細內容請看[Rust Reference 8.18 Pointer Types](http://doc.rust-lang.org/reference.html#pointer-types)。而rust的函數類型應是引用類型，因為它是安全的，而原始指針則是不安全的，要使用原始指針，必須使用`unsafe`關鍵字聲明。

## 函數作為參數
  函數作為參數，其聲明與普通參數一樣。看下例：
  
  ```rust
fn main() {
  println!("3 + 1 = {}", process(3, inc));
  println!("3 - 1 = {}", process(3, dec));
}

fn inc(n: i32) -> i32 {
  n + 1
}

fn dec(n: i32) -> i32 {
  n - 1
}

fn process(n: i32, func: fn(i32) -> i32) -> i32 {
  func(n)
}
  ```
  
  例子中，`process`就是一個高階函數，它有兩個參數，一個類型為`i32`的`n`，另一個類型為`fn(i32)->i32`的函數`func`，返回一個`i32`類型的參數；它在函數體內以`n`作為參數調用`func`函數，返回`func`函數的返回值。運行可以得到以下結果：
  
  ```
3 + 1 = 4
3 - 1 = 2
  ```
  
  不過，這不是函數作為參數的唯一聲明方法，使用泛型函數配合特質（`trait`）也是可以的，因為rust的函數都會實現一個`trait`:`FnOnce`、`Fn`或`FnMut`。將上例中的`process`函數定義換成以下形式是等價的：
  
  ```rust
fn process<F>(n: i32, func: F) -> i32
    where F: Fn(i32) -> i32 {
    func(n)
}
  ```

## 函數作為返回值
  函數作為返回值，其聲明與普通函數的返回值類型聲明一樣。看例子：
  
  ```rust
fn main() {
   let a = [1,2,3,4,5,6,7];
   let mut b = Vec::<i32>::new();
   for i in &a {
       b.push(get_func(*i)(*i));
   }
   println!("{:?}", b);
}

fn get_func(n: i32) -> fn(i32) -> i32 {
    fn inc(n: i32) -> i32 {
        n + 1
    }
    fn dec(n: i32) -> i32 {
        n - 1
    }
    if n % 2 == 0 {
        inc
    } else {
        dec
    }
}
  ```
  
  例子中的高階函數為`get_func`，它接收一個i32類型的參數，返回一個類型為`fn(i32) -> i32`的函數，若傳入的參數為偶數，返回`inc`，否則返回`dec`。這裡需要注意的是，`inc`函數和`dec`函數都定義在`get_func`內。在函數內定義函數在很多其他語言中是不支持的，不過rust支持，這也是rust靈活和強大的一個體現。不過，在函數中定義的函數，不能包含函數中（環境中）的變量，若要包含，應該閉包（詳看13章 閉包）。
  所以下例：
  
  ```rust
fn main() {
  let f = get_func();
  println!("{}", f(3));
}

fn get_func() -> fn(i32)->i32 {
  let a = 1;
  fn inc(n:i32) -> i32 {
    n + a
  }
  inc
}
  ```
  
  使用rustc編譯，會出現如下錯誤：
  ![error](../images/high-order-function.png)
