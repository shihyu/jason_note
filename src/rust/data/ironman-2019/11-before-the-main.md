Before the `main`
=================

我們的 `main` 真的是程式一開始執行的點嗎？還記得在 `gdb` 中看程式是怎麼執行過來的指令 `bt` 嗎，我們用 `gdb` 把中斷點設在 `main` 函式，在執行起來後用 `bt` 來看看：

```plain
#0  0x0000555555557e80 in demo::main ()
#1  0x0000555555557f03 in std::rt::lang_start::{{closure}} ()
#2  0x000055555555e4d3 in std::rt::lang_start_internal::{{closure}} () at src/libstd/rt.rs:49
#3  std::panicking::try::do_call () at src/libstd/panicking.rs:292
#4  0x000055555555fc9a in __rust_maybe_catch_panic () at src/libpanic_unwind/lib.rs:80
#5  0x000055555555ef4d in std::panicking::try () at src/libstd/panicking.rs:271
#6  std::panic::catch_unwind () at src/libstd/panic.rs:394
#7  std::rt::lang_start_internal () at src/libstd/rt.rs:48
#8  0x0000555555557ee8 in std::rt::lang_start ()
#9  0x0000555555557eab in main ()
```

看來…，在這之前的東西還真不少啊，而且又有另一個 `main`，這邊先來看看 C 語言的 `main` 前面又有什麼好了，用同樣的方法來看看：

```plain
#0  main () at c.c:1
```

所以 C 的 `main` 就真的是程式的進入點嗎？我們先輸入這個指令改一下 `gdb` 的設定 `set backtrace past-main on` 再輸入一次 `bt` ：

```plain
#0  main () at c.c:1
#1  0x00007ffff77feb97 in __libc_start_main (main=0x5555555545fa <main>, argc=1, argv=0x7fffffffc0c8, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, stack_end=0x7fffffffc0b8) at ../csu/libc-start.c:310
#2  0x000055555555451a in _start ()
```

怎麼又多出來個東西來了…，預設 `gdb` 會把在 `main` 之前的東西隱藏起來了，上面的 Rust 的範例其實也有這兩個，所以問題就來了，這些在 `main` 執行前執行的東西又是什麼

先從 Rust 的來看吧，因為其實有程式碼，在 [`libstd/rt.rs`][std-rt]，在檔案的開頭其實就說明瞭，這個檔案是為了要提供 `backtrace` 之類的支援而存在的，同時它也把從指令列傳進來的 argc 與 argv 存到某個地方，以便我們之後用 `std::env::args` 來取用

[std-rt]: https://github.com/rust-lang/rust/blob/master/src/libstd/rt.rs

所以具體來說它做了什麼，讓我們一行一行看吧，這邊都假設在 linux 下的環境執行，意思是如果有跟平臺有關的程式碼，我只會看 linux 版本的

```rust
fn lang_start_internal(main: &(dyn Fn() -> i32 + Sync + crate::panic::RefUnwindSafe),
  argc: isize, argv: *const *const u8) -> isize {
  use crate::panic;
  use crate::sys;
  use crate::sys_common;
  use crate::sys_common::thread_info;
  use crate::thread::Thread;

  sys::init();

  unsafe {
    let main_guard = sys::thread::guard::init();
    sys::stack_overflow::init();

    // Next, set up the current Thread with the guard information we just
    // created. Note that this isn't necessary in general for new threads,
    // but we just do this to name the main thread and to give it correct
    // info about the stack bounds.
    let thread = Thread::new(Some("main".to_owned()));
    thread_info::set(main_guard, thread);

    // Store our args if necessary in a squirreled away location
    sys::args::init(argc, argv);

    // Let's run some code!
    #[cfg(feature = "backtrace")]
    let exit_code = panic::catch_unwind(|| {
      sys_common::backtrace::__rust_begin_short_backtrace(move || main())
    });
    #[cfg(not(feature = "backtrace"))]
    let exit_code = panic::catch_unwind(move || main());

    sys_common::cleanup();
    exit_code.unwrap_or(101) as isize
  }
}
```

