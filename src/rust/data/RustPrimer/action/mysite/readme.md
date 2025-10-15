# rust web 開發

rust既然是系統級的編程語言，所以當然也能用來開發 web,不過想我這樣凡夫俗子，肯定不能從頭自己寫一個 web
服務器，肯定要依賴已經存在的 rust web開發框架來完成 web 開發。

rust目前比較有名的框架是iron和nickel，我們兩個都寫一下簡單的使用教程。

##iron

接上一篇，使用cargo獲取第三方庫。`cargo new mysite --bin`

在cargo.toml中添加iron的依賴，

```toml
[dependencies]
iron = "*"
```

然後build將依賴下載到本地 `cargo build`

如果報ssl錯誤，那可能你需要安裝linux的ssl開發庫。

首先還是從 hello world 開始吧,繼續抄襲官方的例子：

``` rust
extern crate iron;

use iron::prelude::*;
use iron::status;

fn main() {
    Iron::new(|_: &mut Request| {
        Ok(Response::with((status::Ok, "Hello World!")))
    }).http("localhost:3000").unwrap();
}
```

然後運行

`cargo run`

使用curl直接就可以訪問你的網站了。

`curl localhost:3000`

`Hello World!`

仔細一看，發現這個例子很無厘頭啊，對於習慣了寫python的我來說，確實不習慣。
簡單點看：

