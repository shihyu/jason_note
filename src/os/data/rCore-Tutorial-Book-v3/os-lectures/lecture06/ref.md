# 第六講 虛擬存儲概念
## ref
中的第七行 https://content.riscv.org/wp-content/uploads/2017/05/riscv-privileged-v1.10.pdf
RISC-V 指令集手冊卷2：特權體系結構（Privileged Architecture Version 1.10）

4.3.2 Virtual Address Translation Process

page-fault exception

3.1.21 Machine Trap Value (mtval) Register

When a hardware breakpoint is triggered, or an instruction-fetch, load, or store address-misaligned, access, or page-fault exception occurs, mtval is written with the faulting effective address.

3.5 Physical Memory Attributes

physical memory attributes (PMAs)
PMAs do not vary by execution context.

PMA checker
where possible, RISC-V processors precisely trap physical memory accesses that fail PMA checks.

4.1.11 Supervisor Trap Value (stval) Register

When a hardware breakpoint is triggered, or an instruction-fetch, load, or store access or page-fault exception occurs, or an instruction-fetch or AMO address-misaligned exception occurs, stval is written with the faulting address.

stval is a WARL register
沒有明白。

4.3.1 Addressing and Memory Protection

Two schemes to manage the A and D bits are permitted:
When a virtual page is accessed and the A bit is clear, or is written and the D bit is clear, a page-fault exception is raised.
a page-fault exception is raised if the physical address is insufficiently aligned.

## 6.1 虛擬存儲的需求背景 
## 6.2 覆蓋和交換 
## 6.3 局部性原理 
## 6.4 虛擬存儲概念 
## 6.5 虛擬頁式存儲管理 
## 6.6 缺頁異常
## 6.7 RISC-V缺頁異常

### Supervisor Trap Handling
riscv-privileged-v1.10.pdf
page 20

Supervisor Trap Handling
與中斷相關的寄存器

![SupervisorTrapHandling](/Users/xyong/Desktop/figs/SupervisorTrapHandling.png)



At the beginning of a trap handler, sscratch is swapped with a user register to provide an initial working register.

When a trap is taken into S-mode, sepc is written with the virtual address of the instruction that encountered the exception.

The Interrupt bit in the scause register is set if the contains a code identifying the last exception.

When a hardware breakpoint is triggered, or an instruction-fetch, load, or store access or page-fault exception occurs, or an instruction-fetch or AMO address-misaligned exception occurs, stval is written with the faulting address.

The sip register is an XLEN-bit read/write register containing information on pending interrupts, while sie is the corresponding XLEN-bit read/write register containing interrupt enable bits.

### 中斷源（scause）

https://content.riscv.org/wp-content/uploads/2018/05/riscv-privileged-BCN.v7-2.pdf
Page 25

![scause-CSR](/Users/xyong/Desktop/figs/scause-CSR.png)



### Supervisor cause register (scause) values after trap

riscv-privileged-v1.10.pdf
page 65
Table 4.2: Supervisor cause register (scause) values after trap.

Instruction access
Load access fault

![scause-trap](/Users/xyong/Desktop/figs/scause-trap.png)




### rCore的缺頁異常處理

Ref: rCore-2_OSLab-g2-interrupt.md-缺頁異常

缺頁異常只會在 MMU 啟用後，虛擬地址翻譯失敗時產生，這時候根據是取指還是訪存，分別觸發 Instruction Abort 與 Data Abort。

當狀態碼是 translation fault、access flag fault、permission fault 時，將被判斷為是缺頁異常，並調用 `handle_page_fault()` 處理缺頁異常。

發生 Instruction page fault 和 Load/Store page access時，虛擬地址將會被保存到stval寄存器中；再調用 `crate::memory::page_fault_handler(addr)` 來做具體的缺頁處理。

### handle_page_fault

fn rust_trap(tf: &mut TrapFrame)

fn page_fault(tf: &mut TrapFrame)

pub fn handle_page_fault(addr: usize) -> bool

pub fn handle_page_fault(&mut self, addr: VirtAddr) -> bool

fn handle_page_fault(&self, pt: &mut dyn PageTable, addr: VirtAddr) -> bool

let frame = self.allocator.alloc().expect("failed to alloc frame");
entry.set_target(frame);
entry.set_present(true);
entry.update();

#### rust_trap
https://github.com/rcore-os/rCore/blob/master/kernel/src/arch/riscv/interrupt.rs#L56
fn rust_trap(tf: &mut TrapFrame)

scause.cause
Load page fault
Store/AMO page fault
Instruction page fault

#### page_fault
rCore/kernel/src/arch/riscv/interrupt.rs
https://github.com/rcore-os/rCore/blob/master/kernel/src/arch/riscv/interrupt.rs#L125
fn page_fault(tf: &mut TrapFrame)


#### handle_page_fault

https://github.com/rcore-os/rCore/blob/master/kernel/src/memory.rs#L132
pub fn handle_page_fault(addr: usize) -> bool

kernel/src/memory.rs
L132：分發給相應的線程進行處理

#### handle_page_fault
https://github.com/rcore-os/rCore/blob/master/crate/memory/src/memory_set/mod.rs#L379
pub fn handle_page_fault(&mut self, addr: VirtAddr) -> bool
分發給相應特徵的內存

#### handle_page_fault
https://github.com/rcore-os/rCore/blob/master/crate/memory/src/memory_set/handler/delay.rs#L52
fn handle_page_fault(&self, pt: &mut dyn PageTable, addr: VirtAddr) -> bool

let frame = self.allocator.alloc().expect("failed to alloc frame");
entry.set_target(frame);
entry.set_present(true);
entry.update();

#### set_target
https://github.com/rcore-os/rCore/blob/master/kernel/src/arch/riscv/paging.rs#L107
fn set_target(&mut self, target: usize)
設置物理頁號

https://github.com/rcore-os/rCore/blob/master/kernel/src/arch/riscv/paging.rs#L101
fn set_present(&mut self, value: bool)
設置頁表項標誌位

https://github.com/rcore-os/rCore/blob/master/kernel/src/arch/riscv/paging.rs#L75
fn update(&mut self)
TLB刷新