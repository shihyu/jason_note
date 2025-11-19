# 特殊過濾

某些工具具有特殊的過濾能力，主要用例是跟蹤運行在容器中的進程，但這些機制是通用的，也可以在其他情況下使用。

## 按 cgroups過濾

某些工具有一個通過引用外部管理的固定的BPF哈希映射來按cgroup過濾的選項。

命令示例：

```sh
# ./opensnoop --cgroupmap /sys/fs/bpf/test01
# ./execsnoop --cgroupmap /sys/fs/bpf/test01
# ./tcpconnect --cgroupmap /sys/fs/bpf/test01
# ./tcpaccept --cgroupmap /sys/fs/bpf/test01
# ./tcptracer --cgroupmap /sys/fs/bpf/test01
```

上述命令將僅顯示屬於一個或多個cgroup的進程的結果，這些cgroup的ID由`bpf_get_current_cgroup_id()`返回，並存在固定的BPF哈希映射中。

通過以下方式創建BPF哈希映射：

```sh
# bpftool map create /sys/fs/bpf/test01 type hash key 8 value 8 entries 128 \
        name cgroupset flags 0
```

要在新cgroup中獲取一個shell，可以使用：

```sh
# systemd-run --pty --unit test bash
```

該shell將在cgroup`/sys/fs/cgroup/unified/system.slice/test.service`中運行。

可以使用`name_to_handle_at()`系統調用來發現cgroup ID。在examples/cgroupid中，您可以找到一個獲取cgroup ID的程序示例。

```sh
# cd examples/cgroupid
# make
# ./cgroupid hex /sys/fs/cgroup/unified/system.slice/test.service
```

或者，使用Docker：

```sh
# cd examples/cgroupid
# docker build -t cgroupid .
# docker run --rm --privileged -v /sys/fs/cgroup:/sys/fs/cgroup \
 cgroupid cgroupid hex /sys/fs/cgroup/unified/system.slice/test.service
```

這將以主機的字節序(hexadecimal string)打印出cgroup ID，例如`77 16 00 00 01 00 00 00`。

```sh
# FILE=/sys/fs/bpf/test01
# CGROUPID_HEX="77 16 00 00 01 00 00 00"
# bpftool map update pinned $FILE key hex $CGROUPID_HEX value hex 00 00 00 00 00 00 00 00 any
```

現在，通過systemd-run啟動的shell的cgroup ID已經存在於BPF哈希映射中，bcc工具將顯示來自該shell的結果。可以添加和。從BPF哈希映射中刪除而不重新啟動bcc工具。

這個功能對於將bcc工具集成到外部項目中非常有用。

## 按命名空間選擇掛載點進行過濾

BPF哈希映射可以通過以下方式創建：

```sh
# bpftool map create /sys/fs/bpf/mnt_ns_set type hash key 8 value 4 entries 128 \
        name mnt_ns_set flags 0
```

僅執行`execsnoop`工具，過濾掛載命名空間在`/sys/fs/bpf/mnt_ns_set`中：

```sh
# tools/execsnoop.py --mntnsmap /sys/fs/bpf/mnt_ns_set
```

在新的掛載命名空間中啟動一個終端：

```sh
# unshare -m bash
```

使用上述終端的掛載命名空間ID更新哈希映射：

```sh
FILE=/sys/fs/bpf/mnt_ns_set
if [ $(printf '\1' | od -dAn) -eq 1 ]; then
 HOST_ENDIAN_CMD=tac
else
  HOST_ENDIAN_CMD=cat
fi

NS_ID_HEX="$(printf '%016x' $(stat -Lc '%i' /proc/self/ns/mnt) | sed 's/.\{2\}/&\n/g' | $HOST_ENDIAN_CMD)"
bpftool map update pinned $FILE key hex $NS_ID_HEX value hex 00 00 00 00 any
```

在這個終端中執行命令：

```sh
# ping kinvolk.io
```

你會看到在上述你啟動的`execsnoop`終端中，這個調用被記錄下來：

```sh
# tools/execsnoop.py --mntnsmap /sys/fs/bpf/mnt_ns_set
[sudo] password for mvb:
PCOMM            PID    PPID   RET ARGS
ping             8096   7970     0 /bin/ping kinvolk.io
```。
