//结构体定义前加上pub, 结构体公有，但字段仍是私有的
//枚举定义前加上pub，它和它所有成员都将变为公有
#[allow(dead_code)]
mod market {
    #[derive(Debug)]
    pub enum FruitOrigin {
        China,
        Thailand,
        Vietnam,
    }

    pub struct Fruit {
        pub fruit_type: String,
        fruit_price: u32,
    }
    impl Fruit {
        pub fn order_fruit(fruit: &str) -> Fruit {
            Fruit {
                fruit_type: String::from(fruit),
                fruit_price: 10,
            }
        }
    }
}
pub fn eat_fruit() {
    let fruit1_origin = market::FruitOrigin::China;
    let fruit2_origin = market::FruitOrigin::Thailand;
    let fruit3_origin = market::FruitOrigin::Vietnam;
    println!("fruit1 is from {:?}", fruit1_origin);
    println!("fruit2 is from {:?}", fruit2_origin);
    println!("fruit3 is from {:?}", fruit3_origin);



    let mut f = market::Fruit::order_fruit("apple");
    f.fruit_type = String::from("pear");
    println!("I eat={}", f.fruit_type);

    //Fruit结构体fruit_type默认是私有的,无法访问
    f.fruit_price = 20;
    println!("price={}", f.fruit_price);
}








