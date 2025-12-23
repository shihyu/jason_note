	.file	"test_env.c"
	.text
	.globl	test_of_parameters
	.type	test_of_parameters, @function
test_of_parameters:
.LFB0:
	.cfi_startproc
	movb	%dil, (%r8)
	movw	%si, (%r9)
	movq	8(%rsp), %rax
	movl	%edx, (%rax)
	movq	16(%rsp), %rax
	movq	%rcx, (%rax)
	ret
	.cfi_endproc
.LFE0:
	.size	test_of_parameters, .-test_of_parameters
	.ident	"GCC: (GNU) 12.1.0"
	.section	.note.GNU-stack,"",@progbits
