// Pass by value
fn update(mut arr:[i32;3]){
   for i in 0..3 {
      arr[i] = 0;
   }
   println!("Inside update {:?}",arr);
}

fn main() {
   let arr = [10,20,30];
   update(arr); // Pass by value

   print!("Inside main {:?}",arr);
}
