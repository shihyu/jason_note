#include "io.h"
#include "asm/plic.h"
#include "asm/csr.h"
#include "asm/plic.h"
#include "asm/irq.h"
#include "printk.h"

#define MAX_CPUS 1

/*
 * CPU_TO_HART改成CPU_TO_CONTEXT
 *
 * PLIC中断控制器支持多个中断硬件上下文（context），
 * 每个hart可能包含多个中断context，每个中断context包含一组中断相关的控制寄存器
 * 这个宏从CPU映射到hart，然后再映射到M模式的中断context
 *
 * 对于QEMU Virt平台，CPU0映射到hart1上，CPU1映射到hart2，以此类推。
 * 每个hart有M模式和S模式的中断context。
 * CPU_TO_CONTEXT宏用来映射CPU对应hart的M模式的中断context。
 */
#define CPU_TO_CONTEXT(cpu) (2 * cpu + 1)

void plic_set_prority(int hwirq, int pro)
{
	unsigned int reg = PLIC_PRIORITY(hwirq);

	writel(1, reg);
}

void plic_enable_irq(int cpu, int hwirq, int enable)
{
	unsigned int hwirq_mask = 1 << (hwirq % 32);
	int context = CPU_TO_CONTEXT(cpu);
	unsigned int reg = PLIC_MENABLE(context) + 4*(hwirq / 32);

	printk("reg: 0x%x, hwirq:%d\n", reg, hwirq);

	if (enable)
		writel(readl(reg) | hwirq_mask, reg);
	else
		writel(readl(reg) & ~hwirq_mask, reg);
}

void plic_handle_irq(struct pt_regs *regs)
{
	int hwirq;
	/*TODO: only CPU0 handle it*/
	int context = CPU_TO_CONTEXT(0);

	unsigned int claim_reg = PLIC_MCLAIM(context);

	csr_clear(sie, SIE_SEIE);

	while((hwirq = readl(claim_reg))) {
		if (hwirq == UART0_IRQ)
			handle_uart_irq();

		writel(hwirq, claim_reg);
	}
	csr_set(sie, SIE_SEIE);
}

int plic_init(void)
{
	int i;
	int hwirq;

	for (i = 0; i < MAX_CPUS; i++) {
		/* 设置所有M模式处理器核心的中断优先级阈值为0*/
		writel(0, PLIC_MTHRESHOLD(CPU_TO_CONTEXT(i)));

		for (hwirq = 1; hwirq <= MAX_PLIC_IRQS; hwirq++) {
			/*关闭PLIC中所有外部中断*/
			plic_enable_irq(i, hwirq, 0);

			/* 预先设置所有中断号的优先级为1*/
			plic_set_prority(hwirq, 1);
		}
	}

	csr_set(sie, SIE_SEIE);

	return 0;
}
