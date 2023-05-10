load elf
========

> 這次的程式碼在 https://github.com/DanSnow/ironman-2019/tree/master/elf-load

之前說過要用 `goblin` 來做點有趣的事，現在先來試一個吧，我們自己來想辦法載入執行檔執行，在之前我們已經介紹過執行檔的格式 - ELF 了，如果忘記的話可以回去複習喔

> 老實說文章的順序規劃上出了點問題，我也沒預料到 `panic` 或稱為例外處理會寫到三篇，在這邊說聲抱歉

這次要載入的執行檔只是個簡單的 `Hello world`

```c
#include <stdio.h>

int main() {
  puts("Hello world");
  return 0;
}
```

總之我們先把執行檔的內容讀進來，然後用 `goblin` 來解析它的內容吧：

```rust
let content = fs::read(env::args().nth(1).unwrap())?;
let elf = Elf::parse(&content).unwrap();
```

不過在載入前我們會需要一塊空間，因為要的空間不小，我們直接用 `mmap` 這個系統呼叫幫我們分塊一塊大的記憶體，這邊我把 `mmap` 用 struct 做了點簡單的包裝，讓它能在離開作用域時把空間釋放掉，並實作 `Deref` ，另外這邊用的是 `nix` 包裝過的 API ，它把 C 的型態都用 Rust 的物件再做包裝過，可以減少呼叫時傳錯參數之類的錯誤：

```rust
struct MMap {
  ptr: *mut u8,
  size: usize,
}

impl MMap {
  unsafe fn new(size: usize, protect: ProtFlags, flag: MapFlags) -> Self {
    let ptr = mmap(ptr::null_mut(), size, protect, flag, 0, 0).unwrap() as *mut u8;
    if ptr == ptr::null_mut() {
      panic!("mmap fail");
    }
    MMap { ptr, size }
  }

  unsafe fn new_zeroed(size: usize, protect: ProtFlags, flag: MapFlags) -> Self {
    let mmap = MMap::new(size, protect, flag);
    ptr::write_bytes(mmap.ptr, 0, size);
    mmap
  }
}

// 實作 Deref 與 DerefMut

impl Drop for MMap {
  fn drop(&mut self) {
    unsafe {
      munmap(self.ptr as *mut c_void, self.size).unwrap();
    }
  }
}
```

然後實際的分配記憶體，這邊先簡單的只分配固定大小的記憶體

```rust
let mut page = unsafe {
  MMap::new_zeroed(
    SIZE,
    ProtFlags::PROT_READ | ProtFlags::PROT_WRITE | ProtFlags::PROT_EXEC,
    MapFlags::MAP_PRIVATE | MapFlags::MAP_ANONYMOUS,
  )
};
```

在介紹 ELF 時說過，載入 ELF 檔最主要的就是讀 program headers 這個部份，如果我們要手動載入的話第一步就是從這個表找出 `PT_LOAD` 類型的區段然後把它載入到記憶體中，並設定好它的屬性

```rust
for header in elf.program_headers.iter() {
  // 找到 PT_LOAD
  if header.p_type == PT_LOAD {
    assert!(header.p_memsz >= header.p_filesz);
    if header.p_filesz == 0 {
      continue;
    }
    unsafe {
      // 載入到指定的記憶體位置
      let dst = page.as_mut_ptr().add(header.p_vaddr as usize);
      ptr::copy_nonoverlapping(
        content.as_ptr().add(header.p_offset as usize),
        dst,
        header.p_filesz as usize,
      );

      // 如果不可寫的話
      if header.p_flags & PF_W == 0 {
        // 讓這段變唯讀
        mprotect(
          dst as *mut c_void,
          header.p_memsz as usize,
          ProtFlags::PROT_READ,
        )
        .unwrap();
      }
      // 如果可執行
      if header.p_flags & PF_X != 0 {
        // 設定為可執行
        mprotect(
          dst as *mut c_void,
          header.p_memsz as usize,
          ProtFlags::PROT_EXEC,
        )
        .unwrap();
      }
    }
  }
}
```

其中的 `p_vaddr` 是那個區段預期被載入的相對位置，所以只要加上我們分配好的開始位置就行了

接著我這邊用了一個比較作弊的方法，我直接從符號表找出 `main` 函式的位置，然後轉成可以呼叫的函式

```rust
let entry = elf
  .syms
  .iter()
  .find(|sym| elf.strtab.get(sym.st_name).unwrap().unwrap() == "main")
  .unwrap();
let entry: unsafe extern "C" fn(i32, *mut *mut u8, *mut *mut u8) -> i32 =
  unsafe { mem::transmute(page.as_ptr().add(entry.st_value as usize)) };
```

這樣的作法有個問題是如果符號表被去掉的話這個方式就沒辦法運作了，不過預設是會有符號表的，除非是用 `strip` 去除掉，對了，這邊有個有趣的東西，在執行檔裡的資訊很多都像這樣，字串的部份與其它的表格是分開來存的，一個原因是為了節省空間

最後一步是要做重定址，我們要把使用到的外部函式的位置填進去，這邊用到的就只有 `puts`

```rust
// 取得重定址表的資料
for reloc in elf.pltrelocs.iter() {
  // 取得符號
  let sym = elf.dynsyms.get(reloc.r_sym).unwrap();
  // 取得符號的名稱
  let name = elf.dynstrtab.get(sym.st_name).unwrap().unwrap();
  match reloc.r_type {
    // 這邊基本上只會有這兩種類型
    R_X86_64_GLOB_DAT | R_X86_64_JUMP_SLOT => {
      let addr = resolve(name);
      let addr = addr.to_le_bytes();
      unsafe {
        ptr::copy_nonoverlapping(
          addr.as_ptr(),
          page.as_mut_ptr().add(reloc.r_offset as usize),
          mem::size_of::<u64>(),
        );
      }
    }
    _ => {
      panic!("unable to handle {}", reloc.r_type);
    }
  }
}
```

`resolve` 的函式實際上只有找 `libc` 中的函式而已，正常應該是要把有用到的動態函式庫都載入，並照順序都找一遍才對的

```rust
static LIB: Lazy<Library> =
  Lazy::new(|| Library::open("/lib/x86_64-linux-gnu/libc.so.6").unwrap());
unsafe { LIB.symbol(name).unwrap() }
```

把完整的程式跑起來的話應該就可以看到我們的 `Hello, world` 顯示出來了
