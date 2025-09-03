fn func1() {
    let mut v = vec![1;1000000];
    let first = &v[0];

    println!("first={}",first);
    println!("&v={:p}, vec@{:p}",&v, v.as_ptr());

    v.push(10);

//    println!("first={}",first);
    println!("&v={:p}, vec@{:p}",&v, v.as_ptr());
}

fn main() {
    func1();
}






