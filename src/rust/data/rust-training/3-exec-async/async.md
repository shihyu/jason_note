## async的簡單使用
加futures依賴到 Cargo.toml 文件：

```toml
[dependencies]
futures = "0.3"
```

async fn函數返回實現了Future的類型。需要使用執行器（executor）執行這個Future

```
use futures::executor::block_on;

async fn async_func1() {
    println!("async_func1!");
}

async fn async_func2() {
    println!("async_func2!");
}

fn main() {
    let future1 = async_func1(); 
    let future2 = async_func2(); 
    block_on(future1); 
    block_on(future2); 
}
```
使用block_on執行器執行futures。

## async塊
async有兩種使用方式，async fn 和 async 塊。兩種方法都返回一個實現了 Future trait 的值。

下面是一個包含async塊的例子：

```shell
use futures::executor::block_on;
use futures::Future;

async fn foo() -> u8 { 6 }

fn bar() -> impl Future<Output = u8> {
    // This `async` block results in a type that implements
    // `Future<Output = u8>`.
    async {
        let x: u8 = foo().await;
        println!("bar {}", x);
        x + 5
    }
}

fn main() {
    let future = bar();
    block_on(future);    
}
```

## async fn 參數生命週期
async fn 會獲取引用，所以參數的生命週期必須比async fn函數更長。

如下是 async fn 展開的例子

```
// This function:
async fn foo(x: &u8) -> u8 { *x }

// Is equivalent to this function:
fn foo_expanded<'a>(x: &'a u8) -> impl Future<Output = u8> + 'a {
    async move { *x }
}
```

aysync fn 返回了一個 Future。在調用.await()之前，其參數的生命週期必須要存在。

一個常用的解決此問題的辦法是，把這些參數 和對 async fn 的函數調用封裝到async 塊中：

```shell
use futures::executor::block_on;
use futures::Future;

async fn foo(x: &u8) -> u8 { *x+10 }

fn bar() -> impl Future<Output = u8> {
    async {
        let x: u8 = 5;
        let y: u8 = foo(&x).await;
        println!("bar {}", y);
        y
    }
}

fn main() {
    let future = bar();
    block_on(future);    
}
```
通過移動參數到 async 塊中，我們把它的生命週期擴展到了匹配調用 foo 函數返回的 Future 的生命週期。

## async與move
async塊可以使用move關鍵字。

下面的例子中。如果不使用move， future_one、future_two都可以訪問 my_string。
```shell
use futures::executor::block_on;
use futures::Future;

async fn blocks() {
    let my_string = "foo".to_string();

    let future_one = async {
        println!("{my_string}");
    };

    let future_two = async {
        println!("{my_string}");
    };

    let ((), ()) = futures::join!(future_one, future_two);
}

fn main() {
    let future = blocks();
    block_on(future);    
}
```

但假設 future_one 使用了 move 的話，future_two就不可以再訪問了。

```shell

async fn blocks() {
    let my_string = "foo".to_string();

    let future_one = async move{
        println!("{my_string}");
    };
    ......
}
```



