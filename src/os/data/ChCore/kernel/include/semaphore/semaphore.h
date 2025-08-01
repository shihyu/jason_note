/*
 * Copyright (c) 2022 Institute of Parallel And Distributed Systems (IPADS)
 * ChCore-Lab is licensed under the Mulan PSL v1.
 * You can use this software according to the terms and conditions of the Mulan PSL v1.
 * You may obtain a copy of Mulan PSL v1 at:
 *     http://license.coscl.org.cn/MulanPSL
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v1 for more details.
 */

#pragma once

#include <common/types.h>
#include <common/list.h>

struct semaphore {
    u32 sem_count;
    u32 waiting_threads_count;
    struct list_head waiting_threads;
};

void init_sem(struct semaphore* sem);
s32 wait_sem(struct semaphore* sem, bool is_block);
s32 signal_sem(struct semaphore* sem);

/* Syscalls */
s32 sys_create_sem(void);
s32 sys_wait_sem(u32 sem_cap, bool is_block);
s32 sys_signal_sem(u32 sem_cap);
