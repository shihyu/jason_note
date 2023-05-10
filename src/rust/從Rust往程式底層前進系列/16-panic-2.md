panic 2
=======

這篇要來看 `panic` 實際上是怎麼實作的，在那之前，先來介紹一個工具吧 - [`cargo-expand`][cargo-expand] ，它可以用來幫我們看 macro 實際展開來長什麼樣子，在它的網站上也可以看到它實際上是包裝了一個 `rustc` 的指令，如果你覺得為了這個功能裝一個程式麻煩的話，你可以直接使用說明裡的那個指令

[cargo-expand]: https://github.com/dtolnay/cargo-expand

當你安裝好這個工具後就來實際來看看 `panic` 展開後變成什麼了吧：

```rust
fn main() {
  panic!("panic");
}
```

上面的程式經過展開後變成了

```rust
#![feature(prelude_import)]
#[prelude_import]
use std::prelude::v1::*;

#[macro_use]
extern crate std;

fn main() {
  {
    ::std::rt::begin_panic("panic", &("src/main.rs", 2u32, 5u32))
  };
}
```

對，就只是一個函式呼叫，這個函式實際定義在 [`libstd/panicking.rs`][std-panicking]，它的內容我節錄重點的部份：

[std-panicking]: https://github.com/rust-lang/rust/blob/master/src/libstd/panicking.rs

```rust
pub fn begin_panic<M: Any + Send>(msg: M, file_line_col: &(&'static str, u32, u32)) -> ! {
  if cfg!(feature = "panic_immediate_abort") {
    unsafe { intrinsics::abort() }
  }

  rust_panic_with_hook(&mut PanicPayload::new(msg), None, file_line_col);
}
```

首先它檢察了一個 std 的 feature flag 叫 `panic_immediate_abort` ，這個功能就是讓 `panic` 發生時程式立刻結束而已，然後就轉去呼叫 `rust_panic_with_hook` 了

`rust_panic_with_hook` 也在同一個檔案裡，它其實也挺簡單的：

```rust
fn rust_panic_with_hook(payload: &mut dyn BoxMeUp,
  message: Option<&fmt::Arguments<'_>>,
  file_line_col: &(&str, u32, u32)) -> ! {
  let (file, line, col) = *file_line_col;

  let panics = update_panic_count(1);

  if panics > 2 {
    util::dumb_print(format_args!("thread panicked while processing \
    panic. aborting.\n"));
    unsafe { intrinsics::abort() }
  }

  // ... 呼叫 hook

  if panics > 1 {
    util::dumb_print(format_args!("thread panicked while panicking. \
    aborting.\n"));
    unsafe { intrinsics::abort() }
  }

  rust_panic(payload)
}
```

它的功能是更新一個 thread local 的 conunter 並用這個 conunter 來判斷是不是在 `panic` 過程中又發生了 `panic` ，如果是的話就直接停止程式，不然就呼叫 panic hook ，這個 panic hook 是可以讓使用者用 `std::panic::set_hook` 來設定的，接著呼叫 `rust_panic` 繼續處理，但接下來的函式其實都是一些簡單的包裝，照著 `rust_panic` -> `__rust_start_panic` 這樣的順序呼叫下去，我們直接跳到位於 [`libpanic_unwind/gcc.rs`][libpanic_unwind-gcc] 的 `panic` 這個函式吧：

```rust
pub unsafe fn panic(data: Box<dyn Any + Send>) -> u32 {
  let exception = Box::new(Exception {
    _uwe: uw::_Unwind_Exception {
      exception_class: rust_exception_class(),
      exception_cleanup,
      private: [0; uw::unwinder_private_data_size],
    },
    cause: Some(data),
  });
  let exception_param = Box::into_raw(exception) as *mut uw::_Unwind_Exception;
  return uw::_Unwind_RaiseException(exception_param) as u32;
  // ...
}
```

這邊終於有點不太一般的東西了， `_Unwind_RaiseException` 與 `_Unwind_Exception` ，這兩個是 C++ 內部用的拋出例外用的 API ，它有份跟 `llvm` 在一起的實作叫 `libunwind` ，在 Rust 的源始碼中也可以看到對 `libunwind` 做的包裝，用 `_Unwind_RaiseException` 就可以拋出由 `_Unwind_Exception` 所描述的例外，但並不是呼叫了這個函式就能拋出例外這麼簡單，還要實作一個東西，不知道你有沒有試過建立一個使用 `#![no_std]` 屬性的 Rust 執行檔專案呢？如果直接編譯應該會出現一些錯誤訊息，比如這個：

