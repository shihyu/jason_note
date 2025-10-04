
## 結構體成員生命週期標註
如果結構體中包含引用，則需要進行生命週期標註。
這個標註意味著結構的實例不能比其 part 字段中的引用存在的更久

下面這段代碼是可以編譯通過的
```
struct Student<'a> {
    name: &'a str
}

fn main() {
    let studet_name = "Alice";
    {
        let student = Student { name : studet_name };
    }
}
```

## 方法中生命週期標註
方法和普通函數一樣，也可以標註生命週期。規則也一樣

規則如下：
- 1. 每個參數都擁有自己的生命週期
- 2. 如果只有一個輸入生命週期參數，則它被賦予所有輸出生命週期參數
- 3. 如果方法有多個輸入生命週期參數並且其中一個參數是 &self 或 &mut self，說明是個對象的方法(method)。那麼所有輸出生命週期參數被賦予 self 的生命週期。

下面這段代碼是可以編譯通過的，因為自動標註可以很好地工作。

```shell
struct Student<'a> {
    name: &'a str
}

impl <'a> Student<'a> {
    fn getScore(&self) -> i32 {
        100
    }
    fn getName(&self, command: &str) -> &str {
        println!("command: {}", command);
        self.name
    }
}
```

