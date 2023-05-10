unwind & backtrace
==================

是說在之前介紹到的 `libunwind` ，因為它有讀取 `frame` 資訊的功能，實際上還有個很有用的用途，顯示 backtrace ，另外在 Rust 發生 `panic` 時不是也有 `backtrace` 可以看嗎？只要呼叫時加上 `RUST_BACKTRACE=1` 就可以看到了，像這樣：

```shell
$ RUST_BACKTRACE=1 ./demo
thread 'main' panicked at 'panic', demo.rs:2:5
stack backtrace:
   0: backtrace::backtrace::libunwind::trace
             at /cargo/registry/src/github.com-1ecc6299db9ec823/backtrace-0.3.37/src/backtrace/libunwind.rs:88
   1: backtrace::backtrace::trace_unsynchronized
             at /cargo/registry/src/github.com-1ecc6299db9ec823/backtrace-0.3.37/src/backtrace/mod.rs:66
   2: std::sys_common::backtrace::_print_fmt
             at src/libstd/sys_common/backtrace.rs:76
   3: <std::sys_common::backtrace::_print::DisplayBacktrace as core::fmt::Display>::fmt
             at src/libstd/sys_common/backtrace.rs:60
   4: core::fmt::write
             at src/libcore/fmt/mod.rs:1028
   5: std::io::Write::write_fmt
             at src/libstd/io/mod.rs:1412
   6: std::sys_common::backtrace::_print
             at src/libstd/sys_common/backtrace.rs:64
   7: std::sys_common::backtrace::print
             at src/libstd/sys_common/backtrace.rs:49
   8: std::panicking::default_hook::{{closure}}
             at src/libstd/panicking.rs:196
   9: std::panicking::default_hook
             at src/libstd/panicking.rs:210
  10: std::panicking::rust_panic_with_hook
             at src/libstd/panicking.rs:473
  11: std::panicking::begin_panic
  12: demo::main
  13: std::rt::lang_start::{{closure}}
  14: std::rt::lang_start_internal::{{closure}}
             at src/libstd/rt.rs:49
  15: std::panicking::try::do_call
             at src/libstd/panicking.rs:292
  16: __rust_maybe_catch_panic
             at src/libpanic_unwind/lib.rs:80
  17: std::panicking::try
             at src/libstd/panicking.rs:271
  18: std::panic::catch_unwind
             at src/libstd/panic.rs:394
  19: std::rt::lang_start_internal
             at src/libstd/rt.rs:48
  20: std::rt::lang_start
  21: main
  22: __libc_start_main
  23: _start
```

其實在上面的 backtrace 中就已經出現 `libunwind` 了，不過我們還是要來實際試試看，自己用 `libunwind` 顯示 backtrace 吧，正好 Rust 有個 crate 叫 [`unwind`][unwind] 有提供 `libunwind` 的包裝，文件中也有附範例，就來試試吧：

[unwind]: https://docs.rs/unwind/0.2.0/unwind/index.html

```rust
use unwind::{Cursor, RegNum};

fn main() {
    Cursor::local(|mut cursor| {
        loop {
            let ip = cursor.register(RegNum::IP)?;

            match (cursor.procedure_info(), cursor.procedure_name()) {
                (Ok(ref info), Ok(ref name)) if ip == info.start_ip() + name.offset() => {
                    println!(
                        "{:#016x} - {} ({:#016x}) + {:#x}",
                        ip,
                        name.name(),
                        info.start_ip(),
                        name.offset()
                    );
                }
                _ => println!("{:#016x} - ????", ip),
            }

            if !cursor.step()? {
                break;
            }
        }
        Ok(())
    })
    .unwrap();
}
```

但它輸出的是：

```plain
0x0055a105c131b6 - _ZN6unwind6Cursor5local17ha597244bc85e9decE (0x0055a105c13170) + 0x46
0x0055a105c13d59 - _ZN14backtrace_test4main17hdb114b59026e36b3E (0x0055a105c13d50) + 0x9
0x0055a105c13f40 - _ZN3std2rt10lang_start28_$u7b$$u7b$closure$u7d$$u7d$17hceb03d45505ee7d3E (0x0055a105c13f30) + 0x10
0x0055a105c230c3 - _ZN3std9panicking3try7do_call17hec516f7d20f460a8E (0x0055a105c230b0) + 0x13
0x0055a105c2488a - __rust_maybe_catch_panic (0x0055a105c24870) + 0x1a
0x0055a105c23b3d - _ZN3std2rt19lang_start_internal17h57288edab9fc6490E (0x0055a105c237e0) + 0x35d
0x0055a105c13f19 - _ZN3std2rt10lang_start17h1cb42ec6dca06f3dE (0x0055a105c13ed0) + 0x49
0x0055a105c13daa - main (0x0055a105c13d80) + 0x2a
0x007fda73677b97 - __libc_start_main (0x007fda73677ab0) + 0xe7
0x0055a105c1307a - _start (0x0055a105c13050) + 0x2a
```

