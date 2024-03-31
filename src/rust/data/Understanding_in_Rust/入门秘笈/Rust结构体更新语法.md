# Rust結構體更新語法

使用 當新範例使用舊範例的大部分值時，可以使用 考慮兩名員工`Struct`
`struct update``employee1``employee2`

- 首先，建立`Employee``employee1`

```rust
let employee1 = Employee{  
    employee_name : String::from("Maxsu"),  
    employee_id: 12,  
    employee_profile : String::from("IT工程師"),  
    active : true,  
};
```

- 其次，建立 範例的某些值與 有兩種方法可以宣告 第一種方法是在沒有語法更新的情況下宣告`employee2``employee2``employee1``employee2`
  `employee2`

```rust
let employee2 = Employee{  
    employee_name : String::from("Maxsu"),  
    employee_id: 11,  
    employee_profile : employee1.employee_profile,  
    active : employee1.active,  
};
```

第二種方法是使用語法更新宣告`employee2`

```rust
let employee2 = Employee{  
    employee_name : String::from("Yiibai"),  
    employee_id: 11,  
    ..employee1  
};
```

語法`..`

下面來看一個結構的簡單範例：

```rust
struct Triangle  
{  
    base:f64,  
    height:f64,  
}  

fn main()  
{  
    let triangle= Triangle{base:20.0,height:30.0};  
    print!("Area of a right angled triangle is {}", area(&triangle));  
}  

fn area(t:&Triangle)->f64  
{  
    0.5 * t.base * t.height  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Area of a right angled triangle is 300
```

在上面的例子中，建立了三角形( 三角形(`Triangle``Triangle``main()`
