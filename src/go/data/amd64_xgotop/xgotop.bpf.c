#include "xgotop.h"

// func casgstatus(gp *g, oldval, newval uint32)
SEC("uprobe/runtime.casgstatus")
int BPF_KPROBE(uprobe_casgstatus,
               const void *gp,
               const u32 oldval,
               const u32 newval) {
    u64 probe_start_ns = bpf_ktime_get_ns();
    u64 _ret, gp_id, g_id, g_parent_id;
    struct go_runtime_g g;

    _ret = bpf_probe_read(&g, sizeof(g), gp);
    if (_ret < 0) {
        bpf_printk("Failed to read g, ret=%d, gp=%p", _ret, gp);
        return 0;
    }

    gp_id = g.goid;

#ifdef BPF_DEBUG
    bpf_printk("casgstatus: goid=%llu, oldval=%u, newval=%u", g.goid, oldval, newval);
#endif

    _ret = get_go_g_struct_arm(ctx, &g);
    if (_ret < 0) {
        bpf_printk("Failed to read g, ret=%d", _ret);
        return 0;
    }

    g_id = g.goid;
    g_parent_id = g.parentGoid;

    if (newval == G_STATUS_DEAD) {
        u64 *ts = bpf_map_lookup_elem(&goroutines_in_exit, &gp_id);
        if (ts != NULL) {
            // Still send the event for the CAS_G_STATUS
            SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_CAS_G_STATUS, g_id, g_parent_id, oldval, newval, gp_id, 0, 0, probe_start_ns);
            
            // Notify the userspace program that the goroutine has exited
            SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_GOEXIT, g_id, g_parent_id, gp_id, *ts, 0, 0, 0, probe_start_ns);
            _ret = bpf_map_delete_elem(&goroutines_in_exit, &g_id);
            if (_ret < 0) {
                bpf_printk("Failed to delete goroutines_in_exit, ret=%d", _ret);
                return 0;
            }

            // No need to process further as the goroutine has exited
            return 0;
        }
    }

    u64 *callerg_id = bpf_map_lookup_elem(&goroutines_in_creation, &g_id);
    if (callerg_id != NULL) {
        // This function is called inside the newproc1 function, so we need to send an event for the caller.
        // We cannot use a uretprobe on newproc1 so we're using this trick!
        SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_NEWGOROUTINE, g_id, g_parent_id, *callerg_id, gp_id, 0, 0, 0, probe_start_ns);
        _ret = bpf_map_delete_elem(&goroutines_in_creation, &g_id);
        if (_ret < 0) {
            bpf_printk("Failed to delete goroutines_in_creation, ret=%d", _ret);
            return 0;
        }
    }

    SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_CAS_G_STATUS, g_id, g_parent_id, oldval, newval, gp_id, 0, 0, probe_start_ns);
    return 0;
}

// func newobject(typ *_type) unsafe.Pointer {
// 	return mallocgc(typ.Size_, typ, true)
// }
// _type is abi.Type
SEC("uprobe/runtime.newobject")
int BPF_KPROBE(uprobe_newobject,
               const void *typ) {
    u64 probe_start_ns = bpf_ktime_get_ns();
    u64 _ret;
    struct go_runtime_g g;

    _ret = get_go_g_struct_arm(ctx, &g);
    if (_ret < 0) {
        bpf_printk("Failed to read g, ret=%d", _ret);
        return 0;
    }
#ifdef BPF_DEBUG
    bpf_printk("newobject: goid=%llu, parentGoid=%llu", g.goid, g.parentGoid);
#endif

    struct go_abi_type go_type;
    _ret = bpf_probe_read(&go_type, sizeof(go_type), typ);
    if (_ret < 0) {
        bpf_printk("Failed to read go_type, ret=%d, go_type=%p", _ret, go_type);
        return 0;
    }

#ifdef BPF_DEBUG
    bpf_printk("newobject: size=%llu, kind=%llu", go_type.size, go_type.kind);
#endif

    SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_NEW_OBJECT, g.goid, g.parentGoid, go_type.size, go_type.kind, 0, 0, 0, probe_start_ns);
    return 0;
}

// func makeslice(et *_type, len, cap int) unsafe.Pointer 
SEC("uprobe/runtime.makeslice")
int BPF_KPROBE(uprobe_makeslice,
               const void *typ,
               const u64 len,
               const u64 cap) {
    u64 probe_start_ns = bpf_ktime_get_ns();
    u64 _ret;

    struct go_runtime_g g;
    _ret = get_go_g_struct_arm(ctx, &g);
    if (_ret < 0) {
        bpf_printk("Failed to read g, ret=%d", _ret);
        return 0;
    }

#ifdef BPF_DEBUG
    bpf_printk("makeslice: goid=%llu, parentGoid=%llu", g.goid, g.parentGoid);
#endif

    struct go_abi_type go_type;
    _ret = bpf_probe_read(&go_type, sizeof(go_type), typ);
    if (_ret < 0) {
        bpf_printk("Failed to read go_type, ret=%d, go_type=%p", _ret, go_type);
        return 0;
    }

#ifdef BPF_DEBUG
    bpf_printk("makeslice: size=%llu, kind=%llu", go_type.size, go_type.kind);
    bpf_printk("makeslice: len=%llu, cap=%llu", len, cap);
#endif

    SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_MAKE_SLICE, g.goid, g.parentGoid, go_type.size, go_type.kind, len, cap, 0, probe_start_ns);
    return 0;
}

