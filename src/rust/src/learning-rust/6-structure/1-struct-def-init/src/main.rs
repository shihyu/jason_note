#[allow(dead_code)]
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}
/*
fn struct_init1() {
    //实例化的时候，必须初始化所有成员，否则编译出错。
    let user1 = User {
        email: String::from("someone@example.com"),
        username: String::from("name123"),
    };
    println!("email={}", user1.email);
}
fn struct_init2() {
    let mut user1 = User {
        email: String::from("someone@example.com"),
        username: String::from("name123"),
        active: true,
        sign_in_count: 1,
    };
    user1.email = String::from("newemail@example.com");
    //有些成员没有被用到，编译出warning。
    println!("email={}", user1.email);
}
*/
fn build_user(email: String, username: String) -> User {
    User {
        email: email,
        username: username,
        active: true,
        sign_in_count: 1,
    }
}
#[allow(dead_code)]
fn build_user2(email: String, username: String) -> User {
    User {
        email,
        username,
        active: true,
        sign_in_count: 1,
    }
}
fn struct_init3() {
    let user1 = build_user(
            String::from("user1@example.com"),
            String::from("user1")
        );
    println!("user1 email={}", user1.email);
    println!("user1 username={}", user1.username);
    println!("user1 active={}", user1.active);
    println!("user1 sign_in_count={}", user1.sign_in_count);
    let user2 = User {
        email: String::from("user2@example.com"),
        ..user1
    };
    println!("user2 email={}", user2.email);
    println!("user2 username={}", user2.username);
    println!("user2 active={}", user2.active);
    println!("user2 sign_in_count={}", user2.sign_in_count);
}

fn main() {
    struct_init3();
}

