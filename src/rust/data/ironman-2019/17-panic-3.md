panic 3
=======

這篇要來看在 `panic` ，或是例外處理的過程中，編譯器幫了什麼忙，上一篇程式碼的部份最後還剩下 `find_eh_action` 的內容沒講，因為它是在讀由編譯器產生的內容來判斷這段程式能不能處理拋出來的例外的，我們繼續回到 [`libpanic_unwind/gcc.rs`][libpanic_unwind-gcc] 看看 `find_eh_action` 裡做了什麼吧：

[libpanic_unwind-gcc]: https://github.com/rust-lang/rust/blob/master/src/libpanic_unwind/gcc.rs

```rust
unsafe fn find_eh_action(context: *mut uw::_Unwind_Context)
    -> Result<EHAction, ()>
{
  let lsda = uw::_Unwind_GetLanguageSpecificData(context) as *const u8;
  let mut ip_before_instr: c_int = 0;
  let ip = uw::_Unwind_GetIPInfo(context, &mut ip_before_instr);
  let eh_context = EHContext {
    ip: if ip_before_instr != 0 { ip } else { ip - 1 },
    func_start: uw::_Unwind_GetRegionStart(context),
    get_text_start: &|| uw::_Unwind_GetTextRelBase(context),
    get_data_start: &|| uw::_Unwind_GetDataRelBase(context),
  };
  eh::find_eh_action(lsda, &eh_context)
}
```

這段程式碼主要都是在從 `libunwind` 取得相關的資料，並把這些資料再傳給 `eh::find_eh_action` 來處理，其中一個很重要的就是 `_Unwind_GetLanguageSpecificData` 所取得的資料，它是由編譯器產生的資料，這個資料只要編成組語就看的到了，我們用個簡單的程式來看看吧：

```rust
struct NeedDrop;

impl Drop for NeedDrop {
  fn drop(&mut self) {}
}

fn main() {
  // 需要一個必須要 drop 的資料，不然 unwind 時因為沒有資源要釋放，是會直接跳過的
  let _need_drop = NeedDrop;
  panic!("panic");
}
```

它產生的組語是：

```asm
_ZN4demo4main17h91ba606413987129E:
.Lfunc_begin7:
  .cfi_startproc
  .cfi_personality 155, DW.ref.rust_eh_personality
  .cfi_lsda 27, .Lexception7
  subq  $24, %rsp
  .cfi_def_cfa_offset 32
.Ltmp31:
  leaq  .L__unnamed_10(%rip), %rdi
  leaq  .L__unnamed_11(%rip), %rdx
  movl  $5, %esi
  callq _ZN3std9panicking11begin_panic17h6cbcf59c0746dd03E
.Ltmp32:
  jmp .LBB74_3
.LBB74_1:
  movq  8(%rsp), %rdi
  callq _Unwind_Resume@PLT
  ud2
.LBB74_2:
  movq  %rsp, %rdi
  callq _ZN4core3ptr18real_drop_in_place17h8897b5f76aed2678E
  jmp .LBB74_1
.LBB74_3:
  ud2
.LBB74_4:
.Ltmp33:
  movq  %rax, 8(%rsp)
  movl  %edx, 16(%rsp)
  jmp .LBB74_2
.Lfunc_end74:
  .size _ZN4demo4main17h91ba606413987129E, .Lfunc_end74-_ZN4demo4main17h91ba606413987129E
  .cfi_endproc
  .section  .gcc_except_table,"a",@progbits
  .p2align  2
GCC_except_table74:
.Lexception7:
  .byte 255
  .byte 255
  .byte 1
  .uleb128 .Lcst_end7-.Lcst_begin7
.Lcst_begin7:
  .uleb128 .Ltmp31-.Lfunc_begin7
  .uleb128 .Ltmp32-.Ltmp31
  .uleb128 .Ltmp33-.Lfunc_begin7
  .byte 0
  .uleb128 .Ltmp32-.Lfunc_begin7
  .uleb128 .Lfunc_end74-.Ltmp32
  .byte 0
  .byte 0
.Lcst_end7:
```

有點長，不過在開頭應該可以看到一個 `.cfi_lsda` 其中的 `lsda` 正好在上面的 `find_eh_action` 中也有出現過，那個是 language specific data 的位置，而編譯器產生並存在裡面的資料就在 `.Lexception7` 中，但這段資料是什麼意思呢？我們搭配著位在 [`libpanic_unwind/dwarf/eh.rs`][libpanic_unwind-eh] 的 `find_eh_action` 的程式碼可能會比較容易看的懂，我們先看第一段程式碼

> 因為關於這部份的資料其實真的很少，如果想看的話這邊有份應該是 C++ 的 exception 實作的[標準文件][cpp-abi]，裡面的 LDSA 的內容其實跟 Rust 是一樣的