天啊，這什麼東西啊，跟 Rust `panic` 時顯示的差好多啊，首先那個像亂碼一樣的名字是怎麼回事呢？還有，有沒有辦法拿到位在哪個檔案與它的行數？

首先那個名字是因為 mangle 的原故， Rust 或是像 C++ 這邊的語言，因為支援 mod 或是 C++ 的 namespace 而要避免在不同 mod 下的函式名稱重覆，所以會把函式名稱以一定的規則加工，變成像上面這樣的名稱，這時候可以用在第 8 篇提過的 c++filt 將名稱還原，還原後會變成像下面這樣

```plain
0x005584f38291b6 - unwind::Cursor::local (0x005584f3829170) + 0x46
0x005584f3829d59 - backtrace_test::main (0x005584f3829d50) + 0x9
0x005584f3829f40 - std::rt::lang_start::{{closure}} (0x005584f3829f30) + 0x10
0x005584f38390c3 - std::panicking::try::do_call (0x005584f38390b0) + 0x13
0x005584f383a88a - __rust_maybe_catch_panic (0x005584f383a870) + 0x1a
0x005584f3839b3d - std::rt::lang_start_internal (0x005584f38397e0) + 0x35d
0x005584f3829f19 - std::rt::lang_start (0x005584f3829ed0) + 0x49
0x005584f3829daa - main (0x005584f3829d80) + 0x2a
0x007f000b64eb97 - __libc_start_main (0x007f000b64eab0) + 0xe7
0x005584f382907a - _start (0x005584f3829050) + 0x2a
```

另外這其實也可以在程式中解決，有個叫 [`rustc-demangle`][rustc-demangle] 的 crate 可以用，不過這晚點再說，先來解決沒有檔名與行號的問題吧，說來 Linux 下有個程式叫 `addr2line` 能讀取 debug 的資訊，從位置轉換回檔名與行號，但它要的是跟 `.text` 段相對的偏移位置，為了要拿到這個位置，我是先透過 `objdump -tC` 取得函式的位置，再加上上面取得的偏移位置來取得的，比如上面那個 `backtrace_test::main` 用 objdump 取得的位置是 `0x5d50` 再加上 `0x9` 得到 `0x5d59` 拿去給 `addr2line` 就能得到以下輸出

[rustc-demangle]: https://github.com/alexcrichton/rustc-demangle

```shell
$ addr2line -e target/debug/backtrace-test 5d59
src/main.rs:4
```

如果有更好的方法歡迎留言跟我說，然後這樣做實在太麻煩了，於是有另一個函式庫把這些功能也包裝了起來叫 `libbacktrace` 而 Rust 也有個包裝的 crate 把這些工作都做好了：

```rust
use backtrace::Backtrace;

fn main() {
    let backtrace = Backtrace::new();
    println!("{:?}", backtrace);
}
```

執行後會得到

```plain
stack backtrace:
   0: backtrace_test::main
             at src/main.rs:4
   1: std::rt::lang_start::{{closure}}
             at /rustc/084beb83e0e87d673d5fabc844d28e8e8ae2ab4c/src/libstd/rt.rs:64
   2: std::rt::lang_start_internal::{{closure}}
             at src/libstd/rt.rs:49
      std::panicking::try::do_call
             at src/libstd/panicking.rs:292
   3: __rust_maybe_catch_panic
             at src/libpanic_unwind/lib.rs:80
   4: std::panicking::try
             at src/libstd/panicking.rs:271
      std::panic::catch_unwind
             at src/libstd/panic.rs:394
      std::rt::lang_start_internal
             at src/libstd/rt.rs:48
   5: std::rt::lang_start
             at /rustc/084beb83e0e87d673d5fabc844d28e8e8ae2ab4c/src/libstd/rt.rs:64
   6: main
   7: __libc_start_main
   8: _start
```

看來平常還是直接用 `backtrace` 就好了，會需要直接利用到 `libunwind` 的機會我想應該不多吧
