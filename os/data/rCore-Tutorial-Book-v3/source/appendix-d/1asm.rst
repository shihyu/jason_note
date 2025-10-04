RISCV 彙編相關
=========================

如何生成彙編代碼
-------------------------

.. code-block:: console
   
   # 通常辦法，生成的彙編代碼有比較冗餘的信息
   # 生成缺省debug模式的彙編
   $cargo rustc -- --emit asm
   $ls target/debug/deps/<crate_name>-<hash>.s  
   # 生成release模式的彙編
   $cargo rustc --release -- --emit asm
   $ls target/release/deps/<crate_name>-<hash>.s
   # 在rcore-tutorial-v3中的應用的彙編代碼生成舉例
   $cd user   
   $cargo  rustc --release --bin hello_world -- --emit asm
   $find ./target -name "hello_world*.s"

   #生成更加乾淨的彙編代碼
   #基於 cargo-show-asm(https://github.com/pacak/cargo-show-asm)的辦法
   如果沒用安裝這個cargo asm子命令，就安裝它
   $cargo install cargo-show-asm
   #在rcore-tutorial-v3中的應用的彙編代碼生成舉例
   $cd user
   $cargo  asm  --release --bin hello_world

   Compiling user_lib v0.1.0 (/home/chyyuu/thecodes/rCore-Tutorial-v3/user)
    Finished release [optimized + debuginfo] target(s) in 0.10s

        .section .text.main,"ax",@progbits
                .globl  main
                .p2align        1
                .type   main,@function
        main:

                .cfi_sections .debug_frame
                .cfi_startproc
                addi sp, sp, -64
                .cfi_def_cfa_offset 64

                sd ra, 56(sp)
                sd s0, 48(sp)
                .cfi_offset ra, -8
                .cfi_offset s0, -16
                addi s0, sp, 64
                .cfi_def_cfa s0, 0

                auipc a0, %pcrel_hi(.L__unnamed_1)
                addi a0, a0, %pcrel_lo(.LBB0_1)

                sd a0, -64(s0)
                li a0, 1

                sd a0, -56(s0)
                sd zero, -48(s0)

                auipc a0, %pcrel_hi(.L__unnamed_2)
                addi a0, a0, %pcrel_lo(.LBB0_2)

                sd a0, -32(s0)
                sd zero, -24(s0)

                addi a0, s0, -64

                call user_lib::console::print
                li a0, 0
                ld ra, 56(sp)
                ld s0, 48(sp)
                addi sp, sp, 64
                ret


參考信息
-------------------------

- `RISC-V Assembly Programmer's Manual  <https://github.com/riscv/riscv-asm-manual/blob/master/riscv-asm.md>`_ 
- `RISC-V Low-level Test Suits <https://github.com/riscv/riscv-tests>`_
- `CoreMark®-PRO comprehensive, advanced processor benchmark <https://github.com/RISCVERS/coremark-pro>`_ 
- `riscv-tests的使用 <https://stackoverflow.com/questions/39321554/how-do-i-use-the-riscv-tests-suite>`_