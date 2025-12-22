	.file	"test.c"
	.text
	.globl	p114_encoding_mult2
	.type	p114_encoding_mult2, @function
p114_encoding_mult2:
.LFB15:
	.cfi_startproc
	movq	%rdi, %rax
	imulq	%rsi, %rax
	ret
	.cfi_endproc
.LFE15:
	.size	p114_encoding_mult2, .-p114_encoding_mult2
	.globl	P114_encoding_multstore
	.type	P114_encoding_multstore, @function
P114_encoding_multstore:
.LFB16:
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	movq	%rdx, %rbx
	call	p114_encoding_mult2
	movq	%rax, (%rbx)
	popq	%rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE16:
	.size	P114_encoding_multstore, .-P114_encoding_multstore
	.globl	P125_move_exchange
	.type	P125_move_exchange, @function
P125_move_exchange:
.LFB17:
	.cfi_startproc
	movq	(%rdi), %rax
	movq	%rsi, (%rdi)
	ret
	.cfi_endproc
.LFE17:
	.size	P125_move_exchange, .-P125_move_exchange
	.globl	p127_exercise_3_5_decode1
	.type	p127_exercise_3_5_decode1, @function
p127_exercise_3_5_decode1:
.LFB18:
	.cfi_startproc
	movq	(%rdx), %rax
	movq	(%rsi), %rcx
	movq	%rcx, (%rdx)
	movq	(%rdi), %rdx
	movq	%rdx, (%rsi)
	movq	%rax, (%rdi)
	ret
	.cfi_endproc
.LFE18:
	.size	p127_exercise_3_5_decode1, .-p127_exercise_3_5_decode1
	.globl	p129_leaq_scale
	.type	p129_leaq_scale, @function
p129_leaq_scale:
.LFB19:
	.cfi_startproc
	leaq	(%rdi,%rsi,4), %rax
	leaq	(%rdx,%rdx,2), %rdx
	leaq	(%rax,%rdx,4), %rax
	ret
	.cfi_endproc
.LFE19:
	.size	p129_leaq_scale, .-p129_leaq_scale
	.globl	p131_exercise_3_9_shift_left4_rightn
	.type	p131_exercise_3_9_shift_left4_rightn, @function
p131_exercise_3_9_shift_left4_rightn:
.LFB20:
	.cfi_startproc
	movq	%rdi, %rax
	salq	$4, %rax
	movl	%esi, %ecx
	sarq	%cl, %rax
	ret
	.cfi_endproc
.LFE20:
	.size	p131_exercise_3_9_shift_left4_rightn, .-p131_exercise_3_9_shift_left4_rightn
	.globl	p134_special_arith_inst_mul
	.type	p134_special_arith_inst_mul, @function
p134_special_arith_inst_mul:
.LFB21:
	.cfi_startproc
	movq	%rsi, %rax
	mulq	%rdx
	movq	%rax, (%rdi)
	movq	%rdx, 8(%rdi)
	ret
	.cfi_endproc
.LFE21:
	.size	p134_special_arith_inst_mul, .-p134_special_arith_inst_mul
	.globl	P134_special_airth_inst_remdiv
	.type	P134_special_airth_inst_remdiv, @function
P134_special_airth_inst_remdiv:
.LFB22:
	.cfi_startproc
	movq	%rdi, %rax
	movq	%rdx, %r8
	cqto
	idivq	%rsi
	movq	%rax, (%r8)
	movq	%rdx, (%rcx)
	ret
	.cfi_endproc
.LFE22:
	.size	P134_special_airth_inst_remdiv, .-P134_special_airth_inst_remdiv
	.globl	p124_sepcial_arith_inst_remdiv_unsigned
	.type	p124_sepcial_arith_inst_remdiv_unsigned, @function
p124_sepcial_arith_inst_remdiv_unsigned:
.LFB23:
	.cfi_startproc
	movq	%rdi, %rax
	movq	%rdx, %r8
	movl	$0, %edx
	divq	%rsi
	movq	%rax, (%r8)
	movq	%rdx, (%rcx)
	ret
	.cfi_endproc
.LFE23:
	.size	p124_sepcial_arith_inst_remdiv_unsigned, .-p124_sepcial_arith_inst_remdiv_unsigned
	.globl	p137_control_flow_less
	.type	p137_control_flow_less, @function
