use std::rc::{Rc, Weak};
use std::cell::RefCell;

#[derive(Debug)]
struct Node {
    value: i32,
    children: Vec<Rc<RefCell<Node>>>,
    parent: Option<Rc<RefCell<Node>>>,
}

impl Node {
    fn new(value: i32) -> Rc<RefCell<Self>> {
        Rc::new(RefCell::new(Node {
            value,
            children: Vec::new(),
            parent: None,
        }))
    }
    
    fn add_child(parent: &Rc<RefCell<Node>>, child: &Rc<RefCell<Node>>) {
        // 借用父節點並添加子節點
        parent.borrow_mut().children.push(Rc::clone(child));
        
        // 設定子節點的父節點引用
        child.borrow_mut().parent = Some(Rc::clone(parent));
    }
    
    fn print_tree(node: &Rc<RefCell<Node>>, depth: usize) {
        let indent = "  ".repeat(depth);
        let borrowed = node.borrow();
        println!("{}Node: {}", indent, borrowed.value);
        
        for child in &borrowed.children {
            Node::print_tree(child, depth + 1);
        }
    }
    
    fn update_value(node: &Rc<RefCell<Node>>, new_value: i32) {
        node.borrow_mut().value = new_value;
    }
}

fn tree_example() {
    // 建立樹狀結構
    let root = Node::new(1);
    let child1 = Node::new(2);
    let child2 = Node::new(3);
    let grandchild = Node::new(4);
    
    // 建立父子關係
    Node::add_child(&root, &child1);
    Node::add_child(&root, &child2);
    Node::add_child(&child1, &grandchild);
    
    println!("原始樹狀結構:");
    Node::print_tree(&root, 0);
    
    // 修改節點值
    Node::update_value(&grandchild, 42);
    
    println!("\n修改後的樹狀結構:");
    Node::print_tree(&root, 0);
}

#[derive(Debug)]
struct GameState {
    score: i32,
    level: i32,
    lives: i32,
}

impl GameState {
    fn new() -> Self {
        GameState {
            score: 0,
            level: 1,
            lives: 3,
        }
    }
    
    fn add_score(&mut self, points: i32) {
        self.score += points;
        if self.score >= self.level * 1000 {
            self.level_up();
        }
    }
    
    fn level_up(&mut self) {
        self.level += 1;
        self.lives += 1;
        println!("升級！等級: {}, 生命: {}", self.level, self.lives);
    }
    
    fn lose_life(&mut self) {
        self.lives -= 1;
        println!("失去生命！剩餘: {}", self.lives);
    }
}

struct Player {
    name: String,
    game_state: Rc<RefCell<GameState>>,
}

impl Player {
    fn new(name: String, game_state: Rc<RefCell<GameState>>) -> Self {
        Player { name, game_state }
    }
    
    fn score_points(&self, points: i32) {
        println!("{} 獲得 {} 分", self.name, points);
        self.game_state.borrow_mut().add_score(points);
    }
    
    fn take_damage(&self) {
        println!("{} 受到傷害", self.name);
        self.game_state.borrow_mut().lose_life();
    }
    
    fn show_status(&self) {
        let state = self.game_state.borrow();
        println!("{} - 分數: {}, 等級: {}, 生命: {}", 
            self.name, state.score, state.level, state.lives);
    }
}

fn game_state_example() {
    let game_state = Rc::new(RefCell::new(GameState::new()));
    
    // 多個玩家共享遊戲狀態
    let player1 = Player::new("玩家1".to_string(), Rc::clone(&game_state));
    let player2 = Player::new("玩家2".to_string(), Rc::clone(&game_state));
    
    // 遊戲過程
    player1.score_points(500);
    player1.show_status();
    
    player2.score_points(300);
    player2.show_status();
    
    player1.score_points(700); // 應該升級
    player1.show_status();
    
    player2.take_damage();
    player2.show_status();
}

fn borrowing_safety_example() {
    let data = Rc::new(RefCell::new(vec![1, 2, 3]));
    
    // ✅ 正確的使用方式
    {
        let borrowed = data.borrow();
        println!("不可變借用: {:?}", *borrowed);
    } // borrowed 在這裡被釋放
    
    {
        let mut borrowed = data.borrow_mut();
        borrowed.push(4);
        println!("可變借用後: {:?}", *borrowed);
    } // borrowed 在這裡被釋放
    
    // ✅ 安全的檢查方式
    if let Ok(borrowed) = data.try_borrow() {
        println!("安全借用: {:?}", *borrowed);
    } else {
        println!("無法借用，已被其他人使用");
    };
    
    // ❌ 這會在運行時 panic！
    // let borrowed1 = data.borrow();
    // let borrowed2 = data.borrow_mut(); // panic: already borrowed
}

// 安全的借用包裝器
fn safe_borrow_pattern() {
    let data = Rc::new(RefCell::new(0));
    
    // 使用函數包裝器避免長時間借用
    fn with_data<F, R>(data: &Rc<RefCell<i32>>, f: F) -> Option<R>
    where
        F: FnOnce(&mut i32) -> R,
    {
        if let Ok(mut guard) = data.try_borrow_mut() {
            Some(f(&mut guard))
        } else {
            None
        }
    }
    
    if let Some(result) = with_data(&data, |value| {
        *value += 1;
        *value
    }) {
        println!("操作成功，新值: {}", result);
    } else {
        println!("操作失敗，資源被借用中");
    }
}

#[derive(Debug)]
struct Parent {
    children: RefCell<Vec<Rc<RefCell<Child>>>>,
}

#[derive(Debug)]
struct Child {
    parent: RefCell<Weak<RefCell<Parent>>>,
    _value: i32,
}

impl Parent {
    fn new() -> Rc<RefCell<Self>> {
        Rc::new(RefCell::new(Parent {
            children: RefCell::new(Vec::new()),
        }))
    }
    
    fn add_child(parent: &Rc<RefCell<Parent>>, value: i32) -> Rc<RefCell<Child>> {
        let child = Rc::new(RefCell::new(Child {
            parent: RefCell::new(Rc::downgrade(parent)),
            _value: value,
        }));
        
        parent.borrow().children.borrow_mut().push(Rc::clone(&child));
        child
    }
}

fn weak_reference_example() {
    let parent = Parent::new();
    let child1 = Parent::add_child(&parent, 1);
    let _child2 = Parent::add_child(&parent, 2);
    
    println!("父節點有 {} 個子節點", 
        parent.borrow().children.borrow().len());
    
    // 通過 weak 引用訪問父節點
    if let Some(_parent_ref) = child1.borrow().parent.borrow().upgrade() {
        println!("子節點可以訪問父節點");
    }
    
    // 當父節點被丟棄時，weak 引用會失效
    drop(parent);
    
    if child1.borrow().parent.borrow().upgrade().is_none() {
        println!("父節點已被丟棄，weak 引用失效");
    }
}

fn main() {
    println!("=== Tree Example ===");
    tree_example();
    
    println!("\n=== Game State Example ===");
    game_state_example();
    
    println!("\n=== Borrowing Safety Example ===");
    borrowing_safety_example();
    
    println!("\n=== Safe Borrow Pattern ===");
    safe_borrow_pattern();
    
    println!("\n=== Weak Reference Example ===");
    weak_reference_example();
}