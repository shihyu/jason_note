use stdext::function_name;
use std::collections::HashMap;

fn hashmap_create1() {
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 15);
    scores.insert(String::from("Yellow"), 20);
//    scores.insert(1, 20);    //编译出错，key类型要一样。这里key是i32类型，前面是String

    let newkey = String::from("Red");
    let newval = 18;
    scores.insert(newkey, newval);

    println!("{}: scores = {:?}", function_name!(), scores);
    println!("{}: get score for Blue team= {:?}",
        function_name!(), scores.get(&String::from("Blue")));
    println!("{}: get score for Test team= {:?}",
        function_name!(), scores.get(&String::from("Test")));
}
fn hashmap_create2() {
    let teams = vec![String::from("Blue"), String::from("Yellow")];
    let initial_scores = vec![15, 20];

    let scores: HashMap<_, _> =
        teams.into_iter().zip(initial_scores.into_iter()).collect();
    println!("{}: ", function_name!());
    for (k, v) in &scores {
        println!("key={}, val={}", k, v);
    }
}

fn main() {
    hashmap_create1();
    hashmap_create2();
}






