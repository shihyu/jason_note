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

#include <sys/types.h>
#include <chcore/assert.h>
#include <errno.h>
#include <string.h>
#include <malloc.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DIV_ROUND_UP(n, d) (((n) + (d)-1) / (d))

/* Avaliable id range is [min_id, max_id) */
struct id_manager {
    int min_id;
    int max_id;
    int curr_slot;
    u64* bitmap;
    size_t nr_slots;
};

#define BITS_PER_U64    (64)
#define DEFAULT_INIT_ID (0)

#define __assemble_idx_bit(idx, bit) ((idx)*BITS_PER_U64 + (bit))

#define __disassemble_idx_bit(id, idx, bit) \
        do {                                \
                idx = (id) / BITS_PER_U64;  \
                bit = (id) % BITS_PER_U64;  \
        } while (0)

#define __clear_bit(u64slot, bit) (u64slot) = (u64slot) & ~(1UL << (bit))

#define __set_bit(u64slot, bit) (u64slot) = (u64slot) | (1UL << (bit))

#define __query_bit(u64slot, bit) ((u64slot) & (1UL << (bit)))

static inline int __find_first_zero(u64 slot)
{
    int i;

    for (i = 0; i < BITS_PER_U64; ++i) {
        if (!__query_bit(slot, i)) {
            return i;
        }
    }

    return i;
}

static inline int alloc_id(struct id_manager* idman)
{
    size_t nr_slots_tried = 0;
    int bit;
    int id;

    while (nr_slots_tried <= idman->nr_slots) {
        /* Loop back. */
        if (idman->curr_slot >= idman->nr_slots) {
            idman->curr_slot = 0;
        }

        bit = __find_first_zero(idman->bitmap[idman->curr_slot]);

        if (bit == BITS_PER_U64) {
            /* All bits are set. Try next slot. */
next:
            idman->curr_slot += 1;
            nr_slots_tried += 1;
            continue;
        }

        id = __assemble_idx_bit(idman->curr_slot, bit);

        if (id >= idman->max_id) {
            goto next;
        }

        __set_bit(idman->bitmap[idman->curr_slot], bit);

        return id;
    }

    return -EINVAL;
}

static inline int id_manager_initialized(struct id_manager* idman)
{
    return idman->bitmap != NULL;
}

static inline int init_id_manager(struct id_manager* idman, int max_id,
                                  int min_id)
{
    int i;
    size_t __size = DIV_ROUND_UP(max_id, BITS_PER_U64);

    /* min_id must >= 0 */
    if (min_id < 0) {
        return -EINVAL;
    }

    idman->min_id = min_id;
    idman->max_id = max_id;
    idman->curr_slot = 0;
    idman->bitmap = malloc(__size* sizeof(u64));

    if (!idman->bitmap) {
        return -EINVAL;
    }

    idman->nr_slots = __size;

    /* NOTE(MK): (bitmap[0] & 0x1) is the first bit. */
    memset(idman->bitmap, 0, __size* sizeof(u64));

    /* Set min_id by reserving all the id below min_id */
    for (i = DEFAULT_INIT_ID; i < min_id; i++) {
        alloc_id(idman);
    }

    return 0;
}

static inline int free_id(struct id_manager* idman, int id)
{
    ssize_t idx, bit;

    chcore_assert(id >= idman->min_id && id < idman->max_id);

    __disassemble_idx_bit(id, idx, bit);

    if (!__query_bit(idman->bitmap[idx], bit)) {
        return -ENOENT;
    }

    __clear_bit(idman->bitmap[idx], bit);

    idman->curr_slot = idx;

    return 0;
}

static inline int query_id(struct id_manager* idman, int id)
{
    ssize_t idx, bit;

    chcore_assert(id >= idman->min_id && id < idman->max_id);

    __disassemble_idx_bit(id, idx, bit);

    if (!__query_bit(idman->bitmap[idx], bit)) {
        return -ENOENT;
    }

    return 0;
}

#ifdef __cplusplus
}

#endif
