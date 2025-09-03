use rust_module_example::swimming::{CanSwim, CanDive, Aquatic};

struct Dolphin {
    name: String,
    max_speed: f32,
}

impl Dolphin {
    fn new(name: String, max_speed: f32) -> Self {
        Dolphin { name, max_speed }
    }
}

impl CanSwim for Dolphin {
    fn swim(&self) {
        println!("海豚 {} 以最高 {} km/h 的速度游泳！", self.name, self.max_speed);
    }
}

impl CanDive for Dolphin {
    fn dive(&self, depth: f32) {
        println!("海豚 {} 潛入 {} 公尺深的海中", self.name, depth);
    }
}

impl Aquatic for Dolphin {
    fn enter_water(&self) {
        println!("海豚 {} 跳入水中，濺起水花！", self.name);
    }
}

fn main() {
    println!("=== 進階功能展示 ===\n");
    
    let dolphin = Dolphin::new("小白".to_string(), 60.0);
    
    dolphin.enter_water();
    dolphin.swim();
    dolphin.dive(100.0);
    dolphin.exit_water();
}