p137_control_flow_less:
.LFB24:
	.cfi_startproc
	cmpq	%rsi, %rdi
	setl	%al
	movzbl	%al, %eax
	ret
	.cfi_endproc
.LFE24:
	.size	p137_control_flow_less, .-p137_control_flow_less
	.globl	p127_control_flow_less_unsinged
	.type	p127_control_flow_less_unsinged, @function
p127_control_flow_less_unsinged:
.LFB25:
	.cfi_startproc
	cmpq	%rsi, %rdi
	setb	%al
	movzbl	%al, %eax
	ret
	.cfi_endproc
.LFE25:
	.size	p127_control_flow_less_unsinged, .-p127_control_flow_less_unsinged
	.globl	p141_encoding_of_jump_inst
	.type	p141_encoding_of_jump_inst, @function
p141_encoding_of_jump_inst:
.LFB26:
	.cfi_startproc
	testl	%edi, %edi
	jg	.L16
	leal	-1(%rdi), %eax
	ret
.L16:
	leal	1(%rdi), %eax
	ret
	.cfi_endproc
.LFE26:
	.size	p141_encoding_of_jump_inst, .-p141_encoding_of_jump_inst
	.globl	p142_absdiff_se
	.type	p142_absdiff_se, @function
p142_absdiff_se:
.LFB27:
	.cfi_startproc
	cmpq	%rsi, %rdi
	jge	.L18
	addq	$1, lt_cnt(%rip)
	movq	%rsi, %rax
	subq	%rdi, %rax
	ret
.L18:
	addq	$1, ge_cnt(%rip)
	movq	%rdi, %rax
	subq	%rsi, %rax
	ret
	.cfi_endproc
.LFE27:
	.size	p142_absdiff_se, .-p142_absdiff_se
	.globl	p142_gotodiff_se
	.type	p142_gotodiff_se, @function
p142_gotodiff_se:
.LFB28:
	.cfi_startproc
	cmpq	%rsi, %rdi
	jge	.L23
	addq	$1, lt_cnt(%rip)
	movq	%rsi, %rax
	subq	%rdi, %rax
	ret
.L23:
	addq	$1, ge_cnt(%rip)
	movq	%rdi, %rax
	subq	%rsi, %rax
	ret
	.cfi_endproc
.LFE28:
	.size	p142_gotodiff_se, .-p142_gotodiff_se
	.globl	p145_absdiff
	.type	p145_absdiff, @function
p145_absdiff:
.LFB29:
	.cfi_startproc
	cmpq	%rsi, %rdi
	jge	.L25
	movq	%rsi, %rax
	subq	%rdi, %rax
	ret
.L25:
	movq	%rdi, %rax
	subq	%rsi, %rax
	ret
	.cfi_endproc
.LFE29:
	.size	p145_absdiff, .-p145_absdiff
	.globl	p145_cmovdiff
	.type	p145_cmovdiff, @function
p145_cmovdiff:
.LFB30:
	.cfi_startproc
	movq	%rsi, %rdx
	subq	%rdi, %rdx
	movq	%rdi, %rax
	subq	%rsi, %rax
	cmpq	%rdi, %rsi
	jle	.L27
	movq	%rdx, %rax
.L27:
	ret
	.cfi_endproc
.LFE30:
	.size	p145_cmovdiff, .-p145_cmovdiff
	.globl	p150_factorial_dowhile
	.type	p150_factorial_dowhile, @function
p150_factorial_dowhile:
.LFB31:
	.cfi_startproc
	movl	$1, %eax
.L30:
	imulq	%rdi, %rax
	subq	$1, %rdi
	cmpq	$1, %rdi
	jg	.L30
	ret
	.cfi_endproc
.LFE31:
	.size	p150_factorial_dowhile, .-p150_factorial_dowhile
	.globl	p154_factorial_while
	.type	p154_factorial_while, @function
p154_factorial_while:
.LFB32:
	.cfi_startproc
	movl	$1, %eax
	jmp	.L32
.L33:
	imulq	%rdi, %rax
	subq	$1, %rdi
.L32:
	cmpq	$1, %rdi
	jg	.L33
	ret
	.cfi_endproc
.LFE32:
	.size	p154_factorial_while, .-p154_factorial_while
	.globl	p157_factorial_for
	.type	p157_factorial_for, @function
p157_factorial_for:
.LFB33:
	.cfi_startproc
	movl	$1, %edx
	movl	$2, %eax
	jmp	.L35
