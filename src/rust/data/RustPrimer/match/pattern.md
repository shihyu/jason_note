# 模式
模式，是Rust另一個強大的特性。它可以被用在`let`和`match`表達式裡面。相信大家應該還記得我們在[複合類型](../type/compound-types.md)中提到的關於在let表達式中解構元組的例子，實際上這就是一個模式。

```rust
let tup = (0u8, 1u8);
let (x, y) = tup;
```

而且我們需要知道的是，如果一個模式中出現了和當前作用域中已存在的同名的綁定，那麼它會覆蓋掉外部的綁定。比如：

```rust
let x = 1;
let c = 'c';

match c {
    x => println!("x: {} c: {}", x, c),
}

println!("x: {}", x);
```

它的輸出結果是:

```
x: c c: c
x: 1
```

在以上代碼中，match作用域裡的`x`這個綁定被覆蓋成了`'c'`，而出了這個作用域，綁定`x`又恢復為`1`。這和變量綁定的行為是一致的。

## 更強大的解構

在上一節裡，我們初步瞭解了模式匹配在解構`enum`時候的便利性，事實上，在Rust中模式可以被用來對任何複合類型進行解構——struct/tuple/enum。現在我們要講述一個複雜點的例子，對`struct`進行解構。

首先，我們可以對一個結構體進行標準的解構：

```rust
struct Point {
    x: i64,
    y: i64,
}
let point = Point { x: 0, y: 0 };
match point {
    Point { x, y } => println!("({},{})", x, y),
}
```

最終，我們拿到了`Point`內部的值。有人說了，那我想改個名字怎麼辦？
很簡單，你可以使用 `:`來對一個struct的字段進行重命名，如下:

```rust
struct Point {
    x: i64,
    y: i64,
}
let point = Point { x: 0, y: 0 };
match point {
    Point { x: x1, y: y1} => println!("({},{})", x1, y1),
}
```

另外，有的時候我們其實只對某些字段感興趣，就可以用`..`來省略其他字段。

```rust
struct Point {
    x: i64,
    y: i64,
}

let point = Point { x: 0, y: 0 };

match point {
    Point { y, .. } => println!("y is {}", y),
}
```

## 忽略和內存管理

總結一下，我們遇到了兩種不同的模式忽略的情況——`_`和`..`。這裡要注意，模式匹配中被忽略的字段是不會被`move`的，而且實現`Copy`的也會優先被Copy而不是被`move`。

說的有點拗口，上代碼：

```rust
let tuple: (u32, String) = (5, String::from("five"));

let (x, s) = tuple;

// 以下行將導致編譯錯誤，因為String類型並未實現Copy, 所以tuple被整體move掉了。
// println!("Tuple is: {:?}", tuple);

let tuple = (5, String::from("five"));

// 忽略String類型，而u32實現了Copy，則tuple不會被move
let (x, _) = tuple;

println!("Tuple is: {:?}", tuple);
```

## 範圍和多重匹配

模式匹配可以被用來匹配單種可能，當然也就能被用來匹配多種情況：

### 範圍

在模式匹配中，當我想要匹配一個數字(字符)範圍的時候，我們可以用`...`來表示：

```rust
let x = 1;

match x {
    1 ... 10 => println!("一到十"),
    _ => println!("其它"),
}

let c = 'w';

match c {
    'a' ... 'z' => println!("小寫字母"),
    'A' ... 'Z' => println!("大寫字母"),
    _ => println!("其他字符"),
}
```

### 多重匹配

當我們只是單純的想要匹配多種情況的時候，可以使用 `|` 來分隔多個匹配條件

```rust
let x = 1;

match x {
    1 | 2 => println!("一或二"),
    _ => println!("其他"),
}
```

## ref 和 ref mut

前面我們瞭解到，當被模式匹配命中的時候，未實現`Copy`的類型會被默認的move掉，因此，原owner就不再持有其所有權。但是有些時候，我們只想要從中拿到一個變量的（可變）引用，而不想將其move出作用域，怎麼做呢？答：用`ref`或者`ref mut`。

```rust
let mut x = 5;

match x {
    ref mut mr => println!("mut ref :{}", mr),
}
// 當然了……在let表達式裡也能用
let ref mut mrx = x;
```


## 變量綁定

在模式匹配的過程內部，我們可以用`@`來綁定一個變量名，這在複雜的模式匹配中是再方便不過的，比如一個具名的範圍匹配如下：

```rust
let x = 1u32;
match x {
    e @ 1 ... 5 | e @ 10 ... 15 => println!("get:{}", e),
    _ => (),
}
```

如代碼所示，e綁定了x的值。

當然，變量綁定是一個極其有用的語法，下面是一個來自官方doc裡的例子：

```rust
#[derive(Debug)]
struct Person {
    name: Option<String>,
}

let name = "Steve".to_string();
let x: Option<Person> = Some(Person { name: Some(name) });
match x {
    Some(Person { name: ref a @ Some(_), .. }) => println!("{:?}", a),
    _ => {}
}
```

輸出：

```
Some("Steve")
```

## 後置條件

一個後置的if表達式可以被放在match的模式之後，被稱為`match guards`。例如如下代碼：

```rust
let x = 4;
let y = false;

match x {
    4 | 5 if y => println!("yes"),
    _ => println!("no"),
}
```

猜一下上面代碼的輸出？

答案是`no`。因為guard是後置條件，是整個匹配的後置條件：所以上面的式子表達的邏輯實際上是：

```
// 偽代碼表示
IF y AND (x IN List[4, 5])
```
