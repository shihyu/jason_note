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

#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#include "defs.h"


int init_fsm(void);
int fsm_init_procmgr_struct(int cap);

int fsm_mount_fs(const char* path, const char* mount_point);
int fsm_umount_fs(const char* path);

void fsm_dispatch(ipc_msg_t* ipc_msg, u64 client_badge);
