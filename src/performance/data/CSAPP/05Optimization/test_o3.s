	.file	"test.c"
	.text
	.p2align 4
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
	.p2align 4
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
	.p2align 4
	.globl	p343_func1
	.type	p343_func1, @function
p343_func1:
.LFB2:
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	xorl	%eax, %eax
	call	p343_f
	movq	%rax, %rbx
	xorl	%eax, %eax
	call	p343_f
	addq	%rax, %rbx
	xorl	%eax, %eax
	call	p343_f
	addq	%rax, %rbx
	xorl	%eax, %eax
	call	p343_f
	addq	%rbx, %rax
	popq	%rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE2:
	.size	p343_func1, .-p343_func1
	.p2align 4
	.globl	p343_func2
	.type	p343_func2, @function
p343_func2:
.LFB3:
	.cfi_startproc
	subq	$8, %rsp
	.cfi_def_cfa_offset 16
	xorl	%eax, %eax
	call	p343_f
	addq	$8, %rsp
	.cfi_def_cfa_offset 8
	salq	$2, %rax
	ret
	.cfi_endproc
.LFE3:
	.size	p343_func2, .-p343_func2
	.p2align 4
	.globl	p355_f1
	.type	p355_f1, @function
p355_f1:
.LFB4:
	.cfi_startproc
	testl	%edx, %edx
	jle	.L8
	movslq	%edx, %rdx
	movl	(%rdi), %eax
	leaq	(%rsi,%rdx,4), %rdx
	.p2align 4,,10
	.p2align 3
.L10:
	imull	(%rsi), %eax
	addq	$4, %rsi
	movl	%eax, (%rdi)
	cmpq	%rsi, %rdx
	jne	.L10
.L8:
	ret
	.cfi_endproc
.LFE4:
	.size	p355_f1, .-p355_f1
	.p2align 4
	.globl	p355_f2
	.type	p355_f2, @function
p355_f2:
.LFB5:
	.cfi_startproc
	movl	(%rdi), %ecx
	movq	%rdi, %r8
	testl	%edx, %edx
	jle	.L14
	leal	-1(%rdx), %eax
	cmpl	$26, %eax
	jbe	.L20
	movl	%edx, %edi
	movdqa	.LC0(%rip), %xmm1
	movq	%rsi, %rax
	shrl	$2, %edi
	salq	$4, %rdi
	addq	%rsi, %rdi
	.p2align 4,,10
	.p2align 3
.L16:
	movdqu	(%rax), %xmm2
	movdqu	(%rax), %xmm0
	addq	$16, %rax
	pmuludq	%xmm1, %xmm2
	psrlq	$32, %xmm0
	psrlq	$32, %xmm1
	pmuludq	%xmm1, %xmm0
	pshufd	$8, %xmm2, %xmm1
	pshufd	$8, %xmm0, %xmm0
	punpckldq	%xmm0, %xmm1
	cmpq	%rdi, %rax
	jne	.L16
	movdqa	%xmm1, %xmm0
	psrldq	$8, %xmm0
	movdqa	%xmm0, %xmm2
	psrlq	$32, %xmm0
	pmuludq	%xmm1, %xmm2
	psrlq	$32, %xmm1
	pmuludq	%xmm1, %xmm0
	pshufd	$8, %xmm2, %xmm1
	pshufd	$8, %xmm0, %xmm0
	punpckldq	%xmm0, %xmm1
	movdqa	%xmm1, %xmm0
	psrldq	$4, %xmm0
	pmuludq	%xmm1, %xmm0
	movd	%xmm0, %eax
	imull	%eax, %ecx
	movl	%edx, %eax
	andl	$-4, %eax
	testb	$3, %dl
	je	.L14
.L15:
	cltq
	.p2align 4,,10
	.p2align 3
.L19:
	imull	(%rsi,%rax,4), %ecx
	addq	$1, %rax
	cmpl	%eax, %edx
	jg	.L19
.L14:
	movl	%ecx, (%r8)
	ret
.L20:
	xorl	%eax, %eax
	jmp	.L15
	.cfi_endproc
.LFE5:
	.size	p355_f2, .-p355_f2
	.section	.text.startup,"ax",@progbits
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB6:
	.cfi_startproc
	xorl	%eax, %eax
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.section	.rodata.cst16,"aM",@progbits,16
	.align 16
.LC0:
	.long	1
	.long	1
	.long	1
	.long	1
	.ident	"GCC: (GNU) 12.1.0"
	.section	.note.GNU-stack,"",@progbits