`iron::new().http("localhost:3000").unwrap()`
這句是服務器的基本的定義，new內部是一個[rust lambda 表達式](https://doc.rust-lang.org/book/closures.html)

```rust
let plus_one = |x: i32| x + 1;

assert_eq!(2, plus_one(1));
```

具體的怎麼使用 ，可以暫時不用理會，因為你只要知道如何完成web，因為我也不會。。
結合之前一章節的json處理，我們來看看web接口怎麼返回json,當然也要 rustc_serialize 放到 cargo.toml 中

*下面的代碼直接參考開源代碼[地址](https://github.com/brson/httptest#lets-make-a-web-service-and-client-in-rust)*

```rust
extern crate iron;
extern crate rustc_serialize;

use iron::prelude::*;
use iron::status;
use rustc_serialize::json;

#[derive(RustcEncodable)]
struct Greeting {
    msg: String
}

fn main() {
    fn hello_world(_: &mut Request) -> IronResult<Response> {
        let greeting = Greeting { msg: "Hello, World".to_string() };
        let payload = json::encode(&greeting).unwrap();
        Ok(Response::with((status::Ok, payload)))
    }

    Iron::new(hello_world).http("localhost:3000").unwrap();
    println!("On 3000");
}
```

執行 cargo run 使用 curl 測試結果:

```
curl localhost:3000
{"msg":"Hello, World"}
```

當然可以可以實現更多的業務需求，通過控制自己的json。

既然有了json了，如果要多個路由什麼的，豈不是完蛋了，所以不可能這樣的，我們需要考慮一下怎麼實現路由的定製

不說話直接上代碼，同一樣要在你的cargo.toml文件中添加對router的依賴

``` rust
extern crate iron;
extern crate router;
extern crate rustc_serialize;

use iron::prelude::*;
use iron::status;
use router::Router;
use rustc_serialize::json;

#[derive(RustcEncodable, RustcDecodable)]
struct Greeting {
    msg: String
}

fn main() {
    let mut router = Router::new();

    router.get("/", hello_world);
    router.post("/set", set_greeting);

    fn hello_world(_: &mut Request) -> IronResult<Response> {
        let greeting = Greeting { msg: "Hello, World".to_string() };
        let payload = json::encode(&greeting).unwrap();
        Ok(Response::with((status::Ok, payload)))
    }

    // Receive a message by POST and play it back.
    fn set_greeting(request: &mut Request) -> IronResult<Response> {
        let payload = request.body.read_to_string();
        let request: Greeting = json::decode(payload).unwrap();
        let greeting = Greeting { msg: request.msg };
        let payload = json::encode(&greeting).unwrap();
        Ok(Response::with((status::Ok, payload)))
    }

    Iron::new(router).http("localhost:3000").unwrap();
}
```

這次添加了路由的實現和獲取客戶端發送過來的數據，有了get，post,所以現在一個基本的api網站已經完成了。不過
並不是所有的網站都是api來訪問，同樣需要html模版引擎和直接返回靜態頁面。等等

```
vagrant@ubuntu-14:~/tmp/test/rustprimer/mysite$ cargo build
   Compiling mysite v0.1.0 (file:///home/vagrant/tmp/test/rustprimer/mysite)
src/main.rs:29:36: 29:52 error: no method named `read_to_string` found for type `iron::request::Body<'_, '_>` in the current scope
src/main.rs:29         let payload = request.body.read_to_string();
                                                  ^~~~~~~~~~~~~~~~
src/main.rs:29:36: 29:52 help: items from traits can only be used if the trait is in scope; the following trait is implemented but not in scope, perhaps add a `use` for it:
src/main.rs:29:36: 29:52 help: candidate #1: use `std::io::Read`
error: aborting due to previous error
Could not compile `mysite`.
```

編譯出錯了，太糟糕了，提示說沒有read_to_string這個方法，然後我去文檔查了一下，發現有[read_to_string方法](http://ironframework.io/doc/iron/request/struct.Body.html)
再看提示信息

```
src/main.rs:29:36: 29:52 help: items from traits can only be used if the trait is in scope; the following trait is implemented but not in scope, perhaps add a `use` for it:
src/main.rs:29:36: 29:52 help: candidate #1: use `std::io::Read`
```

讓我們添加一個`std::io::Read`,這個如果操作過文件，你一定知道怎麼寫，添加一下，應該能過去了，還是繼續出錯了，看看報錯

```
   Compiling mysite v0.1.0 (file:///home/vagrant/tmp/test/rustprimer/mysite)
src/main.rs:30:36: 30:52 error: this function takes 1 parameter but 0 parameters were supplied [E0061]
src/main.rs:30         let payload = request.body.read_to_string();
                                                  ^~~~~~~~~~~~~~~~
src/main.rs:30:36: 30:52 help: run `rustc --explain E0061` to see a detailed explanation
src/main.rs:31:46: 31:53 error: mismatched types:
 expected `&str`,
    found `core::result::Result<usize, std::io::error::Error>`
(expected &-ptr,
    found enum `core::result::Result`) [E0308]
src/main.rs:31         let request: Greeting = json::decode(payload).unwrap();
                                                            ^~~~~~~
src/main.rs:31:46: 31:53 help: run `rustc --explain E0308` to see a detailed explanation
src/main.rs:30:36: 30:52 error: cannot infer an appropriate lifetime for lifetime parameter `'b` due to conflicting requirements [E0495]
src/main.rs:30         let payload = request.body.read_to_string();
                                                  ^~~~~~~~~~~~~~~~
src/main.rs:29:5: 35:6 help: consider using an explicit lifetime parameter as shown: fn set_greeting<'a>(request: &mut Request<'a, 'a>) -> IronResult<Response>
src/main.rs:29     fn set_greeting(request: &mut Request) -> IronResult<Response> {
src/main.rs:30         let payload = request.body.read_to_string();
src/main.rs:31         let request: Greeting = json::decode(payload).unwrap();
src/main.rs:32         let greeting = Greeting { msg: request.msg };
src/main.rs:33         let payload = json::encode(&greeting).unwrap();
src/main.rs:34         Ok(Response::with((status::Ok, payload)))
               ...
error: aborting due to 3 previous errors
Could not compile `mysite`.

```

第一句提示我們，這個read_to_string(),至少要有一個參數，但是我們一個都沒有提供。
我們看看[read_to_string的用法](https://doc.rust-lang.org/nightly/std/io/trait.Read.html#method.read_to_string)

``` rust

se std::io;
use std::io::prelude::*;
use std::fs::File;

let mut f = try!(File::open("foo.txt"));
let mut buffer = String::new();

try!(f.read_to_string(&mut buffer));

```

用法比較簡單，我們修改一下剛剛的函數：

```
fn set_greeting(request: &mut Request) -> IronResult<Response> {
        let mut payload = String::new();
        request.body.read_to_string(&mut payload);
        let request: Greeting = json::decode(&payload).unwrap();
        let greeting = Greeting { msg: request.msg };
        let payload = json::encode(&greeting).unwrap();
        Ok(Response::with((status::Ok, payload)))
    }
```

從request中讀取字符串，讀取的結果存放到payload中，然後就可以進行操作了，編譯之後運行，使用curl提交一個post數據

```
$curl -X POST -d '{"msg":"Just trust the Rust"}' http://localhost:3000/set
{"msg":"Just trust the Rust"}
```

iron 基本告一段落
當然還有如何使用html模版引擎，那就是直接看文檔就行了。

##[nickel](http://nickel.rs/)

當然既然是web框架肯定是iron能幹的nicke也能幹，所以那我們就看看如何做一個hello 和返回一個html
的頁面

同樣我們創建`cargo new site --bin`，然後添加nickel到cargo.toml中,`cargo build`

``` rust

#[macro_use] extern crate nickel;

use nickel::Nickel;

fn main() {
    let mut server = Nickel::new();

    server.utilize(router! {
        get "**" => |_req, _res| {
            "Hello world!"
        }
    });

    server.listen("127.0.0.1:6767");
}
```

簡單來看，也就是這樣回事。

1. 引入了nickel的宏
2. 初始化Nickel
3. 調用utilize來定義路由模塊。
4. `router!` 宏，傳入的參數是 get 方法和對應的路徑，"\*\*"是全路徑匹配。
5. listen啟動服務器

[當然我們要引入關於html模版相關的信息](http://nickel.rs/#easy-templating)

``` rust
#[macro_use] extern crate nickel;

use std::collections::HashMap;
use nickel::{Nickel, HttpRouter};

fn main() {
    let mut server = Nickel::new();

    server.get("/", middleware! { |_, response|
        let mut data = HashMap::new();
        data.insert("name", "user");
        return response.render("site/assets/template.tpl", &data);
    });

    server.listen("127.0.0.1:6767");
}

```

上面的信息你可以編譯，使用curl看看發現出現

```
$ curl http://127.0.0.1:6767
Internal Server Error
```

看看文檔，沒發現什麼問題，我緊緊更換了一個文件夾的名字，這個文件夾我也創建了。
然後我在想難道是服務器將目錄寫死了嗎？於是將上面的路徑改正這個，問題解決。

```rust
return response.render("examples/assets/template.tpl", &data);
```

我們看一下目錄結構

```
.
|-- Cargo.lock
|-- Cargo.toml
|-- examples
|   `-- assets
|       `-- template.tpl
|-- src
|   `-- main.rs

```
