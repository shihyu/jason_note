use rand::Rng;

fn plus_one(x: i32) -> i32 {
    x + 1
//    x + 1;
}

fn main() {
    //生成1-10的随机整数
    let x = rand::thread_rng().gen_range(1..11);
    println!("x = {}", x);
    println!("after calling plus_one() = {}", plus_one(x));

    if x > 5 {
        println!("x > 5");
    } else if x == 5 {
        println!("x == 5");
    } else {
        println!("x < 5, call loop_fn()");
        loop_fn(x);
    }
}

fn loop_fn(n : i32) {
    let mut num = n;

    loop {
        if num < 1 {
            break;
        }
        println!("in loop, num = {}", num);
        num -= 1;
    }

    while num < 5 {
        println!("in while, num = {}",num);
        num += 1;
    }

    let array = [10, 20, 30, 40, 50];
    for a in array {
        println!("a={}",a);
    }

    for number in 1..4 {
        println!("{}", number);
    }
}

