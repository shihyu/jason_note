# rust數據庫操作

編程時，我們依賴數據庫來存儲相應的數據，很多編程語言都支持對數據庫的操作，所以當然可以使用Rust操作數據庫。

不過在我自己操作時，發現很多問題，主要因為我不瞭解Rust在操作數據庫時，應該注意的事情，從而浪費了很多的時間，在進行數據查詢時。
具體遇到的坑，我會做一些演示，從而讓大家避免這些情況。

首先使用Rust操作PostgreSQL,因為PostgreSQL是我最喜歡的數據庫。

首先創建新項目 `cargo new db --bin`

在cargo.toml中添加 `postgres` 如下：


``` rust
[package]
name = "db"
version = "0.1.0"
authors = ["vagrant"]

[dependencies]
postgres="*"
```


當然我們還是進行最簡單的操作，直接粘貼複製，[代碼來源](https://github.com/sfackler/rust-postgres#overview)

``` rust

extern crate postgres;

use postgres::{Connection, SslMode};

struct Person {
    id: i32,
    name: String,
    data: Option<Vec<u8>>
}

fn main() {
    let conn = Connection::connect("postgres://postgres@localhost", SslMode::None)
            .unwrap();

    conn.execute("CREATE TABLE person (
                    id              SERIAL PRIMARY KEY,
                    name            VARCHAR NOT NULL,
                    data            BYTEA
                  )", &[]).unwrap();
    let me = Person {
        id: 0,
        name: "Steven".to_string(),
        data: None
    };
    conn.execute("INSERT INTO person (name, data) VALUES ($1, $2)",
                 &[&me.name, &me.data]).unwrap();

    for row in &conn.query("SELECT id, name, data FROM person", &[]).unwrap() {
        let person = Person {
            id: row.get(0),
            name: row.get(1),
            data: row.get(2)
        };
        println!("Found person {}", person.name);
    }
}

```

這些簡單的，當然不是我們想要的東西，我們想要的是能夠進行一些分層，也就是
基本的一些函數邏輯劃分，而不是在一個main函數中，完成所有的一切。

##創建lib.rs文件

從上到下來看文件：

1. 首先導入postgres的各種庫
2. 創建一個Person 的struct，按照需求的字段和類型。
3. 創建一個連接函數，返回連接對象。
4. 創建一個插入函數，用來插入數據
5. 創建一個查詢函數，用來查詢數據
6. 創建一個查詢函數，用來查詢所有的數據。

當然這些函數都是有一定的功能侷限性。

``` rust

extern crate postgres;

use postgres::{Connection, SslMode};
use postgres::types::FromSql;
use postgres::Result as PgResult;


struct Person {
    id: i32,
    name: String,
    data: Option<Vec<u8>>
}


pub fn connect() -> Connection{
    let dsn = "postgresql://postgres:2015@localhost/rust_example";
    Connection::connect(dsn, SslMode::None).unwrap()
}

pub fn insert_info(conn : &Connection,title : &str, body: &str){

    let stmt = match conn.prepare("insert into blog (title, body) values ($1, $2)") {
        Ok(stmt) => stmt,
        Err(e) => {
            println!("Preparing query failed: {:?}", e);
            return;
        }
    };
        stmt.execute(&[&title, &body]).expect("Inserting blogposts failed");
}


pub fn query<T>(conn: &Connection,query: &str) ->PgResult<T>
        where T: FromSql {
            println!("Executing query: {}", query);
            let stmt = try!(conn.prepare(query));
            let rows = try!(stmt.query(&[]));
            &rows.iter().next().unwrap();
            let row = &rows.iter().next().unwrap();
                //rows.iter().next().unwrap()
            row.get_opt(2).unwrap()

}

pub fn query_all(conn: &Connection,query: &str){
            println!("Executing query: {}", query);
            for row in &conn.query(query,&[]).unwrap(){
                let person = Person{
                    id: row.get(0),
                    name: row.get(1),
                    data: row.get(2)
            };
            println!("Found person {}", person.name);
            }

}

```

然後在main.rs 中調用相應的函數代碼如下
1. extern db ,引入db，也就是將項目本身引入
2. use db 使用db，中的可以被引入的函數
3. 定義Blog,由於個人使用blog表，是自己創建，所以如果報錯說不存在表，需要你自己去創建
4. 使用lib中定義的函數，進行最基本的一些操作

``` rust
extern crate postgres;
extern crate db;

use postgres::{Connection, SslMode};

use db::*;

struct Blog {
    title: String,
    body:  String,
}

fn main() {
    let conn:Connection=connect();

    let blog = Blog{
        title: String::from("title"),
        body: String::from("body"),
    };
    let title = blog.title.to_string();
    let body = blog.body.to_string();
    insert_info(&conn,&title,&body);

   for row in query::<String>(&conn,"select * from blog"){
        println!("{:?}",row);
    }
    let sql = "select * from person";
    query_all(&conn,&sql);
}

```

自己遇到的坑

- 創建連接函數時，連接必須有一個返回值，所以必須指定返回值的類型，
對於一個寫Python的人而言，我覺得是痛苦的，我想按照官方的寫法match
一下，發現可能產生多個返回值。在編譯時直接無法通過編譯，所以最終
使用了unwrap,解決問題，不過我還是沒有學會，函數多值返回時我如何
定義返回值

- 在使用`&conn.query(query,&[]).unwrap()`時，我按照文檔操作，文檔說
返回的是一個可迭代的數據，那也就是說，我可以使用for循環，將數據打印，
但是發現怎麼也不能實現：

``` rust

pub fn query_all(conn: &Connection,query: &str){
            println!("Executing query: {}", query);
            for row in &conn.query(query,&[]).unwrap(){
                  println!("Found person {:?}", row.get_opt(1));
            }
}

```

報錯如下：

``` rust
vagrant@ubuntu-14:~/tmp/test/rustprimer/db$ cargo run
   Compiling db v0.1.0 (file:///home/vagrant/tmp/test/rustprimer/db)
src/lib.rs:53:37: 53:47 error: unable to infer enough type information about `_`; type annotations or generic parameter binding required [E0282]
src/lib.rs:53   println!("Found person {:?}", row.get_opt(1));
                                                  ^~~~~~~~~~
<std macros>:2:25: 2:56 note: in this expansion of format_args!
<std macros>:3:1: 3:54 note: in this expansion of print! (defined in <std macros>)
src/lib.rs:53:3: 53:49 note: in this expansion of println! (defined in <std macros>)
src/lib.rs:53:37: 53:47 help: run `rustc --explain E0282` to see a detailed explanation
error: aborting due to previous error
Could not compile `db`.

```

然後去查看了關於postgres模塊的所有函數，嘗試了無數種辦法，依舊沒有解決。

可能自己眼高手低，如果從頭再把Rust的相關教程看一下，可能很早就發現這個問題，
也有可能是因為習慣了寫Python，導致自己使用固有的思維來看待問題和鑽牛角尖，才
導致出現這樣的問題，浪費很多的時間。

- 改變思維，把自己當作一個全新的新手，既要利用已有的思想來學習新的語言，同樣不要
被自己很精通的語言，固化自己的思維。

