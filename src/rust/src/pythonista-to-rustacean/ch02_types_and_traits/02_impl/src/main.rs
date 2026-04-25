struct NightMarketOrder {
    food: String,
    quantity: u8,
    price: u32,
}

impl NightMarketOrder {
    // 這是一個「關聯函式」
    fn show_order(order: &NightMarketOrder) {
        println!(
            "{} x {} — 總計: {} 元",
            order.food, order.quantity, order.price
        );
    }

    // 這是一個「方法」
    fn show_order_method(&self) {
        println!(
            "{} x {} — 總計: {} 元",
            self.food, self.quantity, self.price
        );
    }

    // 這是一個不含 self 的關聯函式，當作建構子
    fn dessert(food: &str) -> Self {
        Self {
            food: String::from(food),
            quantity: 1,
            price: 30,
        }
    }

    fn new(food: String, quantity: u8) -> Self {
        Self {
            food,
            quantity,
            price: 90, // 假設有預設價格
        }
    }
}

fn main() {
    let my_order = NightMarketOrder {
        food: String::from("鹽酥雞"),
        quantity: 2,
        price: 120,
    };
    // 必須用 型別:: 函式名稱 來呼叫
    NightMarketOrder::show_order(&my_order);

    let my_order = NightMarketOrder {
        food: String::from("豆花"),
        quantity: 1,
        price: 30,
    };
    // 現在可以用 . 語法呼叫
    my_order.show_order_method();

    /// Constructor
    let tofu_pudding = NightMarketOrder::dessert("豆花");
    tofu_pudding.show_order_method();

    let chicken_cutlet = NightMarketOrder::new(String::from("雞排"), 3);
    println!(
        "{} 的預設價格是 {} 元",
        chicken_cutlet.food, chicken_cutlet.price
    );
}
