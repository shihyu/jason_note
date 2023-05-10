## RISC-V 指令集分析

出處：https://ithelp.ithome.com.tw/articles/10257457

有了基本檔案架構後，開始動工指令的部分。RISC-V將指令分成數個子集，其中包括RV32I、RV32E、RV64I、RV128I四套整數指令集，以及約14套擴充指令集，雖然號稱"精簡"，最基本的RV32I指令集也有47條指令，實作的effort也是不小。為了能有的放矢的進行實作，目前打算先以實際編譯出來最常用的指令開始處理。

為了觀察實際上compiler常用的指令，需要先取得RISC-V的[GNU toolchain](https://github.com/riscv/riscv-gnu-toolchain/releases)，由於目前只打算支援riscv32架構，因此使用的是riscv32-elf-ubuntu-20.04-nightly-2021.06.26-nightly.tar.gz這個版本的toolchain。解壓縮後在riscv/bin資料夾下就可以找到gcc、objdump等常用工具。首先撰寫一個最基本的C程式：

```c
int main() {
    return 0;
}
```

使用gcc編譯，並使用odjbump得到完整的assembly：

```bash
riscv/bin/riscv32-unknown-elf-gcc -o main.elf main.c
riscv/bin/riscv32-unknown-elf-objdump -D -M no-aliases main.elf > main.asm
```

觀察入口點`_start`的assembly：

```armasm
00010084 <_start>:
   10084:   00002197            auipc   gp,0x2
   10088:   b5c18193            addi    gp,gp,-1188 # 11be0 <__global_pointer$>
   1008c:   c3418513            addi    a0,gp,-972 # 11814 <completed.1>
   10090:   c5018613            addi    a2,gp,-944 # 11830 <__BSS_END__>
   10094:   8e09                    c.sub   a2,a0
   10096:   4581                    c.li    a1,0
   10098:   2209                    c.jal   1019a <memset>
   1009a:   00000517            auipc   a0,0x0
   1009e:   26650513            addi    a0,a0,614 # 10300 <atexit>
   100a2:   c511                    c.beqz  a0,100ae <_start+0x2a>
   100a4:   00000517            auipc   a0,0x0
   100a8:   26650513            addi    a0,a0,614 # 1030a <__libc_fini_array>
   100ac:   2c91                    c.jal   10300 <atexit>
   100ae:   2049                    c.jal   10130 <__libc_init_array>
   100b0:   4502                    c.lwsp  a0,0(sp)
   100b2:   004c                    c.addi4spn  a1,sp,4
   100b4:   4601                    c.li    a2,0
   100b6:   2881                    c.jal   10106 <main>
   100b8:   a8b9                    c.j 10116 <exit>
```

可以發現除了一般的RV32I外，其中為了降低code size大量使用了`c.`開頭的壓縮指令標準擴充(Standard Extension for Compressed Instructions)，因此也必須實作擴充指令集C。

至此已經有一個明顯的目標，就是將此ELF檔能順利跑完，並且能正確的更新所有的整數register以及PC。為達成此目標，指令實作的順序就以從`_start`開始執行的指令為準。