// func makemap(t *abi.MapType, hint int, m *maps.Map) *maps.Map
SEC("uprobe/runtime.makemap")
int BPF_KPROBE(uprobe_makemap,
               const void *typ,
               const u64 hint,
               const void *m) {
    u64 probe_start_ns = bpf_ktime_get_ns();
    u64 _ret;

    struct go_runtime_g g;
    _ret = get_go_g_struct_arm(ctx, &g);
    if (_ret < 0) {
        bpf_printk("Failed to read g, ret=%d", _ret);
        return 0;
    }
#ifdef BPF_DEBUG
    bpf_printk("makemap: goid=%llu, parentGoid=%llu", g.goid, g.parentGoid);
#endif

    struct go_abi_map_type go_map;
    _ret = bpf_probe_read(&go_map, sizeof(go_map), typ);
    if (_ret < 0) {
        bpf_printk("Failed to read go_map, ret=%d, go_map=%p", _ret, go_map);
        return 0;
    }
    
    struct go_abi_type key_type, elem_type;
    _ret = bpf_probe_read(&key_type, sizeof(key_type), (void*)go_map.key_ptr);
    if (_ret < 0) {
        bpf_printk("Failed to read key_type, ret=%d, key_type=%p", _ret, key_type);
        return 0;
    }
    
    _ret = bpf_probe_read(&elem_type, sizeof(elem_type), (void*)go_map.elem_ptr);
    if (_ret < 0) {
        bpf_printk("Failed to read elem_type, ret=%d, elem_type=%p", _ret, elem_type);
        return 0;
    }
    
#ifdef BPF_DEBUG
    bpf_printk("makemap: key size=%llu, key kind=%llu", key_type.size, key_type.kind);
    bpf_printk("makemap: elem size=%llu, elem kind=%llu, hint=%llu", elem_type.size, elem_type.kind, hint);
#endif
    
    SEND_EVENT_WITH_SAMPLING(GO_RUNTIME_EVENT_TYPE_MAKE_MAP, g.goid, g.parentGoid, key_type.size, key_type.kind, elem_type.size, elem_type.kind, hint, probe_start_ns);
    return 0;
}

// func newproc1(fn *funcval, callergp *g, callerpc uintptr, parked bool, waitreason waitReason) *g
SEC("uprobe/runtime.newproc1")
int BPF_KPROBE(uprobe_newproc1,
               const void *__skip_fn,
               const void *callergp) {
    u64 _ret, goid, callergoid;
    struct go_runtime_g g;

    _ret = bpf_probe_read(&g, sizeof(g), callergp);
    if (_ret < 0) {
        bpf_printk("newproc1: failed to read callerg, ret=%d, callergp=%p", _ret, callergp);
        return 0;
    }

    callergoid = g.goid;
    
    _ret = get_go_g_struct_arm(ctx, &g);
    if (_ret < 0) {
        bpf_printk("newproc1: failed to read g, ret=%d", _ret);
        return 0;
    }

    goid = g.goid;

#ifdef BPF_DEBUG
    bpf_printk("newproc1: callerg.id=%llu, callerg.parent.id=%llu", callergoid, g.parentGoid);
    bpf_printk("newproc1: g.id=%llu, g.parent.id=%llu", goid, g.parentGoid);
#endif

    _ret = bpf_map_update_elem(&goroutines_in_creation, &goid, &callergoid, BPF_ANY);
    if (_ret < 0) {
        bpf_printk("newproc1: failed to update goroutines_in_creation, ret=%d", _ret);
        return 0;
    }

    return 0;
}

// func goexit1()
SEC("uprobe/runtime.goexit1")
int BPF_KPROBE(uprobe_goexit1) {
    u64 _ret;

    struct go_runtime_g g;
    _ret = get_go_g_struct_arm(ctx, &g);
    if (_ret < 0) {
        bpf_printk("goexit1: failed to read g, ret=%d", _ret);
        return 0;
    }

#ifdef BPF_DEBUG
    bpf_printk("goexit1: goid=%llu, parentGoid=%llu", g.goid, g.parentGoid);
#endif

    u64 ts = bpf_ktime_get_ns();
    _ret = bpf_map_update_elem(&goroutines_in_exit, &g.goid, &ts, BPF_ANY);
    if (_ret < 0) {
        bpf_printk("goexit1: failed to update goroutines_in_exit, ret=%d", _ret);
        return 0;
    }

    return 0;
}