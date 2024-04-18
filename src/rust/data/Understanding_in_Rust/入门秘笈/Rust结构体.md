# Rust結構體

結構體是使用者定義的資料型別，由不同資料型別的變數組成。通過在結構體名稱之前使用 結構體成員包含在大括號內。在大括號內，結構體成員定義了它們的名稱和型別，結構成員也稱為欄位。`struct`

結構體語法：

```rust
struct Student  
{  
    member-variable1;  
    member-variable2;  
    .  
    .  
}
```

在上面的語法中，結構體是使用關鍵字 結構體包含不同型別的變數。`struct`

宣告結構體的範例 -

```rust
let user = Student{  
// key:value pairs;  
}
```

在上面的宣告中，它通過使用結構名稱然後使用大括號來定義。大括號包含鍵：值對，其中鍵是欄位的名稱，`user``Student``value`

下面程式碼建立一個員工結構體：

```rust
struct Employee{  
    employee_name : String,  
    employee_id: u64,  
    employee_profile: String,  
    active: bool,  
}
```

員工結構體範例：

```rust
let employee = Employee{  
    employee_name : String::from("Akshay Gupta"),  
    employee_id: 12,  
    employee_profile : String::from("Computer Engineer"),  
    active : true,  
};
```

**如何存取結構體的成員變數？可以使用點( 假設想要存取**
`.``Employee``employee_name`

```rust
employee.employee_name;
```

> 注意：如果想通過使用點表示法來更改特定欄位的值，那麼必須使範例可變，因為Rust不允許特定欄位為可變欄位。

```rust
let mut employee = Employee{  
    employee_name : String::from("Akshay Gupta"),  
    employee_id: 12,  
    employee_profile : String::from("Computer Engineer"),  
    active : true,  
};  
employee.employee_name = String :: from("Akhil Gupta");
```

在函式體中建立範例：

```rust
fn create_employee(name:String, profile:String)  
{  
    Employee{  
        employee_name:name,  
        employee_id:12,  
        employee_profile:profile,  
        active:true,  
    }  
}
```

在上面的範例中，在函式體中隱式建立了 函式返回具有給定名稱和組態檔案的`Employee``create_employee()``Employee`

當傳遞給函式和欄位的引數具有相同名稱時，使用欄位初始化簡寫。

當變數和欄位具有相同的名稱時，Rust提供了使用欄位初始化簡寫的靈活性。不需要重複欄位和變數。

```rust
 fn create_employee(employee_name:String, employee_profile:String)  
{  
    Employee{  
        employee_name,  
        employee_id:12,  
        employee_profile,  
        active:true,  
    }  
}
```

在上面的範例中，引數和欄位的名稱相同。因此，不需要編寫`employee_name:employee_name``employee_name`