.L36:
	imulq	%rdi, %rdx
	addq	$1, %rax
.L35:
	cmpq	%rdi, %rax
	jle	.L36
	movq	%rdx, %rax
	ret
	.cfi_endproc
.LFE33:
	.size	p157_factorial_for, .-p157_factorial_for
	.globl	p160_switch_example
	.type	p160_switch_example, @function
p160_switch_example:
.LFB34:
	.cfi_startproc
	cmpq	$102, %rsi
	je	.L38
	cmpq	$103, %rsi
	je	.L39
	cmpq	$100, %rsi
	je	.L42
	movl	$0, %edi
.L40:
	movq	%rdi, (%rdx)
	ret
.L42:
	leaq	(%rdi,%rdi,2), %rax
	leaq	(%rdi,%rax,4), %rdi
	jmp	.L40
.L38:
	addq	$10, %rdi
.L39:
	addq	$11, %rdi
	jmp	.L40
	.cfi_endproc
.LFE34:
	.size	p160_switch_example, .-p160_switch_example
	.globl	p169_passing_parameter
	.type	p169_passing_parameter, @function
p169_passing_parameter:
.LFB35:
	.cfi_startproc
	movq	16(%rsp), %rax
	addq	%rdi, (%rsi)
	addl	%edx, (%rcx)
	addw	%r8w, (%r9)
	movl	8(%rsp), %edx
	addb	%dl, (%rax)
	ret
	.cfi_endproc
.LFE35:
	.size	p169_passing_parameter, .-p169_passing_parameter
	.globl	p169_passing_parameter_caller
	.type	p169_passing_parameter_caller, @function
p169_passing_parameter_caller:
.LFB36:
	.cfi_startproc
	subq	$16, %rsp
	.cfi_def_cfa_offset 24
	movq	$1, 8(%rsp)
	movl	$2, 4(%rsp)
	movw	$3, 2(%rsp)
	movb	$4, 1(%rsp)
	leaq	1(%rsp), %rax
	pushq	%rax
	.cfi_def_cfa_offset 32
	pushq	$4
	.cfi_def_cfa_offset 40
	leaq	18(%rsp), %r9
	movl	$3, %r8d
	leaq	20(%rsp), %rcx
	movl	$2, %edx
	leaq	24(%rsp), %rsi
	movl	$1, %edi
	call	p169_passing_parameter
	addq	$32, %rsp
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE36:
	.size	p169_passing_parameter_caller, .-p169_passing_parameter_caller
	.globl	p171_swap_add
	.type	p171_swap_add, @function
p171_swap_add:
.LFB37:
	.cfi_startproc
	movq	(%rdi), %rax
	movq	(%rsi), %rdx
	movq	%rdx, (%rdi)
	movq	%rax, (%rsi)
	addq	%rdx, %rax
	ret
	.cfi_endproc
.LFE37:
	.size	p171_swap_add, .-p171_swap_add
	.globl	p171_caller
	.type	p171_caller, @function
p171_caller:
.LFB38:
	.cfi_startproc
	subq	$16, %rsp
	.cfi_def_cfa_offset 24
	movq	$534, 8(%rsp)
	movq	$1057, (%rsp)
	movq	%rsp, %rsi
	leaq	8(%rsp), %rdi
	call	p171_swap_add
	movq	8(%rsp), %rdx
	subq	(%rsp), %rdx
	imulq	%rdx, %rax
	addq	$16, %rsp
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE38:
	.size	p171_caller, .-p171_caller
	.globl	p173_Q
	.type	p173_Q, @function
p173_Q:
.LFB39:
	.cfi_startproc
	movq	%rdi, %rax
	ret
	.cfi_endproc
.LFE39:
	.size	p173_Q, .-p173_Q
	.globl	p173_P
	.type	p173_P, @function
p173_P:
.LFB40:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	pushq	%rbx
	.cfi_def_cfa_offset 24
	.cfi_offset 3, -24
	movq	%rdi, %rbp
	movq	%rsi, %rdi
	call	p173_Q
	movq	%rax, %rbx
	movq	%rbp, %rdi
	call	p173_Q
	addq	%rbx, %rax
	popq	%rbx
	.cfi_def_cfa_offset 16
	popq	%rbp
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE40:
	.size	p173_P, .-p173_P
	.globl	p174_outter
	.type	p174_outter, @function
