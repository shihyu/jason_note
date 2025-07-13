我來提供 Go 和 Rust 的簡單程式範例，讓你測試 GDB 調試功能：## 編譯和調試指令

### Go 測試：


```go
package main

import (
	"fmt"
	"time"
)

func add(a, b int) int {
	result := a + b
	fmt.Printf("Adding %d + %d = %d\n", a, b, result)
	return result
}

func factorial(n int) int {
	if n <= 1 {
		return 1
	}
	return n * factorial(n-1)
}

func main() {
	fmt.Println("=== Go GDB Debug Test ===")
	
	// 簡單變數
	x := 10
	y := 20
	
	// 函數呼叫
	sum := add(x, y)
	
	// 遞迴函數
	fact := factorial(5)
	
	// 陣列操作
	numbers := []int{1, 2, 3, 4, 5}
	total := 0
	for i, num := range numbers {
		total += num
		fmt.Printf("Index %d: %d, Running total: %d\n", i, num, total)
	}
	
	// 結構體
	type Person struct {
		Name string
		Age  int
	}
	
	person := Person{Name: "Alice", Age: 30}
	fmt.Printf("Person: %+v\n", person)
	
	// 故意的延遲，方便設置斷點
	time.Sleep(100 * time.Millisecond)
	
	fmt.Printf("Final results: sum=%d, factorial=%d, total=%d\n", sum, fact, total)
}
```

```bash
# 編譯 (關閉優化)
go build -gcflags="-N -l" -o go_debug main.go

# 使用 GDB
gdb ./go_debug

# GDB 指令範例：
(gdb) break main.main
(gdb) run
(gdb) next
(gdb) print x
(gdb) print sum
(gdb) continue
```

### Rust 測試：

```bash
# 建立 Cargo 專案
cargo new rust_debug_test
cd rust_debug_test

# 將程式碼放到 src/main.rs，然後編譯



```rust
fn add(a: i32, b: i32) -> i32 {
    let result = a + b;
    println!("Adding {} + {} = {}", a, b, result);
    result
}

fn factorial(n: i32) -> i32 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

#[derive(Debug)]
struct Person {
    name: String,
    age: u32,
}

fn main() {
    println!("=== Rust GDB Debug Test ===");
    
    // 簡單變數
    let x = 10;
    let y = 20;
    
    // 函數呼叫
    let sum = add(x, y);
    
    // 遞迴函數
    let fact = factorial(5);
    
    // 向量操作
    let numbers = vec![1, 2, 3, 4, 5];
    let mut total = 0;
    
    for (i, num) in numbers.iter().enumerate() {
        total += num;
        println!("Index {}: {}, Running total: {}", i, num, total);
    }
    
    // 結構體
    let person = Person {
        name: String::from("Alice"),
        age: 30,
    };
    println!("Person: {:?}", person);
    
    // 選項類型
    let maybe_number: Option<i32> = Some(42);
    match maybe_number {
        Some(n) => println!("Found number: {}", n),
        None => println!("No number found"),
    }
    
    // 故意的延遲，方便設置斷點
    std::thread::sleep(std::time::Duration::from_millis(100));
    
    println!("Final results: sum={}, factorial={}, total={}", sum, fact, total);
}
```

cargo build

# 使用 rust-gdb (推薦)
rust-gdb ./target/debug/rust_debug_test

# 或使用一般 GDB
gdb ./target/debug/rust_debug_test

# GDB 指令範例：
(gdb) break main
(gdb) run
(gdb) next
(gdb) print x
(gdb) print sum
(gdb) info locals
(gdb) continue
```

## 實用的 GDB 指令

```bash
# 設置斷點
break function_name
break file.rs:line_number

# 執行控制
run                # 開始執行
continue          # 繼續執行
next              # 執行下一行
step              # 進入函數
finish            # 執行完當前函數

# 查看變數
print variable_name
info locals       # 顯示所有局部變數
info args         # 顯示函數參數

# 查看堆疊
backtrace         # 顯示調用堆疊
frame n           # 切換到第 n 個堆疊框架
```

這些範例包含了各種常見的程式結構，你可以嘗試在不同位置設置斷點，觀察變數的值變化。Go 的調試體驗可能會比較複雜，而 Rust 通常會更順暢一些。