[libpanic_unwind-eh]: https://github.com/rust-lang/rust/blob/master/src/libpanic_unwind/dwarf/eh.rs
[cpp-abi]: https://itanium-cxx-abi.github.io/cxx-abi/exceptions.pdf

```rust
 if lsda.is_null() {
  return Ok(EHAction::None)
 }

 let func_start = context.func_start;
 let mut reader = DwarfReader::new(lsda);

 let start_encoding = reader.read::<u8>();
 // base address for landing pad offsets
 let lpad_base = if start_encoding != DW_EH_PE_omit {
  read_encoded_pointer(&mut reader, context, start_encoding)?
 } else {
  func_start
 };

 let ttype_encoding = reader.read::<u8>();
 if ttype_encoding != DW_EH_PE_omit {
  // Rust doesn't analyze exception types, so we don't care about the type table
  reader.read_uleb128();
 }

 let call_site_encoding = reader.read::<u8>();
 let call_site_table_length = reader.read_uleb128();
 let action_table = reader.ptr.offset(call_site_table_length as isize);
 let ip = context.ip;
```

這段程式碼是在讀 LSDA 的前四個值，也就是從 `.Lexception7` 到 `.Lcst_begin7` 中間的內容，第一個 `.byte` 是 landing pad 的位置的編碼方式，這邊的值是代表省略的 255 (16 進位的 0xff) ，所以就用 `_Unwind_GetRegionStart` 回傳的位置了，第二個則是描述例外的型態的編碼方式，因為 Rust 根本就沒有例外的型態，所以這邊的都是省略的狀態，不過如果有的話還是要把它讀出來，不然會對接下來造成影響，再來是記錄會發生 `panic` 的位置，稱做 call site table 的表格，這邊先存的是它們的編碼方式與長度，長度用的是 [`leb128`][leb128] 的編碼方式存的

[leb128]: https://en.wikipedia.org/wiki/LEB128

第二段則是在讀取 call site table 的資料，這段程式碼外還包了一層 if 不過那是在判斷是不是用 SjLj ，中間的程式碼如下：

```rust
while reader.ptr < action_table {
  let cs_start = read_encoded_pointer(&mut reader, context, call_site_encoding)?;
  let cs_len = read_encoded_pointer(&mut reader, context, call_site_encoding)?;
  let cs_lpad = read_encoded_pointer(&mut reader, context, call_site_encoding)?;
  let cs_action = reader.read_uleb128();
  // Callsite table is sorted by cs_start, so if we've passed the ip, we
  // may stop searching.
  if ip < func_start + cs_start {
    break;
  }
  if ip < func_start + cs_start + cs_len {
    if cs_lpad == 0 {
      return Ok(EHAction::None)
    } else {
      let lpad = lpad_base + cs_lpad;
      return Ok(interpret_cs_action(cs_action, lpad))
    }
  }
}
// Ip is not present in the table.  This should not happen... but it does: issue #35011.
// So rather than returning EHAction::Terminate, we do this.
Ok(EHAction::None)
```

表格有四個欄位，起始位置、長度、 landing pad 的位置，以及一個代表這個是不是 catch 的 byte ，這邊就是判斷是從哪邊發生 `panic` 的，並看是不是需要跳到 landing pad ，到這邊應該大致能看懂那個 `.Lexception7` 的表格中的資料了，另外在組語中有個 `_Unwind_Resume@PLT` 的呼叫，那個也是由編譯器加進去的，為了在清理完資源後能繼續進行 unwind 的過程

在 Rust 中能接住例外的函式只有 `std::panic::catch_unwind` 內部呼叫的 `__rust_maybe_catch_panic` 而已了，所以基本上你是沒辦法在 Rust 產生的組語中看到代表能不能接住例外的那個欄位為 `1` 的時候，如果你想看的話需要用到 Rust nightly 的功能

```rust
#![feature(core_intrinsics)]
use std::{intrinsics, ptr};

struct NeedDrop;

impl Drop for NeedDrop {
    fn drop(&mut self) {}
}

fn foo(_: *mut u8) {
  let _need_drop = NeedDrop;
  panic!("panic");
}

fn main() {
  unsafe {
    let mut payload = ptr::null_mut::<u8>();
    // 需要使用 intrinsics::#try 才有辦法接住例外
    let _ = intrinsics::r#try(foo, ptr::null_mut(), &mut payload as *mut _ as *mut _);
  }
}
```

你可以試著自己編譯上面那段程式並觀察產生的組語，應該是可以在 LDSA 中看到那個欄位變成了 `1` ，並且沒有在程式碼中加入 `_Unwind_Resume@PLT` 了

還真沒想到一個 `panic` 背後實際上是牽涉到這麼多東西呢？不過經過這幾篇，應該認識到不只 `panic` 還有 C++ 的例外是怎麼運作了吧