```plain
error: language item required, but not found: `eh_personality`
```

這個在之前的系列中提到使用 `#![no_std]` 時也有出現過，這東西可以說是使用這個例外處理的函式庫最重要的一個東西吧，基本上它是給 `libunwind` 來呼叫的一個回呼函式，功能是判斷每個 `frame` 有沒有要處理例外，以及處理時應該跳到哪邊執行，我們來看看在同樣檔案中的 `rust_eh_personality` 的內容吧：

```rust
unsafe extern "C" fn rust_eh_personality(version: c_int,
    actions: uw::_Unwind_Action,
    exception_class: uw::_Unwind_Exception_Class,
    exception_object: *mut uw::_Unwind_Exception,
    context: *mut uw::_Unwind_Context)
  -> uw::_Unwind_Reason_Code {
  if version != 1 {
    return uw::_URC_FATAL_PHASE1_ERROR;
  }
  let eh_action = match find_eh_action(context) {
    Ok(action) => action,
    Err(_) => return uw::_URC_FATAL_PHASE1_ERROR,
  };
  if actions as i32 & uw::_UA_SEARCH_PHASE as i32 != 0 {
    match eh_action {
      EHAction::None |
      EHAction::Cleanup(_) => return uw::_URC_CONTINUE_UNWIND,
      EHAction::Catch(_) => return uw::_URC_HANDLER_FOUND,
      EHAction::Terminate => return uw::_URC_FATAL_PHASE1_ERROR,
    }
  } else {
    match eh_action {
      EHAction::None => return uw::_URC_CONTINUE_UNWIND,
      EHAction::Cleanup(lpad) |
      EHAction::Catch(lpad) => {
        uw::_Unwind_SetGR(context, UNWIND_DATA_REG.0, exception_object as uintptr_t);
        uw::_Unwind_SetGR(context, UNWIND_DATA_REG.1, 0);
        uw::_Unwind_SetIP(context, lpad);
        return uw::_URC_INSTALL_CONTEXT;
      }
      EHAction::Terminate => return uw::_URC_FATAL_PHASE2_ERROR,
    }
  }
}
```

`libunwind` 在呼叫這個函式時會分成兩個階段，搜尋與執行實際的 unwind 的工作，`libunwind` 會依序向上走訪每個 `frame` 並呼叫這個函式

在第一階段的搜尋是要找出有沒有 `frame` 可以處理例外的，它這邊會呼叫 `find_eh_action` 這個函式，這個函式會回傳目前的 `frame` 需要做的動作，正常情況下有可能是什麼都不做的 `None` 或是需要清理的 `Cleanup` 與能處理例外的 `Catch` ，但函式的內容可能要留到下一篇了，這個階段就是根據這個回傳值回傳一個告訴 `libunwind` 要不要繼續找下去的值， `_URC_CONTINUE_UNWIND` 就是繼續下去 `_URC_HANDLER_FOUND` 則是找到能處理例外的位置，那它就會停止搜尋階段，進入第二個階段

第二個階段則要進行資源的釋放或是讓程式去處理例外並回到正常流程，不過實際上 Rust 並不是真的有例外處理，所以這邊的處理例外只是讓程式回到正常流程執行而已，也就是回到 `catch_unwind` 裡，但不管是哪個，在這邊 Rust 做的事都一樣，都是告訴 `libunwind` 要把 `panic` 的資訊存進暫存器裡，然後跳到 `lpad` 的位置繼續執行，這邊把這些資訊紀錄到 `context` 後再回傳 `_URC_INSTALL_CONTEXT` 讓 `libunwind` 去執行這些工作， `libunwind` 會去考慮不同的平臺把這些值正確設定好的

> `lpad` 是 landing pad 的縮寫，這是從 C++ 的例外處理的流程中出現的名詞，
> 如果這邊是要釋放資源的話就會跳到資源釋放的程式碼去，如果是回到正常流程的話就是到回復正常流程的程式碼去，
> 至於這個位置是需要由編譯器幫忙產生的

到這邊其實已經差不多把 `panic` 實際的處理流程講完了，不過怎麼看都還是少一塊拼圖，下一篇要來看的是編譯器在這個流程中幫了什麼忙
