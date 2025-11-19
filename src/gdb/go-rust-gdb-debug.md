# Go 和 Rust GDB 調試指南

## Go 測試範例

### 程式碼 (main.go)
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

### 編譯和調試指令
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

## Rust 測試範例

### 建立專案
```bash
# 建立 Cargo 專案
cargo new rust_debug_test
cd rust_debug_test
```

### 程式碼 (src/main.rs)
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

### 編譯和調試指令
```bash
# 編譯
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

### 設置斷點
```bash
break function_name           # 在函數入口設置斷點
break file.rs:line_number     # 在指定行設置斷點
break main.go:25              # 在指定檔案的指定行設置斷點
info breakpoints              # 顯示所有斷點
delete 1                      # 刪除編號 1 的斷點
```

### 執行控制
```bash
run                          # 開始執行程式
continue                     # 繼續執行直到下一個斷點
next                         # 執行下一行 (不進入函數)
step                         # 執行下一行 (進入函數)
finish                       # 執行完當前函數並返回
quit                         # 退出 GDB
```

### 查看變數和狀態
```bash
print variable_name          # 顯示變數值
print *pointer              # 顯示指標指向的值
info locals                 # 顯示所有局部變數
info args                   # 顯示函數參數
whatis variable_name        # 顯示變數類型
```

### 查看堆疊和框架
```bash
backtrace                   # 顯示調用堆疊
bt                          # backtrace 的縮寫
frame n                     # 切換到第 n 個堆疊框架
up                          # 上移一個框架
down                        # 下移一個框架
```

### 查看程式碼
```bash
list                        # 顯示當前位置的程式碼
list function_name          # 顯示指定函數的程式碼
list file.rs:20             # 顯示指定檔案的指定行
```

## 調試技巧

### Go 特定注意事項
- 使用 `-gcflags="-N -l"` 關閉優化，否則變數可能被優化掉
- Go 的 goroutine 調試需要特殊處理
- 某些 Go 內建類型在 GDB 中可能顯示不完整

### Rust 特定注意事項
- 優先使用 `rust-gdb` 而非一般 GDB，它有更好的 Rust 支援
- Rust 的 `Option` 和 `Result` 類型在 GDB 中可能需要特殊處理
- 使用 `cargo build` 而非 `cargo build --release` 以保留調試資訊

### 通用技巧
- 在關鍵位置添加 `sleep` 或 `pause` 來方便設置斷點
- 使用 `info locals` 快速查看所有局部變數
- 善用 `backtrace` 瞭解函數調用關係
