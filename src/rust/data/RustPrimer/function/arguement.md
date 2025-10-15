# 函數參數
## 參數聲明
  rust的函數參數聲明和一般的變量聲明相仿，也是參數名後加冒號，冒號後跟參數類型，不過不需要`let`關鍵字。需要注意的是，普通變量聲明(let語句)是可以省略變量類型的，而函數參數的聲明則不能省略參數類型。
  來看一個簡單例子：
  
  ```rust
fn main() {
  say_hi("ruster");
}

fn say_hi(name: &str) {
  println!("Hi, {}", name);
}
  ```
  
  上例中，`say_hi`函數擁有一個參數，名為`name`，類型為`&str`。

## 將函數作為參數
  在rust中，函數是一等公民（可以儲存在變量/數據結構中，可以作為參數傳入函數，可以作為返回值），所以rust的函數參數不僅可以是一般的類型，也可以是函數。如：
  
  ```rust
fn main() {
  let xm = "xiaoming";
  let xh = "xiaohong";
  say_what(xm, hi);
  say_what(xh, hello);
}

fn hi(name: &str) {
  println!("Hi, {}.", name);
}

fn hello(name: &str) {
  println!("Hello, {}.", name);
}

fn say_what(name: &str, func: fn(&str)) {
  func(name)
}
  ```
  
  上例中，`hi`函數和`hello`函數都是隻有一個`&str`類型的參數且沒有返回值。而`say_what`函數則有兩個參數，一個是`&str`類型，另一個則是函數類型（function type），它是隻有一個`&str`類型參數且沒有返回值的函數類型。

## 模式匹配
  支持模式匹配，讓rust平添了許多的靈活性，用起來也是十分的舒爽。模式匹配不僅可以用在變量聲明（let語句）中，也可以用在函數參數聲明中，如：
  
  ```rust
fn main() {
  let xm = ("xiaoming", 54);
  let xh = ("xiaohong", 66);
  print_id(xm);
  print_id(xh);
  print_name(xm);
  print_age(xh);
  print_name(xm);
  print_age(xh);
}

fn print_id((name, age): (&str, i32)) {
  println!("I'm {},age {}.", name, age);
}

fn print_age((_, age): (&str, i32)) {
  println!("My age is  {}", age);
}

fn print_name((name,_): (&str, i32)) {
  println!("I am  {}", name);
}
  ```
  
  上例是一個元組(Tuple)匹配的例子，當然也可以是其他可在let語句中使用的類型。參數的模式匹配跟let語句的匹配一樣，也可以使用下劃線來表示丟棄一個值。
