# C++ vs Rust

```cpp
#include <iostream>
using namespace std;

int main() {
    int a = 10;
    int *ptr1 = &a;
    int **ptr2 = &ptr1;

    const int size = 2;
    int arr[size];
    int *ptr;
    ptr = arr; // 將 ptr 指向陣列

    // 1. 記憶體位址
    for (int i = 0; i < size; i++) {
        std::cout << "&arr[" << i << "]: " << &arr[i] << ", ptr+" << i << ": " << (ptr + i) << std::endl;
    }

    // 2. 值的存取
    arr[0] = 0;
    *(ptr + 1) = 1;
    for (int i = 0; i < size; i++) {
        std::cout << "arr[" << i << "]: " << arr[i] << ", *(ptr+" << i << "): " << *(ptr + i) << std::endl;
    }

    return 0;
}
```

```rust
fn main() {
    let a = 10;
    let ptr1 = &a;
    let _ptr2 = &ptr1;

    const SIZE: usize = 2;
    let mut arr = [0; SIZE];
    let ptr: *mut i32; // 將 ptr 聲明為可變指標
    ptr = arr.as_mut_ptr(); // 將 ptr 指向陣列

    // 1. 記憶體位址
    for i in 0..SIZE {
        println!("&arr[{}]: {:p}, ptr+{}: {:p}", i, &arr[i], i, unsafe { ptr.add(i) });
    }

    // 2. 值的存取
    arr[0] = 0;
    unsafe {
        *(ptr.add(1)) = 1; // 使用 add() 方法計算指標的偏移量並修改值
    }
    for i in 0..SIZE {
        println!("arr[{}]: {}, *(ptr+{}): {}", i, arr[i], i, unsafe { *ptr.add(i) });
    }
}
```

