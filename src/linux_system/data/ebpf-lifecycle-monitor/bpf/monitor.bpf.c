#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "../src/monitor.h"

char LICENSE[] SEC("license") = "GPL";

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

static __always_inline void fill_common_fields(struct event *e) {
    e->timestamp = bpf_ktime_get_ns();
    e->pid = bpf_get_current_pid_tgid() >> 32;
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    e->ppid = BPF_CORE_READ(task, real_parent, tgid);
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
}

// 1. Monitor Process Exec (using BTF raw tracepoint)
SEC("tp_btf/sched_process_exec")
int BPF_PROG(handle_exec, struct task_struct *p, pid_t old_pid, struct linux_binprm *bprm) {
    struct event *e;

    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;

    fill_common_fields(e);
    e->type = EVENT_PROCESS_EXEC;
    e->exit_code = 0;

    bpf_ringbuf_submit(e, 0);
    return 0;
}

// 2. Monitor Process Exit (using BTF raw tracepoint)
SEC("tp_btf/sched_process_exit")
int BPF_PROG(handle_exit, struct task_struct *p) {
    struct event *e;

    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;

    fill_common_fields(e);
    e->type = EVENT_PROCESS_EXIT;
    e->exit_code = BPF_CORE_READ(p, exit_code); 

    bpf_ringbuf_submit(e, 0);
    return 0;
}

// 3. Monitor OOM Kill (using standard tracepoint with custom struct)
struct oom_mark_victim_ctx {
    unsigned short common_type;
    unsigned char common_flags;
    unsigned char common_preempt_count;
    int common_pid;
    int pid;
};

SEC("tp/oom/mark_victim")
int handle_oom(struct oom_mark_victim_ctx *ctx) {
    struct event *e;

    e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
    if (!e) return 0;

    fill_common_fields(e);
    e->type = EVENT_OOM_KILL;
    e->target_pid = ctx->pid;
    
    bpf_ringbuf_submit(e, 0);
    return 0;
}