p174_outter:
.LFB41:
	.cfi_startproc
	pushq	%r13
	.cfi_def_cfa_offset 16
	.cfi_offset 13, -16
	pushq	%r12
	.cfi_def_cfa_offset 24
	.cfi_offset 12, -24
	pushq	%rbp
	.cfi_def_cfa_offset 32
	.cfi_offset 6, -32
	pushq	%rbx
	.cfi_def_cfa_offset 40
	.cfi_offset 3, -40
	subq	$8, %rsp
	.cfi_def_cfa_offset 48
	movq	%rdi, %rbx
	movq	%rsi, %r13
	movq	%rdx, %r12
	movq	%rcx, %rbp
	movl	$2, %esi
	movl	$1, %edi
	movl	$0, %eax
	call	p174_inner
	leaq	(%rbx,%r13), %rax
	addq	%r12, %rax
	addq	%rbp, %rax
	addq	$8, %rsp
	.cfi_def_cfa_offset 40
	popq	%rbx
	.cfi_def_cfa_offset 32
	popq	%rbp
	.cfi_def_cfa_offset 24
	popq	%r12
	.cfi_def_cfa_offset 16
	popq	%r13
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE41:
	.size	p174_outter, .-p174_outter
	.globl	p185_test_struct
	.type	p185_test_struct, @function
p185_test_struct:
.LFB42:
	.cfi_startproc
	movl	4(%rdi), %eax
	addl	(%rdi), %eax
	cltq
	leaq	8(%rdi,%rax,4), %rax
	movq	%rax, 16(%rdi)
	ret
	.cfi_endproc
.LFE42:
	.size	p185_test_struct, .-p185_test_struct
	.globl	p195_buffer_overflow
	.type	p195_buffer_overflow, @function
p195_buffer_overflow:
.LFB43:
	.cfi_startproc
	subq	$24, %rsp
	.cfi_def_cfa_offset 32
	leaq	8(%rsp), %rdi
	call	p195_do_something
	addq	$24, %rsp
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE43:
	.size	p195_buffer_overflow, .-p195_buffer_overflow
	.globl	p206_floating_point_moving
	.type	p206_floating_point_moving, @function
p206_floating_point_moving:
.LFB44:
	.cfi_startproc
	vmovaps	%xmm0, %xmm1
	vmovss	(%rdi), %xmm0
	vmovss	%xmm1, (%rsi)
	ret
	.cfi_endproc
.LFE44:
	.size	p206_floating_point_moving, .-p206_floating_point_moving
	.globl	p207_floating_integer_conversion
	.type	p207_floating_integer_conversion, @function
p207_floating_integer_conversion:
.LFB45:
	.cfi_startproc
	vxorps	%xmm0, %xmm0, %xmm0
	movq	%rcx, %rax
	vcvtsi2ssl	%edi, %xmm0, %xmm1
	vmovss	%xmm1, (%rdx)
	vcvtsi2ssq	%rsi, %xmm0, %xmm1
	vmovss	%xmm1, (%rdx)
	vcvtsi2sdl	%edi, %xmm0, %xmm1
	vmovsd	%xmm1, (%rcx)
	vcvtsi2sdq	%rsi, %xmm0, %xmm0
	vmovsd	%xmm0, (%rcx)
	vcvttss2sil	(%rdx), %ecx
	movl	%ecx, (%r8)
	vcvttss2siq	(%rdx), %rdx
	movq	%rdx, (%r9)
	vcvttsd2sil	(%rax), %edx
	movl	%edx, (%r8)
	vcvttsd2siq	(%rax), %rax
	movq	%rax, (%r9)
	ret
	.cfi_endproc
.LFE45:
	.size	p207_floating_integer_conversion, .-p207_floating_integer_conversion
	.globl	p207_float_double_conversion
	.type	p207_float_double_conversion, @function
p207_float_double_conversion:
.LFB46:
	.cfi_startproc
	vxorps	%xmm0, %xmm0, %xmm0
	vcvtsd2ss	(%rsi), %xmm0, %xmm0
	vmovss	%xmm0, (%rdi)
	vcvtss2sd	%xmm0, %xmm0, %xmm0
	vmovsd	%xmm0, (%rsi)
	ret
	.cfi_endproc
.LFE46:
	.size	p207_float_double_conversion, .-p207_float_double_conversion
	.globl	p210_passing_floating_caller
	.type	p210_passing_floating_caller, @function
