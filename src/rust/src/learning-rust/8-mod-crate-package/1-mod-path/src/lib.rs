#[allow(dead_code)]
//默认函数、方法、结构体、枚举、模块和常量, 都是私有的
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
        fn seat_at_table() {}
    }
    mod serving {
        fn take_order() {}
        fn serve_order() {}
        fn take_payment() {}
    }
}
pub fn eat_at_rest() {
    //absolute path
    // 'crate' -> same crate as front_of_house
    // front_of_house not pub, but can be used, because
    // eat_at_rest & front_of_house are in same crate
    crate::front_of_house::hosting::add_to_waitlist();

    //relative path
    front_of_house::hosting::add_to_waitlist();
}

//////////////////////////////////////////////////////
//super -> ../ parent level mod
pub fn serve_order() {}
#[allow(dead_code)]
mod back_of_house {
    fn fix_incorrect_order() {
        cook_order();
        super::serve_order();
    }
    fn cook_order() {}
}







