# 在應用程序退出後運行 eBPF 程序：eBPF 程序的生命週期

eBPF（Extended Berkeley Packet Filter）是 Linux 內核中的一項重大技術創新，允許用戶在內核空間中執行自定義程序，而無需修改內核源代碼或加載任何內核模塊。這為開發人員提供了極大的靈活性，可以觀察、修改和控制 Linux 系統。

本文將介紹 eBPF 程序的生命週期，以及如何在用戶空間應用程序退出後繼續運行 eBPF 程序的方法，還將介紹如何使用 "pin" 在不同進程之間共享 eBPF 對象。本文是 eBPF 開發者教程的一部分，更多詳細信息可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 和 <https://eunomia.dev/tutorials> 中找到。

通過使用 "detach" 方法來運行 eBPF 程序，用戶空間加載程序可以在不停止 eBPF 程序的情況下退出。另外，使用 "pin" 的方法可以在進程之間共享 eBPF 對象，使其保持活動狀態。

## eBPF 程序的生命週期

BPF對象（包括程序、映射和調試信息）通過文件描述符（FD）進行訪問，並具有引用計數器。每個對象都有一個引用計數器，用於追蹤對象被引用的次數。例如，當創建一個映射時，內核會分配一個struct bpf_map對象，並將其引用計數器初始化為1。然後，將映射的文件描述符返回給用戶空間進程。如果進程退出或崩潰，文件描述符將被關閉，並且映射的引用計數將減少。當引用計數為零時，內存將被釋放。

BPF程序使用 maps 有兩個階段。首先，創建 maps 並將其文件描述符存儲為BPF_LD_IMM64指令的一部分。當內核驗證程序時，它會增加程序使用的 maps 的引用計數，並將程序的引用計數初始化為1。此時，用戶空間可以關閉與maps 相關的文件描述符，但 maps 不會被銷燬，因為程序仍然在使用它們。當程序文件描述符關閉且引用計數為零時，銷燬邏輯將減少 maps 的引用計數。這允許多個不同類型的程序同時使用同一個 maps。

當程序附加到一個掛鉤時，程序的引用計數增加。用戶空間進程創建 maps 和程序，然後加載程序並將其附加到掛鉤上後，就可以退出了。此時，由用戶空間創建的 maps 和程序將保持活動狀態，因為引用計數>0。這就是BPF對象的生命週期。只要BPF對象的引用計數>0，內核將保持其活動狀態。

然而，不同的附加點的行為不同。一些附加點（如XDP、tc的clsact和基於cgroup的hooks）是全局的，即使沒有進程使用它們，程序也會繼續處理數據包。另一些附加點（如kprobe、uprobe、tracepoint、perf_event、raw_tracepoint、socket過濾器和so_reuseport掛鉤）只在持有事件的進程的生命週期內生效。當這些進程崩潰時，內核將分離BPF程序並減少其引用計數。

總結：XDP、tc、lwt和cgroup掛鉤是全局的，而kprobe、uprobe、tracepoint、perf_event、raw_tracepoint、socket過濾器和so_reuseport掛鉤是本地於進程的。基於文件描述符的API具有自動清理的優點，因此如果用戶空間進程出現問題，內核將自動清理所有對象。在網絡方面，基於文件描述符的API可以防止程序無限制地運行。

另一種保持 BPF 程序和映射活動的方法是 BPFFS，即BPF文件系統。通過將程序或 maps 固定(pin)到BPFFS中的某個位置，可以增加其引用計數，並使其保持活動狀態，即使沒有附加到任何位置或任何程序使用固定的BPF程序和 maps 。

瞭解BPF程序和 maps 的生命週期對於用戶安全、可靠地使用BPF是非常重要的。文件描述符、引用計數器和 BPFFS 等機制有助於管理BPF對象的生命週期，確保它們的正確創建、附加、分離和替換。

### Kubernetes 中的 eBPF：通過遠程過程調用（RPC）部署 eBPF 程序

在 Kubernetes 環境中，部署 eBPF 程序通常需要更高級別的系統權限。通常，這些應用程序需要至少 CAP_BPF 權限，根據程序類型的不同，可能還需要其他權限。在多租戶的 Kubernetes 環境中，為每個容器或應用程序授予廣泛的權限可能帶來安全風險。

