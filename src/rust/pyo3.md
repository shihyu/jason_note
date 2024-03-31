# 解密 Python 如何呼叫 Rust 編譯生成的動態連結庫



## 楔子





Rust 讓 Python 更加偉大，隨著 Rust 的流行，反而讓 Python 的生產力提高了不少。因為有越來越多的 Python 工具，都選擇了 Rust 進行開發，並且性能也優於同類型的其它工具。比如：

- ruff：速度極快的程式碼分析工具，以及程式碼格式化工具；
- orjson：一個高性能的 JSON 解析庫；
- watchfiles：可以對指定目錄進行即時監控；
- polars：和 pandas 類似的資料分析工具；
- pydantic：資料驗證工具；
- ......

總之現在 Rust + Python 已經成為了一個趨勢，並且 Rust 也提供了一系列成熟好用的工具，比如 PyO3、Maturin，專門為 Python 編寫擴展。不過關於 PyO3 我們以後再聊，本篇文章先來介紹如何將 Rust 程式碼編譯成動態庫，然後交給 Python 的 ctypes 模組呼叫。

因為通過 ctypes 呼叫動態庫是最簡單的一種方式，它只對作業系統有要求，只要作業系統一致，那麼任何提供了 ctypes 模組的 Python 直譯器都可以呼叫。

當然這也側面要求，Rust 提供的介面不能太複雜，因為 ctypes 提供的互動能力還是比較有限的，最明顯的問題就是不同語言的資料類型不同，一些複雜的互動方式還是比較難做到的，還有多執行緒的控制問題等等。

> 之前說過使用 ctypes 呼叫 C 的動態庫，裡面詳細介紹了 ctypes 的用法，因此本文關於 ctypes 就不做詳細介紹了。



## 舉個例子





下面我們舉個例子感受一下 Python 和 Rust 的互動過程，首先通過如下命令建立一個 Rust 項目：

複製

```sql
cargo new py_lib --lib1.
```

建立完之後修改 Cargo.toml，在裡面加入如下內容：

複製

```sql
[lib]
# 編譯之後的動態庫的名稱
name = "py_lib"
# 表示編譯成一個和 C 語言二進制介面（ABI）相容的動態連結庫
crate-type = ["cdylib"]1.2.3.4.5.
```

cdylib 表示生成動態庫，如果想生成靜態庫，那麼就指定為 staticlib。

下面開始編寫原始碼，在生成項目之後，src 目錄下會有一個 lib.rs，它是整個庫的入口點。我們的程式碼比較簡單，直接寫在 lib.rs 裡面即可。

複製

```sql
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[no_mangle]
pub extern "C" fn get_square_root(v: i32) -> f64 {
    (v as f64).sqrt()
}1.2.3.4.5.6.7.8.9.
```

在定義函數時需要使用 pub extern "C" 進行聲明，它表示建立一個外部可見、遵循 C 語言呼叫約定的函數，因為 Python 使用的是 C ABI。

此外還要給函數新增一個 #[no_mangle] 屬性，讓編譯器在將 Rust 函數匯出為 C 函數時，不要改變函數的名稱。確保在編譯成動態庫後，函數名保持不變，否則在呼叫動態庫時就找不到指定的函數了。

Rust 有個名稱修飾（Name Mangling）的機制，在跨語言操作時，會修改函數名，增加一些額外資訊。這種修改對 Rust 內部使用沒有影響，但會干擾其它語言的呼叫，因此需要通過 #[no_mangle] 將該機制停用掉。

程式碼編寫完成，我們通過 cargo build 進行編譯，然後在 target/debug 目錄下就會生成相應的動態庫。由於庫的名稱我們指定為 py_lib，那麼生成的庫檔案名稱就叫 libpy_lib.dylib。

當功能全部實現並且測試通過時，最好重新編譯一次，並加上 --release 參數。這樣可以對程式碼進行最佳化，當然編譯時間也會稍微長一些，並且生成的庫檔案會在 target/release 目錄中。

