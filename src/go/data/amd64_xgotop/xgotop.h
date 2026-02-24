#ifndef _XGOTOP_H
#define _XGOTOP_H

#include "vmlinux.h"

#include <bpf/bpf_core_read.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#if !defined(bpf_target_arm64) && !defined(bpf_target_x86)
    #error "This BPF program is only supported on arm64/x86_64"
#endif

#if defined(bpf_target_arm64)
#define __GO_G_ADDR(x) (__PT_REGS_CAST(x)->regs[28])
#elif defined(bpf_target_x86)
#define __GO_G_ADDR(x) (__PT_REGS_CAST(x)->r14)
#endif

// #define BPF_DEBUG 1

#define G_ADDR_OFFSET -8
#define G_GOID_OFFSET 152
#define G_PARENT_GOID_OFFSET 272

// From runtime/runtime2.go of Go 1.25
#define G_STATUS_DEAD 6

char LICENSE[] SEC("license") = "GPL";

struct trace_event_raw_bpf_trace_printk___x {};

#undef bpf_printk
#define bpf_printk(fmt, ...)                                                 \
({                                                                           \
    static char ____fmt[] = fmt "\0";                                        \
    if (bpf_core_type_exists(struct trace_event_raw_bpf_trace_printk___x)) { \
        bpf_trace_printk(____fmt, sizeof(____fmt) - 1, ##__VA_ARGS__);       \
    } else {                                                                 \
        ____fmt[sizeof(____fmt) - 2] = '\n';                                 \
        bpf_trace_printk(____fmt, sizeof(____fmt), ##__VA_ARGS__);           \
    }                                                                        \
})

typedef struct go_runtime_g {
    uint8_t _pad1[G_GOID_OFFSET];
    uint64_t goid; // offset=152 size=8
    uint8_t _pad2[G_PARENT_GOID_OFFSET - G_GOID_OFFSET - sizeof(uint64_t)];
    uint64_t parentGoid; // offset=272 size=8
} __attribute__((packed)) go_runtime_g;

typedef struct go_abi_type {
    uint64_t size; // offset=0 size=8
    uint8_t _pad1[15];
    uint8_t kind; // offset=23 size=1
} __attribute__((packed)) go_abi_type;

typedef struct go_abi_map_type {
    uint8_t _pad1[48];
    uint64_t key_ptr; // offset=48 size=8
    uint64_t elem_ptr; // offset=56 size=8
} __attribute__((packed)) go_abi_map_type;

typedef enum go_runtime_event_type {
    GO_RUNTIME_EVENT_TYPE_CAS_G_STATUS = 0,
    GO_RUNTIME_EVENT_TYPE_MAKE_SLICE   = 1,
    GO_RUNTIME_EVENT_TYPE_MAKE_MAP     = 2,
    GO_RUNTIME_EVENT_TYPE_NEW_OBJECT   = 3,
    GO_RUNTIME_EVENT_TYPE_NEWGOROUTINE = 4,
    GO_RUNTIME_EVENT_TYPE_GOEXIT       = 5,
} __attribute__((packed)) go_runtime_event_type_t;

typedef struct go_runtime_event {
    u64 timestamp;
    
    u32 event_type;
    u32 probe_duration_ns;

    u32 goroutine;
    u32 parent_goroutine;

    // Dynamic attributes for each event type
    // casgstatus: oldval, newval, gp.id
    // makeslice: size, kind, len, cap
    // makemap: key_size, key_kind, elem_size, elem_kind, hint
    // newobject: size, kind
    // newproc1: callerg.id, newg.id
    // goexit1: g.id, ts
    u64 attributes[5];
} __attribute__((packed)) go_runtime_event_t;

// Force emitting structs into the ELF for automatic creation of Go struct
const go_runtime_event_t *unused_go_runtime_event_t __attribute__((unused));

// TODO: This doesn't work and IDK why.
//
// // Source: https://github.com/pixie-io/pixie/blob/a95d6617f17e374ff0a79b1a49fc1abc2ca0023a/src/stirling/source_connectors/socket_tracer/bcc_bpf/go_trace_common.h#L94
// //
// // Gets the ID of the go routine currently scheduled on the current tgid and pid.
// // We do that by accessing the thread local storage (fsbase) of the current pid from the
// // task_struct. From the tls, we find a pointer to the g struct and access the goid.
// static inline uint64_t get_goid() {
//     // Get fsbase from `struct task_struct`.
//     const struct task_struct* task_ptr = (struct task_struct*)bpf_get_current_task();
//     if (!task_ptr) {
//       return 0;
//     }
  
//   #if defined(TARGET_ARCH_X86_64)
//     const void* fs_base = (void*)task_ptr->thread.fsbase;
//   #elif defined(TARGET_ARCH_AARCH64)
//     const void* fs_base = (void*)task_ptr->thread.uw.tp_value;
//   #else
//   #error Target architecture not supported
//   #endif
  
//     // Get ptr to `struct g` from 8 bytes before fsbase and then access the goID.
//     u64 goid;
//     size_t g_addr;
//     bpf_probe_read_user(&g_addr, sizeof(void*), (void*)(fs_base + G_ADDR_OFFSET));
//     bpf_probe_read_user(&goid, sizeof(void*), (void*)(g_addr + G_GOID_OFFSET));
//     // bpf_probe_read_user(&parentGoid, sizeof(void*), (void*)(g_addr + G_PARENT_GOID_OFFSET));
    
//     // return parentGoid << 32 | goid;
//     return goid;
// }

// Maps
struct {
	__uint(type, BPF_MAP_TYPE_RINGBUF);
    // TODO: If this is too small and the read workers put more messages in the Go chan
    // than processors can handle, the ringbuffer is blocked and we start to get these
    // error messages in trace_pipe:
    // testserver-3455    [001] ...11   716.382798: bpf_trace_printk: Failed to reserve ringbuf
    // We need to send another event to the Go prog with a new ringbuffer only for errors
    // (and stats in the future) and the new ACC metric (accuracy) should use that ringbuffer's
    // message count to calculate the accuracy as ACC = 100 * (total_events - errors) / total_events
	__uint(max_entries, 1 << 24); // sizeof(go_runtime_event_t) = 64 = 2^6 => 2^(24 + 6) = 1 GB
} events SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 32);  // Support up to 32 different event types
    __type(key, u32);         // Event type ID
    __type(value, u32);       // Sampling rate (0-100, representing percentage)
} sampling_rates SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 1 << 16);
    __type(key, u64); // Address of g.id
    __type(value, u64); // Address of callerg.id
} goroutines_in_creation SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_LRU_HASH);
    __uint(max_entries, 1 << 16);
    __type(key, u64); // Address of g.id
    __type(value, u64); // Timestamp of exit (unused for now)
} goroutines_in_exit SEC(".maps");

