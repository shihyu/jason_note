#[allow(dead_code)]
//if let以一种不冗长的方式，来处理只匹配一个模式的值而忽略其他模式的情况。
fn func1() 
{
    let num = Some(3);
    /*
    match num {
        Some(n) => println!("the num is {}",n),
        _ => ()
    }
    */
    if let Some(n) = num {
        println!("the num is {}",n);
    }
}

#[derive(Debug)]
#[allow(dead_code)]
enum Month {
    Jan,
    Feb,
    Mar,
    Apr,
}
fn func2() 
{
    //let m = Month::Jan;
    let m = Month::Mar;
    /*
    match m {
        Month::Jan => println!("{:?} is the special month", m),
        _ => println!("other month")
    }
    */
    if let Month::Jan = m {
        println!("{:?} is the special month", m);
    } else {
        println!("other month");
    }
}

fn main() {
    func1();
    func2();
}