第一行 `sys::init()` 馬上就跟平臺有關了，這個函式位於 [`libstd/sys/unix/mod.rs`][sys-mod]，其實它做的事很簡單，就只是忽略 `SIGPIPE` 而已：

[sys-mod]: https://github.com/rust-lang/rust/blob/master/src/libstd/sys/unix/mod.rs

```rust
#[cfg(not(test))]
pub fn init() {
    // ...
    unsafe {
        reset_sigpipe();
    }

    // ...
    unsafe fn reset_sigpipe() {
        assert!(signal(libc::SIGPIPE, libc::SIG_IGN) != libc::SIG_ERR);
    }
    // ...
}
```

`SIGPIPE` 是當你在 shell 將一個指令的輸出 pipe 到另一個指令時，如果接收輸出的程式提早結束的話，則前一個程式就會收到 `SIGPIPE`

再來的 `main_guard` 則是在 [`libstd/sys/unix/thread.rs`][sys-thread]：

[sys-thread]: https://github.com/rust-lang/rust/blob/master/src/libstd/sys/unix/thread.rs

```rust
pub unsafe fn init() -> Option<Guard> {
  PAGE_SIZE = os::page_size();

  let stackaddr = get_stack_start_aligned()?;

  if cfg!(target_os = "linux") {
    // ...
    let stackaddr = stackaddr as usize;
    Some(stackaddr - PAGE_SIZE..stackaddr)
  } else {
    // ...
  }
}
```

看來是回傳 `stack` 的前一個分頁的範圍

再來是 `sys::stack_overflow::init()` ，這則在 [`libstd/sys/unix/stack_overflow.rs`][sys-stackoverflow]，這個函式是註冊 signal 的處理器來顯示 stack overflow 的訊息：

[sys-stackoverflow]: https://github.com/rust-lang/rust/blob/master/src/libstd/sys/unix/stack_overflow.rs

```rust
pub unsafe fn init() {
  let mut action: sigaction = mem::zeroed();
  action.sa_flags = SA_SIGINFO | SA_ONSTACK;
  action.sa_sigaction = signal_handler as sighandler_t;
  sigaction(SIGSEGV, &action, ptr::null_mut());
  sigaction(SIGBUS, &action, ptr::null_mut());

  let handler = make_handler();
  MAIN_ALTSTACK = handler._data;
  mem::forget(handler);
}
```

如果想到這個東西印出的訊息只要無窮遞迴呼叫某個函式就行了

接下來兩行是幫目前主要的執行緒設定名字什麼的，另外 stack 的前一個分頁的資訊也會存起來：

```rust
let thread = Thread::new(Some("main".to_owned()));
thread_info::set(main_guard, thread);
```

再接著的 `sys::args::init(argc, argv);` 存 `argv` ，看了這邊的程式碼才知道，原來每次存取 `argv` 的時候 Rust 都會把內部存的 `argv` 完整的複製一份，看來下次應該要避免重覆的使用 `env::args()` 了

終於到達呼叫我們的 `main` 函式的地方了，不過這邊的 `main` 外又包了一層 `catch_unwind` ，這是為了捕捉 `panic` 時的 `unwind` ，它會一路往上看有沒有需要 drop 的物件，然後在 `catch_unwind` 的地方停下來，但如果讓程式繼續 `unwind` 下去會發生未定義行為，所以要讓它在這邊停下來，同時這邊也會紀錄有沒有發生 `panic` 來決定接下來要不要回傳錯誤代碼給系統

最後做些收尾的工作，把上面提到的設定的東西回復原狀，接著回傳離開的代碼，可以看到最後一行是 `exit_code.unwrap_or(101)` 就是當發生 `panic` 時回傳 101 ，你可以試看看，是不是程式最後 `panic` 了就是回傳 101

沒到想 `main` 前其實做了不少工作啊，但這其實還不是全部，下一篇來談談比這更加上層的程式碼