#define SEND_EVENT_WITH_SAMPLING(EVENT_TYPE, G_ID, G_PARENT_ID, ATTR0, ATTR1, ATTR2, ATTR3, ATTR4, START_NS_U64) \
        do {                                                                                                     \
            u32 event_type = (EVENT_TYPE);                                                                       \
            u32 *rate_ptr = bpf_map_lookup_elem(&sampling_rates, &event_type);                                   \
            if (rate_ptr) {                                                                                      \
                u32 rate = *rate_ptr;                                                                            \
                u32 rand = bpf_get_prandom_u32() % 100;                                                          \
                if (rand >= rate) {                                                                              \
                    break;                                                                                       \
                }                                                                                                \
            }                                                                                                    \
            go_runtime_event_t *e = bpf_ringbuf_reserve(&events, sizeof(go_runtime_event_t), 0);                 \
            if (!e) {                                                                                            \
                bpf_printk("Failed to reserve ringbuf");                                                         \
                break;                                                                                           \
            }                                                                                                    \
            e->timestamp = bpf_ktime_get_ns();                                                                   \
            e->event_type = (EVENT_TYPE);                                                                        \
            e->probe_duration_ns = (u32)(e->timestamp - (START_NS_U64));                                         \
            e->goroutine = (G_ID);                                                                               \
            e->parent_goroutine = (G_PARENT_ID);                                                                 \
            e->attributes[0] = (ATTR0);                                                                          \
            e->attributes[1] = (ATTR1);                                                                          \
            e->attributes[2] = (ATTR2);                                                                          \
            e->attributes[3] = (ATTR3);                                                                          \
            e->attributes[4] = (ATTR4);                                                                          \
            bpf_ringbuf_submit(e, 0);                                                                            \
        } while (0)

__always_inline static int get_go_g_struct_arm(struct pt_regs *ctx, struct go_runtime_g *g) {
    u64 x28 = __GO_G_ADDR(ctx);
#ifdef BPF_DEBUG
    bpf_printk("get_go_g_struct_arm: x28=%llu", x28);
#endif
    return bpf_probe_read(g, sizeof(*g), (void*)x28);
}

#endif
