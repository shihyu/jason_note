ptrace
======

這篇要來介紹一個很強大的系統呼叫 `ptrace` 它可以用來中斷別的程式，讀取與寫入別的程式的資料，它的用途基本上就是拿來實作除錯器，當然除錯器並不是隻要能暫停程式與讀寫程式就行了，不過這總是個第一步，因為接下來我想來介紹除錯器怎麼運作的

如果你去看 `ptrace` 的 man page 你會發現長長一串的說明，因為 `ptrace` 所有的功能就只有一個系統呼叫，那就是 `ptrace` ，它的功能我這邊大致上分成三類

1. 設定程式為除錯狀態
2. 中斷與繼續程式的執行
3. 讀寫程式的資料

另外這系列是用 Rust 來當範例，所以接下來的範例程式碼會直接使用 [`nix`][nix] 所提供的 `ptrace` 的包裝，這些包裝函式都定義在 [`nix::sys::ptrace`][nix-ptrace] 之下，雖然也有提供原始的 `ptrace` 介面，不過包裝的函式提供的介面還是比較方便的

[nix]: https://github.com/nix-rust/nix
[nix-ptrace]: https://docs.rs/nix/0.15.0/nix/sys/ptrace/index.html

設定程式為除錯狀態
------------------

你想要除錯一個程式你必須要先把你自己註冊為另一個程式的除錯器，這又分成兩種方式：

- `PTRACE_TRACEME`：
  使用 `PTRACE_TRACEME` 的程式將會成為被除錯的程式，而它的父處理序會理所當然的成為除錯的程式，不論它願不願意，當然如果父處理序沒有處理這種情況，基本上是會出錯的，在 `nix` 中這個功能被包裝為 `traceme()`

  ```rust
  use std::process::Command;
  use nix::sys::ptrace;

  let child = unsafe {
    Command::new("true")
      .pre_exec(|| {
        // pre_exec 可以讓程式碼在 fork 後的子處理序在要執行 exec 前執行
        ptrace::traceme().unwrap();
        Ok(())
      })
      .spawn()
      .unwrap()
  };
  ```

- `PTRACE_ATTACH`：
  這個則是可以讓你把自己註冊為其它程式的除錯器，但畢竟如果可以註冊成為任何程式的除錯器的話就太 OP 了，所以你必須要有某些權限才能這麼做，權限的控制則是在 `/proc/sys/kernel/yama/ptrace_scope` ，如果寫入 0 的話就可以關掉限制
- `PTRACE_DETACH`：
  這個是用來停止除錯用的，呼叫了這個函式後你就不在是指定的程式的除錯器了，程式將可以繼續執行 (或是直接被 kill 掉，這有個設定可以調整)

中斷與繼續程式的執行
--------------------

在你成為另一個程式的除錯器時，系統會在某些情況下幫你暫停程式並通知你，如果你想要接到這個通知，你需要的是 `waitpid` ，正是那個平常用來等待子處理序結束用的系統呼叫，不過事實上它的用途是子處理序的狀態改變時就會收到通知

```rust
use nix::{
  sys::{
    ptrace::traceme,
    signal::Signal,
    wait::{waitpid, WaitStatus},
  },
  unistd::Pid,
};
use std::{os::unix::process::CommandExt, process::Command};

fn main() {
  let child = unsafe {
    Command::new("true")
      .pre_exec(|| {
        traceme().unwrap();
        Ok(())
      })
      .spawn()
      .unwrap()
  };
  match waitpid(Pid::from_raw(child.id() as i32), None).unwrap() {
    WaitStatus::Stopped(_, sig) => {
      // 這邊會是在 exec 時暫停
      assert_eq!(sig, Signal::SIGTRAP);
    }
    _ => (),
  }
}
```

在這之後如果你想讓程式暫停或繼續你就需要其它的 `ptrace` 的 API 了

- `PTRACE_CONT`： 讓程式繼續執行，就像是 `gdb` 中的 continue 一樣
- `PTRACE_SINGLESTEP`： 執行這個指令後在下一個指令暫停
- `PTRACE_SYSCALL`： 這個就比較有趣了，是讓程式在呼叫系統呼叫時暫停，這個東西有沒有想到什麼程式啊，就是 `strace` ，它能印出系統呼叫就是靠這個喔 (外加針對每個系統呼叫的解析呼叫參數的處理)

