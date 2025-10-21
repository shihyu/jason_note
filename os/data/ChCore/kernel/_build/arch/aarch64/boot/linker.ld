




       

ENTRY(_start)

SECTIONS
{
    . = 0x80000;
    img_start = .;
    init : {
        CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/start.S.obj
CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/mmu.c.obj
CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/tools.S.obj
CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/init_c.c.obj
CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/peripherals/uart.c.obj
    }

    . = ALIGN(0x4000);

    init_end = ABSOLUTE(.);

    .text 0xffffff0000000000 + init_end : AT(init_end) {
        *(.text*)
    }

    . = ALIGN(0x10000);
    .data : {
        *(.data*)
    }
    . = ALIGN(0x10000);

    .rodata : {
        *(.rodata*)
    }
    _edata = . - 0xffffff0000000000;

    _bss_start = . - 0xffffff0000000000;
    .bss : {
        *(.bss*)
    }
    _bss_end = . - 0xffffff0000000000;
    . = ALIGN(0x10000);

    img_end = . - 0xffffff0000000000;

    /DISCARD/ : { *(.comment) *(.gnu*) *(.note*) *(.eh_frame*) }
}
