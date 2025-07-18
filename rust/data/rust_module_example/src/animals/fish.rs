use crate::swimming::CanSwim;

pub struct Fish {
    pub name: String,
    pub species: String,
}

impl Fish {
    pub fn new(name: String, species: String) -> Self {
        Fish { name, species }
    }
}

impl CanSwim for Fish {
    fn swim(&self) {
        println!("{}（{}）游泳中...", self.name, self.species);
    }
}