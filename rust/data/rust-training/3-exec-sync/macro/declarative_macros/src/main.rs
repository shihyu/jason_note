use std::vec::Vec;
use std::fs::File;
use std::io::{self, Read};

macro_rules! mymacro {
    () => {
        println!("{}","Hello World!")
    };
}

macro_rules! my_vec {
    // 匹配空输入，创建一个新的 vector
    () => {
        std::vec::Vec::new()
    };

    // 匹配类似于 vec![0; 10] 的输入
    ( $elem: expr ; $n: expr ) => {
        std::vec::from_elem($elem, $n)
    };

    // 匹配类似于 vec![1, 2, 3] 的输入
    ( $( $elem: expr ),* ) => {
        // 由于我们将生成多条语句，因此必须再用 {} 包起来
        {
            let mut v = std::vec::Vec::new();
            $( v.push($elem); )*
            v
        }
    };

    // 匹配类似于 vec![1, 2, 3, ] 的输入
    ( $( $elem: expr, )* ) => {
        // 递归调用
        my_vec![ $( $elem ),* ]
    };
}

fn myTest1() -> Result<(), Box<dyn std::error::Error>>{
    let mut f = {
        match File::open("hello.txt") {
            Ok(file) => file,
            Err(err) => return Err(From::from(err)),
        };
    };
    Ok(())
}

macro_rules! my_try {
    ($result:expr) => {
        match $result {
            Ok(v) => v,
            Err(e) => {
                return std::result::Result::Err(std::convert::From::from(e));
            }
        }
    };
}

fn myTest2() -> Result<(), Box<dyn std::error::Error>>{
    let mut f1 = my_try!(File::open("hello.txt"));
    let mut f2 = File::open("hello.txt")?;
    Ok(())
}


fn main() {
    mymacro!();
    mymacro!{};
    mymacro![];

    let v1 = my_vec![1, 2, 3];
    let v2 = my_vec![0; 10];
    println!("{:?}", v1);
    println!("{:?}", v2);

    myTest1();
    myTest2();
}


