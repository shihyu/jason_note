// lib.rs

#[no_mangle]
pub extern "C" fn is_prime(num: u64) -> bool {
    if num < 2 {
        return false;
    }
    for i in 2..=(num / 2) {
        if num % i == 0 {
            return false;
        }
    }
    true
}

#[no_mangle]
pub extern "C" fn calculate_sum(n: u64) -> u64 {
    (1..=n).sum()
}
