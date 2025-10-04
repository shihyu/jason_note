
Rust 提供了將包分成多個 crate，將 crate 分成模塊的機制。

模塊系統包括：
- 包（Packages）： 一個包中至多 只能 包含一個庫 crate(library crate)；包中可以包含任意多個二進制 crate(binary crate)；
- Crates ：一個模塊的樹形結構，它形成了庫或二進制項目。
- 模塊（Modules）和 use： 允許你控制作用域和路徑的私有性。
- 路徑（path）：一個命名例如結構體、函數或模塊等項的方式

創建新項目
```shell
#cargo new helloworld
```

- src/main.rs 就是一個與包同名的二進制 crate
- src/lib.rs 是一個與包同名的庫 crate  
- 將文件放在 src/bin 目錄下，一個包可以擁有多個二進制 crate：每個 src/bin 下的文件都會被編譯成一個獨立的二進制 crate


創建lib
```shell
#cargo new --lib testlib
```