對了，不知道你有沒有試過用 `strace` 來追蹤 `strace` 本身啊，聽起來很奇怪，不過其實是可以的：

```shell
$ strace strace -o /dev/null true
...
ptrace(PTRACE_SYSCALL, 21759, NULL, SIG_0) = 0
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_TRAPPED, si_pid=21759, si_uid=1000, si_status=SIGTRAP, si_utime=0, si_stime=0} ---
wait4(-1, [{WIFSTOPPED(s) && WSTOPSIG(s) == SIGTRAP | 0x80}], __WALL, NULL) = 21759
ptrace(PTRACE_GETREGSET, 21759, NT_PRSTATUS, [{iov_base=0x56174a4a6660, iov_len=216}]) = 0
write(3, "exit_group(0", 12)            = 12
ptrace(PTRACE_SYSCALL, 21759, NULL, SIG_0) = 0
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_TRAPPED, si_pid=21759, si_uid=1000, si_status=SIGTRAP, si_utime=0, si_stime=0} ---
wait4(-1, [{WIFSTOPPED(s) && WSTOPSIG(s) == SIGTRAP} | PTRACE_EVENT_EXIT << 16], __WALL, NULL) = 21759
write(3, ")                           = ?\n", 32) = 32
...
```

這邊讓第二個 `strace` 輸出到 `/dev/null` 這樣就不會有另一個輸出的幹擾了，另外這邊可以看到 `strace` 呼叫了 `PTRACE_SYSCALL` 與 `PTRACE_GETREGSET`

讀寫程式的資料
--------------

程式的資料大致上又分成兩種，一個是在記憶體中的資料，這包括堆疊，程式的變數， heap 上的資料等等的，另外還有個資料就是暫存器中的資料，比如在函式呼叫時就因為參數會使用暫存器傳遞而需要去讀取，事實上還有一個東西是程式收到的 signal 也有額外的資訊可以讀取，不過這邊先帶過吧

`PTRACE_PEEKDATA`： 這可以用來讀取另一個處理序的記憶體，但有趣的是它讀取的大小固定是 `sizeof(long)` 並且會以 `ptrace` 的回傳值的方式傳回來，老實說這用起來不太方便，另外有個 API 是 `process_vm_readv` 這個就能一次讀取比較多的資料了
`PTRACE_GETREGS`： 可以用來取得暫存器的值

strace
------

這邊我們試著做一個簡單版的 `strace` 吧，主要就是透過 `PTRACE_SYSCALL` 讓程式在呼叫系統呼叫時暫停，再用 `PTRACE_GETREGS` 取得呼叫的系統呼叫的編號：

> 完整的程式碼在 https://github.com/DanSnow/ironman-2019/tree/master/strace

```rust
let mut enter = true;
while let Ok(status) = waitpid(pid, None) {
  match status {
    // 在這之前有使用 ptrace::setoptions(pid, ptrace::Options::PTRACE_O_TRACESYSGOOD);
    // 這會讓程式是因為 syscall 暫停時在狀態中多設定一個 bit ，而 nix 就有把這部份區別出來
    WaitStatus::PtraceSyscall(_) => {
      // 取得暫存器
      let regs = ptrace::getregs(pid).unwrap();
      // 如果暫停在系統呼叫的話程式會被暫停兩次，一次是剛呼叫後，一次是呼叫要結束時
      if enter {
        match regs.orig_rax {
          // 這邊用 `orig_rax` 來判斷呼叫的系統呼叫是哪一個，我只有寫一些常用的系統呼叫而已
          0 => print!("read(...)"),
          // ... 中間省略
          _ => print!("{}(...)", regs.orig_rax),
        }
      } else {
        // 這邊是讀出系統呼叫的回傳值
        println!(" = {}", regs.rax);
      }
      enter = !enter;
      // 讓 ptrace 中斷在下一次的系統呼叫 (開始或結束的位置)
      ptrace::syscall(pid).unwrap();
    }
    _ => (),
  }
}
```