為了解決權限問題，一種方法是通過固定（pinning）eBPF 映射來減輕權限要求。固定允許 eBPF 對象在創建它們的進程的生命週期之外保持活動狀態，以便其他進程可以訪問它們。在 Kubernetes 中，不同的容器可能需要與相同的 eBPF 對象進行交互，因此固定對象很有用。

例如，可以使用特權的初始化器容器來創建並固定一個 eBPF 映射。隨後的容器（可能以較低權限運行）可以與固定的 eBPF 對象進行交互。這種方法將權限要求限制在初始化階段，增強了整體安全性。

在這種背景下，bpfman 項目發揮了關鍵作用。bpfman，即 BPF Daemon，旨在以更受控且更安全的方式管理 eBPF 程序和映射的生命週期。它充當用戶空間與內核空間之間的中間層，提供加載和管理 eBPF 程序的機制，而無需為每個單獨的容器或應用程序授予廣泛的權限。

在 Kubernetes 中，bpfman 可以作為特權服務部署，負責在集群的不同節點上加載和管理 eBPF 程序。它可以處理 eBPF 生命週期管理的複雜性，如加載、卸載、更新 eBPF 程序，並對其狀態進行管理。這種集中化的方法簡化了在 Kubernetes 集群中部署和管理 eBPF 程序的過程，同時符合安全最佳實踐。

## 使用 Detach 在應用程序退出後通過任何程序替換 eBPF

在 libbpf 中，可以使用 `bpf_object__pin_maps` 函數將映射固定到 BPF 對象中。對於程序和鏈接，也有類似的 API。

以下是一個示例，演示如何使用類似於前一節中的 textreplace 程序的字符串替換示例來展示 detach 方法。可以使用類似的代碼將程序、映射和鏈接固定到 BPF 對象中：

```c
int pin_program(struct bpf_program *prog, const char* path)
{
    int err;
    err = bpf_program__pin(prog, path);
        if (err) {
            fprintf(stdout, "could not pin prog %s: %d\n", path, err);
            return err;
        }
    return err;
}

int pin_map(struct bpf_map *map, const char* path)
{
    int err;
    err = bpf_map__pin(map, path);
        if (err) {
            fprintf(stdout, "could not pin map %s: %d\n", path, err);
            return err;
        }
    return err;
}

int pin_link(struct bpf_link *link, const char* path)
{
    int err;
    err = bpf_link__pin(link, path);
        if (err) {
            fprintf(stdout, "could not pin link %s: %d\n", path, err);
            return err;
        }
    return err;
}
```

## 運行示例

在這個示例中，我們將繼續使用前一節中的字符串替換示例來演示在應用程序退出後運行 eBPF 程序的方法，並展示潛在的安全風險。通過使用 `--detach` 參數運行該程序，可以使用戶空間加載程序在不停止 eBPF 程序的情況下退出。完整的示例代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/28-detach> 中找到。關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

在運行之前，請確保已經掛載了 BPF 文件系統：

```bash
sudo mount bpffs -t bpf /sys/fs/bpf
mkdir /sys/fs/bpf/textreplace
```

然後，可以使用以下命令運行帶有 detach 參數的 text-replace2 程序：

```bash
./textreplace2 -f /proc/modules -i 'joydev' -r 'cryptd' -d
```

這將在 `/sys/fs/bpf/textreplace` 目錄下創建一些 eBPF 鏈接文件。加載程序成功運行後，可以使用以下命令檢查日誌：

```bash
sudo cat /sys/kernel/debug/tracing/trace_pipe
# 確認鏈接文件是否存在
sudo ls -l /sys/fs/bpf/textreplace
```

最後，要停止程序，只需刪除鏈接文件：

```bash
sudo rm -r /sys/fs/bpf/textreplace
```

## 參考資料

您可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

- [bad-bpf](https://github.com/pathtofile/bad-bpf)
- [Object Lifetime in the Linux kernel](https://facebookmicrosites.github.io/bpf/blog/2018/08/31/object-lifetime.html)
- [BPFMan: A Novel Way to Manage eBPF—Beyond Capsule Mode](https://bpfman.io/main/blog/2023/09/07/bpfman-a-novel-way-to-manage-ebpf)

> 原文地址：<https://eunomia.dev/zh/tutorials/28-detach/>