編譯器生成動態庫後，會自動加上一個 lib 前綴（Windows 系統除外），至於後綴則與作業系統有關。

- Windows 系統，後綴名為 .dll；
- macOS 系統，後綴名為 .dylib；
- Linux 系統，後綴名為 .so；

然後我們通過 Python 進行呼叫。

複製

```sql
import ctypes

# 使用 ctypes 很簡單，直接 import 進來
# 然後使用 ctypes.CDLL 這個類來載入動態連結庫
# 或者使用 ctypes.cdll.LoadLibrary 也是可以的
py_lib = ctypes.CDLL("../py_lib/target/debug/libpy_lib.dylib")

# 載入之後就得到了動態連結庫對象，我們起名為 py_lib
# 然後通過屬性訪問的方式去呼叫裡面的函數
print(py_lib.add(11, 22))
"""
33
"""

# 如果不確定函數是否存在，那麼建議使用反射
# 因為函數不存在，通過 . 的方式獲取是會拋異常的
get_square_root = getattr(py_lib, "get_square_root", None)
if get_square_root:
    print(get_square_root)
    """
    <_FuncPtr object at 0x7fae30a2b040>
    """

# 不存在 sub 函數，所以得到的結果為 None
sub = getattr(py_lib, "sub", None)
print(sub)
"""
None
"""1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.
```

所以使用 ctypes 去呼叫動態連結庫非常方便，過程很簡單：

- 1）通過 ctypes.CDLL 去載入動態庫；
- 2）載入動態連結庫之後會返回一個對象，我們上面起名為 py_lib；
- 3）然後直接通過 py_lib 呼叫裡面的函數，但為了程序的健壯性，建議使用反射，確定呼叫的函數存在後才會呼叫;



我們以上就演示瞭如何通過 ctypes 模組來呼叫 Rust 編譯生成的動態庫，但顯然目前還是遠遠不夠的，比如說：

複製

```sql
from ctypes import CDLL

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

square_root = py_lib.get_square_root(100)
print(square_root)  # 01.2.3.4.5.6.
```

100 的平方根是 10，但卻返回了 0。這是因為 ctypes 在解析返回值的時候默認是按照整型來解析的，但當前的函數返回的是浮點型，因此函數在呼叫之前需要顯式地指定其返回值類型。

不過在這之前，我們需要先來看看 Python 類型和 Rust 類型之間的轉換關係。



## 數值類型





使用 ctypes 呼叫動態連結庫，主要是呼叫庫裡面使用 Rust 編寫好的函數，但這些函數是需要參數的，還有返回值。而不同語言的變數類型不同，Python 不能直接往 Rust 編寫的函數中傳參，因此 ctypes 提供了大量的類，幫我們將 Python 的類型轉成 Rust 的類型。

與其說轉成 Rust 的類型，倒不如說轉成 C 的類型，因為 Rust 匯出的函數要遵循 C 的呼叫約定。

下面來測試一下，首先編寫 Rust 程式碼：

複製

```sql
#[no_mangle]
pub extern "C" fn add_u32(a: u32) -> u32 {
    a + 1
}
#[no_mangle]
pub extern "C" fn add_isize(a: isize) -> isize {
    a + 1
}
#[no_mangle]
pub extern "C" fn add_f32(a: f32) -> f32 {
    a + 1.
}
#[no_mangle]
pub extern "C" fn add_f64(a: f64) -> f64 {
    a + 1.
}
#[no_mangle]
pub extern "C" fn reverse_bool(a: bool) -> bool {
    !a
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.
```

編譯之後 Python 進行呼叫。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

print(py_lib.add_u32(123))
"""
124
"""
print(py_lib.add_isize(666))
"""
667
"""
try:
    print(py_lib.add_f32(3.14))
except Exception as e:
    print(e)
