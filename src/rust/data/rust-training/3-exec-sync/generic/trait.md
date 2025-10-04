trait 定義是一種將方法簽名組合起來的方法，目的是定義一個實現某些目的所必需的行為的集合。


## 入門例子
下面是一個trait的簡單例子，用法有點和其他語言中的接口類似。

```shell
pub trait Action {
    fn Eat(&self) -> String{
        return "Use hands".to_string();
    }
}

pub struct Chinese {}
impl Action for Chinese {
    fn Eat(&self) -> String{
        return "Use chopsticks eat".to_string();
    }
}

pub struct American {}
impl Action for American {
    fn Eat(&self) -> String{
        return "Use knife and fork".to_string();
    }
}
```

## trait當參數
trait可以作為參數傳遞給函數。
- impl Trait 方式
- trait bound 方式

下面是是採用impl Trait 的方式
```
fn function1(a: impl Action){
    println!("{}", a.Eat());
}
fn main() {
    let c = Chinese {};
    function1(c)；
}
```

下面是採用trait bound 的方式。
```
fn function2<T:Action>(a: T){
    println!("{}", a.Eat());
}
fn main() {
    let d = Chinese {};
    function2(d);
}
```

雖然trait bound看起來更長一些，但是它在傳遞多個trait為參數時更方便使用。