# The set of languages for which implicit dependencies are needed:
set(CMAKE_DEPENDS_LANGUAGES
  "ASM"
  "C"
  )
# The set of files for implicit dependencies of each language:
set(CMAKE_DEPENDS_CHECK_ASM
  "/chos/kernel/arch/aarch64/boot/raspi3/init/start.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/start.S.obj"
  "/chos/kernel/arch/aarch64/boot/raspi3/init/tools.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/tools.S.obj"
  "/chos/kernel/arch/aarch64/head.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/head.S.obj"
  "/chos/kernel/arch/aarch64/irq/irq.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/irq/irq.S.obj"
  "/chos/kernel/arch/aarch64/irq/irq_entry.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/irq/irq_entry.S.obj"
  "/chos/kernel/arch/aarch64/mm/memcpy.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/memcpy.S.obj"
  "/chos/kernel/arch/aarch64/mm/memmove.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/memmove.S.obj"
  "/chos/kernel/arch/aarch64/mm/page_table.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/page_table.S.obj"
  "/chos/kernel/arch/aarch64/sched/idle.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/sched/idle.S.obj"
  "/chos/kernel/arch/aarch64/tools.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/tools.S.obj"
  "/chos/kernel/_build/incbin_root.S" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/incbin_root.S.obj"
  )
set(CMAKE_ASM_COMPILER_ID "GNU")

# Preprocessor definitions for this target.
set(CMAKE_TARGET_DEFINITIONS_ASM
  "CHCORE"
  "CHCORE_ARCH=\"aarch64\""
  "CHCORE_ARCH_AARCH64"
  "CHCORE_CROSS_COMPILE=\"aarch64-linux-gnu-\""
  "CHCORE_KERNEL_TEST"
  "CHCORE_PLAT=\"raspi3\""
  "CHCORE_PLAT_RASPI3"
  "CHCORE_ROOT_PROGRAM=\"procm.srv\""
  "LOG_LEVEL=1"
  "__ASM__"
  )

# The include file search paths:
set(CMAKE_ASM_TARGET_INCLUDE_PATH
  "../include"
  "../include/arch/aarch64"
  "../include/arch/aarch64/plat/raspi3"
  "../arch/aarch64/boot/raspi3/include"
  )
