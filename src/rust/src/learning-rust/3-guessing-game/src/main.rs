use std::io;                                //用到的类型没有在prelude中，就要用use引入
use rand::Rng;                              //引入rand随机数crate。Cargo.toml加入dependency后，这里可以使用
use std::cmp::Ordering;                     //引入cmp比较库

fn main() {
    println!("Guess the number!");

    let secret_number = rand::thread_rng().gen_range(1..101); //生成1-100的随机整数。
    //println!("The random secret num is: {}", secret_number);

    loop {
        println!("Please input your guess.");

        let mut guess = String::new();          //let语句创建mutable可变变量，绑定一个空字符串;RUST变量默认是不可变的。
        //let guess = String::new();                //这样是错的！guess 无法用来保存用户输入的数字，编译出错

        io::stdin()                             //调用io的stdin函数创建一个Stdin实例。
            .read_line(&mut guess)              //调用io stdin的read_line函数读用户输入，添加到guess变量。&是引用。
            .expect("Failed to read line");     //readline出错时候打印，并且退出程序。不能假设执行成功，要有出错处理。

        let guess: u32 = guess.trim()           //把原来的guess字符串转换为u32数字
                              .parse()          //trim去掉头尾空格，parse字符串转换为数字
                              .expect("Please type a valid number!"); //出错时打印 
        /*
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };
        */

        println!("You guessed: {}", guess);     //打印读到的数字,{}是占位符

        match guess.cmp(&secret_number) {       //输入和随机数比较大小
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            }
        }
    }
}