p210_passing_floating_caller:
.LFB47:
	.cfi_startproc
	subq	$8, %rsp
	.cfi_def_cfa_offset 16
	pushq	$-1717986918
	.cfi_def_cfa_offset 24
	movl	$1076205977, 4(%rsp)
	pushq	$1717986918
	.cfi_def_cfa_offset 32
	movl	$1076061798, 4(%rsp)
	vmovsd	.LC0(%rip), %xmm7
	vmovsd	.LC1(%rip), %xmm6
	vmovss	.LC6(%rip), %xmm5
	vmovsd	.LC2(%rip), %xmm4
	vmovss	.LC7(%rip), %xmm3
	movl	$0, %esi
	movl	$10, %edi
	vmovss	.LC8(%rip), %xmm2
	vmovsd	.LC3(%rip), %xmm1
	vmovss	.LC9(%rip), %xmm0
	call	p210_passing_floating_parameters
	addq	$24, %rsp
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE47:
	.size	p210_passing_floating_caller, .-p210_passing_floating_caller
	.globl	p210_floating_point_airthmetics
	.type	p210_floating_point_airthmetics, @function
p210_floating_point_airthmetics:
.LFB48:
	.cfi_startproc
	vcvtss2sd	%xmm1, %xmm1, %xmm1
	vmulsd	%xmm0, %xmm1, %xmm1
	vxorps	%xmm0, %xmm0, %xmm0
	vcvtsi2sdl	%edi, %xmm0, %xmm0
	vdivsd	%xmm0, %xmm2, %xmm2
	vsubsd	%xmm2, %xmm1, %xmm0
	ret
	.cfi_endproc
.LFE48:
	.size	p210_floating_point_airthmetics, .-p210_floating_point_airthmetics
	.globl	p210_floating_point_constant
	.type	p210_floating_point_constant, @function
p210_floating_point_constant:
.LFB49:
	.cfi_startproc
	vmulsd	.LC10(%rip), %xmm0, %xmm0
	vaddsd	.LC11(%rip), %xmm0, %xmm0
	ret
	.cfi_endproc
.LFE49:
	.size	p210_floating_point_constant, .-p210_floating_point_constant
	.globl	p214_floating_point_comparison
	.type	p214_floating_point_comparison, @function
p214_floating_point_comparison:
.LFB50:
	.cfi_startproc
	vxorpd	%xmm1, %xmm1, %xmm1
	vcomisd	%xmm1, %xmm0
	jbe	.L74
	movl	$0, %eax
	ret
.L74:
	vucomisd	%xmm1, %xmm0
	jp	.L71
	jne	.L71
	movl	$1, %eax
	ret
.L71:
	vxorpd	%xmm1, %xmm1, %xmm1
	vcomisd	%xmm0, %xmm1
	ja	.L75
	movl	$3, %eax
	ret
.L75:
	movl	$2, %eax
	ret
	.cfi_endproc
.LFE50:
	.size	p214_floating_point_comparison, .-p214_floating_point_comparison
	.globl	main
	.type	main, @function
main:
.LFB51:
	.cfi_startproc
	movl	$0, %eax
	ret
	.cfi_endproc
.LFE51:
	.size	main, .-main
	.globl	ge_cnt
	.bss
	.align 8
	.type	ge_cnt, @object
	.size	ge_cnt, 8
ge_cnt:
	.zero	8
	.globl	lt_cnt
	.align 8
	.type	lt_cnt, @object
	.size	lt_cnt, 8
lt_cnt:
	.zero	8
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC0:
	.long	858993459
	.long	1075917619
	.align 8
.LC1:
	.long	0
	.long	1075707904
	.align 8
.LC2:
	.long	858993459
	.long	1075131187
	.align 8
.LC3:
	.long	0
	.long	1073741824
	.section	.rodata.cst4,"aM",@progbits,4
	.align 4
.LC6:
	.long	1087163597
	.align 4
.LC7:
	.long	1082549862
	.align 4
.LC8:
	.long	1078355558
	.align 4
.LC9:
	.long	1065353216
	.section	.rodata.cst8
	.align 8
.LC10:
	.long	-858993459
	.long	1073532108
	.align 8
.LC11:
	.long	-858993459
	.long	1077939404
	.ident	"GCC: (GNU) 12.1.0"
	.section	.note.GNU-stack,"",@progbits
