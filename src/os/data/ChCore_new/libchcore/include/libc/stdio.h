/*
 * Copyright (c) 2022 Institute of Parallel And Distributed Systems (IPADS)
 * ChCore-Lab is licensed under the Mulan PSL v1.
 * You can use this software according to the terms and conditions of the Mulan
 * PSL v1. You may obtain a copy of Mulan PSL v1 at:
 *     http://license.coscl.org.cn/MulanPSL
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY
 * KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 * NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE. See the
 * Mulan PSL v1 for more details.
 */

#pragma once

#include <chcore/console.h>
#include <FILE.h>

#define printf chcore_console_printf
#define cgetc  chcore_console_getc
#define putc   chcore_console_putc
#define getc   chcore_console_getc

FILE* fopen(const char* filename, const char* mode);
unsigned long fwrite(const void* src, unsigned long size, unsigned long nmemb,
                     FILE* f);
unsigned long fread(void* destv, unsigned long size, unsigned long nmemb,
                    FILE* f);
int fclose(FILE* f);
int fscanf(FILE* f, const char* fmt, ...);
int fprintf(FILE* f, const char* fmt, ...);
