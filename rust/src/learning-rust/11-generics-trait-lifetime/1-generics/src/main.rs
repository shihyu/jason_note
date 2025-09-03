#[allow(dead_code)]
fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>())
}
fn largest_i32(list: &[i32]) -> i32 {
    let mut largest = list[0];
    for &item in list {
        //print_type_of(&item);
        //print_type_of(&largest);
        if item > largest {
            largest = item;
        }
    }
    largest
}
#[allow(dead_code)]
#[derive(Debug)]
struct Point<T, U> {
    x:T,
    y:U,
}

impl<T, U> Point<T, U> {
    fn x(&self) -> &T {
        &self.x
    }
}


fn main() {
    let arr = vec![1,3,0,200,7];
    println!("larggest={}", largest_i32(&arr));

    let integer_n_float = Point{x:5, y:1.2};
    println!("Point={:?}", integer_n_float);
    println!("Point.x={}", integer_n_float.x());

}
