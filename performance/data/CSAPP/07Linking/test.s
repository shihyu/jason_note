	.file	"test.c"
	.text
	.globl	p1468_f
	.type	p1468_f, @function
p1468_f:
.LFB0:
	.cfi_startproc
	movl	$x.1, %eax
	ret
	.cfi_endproc
.LFE0:
	.size	p1468_f, .-p1468_f
	.globl	p468_g
	.type	p468_g, @function
p468_g:
.LFB1:
	.cfi_startproc
	movl	$x.0, %eax
	ret
	.cfi_endproc
.LFE1:
	.size	p468_g, .-p468_g
	.local	x.0
	.comm	x.0,4,4
	.local	x.1
	.comm	x.1,4,4
	.globl	x
	.bss
	.align 4
	.type	x, @object
	.size	x, 4
x:
	.zero	4
	.ident	"GCC: (GNU) 12.1.0"
	.section	.note.GNU-stack,"",@progbits
