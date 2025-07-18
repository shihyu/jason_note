pub trait CanSwim {
    fn swim(&self);
}

pub trait CanDive {
    fn dive(&self, depth: f32);
}

pub trait Aquatic {
    fn enter_water(&self) {
        println!("進入水中...");
    }
    
    fn exit_water(&self) {
        println!("離開水中...");
    }
}

#[cfg(feature = "advanced")]
pub mod advanced_swimming {
    pub trait AdvancedSwimming {
        fn underwater_breathing(&self);
        fn deep_dive(&self, depth: f32);
    }
}

#[cfg(feature = "advanced")]
pub use advanced_swimming::AdvancedSwimming;