/*在vector 的结尾增加新元素时，在没有足够空间将所有所有元素依次相邻存放的情况下，
 * 可能会要求分配新内存并将老的元素拷贝到新的空间中。
 */
fn func1() {
    //let mut v = vec![1,2,3];
    let mut v = vec![1;1000000];
//    println!("v={:?}",v);
    println!("&v={:p}, vec@{:p}",&v, v.as_ptr());

    v.push(10);
//    println!("v={:?}",v);
    println!("&v={:p}, vec@{:p}",&v, v.as_ptr());
}

fn main() {
    func1();
}






