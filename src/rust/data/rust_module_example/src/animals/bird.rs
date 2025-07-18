use crate::swimming::CanSwim;

pub struct Bird {
    pub name: String,
    pub species: String,
    pub can_fly: bool,
}

impl Bird {
    pub fn new(name: String, species: String) -> Self {
        Bird { 
            name, 
            species,
            can_fly: false,
        }
    }
}

impl CanSwim for Bird {
    fn swim(&self) {
        if self.can_fly {
            println!("{}（{}）在水面划水游泳！", self.name, self.species);
        } else {
            println!("{}（{}）是不會飛的鳥類，用腳划水游泳！", self.name, self.species);
        }
    }
}