set(CMAKE_DEPENDS_CHECK_C
  "/chos/kernel/arch/aarch64/boot/raspi3/init/init_c.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/init_c.c.obj"
  "/chos/kernel/arch/aarch64/boot/raspi3/init/mmu.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/init/mmu.c.obj"
  "/chos/kernel/arch/aarch64/boot/raspi3/peripherals/uart.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/boot/raspi3/peripherals/uart.c.obj"
  "/chos/kernel/arch/aarch64/irq/ipi.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/irq/ipi.c.obj"
  "/chos/kernel/arch/aarch64/irq/irq_entry.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/irq/irq_entry.c.obj"
  "/chos/kernel/arch/aarch64/irq/pgfault.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/irq/pgfault.c.obj"
  "/chos/kernel/arch/aarch64/machine/pmu.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/machine/pmu.c.obj"
  "/chos/kernel/arch/aarch64/machine/smp.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/machine/smp.c.obj"
  "/chos/kernel/arch/aarch64/main.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/main.c.obj"
  "/chos/kernel/arch/aarch64/mm/cache.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/cache.c.obj"
  "/chos/kernel/arch/aarch64/mm/memset.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/memset.c.obj"
  "/chos/kernel/arch/aarch64/mm/page_table.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/page_table.c.obj"
  "/chos/kernel/arch/aarch64/mm/tlb.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/tlb.c.obj"
  "/chos/kernel/arch/aarch64/mm/uaccess.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/uaccess.c.obj"
  "/chos/kernel/arch/aarch64/mm/vmspace.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/mm/vmspace.c.obj"
  "/chos/kernel/arch/aarch64/plat/raspi3/irq/irq.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/plat/raspi3/irq/irq.c.obj"
  "/chos/kernel/arch/aarch64/plat/raspi3/irq/timer.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/plat/raspi3/irq/timer.c.obj"
  "/chos/kernel/arch/aarch64/plat/raspi3/mm/mmparse.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/plat/raspi3/mm/mmparse.c.obj"
  "/chos/kernel/arch/aarch64/plat/raspi3/uart/uart.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/plat/raspi3/uart/uart.c.obj"
  "/chos/kernel/arch/aarch64/sched/context.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/sched/context.c.obj"
  "/chos/kernel/arch/aarch64/sched/sched.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/sched/sched.c.obj"
  "/chos/kernel/arch/aarch64/sync/ticket.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/arch/aarch64/sync/ticket.c.obj"
  "/chos/kernel/ipc/connection.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/ipc/connection.c.obj"
  "/chos/kernel/irq/ipi.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/irq/ipi.c.obj"
  "/chos/kernel/irq/timer.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/irq/timer.c.obj"
  "/chos/kernel/lib/elf.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/lib/elf.c.obj"
  "/chos/kernel/lib/printk.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/lib/printk.c.obj"
  "/chos/kernel/lib/radix.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/lib/radix.c.obj"
  "/chos/kernel/mm/buddy.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/buddy.c.obj"
  "/chos/kernel/mm/kmalloc.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/kmalloc.c.obj"
  "/chos/kernel/mm/mm.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/mm.c.obj"
  "/chos/kernel/mm/mm_check.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/mm_check.c.obj"
  "/chos/kernel/mm/pgfault_handler.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/pgfault_handler.c.obj"
  "/chos/kernel/mm/slab.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/slab.c.obj"
  "/chos/kernel/mm/vmregion.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/mm/vmregion.c.obj"
  "/chos/kernel/object/cap_group.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/object/cap_group.c.obj"
  "/chos/kernel/object/capability.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/object/capability.c.obj"
  "/chos/kernel/object/memory.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/object/memory.c.obj"
  "/chos/kernel/object/set_thread_env.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/object/set_thread_env.c.obj"
  "/chos/kernel/object/thread.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/object/thread.c.obj"
  "/chos/kernel/sched/context.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/sched/context.c.obj"
  "/chos/kernel/sched/policy_rr.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/sched/policy_rr.c.obj"
  "/chos/kernel/sched/sched.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/sched/sched.c.obj"
  "/chos/kernel/semaphore/semaphore.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/semaphore/semaphore.c.obj"
  "/chos/kernel/syscall/syscall.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/syscall/syscall.c.obj"
  "/chos/kernel/tests/barrier.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/tests/barrier.c.obj"
  "/chos/kernel/tests/tests.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/tests/tests.c.obj"
  "/chos/kernel/tests/tst_malloc.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/tests/tst_malloc.c.obj"
  "/chos/kernel/tests/tst_mutex.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/tests/tst_mutex.c.obj"
  "/chos/kernel/tests/tst_sched.c" "/chos/kernel/_build/CMakeFiles/kernel.img.dir/tests/tst_sched.c.obj"
  )
set(CMAKE_C_COMPILER_ID "GNU")

# Preprocessor definitions for this target.
set(CMAKE_TARGET_DEFINITIONS_C
  "CHCORE"
  "CHCORE_ARCH=\"aarch64\""
  "CHCORE_ARCH_AARCH64"
  "CHCORE_CROSS_COMPILE=\"aarch64-linux-gnu-\""
  "CHCORE_KERNEL_TEST"
  "CHCORE_PLAT=\"raspi3\""
  "CHCORE_PLAT_RASPI3"
  "CHCORE_ROOT_PROGRAM=\"procm.srv\""
  "LOG_LEVEL=1"
  )

# The include file search paths:
set(CMAKE_C_TARGET_INCLUDE_PATH
  "../include"
  "../include/arch/aarch64"
  "../include/arch/aarch64/plat/raspi3"
  "../arch/aarch64/boot/raspi3/include"
  )

# Targets to which this target links.
set(CMAKE_TARGET_LINKED_INFO_FILES
  )

# Fortran module output directory.
set(CMAKE_Fortran_TARGET_MODULE_DIR "")
