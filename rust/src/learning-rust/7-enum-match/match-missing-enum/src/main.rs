#[allow(dead_code)]
enum Province {
    Zhejiang,
    Tianjin,
    Shandong,
}
fn func1(prov: Province) -> i32 {
    match prov {
        Province::Zhejiang => 10,
        Province::Tianjin => 20,
        //如果enum某值没有被match用，编译出错
        Province::Shandong => 30,
    }
}

fn main() {
    println!("Provice num is: {}", func1(Province::Zhejiang));
}







