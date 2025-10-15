# Any和反射

熟悉Java的同學肯定對Java的反射能力記憶猶新，同樣的，Rust也提供了運行時反射的能力。但是，這裡有點小小的不同，因為 Rust 不帶 VM 不帶 Runtime ,因此，其提供的反射更像是一種編譯時反射。

因為，Rust只能對 `'static` 生命週期的變量（常量）進行反射！

## 舉個例子

我們會有這樣的需求，去某些路徑里加載配置文件。我們可能提供一個配置文件路徑，好吧，這是個字符串(`String`)。但是，當我想要傳入多個配置文件的路徑的時候怎們辦？理所應當的，我們傳入了一個數組。

這下可壞了……Rust不支持重載啊！於是有人就很單純的寫了兩個函數～～！

其實不用……我們只需要這麼寫……

```rust
use std::any::Any;
use std::fmt::Debug ;

fn load_config<T:Any+Debug>(value: &T) -> Vec<String>{
    let mut cfgs: Vec<String>= vec![];
    let value = value as &Any;
    match value.downcast_ref::<String>() {
        Some(cfp) => cfgs.push(cfp.clone()),
        None => (),
    };

    match value.downcast_ref::<Vec<String>>() {
        Some(v) => cfgs.extend_from_slice(&v),
        None =>(),
    }

    if cfgs.len() == 0 {
        panic!("No Config File");
    }
    cfgs
}

fn main() {
    let cfp = "/etc/wayslog.conf".to_string();
    assert_eq!(load_config(&cfp), vec!["/etc/wayslog.conf".to_string()]);
    let cfps = vec!["/etc/wayslog.conf".to_string(),
                    "/etc/wayslog_sec.conf".to_string()];
    assert_eq!(load_config(&cfps),
               vec!["/etc/wayslog.conf".to_string(),
                    "/etc/wayslog_sec.conf".to_string()]);
}
```

我們來重點分析一下中間這個函數：

```rust
fn load_config<T:Any+Debug>(value: &T) -> Vec<String>{..}
```

首先，這個函數接收一個泛型`T`類型，`T`必須實現了`Any`和`Debug`。

這裡可能有同學疑問了，你不是說只能反射 `'static` 生命週期的變量麼？我們來看一下`Any`限制：

```rust
pub trait Any: 'static + Reflect {
    fn get_type_id(&self) -> TypeId;
}
```

看，`Any`在定義的時候就規定了其生命週期，而`Reflect`是一個Marker，默認所有的Rust類型都會實現他！注意，這裡不是所有原生類型，而是所有類型。

好的，繼續，由於我們無法判斷出傳入的參數類型，因此，只能從運行時候反射類型。

```rust
let value = value as &Any;
```

首先，我們需要將傳入的類型轉化成一個 `trait Object`, 當然了，你高興的話用 `UFCS` 也是可以做的，參照本章最後的附錄。

這樣，value 就可以被堪稱一個 Any 了。然後，我們通過 `downcast_ref` 來進行類型推斷。如果類型推斷成功，則 value 就會被轉換成原來的類型。

有的同學看到這裡有點懵，為什麼你都轉換成 Any 了還要轉回來？

其實，轉換成 Any 是為了有機會獲取到他的類型信息，轉換回來，則是為了去使用這個值本身。

最後，我們對不同的類型處以不同的處理邏輯。最終，一個反射函數就完成了。

## 說說注意的地方

需要注意的是，Rust本身提供的反射能力並不是很強大。相對而言只能作為一個輔助的手段。並且，其只能對`'static`週期進行反射的限制，的確限制了其發揮。還有一點需要注意的是，Rust的反射只能被用作類型推斷，絕對不能被用作接口斷言！

啥，你問原因？因為寫不出來啊……
