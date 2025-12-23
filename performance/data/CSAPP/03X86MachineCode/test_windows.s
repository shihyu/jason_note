	.file	"test_env.c"
	.text
	.globl	test_of_parameters
	.def	test_of_parameters;	.scl	2;	.type	32;	.endef
	.seh_proc	test_of_parameters
test_of_parameters:
	.seh_endprologue
	movq	40(%rsp), %rax
	movb	%cl, (%rax)
	movq	48(%rsp), %rax
	movw	%dx, (%rax)
	movq	56(%rsp), %rax
	movl	%r8d, (%rax)
	movq	64(%rsp), %rax
	movl	%r9d, (%rax)
	ret
	.seh_endproc
	.ident	"GCC: (x86_64-posix-seh-rev3, Built by MinGW-W64 project) 12.1.0"
