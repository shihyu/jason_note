	.file	"test.c"
	.text
	.globl	p343_twiddle1
	.type	p343_twiddle1, @function
p343_twiddle1:
.LFB0:
	.cfi_startproc
	movq	(%rsi), %rax
	addq	(%rdi), %rax
	movq	%rax, (%rdi)
	addq	(%rsi), %rax
	movq	%rax, (%rdi)
	ret
	.cfi_endproc
.LFE0:
	.size	p343_twiddle1, .-p343_twiddle1
	.globl	p343_twiddle2
	.type	p343_twiddle2, @function
p343_twiddle2:
.LFB1:
	.cfi_startproc
	movq	(%rsi), %rax
	addq	%rax, %rax
	addq	%rax, (%rdi)
	ret
	.cfi_endproc
.LFE1:
	.size	p343_twiddle2, .-p343_twiddle2
	.globl	p343_func1
	.type	p343_func1, @function
p343_func1:
.LFB2:
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	movl	$0, %eax
	call	p343_f
	movq	%rax, %rbx
	movl	$0, %eax
	call	p343_f
	addq	%rax, %rbx
	movl	$0, %eax
	call	p343_f
	addq	%rax, %rbx
	movl	$0, %eax
	call	p343_f
	addq	%rbx, %rax
	popq	%rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE2:
	.size	p343_func1, .-p343_func1
	.globl	p343_func2
	.type	p343_func2, @function
p343_func2:
.LFB3:
	.cfi_startproc
	subq	$8, %rsp
	.cfi_def_cfa_offset 16
	movl	$0, %eax
	call	p343_f
	salq	$2, %rax
	addq	$8, %rsp
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE3:
	.size	p343_func2, .-p343_func2
	.globl	p355_f1
	.type	p355_f1, @function
p355_f1:
.LFB4:
	.cfi_startproc
	testl	%edx, %edx
	jle	.L7
	movq	%rsi, %rax
	movslq	%edx, %rdx
	leaq	(%rsi,%rdx,4), %rcx
.L9:
	movl	(%rdi), %edx
	imull	(%rax), %edx
	movl	%edx, (%rdi)
	addq	$4, %rax
	cmpq	%rcx, %rax
	jne	.L9
.L7:
	ret
	.cfi_endproc
.LFE4:
	.size	p355_f1, .-p355_f1
	.globl	p355_f2
	.type	p355_f2, @function
p355_f2:
.LFB5:
	.cfi_startproc
	movl	(%rdi), %ecx
	testl	%edx, %edx
	jle	.L12
	movq	%rsi, %rax
	movslq	%edx, %rdx
	leaq	(%rsi,%rdx,4), %rdx
.L13:
	imull	(%rax), %ecx
	addq	$4, %rax
	cmpq	%rdx, %rax
	jne	.L13
.L12:
	movl	%ecx, (%rdi)
	ret
	.cfi_endproc
.LFE5:
	.size	p355_f2, .-p355_f2
	.globl	main
	.type	main, @function
main:
.LFB6:
	.cfi_startproc
	movl	$0, %eax
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"GCC: (GNU) 12.1.0"
	.section	.note.GNU-stack,"",@progbits
