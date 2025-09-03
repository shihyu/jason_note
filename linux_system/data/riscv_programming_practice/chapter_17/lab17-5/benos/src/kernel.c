#include "uart.h"
#include "type.h"
#include "memset.h"
#include "printk.h"
#include "asm/csr.h"
#include "io.h"
#include "asm/sbi.h"
#include "asm/timer.h"
#include "asm/irq.h"
#include "asm/plic.h"
#include "asm/memory.h"
#include "asm/pgtable.h"
#include "sched.h"
#include "../usr/syscall.h"

extern void load_store_test(void);
extern void shift_test(void);
extern void add_sub_test(void);
extern void branch_test(void);
extern void my_memcpy_test(void);
extern unsigned long compare_and_return(unsigned long a, unsigned long b);
extern unsigned long sel_test(unsigned long a, unsigned long b); 
extern void bl_test();
extern unsigned long macro_test_1(long a, long b);
extern unsigned long macro_test_2(long a, long b);

extern unsigned long func_addr[];
extern unsigned long func_num_syms;
extern char func_string;
extern void trap_init(void);
extern void trigger_load_access_fault();

static int print_func_name(unsigned long addr)
{
	int i;
	char *p, *string;

	for (i = 0; i < func_num_syms; i++) {
		if (addr == func_addr[i])
			goto found;
	}

	return 0;

found:
    p = &func_string;
    
    if (i == 0) {
	    string = p;
	    goto done;
    }

    while (1) {
    	p++;

    	if (*p == '\0')
    		i--;

    	if (i == 0) {
    		p++;
    		string = p;
    		break;
    	}
    }

done:
    printk("<0x%lx> %s\n", addr, string);

    return 0;
}

#define MY_OPS(ops, asm_ops) \
static inline void my_asm_##ops(unsigned long mask, void *p) \
{                                                     \
	unsigned long tmp = 0;                            \
	asm volatile (                                \
			"ld %[tmp], (%[p])\n"              \
			" "#asm_ops" %[tmp], %[tmp], %[mask]\n"    \
			"sd %[tmp], (%[p])\n"               \
			: [p] "+r"(p), [tmp]"+r" (tmp)          \
			: [mask]"r" (mask)                   \
			: "memory"	               \
		     );                                \
}

MY_OPS(orr, or)
MY_OPS(and, and)
MY_OPS(add, add)

#if 0
static int test_access_map_address(void)
{
	unsigned long address = DDR_END - 4096;

	*(unsigned long *)address = 0x55;

	if (*(unsigned long *)address == 0x55)
		printk("%s access 0x%x done\n", __func__, address);

	return 0;
}

/*
 * 访问一个没有建立映射的地址
 *
 * Store/AMO page fault
 */
static int test_access_unmap_address(void)
{
	unsigned long address = DDR_END + 4096;

	*(unsigned long *)address = 0x55;

	printk("%s access 0x%x done\n", __func__, address);

	return 0;
}

static void test_mmu(void)
{
	test_access_map_address();
	test_access_unmap_address();
}

extern char idmap_pg_dir[];

static pte_t *walk_pgtable(unsigned long address)
{
	pgd_t *pgdp;
	pmd_t *pmdp;
	pte_t *ptep;

	/* pgd */
	pgdp = pgd_offset_raw((pgd_t *)idmap_pg_dir, address);
	if (pgdp == NULL || pgd_none(*pgdp))
		return NULL;

	pmdp = get_pmdp_from_pgdp(pgdp, address);
	if (pmdp == NULL || pmd_none(*pmdp))
		return NULL;

	ptep = get_ptep_from_pmdp(pmdp, address);
	if ((ptep == NULL) || pte_none(*ptep))
		return NULL;

	return ptep;
}

extern char readonly_page[];

static void test_walk_pgtable(void)
{
	pte_t pte, *ptep;
	pte_t pte_new;

	unsigned long addr = (unsigned long)readonly_page;

	ptep = walk_pgtable(addr);

	pte = *ptep;

	printk("%s:\n", __func__);
	printk("page:0x%lx, pte value: 0x%lx\n", addr, pte);
	walk_pgd((pgd_t *)idmap_pg_dir, addr, PAGE_SIZE);

	pte_new = pte_mkyoung(pte);
	pte_new = pte_mkwrite(pte_new);

	set_pte(ptep, pte_new);

	printk("after mkwrite:\n");
	/*dump addr's pte*/
	walk_pgd((pgd_t *)idmap_pg_dir, addr, PAGE_SIZE);

	memset(readonly_page, 0x55, 100);
	printk("write readonly page done\n");
}

#endif

extern char _text_boot[], _etext_boot[];
extern char _text[], _etext[];
extern char _rodata[], _erodata[];
extern char _data[], _edata[];
extern char _bss[], _ebss[];