"""
<class 'TypeError'>: Don't know how to convert parameter 1
"""
# 我們看到報錯了，告訴我們不知道如何轉化第 1 個參數
# 因為 Python 的資料和 C 的資料不一樣，所以不能直接傳遞
# 但整數是個例外，除了整數，其它資料都需要使用 ctypes 包裝一下
# 另外整數最好也包裝一下，因為不同整數之間，精度也有區別
print(py_lib.add_f32(c_float(3.14)))
"""
1
"""
# 雖然沒報錯，但是結果不對，結果應該是 3.14 + 1 = 4.14，而不是 1
# 因為 ctypes 呼叫函數時默認使用整型來解析，但該函數返回的不是整型
# 需要告訴 ctypes，add_f32 函數返回的是 c_float，請按照 c_float 來解析
py_lib.add_f32.restype = c_float
print(py_lib.add_f32(c_float(3.14)))
"""
4.140000343322754
"""
# f32 和 f64 是不同的類型，佔用的位元組數也不一樣
# 所以 c_float 和 c_double 之間不可混用，雖然都是浮點數
py_lib.add_f64.restype = c_double
print(py_lib.add_f64(c_double(3.14)))
"""
4.140000000000001
"""

py_lib.reverse_bool.restype = c_bool
print(py_lib.reverse_bool(c_bool(True)))
print(py_lib.reverse_bool(c_bool(False)))
"""
False
True
"""1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.30.31.32.33.34.35.36.37.38.39.40.41.42.43.44.45.46.47.48.49.50.
```

不複雜，以上我們就實現了數值類型的傳遞。



## 字元類型





字元類型有兩種，一種是 ASCII 字元，本質上是個 u8；一種是 Unicode 字元，本質上是個 u32。

編寫 Rust 程式碼：

複製

```sql
#[no_mangle]
pub extern "C" fn get_char(a: u8) -> u8  {
    a + 1
}

