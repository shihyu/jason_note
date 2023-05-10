#[derive(Debug)]
#[allow(dead_code)]
enum Province {
    Zhejiang,
    Tianjin,
    Shandong,
}
#[allow(dead_code)]
enum Greetings {
    Qing,   //请
    Nin,    //您
    Nihao(Province),  //你好
}
fn get_greet(greet: Greetings) {
    match greet {
        Greetings::Qing => println!("Qing"),
        Greetings::Nin => println!("Nin"),
        Greetings::Nihao(p) => {
            println!("In {:?}, we say: Nihao",p)
        }
    }
}
fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i+1),
    }
}

fn main() {
    let greet = Greetings::Nihao(Province::Zhejiang);
    get_greet(greet);

    let num = Some(5);
    let ret = plus_one(num);
    println!("six = {}", ret.unwrap());

    let num = None;
    let ret = plus_one(num);
    println!("six = {:?}", ret);
}