static void print_mem(void)
{
	printk("BenOS image layout:\n");
	printk("  .text.boot: 0x%08lx - 0x%08lx (%6ld B)\n",
			(unsigned long)_text_boot, (unsigned long)_etext_boot,
			(unsigned long)(_etext_boot - _text_boot));
	printk("       .text: 0x%08lx - 0x%08lx (%6ld B)\n",
			(unsigned long)_text, (unsigned long)_etext,
			(unsigned long)(_etext - _text));
	printk("     .rodata: 0x%08lx - 0x%08lx (%6ld B)\n",
			(unsigned long)_rodata, (unsigned long)_erodata,
			(unsigned long)(_erodata - _rodata));
	printk("       .data: 0x%08lx - 0x%08lx (%6ld B)\n",
			(unsigned long)_data, (unsigned long)_edata,
			(unsigned long)(_edata - _data));
	printk("        .bss: 0x%08lx - 0x%08lx (%6ld B)\n",
			(unsigned long)_bss, (unsigned long)_ebss,
			(unsigned long)(_ebss - _bss));
}

static void clean_bss(void)
{
	unsigned long start = (unsigned long)_bss;
	unsigned long end = (unsigned long)_ebss;
	unsigned size = end - start;

	memset((void *)start, 0, size);
}

extern union task_union init_task_union;

#ifdef CONFIG_BOARD_QEMU
#define DELAY_TIME 8000000
#else
#define DELAY_TIME 80000
#endif

void user_thread1(void)
{
	unsigned long i = 0;
	while (1) {
		delay(DELAY_TIME);
		printk("%s: %ld\n", __func__, i++);
	}
}

void user_thread2(void)
{
	unsigned long y = 0;
	while (1) {
		delay(DELAY_TIME);
		printk("%s: %s + %llu\n", __func__, "abcde", y++);
	}
}

int run_new_clone_thread(void *arg)
{
	unsigned long i = 0;

	while (1) {
		delay(DELAY_TIME);
		printk("%s %llu\n", __func__, i++);
	}
	return 0;
}


int run_user_thread(void)
{
	unsigned long child_stack;
	int ret;
	unsigned long i = 0;

	child_stack = malloc();
	if (child_stack < 0) {
		printk("cannot allocate memory\n");
		return -1;
	}

	printk("malloc success 0x%x\n", child_stack);

	child_stack = malloc();
	if (child_stack < 0)
		printk("cannot allocate memory\n");

	memset((void *)child_stack, 0, PAGE_SIZE);

	printk("child_stack 0x%x\n", child_stack);

	ret = clone(&run_new_clone_thread,
			(void *)(child_stack + PAGE_SIZE), 0, NULL);
	if (ret < 0) {
		printk("%s: error while clone\n", __func__);
		return ret;
	}

	printk("clone done, 0x%llx 0x%llx\n", &run_new_clone_thread, child_stack + PAGE_SIZE);

	while (1) {
		delay(DELAY_TIME);
		printk("%s: %llu\n", __func__, i++);
	}

	return 0;
}

void user_thread(void)
{

       if (move_to_user_space((unsigned long)&run_user_thread))
               printk("error move_to_user_space\n");
}

void move_thread1(void)
{

       if (move_to_user_space((unsigned long)&user_thread1))
               printk("error move_to_user_space\n");
}

void move_thread2(void)
{

       if (move_to_user_space((unsigned long)&user_thread2))
               printk("error move_to_user_space\n");
}

void kernel_main(void)
{
	clean_bss();
	sbi_put_string("Welcome RISC-V!\r\n");
	init_printk_done(putchar);
	printk("printk init done\n");

	/* lab5-4：查表*/
	print_func_name(0x800880);
	print_func_name(0x800860);
	print_func_name(0x800800);

	//printk("alloc page 0x%lx\n",get_free_page());
	
	sched_init();
	trap_init();

	mem_init((unsigned long)_ebss, DDR_END);
	paging_init();

#ifdef CONFIG_BOARD_QEMU
	plic_init();
	enable_uart_plic();
#endif
	print_mem();

	timer_init();
	
	dump_pgtable();

	int pid;

	pid = do_fork(PF_KTHREAD, (unsigned long)&move_thread1, 0);
	if (pid < 0)
		printk("create thread fail\n");
	printk("pid %d created\n", pid);

	pid = do_fork(PF_KTHREAD, (unsigned long)&move_thread2, 0);
	if (pid < 0)
		printk("create thread fail\n");
	
	printk("pid %d created\n", pid);

	pid = do_fork(PF_KTHREAD, (unsigned long)&user_thread, 0);
       if (pid < 0)
               printk("create thread fail\n");

	printk("pid %d created\n", pid);

	printk("sstatus:0x%lx\n", read_csr(sstatus));
	arch_local_irq_enable();
	printk("sstatus:0x%lx, sie:0x%x\n", read_csr(sstatus), read_csr(sie));

	while (1) {
		;
	}
}
