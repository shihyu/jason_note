# bcc 參考指南

用於搜索 (Ctrl-F) 和參考。如需教程，請從 [tutorial.md](tutorial.md) 開始。

該指南尚未完成。如果感覺有遺漏的內容，請查看 bcc 和內核源碼。如果確認確實有遺漏，請發送拉取請求進行修復，並協助所有人。

## 目錄

- [bcc 參考指南](#bcc-參考指南)
  - [目錄](#目錄)
- [BPF C](#bpf-c)
  - [Events \& Arguments](#events--arguments)
    - [1. kprobes](#1-kprobes)
    - [2. kretprobes](#2-kretprobes)
    - [3. Tracepoints](#3-tracepoints)
    - [4. uprobes](#4-uprobes)
    - [6. USDT探測點](#6-usdt探測點)
    - [7. 原始跟蹤點](#7-原始跟蹤點)
    - [8. 系統調用跟蹤點](#8-系統調用跟蹤點)
    - [9. kfuncs](#9-kfuncs)
    - [10. kretfuncs](#10-kretfuncs)
    - [11. LSM Probes](#11-lsm-probes)
    - [12. BPF迭代器](#12-bpf迭代器)
  - [數據](#數據)
    - [1. bpf\_probe\_read\_kernel()](#1-bpf_probe_read_kernel)
    - [2. bpf\_probe\_read\_kernel\_str()".\`\`\`shell](#2-bpf_probe_read_kernel_strshell)
    - [3. bpf\_ktime\_get\_ns()](#3-bpf_ktime_get_ns)
    - [4. bpf\_get\_current\_pid\_tgid()](#4-bpf_get_current_pid_tgid)
    - [5. bpf\_get\_current\_uid\_gid()](#5-bpf_get_current_uid_gid)
    - [6. bpf\_get\_current\_comm()](#6-bpf_get_current_comm)
    - [7. bpf\_get\_current\_task()](#7-bpf_get_current_task)
    - [8. bpf\_log2l()](#8-bpf_log2l)
    - [9. bpf\_get\_prandom\_u32()](#9-bpf_get_prandom_u32)
    - [10. bpf\_probe\_read\_user()](#10-bpf_probe_read_user)
    - [11. bpf\_probe\_read\_user\_str()](#11-bpf_probe_read_user_str)
    - [12. bpf\_get\_ns\_current\_pid\_tgid()](#12-bpf_get_ns_current_pid_tgid)
  - [調試](#調試)
    - [1. bpf\_override\_return()](#1-bpf_override_return)
  - [輸出](#輸出)
    - [1. bpf\_trace\_printk()](#1-bpf_trace_printk)
    - [2. BPF\_PERF\_OUTPUT](#2-bpf_perf_output)
    - [3. perf\_submit()](#3-perf_submit)
    - [4. perf\_submit\_skb()](#4-perf_submit_skb)
    - [5. BPF\_RINGBUF\_OUTPUT](#5-bpf_ringbuf_output)
    - [6. ringbuf\_output（）](#6-ringbuf_output)
    - [7. ringbuf\_reserve()](#7-ringbuf_reserve)
    - [8. ringbuf\_submit（）](#8-ringbuf_submit)
    - [9. ringbuf\_discard()](#9-ringbuf_discard)
  - [Maps](#maps)
    - [1. BPF\_TABLE](#1-bpf_table)
      - [固定映射](#固定映射)
    - [2. BPF\_HASH](#2-bpf_hash)
    - [3. BPF\_ARRAY](#3-bpf_array)
    - [4. BPF\_HISTOGRAM](#4-bpf_histogram)
    - [5. BPF\_STACK\_TRACE](#5-bpf_stack_trace)
    - [6. BPF\_PERF\_ARRAY](#6-bpf_perf_array)
    - [7. BPF\_PERCPU\_HASH](#7-bpf_percpu_hash)
    - [8. BPF\_PERCPU\_ARRAY](#8-bpf_percpu_array)
    - [9. BPF\_LPM\_TRIE](#9-bpf_lpm_trie)
    - [10. BPF\_PROG\_ARRAY](#10-bpf_prog_array)
    - [11. BPF\_DEVMAP](#11-bpf_devmap)
    - [12. BPF\_CPUMAP](#12-bpf_cpumap)
    - [13. BPF\_XSKMAP](#13-bpf_xskmap)
    - [14. BPF\_ARRAY\_OF\_MAPS](#14-bpf_array_of_maps)
    - [15. BPF\_HASH\_OF\_MAPS](#15-bpf_hash_of_maps)
    - [16. BPF\_STACK](#16-bpf_stack)
    - [17. BPF\_QUEUE](#17-bpf_queue)
    - [18. BPF\_SOCKHASH](#18-bpf_sockhash)
    - [19. map.lookup()](#19-maplookup)
    - [20. map.lookup\_or\_try\_init()](#20-maplookup_or_try_init)
    - [21. map.delete()](#21-mapdelete)
    - [22. map.update()](#22-mapupdate)
    - [23. map.insert()](#23-mapinsert)
    - [24. map.increment()](#24-mapincrement)
    - [25. map.get\_stackid()](#25-mapget_stackid)
    - [26. map.perf\_read()](#26-mapperf_read)
    - [27. map.call()](#27-mapcall)
    - [28. map.redirect\_map()](#28-mapredirect_map)
    - [29. map.push()](#29-mappush)
    - [30. map.pop()](#30-mappop)
    - [31. map.peek()](#31-mappeek)
    - [32. map.sock\_hash\_update()](#32-mapsock_hash_update)
    - [33. map.msg\_redirect\_hash()](#33-mapmsg_redirect_hash)
    - [34. map.sk\_redirect\_hash()](#34-mapsk_redirect_hash)
  - [許可證](#許可證)
  - [Rewriter](#rewriter)
- [bcc Python](#bcc-python)
  - [初始化](#初始化)
    - [1. BPF](#1-bpf)
  - [事件](#事件)
    - [1. attach\_kprobe()](#1-attach_kprobe)
    - [2. attach\_kretprobe()](#2-attach_kretprobe)
    - [3. attach\_tracepoint()](#3-attach_tracepoint)
    - [4. attach\_uprobe()](#4-attach_uprobe)
    - [5. attach\_uretprobe()](#5-attach_uretprobe)
    - [6. USDT.enable\_probe()](#6-usdtenable_probe)
    - [7. attach\_raw\_tracepoint()](#7-attach_raw_tracepoint)
    - [8. attach\_raw\_socket()](#8-attach_raw_socket)
    - [9. attach\_xdp()](#9-attach_xdp)
      - [1. XDP\_FLAGS\_UPDATE\_IF\_NOEXIST](#1-xdp_flags_update_if_noexist)
      - [2. XDP\_FLAGS\_SKB\_MODE](#2-xdp_flags_skb_mode)
      - [3. XDP\_FLAGS\_DRV\_MODE](#3-xdp_flags_drv_mode)
      - [4. XDP\_FLAGS\_HW\_MODE](#4-xdp_flags_hw_mode)
    - [10. attach\_func()](#10-attach_func)
    - [12. detach\_kprobe()](#12-detach_kprobe)
    - [13. detach\_kretprobe()](#13-detach_kretprobe)
  - [調試輸出](#調試輸出)
    - [1. trace\_print()](#1-trace_print)
    - [2. trace\_fields()](#2-trace_fields)
  - [輸出 API](#輸出-api)
    - [1. perf\_buffer\_poll()](#1-perf_buffer_poll)
    - [2. ring\_buffer\_poll()](#2-ring_buffer_poll)
    - [3. ring\_buffer\_consume()](#3-ring_buffer_consume)
  - [Map APIs](#map-apis)
    - [1. get\_table()](#1-get_table)
    - [2. open\_perf\_buffer()](#2-open_perf_buffer)
    - [4. values()](#4-values)
    - [5. clear()](#5-clear)
    - [6. items\_lookup\_and\_delete\_batch()](#6-items_lookup_and_delete_batch)
    - [7. items\_lookup\_batch()](#7-items_lookup_batch)
    - [8. items\_delete\_batch()](#8-items_delete_batch)
    - [9. items\_update\_batch()](#9-items_update_batch)
    - [11. print\_linear\_hist()".語法: ```table.print_linear_hist(val_type="value", section_header="Bucket ptr", section_print_fn=None)```](#11-print_linear_hist語法-tableprint_linear_histval_typevalue-section_headerbucket-ptr-section_print_fnnone)
    - [12. open\_ring\_buffer()](#12-open_ring_buffer)
    - [13. push()](#13-push)
    - [14. pop()](#14-pop)
    - [15. peek()](#15-peek)
  - [輔助方法](#輔助方法)
    - [1. ksym()](#1-ksym)
    - [2. ksymname()](#2-ksymname)
    - [3. sym()](#3-sym)
    - [4. num\_open\_kprobes()](#4-num_open_kprobes)
    - [5. get\_syscall\_fnname()](#5-get_syscall_fnname)
- [BPF 錯誤](#bpf-錯誤)
  - [1. Invalid mem access](#1-invalid-mem-access)
  - [2. 無法從專有程序調用 GPL-only 函數](#2-無法從專有程序調用-gpl-only-函數)
- [環境變量](#環境變量)
  - [1. 內核源代碼目錄](#1-內核源代碼目錄)
  - [2. 內核版本覆蓋](#2-內核版本覆蓋)

# BPF C

本節介紹了 bcc 程序的 C 部分。

## Events & Arguments

### 1. kprobes

語法：kprobe__*kernel_function_name*

```kprobe__``` 是一個特殊的前綴，用於創建一個 kprobe（對內核函數調用的動態跟蹤），後面跟著的是內核函數的名稱。你也可以通過聲明一個普通的 C 函數，然後使用 Python 的 ```BPF.attach_kprobe()```（稍後會介紹）將其與一個內核函數關聯起來來使用 kprobe。

參數在函數聲明中指定：kprobe__*kernel_function_name*(struct pt_regs *ctx [, *argument1* ...])

例如：

```c
int kprobe__tcp_v4_connect(struct pt_regs *ctx, struct sock *sk) {
    [...]
}
```

這會使用 kprobe 對 tcp_v4_connect() 內核函數進行插裝，並使用以下參數：

- ```struct pt_regs *ctx```: 寄存器和 BPF 上下文。
- ```struct sock *sk```: tcp_v4_connect() 的第一個參數。

第一個參數始終是 ```struct pt_regs *```，其餘的是函數的參數（如果你不打算使用它們，則不需要指定）。

示例代碼：
[code](https://github.com/iovisor/bcc/blob/4afa96a71c5dbfc4c507c3355e20baa6c184a3a8/examples/tracing/tcpv4connect.py#L28)（[輸出結果](https://github.com/iovisor/bcc/blob/5bd0eb21fd148927b078deb8ac29fff2fb044b66/examples/tracing/tcpv4connect_example.txt#L8)),"."[code](https://github.com/iovisor/bcc/commit/310ab53710cfd46095c1f6b3e44f1dbc8d1a41d8#diff-8cd1822359ffee26e7469f991ce0ef00R26) （[output](https://github.com/iovisor/bcc/blob/3b9679a3bd9b922c736f6061dc65cb56de7e0250/examples/tracing/bitehist_example.txt#L6))

<!--- 這裡無法添加搜索鏈接，因為GitHub目前無法處理"kprobe__"所需的部分詞搜索--->

### 2. kretprobes

語法: kretprobe__*kernel_function_name*

```kretprobe__```是一個特殊的前綴，它創建了一個kretprobe（對提供的內核函數名進行動態追蹤，跟蹤內核函數的返回）。您也可以通過聲明一個普通的C函數，然後使用Python的```BPF.attach_kretprobe()```（稍後介紹）將其與內核函數關聯起來，來使用kretprobes。

返回值可用作```PT_REGS_RC(ctx)```，給定函數聲明為：kretprobe__*kernel_function_name*(struct pt_regs *ctx)

例如:

```C
int kretprobe__tcp_v4_connect(struct pt_regs *ctx)
{
    int ret = PT_REGS_RC(ctx);
    [...]
}
```

這個例子使用kretprobe來對tcp_v4_connect()內核函數的返回進行檢測，並將返回值存儲在```ret```中。

現有的用法示例:
[code](https://github.com/iovisor/bcc/blob/4afa96a71c5dbfc4c507c3355e20baa6c184a3a8/examples/tracing/tcpv4connect.py#L38) （[output](https://github.com/iovisor/bcc/blob/5bd0eb21fd148927b078deb8ac29fff2fb044b66/examples/tracing/tcpv4connect_example.txt#L8))

### 3. Tracepoints

語法: TRACEPOINT_PROBE(*category*, *event*)

這是一個宏，用於對由*category*:*event*定義的tracepoint進行追蹤。

tracepoint名稱為`<category>:<event>`。
probe函數名為`tracepoint__<category>__<event>`。

參數在一個```args```結構體中可用，這些參數是tracepoint的參數。列出這些參數的一種方法是在/sys/kernel/debug/tracing/events/*category*/*event*/format下查看相關的格式文件。"`args` 結構體可用於替代 `ctx`，作為需要上下文作為參數的每個函數中的參數。這包括特別是 [perf_submit()](#3-perf_submit)。

例如：

```C
TRACEPOINT_PROBE(random, urandom_read) {
    // args is from /sys/kernel/debug/tracing/events/random/urandom_read/format
    bpf_trace_printk("%d\\n", args->got_bits);
    return 0;
}
```

這會給 `random:urandom_read` 追蹤點注入代碼，並打印出追蹤點參數 `got_bits`。
在使用 Python API 時，此探針會自動附加到正確的追蹤點目標上。
對於 C++，可以通過明確指定追蹤點目標和函數名來附加此追蹤點探針：
`BPF::attach_tracepoint("random:urandom_read", "tracepoint__random__urandom_read")`
注意，上面定義的探針函數的名稱是 `tracepoint__random__urandom_read`。

實際示例：
[code](https://github.com/iovisor/bcc/blob/a4159da8c4ea8a05a3c6e402451f530d6e5a8b41/examples/tracing/urandomread.py#L19) ([output](https://github.com/iovisor/bcc/commit/e422f5e50ecefb96579b6391a2ada7f6367b83c4#diff-41e5ecfae4a3b38de5f4e0887ed160e5R10))，
[search /examples](https://github.com/iovisor/bcc/tree/master/examples)，
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 4. uprobes

這些是通過在 C 中聲明一個普通函數，然後在 Python 中通過 `BPF.attach_uprobe()` 將其關聯為 uprobes 探針來進行注入的（稍後會介紹）。

可以使用 `PT_REGS_PARM` 宏來檢查參數。

例如：

```C
int count(struct pt_regs *ctx) {
    char buf[64];
    bpf_probe_read_user(&buf, sizeof(buf), (void *)PT_REGS_PARM1(ctx));
    bpf_trace_printk("%s %d", buf, PT_REGS_PARM2(ctx));
    return(0);
}
```

這將讀取第一個參數作為字符串，然後用第二個參數作為整數打印出來。

實際示例：
[code](https://github.com/iovisor/bcc/blob/4afa96a71c5dbfc4c507c3355e20baa6c184a3a8/examples/tracing/strlen_count.py#L26)。### 5。uretprobes

這些是通過在C中聲明一個普通函數，然後在Python中通過```BPF.attach_uretprobe()```將其關聯為uretprobe探測點（稍後詳述）來進行插裝的。

返回值可以通過```PT_REGS_RC(ctx)```訪問，前提是有一個如下聲明的函數：*function_name*(struct pt_regs *ctx)

例如：

```C
BPF_HISTOGRAM(dist);
int count(struct pt_regs *ctx) {
    dist.increment(PT_REGS_RC(ctx));
    return 0;
}
```

這會遞增由返回值索引的```dist```直方圖中的存儲桶。

現場演示示例：
[code](https://github.com/iovisor/bcc/blob/4afa96a71c5dbfc4c507c3355e20baa6c184a3a8/examples/tracing/strlen_hist.py#L39) ([output](https://github.com/iovisor/bcc/blob/4afa96a71c5dbfc4c507c3355e20baa6c184a3a8/examples/tracing/strlen_hist.py#L15)),
[code](https://github.com/iovisor/bcc/blob/4afa96a71c5dbfc4c507c3355e20baa6c184a3a8/tools/bashreadline.py) ([output](https://github.com/iovisor/bcc/commit/aa87997d21e5c1a6a20e2c96dd25eb92adc8e85d#diff-2fd162f9e594206f789246ce97d62cf0R7))

### 6. USDT探測點

這些是用戶靜態定義追蹤（USDT）探測點，可以放置在某些應用程序或庫中，以提供用戶級別等效的跟蹤點。用於USDT支持的主要BPF方法是```enable_probe()```。通過在C中聲明一個普通函數，然後在Python中通過```USDT.enable_probe()```將其關聯為USDT探測點來進行插裝。

可以通過以下方式讀取參數：bpf_usdt_readarg(*index*, ctx, &addr)

例如：

```C
int do_trace(struct pt_regs *ctx) {
    uint64_t addr;
    char path[128];
    bpf_usdt_readarg(6, ctx, &addr);
    bpf_probe_read_user(&path, sizeof(path), (void *)addr);
    bpf_trace_printk("path:%s\\n", path);
    return 0;
};
```

這會讀取第六個USDT參數，然後將其作為字符串存儲到```path```中。當使用C API中的```BPF::init```的第三個參數進行USDT的初始化時，如果任何USDT無法進行```init```，則整個```BPF::init```都會失敗。如果您對一些USDT無法進行```init```感到滿意，則在調用```BPF::init```之前使用```BPF::init_usdt```。

### 7. 原始跟蹤點

語法：RAW_TRACEPOINT_PROBE(*event*)

這是一個宏，用於儀表化由*event*定義的原始跟蹤點。

該參數是指向結構體```bpf_raw_tracepoint_args```的指針，該結構體定義在[bpf.h](https://github.com/iovisor/bcc/blob/master/src/cc/compat/linux/virtual_bpf.h)中。結構體字段```args```包含了原始跟蹤點的所有參數，可以在[include/trace/events](https://github.com/torvalds/linux/tree/master/include/trace/events)目錄中找到。

例如：

```C
RAW_TRACEPOINT_PROBE(sched_switch)
{
    // TP_PROTO(bool preempt, struct task_struct *prev, struct task_struct *next)
    struct task_struct *prev = (struct task_struct *)ctx->args[1];
    struct task_struct *next= (struct task_struct *)ctx->args[2];
    s32 prev_tgid, next_tgid;

    bpf_probe_read_kernel(&prev_tgid, sizeof(prev->tgid), &prev->tgid);
    bpf_probe_read_kernel(&next_tgid, sizeof(next->tgid), &next->tgid);
    bpf_trace_printk("%d -> %d\\n", prev_tgid, next_tgid);
}
```

這將儀表化sched:sched_switch跟蹤點，並打印prev和next tgid。

### 8. 系統調用跟蹤點

語法：```syscall__SYSCALLNAME```。```syscall__```是一個特殊的前綴，用於為提供的系統調用名稱創建一個kprobe。您可以通過聲明一個普通的C函數，然後使用Python的```BPF.get_syscall_fnname(SYSCALLNAME)```和```BPF.attach_kprobe()```來使用它。

參數在函數聲明中指定: ```syscall__SYSCALLNAME(struct pt_regs *ctx, [, argument1 ...])```.

例如：

```C
int syscall__execve(struct pt_regs *ctx,
    const char __user *filename,
    const char __user *const __user *__argv,
    const char __user *const __user *__envp)
{
    [...]
}
```

這將對execve系統調用進行探查。

第一個參數始終是```struct pt_regs *```，其餘的參數是函數的參數（如果您不打算使用它們，則無需指定）。

相應的Python代碼：

```Python
b = BPF(text=bpf_text)
execve_fnname = b.get_syscall_fnname("execve")
b.attach_kprobe(event=execve_fnname, fn_name="syscall__execve")
```

示例：
[code](https://github.com/iovisor/bcc/blob/552658edda09298afdccc8a4b5e17311a2d8a771/tools/execsnoop.py#L101) ([output](https://github.com/iovisor/bcc/blob/552658edda09298afdccc8a4b5e17311a2d8a771/tools/execsnoop_example.txt#L8))

### 9. kfuncs

語法：KFUNC_PROBE(*function*, typeof(arg1) arg1, typeof(arg2) arge ...)

這是一個通過跳板來在內核函數執行**之前**對其進行探查的宏。它由*function*名稱和*argX*定義的函數參數組成。

例如：

```C
KFUNC_PROBE(do_sys_open, int dfd, const char *filename, int flags, int mode)
{
    ...
}
```

這將對do_sys_open內核函數進行探查，並將其參數作為標準參數值訪問。

示例：
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 10. kretfuncs

語法：KRETFUNC_PROBE(*event*, typeof(arg1) arg1, typeof(arg2) arge ..., int ret)

這是一個通過跳板來在內核函數執行**之前**探查的宏。
格式：僅返回翻譯後的內容，不包括原始文本。*在*函數執行之後。它由*函數*名稱和定義為*argX*的函數參數定義。

探針的最後一個參數是檢測函數的返回值。

例如：

```C
KRETFUNC_PROBE(do_sys_open, int dfd, const char *filename, int flags, int mode, int ret)
{
    ...
```

這會對do_sys_open內核函數進行檢測，並將其參數作為標準參數值一起與其返回值一起提取。

原地示例：
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 11. LSM Probes

語法：LSM_PROBE(*hook*, typeof(arg1) arg1, typeof(arg2) arg2 ...)

這是一種將LSM掛鉤作為BPF程序進行檢測的宏。它可以用於審計安全事件和實施BPF中的MAC安全策略。
它通過指定掛鉤名及其參數來定義。

可以在
[include/linux/security.h](https://github.com/torvalds/linux/blob/v5.15/include/linux/security.h#L260)
中找到掛鉤名稱，方法是取security_hookname之類的函數名，然後只保留`hookname`部分。
例如，`security_bpf`僅變成了`bpf`。

與其他BPF程序類型不同，LSM探針中指定的返回值是很重要的。返回值為0表示掛鉤成功，而
任何非零的返回值都會導致掛鉤失敗和拒絕安全操作。

以下示例對一個拒絕所有未來BPF操作的掛鉤進行了檢測：

```C
LSM_PROBE(bpf, int cmd, union bpf_attr *attr, unsigned int size)
{
    return -EPERM;
}
```

這會對`security_bpf`掛鉤進行檢測，並導致其返回`-EPERM`。
將`return -EPERM`更改為`return 0`會導致BPF程序允許該操作。

LSM探針需要至少一個5.7+內核，並設置了以下配置選項：

- `CONFIG_BPF_LSM=y`
- `CONFIG_LSM` 逗號分隔的字符串必須包含"bpf"（例如，
  `CONFIG_LSM="lockdown,yama,bpf"`)

原地示例："[搜索/tests](https://github.com/iovisor/bcc/tree/master/tests)

### 12. BPF迭代器

語法: BPF_ITER(target)

這是一個宏，用於定義一個bpf迭代器程序的程序簽名。參數 *target* 指定要迭代的內容。

目前，內核沒有接口來發現支持哪些目標。一個好的查找支持內容的地方是在 [tools/testing/selftests/bpf/prog_test/bpf_iter.c](https://github.com/torvalds/linux/blob/master/tools/testing/selftests/bpf/prog_tests/bpf_iter.c) ，一些示例bpf迭代器程序位於 [tools/testing/selftests/bpf/progs](https://github.com/torvalds/linux/tree/master/tools/testing/selftests/bpf/progs) ，其中文件名以 *bpf_iter* 為前綴。

以下示例為 *task* 目標定義了一個程序，該程序遍歷內核中的所有任務。

```C
BPF_ITER(task)
{
  struct seq_file *seq = ctx->meta->seq;
  struct task_struct *task = ctx->task;

  if (task == (void *)0)
    return 0;

  ... task->pid, task->tgid, task->comm, ...
  return 0;
}
```

在5.8內核中引入了BPF迭代器，可以用於任務（task）、任務文件（task_file）、bpf map、netlink_sock和ipv6_route。在5.9中，對tcp/udp socket和bpf map元素（hashmap、arraymap和sk_local_storage_map）遍歷添加了支持。

## 數據

### 1. bpf_probe_read_kernel()

語法: ```int bpf_probe_read_kernel(void *dst, int size, const void*src)```

返回值: 成功時返回0

該函數將從內核地址空間複製size字節到BPF堆棧，以便BPF之後可以對其進行操作。為了安全起見，所有內核內存讀取都必須通過bpf_probe_read_kernel()進行。在某些情況下，比如解引用內核變量時，這會自動發生，因為bcc會重新編寫BPF程序以包含所需的bpf_probe_read_kernel()。

現場示例：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 2. bpf_probe_read_kernel_str()".```shell

語法：```int bpf_probe_read_kernel_str(void *dst, int size, const void*src)```

返回值：

- \> 0 成功時字符串長度（包括結尾的NULL字符）
- \< 0 出錯

該函數將一個以`NULL`結尾的字符串從內核地址空間複製到BPF堆棧中，以便BPF以後可以對其進行操作。如果字符串的長度小於size，則目標不會用更多的`NULL`字節進行填充。如果字符串的長度大於size，則只會複製`size - 1`個字節，並將最後一個字節設置為`NULL`。

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 3. bpf_ktime_get_ns()

語法：```u64 bpf_ktime_get_ns(void)```

返回值：u64 納秒數。從系統啟動時間開始計數，但在掛起期間停止計數。

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 4. bpf_get_current_pid_tgid()

語法：```u64 bpf_get_current_pid_tgid(void)```

返回值：```current->tgid << 32 | current->pid```

返回進程ID位於低32位（內核視圖的PID，在用戶空間通常表示為線程ID），線程組ID位於高32位（在用戶空間通常被認為是PID）。通過直接設置為u32類型，我們丟棄了高32位。

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 5. bpf_get_current_uid_gid()

語法：```u64 bpf_get_current_uid_gid(void)```

返回值：```current_gid << 32 | current_uid```

返回用戶ID和組ID。

示例：[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples), [搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 6. bpf_get_current_comm()

語法: ```bpf_get_current_comm(char *buf, int size_of_buf)```

返回值: 成功時返回0

將當前進程的名稱填充到第一個參數地址中。它應該是一個指向字符數組的指針，大小至少為TASK_COMM_LEN，該變量在linux/sched.h中定義。例如:

```C
#include <linux/sched.h>

int do_trace(struct pt_regs *ctx) {
    char comm[TASK_COMM_LEN];
    bpf_get_current_comm(&comm, sizeof(comm));
[...]
```

現有示例:
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples), [搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 7. bpf_get_current_task()

語法: ```bpf_get_current_task()```

返回值: 返回指向當前任務的struct task_struct指針。

返回指向當前任務的task_struct對象的指針。該輔助函數可用於計算進程的CPU時間，標識內核線程，獲取當前CPU的運行隊列或檢索許多其他信息。

在Linux 4.13中，由於字段隨機化的問題，您可能需要在包含之前定義兩個#define指令:

```C
#define randomized_struct_fields_start  struct {
#define randomized_struct_fields_end    };
#include <linux/sched.h>

int do_trace(void *ctx) {
    struct task_struct *t = (struct task_struct *)bpf_get_current_task();
[...]
```

現有示例:
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples), [搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 8. bpf_log2l()

語法: ```unsigned int bpf_log2l(unsigned long v)```

返回提供的值的log-2。這通常用於創建直方圖的索引，以構建2的冪次直方圖。在原地示例：

[搜索/示例](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/工具](https://github.com/iovisor/bcc/tree/master/tools)

### 9. bpf_get_prandom_u32()

語法：```u32 bpf_get_prandom_u32()```

返回一個偽隨機的 u32。

在原地示例：

[搜索/示例](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/工具](https://github.com/iovisor/bcc/tree/master/tools)

### 10. bpf_probe_read_user()

語法：```int bpf_probe_read_user(void *dst, int size, const void*src)```

返回值：成功時返回0

該函數嘗試安全地從用戶地址空間讀取size個字節到BPF棧中，以便BPF之後可以操作它。為確保安全，所有用戶地址空間內存讀取必須通過bpf_probe_read_user()。

在原地示例：

[搜索/示例](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/工具](https://github.com/iovisor/bcc/tree/master/tools)

### 11. bpf_probe_read_user_str()

語法：```int bpf_probe_read_user_str(void *dst, int size, const void*src)```

返回值：

- \> 0 成功時返回字符串長度（包括結尾的NULL）
- \< 0 錯誤

該函數將一個以`NULL`結尾的字符串從用戶地址空間複製到BPF棧中，以便BPF之後可以操作它。如果字符串長度小於size，則目標不會用額外的`NULL`字節填充。如果字符串長度大於size，則只會複製`size - 1`字節，並將最後一字節設置為`NULL`。

在原地示例：

[搜索/示例](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/工具](https://github.com/iovisor/bcc/tree/master/tools)

### 12. bpf_get_ns_current_pid_tgid()

語法：```u32 bpf_get_ns_current_pid_tgid(u64 dev, u64 ino, struct bpf_pidns_info*nsdata, u32 size)```。從當前**命名空間**中看到的*pid*和*tgid*的值將在*nsdata*中返回。

成功返回0，失敗時返回以下之一：

- 如果提供的dev和inum與當前任務的nsfs的dev_t和inode號不匹配，或者dev轉換為dev_t丟失了高位，則返回**-EINVAL**。

- 如果當前任務的pidns不存在，則返回**-ENOENT**。

原地示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

## 調試

### 1. bpf_override_return()

語法：```int bpf_override_return(struct pt_regs *, unsigned long rc)```

返回值：成功時返回0

當用於附加到函數入口的程序時，會導致該函數的執行被跳過，立即返回`rc`。這用於目標錯誤注入。

僅當允許錯誤注入時，bpf_override_return才有效。白名單列表中需要在內核源代碼中給一個函數打上 `ALLOW_ERROR_INJECTION()` 的標籤；參考 `io_ctl_init` 的示例。如果該函數未被加入白名單，bpf程序將無法附加，出現 `ioctl(PERF_EVENT_IOC_SET_BPF): Invalid argument` 錯誤。

```C
int kprobe__io_ctl_init(void *ctx) {
 bpf_override_return(ctx, -ENOMEM);
 return 0;
}
```

## 輸出

### 1. bpf_trace_printk()

語法：```int bpf_trace_printk(const char *fmt, ...)```

返回值：成功時返回0

對於通常的trace_pipe (/sys/kernel/debug/tracing/trace_pipe)提供了一個簡單的內核printf()功能。這對於一些快速示例是可以接受的，但有一些限制：最多3個參數，只有一個%s，而且trace_pipe是全局共享的，所以併發程序會有衝突輸出。更好的接口是通過BPF_PERF_OUTPUT()。注意，與原始內核版本相比，調用這個輔助函數變得更簡單，它的第二個參數已經是 ```fmt_size```。

原地示例："[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples), [搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 2. BPF_PERF_OUTPUT

語法：```BPF_PERF_OUTPUT(name)```

創建一個BPF表格，通過性能環形緩衝區將自定義事件數據推送到用戶空間。這是將每個事件數據推送到用戶空間的首選方法。

例如：

```C
struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
};
BPF_PERF_OUTPUT(events);

int hello(struct pt_regs *ctx) {
    struct data_t data = {};

    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
```

輸出表格名為```events```，數據通過```events.perf_submit()```推送到該表格。

示例中包含以下內容：
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples), [搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 3. perf_submit()

語法：```int perf_submit((void *)ctx, (void*)data, u32 data_size)```

返回值：成功返回0

這是BPF_PERF_OUTPUT表格的一種方法，用於向用戶空間提交自定義事件數據。參見BPF_PERF_OUTPUT條目（最終調用bpf_perf_event_output()）。

```ctx```參數在[kprobes](#1-kprobes)或[kretprobes](#2-kretprobes)中提供。對於```SCHED_CLS```或```SOCKET_FILTER```程序，必須使用```struct __sk_buff *skb```。

示例中包含以下內容：
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples), [搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 4. perf_submit_skb()

語法：```int perf_submit_skb((void *)ctx, u32 packet_size, (void*)data, u32 data_size)```

返回值：成功返回0".一種在網絡程序類型中可用的BPF_PERF_OUTPUT表的方法，用於將自定義事件數據和數據包緩衝區的前```packet_size```字節一起提交到用戶空間。請參閱BPF_PERF_OUTPUT條目。（最終調用bpf_perf_event_output()函數。）

現場示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples)
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 5. BPF_RINGBUF_OUTPUT

語法：```BPF_RINGBUF_OUTPUT(name, page_cnt)```

創建一個BPF表，通過一個環形緩衝區將自定義事件數據推送到用戶空間。
```BPF_RINGBUF_OUTPUT```相較於```BPF_PERF_OUTPUT```具有以下幾個優點：

- 緩衝區在所有CPU之間共享，即每個CPU不需要單獨分配
- 支持兩種BPF程序的API
  - ```map.ringbuf_output()```類似於```map.perf_submit()```（在[ringbuf_output](#6-ringbuf_output)中介紹）
  - ```map.ringbuf_reserve()```/```map.ringbuf_submit()```/```map.ringbuf_discard()```將保留緩衝區空間和提交事件的過程分為兩步（在[ringbuf_reserve](#7-ringbuf_reserve)、[ringbuf_submit](#8-ringbuf_submit)和[ringbuf_discard](#9-ringbuf_discard)中介紹）
- BPF API不需要訪問CPU ctx參數
- 通過共享的環形緩衝區管理器，在用戶空間中具有更高的性能和更低的延遲
- 支持兩種在用戶空間中消費數據的方式

從Linux 5.8開始，這應該是將事件數據推送到用戶空間的首選方法。

輸出表命名為'事件'。數據通過'事件'。ringbuf_reserve（）分配，並通過'事件'。ringbuf_submit（）推送到其中。

在situ示例：<!-- TODO -->
[搜索/示例](https://github.com/iovisor/bcc/tree/master/examples)，

### 6. ringbuf_output（）

語法：int ringbuf_output（（void *）data，u64 data_size，u64 flags）

返回：成功返回0

標誌：

- ```BPF_RB_NO_WAKEUP```：不發送新數據可用的通知
- ```BPF_RB_FORCE_WAKEUP```：無條件發送新數據可用的通知

BPF_RINGBUF_OUTPUT表的方法，用於將自定義事件數據提交給用戶空間。此方法類似於```perf_submit（）```，但不需要ctx參數。

在situ示例：<!-- TODO -->
[搜索/示例](https://github.com/iovisor/bcc/tree/master/examples)，

### 7. ringbuf_reserve()

語法：void * ringbuf_reserve（u64 data_size）

返回：成功時返回數據結構的指針，失敗時返回NULL

BPF_RINGBUF_OUTPUT表的方法，用於在環形緩衝區中保留空間並同時分配一個用於輸出的數據結構。必須與```ringbuf_submit```或```ringbuf_discard```之一配合使用。

在situ示例：<!-- TODO -->
[搜索/示例]（<https://github.com/iovisor/bcc/tree/master/examples)```之前調用，以為數據預留空間。

現場示例：<!-- TODO -->
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),

### 9. ringbuf_discard()

語法: ```void ringbuf_discard((void *)data, u64 flags)```

返回值: 無，始終成功

標誌:

- ```BPF_RB_NO_WAKEUP```: 不發送新數據可用的通知
- ```BPF_RB_FORCE_WAKEUP```: 無條件發送新數據可用的通知

BPF_RINGBUF_OUTPUT表的方法，用於丟棄自定義事件數據；用戶空間將忽略與丟棄事件相關聯的數據。必須在調用```ringbuf_reserve()```之前調用，以為數據預留空間。

現場示例：<!-- TODO -->
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),

## Maps

Maps是BPF數據存儲，是更高級對象類型（包括表、哈希和直方圖）的基礎。

### 1. BPF_TABLE

語法: ```BPF_TABLE(_table_type,_key_type, _leaf_type,_name, _max_entries)```

創建名為```_name```的映射。大多數情況下，這將通過更高級的宏（如BPF_HASH、BPF_ARRAY、BPF_HISTOGRAM等）使用。

`BPF_F_TABLE`是一個變體，最後一個參數採用標誌。`BPF_TABLE(https://github.com/iovisor/bcc/tree/master.)`實際上是`BPF_F_TABLE(<https://github.com/iovisor/bcc/tree/master>., 0 /*flag*/)```的包裝。

方法（稍後討論）：map.lookup()、map.lookup_or_try_init()、map.delete()、map.update()、map.insert()、map.increment()。

現場示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),"[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

#### 固定映射

語法: ```BPF_TABLE_PINNED(_table_type,_key_type, _leaf_type,_name, _max_entries, "/sys/fs/bpf/xyz")```

如果映射不存在，則創建一個新的映射並將其固定到bpffs作為文件；否則使用已固定到bpffs的映射。類型信息不強制執行，實際的映射類型取決於固定到位置的映射。

例如:

```C
BPF_TABLE_PINNED("hash", u64, u64, ids, 1024, "/sys/fs/bpf/ids");
```

### 2. BPF_HASH

語法: ```BPF_HASH(name [, key_type [, leaf_type [, size]]])```

創建一個哈希映射（關聯數組），名稱為```name```，具有可選參數。

默認值: ```BPF_HASH(name, key_type=u64, leaf_type=u64, size=10240)```

例如:

```C
BPF_HASH(start, struct request *);
```

這將創建一個名為```start```的哈希，其中關鍵字為```struct request *```，值默認為u64。此哈希由disksnoop.py示例用於保存每個I/O請求的時間戳，其中關鍵字是指向struct request的指針，而值是時間戳。

這是`BPF_TABLE("hash", ...)`的包裝宏。

方法（稍後涵蓋）：map.lookup()，map.lookup_or_try_init()，map.delete()，map.update()，map.insert()，map.increment()。

示例中的原位置鏈接：[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 3. BPF_ARRAY

語法: ```BPF_ARRAY(name [, leaf_type [, size]])```

創建一個以整數索引的數組，最快速的查找和更新為優化，名稱為```name```，具有可選參數。

默認值: ```BPF_ARRAY(name, leaf_type=u64, size=10240)```

例如:

```C
BPF_ARRAY(counts, u64, 32);
```

這將創建一個名為```counts```的數組，其中有32個存儲桶和64位整數值。funccount.py示例使用此數組保存每個函數的調用計數。".這是一個 `BPF_TABLE("array", ...)` 的包裝宏。

方法（稍後介紹）：map.lookup()、map.update()、map.increment()。注意，所有數組元素都預先分配為零值，無法刪除。

在當前位置的示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 4. BPF_HISTOGRAM

語法：```BPF_HISTOGRAM(name [, key_type [, size ]])```

創建一個名為 ```name``` 的直方圖映射，包含可選參數。

默認值：```BPF_HISTOGRAM(name, key_type=int, size=64)```

例如：

```C
BPF_HISTOGRAM(dist);
```

這創建了一個名為 ```dist``` 的直方圖，默認有 64 個桶，以 int 類型的鍵索引。

這是一個 `BPF_TABLE("histgram", ...)` 的包裝宏。

方法（稍後介紹）：map.increment()。

在當前位置的示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 5. BPF_STACK_TRACE

語法：```BPF_STACK_TRACE(name, max_entries)```

創建一個名為 ```name``` 的堆棧跟蹤映射，提供最大條目數。這些映射用於存儲堆棧跟蹤。

例如：

```C
BPF_STACK_TRACE(stack_traces, 1024);
```

這創建了一個名為 ```stack_traces``` 的堆棧跟蹤映射，最大堆棧跟蹤條目數為 1024。

這是一個 `BPF_TABLE("stacktrace", ...)` 的包裝宏。

方法（稍後介紹）：map.get_stackid()。

在當前位置的示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 6. BPF_PERF_ARRAY

語法：```BPF_PERF_ARRAY(name, max_entries)```

創建一個名為 ```name``` 的 perf 數組，提供最大條目數，該數必須等於系統 CPU 的數量。這些映射用於獲取硬件性能計數器。例如：

```C
text="""
BPF_PERF_ARRAY(cpu_cycles, NUM_CPUS);
"""
b = bcc.BPF(text=text, cflags=["-DNUM_CPUS=%d" % multiprocessing.cpu_count()])
b["cpu_cycles"].open_perf_event(b["cpu_cycles"].HW_CPU_CYCLES)
```

這將創建一個名為```cpu_cycles```的性能數組，條目數量等於CPU核心數。該數組被配置為，稍後調用```map.perf_read()```將返回從過去某一時刻開始計算的硬件計數器的週期數。每個表只能配置一種類型的硬件計數器。

方法（稍後介紹）：```map.perf_read()```。

現場示例：
[搜索 /tests](https://github.com/iovisor/bcc/tree/master/tests)

### 7. BPF_PERCPU_HASH

語法：```BPF_PERCPU_HASH(name [, key_type [, leaf_type [, size]]])```

創建NUM_CPU個以int索引的哈希映射（關聯數組），名為```name```，具有可選參數。每個CPU都會有一個單獨的該數組副本。這些副本不以任何方式進行同步。

請注意，由於內核中定義的限制（位於linux/mm/percpu.c中），```leaf_type```的大小不能超過32KB。
換句話說，```BPF_PERCPU_HASH```元素的大小不能超過32KB。

默認值：```BPF_PERCPU_HASH(name, key_type=u64, leaf_type=u64, size=10240)```

例如：

```C
BPF_PERCPU_HASH(start, struct request *);
```

這將創建名為```start```的NUM_CPU個哈希，其中鍵為```struct request *```，值默認為u64。

這是對```BPF_TABLE("percpu_hash", ...)```的包裝宏。

方法（稍後介紹）：```map.lookup()```、```map.lookup_or_try_init()```、```map.delete()```、```map.update()```、```map.insert()```、```map.increment()```。

現場示例：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 8. BPF_PERCPU_ARRAY

語法：```BPF_PERCPU_ARRAY(name [, leaf_type [, size]])```。創建```name```的NUM_CPU個按整數索引優化的數組，以實現最快的查找和更新，具有可選參數。每個CPU都會有一個單獨的副本。這些副本不能以任何方式同步。

請注意，由於內核（在linux/mm/percpu.c中）定義的限制，```leaf_type```的大小不能超過32KB。
換句話說，```BPF_PERCPU_ARRAY```元素的大小不能超過32KB。

默認值：```BPF_PERCPU_ARRAY(name, leaf_type=u64, size=10240)```

例如：

```C
BPF_PERCPU_ARRAY(counts, u64, 32);
```

這將創建NUM_CPU個名為```counts```的數組，其中每個數組有32個桶和64位整數值。

這是```BPF_TABLE("percpu_array", ...)```的包裝宏。

方法（稍後介紹）：map.lookup()，map.update()，map.increment()。請注意，所有數組元素都預先分配為零值，並且不能被刪除。

In situ示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 9. BPF_LPM_TRIE

語法：```BPF_LPM_TRIE(name [, key_type [, leaf_type [, size]]])```

創建一個名為```name```的最長前綴匹配字典樹映射，帶有可選參數。

默認值：```BPF_LPM_TRIE(name, key_type=u64, leaf_type=u64, size=10240)```

例如：

```c
BPF_LPM_TRIE(trie, struct key_v6);
```

這將創建一個名為```trie```的LPM字典樹映射，其中鍵是```struct key_v6```，值默認為u64。

這是一個對```BPF_F_TABLE("lpm_trie", ..., BPF_F_NO_PREALLOC)```的包裝宏。

方法（稍後介紹）：map.lookup()，map.lookup_or_try_init()，map.delete()，map.update()，map.insert()，map.increment()。

In situ示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples)，
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 10. BPF_PROG_ARRAY

語法：```BPF_PROG_ARRAY(name, size)```。創建一個名為 ```name``` 的程序數組，其中包含 ```size``` 個條目。數組的每個條目要麼是指向一個 bpf 程序的文件描述符，要麼是 ```NULL```。該數組作為一個跳轉表，以便 bpf 程序可以“尾調用”其他 bpf 程序。

這是一個 ```BPF_TABLE("prog", ...)``` 的包裝宏。

方法（稍後介紹）：map.call()。

實時示例：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tests](https://github.com/iovisor/bcc/tree/master/tests),
[分配 fd](https://github.com/iovisor/bcc/blob/master/examples/networking/tunnel_monitor/monitor.py#L24-L26)

### 11. BPF_DEVMAP

語法：```BPF_DEVMAP(name, size)```

這創建了一個名為 ```name``` 的設備映射，其中包含 ```size``` 個條目。映射的每個條目都是一個網絡接口的 `ifindex`。此映射僅在 XDP 中使用。

例如：

```C
BPF_DEVMAP(devmap, 10);
```

方法（稍後介紹）：map.redirect_map()。

實時示例：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),

### 12. BPF_CPUMAP

語法：```BPF_CPUMAP(name, size)```

這創建了一個名為 ```name``` 的 CPU 映射，其中包含 ```size``` 個條目。映射的索引表示 CPU 的 ID，每個條目是為 CPU 分配的環形緩衝區的大小。此映射僅在 XDP 中使用。

例如：

```C
BPF_CPUMAP(cpumap, 16);
```

方法（稍後介紹）：map.redirect_map()。

實時示例：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),

### 13. BPF_XSKMAP

語法：```BPF_XSKMAP(name, size [, "/sys/fs/bpf/xyz"])```。這將創建一個名為```name```的xsk映射，帶有```size```個條目，並將其固定到bpffs作為一個文件。每個條目表示一個NIC的隊列ID。該映射僅在XDP中用於將數據包重定向到AF_XDP套接字。如果AF_XDP套接字綁定到與當前數據包的隊列ID不同的隊列，則數據包將被丟棄。對於內核v5.3及更高版本，“lookup”方法可用於檢查當前數據包的隊列ID是否可用於AF_XDP套接字。有關詳細信息，請參閱[AF_XDP](https://www.kernel.org/doc/html/latest/networking/af_xdp.html)。

例如：

```C
BPF_XSKMAP(xsks_map, 8);
```

方法（稍後涵蓋）：map.redirect_map()。map.lookup()

現場示例：
[search /examples](https://github.com/iovisor/bcc/tree/master/examples),

### 14. BPF_ARRAY_OF_MAPS

語法：```BPF_ARRAY_OF_MAPS(name, inner_map_name, size)```

這將創建一個帶有映射內部類型（BPF_MAP_TYPE_HASH_OF_MAPS）的數組映射，名稱為```name```，包含```size```個條目。映射的內部元數據由映射```inner_map_name```提供，可以是除了```BPF_MAP_TYPE_PROG_ARRAY```、```BPF_MAP_TYPE_CGROUP_STORAGE```和```BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE```之外的大多數數組或哈希映射。

例如：

```C
BPF_TABLE("hash", int, int, ex1, 1024);
BPF_TABLE("hash", int, int, ex2, 1024);
BPF_ARRAY_OF_MAPS(maps_array, "ex1", 10);
```

### 15. BPF_HASH_OF_MAPS

語法：```BPF_HASH_OF_MAPS(name, key_type, inner_map_name, size)```

這將創建一個帶有映射內部類型（BPF_MAP_TYPE_HASH_OF_MAPS）的哈希映射，名稱為```name```，包含```size```個條目。映射的內部元數據由映射```inner_map_name```提供，可以是除了```BPF_MAP_TYPE_PROG_ARRAY```、```BPF_MAP_TYPE_CGROUP_STORAGE```和```BPF_MAP_TYPE_PERCPU_CGROUP_STORAGE```之外的大多數數組或哈希映射。

例如：

```C
BPF_ARRAY(ex1, int, 1024);
BPF_ARRAY(ex2, int, 1024);
BPF_HASH_OF_MAPS(maps_hash, struct custom_key, "ex1", 10);
```

### 16. BPF_STACK

語法：```BPF_STACK(name, leaf_type, max_entries[, flags])```。創建一個名為 `name` 的堆棧，其值類型為 `leaf_type`，最大條目數為 `max_entries`。
堆棧和隊列映射僅適用於 Linux 4.20+。

例如:

```C
BPF_STACK(stack, struct event, 10240);
```

這將創建一個名為 `stack` 的堆棧，其值類型為 `struct event`，最多可容納 10240 個條目。

方法（後面會涉及）：map.push()、map.pop()、map.peek()。

示例：

在 [search /tests](https://github.com/iovisor/bcc/tree/master/tests) 中。

### 17. BPF_QUEUE

語法：```BPF_QUEUE(name, leaf_type, max_entries[, flags])```

創建一個名為 `name` 的隊列，其值類型為 `leaf_type`，最大條目數為 `max_entries`。
堆棧和隊列映射僅適用於 Linux 4.20+。

例如：

```C
BPF_QUEUE(queue, struct event, 10240);
```

這將創建一個名為 `queue` 的隊列，其值類型為 `struct event`，最多可容納 10240 個條目。

方法（後面會涉及）：map.push()、map.pop()、map.peek()。

示例：

在 [search /tests](https://github.com/iovisor/bcc/tree/master/tests) 中。

### 18. BPF_SOCKHASH

語法：```BPF_SOCKHASH(name[, key_type [, max_entries)```

創建一個名為 `name` 的哈希，帶有可選參數。sockhash僅適用於Linux 4.18+。

默認值：```BPF_SOCKHASH(name, key_type=u32, max_entries=10240)```

例如：

```C
struct sock_key {
  u32 remote_ip4;
  u32 local_ip4;
  u32 remote_port;
  u32 local_port;
};
BPF_HASH(skh, struct sock_key, 65535);
```

這將創建一個名為 `skh` 的哈希表，其中鍵是 `struct sock_key`。

sockhash是一種BPF映射類型，它保存對sock結構體的引用。然後，通過使用新的sk/msg重定向BPF輔助函數，BPF程序可以使用該映射在套接字之間重定向skbs/msgs（`map.sk_redirect_hash()/map.msg_redirect_hash()`）。```BPF_SOCKHASH```和```BPF_SOCKMAP```的區別在於```BPF_SOCKMAP```是基於數組實現的，並且強制鍵為四個字節。
而```BPF_SOCKHASH```是基於哈希表實現的，並且鍵的類型可以自由指定。

方法（稍後介紹）：map.sock_hash_update()，map.msg_redirect_hash()，map.sk_redirect_hash()。

[搜索/tests](https://github.com/iovisor/bcc/tree/master/tests)

### 19. map.lookup()

語法：```*val map.lookup(&key)```

在映射中查找鍵，如果存在則返回指向其值的指針，否則返回NULL。我們將鍵作為指針的地址傳入。

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 20. map.lookup_or_try_init()

語法：```*val map.lookup_or_try_init(&key, &zero)```

在映射中查找鍵，如果存在則返回指向其值的指針，否則將鍵的值初始化為第二個參數。通常用於將值初始化為零。如果無法插入鍵（例如映射已滿），則返回NULL。

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

注意：舊的map.lookup_or_init()可能導致函數返回，因此建議使用lookup_or_try_init()，它沒有這種副作用。

### 21. map.delete()

語法：```map.delete(&key)```

從哈希表中刪除鍵。

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 22. map.update()

語法：```map.update(&key, &val)```

將第二個參數中的值與鍵關聯，覆蓋任何先前的值。

示例："[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 23. map.insert()

語法: ```map.insert(&key, &val)```

將第二個參數中的值與鍵相關聯，僅在之前沒有值的情況下。

現場示例:
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 24. map.increment()

語法: ```map.increment(key[, increment_amount])```

通過 `increment_amount`（默認為1）增加鍵的值。用於柱狀圖。

```map.increment()```不是原子操作。在併發情況下，如果要獲得更準確的結果，請使用 ```map.atomic_increment()``` 而不是 ```map.increment()```。```map.increment()``` 和 ```map.atomic_increment()``` 的開銷相似。

注意. 當使用 ```map.atomic_increment()``` 操作類型為 ```BPF_MAP_TYPE_HASH``` 的 BPF map 時，如果指定的鍵不存在，則 ```map.atomic_increment()``` 無法保證操作的原子性。

現場示例:
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 25. map.get_stackid()

語法: ```int map.get_stackid(void *ctx, u64 flags)```

這會遍歷在 ```ctx``` 中找到的 struct pt_regs 中的堆棧，將其保存在堆棧跟蹤 map 中，並返回一個唯一的堆棧跟蹤 ID。

現場示例:
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 26. map.perf_read()

語法: ```u64 map.perf_read(u32 cpu)```

現場示例:""[搜索/tests](https://github.com/iovisor/bcc/tree/master/tests)

### 27. map.call()

語法：```void map.call(void *ctx, int index)```

這將調用```bpf_tail_call()```來尾調用[BPF_PROG_ARRAY](#10-bpf_prog_array)中指向```index```入口的bpf程序。尾調用與普通調用不同。它在跳轉到另一個bpf程序後重用當前的棧幀，並且不會返回。如果```index```入口為空，它將不會跳轉到任何地方，程序的執行將會繼續進行。

例如：

```C
BPF_PROG_ARRAY(prog_array, 10);

int tail_call(void *ctx) {
    bpf_trace_printk("尾調用\n");
    return 0;
}

int do_tail_call(void *ctx) {
    bpf_trace_printk("原始的程序\n");
    prog_array.call(ctx, 2);
    return 0;
}
```

```Python
b = BPF(src_file="example.c")
tail_fn = b.load_func("tail_call", BPF.KPROBE)
prog_array = b.get_table("prog_array")
prog_array[c_int(2)] = c_int(tail_fn.fd)
b.attach_kprobe(event="some_kprobe_event", fn_name="do_tail_call")
```

這將```tail_call()```分配給```prog_array[2]```。在```do_tail_call()```的最後，```prog_array.call(ctx, 2)```尾調用```tail_call()```並執行它。

**注意：**為了防止無限循環，尾調用的最大數量是32（[```MAX_TAIL_CALL_CNT```](https://github.com/torvalds/linux/search?l=C&q=MAX_TAIL_CALL_CNT+path%3Ainclude%2Flinux&type=Code)）。

在現場示例中：
[搜索/examples](https://github.com/iovisor/bcc/search?l=C&q=call+path%3Aexamples&type=Code),
[搜索/tests](https://github.com/iovisor/bcc/search?l=C&q=call+path%3Atests&type=Code)

### 28. map.redirect_map()

語法：```int map.redirect_map(int index, int flags)```".這將根據 ```index``` 條目重定向傳入的數據包。如果映射是 [BPF_DEVMAP](#11-bpf_devmap)，數據包將被髮送到該條目指向的網絡接口的傳輸隊列。如果映射是 [BPF_CPUMAP](#12-bpf_cpumap)，數據包將被髮送到```index``` CPU的環形緩衝區，並稍後由CPU處理。如果映射是 [BPF_XSKMAP](#13-bpf_xskmap)，數據包將被髮送到連接到隊列的 AF_XDP 套接字。

如果數據包成功被重定向，該函數將返回 XDP_REDIRECT。否則，將返回 XDP_ABORTED 以丟棄該數據包。

例如：

```C
BPF_DEVMAP(devmap, 1);

int redirect_example(struct xdp_md *ctx) {
    return devmap.redirect_map(0, 0);
}
int xdp_dummy(struct xdp_md *ctx) {
    return XDP_PASS;
}
```

```Python
ip = pyroute2.IPRoute()
idx = ip.link_lookup(ifname="eth1")[0]

b = bcc.BPF(src_file="example.c")

devmap = b.get_table("devmap")
devmap[c_uint32(0)] = c_int(idx)

in_fn = b.load_func("redirect_example", BPF.XDP)
out_fn = b.load_func("xdp_dummy", BPF.XDP)
b.attach_xdp("eth0", in_fn, 0)
b.attach_xdp("eth1", out_fn, 0)
```

示例位置：
[搜索 /examples](https://github.com/iovisor/bcc/search?l=C&q=redirect_map+path%3Aexamples&type=Code),

### 29. map.push()

語法：```int map.push(&val, int flags)```

將元素推入堆棧或隊列表。將 BPF_EXIST 作為標誌傳遞會導致隊列或堆棧在已滿時丟棄最舊的元素。成功返回0，失敗返回負錯誤值。

示例位置：
[搜索 /tests](https://github.com/iovisor/bcc/tree/master/tests),

### 30. map.pop()

語法：```int map.pop(&val)```

從堆棧或隊列表中彈出一個元素。```*val```被填充為結果。與查看不同，彈出操作會移除該元素。成功返回0，失敗返回負錯誤值。

示例位置：
[搜索 /tests](https://github.com/iovisor/bcc/tree/master/tests),

### 31. map.peek()

語法：```int map.peek(&val)```查看堆棧或隊列表頭的元素。```*val```將被結果填充。
與彈出不同，查看不會刪除元素。
成功返回0，失敗返回負錯誤。

實例：
[搜索/tests](https://github.com/iovisor/bcc/tree/master/tests)

### 32. map.sock_hash_update()

語法：```int map.sock_hash_update(struct bpf_sock_ops *skops, &key, int flags)```

向sockhash映射添加條目或更新條目。skops用作與鍵相關聯的條目的新值。flags為以下之一：

```sh
BPF_NOEXIST：映射中不得存在key的條目。
BPF_EXIST：映射中必須已存在key的條目。
BPF_ANY：對於key的條目是否存在，沒有條件。
```

如果映射具有eBPF程序（解析器和判決器），則這些程序將被添加的套接字繼承。如果套接字已經附加到eBPF程序，則會出錯。

成功返回0，失敗返回負錯誤。

實例：
[搜索/tests](https://github.com/iovisor/bcc/tree/master/tests)

### 33. map.msg_redirect_hash()

語法：```int map.msg_redirect_hash(struct sk_msg_buff *msg, void*key, u64 flags)```

該輔助程序用於在套接字級別實施策略的程序中。如果消息msg被允許通過（即判決eBPF程序返回SK_PASS），則使用哈希鍵將其重定向到映射引用的套接字（類型為BPF_MAP_TYPE_SOCKHASH）。可以使用入站和出站接口進行重定向。標誌中的BPF_F_INGRESS值用於區分（如果存在該標誌，則選擇入站路徑，否則選擇出站路徑）。目前，這是唯一支持的標誌。

成功返回SK_PASS，發生錯誤返回SK_DROP。

實例：
[搜索/tests](https://github.com/iovisor/bcc/tree/master/tests)

### 34. map.sk_redirect_hash()

語法：```int map.sk_redirect_hash(struct sk_buff *skb, void*key, u64 flags)```".This helper is used in programs implementing policies at the skb socket level.
If the sk_buff skb is allowed to pass (i.e. if the verdict eBPF program returns SK_PASS), redirect it to the socket referenced by map (of type BPF_MAP_TYPE_SOCKHASH) using hash key.
Both ingress and egress interfaces can be used for redirection.
The BPF_F_INGRESS value in flags is used to make the distinction (ingress path is selected if the flag is present, egress otherwise).
This is the only flag supported for now.

Return SK_PASS on success, or SK_DROP on error.

Examples in situ:
\[搜索/tests\]\(<https://github.com/iovisor/bcc/tree/master/tests),

## 許可證

Depending on which \[BPF helpers\]\(kernel-versions.md#helpers\) are used, a GPL-compatible license is required.

The special BCC macro `BPF_LICENSE` specifies the license of the BPF program.
You can set the license as a comment in your source code, but the kernel has a special interface to specify it programmatically.
If you need to use GPL-only helpers, it is recommended to specify the macro in your C code so that the kernel can understand it:

```C
// SPDX-License-Identifier: GPL-2.0+
#define BPF_LICENSE GPL
```

Otherwise, the kernel may reject loading your program (see the \[錯誤描述\](#2-cannot-call-gpl-only-function-from-proprietary-program) below).
Note that it supports multiple words and quotes are not necessary:

```C
// SPDX-License-Identifier: GPL-2.0+ OR BSD-2-Clause
#define BPF_LICENSE Dual BSD/GPL
```

Check the \[BPF helpers reference\]\(kernel-versions.md#helpers\) to see which helpers are GPL-only and what the kernel understands as GPL-compatible.

**If the macro is not specified, BCC will automatically define the license of the program as GPL.**

## Rewriter

一個重寫器的工作是使用內核輔助程序將隱式內存訪問轉換為顯式內存訪問。最近的內核引入了一個配置選項ARCH_HAS_NON_OVERLAPPING_ADDRESS_SPACE，該選項將被設置為使用用戶地址空間和內核地址空間不重疊的體系結構。x86和arm設置了這個配置選項，而s390沒有。如果沒有設置ARCH_HAS_NON_OVERLAPPING_ADDRESS_SPACE，bpf舊幫助函數`bpf_probe_read()`將不可用。一些現有的用戶可能有隱式內存訪問來訪問用戶內存，所以使用`bpf_probe_read_kernel()`會導致他們的應用程序失敗。因此，對於非s390，重寫器將對這些隱式內存訪問使用`bpf_probe_read()`。對於s390，默認使用`bpf_probe_read_kernel()`，用戶在訪問用戶內存時應顯式使用`bpf_probe_read_user()`

# bcc Python

## 初始化

構造函數。

### 1. BPF

語法: ```BPF({text=BPF_program | src_file=filename} [, usdt_contexts=[USDT_object, ...]] [, cflags=[arg1, ...]] [, debug=int])```

創建一個BPF對象。這是定義BPF程序並與其輸出交互的主要對象。

必須提供`text`或`src_file`之一，不能兩者都提供。

`cflags`指定要傳遞給編譯器的額外參數，例如`-DMACRO_NAME=value`或`-I/include/path`。參數以數組形式傳遞，每個元素為一個額外的參數。注意，字符串不會按空格拆分，所以每個參數必須是數組的不同元素，例如`["-include", "header.h"]`。

`debug`標誌控制調試輸出，可以使用或運算:

- `DEBUG_LLVM_IR = 0x1` 編譯後的LLVM IR
- `DEBUG_BPF = 0x2` 加載的BPF字節碼和分支時的寄存器狀態
- `DEBUG_PREPROCESSOR = 0x4` 預處理器的結果
- `DEBUG_SOURCE = 0x8` 嵌入源碼的ASM指令
- `DEBUG_BPF_REGISTER_STATE = 0x10` 所有指令的寄存器狀態，額外打印DEBUG_BPF的信息
- `DEBUG_BTF = 0x20` 打印來自`libbpf`庫的消息。

示例:

```Python"# 定義整個BPF程序在一行中:
BPF(text='int do_trace(void *ctx) { bpf_trace_printk("命中！\\n"); return 0; }');

# 定義程序為一個變量:
prog = """
int hello(void *ctx) {
    bpf_trace_printk("你好，世界！\\n");
    return 0;
}
"""
b = BPF(text=prog)

# 源文件:
b = BPF(src_file = "vfsreadlat.c")

# 包括一個USDT對象:
u = USDT(pid=int(pid))
[...]
b = BPF(text=bpf_text, usdt_contexts=[u])

# 添加包含路徑:
u = BPF(text=prog, cflags=["-I/path/to/include"])


在原地的示例:
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 2. USDT

語法: ```USDT({pid=pid | path=path})```

創建一個對象以檢測用戶靜態定義的跟蹤(USDT)探針。它的主要方法是```enable_probe()```。

參數:

- pid: 附加到該進程ID。
- path: 從此二進制路徑檢測USDT探針。

示例:

```Python
# 包括一個USDT對象:
u = USDT(pid=int(pid))
[...]
b = BPF(text=bpf_text, usdt_contexts=[u])
```

在原地的示例:
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

## 事件

### 1. attach_kprobe()

語法: ```BPF.attach_kprobe(event="event", fn_name="name")```

通過內核動態跟蹤函數入口，來檢測內核函數```event()```，並將我們的C定義的函數```name()```附加到每次調用內核函數時被調用。

例如:

```Python
b.attach_kprobe(event="sys_clone", fn_name="do_trace")
```

這將檢測內核```sys_clone()```函數，並在每次調用時運行我們定義的BPF函數```do_trace()```。

您可以多次調用attach_kprobe()，並將您的BPF函數附加到多個內核函數上。您也可以多次調用attach_kprobe()函數將多個BPF函數附加到同一個內核函數。

有關如何從BPF中提取參數的詳細信息，請參閱前面的kprobes部分。

示例：
[查找/examples](https://github.com/iovisor/bcc/tree/master/examples),
[查找/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 2. attach_kretprobe()

語法：BPF.attach_kretprobe(event="事件", fn_name="名稱" [, maxactive=int])

使用內核動態跟蹤函數返回來檢測內核函數event()的返回，並附加我們定義的C函數name()在內核函數返回時調用。

例如：

```Python
b.attach_kretprobe(event="vfs_read", fn_name="do_return")
```

這將檢測內核的vfs_read()函數，每次調用該函數時都會執行我們定義的BPF函數do_return()。

您可以多次調用attach_kretprobe()函數，並將您的BPF函數附加到多個內核函數的返回值。
您也可以多次調用attach_kretprobe()函數將多個BPF函數附加到同一個內核函數的返回值。

當在內核函數上安裝kretprobe時，它可以捕獲的並行調用次數存在限制。您可以使用maxactive參數更改該限制。有關默認值，請參閱kprobes文檔。

有關如何從BPF中提取返回值的詳細信息，請參閱前面的kretprobes部分。

示例：
[查找/examples](https://github.com/iovisor/bcc/tree/master/examples),
[查找/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 3. attach_tracepoint()

語法：BPF.attach_tracepoint(tp="追蹤點", fn_name="名稱")

檢測由tracepoint描述的內核追蹤點，並在命中時運行BPF函數name()。這是一種顯式方式來操控 tracepoints。在前面的 tracepoints 部分講解過的 ```TRACEPOINT_PROBE``` 語法是另一種方法，其優點是自動聲明一個包含 tracepoint 參數的 ```args``` 結構體。在使用 ```attach_tracepoint()``` 時，tracepoint 參數需要在 BPF 程序中聲明。

例如：

```Python
# 定義 BPF 程序
bpf_text = """
#include <uapi/linux/ptrace.h>

struct urandom_read_args {
    // 來自 /sys/kernel/debug/tracing/events/random/urandom_read/format
    u64 __unused__;
    u32 got_bits;
    u32 pool_left;
    u32 input_left;
};

int printarg(struct urandom_read_args *args) {
    bpf_trace_printk("%d\\n", args->got_bits);
    return 0;
};
"""

# 加載 BPF 程序
b = BPF(text=bpf_text)
b.attach_tracepoint("random:urandom_read", "printarg")
```

注意，```printarg()``` 的第一個參數現在是我們定義的結構體。

代碼示例：
[code](https://github.com/iovisor/bcc/blob/a4159da8c4ea8a05a3c6e402451f530d6e5a8b41/examples/tracing/urandomread-explicit.py#L41),
[search /examples](https://github.com/iovisor/bcc/tree/master/examples),
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 4. attach_uprobe()

語法：```BPF.attach_uprobe(name="location", sym="symbol", fn_name="name" [, sym_off=int])```, ```BPF.attach_uprobe(name="location", sym_re="regex", fn_name="name")```, ```BPF.attach_uprobe(name="location", addr=int, fn_name="name")```

用於操控位於 ```location``` 中的庫或二進制文件中的用戶級別函數 ```symbol()```，使用用戶級別動態跟蹤該函數的入口，並將我們定義的 C 函數 ```name()``` 附加為在用戶級別函數被調用時調用的函數。如果給定了 ```sym_off```，則該函數將附加到符號的偏移量上。真實的地址```addr```可以替代```sym```，在這種情況下，```sym```必須設置為其默認值。如果文件是非PIE可執行文件，則```addr```必須是虛擬地址，否則它必須是相對於文件加載地址的偏移量。

可以在```sym_re```中提供普通表達式來代替符號名稱。然後，uprobes將附加到與提供的正則表達式匹配的符號。

在名字參數中可以給出庫名而不帶lib前綴，或者給出完整路徑（/usr/lib/...）。只能通過完整路徑（/bin/sh）給出二進制文件。

例如:

```Python
b.attach_uprobe(name="c", sym="strlen", fn_name="count")
```

這將在libc中對```strlen()```函數進行插裝，並在調用該函數時調用我們的BPF函數```count()```。請注意，在```libc```中的```libc```中的"lib"是不必要的。

其他例子:

```Python
b.attach_uprobe(name="c", sym="getaddrinfo", fn_name="do_entry")
b.attach_uprobe(name="/usr/bin/python", sym="main", fn_name="do_main")
```

您可以多次調用attach_uprobe()，並將BPF函數附加到多個用戶級函數。

有關如何從BPF工具獲取參數的詳細信息，請參見上一節uprobes。

原址示例：
[search /examples](https://github.com/iovisor/bcc/tree/master/examples),
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 5. attach_uretprobe()

語法: ```BPF.attach_uretprobe(name="location", sym="symbol", fn_name="name")```

使用用戶級動態跟蹤從名為```location```的庫或二進制文件中的用戶級函數```symbol()```返回值的方式儀器化，並將我們定義的C函數```name()```附加到用戶級函數返回時調用。

例如:

```Python
b.attach_uretprobe(name="c", sym="strlen", fn_name="count")
```。這將使用libc庫對```strlen()```函數進行插裝，並在其返回時調用我們的BPF函數```count()```。

其他示例：

```Python
b.attach_uretprobe(name="c", sym="getaddrinfo", fn_name="do_return")
b.attach_uretprobe(name="/usr/bin/python", sym="main", fn_name="do_main")
```

您可以多次調用attach_uretprobe()，並將您的BPF函數附加到多個用戶級函數上。

有關如何對BPF返回值進行插裝的詳細信息，請參閱前面的uretprobes部分。

內部示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 6. USDT.enable_probe()

語法：```USDT.enable_probe(probe=probe, fn_name=name)```

將BPF C函數```name```附加到USDT探針```probe```。

示例：

```Python
# 根據給定的PID啟用USDT探針
u = USDT(pid=int(pid))
u.enable_probe(probe="http__server__request", fn_name="do_trace")
```

要檢查您的二進制文件是否具有USDT探針以及它們的詳細信息，可以運行```readelf -n binary```並檢查stap調試部分。

內部示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 7. attach_raw_tracepoint()

語法：```BPF.attach_raw_tracepoint(tp="tracepoint", fn_name="name")```

對由```tracepoint```（僅```event```，無```category```）描述的內核原始跟蹤點進行插裝，並在命中時運行BPF函數```name()```。

這是一種明確的插裝跟蹤點的方法。早期原始跟蹤點部分介紹的```RAW_TRACEPOINT_PROBE```語法是一種替代方法。

例如：

```Python
b.attach_raw_tracepoint("sched_switch", "do_trace")
```

內部示例："."[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 8. attach_raw_socket()

語法: ```BPF.attach_raw_socket(fn, dev)```

將一個BPF函數附加到指定的網絡接口。

```fn``` 必須是 ```BPF.function``` 類型，並且 bpf_prog 類型需要是 ```BPF_PROG_TYPE_SOCKET_FILTER```  (```fn=BPF.load_func(func_name, BPF.SOCKET_FILTER)```)

```fn.sock``` 是一個非阻塞原始套接字，已經創建並綁定到 ```dev```。

所有處理 ```dev``` 的網絡數據包都會在經過 bpf_prog 處理後，被複制到 ```fn.sock``` 的 ```recv-q``` 中。可以使用 ```recv/recvfrom/recvmsg``` 來從 ```fn.sock``` 接收數據包。需要注意的是，如果在 ```recv-q``` 滿了之後沒有及時讀取，複製的數據包將會被丟棄。

可以使用這個功能來像 ```tcpdump``` 一樣捕獲網絡數據包。

可以使用```ss --bpf --packet -p```來觀察 ```fn.sock```。

示例:

```Python
BPF.attach_raw_socket(bpf_func, ifname)
```

示例位置:
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples)

### 9. attach_xdp()

語法: ```BPF.attach_xdp(dev="device", fn=b.load_func("fn_name",BPF.XDP), flags)```

改裝由 ```dev``` 描述的網絡驅動程序，然後接收數據包，並使用標誌運行 BPF 函數 ```fn_name()```。

以下是可選的標誌列表。

```Python
# from xdp_flags uapi/linux/if_link.h
XDP_FLAGS_UPDATE_IF_NOEXIST = (1 << 0)
XDP_FLAGS_SKB_MODE = (1 << 1)
XDP_FLAGS_DRV_MODE = (1 << 2)
XDP_FLAGS_HW_MODE = (1 << 3)
XDP_FLAGS_REPLACE = (1 << 4)
```

您可以像這樣使用標誌: ```BPF.attach_xdp(dev="device", fn=b.load_func("fn_name",BPF.XDP), flags=BPF.XDP_FLAGS_UPDATE_IF_NOEXIST)```

標誌的默認值為0。這意味著如果沒有帶有 `device` 的xdp程序，fn將在該設備上運行。如果有一個正在運行的xdp程序與設備關聯，舊程序將被新的fn程序替換。".當前，bcc不支持XDP_FLAGS_REPLACE標誌。以下是其他標誌的描述。

#### 1. XDP_FLAGS_UPDATE_IF_NOEXIST

如果已經將XDP程序附加到指定的驅動程序上，再次附加XDP程序將失敗。

#### 2. XDP_FLAGS_SKB_MODE

驅動程序不支持XDP，但內核模擬支持它。
XDP程序可以工作，但沒有真正的性能優勢，因為數據包無論如何都會傳遞給內核堆棧，然後模擬XDP - 這通常適用於家用電腦，筆記本電腦和虛擬化硬件所使用的通用網絡驅動程序。

#### 3. XDP_FLAGS_DRV_MODE

驅動程序具有XDP支持，並且可以將數據包直接傳遞給XDP，無需內核堆棧交互 - 少數驅動程序可以支持此功能，通常用於企業級硬件。

#### 4. XDP_FLAGS_HW_MODE

XDP可以直接在NIC上加載和執行 - 只有少數NIC支持這一功能。

例如：

```Python
b.attach_xdp(dev="ens1", fn=b.load_func("do_xdp", BPF.XDP))
```

這將為網絡設備```ens1```安裝工具，並在接收數據包時運行我們定義的BPF函數```do_xdp()```。

不要忘記在最後調用```b.remove_xdp("ens1")```！

示例：
[搜索/examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索/tools](https://github.com/iovisor/bcc/tree/master/tools)

### 10. attach_func()

語法：```BPF.attach_func(fn, attachable_fd, attach_type [, flags])```

將指定類型的BPF函數附加到特定的```attachable_fd```上。如果```attach_type```是```BPF_FLOW_DISSECTOR```，則預期該函數將附加到當前的網絡命名空間，並且```attachable_fd```必須為0。

例如：

```Python
b.attach_func(fn, cgroup_fd, BPFAttachType.CGROUP_SOCK_OPS)
b.attach_func(fn, map_fd, BPFAttachType.SK_MSG_VERDICT)
```注意。當附加到“全局”鉤子（xdp、tc、lwt、cgroup）時。如果程序終止後不再需要“BPF 函數”，請確保在程序退出時調用 `detach_func`。

示例中的內部代碼：

[search /examples](https://github.com/iovisor/bcc/tree/master/examples),

### 11. detach_func()

語法：```BPF.detach_func(fn, attachable_fd, attach_type)```

斷開指定類型的 BPF 函數。

例如：

```Python
b.detach_func(fn, cgroup_fd, BPFAttachType.CGROUP_SOCK_OPS)  // 斷開 cgroup_fd 上的 fn 函數
b.detach_func(fn, map_fd, BPFAttachType.SK_MSG_VERDICT)  // 斷開 map_fd 上的 fn 函數
```

示例中的內部代碼：

[search /examples](https://github.com/iovisor/bcc/tree/master/examples),

### 12. detach_kprobe()

語法：```BPF.detach_kprobe(event="event", fn_name="name")```

斷開指定事件的 kprobe 處理函數。

例如：

```Python
b.detach_kprobe(event="__page_cache_alloc", fn_name="trace_func_entry")  // 斷開 "__page_cache_alloc" 事件上的 "trace_func_entry" 函數
```

### 13. detach_kretprobe()

語法：```BPF.detach_kretprobe(event="event", fn_name="name")```

斷開指定事件的 kretprobe 處理函數。

例如：

```Python
b.detach_kretprobe(event="__page_cache_alloc", fn_name="trace_func_return")  // 斷開 "__page_cache_alloc" 事件上的 "trace_func_return" 函數
```

## 調試輸出

### 1. trace_print()

語法：```BPF.trace_print(fmt="fields")```

該方法持續讀取全局共享的 `/sys/kernel/debug/tracing/trace_pipe` 文件並打印其內容。可以通過 BPF 和 `bpf_trace_printk()` 函數將數據寫入該文件，但該方法存在限制，包括缺乏併發跟蹤支持。更推薦使用前面介紹的 BPF_PERF_OUTPUT 機制。

參數：

- ```fmt```: 可選，可以包含字段格式化字符串，默認為 ```None```。

示例：

```Python
# 將 trace_pipe 輸出原樣打印：
b.trace_print()

# 打印 PID 和消息：
b.trace_print(fmt="{1} {5}")
```

示例中的內部代碼：
[search /examples](https://github.com/iovisor/bcc/tree/master/examples)。"[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 2. trace_fields()

語法: ```BPF.trace_fields(nonblocking=False)```

該方法從全局共享的 /sys/kernel/debug/tracing/trace_pipe 文件中讀取一行，並將其作為字段返回。該文件可以通過 BPF 和 bpf_trace_printk() 函數進行寫入，但該方法有一些限制，包括缺乏併發追蹤支持。我們更推薦使用之前介紹的 BPF_PERF_OUTPUT 機制。

參數:

- ```nonblocking```: 可選參數，默認為 ```False```。當設置為 ```True``` 時，程序將不會阻塞等待輸入。

示例:

```Python
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    [...]
```

內聯示例:
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

## 輸出 API

BPF 程序的正常輸出有兩種方式:

- 每個事件: 使用 PERF_EVENT_OUTPUT、open_perf_buffer() 和 perf_buffer_poll()。
- map 彙總: 使用 items() 或 print_log2_hist()，在 Maps 部分有介紹。

### 1. perf_buffer_poll()

語法: ```BPF.perf_buffer_poll(timeout=T)```

該方法從所有打開的 perf 環形緩衝區中輪詢，並對每個條目調用在調用 open_perf_buffer 時提供的回調函數。

timeout 參數是可選的，並以毫秒為單位計量。如果未提供，則輪詢將無限期進行。

示例:

```Python
# 循環調用帶有回調函數 print_event 的 open_perf_buffer
b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
```

內聯示例:
[代碼](https://github.com/iovisor/bcc/blob/v0.9.0/examples/tracing/hello_perf_output.py#L55)"."[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 2. ring_buffer_poll()

語法: ```BPF.ring_buffer_poll(timeout=T)```

這個方法從所有已打開的ringbuf環形緩衝區中輪詢數據，對每個條目調用在調用open_ring_buffer時提供的回調函數。

timeout參數是可選的，以毫秒為單位測量。如果沒有指定，輪詢將持續到沒有更多的數據或回調函數返回負值。

示例:

```Python
# 循環使用回調函數print_event
b["events"].open_ring_buffer(print_event)
while 1:
    try:
        b.ring_buffer_poll(30)
    except KeyboardInterrupt:
        exit();
```

示例：
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),

### 3. ring_buffer_consume()

語法: ```BPF.ring_buffer_consume()```

這個方法從所有已打開的ringbuf環形緩衝區中消費數據，對每個條目調用在調用open_ring_buffer時提供的回調函數。

與```ring_buffer_poll```不同，這個方法在嘗試消費數據之前**不會輪詢數據**。這樣可以減少延遲，但會增加CPU消耗。如果不確定使用哪種方法，建議使用```ring_buffer_poll```。

示例:

```Python
# 循環使用回調函數print_event
b["events"].open_ring_buffer(print_event)
while 1:
    try:
        b.ring_buffer_consume()
    except KeyboardInterrupt:
        exit();
```

示例：
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),

## Map APIs

Maps是BPF數據存儲器，在bcc中用於實現表、哈希和直方圖等更高層次的對象。

### 1. get_table()

語法: ```BPF.get_table(name)```".返回一個table對象。由於可以將表格作為BPF項進行讀取，因此此功能不再使用。例如：`BPF[name]`。

示例：

```Python
counts = b.get_table("counts")

counts = b["counts"]
```

這兩者是等價的。

### 2. open_perf_buffer()

語法：`table.open_perf_buffers(callback, page_cnt=N, lost_cb=None)`

此操作基於BPF中定義的表格（`BPF_PERF_OUTPUT()`），將回調Python函數`callback`關聯到在perf環形緩衝區中有數據可用時調用。這是從內核傳輸每個事件的數據到用戶空間的推薦機制的一部分。可以通過`page_cnt`參數指定perf環形緩衝區的大小，默認為8個頁面，必須是頁數的2的冪次方。如果回調函數不能快速處理數據，則可能丟失某些提交的數據。`lost_cb`用於記錄/監視丟失的計數。如果`lost_cb`是默認的`None`值，則只會打印一行消息到`stderr`。

示例：

```Python
# 處理事件
def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents
    [...]

# 循環通過回調函數打印事件
b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
```

請注意，傳輸的數據結構需要在BPF程序中以C方式聲明。例如：

```C
// 在C中定義輸出數據結構
struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
};
BPF_PERF_OUTPUT(events);
[...]
```

在Python中，您可以讓bcc自動生成C聲明中的數據結構（建議方法）：

```Python
def print_event(cpu, data, size):
    event = b["events"].event(data)
[...]
```

或者手動定義：

```Python
# 在Python中定義輸出數據結構
TASK_COMM_LEN = 16    # linux/sched.h
class Data(ct.Structure):
    _fields_ = [("pid", ct.c_ulonglong),
                ("ts", ct.c_ulonglong),
                ("comm", ct.c_char * TASK_COMM_LEN)]"。def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents
[...]


在此處的示例中：
[code](https://github.com/iovisor/bcc/blob/v0.9.0/examples/tracing/hello_perf_output.py#L52),
[search /examples](https://github.com/iovisor/bcc/tree/master/examples),
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 3. items()

語法: ```table.items()```

返回一個表中的鍵數組。它可以與BPF_HASH映射一起使用，從而獲取並迭代鍵。

示例:

```Python
# 打印輸出
print("%10s %s" % ("COUNT", "STRING"))
counts = b.get_table("counts")
for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
    print("%10d \"%s\"" % (v.value, k.c.encode('string-escape')))
```

此示例還使用```sorted()```方法按值排序。

在此處的示例中：
[search /examples](https://github.com/iovisor/bcc/tree/master/examples),
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)。

### 4. values()

語法: ```table.values()```

返回一個表中的值數組。

### 5. clear()

語法: ```table.clear()```

清除表：刪除所有條目。

示例:

```Python
# 每秒打印映射摘要：
while True:
    time.sleep(1)
    print("%-8s\n" % time.strftime("%H:%M:%S"), end="")
    dist.print_log2_hist(sym + " return:")
    dist.clear()
```

在此處的示例中:
[search /examples](https://github.com/iovisor/bcc/tree/master/examples),
[search /tools](https://github.com/iovisor/bcc/tree/master/tools)。

### 6. items_lookup_and_delete_batch()

語法: ```table.items_lookup_and_delete_batch()```。返回一個使用一次BPF系統調用在表中的鍵的數組。可以與BPF_HASH映射一起使用以獲取和迭代鍵。還會清除表：刪除所有條目。
您應該使用table.items_lookup_and_delete_batch()而不是table.items()後跟table.clear()。它需要內核v5.6。

示例:

```Python
# 每秒打印調用率:
print("%9s-%9s-%8s-%9s" % ("PID", "COMM", "fname", "counter"))
while True:
    for k, v in sorted(b['map'].items_lookup_and_delete_batch(), key=lambda kv: (kv[0]).pid):
        print("%9s-%9s-%8s-%9d" % (k.pid, k.comm, k.fname, v.counter))
    sleep(1)
```

### 7. items_lookup_batch()

語法: ```table.items_lookup_batch()```

使用一次BPF系統調用返回表中的鍵數組。可以與BPF_HASH映射一起使用以獲取和迭代鍵。
您應該使用table.items_lookup_batch()而不是table.items()。它需要內核v5.6。

示例:

```Python
# 打印映射的當前值:
print("%9s-%9s-%8s-%9s" % ("PID", "COMM", "fname", "counter"))
while True:
    for k, v in sorted(b['map'].items_lookup_batch(), key=lambda kv: (kv[0]).pid):
        print("%9s-%9s-%8s-%9d" % (k.pid, k.comm, k.fname, v.counter))
```

### 8. items_delete_batch()

語法: ```table.items_delete_batch(keys)```

當keys為None時，它會清除BPF_HASH映射的所有條目。它比table.clear()更有效，因為它只生成一個系統調用。您可以通過給出一個鍵數組來刪除映射的一個子集。這些鍵及其關聯值將被刪除。它需要內核v5.6。

參數:

- keys是可選的，默認為None。

### 9. items_update_batch()

語法: ```table.items_update_batch(keys, values)```

使用新值更新所有提供的鍵。兩個參數必須具有相同的長度並且在映射限制之內（在1到最大條目之間）。它需要內核v5.6。

參數:

- keys是要更新的鍵列表
- values是包含新值的列表。### 10. print_log2_hist()

語法: ```table.print_log2_hist(val_type="value", section_header="Bucket ptr", section_print_fn=None)```

以ASCII的形式打印一個表格作為log2直方圖。該表必須以log2的形式存儲，可使用BPF函數```bpf_log2l()```完成。

參數:

- val_type: 可選，列標題。
- section_header: 如果直方圖有一個輔助鍵，多個表格將被打印，並且section_header可以用作每個表格的標題描述。
- section_print_fn: 如果section_print_fn不為None，則將傳遞給bucket值。

示例:

```Python
b = BPF(text="""
BPF_HISTOGRAM(dist);

int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
 dist.increment(bpf_log2l(req->__data_len / 1024));
 return 0;
}
""")
[...]

b["dist"].print_log2_hist("kbytes")
```

輸出:

```sh
     kbytes          : count     distribution
       0 -> 1        : 3        |                                      |
       2 -> 3        : 0        |                                      |
       4 -> 7        : 211      |**********                            |
       8 -> 15       : 0        |                                      |
      16 -> 31       : 0        |                                      |
      32 -> 63       : 0        |                                      |
      64 -> 127      : 1        |                                      |
     128 -> 255      : 800      |**************************************|
```

這個輸出顯示了一個多模式分佈，最大模式是128->255 kbytes，計數為800。

這是一種高效的數據概括方法，因為概括是在內核中執行的，只有計數列被傳遞到用戶空間。

實際示例:
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 11. print_linear_hist()".語法: ```table.print_linear_hist(val_type="value", section_header="Bucket ptr", section_print_fn=None)```

以ASCII字符形式打印一個線性直方圖的表格。此功能旨在可視化小的整數範圍，例如0到100。

參數:

- val_type: 可選，列標題。
- section_header: 如果直方圖有一個二級鍵，則會打印多個表格，並且section_header可以用作每個表格的頭部描述。
- section_print_fn: 如果section_print_fn不為None，則會將bucket的值傳遞給它。

示例:

```Python
b = BPF(text="""
BPF_HISTOGRAM(dist);

int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
 dist.increment(req->__data_len / 1024);
 return 0;
}
""")
[...]

b["dist"].print_linear_hist("kbytes")
```

輸出:

```sh
     kbytes        : count     distribution
        0          : 3        |******                                  |
        1          : 0        |                                        |
        2          : 0        |                                        |
        3          : 0        |                                        |
        4          : 19       |****************************************|
        5          : 0        |                                        |
        6          : 0        |                                        |
        7          : 0        |                                        |
        8          : 4        |********                                |
        9          : 0        |                                        |
        10         : 0        |                                        |
        11         : 0        |                                        |
        12         : 0        |                                        |
        13         : 0        |                                        |
        14         : 0        |                                        |
        15         : 0        |                                        |。
```### 16         : 2        |****                                    |
[...]
```

這是一種高效的數據彙總方式，因為彙總是在內核中執行的，只有計數列中的值傳遞到用戶空間。

現場示例:
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 12. open_ring_buffer()

語法: ```table.open_ring_buffer(callback, ctx=None)```

此操作用於在BPF中定義為BPF_RINGBUF_OUTPUT()的表，並將Python回調函數```callback```與ringbuf環形緩衝區中有可用數據時調用相連。這是從內核向用戶空間傳輸每個事件數據的新（Linux 5.8+）推薦機制的一部分。不同於perf緩衝區，ringbuf大小在BPF程序中指定，作為```BPF_RINGBUF_OUTPUT```宏的一部分。如果回調函數處理數據不夠快，可能會丟失一些提交的數據。在這種情況下，事件應該更頻繁地進行輪詢和/或增加環形緩衝區的大小。

示例:

```Python
# 處理事件
def print_event(ctx, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents
    [...]

# 循環並使用print_event回調函數
b["events"].open_ring_buffer(print_event)
while 1:
    try:
        b.ring_buffer_poll()
    except KeyboardInterrupt:
        exit()
```

請注意，在BPF程序中，傳輸的數據結構需要在C中聲明。例如:

```C
// 在C中定義輸出數據結構
struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
};
BPF_RINGBUF_OUTPUT(events, 8);
[...]
```

在Python中，您可以讓bcc自動從C的聲明中生成數據結構（推薦）:

```Python
def print_event(ctx, data, size):
    event = b["events"].event(data)
[...]
```

或者手動定義:

```Python".# 在Python中定義輸出數據結構
TASK_COMM_LEN = 16    # linux/sched.h
class Data(ct.Structure):
    _fields_ = [("pid", ct.c_ulonglong),
                ("ts", ct.c_ulonglong),
                ("comm", ct.c_char * TASK_COMM_LEN)]

def print_event(ctx, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents
[...]

```

在原地的示例:
[在/examples中搜索](https://github.com/iovisor/bcc/tree/master/examples),

### 13. push()

語法: ```table.push(leaf, flags=0)```

將元素推入堆棧或隊列表。如果操作不成功，會引發異常。傳遞QueueStack.BPF_EXIST作為標誌會使隊列或堆棧丟棄最舊的元素，如果表已滿。

在原地的示例:
[在/tests中搜索](https://github.com/iovisor/bcc/tree/master/tests),

### 14. pop()

語法: ```leaf = table.pop()```

從堆棧或隊列表中彈出一個元素。與```peek()```不同，```pop()```在返回元素之前會將其從表中移除。如果操作不成功，會引發KeyError異常。

在原地的示例:
[在/tests中搜索](https://github.com/iovisor/bcc/tree/master/tests),

### 15. peek()

語法: ```leaf = table.peek()```

查看堆棧或隊列表頭部的元素。與```pop()```不同，```peek()```不會將元素從表中移除。如果操作不成功，會引發異常。

在原地的示例:
[在/tests中搜索](https://github.com/iovisor/bcc/tree/master/tests),

## 輔助方法

一些由bcc提供的輔助方法。請注意，因為我們在Python中，我們可以導入任何Python庫及其方法，包括例如argparse、collections、ctypes、datetime、re、socket、struct、subprocess、sys和time等庫。

### 1. ksym()

語法: ```BPF.ksym(addr)```

將內核內存地址轉換為內核函數名稱，並返回該名稱。

示例:

```Python"。
格式: 只返回轉換後的內容，不包括原始文本。```markdown
print("內核函數：" + b.ksym(addr))
```

例子：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 2. ksymname()

語法：```BPF.ksymname(name)```

將內核名稱翻譯為地址。這是ksym的反向過程。當函數名稱未知時，返回-1。

例子：

```Python
print("內核地址：%x" % b.ksymname("vfs_read"))
```

例子：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 3. sym()

語法：```BPF.sym(addr, pid, show_module=False, show_offset=False)```

將內存地址翻譯為pid的函數名稱，並返回。小於零的pid將訪問內核符號緩存。`show_module`和`show_offset`參數控制是否顯示函數所在的模塊以及是否顯示從符號開頭的指令偏移量。這些額外參數的默認值為`False`。

例子：

```python
print("函數：" + b.sym(addr, pid))
```

例子：
[搜索 /examples](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /tools](https://github.com/iovisor/bcc/tree/master/tools)

### 4. num_open_kprobes()

語法：```BPF.num_open_kprobes()```

返回打開的k[ret]probe的數量。當使用event_re附加和分離探測點時，可以發揮作用。不包括perf_events讀取器。

例子：

```python
b.attach_kprobe(event_re=pattern, fn_name="trace_count")
matched = b.num_open_kprobes()
if matched == 0:
    print("0個函數與\"%s\"匹配。程序退出。" % args.pattern)
    exit()
```

例子："[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

### 5. get_syscall_fnname()

語法: ```BPF.get_syscall_fnname(name : str)```

返回系統調用的相應內核函數名。該輔助函數將嘗試不同的前綴，並與系統調用名連接起來。請注意，返回值可能在不同版本的Linux內核中有所不同，有時會引起問題。 （見 [#2590](https://github.com/iovisor/bcc/issues/2590)）

示例:

```python
print("在內核中，%s 的函數名是 %s" % ("clone", b.get_syscall_fnname("clone")))
# sys_clone 或 __x64_sys_clone 或 ...
```

現場示例:
[搜索 /示例](https://github.com/iovisor/bcc/tree/master/examples),
[搜索 /工具](https://github.com/iovisor/bcc/tree/master/tools)

# BPF 錯誤

請參閱內核源碼中的“Understanding eBPF verifier messages”部分，位於 Documentation/networking/filter.txt。

## 1. Invalid mem access

這可能是因為試圖直接讀取內存，而不是操作BPF堆棧上的內存。所有對內核內存的讀取必須通過 bpf_probe_read_kernel() 傳遞，以將內核內存複製到BPF堆棧中，在一些簡單關聯的情況下，bcc 重寫器可以自動完成。bpf_probe_read_kernel() 執行所有必要的檢查。

示例:

```sh
bpf: Permission denied
0: (bf) r6 = r1
1: (79) r7 = *(u64 *)(r6 +80)
2: (85) call 14
3: (bf) r8 = r0
[...]
23: (69) r1 = *(u16 *)(r7 +16)
R7 invalid mem access 'inv'

Traceback (most recent call last):
  File "./tcpaccept", line 179, in <module>
    b = BPF(text=bpf_text)
  File "/usr/lib/python2.7/dist-packages/bcc/__init__.py", line 172, in __init__
    self._trace_autoload()".
/usr/lib/python2.7/dist-packages/bcc/__init__.py"，第 612 行，_trace_autoload 中：
    fn = self.load_func(func_name, BPF.KPROBE)
  文件 "/usr/lib/python2.7/dist-packages/bcc/__init__.py"，第 212 行，load_func 中：
    raise Exception("加載 BPF 程序 %s 失敗" % func_name)
Exception: 加載 BPF 程序 kretprobe__inet_csk_accept 失敗
```

## 2. 無法從專有程序調用 GPL-only 函數

當非 GPL BPF 程序調用 GPL-only 輔助函數時，會出現此錯誤。要修復此錯誤，請勿在專有 BPF 程序中使用 GPL-only 輔助函數，或者將 BPF 程序重新授權為 GPL-compatible 許可證。請查看哪些 [BPF helpers](https://github.com/iovisor/bcc/blob/master/docs/kernel-versions.md#helpers) 是 GPL-only 的，並且哪些許可證被視為 GPL-compatible。

示例，從專有程序（`#define BPF_LICENSE Proprietary`）調用 `bpf_get_stackid()`，一種 GPL-only 的 BPF helper：

```sh
bpf: 加載程序失敗：無效參數
[...]
8: (85) 調用 bpf_get_stackid#27
無法從專有程序調用 GPL-only 函數
```

# 環境變量

## 1. 內核源代碼目錄

eBPF 程序編譯需要內核源代碼或已編譯的內核頭。如果你的內核源代碼位於無法被 BCC 找到的非標準位置，可以通過將 `BCC_KERNEL_SOURCE` 設置為該路徑的絕對路徑來為 BCC 提供所需的位置信息。

## 2. 內核版本覆蓋

默認情況下，BCC 將 `LINUX_VERSION_CODE` 存儲在生成的 eBPF 對象中，並在加載 eBPF 程序時傳遞給內核。有時，這可能非常不方便，尤其是當內核略有更新時，比如 LTS 內核發佈。微小的不匹配幾乎不會導致加載的 eBPF 程序出現任何問題。通過將 `BCC_LINUX_VERSION_CODE` 設置為正在運行的內核版本，可以繞過驗證內核版本的檢查。這對於程序是必需的。使用kprobes的程序需要以`(VERSION * 65536) + (PATCHLEVEL * 256) + SUBLEVEL`的格式進行編碼。例如，如果當前運行的內核是`4.9.10`，則可以設置`export BCC_LINUX_VERSION_CODE=264458`以成功地覆蓋內核版本檢查。
