struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}
fn struct_init() {
    let user1 = User {
        email: String::from("user1@example.com"),
        username: String::from("user1"),
        active: true,
        sign_in_count: 1
    };
    println!("user1 email={}", user1.email);
    println!("user1 username={}", user1.username);
    println!("user1 active={}", user1.active);
    println!("user1 sign_in_count={}", user1.sign_in_count);
    let user2 = User {
        email: String::from("user2@example.com"),
//        username: String::from("user2"),
        ..user1
    };
    println!("user2 email={}", user2.email);
    println!("user2 username={}", user2.username);
    println!("user2 active={}", user2.active);
    println!("user2 sign_in_count={}", user2.sign_in_count);

    //user2.email创建了新字符串，user2有所有权
    //active: bool, sign_in_count: u64 带有copy trait，所有权不会移动到user2
    //user1.username所有权移动到了user2
    println!("user1 email={}", user1.email);
    println!("user1 username={}", user1.username);
    println!("user1 active={}", user1.active);
    println!("user1 sign_in_count={}", user1.sign_in_count);
}

fn main() {
    struct_init();
}