#[no_mangle]
pub extern "C" fn get_unicode(a: u32) -> u32  {
    let chr = char::from_u32(a).unwrap();
    if chr == '憨' {
        '批' as u32
    } else {
        a
    }
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.
```

我們知道 Rust 專門提供了 4 個位元組 char 類型來表示 unicode 字元，但對於外部匯出函數來說，使用 char 是不安全的，所以直接使用 u8 和 u32 就行。

編譯之後，Python 呼叫：

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

# u8 除了可以使用 c_byte 包裝之外，還可以使用 c_char
# 並且 c_byte 裡面只能接收整數，而 c_char 除了整數，還可以接收長度為 1 的位元組串
print(c_byte(97))
print(c_char(97))
print(c_char(b"a"))
"""
c_byte(97)
c_char(b'a')
c_char(b'a')
"""
# 以上三者是等價的，因為 char 說白了就是個 u8

# 指定返回值為 c_byte，會返回一個整數
py_lib.get_char.restype = c_byte
# c_byte(97)、c_char(97)、c_char(b"a") 都是等價的
# 因為它們本質上都是 u8，至於 97 也可以解析為 u8
print(py_lib.get_char(97))  # 98
# 指定返回值為 c_char，會返回一個字元（長度為 1 的 bytes 對象）
py_lib.get_char.restype = c_char
print(py_lib.get_char(97))  # b'b'


py_lib.get_unicode.restype = c_wchar
print(py_lib.get_unicode(c_wchar("嘿")))  # 嘿
# 直接傳一個 u32 整數也可以，因為 unicode 字元底層就是個 u32
print(py_lib.get_unicode(ord("憨")))  # 批1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.30.
```

以上就是字元類型的操作，比較簡單。



## 字串類型





再來看看字串，我們用 Rust 實現一個函數，它接收一個字串，然後返回大寫形式。

複製

```sql
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn to_uppercase(s: *const c_char) -> *mut c_char {
    // 將 *const c_char 轉成 &CStr
    let s = unsafe {
        CStr::from_ptr(s)
    };
    // 將 &CStr 轉成 &str
    // 然後呼叫 to_uppercase 轉成大寫，得到 String
    let s = s.to_str().unwrap().to_uppercase();
    // 將 String 轉成 *mut char 返回
    CString::new(s).unwrap().into_raw()
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.
```

解釋一下里面的 CStr 和 CString，在 Rust 中，CString 用於建立 C 風格的字串（以 \0 結尾），擁有自己的記憶體。關鍵的是，CString 擁有值的所有權，當實例離開範疇時，它的解構函式會被呼叫，相關記憶體會被自動釋放。

而 CStr，它和 CString 之間的關係就像 str 和 String 的關係，所以 CStr 一般以引用的形式出現。並且 CStr 沒有 new 方法，不能直接建立，它需要通過 from_ptr 方法從原始指針轉化得到。

然後指針類型是 *const 和 *mut，分別表示指向 C 風格字串的首字元的不可變指針和可變指針，它們的區別主要在於指向的資料是否可以被修改。如果不需要修改，那麼使用 *const 會更安全一些。

我們編寫 Python 程式碼測試一下。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")
s = "hello 古明地覺".encode("utf-8")
# 默認是按照整型解析的，所以不指定返回值類型的話，會得到髒資料
print(py_lib.to_uppercase(c_char_p(s)))
"""
31916096
"""
# 指定返回值為 c_char_p，表示按照 char * 來解析
py_lib.to_uppercase.restype = c_char_p
print(
    py_lib.to_uppercase(c_char_p(s)).decode("utf-8")
)
"""
HELLO 古明地覺
"""1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.
```

從表面上看似乎挺順利的，但背後隱藏著記憶體洩露的風險，因為 Rust 裡面建立的 CString 還駐留在堆區，必須要將它釋放掉。所以我們還要寫一個函數，用於釋放字串。

複製

```sql
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn to_uppercase(s: *const c_char) -> *mut c_char {
    let s = unsafe {
        CStr::from_ptr(s)
    };
    let s = s.to_str().unwrap().to_uppercase();
    CString::new(s).unwrap().into_raw()
}

#[no_mangle]
pub extern "C" fn free_cstring(s: *mut c_char) {
    unsafe {
        if s.is_null() { return }
        // 基於原始指針建立 CString，拿到堆區字串的所有權
        // 然後離開範疇，自動釋放
        CString::from_raw(s)
    };
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.
```

然後來看看 Python 如何呼叫：

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

s = "hello 古明地覺".encode("utf-8")
# Rust 返回的是原始指針，這裡必須要拿到它保存的地址
# 所以指定返回值為 c_void_p，如果指定為 c_char_p，
# 那麼會直接轉成 bytes 對象，這樣地址就拿不到了
py_lib.to_uppercase.restype = c_void_p
# 拿到地址，此時的 ptr 是一個普通的整數，但它和指針保存的地址是一樣的
ptr = py_lib.to_uppercase(c_char_p(s))
# 將 ptr 轉成 c_char_p，獲取 value 屬性，即可得到具體的 bytes 對象
print(cast(ptr, c_char_p).value.decode("utf-8"))
"""
HELLO 古明地覺
"""
# 內容我們拿到了，但堆區的字串還沒有釋放，所以呼叫 free_cstring
py_lib.free_cstring(c_void_p(ptr))1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.
```

通過 CString 的 into_raw，可以基於 CString 建立原始指針 *mut，然後 Python 將指針指向的堆區資料複製一份，得到 bytes 對象。

但這個 CString 依舊駐留在堆區，所以 Python 不能將返回值指定為 c_char_p，因為它會直接建立 bytes 對象，這樣就拿不到指針了。因此將返回值指定為 c_void_p，呼叫函數會得到一串整數，這個整數就是指針保存的地址。

我們使用 cast 函數可以將地址轉成 c_char_p，獲取它的 value 屬性拿到具體的位元組串。再通過 c_void_p 建立原始指針交給 Rust，呼叫 CString 的 from_raw，可以基於 *mut 建立 CString，從而將所有權奪回來，然後離開範疇時釋放堆記憶體。



## 給函數傳遞指針





如果擴展函數裡面接收的是指針，那麼 Python 要怎麼傳遞呢？

複製

```sql
#[no_mangle]
pub extern "C" fn add(a: *mut i32, b: *mut i32) -> i32 {
    // 定義為 *mut，那麼可以修改指針指向的值，定義為 *const，則不能修改
    if a.is_null() || b.is_null() {
        0
    } else {
        let res = unsafe {
            *a + *b
        };
        unsafe {
            // 這裡將 *a 和 *b 給改掉
            *a = 666;
            *b = 777;
        }
        res
    }
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.
```

定義了一個 add 函數，接收兩個 i32 指針，返回解引用後相加的結果。但是在返回之前，我們將 *a 和 *b 的值也修改了。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

a = c_int(22)
b = c_int(33)
# 計算
print(py_lib.add(pointer(a), pointer(b)))  # 55
# 我們看到 a 和 b 也被修改了
print(a, a.value)  # c_int(666) 666
print(b, b.value)  # c_int(777) 7771.2.3.4.5.6.7.8.9.10.11.
```

非常簡單，那麼問題來了，能不能返回一個指針呢？答案是當然可以，只不過存在一些注意事項。

由於 Rust 本身的記憶體安全原則，直接從函數返回一個指向本地局部變數的指針是不安全的。因為該變數的範疇僅限於函數本身，一旦函數返回，該變數的記憶體就會被回收，從而出現懸空指針。

為了避免這種情況出現，我們應該在堆上分配記憶體，但這又出現了之前 CString 的問題。Python 在拿到值之後，堆記憶體依舊駐留在堆區。因此 Rust 如果想返回指針，那麼同時還要定義一個釋放函數。

複製

```sql
#[no_mangle]
pub extern "C" fn add(a: *const i32, b: *const i32) -> *mut i32 {
    // 返回值的類型是 *mut i32，所以 res 不能直接返回，因此它是 i32
    let res = unsafe {*a + *b};
    // 建立智能指針（將 res 裝箱），然後返回原始指針
    Box::into_raw(Box::new(res))
}

#[no_mangle]
pub extern "C" fn free_i32(ptr: *mut i32) {
    if !ptr.is_null() {
        // 轉成 Box<i32>，同時拿到所有權，在離開範疇時釋放堆記憶體
        unsafe { let _ = Box::from_raw(ptr); }
    }
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.
```

然後 Python 進行呼叫：

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

a, b = c_int(22), c_int(33)
# 指定類型為 c_void_p
py_lib.add.restype = c_void_p
# 拿到指針保存的地址
ptr = py_lib.add(pointer(a), pointer(b))
# 將 c_void_p 轉成 POINTER(c_int) 類型，也就是 c_int *
# 通過它的 contents 屬性拿到具體的值
print(cast(ptr, POINTER(c_int)).contents)  # c_int(55)
print(cast(ptr, POINTER(c_int)).contents.value)  # 55
# 釋放堆記憶體
py_lib.free_i32(c_void_p(ptr))1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.
```

這樣我們就拿到了指針，並且也不會出現記憶體洩露。但是單獨定義一個釋放函數還是有些麻煩的，所以 Rust 自動提供了一個 free 函數，專門用於釋放堆記憶體。舉個例子：

複製

```sql
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn to_uppercase(s: *const c_char) -> *mut c_char {
    let s = unsafe {
        CStr::from_ptr(s)
    };
    let s = s.to_str().unwrap().to_uppercase();
    CString::new(s).unwrap().into_raw()
}

#[no_mangle]
pub extern "C" fn add(a: *const i32, b: *const i32) -> *mut i32 {
    let res = unsafe {*a + *b};
    Box::into_raw(Box::new(res))
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.
```

這是出現過的兩個函數，它們的記憶體都申請在堆區，但我們將記憶體釋放函數刪掉了，因為 Rust 自動提供了一個 free 函數，專門用於堆記憶體的釋放。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

# 返回值類型指定為 c_void_p，表示萬能指針
py_lib.to_uppercase.restype = c_void_p
py_lib.add.restype = c_void_p

ptr1 = py_lib.to_uppercase(
    c_char_p("Serpen 老師".encode("utf-8"))
)
ptr2 = py_lib.add(
    pointer(c_int(123)), pointer(c_int(456))
)
# 函數呼叫完畢，將地址轉成具體的類型的指針
print(cast(ptr1, c_char_p).value.decode("utf-8"))
"""
SERPEN 老師
"""
print(cast(ptr2, POINTER(c_int)).contents.value)
"""
579
"""
# 釋放堆記憶體，直接呼叫 free 函數即可，非常方便
py_lib.free(c_void_p(ptr1))
py_lib.free(c_void_p(ptr2))1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.
```

以上我們就實現了指針的傳遞和返回，但對於整數、浮點數而言，直接返回它們的值即可，沒必要返回指針。



## 傳遞陣列





下面來看看如何傳遞陣列，由於陣列在作為參數傳遞的時候會退化為指針，所以陣列的長度資訊就丟失了，使用 sizeof 計算出來的結果就是一個指針的大小。因此將陣列作為參數傳遞的時候，應該將當前陣列的長度資訊也傳遞過去，否則可能會訪問非法的記憶體。

我們實現一個功能，Rust 接收一個 Python 陣列，進行原地排序。

複製

```sql
use std::slice;

#[no_mangle]
pub extern "C" fn sort_array(arr: *mut i32, len: usize) {
    assert!(!arr.is_null());

    unsafe {
        // 得到一個切片 &mut[i32]
        let slice = slice::from_raw_parts_mut(arr, len);
        slice.sort();  // 排序
    }
}1.2.3.4.5.6.7.8.9.10.11.12.
```

然後 Python 進行呼叫：

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

# 一個列表
data = [3, 2, 1, 5, 4, 7, 6]
# 但是列表不能傳遞，必須要轉成 C 陣列
# Array_Type 就相當於 C 的 int array[len(data)]
Array_Type = c_int * len(data)
# 建立陣列
array = Array_Type(*data)
print(list(array))  # [3, 2, 1, 5, 4, 7, 6]
py_lib.sort_array(array, len(array))
print(list(array))  # [1, 2, 3, 4, 5, 6, 7]1.2.3.4.5.6.7.8.9.10.11.12.13.14.
```

排序實現完成，這裡的陣列是 Python 傳過去的，並且進行了原地修改。那 Rust 可不可以返回陣列給 Python 呢？從理論上來說可以，但實際不建議這麼做，因為你不知道返回的陣列的長度是多少？

如果你真的想返回陣列的話，那麼可以將陣列拼接成字串，然後返回。

複製

```sql
use std::ffi::{c_char, CString};

#[no_mangle]
pub extern "C" fn create_array() -> *mut c_char {
    // 篩選出 1 到 50 中，能被 3 整除的數
    // 並以逗號為分隔符，將這些整數拼接成字串
    let vec = (1..=50)
        .filter(|c| *c % 3 == 0)
        .map(|c| c.to_string())
        .collect::<Vec<String>>()
        .join(",");
    CString::new(vec).unwrap().into_raw()
}1.2.3.4.5.6.7.8.9.10.11.12.13.
```

編譯之後交給 Python 呼叫。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

# 只要是需要釋放的堆記憶體，都建議按照 c_void_p 來解析
py_lib.create_array.restype = c_void_p
# 此時拿到的就是指針保存的地址，在 Python 裡面就是一串整數
ptr = py_lib.create_array()
# 由於是字串首字元的地址，所以轉成 char *，拿到具體內容
print(cast(ptr, c_char_p).value.decode("utf-8"))
"""
3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48
"""
# 此時我們就將陣列拼接成字串返回了
# 但是堆區的 CString 還在，所以還要釋放掉，呼叫 free 函數即可
# 注意：ptr 只是一串整數，或者說它就是 Python 的一個 int 對象
# 換句話說 ptr 只是保存了地址值，但它不具備指針的含義
# 因此需要再使用 c_void_p 包裝一下（轉成指針），才能傳給 free 函數
py_lib.free(c_void_p(ptr))1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.
```

因此雖然不建議返回陣列，但將陣列轉成字串返回也不失為一個辦法，當然除了陣列，你還可以將更複雜的結構轉成字串返回。



## 傳遞結構體





結構體應該是 Rust 裡面最重要的結構之一了，它要如何和外部互動呢？

複製

```sql
use std::ffi::c_char;

#[repr(C)]
pub struct Girl {
    pub name: *mut c_char,
    pub age: u8,
}

#[no_mangle]
pub extern "C" fn create_struct(name: *mut c_char, age: u8) -> Girl {
    Girl { name, age }
}1.2.3.4.5.6.7.8.9.10.11.12.
```

因為結構體實例要返回給外部，所以它的欄位類型必須是相容的，不能定義 C 理解不了的類型。然後還要設定 #[repr(C)] 屬性，來保證結構體的記憶體佈局和 C 是相容的。

下面通過 cargo build 命令編譯成動態庫，Python 負責呼叫。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

class Girl(Structure):

    _fields_ = [
        ("name", c_char_p),
        ("age", c_uint8),
    ]

# 指定 create_struct 的返回值類型為 Girl
py_lib.create_struct.restype = Girl
girl = py_lib.create_struct(
    c_char_p("S 老師".encode("utf-8")),
    c_uint8(18)
)
print(girl.name.decode("utf-8"))  # S 老師
print(girl.age)  # 181.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.
```

呼叫成功，並且此時是沒有記憶體洩露的。

當通過 FFI 將資料從 Rust 傳遞到 Python 時，如果傳遞的是指針，那麼會涉及記憶體釋放的問題。但如果傳遞的是值，那麼它會複製一份給 Python，而原始的值（這裡是結構體實例）會被自動銷毀，所以無需擔心。

然後是結構體內部的欄位，雖然裡面的 name 欄位是 *mut c_char，但它的值是由 Python 傳過來的，而不是在 Rust 內部建立的，因此沒有問題。

但如果將 Rust 程式碼改一下：

複製

```sql
use std::ffi::{c_char, CString};

#[repr(C)]
pub struct Girl {
    pub name: *mut c_char,
    pub age: u8,
}

#[no_mangle]
pub extern "C" fn create_struct() -> Girl {
    let name = CString::new("S 老師").unwrap().into_raw();
    let age = 18;
    Girl { name, age }
}1.2.3.4.5.6.7.8.9.10.11.12.13.14.
```

這時就尷尬了，此時的字串是 Rust 裡面建立的，轉成原始指針之後，Rust 將不再管理相應的堆記憶體（因為 into_raw 將所有權轉移走了），此時就需要手動堆記憶體了。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

class Girl(Structure):

    _fields_ = [
        ("name", c_char_p),
        ("age", c_uint8),
    ]

# 指定 create_struct 的返回值類型為 Girl
py_lib.create_struct.restype = Girl
girl = py_lib.create_struct()
print(girl.name.decode("utf-8"))  # S 老師
print(girl.age)  # 18
# 直接傳遞 girl 即可，會釋放 girl 裡面的欄位在堆區的記憶體
py_lib.free(girl)1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.
```

此時就不會出現記憶體洩露了，在 free 的時候，將變數 girl 傳進去，釋放掉內部欄位佔用的堆記憶體。

當然，Rust 也可以返回結構體指針，通過 Box<T> 實現。

複製

```sql
#[no_mangle]
pub extern "C" fn create_struct() -> *mut Girl {
    let name = CString::new("S 老師").unwrap().into_raw();
    let age = 18;
    Box::into_raw(Box::new(Girl { name, age }))
}1.2.3.4.5.6.
```

注意：之前是 name 欄位在堆上，但結構體實例在棧上，現在 name 欄位和結構體實例都在堆上。

然後 Python 呼叫也很簡單，關鍵是釋放的問題。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

class Girl(Structure):

    _fields_ = [
        ("name", c_char_p),
        ("age", c_uint8),
    ]

# 此時返回值類型就變成了 c_void_p
# 當返回指針時，建議將返回值設定為 c_void_p
py_lib.create_struct.restype = c_void_p
# 拿到指針（一串整數）
ptr = py_lib.create_struct()
# 將指針轉成指定的類型，而類型顯然是 POINTER(Girl)
# 呼叫 POINTER(T) 的 contents 方法，拿到相應的結構體實例
girl = cast(ptr, POINTER(Girl)).contents
# 訪問具體內容
print(girl.name.decode("utf-8"))  # S 老師
print(girl.age)  # 18

# 釋放堆記憶體，這裡的釋放分為兩步，並且順序不能錯
# 先 free(girl)，釋放掉內部欄位（name）佔用的堆記憶體
# 然後 free(c_void_p(ptr))，釋放掉結構體實例 girl 佔用的堆記憶體
py_lib.free(girl)
py_lib.free(c_void_p(ptr))1.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.
```

不難理解，只是在釋放結構體實例的時候需要多留意，如果內部有欄位佔用堆記憶體，那麼需要先將這些欄位釋放掉。而釋放的方式是將結構體實例作為參數傳給 free 函數，然後再傳入 c_void_p 釋放結構體實例。



## 回呼函數





最後看一下 Python 如何傳遞函數給 Rust，因為 Python 和 Rust 之間使用的是 C ABI，所以函數必須遵循 C 的標準。

複製

```sql
// calc 接收三個參數，前兩個參數是 *const i32
// 最後一個參數是函數，它接收兩個 *const i32，返回一個 i32
#[no_mangle]
pub extern "C" fn calc(
    a: *const i32, b: *const i32,
    op: extern "C" fn(*const i32, *const i32) -> i32
) -> i32
{
    op(a, b)
}1.2.3.4.5.6.7.8.9.10.
```

然後看看 Python 如何傳遞迴調函數。

複製

```sql
from ctypes import *

py_lib = CDLL("../py_lib/target/debug/libpy_lib.dylib")

# 基於 Python 函數建立 C 函數，通過 @CFUNCTYPE() 進行裝飾
# CFUNCTYPE 第一個參數是返回值類型，剩餘的參數是參數類型
@CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))
def add(a, b):  # a、b 為 int *，通過 .contents.value 拿到具體的值
    return a.contents.value + b.contents.value

@CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))
def sub(a, b):
    return a.contents.value - b.contents.value

@CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))
def mul(a, b):
    return a.contents.value * b.contents.value

@CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))
def div(a, b):
    return a.contents.value // b.contents.value

a = pointer(c_int(10))
b = pointer(c_int(2))
print(py_lib.calc(a, b, add))  # 12
print(py_lib.calc(a, b, sub))  # 8
print(py_lib.calc(a, b, mul))  # 20
print(py_lib.calc(a, b, div))  # 51.2.3.4.5.6.7.8.9.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.
```

成功實現了向 Rust 傳遞迴調函數，當然例子舉得有點刻意了，比如參數類型指定為 i32 即可，沒有必要使用指針。



## 小結





以上我們就介紹了 Python 如何呼叫 Rust 編譯的動態庫，再次強調一下，通過 ctypes 呼叫動態庫是最方便、最簡單的方式。它和 Python 的版本無關，也不涉及底層的 C 擴展，它只是將 Rust 編譯成 C ABI 相容的動態庫，然後交給 Python 進行呼叫。

因此這也側面要求，函數的參數和返回值的類型應該是 C 可以表示的類型，比如 Rust 函數不能返回一個 trait 對象。總之在呼叫動態庫的時候，庫函數內部的邏輯可以很複雜，但是參數和返回值最好要簡單。

如果你發現 Python 程式碼存在大量的 CPU 密集型計算，並且不怎麼涉及複雜的 Python 資料結構，那麼不妨將這些計算交給 Rust。

以上就是本文的內容，後續有空我們介紹如何用 Rust 的 PyO3 來為 Python 編寫擴展。PyO3 的定位類似於 Cython，用它來寫擴展非常的方便，後續有機會我們詳細聊一聊。