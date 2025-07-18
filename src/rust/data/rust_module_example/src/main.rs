mod animals;
mod swimming;

use animals::{SubFish, SubBird};
use swimming::CanSwim;

#[cfg(debug_assertions)]
fn debug_info() {
    println!("這是 debug 模式 - 啟用額外檢查");
}

#[cfg(not(debug_assertions))]
fn debug_info() {
    // release 模式下什麼都不做
}

#[cfg(target_os = "windows")]
fn platform_specific() {
    println!("Windows 平台");
}

#[cfg(target_os = "linux")]
fn platform_specific() {
    println!("Linux 平台");
}

#[cfg(target_os = "macos")]
fn platform_specific() {
    println!("macOS 平台");
}

fn main() {
    println!("=== Rust 模組系統範例 ===\n");
    
    debug_info();
    platform_specific();
    println!();
    
    let fish = SubFish::new("小丑魚".to_string(), "小丑魚".to_string());
    let bird = SubBird::new("企鵝".to_string(), "國王企鵝".to_string());
    
    println!("魚類游泳：");
    fish.swim();
    
    println!("\n鳥類游泳：");
    bird.swim();
    
    println!("\n=== 程式執行完成 ===");
}